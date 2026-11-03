/* Pakistan Evidence Catalogue — core behaviour shared by every page. */
(function () {
  'use strict';
  var PEC = window.PEC || {};
  var base = document.body.getAttribute('data-base') || '';
  var REPO = 'itssaqib/pakistan-evidence-catalogue';

  var U = window.PECU = {
    base: base,
    repo: REPO,
    esc: function (s) {
      return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    },
    byId: function (id) {
      if (!U._idx) { U._idx = {}; (PEC.programmes || []).forEach(function (p) { U._idx[p.id] = p; }); }
      return U._idx[id];
    },
    progUrl: function (id) { return base + 'programmes/' + id.toLowerCase() + '.html'; },
    span: function (p) {
      if (!p.start_y) return 'Continuous';
      if (!p.end_y || p.end_y === p.start_y) return String(p.start_y);
      return p.start_y + '–' + String(p.end_y).slice(2);
    },
    meter: function (rank) {
      var s = '<span class="meter" aria-hidden="true">';
      for (var i = 1; i <= 3; i++) s += '<i class="' + (i <= rank ? 'on' : '') + '"></i>';
      return s + '</span>';
    },
    store: {
      get: function (k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
      set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
    },
    download: function (name, text, mime) {
      var blob = new Blob([(mime === 'text/csv' ? '﻿' : '') + text], { type: (mime || 'text/plain') + ';charset=utf-8' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = name;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 800);
    },
    toCSV: function (rows, fields) {
      var q = function (v) {
        if (Array.isArray(v)) v = v.join('; ');
        v = v == null ? '' : String(v);
        return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
      };
      return [fields.join(',')].concat(rows.map(function (r) { return fields.map(function (f) { return q(r[f]); }).join(','); })).join('\n');
    },
    debounce: function (fn, ms) { var t; return function () { var a = arguments, c = this; clearTimeout(t); t = setTimeout(function () { fn.apply(c, a); }, ms || 150); }; },
    icon: function (name) {
      var I = {
        star: '<svg viewBox="0 0 24 24"><path d="M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/></svg>',
        down: '<svg viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
        copy: '<svg viewBox="0 0 24 24"><rect x="8" y="8" width="11" height="12"/><path d="M5 16V4h11"/></svg>',
        ext: '<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>'
      };
      return I[name] || '';
    }
  };

  /* ---------------------------------------------------------------- tooltip */
  var tip = document.createElement('div');
  tip.className = 'tip'; tip.setAttribute('role', 'tooltip');
  document.body.appendChild(tip);
  U.tip = {
    show: function (html, x, y) {
      tip.innerHTML = html; tip.style.display = 'block';
      var w = tip.offsetWidth, h = tip.offsetHeight;
      var left = Math.min(window.innerWidth - w - 12, x + 14);
      var top = y + 16 + h > window.innerHeight ? y - h - 12 : y + 16;
      tip.style.left = Math.max(8, left) + 'px'; tip.style.top = Math.max(8, top) + 'px';
    },
    hide: function () { tip.style.display = 'none'; }
  };

  /* ---------------------------------------------------------------- header */
  var header = document.querySelector('.site-header');
  var onScroll = function () { document.body.classList.toggle('is-compact', window.scrollY > 60); };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  function openOverlay(el) {
    if (!el) return;
    el.classList.add('is-open'); document.body.style.overflow = 'hidden';
    el._prevFocus = document.activeElement;
    var f = el.querySelector('input, a, button'); if (f) setTimeout(function () { f.focus(); }, 30);
  }
  function closeOverlay(el) {
    if (!el) return;
    el.classList.remove('is-open'); document.body.style.overflow = '';
    if (el._prevFocus) el._prevFocus.focus();
  }
  var menu = document.getElementById('menu'), search = document.getElementById('search');
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-open]');
    if (t) { e.preventDefault(); openOverlay(document.getElementById(t.getAttribute('data-open'))); if (t.getAttribute('data-open') === 'search') runSearch(''); return; }
    var c = e.target.closest('[data-close]');
    if (c) { e.preventDefault(); closeOverlay(c.closest('.overlay')); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { document.querySelectorAll('.overlay.is-open').forEach(closeOverlay); }
    var typing = /input|textarea|select/i.test((e.target || {}).tagName || '');
    if (!typing && (e.key === '/' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k'))) {
      e.preventDefault(); openOverlay(search); runSearch('');
    }
  });

  /* ---------------------------------------------------------------- search */
  var PAGES = [
    ['Programmes', 'programmes/index.html', 'Browse all programmes and natural experiments'],
    ['Atlas', 'atlas/index.html', 'District map of programme scope and documented rollout'],
    ['Insights', 'insights/index.html', 'The catalogue in charts'],
    ['Datasets', 'datasets/index.html', 'Survey calendar and dataset catalogue'],
    ['Toolkit', 'toolkit/index.html', 'Downloads, district crosswalk, Stata templates, power calculator'],
    ['Methods', 'guide/index.html', 'Identification playbook for staggered designs'],
    ['Finding treatment dates', 'guide/timing.html', 'Where district-by-date rollout data comes from'],
    ['Standing caveats', 'guide/caveats.html', 'Boundary changes, targeting, migration, switching treatment'],
    ['About', 'about/index.html', 'Why the catalogue exists and how it was built'],
    ['Contribute', 'contribute/index.html', 'Claim an idea, correct a date, share a timing file'],
    ['Shortlist', 'shortlist/index.html', 'Programmes you have saved, side by side']
  ];
  var index = null;
  function buildIndex() {
    index = [];
    (PEC.programmes || []).forEach(function (p) {
      index.push({ kind: 'Programme', id: p.id, title: p.short, sub: p.name + ' — ' + p.agency, url: U.progUrl(p.id),
        hay: (p.id + ' ' + p.name + ' ' + p.short + ' ' + p.domain + ' ' + p.agency + ' ' + p.scope + ' ' + p.window + ' ' + p.methods.join(' ')).toLowerCase() });
    });
    (PEC.outcomes || []).forEach(function (o) {
      index.push({ kind: 'Outcome', id: o.id, title: o.outcome, sub: o.domain + ' — ' + o.definition, url: base + 'insights/index.html#outcomes',
        hay: (o.id + ' ' + o.outcome + ' ' + o.domain + ' ' + o.definition).toLowerCase(), oid: o.id });
    });
    (PEC.datasets || []).forEach(function (d) {
      index.push({ kind: 'Dataset', id: d.key, title: d.dataset, sub: d.producer, url: base + 'datasets/index.html#ds-' + d.key,
        hay: (d.key + ' ' + d.dataset + ' ' + d.producer + ' ' + d.type + ' ' + d.coverage).toLowerCase() });
    });
    PAGES.forEach(function (pg) { index.push({ kind: 'Page', id: '', title: pg[0], sub: pg[2], url: base + pg[1], hay: (pg[0] + ' ' + pg[2]).toLowerCase() }); });
  }
  var active = -1;
  function runSearch(q) {
    var list = document.getElementById('search-results'); if (!list) return;
    if (!index) buildIndex();
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    var res;
    if (!terms.length) {
      res = index.filter(function (r) { return r.kind === 'Page'; }).slice(0, 8);
    } else {
      res = index.map(function (r) {
        var s = 0;
        for (var i = 0; i < terms.length; i++) {
          var t = terms[i], at = r.hay.indexOf(t);
          if (at < 0) return null;
          s += (r.title.toLowerCase().indexOf(t) >= 0 ? 6 : 1) + (at === 0 ? 2 : 0);
          if (r.id && r.id.toLowerCase() === t) s += 20;
        }
        s += r.kind === 'Programme' ? 3 : r.kind === 'Page' ? 2 : 0;
        return { r: r, s: s };
      }).filter(Boolean).sort(function (a, b) { return b.s - a.s; }).slice(0, 14).map(function (x) { return x.r; });
    }
    active = -1;
    list.innerHTML = res.length ? res.map(function (r, i) {
      return '<li data-i="' + i + '"><a href="' + r.url + '"><span class="sr-kind">' + r.kind + '</span><span class="sr-title">' + U.esc(r.title) +
        '<span class="sr-sub">' + U.esc(r.sub.length > 150 ? r.sub.slice(0, 150) + '…' : r.sub) + '</span></span><span class="sr-id">' + U.esc(r.id) + '</span></a></li>';
    }).join('') : '<li class="search-empty">Nothing matches “' + U.esc(q) + '”. Try a district, a programme name or an outcome such as “stunting”.</li>';
  }
  var sInput = document.getElementById('search-input');
  if (sInput) {
    sInput.addEventListener('input', U.debounce(function () { runSearch(sInput.value); }, 80));
    sInput.addEventListener('keydown', function (e) {
      var items = document.querySelectorAll('#search-results li[data-i]');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        active = Math.max(0, Math.min(items.length - 1, active + (e.key === 'ArrowDown' ? 1 : -1)));
        items.forEach(function (li, i) { li.classList.toggle('is-active', i === active); });
        if (items[active]) items[active].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && items.length) {
        var a = items[Math.max(0, active)].querySelector('a'); if (a) window.location.href = a.href;
      }
    });
  }

  /* ---------------------------------------------------------------- shortlist */
  var SL_KEY = 'pec_shortlist_v2';
  U.shortlist = {
    all: function () { return U.store.get(SL_KEY, []); },
    has: function (id) { return U.shortlist.all().indexOf(id) >= 0; },
    toggle: function (id) {
      var l = U.shortlist.all(), i = l.indexOf(id);
      if (i >= 0) l.splice(i, 1); else l.push(id);
      U.store.set(SL_KEY, l); U.shortlist.sync(); return i < 0;
    },
    sync: function () {
      var l = U.shortlist.all();
      document.querySelectorAll('[data-shortlist-count]').forEach(function (el) { el.textContent = l.length ? l.length : ''; });
      document.querySelectorAll('[data-star]').forEach(function (b) {
        var on = l.indexOf(b.getAttribute('data-star')) >= 0;
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        var lbl = b.querySelector('.lbl'); if (lbl) lbl.textContent = on ? 'Saved to shortlist' : 'Save to shortlist';
        b.setAttribute('aria-label', (on ? 'Remove ' : 'Save ') + b.getAttribute('data-star') + (on ? ' from' : ' to') + ' shortlist');
      });
    }
  };
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-star]');
    if (b) { e.preventDefault(); e.stopPropagation(); U.shortlist.toggle(b.getAttribute('data-star')); }
  });
  U.shortlist.sync();

  /* ---------------------------------------------------------------- copy */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-copy]'); if (!b) return;
    var el = document.querySelector(b.getAttribute('data-copy'));
    var text = el ? el.innerText : '';
    var done = function () { var o = b.innerHTML; b.textContent = 'Copied'; setTimeout(function () { b.innerHTML = o; }, 1500); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
    else { var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (x) {} document.body.removeChild(ta); }
  });

  /* ---------------------------------------------------------------- rails */
  U.initRails = function (root) {
    (root || document).querySelectorAll('.rail-wrap').forEach(function (w) {
      var rail = w.querySelector('.rail'); if (!rail || w._init) return; w._init = true;
      var prev = w.querySelector('[data-dir="-1"]'), next = w.querySelector('[data-dir="1"]');
      var upd = function () {
        if (prev) prev.disabled = rail.scrollLeft < 8;
        if (next) next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 8;
      };
      w.querySelectorAll('.rail-arrow').forEach(function (b) {
        b.addEventListener('click', function () { rail.scrollBy({ left: +b.getAttribute('data-dir') * rail.clientWidth * 0.8, behavior: 'smooth' }); });
      });
      rail.addEventListener('scroll', U.debounce(upd, 60), { passive: true }); upd();
      window.addEventListener('resize', U.debounce(upd, 120));
    });
  };

  /* ---------------------------------------------------------------- claims (live from GitHub issues) */
  U.claims = function (cb) {
    var cacheKey = 'pec_claims_v2', cached = null;
    try { cached = JSON.parse(sessionStorage.getItem(cacheKey) || 'null'); } catch (e) {}
    if (cached && Date.now() - cached.t < 10 * 60 * 1000) { cb(cached.d); return; }
    if (!window.fetch || location.protocol === 'file:') { cb({}); return; }
    fetch('https://api.github.com/repos/' + REPO + '/issues?state=open&per_page=100', { headers: { Accept: 'application/vnd.github+json' } })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (issues) {
        var out = {};
        (issues || []).forEach(function (is) {
          var m = /^\s*\[claim\]\s*(P\d{2})/i.exec(is.title || '');
          if (m && !is.pull_request) out[m[1].toUpperCase()] = { url: is.html_url, by: (is.user || {}).login, at: is.created_at };
        });
        try { sessionStorage.setItem(cacheKey, JSON.stringify({ t: Date.now(), d: out })); } catch (e) {}
        cb(out);
      }).catch(function () { cb({}); });
  };
  U.issueUrl = function (template, title, body) {
    return 'https://github.com/' + REPO + '/issues/new?template=' + encodeURIComponent(template) +
      '&title=' + encodeURIComponent(title) + (body ? '&body=' + encodeURIComponent(body) : '');
  };
})();
