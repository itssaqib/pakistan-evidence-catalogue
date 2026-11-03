/* SVG charts. Every chart has a hover tooltip and a table-view twin. */
(function () {
  'use strict';
  var U = window.PECU, PEC = window.PEC;
  var NS = 'http://www.w3.org/2000/svg';
  function svg(w, h, label) {
    var s = document.createElementNS(NS, 'svg');
    s.setAttribute('viewBox', '0 0 ' + w + ' ' + h); s.setAttribute('role', 'img');
    if (label) s.setAttribute('aria-label', label);
    return s;
  }
  function el(tag, attrs, parent, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function roundTopBar(x, y, w, h, r) { // square at baseline, rounded data end
    r = Math.min(r, w / 2, h);
    return 'M' + x + ',' + (y + h) + 'V' + (y + r) + 'Q' + x + ',' + y + ' ' + (x + r) + ',' + y + 'H' + (x + w - r) +
      'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (y + h) + 'Z';
  }
  function roundRightBar(x, y, w, h, r) {
    r = Math.min(r, h / 2, w);
    return 'M' + x + ',' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (y + h - r) +
      'Q' + (x + w) + ',' + (y + h) + ' ' + (x + w - r) + ',' + (y + h) + 'H' + x + 'Z';
  }
  function tipOn(node, html) {
    node.addEventListener('mousemove', function (e) { U.tip.show(html, e.clientX, e.clientY); });
    node.addEventListener('mouseleave', U.tip.hide);
    node.addEventListener('focus', function () { var r = node.getBoundingClientRect(); U.tip.show(html, r.right, r.top); });
    node.addEventListener('blur', U.tip.hide);
  }
  function table(block, head, rows) {
    var t = block && block.querySelector('.chart-table'); if (!t) return;
    t.innerHTML = '<div class="table-wrap"><table class="t"><thead><tr>' + head.map(function (h) { return '<th scope="col">' + U.esc(h) + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-table-toggle]'); if (!b) return;
    var blk = b.closest('.chart-block'); var on = blk.classList.toggle('show-table');
    b.textContent = on ? 'Hide table' : 'Show as table';
  });

  /* ---------------------------------------------------------------- swimlane of rollout windows */
  function swimlane(host, progs, opt) {
    opt = opt || {};
    var order = PEC.meta.macro_order;
    var rows = progs.slice().sort(function (a, b) {
      return order.indexOf(a.macro) - order.indexOf(b.macro) || (a.start_y || 1990) - (b.start_y || 1990) || a.id.localeCompare(b.id);
    });
    var X0 = 1994, X1 = 2026, L = 250, R = 18, W = 1000, rowH = opt.compact ? 11 : 15, gH = 30, top = 26;
    var groups = []; rows.forEach(function (p) { if (!groups.length || groups[groups.length - 1].k !== p.macro) groups.push({ k: p.macro, n: 0 }); groups[groups.length - 1].n++; });
    var H = top + rows.length * rowH + groups.length * gH + 20;
    var s = svg(W, H, 'Rollout window of each programme, ' + X0 + ' to ' + X1);
    var x = function (y) { return L + (y - X0) / (X1 - X0) * (W - L - R); };
    for (var y = X0; y <= X1; y += 2) {
      el('line', { x1: x(y), x2: x(y), y1: top - 6, y2: H - 14, class: 'grid-l' }, s);
      if (y % 4 === 0) { el('text', { x: x(y), y: 12, 'text-anchor': 'middle' }, s, y); el('text', { x: x(y), y: H - 2, 'text-anchor': 'middle' }, s, y); }
    }
    var cy = top, gi = -1, prev = null;
    rows.forEach(function (p) {
      if (p.macro !== prev) { cy += gH; el('text', { x: 0, y: cy - 10, class: 'group-l' }, s, p.macro); prev = p.macro; }
      var a = el('a', { href: U.progUrl(p.id), tabindex: '0' }, s);
      el('rect', { x: 0, y: cy - rowH / 2, width: W, height: rowH, class: 'hit' }, a);
      el('text', { x: 0, y: cy + 4, class: p.tq_rank === 3 ? 'lbl-strong' : '' }, a, p.id + '  ' + (p.short.length > 34 ? p.short.slice(0, 33) + '…' : p.short));
      var sy = p.start_y || 2000, ey = Math.max(p.end_y || sy, sy) + 0.85;
      el('rect', { x: x(sy), y: cy - 3, width: Math.max(4, x(ey) - x(sy)), height: 6, rx: 3, class: 'span' }, a);
      if (p.footprint) p.footprint.phases.forEach(function (ph) { el('circle', { cx: x(ph.year + 0.4), cy: cy, r: 4.2, class: 'span-dot' }, a); });
      tipOn(a, '<strong>' + U.esc(p.id + ' ' + p.short) + '</strong>' + U.esc(p.window) + '<br><span class="tk">Timing data: ' + p.tq + '</span>');
      cy += rowH;
    });
    host.innerHTML = ''; host.appendChild(s);
    table(host.closest('.chart-block'), ['ID', 'Programme', 'Domain', 'Start', 'Latest year', 'Rollout window', 'Timing data'],
      rows.map(function (p) { return [p.id, '<a class="link" href="' + U.progUrl(p.id) + '">' + U.esc(p.short) + '</a>', U.esc(p.macro), p.start_y || '', p.end_y || '', U.esc(p.window), p.tq]; }));
  }

  /* ---------------------------------------------------------------- columns (single series) */
  function columns(host, data, opt) {
    opt = opt || {};
    var W = 1000, H = opt.h || 300, L = 40, B = 34, T = 22, max = Math.max.apply(null, data.map(function (d) { return d.v; })) || 1;
    var top = Math.ceil(max / 5) * 5;
    var s = svg(W, H, opt.label);
    var y = function (v) { return T + (H - T - B) * (1 - v / top); };
    for (var g = 0; g <= top; g += top / 5) {
      el('line', { x1: L, x2: W, y1: y(g), y2: y(g), class: g === 0 ? 'axis-l' : 'grid-l' }, s);
      el('text', { x: L - 8, y: y(g) + 4, 'text-anchor': 'end' }, s, Math.round(g));
    }
    var band = (W - L) / data.length, bw = Math.min(24 * 2.4, band * 0.5);
    data.forEach(function (d, i) {
      var cx = L + band * i + band / 2;
      var g = el('g', { tabindex: '0' }, s);
      el('rect', { x: cx - band / 2, y: T, width: band, height: H - T - B, class: 'hit' }, g);
      el('path', { d: roundTopBar(cx - bw / 2, y(d.v), bw, y(0) - y(d.v), 4), class: 'bar' + (d.hl ? ' hl' : '') }, g);
      el('text', { x: cx, y: y(d.v) - 8, 'text-anchor': 'middle', class: 'lbl-strong' }, g, d.v);
      el('text', { x: cx, y: H - 10, 'text-anchor': 'middle' }, g, d.k);
      tipOn(g, '<strong>' + U.esc(d.k) + '</strong>' + d.v + ' ' + (opt.unit || '') + (d.note ? '<br><span class="tk">' + U.esc(d.note) + '</span>' : ''));
    });
    host.innerHTML = ''; host.appendChild(s);
    table(host.closest('.chart-block'), [opt.kLabel || 'Category', opt.vLabel || 'Count'], data.map(function (d) { return [U.esc(d.k), d.v]; }));
  }

  /* ---------------------------------------------------------------- horizontal bars (single series) */
  function hbars(host, data, opt) {
    opt = opt || {};
    var W = 1000, rowH = 30, L = opt.left || 330, R = 50, T = 8;
    var H = T + data.length * rowH + 26, max = Math.max.apply(null, data.map(function (d) { return d.v; })) || 1;
    var top = Math.ceil(max / 10) * 10;
    var s = svg(W, H, opt.label);
    var x = function (v) { return L + (W - L - R) * v / top; };
    for (var g = 0; g <= top; g += top / 5) {
      el('line', { x1: x(g), x2: x(g), y1: T, y2: H - 22, class: g === 0 ? 'axis-l' : 'grid-l' }, s);
      el('text', { x: x(g), y: H - 6, 'text-anchor': 'middle' }, s, Math.round(g));
    }
    data.forEach(function (d, i) {
      var cy = T + i * rowH + rowH / 2;
      var g = el(d.href ? 'a' : 'g', d.href ? { href: d.href } : { tabindex: '0' }, s);
      el('rect', { x: 0, y: cy - rowH / 2, width: W, height: rowH, class: 'hit' }, g);
      el('text', { x: L - 12, y: cy + 4, 'text-anchor': 'end', class: 'lbl-strong' }, g, d.k.length > 46 ? d.k.slice(0, 45) + '…' : d.k);
      el('path', { d: roundRightBar(L, cy - 7, Math.max(2, x(d.v) - L), 14, 4), class: 'bar' + (d.hl ? ' hl' : '') }, g);
      el('text', { x: x(d.v) + 8, y: cy + 4 }, g, d.v);
      tipOn(g, '<strong>' + U.esc(d.k) + '</strong>' + d.v + ' ' + (opt.unit || '') + (d.note ? '<br><span class="tk">' + U.esc(d.note) + '</span>' : ''));
    });
    host.innerHTML = ''; host.appendChild(s);
    table(host.closest('.chart-block'), [opt.kLabel || 'Item', opt.vLabel || 'Count'], data.map(function (d) { return [U.esc(d.k), d.v]; }));
  }

  /* ---------------------------------------------------------------- heatmap (binned sequential, white surface) */
  function heatmap(host, rows, cols, val, opt) {
    opt = opt || {};
    var W = 1000, L = 210, T = 150, cell = (W - L) / cols.length, rh = 34, H = T + rows.length * rh + 4;
    var bins = [0, 1, 3, 6, 10, 15], fills = ['#f4f5f7', 'var(--h1)', 'var(--h2)', 'var(--h3)', 'var(--h4)', 'var(--h5)'];
    var bin = function (v) { var b = 0; for (var i = 1; i < bins.length; i++) if (v >= bins[i]) b = i; return b; };
    var s = svg(W, H, opt.label);
    cols.forEach(function (c, j) {
      var tx = L + cell * j + cell / 2;
      el('text', { x: tx, y: T - 10, transform: 'rotate(-48 ' + tx + ' ' + (T - 10) + ')', 'text-anchor': 'start' }, s, c);
    });
    var tbl = [];
    rows.forEach(function (r, i) {
      el('text', { x: L - 12, y: T + i * rh + rh / 2 + 4, 'text-anchor': 'end', class: 'lbl-strong' }, s, r);
      var tr = [U.esc(r)];
      cols.forEach(function (c, j) {
        var v = val(r, c) || 0; tr.push(v);
        var g = el('g', { tabindex: v ? '0' : '-1' }, s);
        el('rect', { x: L + cell * j, y: T + i * rh, width: cell, height: rh, fill: fills[bin(v)], class: 'cell' }, g);
        if (v) tipOn(g, '<strong>' + U.esc(r) + '</strong>' + U.esc(c) + ': ' + v + ' programme–outcome pairs');
      });
      tbl.push(tr);
    });
    host.innerHTML = ''; host.appendChild(s);
    var lg = host.parentNode.querySelector('.chart-legend');
    if (lg) lg.innerHTML = ['None', '1–2', '3–5', '6–9', '10–14', '15+'].map(function (t, i) {
      return '<span><i class="sw" style="background:' + fills[i] + (i === 0 ? ';border:1px solid #ddd' : '') + '"></i>' + t + '</span>'; }).join('');
    table(host.closest('.chart-block'), ['Programme domain'].concat(cols), tbl);
  }

  /* ---------------------------------------------------------------- survey calendar + coverage of a rollout window */
  function coverage(row, s, e) {
    if (row.band) {
      var b0 = row.band[0], b1 = row.band[1];
      var before = Math.max(0, Math.min(b1, s - 1) - b0 + 1), after = Math.max(0, b1 - Math.max(b0, s) + 1);
      return { before: before, after: after, text: before > 0 ? (row.band_note + ': ' + before + ' yrs before, ' + after + ' from start') : (b0 > s ? 'starts after rollout' : row.band_note) };
    }
    var w = row.waves.map(function (x) { return x[0]; });
    var bf = w.filter(function (y) { return y < s; }).length, du = w.filter(function (y) { return y >= s && y <= e; }).length,
      af = w.filter(function (y) { return y > e; }).length;
    return { before: bf, during: du, afterEnd: af, after: du + af, text: bf + ' before, ' + du + ' during, ' + af + ' after' };
  }
  function calendar(host, cal, opt) {
    opt = opt || {};
    var X0 = opt.from || 1990, X1 = opt.to || 2026, L = 230, R = opt.win ? 190 : 20, W = 1000, rowH = 30, T = 26;
    var H = T + cal.length * rowH + 26;
    var s = svg(W, H, 'Survey and data waves by year' + (opt.win ? ' against the rollout window' : ''));
    var x = function (y) { return L + (y - X0 + 0.5) / (X1 - X0 + 1) * (W - L - R); };
    for (var y = X0; y <= X1; y++) if (y % 5 === 0) {
      el('line', { x1: x(y), x2: x(y), y1: T - 6, y2: H - 20, class: 'grid-l' }, s);
      el('text', { x: x(y), y: 12, 'text-anchor': 'middle' }, s, y);
    }
    if (opt.win) {
      var ws = opt.win[0], we = Math.max(opt.win[1], ws);
      el('rect', { x: x(ws) - 6, y: T - 8, width: Math.max(10, x(we) - x(ws) + 12), height: H - T - 12, class: 'win' }, s);
      el('line', { x1: x(ws) - 6, x2: x(ws) - 6, y1: T - 8, y2: H - 20, class: 'win-edge' }, s);
      el('text', { x: W - R + 14, y: 12, class: 'lbl-strong' }, s, 'Waves vs rollout');
    }
    var tbl = [];
    cal.forEach(function (r, i) {
      var cy = T + i * rowH + rowH / 2;
      var g = el('g', { tabindex: '0' }, s);
      el('rect', { x: 0, y: cy - rowH / 2, width: W, height: rowH, class: 'hit' }, g);
      el('line', { x1: L, x2: W - R, y1: cy, y2: cy, class: 'lane-l' }, g);
      el('text', { x: L - 12, y: cy + 4, 'text-anchor': 'end', class: 'lbl-strong' }, g, r.label);
      if (r.band) {
        var b0 = Math.max(r.band[0], X0), b1 = Math.min(r.band[1], X1);
        el('rect', { x: x(b0) - 5, y: cy - 5, width: x(b1) - x(b0) + 10, height: 10, rx: 5, class: 'band' }, g);
      } else {
        r.waves.forEach(function (w) { if (w[0] >= X0 && w[0] <= X1) el('circle', { cx: x(w[0]), cy: cy, r: 5.5, class: 'wave' }, g); });
      }
      var cov = opt.win ? coverage(r, opt.win[0], opt.win[1]) : null;
      if (cov) el('text', { x: W - R + 14, y: cy + 4, class: 'pre-post' }, g, cov.text);
      var waves = r.band ? (r.band[0] + '–' + r.band[1] + ' (' + r.band_note + ')') : r.waves.map(function (w) { return w[1]; }).join(', ');
      tipOn(g, '<strong>' + U.esc(r.label) + '</strong>' + U.esc(waves) + (r.dist ? '<br><span class="tk">District identifier available</span>' : '<br><span class="tk">Province-representative</span>') + (cov ? '<br>' + U.esc(cov.text) : ''));
      tbl.push([U.esc(r.label), U.esc(waves), r.dist ? 'Yes' : 'Province only'].concat(cov ? [U.esc(cov.text)] : []));
    });
    host.innerHTML = ''; host.appendChild(s);
    table(host.closest('.chart-block'), ['Dataset', 'Waves', 'District level'].concat(opt.win ? ['Against rollout window'] : []), tbl);
  }

  window.PECCharts = { swimlane: swimlane, columns: columns, hbars: hbars, heatmap: heatmap, calendar: calendar, coverage: coverage };
})();
