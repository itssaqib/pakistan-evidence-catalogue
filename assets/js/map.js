/* Canvas district maps: density by year, documented footprints, highlights. */
(function () {
  'use strict';
  var GEO = window.PEC_GEO, PEC = window.PEC;
  if (!GEO) return;
  var VBW = GEO.vb[0], VBH = GEO.vb[1];
  var css = getComputedStyle(document.documentElement);
  var C = function (n) { return css.getPropertyValue(n).trim(); };
  var COL = {
    out: C('--slate-2'), scope: C('--fp-scope'), p1: C('--fp-1'), p2: C('--fp-2'), later: C('--fp-later'),
    stage: C('--slate'), line: C('--on-slate'),
    dens: [C('--slate-2'), C('--d1'), C('--d2'), C('--d3'), C('--d4'), C('--d5')]
  };
  var paths = null, provPath = null, outlinePath = null, hitCtx = null;
  function build() {
    if (paths) return;
    paths = GEO.d.map(function (d) { return { id: d.id, n: d.n, p: d.p, f: d.f, c: d.c, path: new Path2D(d.path) }; });
    provPath = new Path2D(GEO.prov); outlinePath = new Path2D(GEO.outline);
    hitCtx = document.createElement('canvas').getContext('2d');
  }
  var byCode = null;
  function unitsFor(codes) {
    build();
    if (!byCode) {
      byCode = { ALL: [], FATA: [] };
      paths.forEach(function (d) { byCode.ALL.push(d.id); (byCode[d.p] = byCode[d.p] || []).push(d.id); if (d.f) byCode.FATA.push(d.id); });
    }
    if (codes.indexOf('ALL') >= 0) return byCode.ALL.slice();
    var out = [];
    codes.forEach(function (c) { (byCode[c] || []).forEach(function (u) { if (out.indexOf(u) < 0) out.push(u); }); });
    return out;
  }
  function densBin(n) { return n <= 0 ? 0 : n <= 10 ? 1 : n <= 20 ? 2 : n <= 30 ? 3 : n <= 40 ? 4 : 5; }

  /* class per district for one programme; upTo limits how many phases are lit */
  function footprint(p, upTo) {
    var scope = unitsFor(p.regions), cls = {};
    paths.forEach(function (d) { cls[d.id] = 'out'; });
    scope.forEach(function (u) { cls[u] = 'scope'; });
    var fp = p.footprint;
    if (fp) {
      var phases = fp.phases.slice().sort(function (a, b) { return a.year - b.year; });
      var lim = upTo == null ? phases.length : upTo;
      phases.slice(0, lim).forEach(function (ph, k) {
        var key = k === 0 ? 'p1' : k === 1 ? 'p2' : 'later';
        ph.units.forEach(function (u) { if (cls[u] === 'scope' || cls[u] === 'out') cls[u] = key; });
      });
      if (fp.final === 'scope' && lim >= phases.length) (fp.final_regions ? unitsFor(fp.final_regions) : scope).forEach(function (u) { if (cls[u] === 'scope') cls[u] = 'later'; });
    }
    return cls;
  }

  function Map(canvas, opt) {
    build();
    this.c = canvas; this.ctx = canvas.getContext('2d'); this.opt = opt || {};
    this.state = { mode: 'scope', codes: ['ALL'] }; this.hover = null; this.sel = null;
    var self = this;
    this.resize();
    if (window.ResizeObserver) { new ResizeObserver(function () { self.resize(); self.draw(); }).observe(canvas); }
    if (this.opt.interactive) {
      canvas.addEventListener('mousemove', function (e) { self._move(e); });
      canvas.addEventListener('mouseleave', function () { self.hover = null; self.draw(); if (self.opt.onHover) self.opt.onHover(null, null); });
      canvas.addEventListener('click', function (e) { var id = self.hit(e); if (self.opt.onClick) self.opt.onClick(id, e); });
    }
  }
  Map.prototype.resize = function () {
    var r = this.c.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.max(10, Math.round(r.width * dpr));
    var h = this.opt.cover ? Math.max(10, Math.round(r.height * dpr)) : Math.round(w * VBH / VBW);
    if (this.c.width !== w || this.c.height !== h) { this.c.width = w; this.c.height = h; }
    this.dpr = dpr;
    var s = Math.min(w / VBW, h / VBH) * (this.opt.zoom || 1);
    this.s = s; this.ox = (w - VBW * s) / 2; this.oy = (h - VBH * s) / 2 + (this.opt.dy || 0) * h;
  };
  Map.prototype.set = function (st) { for (var k in st) this.state[k] = st[k]; this.draw(); return this; };
  Map.prototype.fillFor = function () {
    var st = this.state, f = {};
    if (st.mode === 'density') {
      var yi = st.yearIndex, D = PEC.density;
      paths.forEach(function (d) { f[d.id] = COL.dens[densBin(D[d.id][yi])]; });
    } else if (st.mode === 'footprint') {
      var cls = footprint(st.prog, st.upTo);
      paths.forEach(function (d) { f[d.id] = COL[cls[d.id]]; });
    } else if (st.mode === 'highlight') {
      var hl = st.units || {}, base = st.base || COL.out;
      paths.forEach(function (d) { f[d.id] = hl[d.id] ? (COL[hl[d.id]] || hl[d.id]) : base; });
    } else {
      var sc = {}; unitsFor(st.codes || ['ALL']).forEach(function (u) { sc[u] = 1; });
      paths.forEach(function (d) { f[d.id] = sc[d.id] ? COL.scope : COL.out; });
    }
    return f;
  };
  Map.prototype.draw = function () {
    var ctx = this.ctx, s = this.s, dpr = this.dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.c.width, this.c.height);
    if (this.opt.bg) { ctx.fillStyle = this.opt.bg; ctx.fillRect(0, 0, this.c.width, this.c.height); }
    ctx.setTransform(s, 0, 0, s, this.ox, this.oy);
    var fill = this.fillFor(), self = this;
    paths.forEach(function (d) { ctx.fillStyle = fill[d.id]; ctx.fill(d.path); });
    ctx.lineJoin = 'round';
    ctx.strokeStyle = COL.stage; ctx.lineWidth = (this.opt.thin ? 0.45 : 0.8) * dpr / s;
    paths.forEach(function (d) { ctx.stroke(d.path); });
    ctx.globalAlpha = 0.38; ctx.strokeStyle = COL.line; ctx.lineWidth = (this.opt.thin ? 0.6 : 1) * dpr / s; ctx.stroke(provPath);
    ctx.globalAlpha = 0.55; ctx.lineWidth = (this.opt.thin ? 0.7 : 1.2) * dpr / s; ctx.stroke(outlinePath);
    ctx.globalAlpha = 1;
    var mark = function (id, w) {
      var d = paths.find(function (x) { return x.id === id; }); if (!d) return;
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = w * dpr / s; ctx.stroke(d.path);
    };
    if (this.sel) mark(this.sel, 2.2);
    if (this.hover && this.hover !== this.sel) mark(this.hover, 1.6);
    if (this.opt.labels) {
      ctx.fillStyle = 'rgba(244,239,230,.92)'; ctx.font = '500 ' + (10.5 * dpr / s) + 'px Jost, sans-serif'; if ('letterSpacing' in ctx) ctx.letterSpacing = (1.2 * dpr / s) + 'px'; ctx.textAlign = 'center';
      var NAMES = { PB: 'PUNJAB', SD: 'SINDH', KP: 'KHYBER PAKHTUNKHWA', BA: 'BALOCHISTAN', GB: 'GILGIT-BALTISTAN', AJK: 'AJK' };
      ctx.lineJoin = 'round'; ctx.strokeStyle = 'rgba(33,41,52,.7)'; ctx.lineWidth = 2.6 * dpr / s;
      for (var k in GEO.provLabels) if (NAMES[k]) { var pt = GEO.provLabels[k]; ctx.strokeText(NAMES[k], pt[0], pt[1]); ctx.fillText(NAMES[k], pt[0], pt[1]); }
    }
  };
  Map.prototype.hit = function (e) {
    var r = this.c.getBoundingClientRect();
    var x = ((e.clientX - r.left) * this.dpr - this.ox) / this.s, y = ((e.clientY - r.top) * this.dpr - this.oy) / this.s;
    for (var i = 0; i < paths.length; i++) if (hitCtx.isPointInPath(paths[i].path, x, y)) return paths[i].id;
    return null;
  };
  Map.prototype._move = function (e) {
    var id = this.hit(e);
    if (id !== this.hover) { this.hover = id; this.draw(); }
    if (this.opt.onHover) this.opt.onHover(id, e);
  };

  /* tiles: draw lazily when they scroll into view; hover replays documented phases */
  function drawTile(el) {
    if (el._map) return;
    var p = window.PECU.byId(el.getAttribute('data-pid')); if (!p) return;
    var cv = el.querySelector('canvas'); if (!cv) return;
    var m = new Map(cv, { thin: true, cover: true, zoom: 0.92, bg: COL.stage });
    m.set({ mode: 'footprint', prog: p });
    el._map = m;
    var n = p.footprint ? p.footprint.phases.length : 0;
    var host = el.closest('a, .tile') || el;
    if (n && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var timer = null;
      host.addEventListener('mouseenter', function () {
        var k = 0; clearInterval(timer); m.set({ upTo: 0 });
        timer = setInterval(function () { k++; m.set({ upTo: k }); if (k > n) { clearInterval(timer); m.set({ upTo: null }); } }, 420);
      });
      host.addEventListener('mouseleave', function () { clearInterval(timer); m.set({ upTo: null }); });
    }
  }
  function lazyTiles(root) {
    var els = (root || document).querySelectorAll('[data-pid] .tile-media, .tile-media[data-pid]');
    var targets = [];
    els.forEach(function (m) { var host = m.hasAttribute('data-pid') ? m : m.closest('[data-pid]'); if (host) { m.setAttribute('data-pid', host.getAttribute('data-pid')); targets.push(m); } });
    if (!('IntersectionObserver' in window)) { targets.forEach(drawTile); return; }
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { drawTile(en.target); io.unobserve(en.target); } });
    }, { rootMargin: '300px' });
    targets.forEach(function (t) { io.observe(t); });
  }

  window.PECMap = { Map: Map, footprint: footprint, unitsFor: unitsFor, lazyTiles: lazyTiles, COL: COL, densBin: densBin,
    districts: function () { build(); return paths; } };
})();
