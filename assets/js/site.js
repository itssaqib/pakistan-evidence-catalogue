/* Shared site behaviour: nav, sticky masthead, copy buttons. */
(function () {
  'use strict';

  // Mobile nav
  var toggle = document.querySelector('.navtoggle');
  var nav = document.querySelector('.mainnav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // On narrow screens the facet rail would push results far down the page,
  // so collapse it behind a toggle. Desktop keeps every facet visible.
  var rail = document.getElementById('rail');
  if (rail && window.matchMedia('(max-width: 860px)').matches) {
    var fb = document.createElement('button');
    fb.type = 'button';
    fb.className = 'btn btn--ghost btn--sm';
    fb.setAttribute('aria-expanded', 'false');
    fb.setAttribute('aria-controls', 'rail');
    fb.style.cssText = 'margin-top:14px;width:100%';
    fb.textContent = 'Show filters';
    rail.parentNode.insertBefore(fb, rail);
    rail.hidden = true;
    fb.addEventListener('click', function () {
      rail.hidden = !rail.hidden;
      fb.setAttribute('aria-expanded', rail.hidden ? 'false' : 'true');
      fb.textContent = rail.hidden ? 'Show filters' : 'Hide filters';
    });
  }

  // Sticky masthead compaction
  var mast = document.querySelector('.masthead');
  if (mast) {
    var onScroll = function () {
      if (window.scrollY > 40) { mast.classList.add('is-stuck'); }
      else { mast.classList.remove('is-stuck'); }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Copy-to-clipboard
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.copybtn');
    if (!btn) return;
    var sel = btn.getAttribute('data-copy');
    var el = sel ? document.querySelector(sel) : null;
    var text = el ? (el.innerText || el.textContent) : (btn.getAttribute('data-text') || '');
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (err) {}
      document.body.removeChild(ta);
    }
  });
})();

/* ---------------------------------------------------------------------- */
/* Shared helpers                                                          */
/* ---------------------------------------------------------------------- */
var PEC = (function () {
  'use strict';

  function esc(s) {
    return String(s === undefined || s === null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function meter(rank, label) {
    var cells = '';
    for (var i = 1; i <= 3; i++) {
      cells += '<i class="' + (i <= rank ? 'on' : '') + '"></i>';
    }
    return '<span class="meter meter--' + rank + '" role="img" aria-label="Timing data quality: ' +
      esc(label) + '">' + cells + '</span><span class="meter-label">' + esc(label) + '</span>';
  }

  function dataPath(file) {
    var base = document.body.getAttribute('data-base') || '';
    return base + 'data/' + file;
  }

  function link(path) {
    var base = document.body.getAttribute('data-base') || '';
    return base + path;
  }

  function load(file) {
    return fetch(dataPath(file)).then(function (r) {
      if (!r.ok) throw new Error('Could not load ' + file);
      return r.json();
    });
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      var a = arguments, c = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(c, a); }, ms || 160);
    };
  }

  function toCSV(rows, fields) {
    var q = function (v) {
      v = v === undefined || v === null ? '' : String(v);
      return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
    };
    var out = [fields.join(',')];
    rows.forEach(function (r) {
      out.push(fields.map(function (f) {
        var v = r[f];
        if (Array.isArray(v)) v = v.join('; ');
        return q(v);
      }).join(','));
    });
    return out.join('\n');
  }

  function download(name, text, mime) {
    var blob = new Blob(['﻿' + text], { type: (mime || 'text/csv') + ';charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 500);
  }

  /* --------------------------------------------------------------------
     Facet table: generic filter + search + sort over a list of records
     -------------------------------------------------------------------- */
  function facetTable(cfg) {
    var state = { q: '', facets: {}, sort: cfg.defaultSort || null, dir: cfg.defaultDir || 'asc' };
    var railEl = document.querySelector(cfg.rail);
    var bodyEl = document.querySelector(cfg.body);
    var chipsEl = document.querySelector(cfg.chips);
    var countEl = document.querySelector(cfg.count);
    var searchEl = document.querySelector(cfg.search);
    var records = cfg.records;

    cfg.facetDefs.forEach(function (f) { state.facets[f.key] = []; });

    function values(f) {
      var counts = {};
      records.forEach(function (r) {
        var v = f.get(r);
        (Array.isArray(v) ? v : [v]).forEach(function (x) {
          if (x === '' || x === undefined || x === null) return;
          counts[x] = (counts[x] || 0) + 1;
        });
      });
      var keys = Object.keys(counts);
      if (f.order) {
        keys.sort(function (a, b) {
          var ia = f.order.indexOf(a), ib = f.order.indexOf(b);
          if (ia === -1) ia = 999; if (ib === -1) ib = 999;
          return ia - ib || a.localeCompare(b);
        });
      } else {
        keys.sort(function (a, b) { return counts[b] - counts[a] || a.localeCompare(b); });
      }
      return keys.map(function (k) { return { value: k, n: counts[k] }; });
    }

    function buildRail() {
      if (!railEl) return;
      var html = '';
      cfg.facetDefs.forEach(function (f) {
        html += '<div class="facet"><h3>' + esc(f.label) + '</h3>';
        values(f).forEach(function (v) {
          var id = f.key + '-' + v.value.replace(/[^a-z0-9]+/gi, '-').toLowerCase();
          html += '<label for="' + esc(id) + '"><input type="checkbox" id="' + esc(id) +
            '" data-facet="' + esc(f.key) + '" value="' + esc(v.value) + '">' +
            '<span>' + esc(v.value) + '</span><span class="count">' + v.n + '</span></label>';
        });
        html += '</div>';
      });
      railEl.innerHTML = html;
      railEl.addEventListener('change', function (e) {
        var cb = e.target;
        if (!cb.matches('input[data-facet]')) return;
        var key = cb.getAttribute('data-facet');
        var arr = state.facets[key];
        var i = arr.indexOf(cb.value);
        if (cb.checked && i === -1) arr.push(cb.value);
        if (!cb.checked && i > -1) arr.splice(i, 1);
        render();
      });
    }

    function matches(r) {
      for (var i = 0; i < cfg.facetDefs.length; i++) {
        var f = cfg.facetDefs[i];
        var sel = state.facets[f.key];
        if (!sel.length) continue;
        var v = f.get(r);
        var vals = Array.isArray(v) ? v : [v];
        var hit = sel.some(function (s) { return vals.indexOf(s) > -1; });
        if (!hit) return false;
      }
      if (state.q) {
        var hay = cfg.searchFields.map(function (k) {
          var v = r[k];
          return Array.isArray(v) ? v.join(' ') : (v || '');
        }).join(' ').toLowerCase();
        var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
        for (var j = 0; j < terms.length; j++) {
          if (hay.indexOf(terms[j]) === -1) return false;
        }
      }
      return true;
    }

    function sorted(list) {
      if (!state.sort) return list;
      var key = state.sort, dir = state.dir === 'desc' ? -1 : 1;
      return list.slice().sort(function (a, b) {
        var va = a[key], vb = b[key];
        if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir;
        return String(va).localeCompare(String(vb), 'en', { numeric: true }) * dir;
      });
    }

    function renderChips() {
      if (!chipsEl) return;
      var html = '';
      cfg.facetDefs.forEach(function (f) {
        state.facets[f.key].forEach(function (v) {
          html += '<span class="chip">' + esc(f.label) + ': ' + esc(v) +
            ' <button type="button" data-clear-facet="' + esc(f.key) + '" data-clear-value="' +
            esc(v) + '" aria-label="Remove filter ' + esc(v) + '">&times;</button></span>';
        });
      });
      if (state.q) {
        html += '<span class="chip">Search: ' + esc(state.q) +
          ' <button type="button" data-clear-search aria-label="Clear search">&times;</button></span>';
      }
      if (html) {
        html += '<button type="button" class="copybtn" data-clear-all style="margin-top:0">Clear all</button>';
      }
      chipsEl.innerHTML = html;
    }

    var current = records;

    function render() {
      current = sorted(records.filter(matches));
      bodyEl.innerHTML = current.length
        ? current.map(cfg.row).join('')
        : '<tr><td colspan="' + (cfg.colspan || 6) + '"><div class="empty">No records match these filters. ' +
          'Try removing one.</div></td></tr>';
      if (countEl) {
        countEl.innerHTML = '<strong>' + current.length + '</strong> of ' + records.length +
          ' ' + (cfg.noun || 'records');
      }
      renderChips();
      syncSortHeaders();
      if (cfg.onRender) cfg.onRender(current);
    }

    function syncSortHeaders() {
      document.querySelectorAll(cfg.table + ' th.sortable').forEach(function (th) {
        var k = th.getAttribute('data-sort');
        if (k === state.sort) { th.setAttribute('aria-sort', state.dir === 'asc' ? 'ascending' : 'descending'); }
        else { th.removeAttribute('aria-sort'); }
        var arrow = th.querySelector('.arrow');
        if (arrow) arrow.innerHTML = k === state.sort ? (state.dir === 'asc' ? '&#9650;' : '&#9660;') : '&#8597;';
      });
    }

    if (searchEl) {
      searchEl.addEventListener('input', debounce(function () {
        state.q = searchEl.value.trim();
        render();
      }, 140));
    }

    if (chipsEl) {
      chipsEl.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        if (b.hasAttribute('data-clear-all')) {
          cfg.facetDefs.forEach(function (f) { state.facets[f.key] = []; });
          state.q = '';
          if (searchEl) searchEl.value = '';
          railEl.querySelectorAll('input[type=checkbox]').forEach(function (c) { c.checked = false; });
          render(); return;
        }
        if (b.hasAttribute('data-clear-search')) {
          state.q = ''; if (searchEl) searchEl.value = ''; render(); return;
        }
        var key = b.getAttribute('data-clear-facet');
        var val = b.getAttribute('data-clear-value');
        if (key) {
          var arr = state.facets[key];
          var i = arr.indexOf(val);
          if (i > -1) arr.splice(i, 1);
          var cb = railEl.querySelector('input[data-facet="' + key + '"][value="' + val.replace(/"/g, '\\"') + '"]');
          if (cb) cb.checked = false;
          render();
        }
      });
    }

    document.querySelectorAll(cfg.table + ' th.sortable').forEach(function (th) {
      th.setAttribute('tabindex', '0');
      var act = function () {
        var k = th.getAttribute('data-sort');
        if (state.sort === k) { state.dir = state.dir === 'asc' ? 'desc' : 'asc'; }
        else { state.sort = k; state.dir = th.getAttribute('data-dir') || 'asc'; }
        render();
      };
      th.addEventListener('click', act);
      th.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); act(); }
      });
    });

    var dlBtn = document.querySelector(cfg.download || '#dl-filtered');
    if (dlBtn) {
      dlBtn.addEventListener('click', function () {
        download(cfg.downloadName || 'filtered.csv', toCSV(current, cfg.downloadFields));
      });
    }

    // deep link: ?q=  &  #facet=value
    var params = new URLSearchParams(window.location.search);
    if (params.get('q') && searchEl) { searchEl.value = params.get('q'); state.q = params.get('q'); }
    cfg.facetDefs.forEach(function (f) {
      var v = params.get(f.key);
      if (v) { v.split('|').forEach(function (x) { state.facets[f.key].push(x); }); }
    });

    buildRail();
    cfg.facetDefs.forEach(function (f) {
      state.facets[f.key].forEach(function (v) {
        var cb = railEl.querySelector('input[data-facet="' + f.key + '"][value="' + v.replace(/"/g, '\\"') + '"]');
        if (cb) cb.checked = true;
      });
    });
    render();

    return { render: render, state: state, getCurrent: function () { return current; } };
  }

  /* --------------------------------------------------------------------
     SVG charts
     -------------------------------------------------------------------- */
  function barChart(el, data, opts) {
    opts = opts || {};
    var W = 640, rowH = opts.rowH || 26, padL = opts.padL || 170, padR = 48, padT = 8;
    var H = padT + data.length * rowH + 24;
    var max = Math.max.apply(null, data.map(function (d) { return d.value; })) || 1;
    var inner = W - padL - padR;
    var s = '';
    // gridlines
    for (var g = 0; g <= 4; g++) {
      var x = padL + (inner * g / 4);
      s += '<line class="gl" x1="' + x + '" y1="' + padT + '" x2="' + x + '" y2="' + (H - 24) + '"/>';
      s += '<text x="' + x + '" y="' + (H - 8) + '" text-anchor="middle">' +
        Math.round(max * g / 4) + '</text>';
    }
    data.forEach(function (d, i) {
      var y = padT + i * rowH;
      var w = Math.max(1, inner * d.value / max);
      s += '<text x="' + (padL - 10) + '" y="' + (y + rowH / 2 + 4) + '" text-anchor="end">' +
        esc(d.label) + '</text>';
      s += '<rect class="bar' + (d.alt ? ' alt' : '') + '" x="' + padL + '" y="' + (y + 5) +
        '" width="' + w + '" height="' + (rowH - 11) + '" rx="1"/>';
      s += '<text class="val" x="' + (padL + w + 7) + '" y="' + (y + rowH / 2 + 4) + '">' +
        d.value + '</text>';
    });
    s += '<line class="ax" x1="' + padL + '" y1="' + padT + '" x2="' + padL + '" y2="' + (H - 24) + '"/>';
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    el.setAttribute('role', 'img');
    el.innerHTML = s;
  }

  function columnChart(el, data, opts) {
    opts = opts || {};
    var W = 640, H = opts.height || 190, padL = 34, padB = 34, padT = 12, padR = 8;
    var max = Math.max.apply(null, data.map(function (d) { return d.value; })) || 1;
    var innerW = W - padL - padR, innerH = H - padT - padB;
    var bw = innerW / data.length;
    var s = '';
    for (var g = 0; g <= 3; g++) {
      var y = padT + innerH - (innerH * g / 3);
      s += '<line class="gl" x1="' + padL + '" y1="' + y + '" x2="' + (W - padR) + '" y2="' + y + '"/>';
      s += '<text x="' + (padL - 7) + '" y="' + (y + 4) + '" text-anchor="end">' +
        Math.round(max * g / 3) + '</text>';
    }
    data.forEach(function (d, i) {
      var h = innerH * d.value / max;
      var x = padL + i * bw + bw * 0.18;
      s += '<rect class="bar" x="' + x + '" y="' + (padT + innerH - h) + '" width="' + (bw * 0.64) +
        '" height="' + Math.max(1, h) + '" rx="1"><title>' + esc(d.label) + ': ' + d.value + '</title></rect>';
      s += '<text x="' + (padL + i * bw + bw / 2) + '" y="' + (H - 12) + '" text-anchor="middle">' +
        esc(d.label) + '</text>';
    });
    s += '<line class="ax" x1="' + padL + '" y1="' + (padT + innerH) + '" x2="' + (W - padR) +
      '" y2="' + (padT + innerH) + '"/>';
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    el.setAttribute('role', 'img');
    el.innerHTML = s;
  }

  /* Rollout timeline for a single programme */
  function timeline(el, prog) {
    var years = (prog.rollout_window + ' ' + prog.start_year).match(/\b(19|20)\d{2}\b/g) || [];
    years = years.map(Number);
    var start = Math.min.apply(null, years.length ? years : [2000]);
    var end = Math.max.apply(null, years.length ? years : [2024]);
    if (end - start < 2) end = start + 2;
    var axisStart = Math.min(start - 1, 1998);
    var axisEnd = Math.max(end + 1, 2024);
    var W = 640, H = 72, padL = 8, padR = 8, y = 34;
    var innerW = W - padL - padR;
    var x = function (yr) { return padL + innerW * (yr - axisStart) / (axisEnd - axisStart); };
    var s = '';
    for (var yr = axisStart; yr <= axisEnd; yr++) {
      if (yr % 5 !== 0) continue;
      s += '<line class="tickline" x1="' + x(yr) + '" y1="14" x2="' + x(yr) + '" y2="' + (y + 12) + '"/>';
      s += '<text x="' + x(yr) + '" y="' + (y + 26) + '" text-anchor="middle">' + yr + '</text>';
    }
    s += '<line class="axis" x1="' + padL + '" y1="' + (y + 12) + '" x2="' + (W - padR) + '" y2="' + (y + 12) + '"/>';
    s += '<rect class="band" x="' + x(start) + '" y="' + (y - 10) + '" width="' +
      Math.max(2, x(end) - x(start)) + '" height="20" rx="1"/>';
    s += '<line class="bandline" x1="' + x(start) + '" y1="' + y + '" x2="' + x(end) + '" y2="' + y + '"/>';
    years.forEach(function (yr) {
      s += '<circle class="mark" cx="' + x(yr) + '" cy="' + y + '" r="3.5"><title>' + yr + '</title></circle>';
    });
    s += '<text class="lbl" x="' + x(start) + '" y="' + (y - 16) + '">' + start + '</text>';
    s += '<text class="lbl" x="' + x(end) + '" y="' + (y - 16) + '" text-anchor="end">' +
      (end === start ? '' : end) + '</text>';
    el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    el.setAttribute('role', 'img');
    el.setAttribute('aria-label', 'Rollout window ' + start + ' to ' + end);
    el.innerHTML = s;
  }

  return {
    esc: esc, meter: meter, load: load, link: link, facetTable: facetTable,
    barChart: barChart, columnChart: columnChart, timeline: timeline,
    toCSV: toCSV, download: download, debounce: debounce
  };
})();
