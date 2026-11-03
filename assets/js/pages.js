/* Page controllers. Each page sets <body data-page="...">. */
(function () {
  'use strict';
  var U = window.PECU, PEC = window.PEC, M = window.PECMap, CH = window.PECCharts;
  var page = document.body.getAttribute('data-page');
  var REG_NAME = { ALL: 'National', PB: 'Punjab', SD: 'Sindh', KP: 'Khyber Pakhtunkhwa', BA: 'Balochistan', FATA: 'Ex-FATA',
    AJK: 'Azad Kashmir', GB: 'Gilgit-Baltistan', ICT: 'Islamabad' };
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ================================================================ statistics for the power calculator */
  function lgamma(x) {
    var g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059,
      12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x);
    x -= 1; var a = c[0], t = x + g + 0.5;
    for (var i = 1; i < g + 2; i++) a += c[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }
  function betacf(a, b, x) {
    var MAXIT = 200, EPS = 3e-14, FPMIN = 1e-300, qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap;
    if (Math.abs(d) < FPMIN) d = FPMIN; d = 1 / d; var h = d;
    for (var m = 1; m <= MAXIT; m++) {
      var m2 = 2 * m, aa = m * (b - m) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN; c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN; d = 1 / d; h *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN; c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN; d = 1 / d;
      var del = d * c; h *= del; if (Math.abs(del - 1) < EPS) break;
    }
    return h;
  }
  function ibeta(x, a, b) {
    if (x <= 0) return 0; if (x >= 1) return 1;
    var bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
  }
  function tcdf(t, df) { var x = df / (df + t * t), p = 0.5 * ibeta(x, df / 2, 0.5); return t >= 0 ? 1 - p : p; }
  function tinv(p, df) { var lo = -60, hi = 60; for (var i = 0; i < 120; i++) { var mid = (lo + hi) / 2; if (tcdf(mid, df) < p) lo = mid; else hi = mid; } return (lo + hi) / 2; }
  /* Burlig, Preonas & Woerman (2020) panel DiD MDE with AR(1) errors, in residual-SD units */
  function mde(J, P, m, r, phi, alpha, power) {
    phi = Math.min(Math.max(phi, 0), 0.99);
    var S1 = function (n) { return n < 2 ? 0 : phi * ((n - 1) - n * phi + Math.pow(phi, n)) / Math.pow(1 - phi, 2); };
    var psiB = m < 2 ? 0 : 2 * S1(m) / (m * (m - 1)), psiA = r < 2 ? 0 : 2 * S1(r) / (r * (r - 1));
    var psiX = ((1 - Math.pow(phi, m)) / (1 - phi)) * (phi * (1 - Math.pow(phi, r)) / (1 - phi)) / (m * r);
    var V = (1 / (P * (1 - P) * J)) * ((m + r) / (m * r) + (m - 1) / m * psiB + (r - 1) / r * psiA - 2 * psiX);
    var df = Math.max(1, J - 2), t1 = tinv(1 - alpha / 2, df), t2 = tinv(power, df);
    return { mde: (t1 + t2) * Math.sqrt(Math.max(V, 0)), t1: t1, t2: t2, V: V, df: df };
  }
  function bindMDE(form, out) {
    if (!form) return;
    var calc = function () {
      var v = function (n) { return parseFloat(form.elements[n].value); };
      var J = Math.round(v('J')), P = v('P'), m = Math.round(v('m')), r = Math.round(v('r')), phi = v('phi'), a = v('alpha'), pw = v('power');
      if (!(J > 2 && P > 0 && P < 1 && m >= 1 && r >= 1)) { out.querySelector('.big').textContent = '\u2014'; return; }
      var res = mde(J, P, m, r, phi, a, pw), treated = Math.round(J * P);
      out.querySelector('.big').textContent = res.mde.toFixed(2);
      out.querySelector('.expl').innerHTML = 'With ' + J + ' districts, about ' + treated + ' treated, ' + m + ' pre and ' + r +
        ' post periods and serial correlation of ' + phi.toFixed(2) + ', the smallest effect detectable with ' + Math.round(pw * 100) +
        '% power at the ' + Math.round(a * 100) + '% level is <strong>' + res.mde.toFixed(2) + ' residual standard deviations</strong>.' +
        (treated < 20 ? ' Fewer than 20 treated districts: use wild cluster bootstrap or randomisation inference for the test.' : '');
      out.querySelector('.formula').textContent = 't(' + res.df + ') critical values ' + res.t1.toFixed(2) + ' and ' + res.t2.toFixed(2) + '; variance factor ' + res.V.toFixed(4) + '.';
    };
    form.addEventListener('input', calc); calc();
  }

  /* ================================================================ Stata do-file generator */
  function dofile(p) {
    var L = [], add = function (s) { L.push(s == null ? '' : s); };
    var rows = PEC.matrix.filter(function (m) { return m.pid === p.id; });
    var few = (p.mde.J * p.mde.P) < 20;
    add('* ' + '='.repeat(74));
    add('* ' + p.id + '  ' + p.name);
    add('* Starter do-file generated by the Pakistan Evidence Catalogue v' + PEC.meta.version);
    add('* ' + '='.repeat(74));
    add('* Rollout     : ' + p.window);
    add('* Unit        : ' + p.unit);
    add('* Assignment  : ' + p.assign);
    add('* Timing data : ' + p.timing_src);
    add('* Threats     : ' + p.threats);
    add('*');
    add('* Outcomes mapped in the catalogue (pick one as y):');
    rows.slice(0, 8).forEach(function (m) { add('*   ' + m.oid + '  ' + m.outcome + '  [' + m.keys.join(', ') + ']'); });
    add('* ' + '-'.repeat(74));
    add('');
    add('version 16');
    add('clear all');
    add('set more off');
    add('global PEC  "C:/path/to/pakistan-evidence-catalogue"');
    add('global WORK "C:/path/to/your/project"');
    add('');
    add('* ---------------------------------------------------------------------------');
    add('* 1. Treatment timing: one row per district, first year treated');
    add('* ---------------------------------------------------------------------------');
    var fp = p.footprint;
    if (fp) {
      add('* Documented phases from the catalogue (sources on the programme page).');
      add('* ' + (fp.final === 'listed' ? 'This list is the full documented footprint.' :
        fp.final === 'scope' ? restLabel(fp) + ' was covered by about ' + fp.final_year + ' - fill those years from the timing source.' :
          'Partial list: later districts must come from the timing source above.'));
      add('clear');
      add('input str40 pec_unit_id int first_treated_year');
      var seen = {};
      fp.phases.slice().sort(function (a, b) { return a.year - b.year; }).forEach(function (ph) {
        ph.units.forEach(function (u) { if (!seen[u]) { seen[u] = 1; add('"' + u + '" ' + ph.year); } });
      });
      add('end');
      add('save "$WORK/rollout_' + p.id.toLowerCase() + '.dta", replace');
    } else {
      add('* No district list is documented yet. Build rollout.csv with columns');
      add('*   pec_unit_id, first_treated_year   (blank = never treated)');
      add('* using the timing source above, then:');
      add('import delimited using "$WORK/rollout.csv", varnames(1) clear');
      add('save "$WORK/rollout_' + p.id.toLowerCase() + '.dta", replace');
    }
    add('');
    add('* ---------------------------------------------------------------------------');
    add('* 2. District-year panel on constant 2019 boundaries');
    add('* ---------------------------------------------------------------------------');
    add('use "$WORK/panel.dta", clear      // your outcome panel with a district name and year');
    add('do "$PEC/toolkit/stata/01_harmonise_districts.do"   // adds pec_unit_id');
    add('collapse (mean) y [aw=weight], by(pec_unit_id year)   // edit: outcome and weight');
    add('merge m:1 pec_unit_id using "$WORK/rollout_' + p.id.toLowerCase() + '.dta", keep(master match) nogenerate');
    add('generate gvar = first_treated_year');
    add('replace  gvar = 0 if missing(gvar)                 // csdid: 0 = never treated');
    add('generate Ei   = first_treated_year                 // did_imputation: missing = never');
    add('generate rel_time = year - first_treated_year');
    add('generate D = (year >= first_treated_year) & !missing(first_treated_year)');
    add('egen id = group(pec_unit_id)');
    add('xtset id year');
    add('');
    add('* ---------------------------------------------------------------------------');
    add('* 3. Estimation');
    add('* ---------------------------------------------------------------------------');
    add('* 3a. How much of two-way FE comes from already-treated controls?');
    add('bacondecomp y D, ddetail');
    add('');
    add('* 3b. Callaway-Sant\'Anna, not-yet-treated comparison, doubly robust');
    add('csdid y, ivar(id) time(year) gvar(gvar) notyet method(dripw)');
    add('estat simple');
    add('estat event, window(-5 5) estore(cs_event)');
    add('csdid_plot');
    add('');
    add('* 3c. Borusyak-Jaravel-Spiess imputation');
    add('did_imputation y id year Ei, horizons(0/5) pretrends(5) autosample cluster(id)');
    add('event_plot, default_look');
    add('');
    add('* 3d. Sun-Abraham interaction-weighted event study (lead 1 omitted)');
    add('generate never_treated = missing(first_treated_year)');
    add('generate lead5 = rel_time == -5');
    add('generate lead4 = rel_time == -4');
    add('generate lead3 = rel_time == -3');
    add('generate lead2 = rel_time == -2');
    add('generate lag0  = rel_time == 0');
    add('generate lag1  = rel_time == 1');
    add('generate lag2  = rel_time == 2');
    add('generate lag3  = rel_time == 3');
    add('generate lag4  = rel_time == 4');
    add('generate lag5  = rel_time == 5');
    add('eventstudyinteract y lead5 lead4 lead3 lead2 lag0 lag1 lag2 lag3 lag4 lag5, ///');
    add('    cohort(first_treated_year) control_cohort(never_treated) absorb(i.id i.year) vce(cluster id)');
    if (p.methods.indexOf('Regression discontinuity') >= 0) {
      add('');
      add('* 3e. Regression discontinuity at the assignment threshold (see Assignment above)');
      add('*     Run on the unit-level running variable, not the district panel.');
      add('* rdrobust y score, c(CUTOFF) kernel(triangular) bwselect(mserd) vce(cluster id)');
      add('* rdplot   y score, c(CUTOFF) binselect(es)');
      add('* rddensity score, c(CUTOFF)');
    }
    if (p.methods.indexOf('Treatment switches off') >= 0) {
      add('');
      add('* 3f. Treatment switches off again: estimator that allows exit');
      add('did_multiplegt_dyn y id year D, effects(5) placebo(3) cluster(id)');
    }
    if (few || p.methods.indexOf('Synthetic control') >= 0) {
      add('');
      add('* 3g. Few treated districts (about ' + Math.round(p.mde.J * p.mde.P) + '): synthetic DiD and wild bootstrap');
      add('sdid y id year D, vce(placebo) reps(500) seed(20261104) method(sdid) graph');
      add('reghdfe y D, absorb(id year) vce(cluster id)');
      add('boottest D, cluster(id) reps(9999) seed(20261104) nograph');
    }
    if (p.methods.indexOf('Continuous treatment') >= 0) {
      add('');
      add('* 3h. Continuous intensity: dose-response baseline (see did_multiplegt_dyn help');
      add('*     for heterogeneity-robust estimators with non-binary treatment)');
      add('* reghdfe y c.dose, absorb(id year) vce(cluster id)');
    }
    add('');
    add('* ---------------------------------------------------------------------------');
    add('* 4. Sensitivity to parallel-trend violations (Rambachan-Roth)');
    add('* ---------------------------------------------------------------------------');
    add('estimates restore cs_event');
    add('matrix list e(b)      // window(-5 5): Tm5..Tm1 are positions 3-7, Tp0..Tp5 are 8-13');
    add('honestdid, pre(3/7) post(8/13) mvec(0(0.5)2) coefplot');
    add('');
    add('* ---------------------------------------------------------------------------');
    add('* 5. Minimum detectable effect (Burlig, Preonas & Woerman 2020; AR(1) errors)');
    add('* ---------------------------------------------------------------------------');
    add('scalar J     = ' + p.mde.J + '        // districts');
    add('scalar P     = ' + p.mde.P + '      // share treated');
    add('scalar m     = 3         // pre periods');
    add('scalar r     = 3         // post periods');
    add('scalar phi   = 0.4       // residual serial correlation');
    add('scalar S1m   = cond(m < 2, 0, phi*((m-1) - m*phi + phi^m)/(1-phi)^2)');
    add('scalar S1r   = cond(r < 2, 0, phi*((r-1) - r*phi + phi^r)/(1-phi)^2)');
    add('scalar psiB  = cond(m < 2, 0, 2*S1m/(m*(m-1)))');
    add('scalar psiA  = cond(r < 2, 0, 2*S1r/(r*(r-1)))');
    add('scalar psiX  = ((1-phi^m)/(1-phi)) * (phi*(1-phi^r)/(1-phi)) / (m*r)');
    add('scalar V     = (1/(P*(1-P)*J)) * ((m+r)/(m*r) + (m-1)/m*psiB + (r-1)/r*psiA - 2*psiX)');
    add('scalar MDE   = (invttail(J-2, 0.025) + invttail(J-2, 0.20)) * sqrt(V)');
    add('display "MDE (residual SD units): " %5.3f MDE');
    return L.join('\n') + '\n';
  }

  /* ================================================================ legends */
  var RN = { PB: 'Punjab', SD: 'Sindh', KP: 'Khyber Pakhtunkhwa', BA: 'Balochistan', AJK: 'Azad Kashmir', GB: 'Gilgit-Baltistan', ICT: 'Islamabad', FATA: 'ex-FATA' };
  function restLabel(fp) { return fp.final_regions ? 'Rest of ' + fp.final_regions.map(function (r) { return RN[r] || r; }).join(', ') : 'Rest of scope'; }
  function inFinal(fp, unit) { return !fp.final_regions || M.unitsFor(fp.final_regions).indexOf(unit) >= 0; }

  function fpLegend(p) {
    var C = M.COL, it = [], fp = p.footprint;
    if (fp) {
      var ph = fp.phases.slice().sort(function (a, b) { return a.year - b.year; });
      ph.forEach(function (x, k) { it.push([k === 0 ? C.p1 : k === 1 ? C.p2 : C.later, x.label + ' (' + x.year + ')']); });
      var cls = M.footprint(p), left = Object.keys(cls).some(function (k) { return cls[k] === 'scope'; });
      if (fp.final === 'scope') { it.push([C.later, restLabel(fp) + ' by ' + fp.final_year]); if (fp.final_regions && left) it.push([C.scope, 'In scope, timing not documented']); }
      else if (fp.final === 'partial') it.push([C.scope, 'In scope, timing not documented']);
      else if (left) it.push([C.scope, 'Same province, not listed']);
    } else {
      it.push([C.scope, 'Stated scope: district timing not documented']);
    }
    it.push([C.out, 'Outside scope']);
    return it.map(function (x) { return '<span><i class="sw" style="background:' + x[0] + '"></i>' + U.esc(x[1]) + '</span>'; }).join('');
  }
  function fpMeaning(p, unit) {
    var cls = M.footprint(p)[unit], fp = p.footprint;
    if (cls === 'out') return 'Outside stated scope';
    if (cls === 'scope') return fp && fp.final === 'listed' ? 'Same province, not in the documented list' : 'In stated scope; district timing not documented';
    if (fp) {
      var hits = fp.phases.filter(function (ph) { return ph.units.indexOf(unit) >= 0; });
      if (hits.length) return hits.map(function (h) { return h.label + ', ' + h.year; }).join('; ');
      if (fp.final === 'scope' && inFinal(fp, unit)) return 'Covered by about ' + fp.final_year;
    }
    return '';
  }

  /* ================================================================ HOME */
  function home() {
    var cv = document.getElementById('hero-map'); if (!cv) return;
    var years = PEC.meta.years, yi = years.length - 1;
    var map = new M.Map(cv, { cover: false });
    var yr = document.getElementById('hero-yr'), slider = document.getElementById('hero-slider'), play = document.getElementById('hero-play');
    var set = function (i) { yi = i; map.set({ mode: 'density', yearIndex: i }); if (yr) yr.textContent = years[i]; if (slider) slider.value = i; };
    var timer = null;
    var run = function () {
      clearInterval(timer); var i = 0; set(0);
      timer = setInterval(function () { i++; if (i >= years.length) { clearInterval(timer); timer = null; return; } set(i); }, 190);
    };
    if (slider) { slider.max = years.length - 1; slider.addEventListener('input', function () { clearInterval(timer); set(+slider.value); }); }
    if (play) play.addEventListener('click', run);
    if (reduced) set(years.length - 1); else run();
    var lg = document.getElementById('hero-ramp');
    if (lg) lg.innerHTML = M.COL.dens.slice(1).map(function (c) { return '<i style="background:' + c + '"></i>'; }).join('');
    M.lazyTiles(); U.initRails();
  }

  /* ================================================================ BROWSE */
  function browse() {
    var grid = document.getElementById('grid'); if (!grid) return;
    var tiles = Array.prototype.slice.call(grid.querySelectorAll('.tile[data-pid]'));
    var tableHost = document.getElementById('table-view'), count = document.getElementById('count'), chips = document.getElementById('chips');
    var q = document.getElementById('q'), sortSel = document.getElementById('sort');
    var F = {
      macro: { label: 'Domain', get: function (p) { return [p.macro]; }, order: PEC.meta.macro_order },
      region: { label: 'Province', get: function (p) { return p.regions.map(function (r) { return REG_NAME[r] || r; }); } },
      tq: { label: 'Timing data', get: function (p) { return [p.tq]; }, order: ['High', 'Medium-high', 'Medium', 'Low'] },
      evidence: { label: 'Evidence', get: function (p) { return [p.evidence_status]; }, order: ['Unstudied', 'Limited', 'Published causal work'] },
      unit: { label: 'Rollout unit', get: function (p) { return [p.unit_class]; } },
      method: { label: 'Design', get: function (p) { return p.methods; } },
      kind: { label: 'Type', get: function (p) { return [p.kind]; } },
      map: { label: 'Map', get: function (p) { return [p.footprint ? 'Documented districts' : 'Scope only']; } }
    };
    var state = { q: '', sort: 'id', view: 'grid', f: {} };
    Object.keys(F).forEach(function (k) { state.f[k] = []; });
    var params = new URLSearchParams(location.search);
    Object.keys(F).forEach(function (k) { var v = params.get(k); if (v) state.f[k] = v.split('|'); });
    if (params.get('q')) state.q = params.get('q');
    if (params.get('sort')) state.sort = params.get('sort');
    if (q) q.value = state.q; if (sortSel) sortSel.value = state.sort;

    // facet panels
    Object.keys(F).forEach(function (k) {
      var host = document.querySelector('.fgroup[data-f="' + k + '"] .fpanel'); if (!host) return;
      var counts = {};
      PEC.programmes.forEach(function (p) { F[k].get(p).forEach(function (v) { counts[v] = (counts[v] || 0) + 1; }); });
      var keys = Object.keys(counts).sort(function (a, b) {
        var o = F[k].order; if (o) { var ia = o.indexOf(a), ib = o.indexOf(b); return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib); }
        return counts[b] - counts[a] || a.localeCompare(b);
      });
      host.innerHTML = keys.map(function (v) {
        return '<label><input type="checkbox" value="' + U.esc(v) + '"' + (state.f[k].indexOf(v) >= 0 ? ' checked' : '') + '> ' + U.esc(v) + '<span class="c">' + counts[v] + '</span></label>';
      }).join('');
      host.addEventListener('change', function (e) {
        var v = e.target.value, a = state.f[k], i = a.indexOf(v);
        if (e.target.checked && i < 0) a.push(v); if (!e.target.checked && i >= 0) a.splice(i, 1);
        render();
      });
    });
    document.querySelectorAll('.fgroup > button').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.stopPropagation(); var g = b.parentNode, open = !g.classList.contains('is-open');
        document.querySelectorAll('.fgroup.is-open').forEach(function (x) { x.classList.remove('is-open'); x.querySelector('button').setAttribute('aria-expanded', 'false'); });
        if (open) { g.classList.add('is-open'); b.setAttribute('aria-expanded', 'true'); }
      });
    });
    document.addEventListener('click', function (e) { if (!e.target.closest('.fgroup')) document.querySelectorAll('.fgroup.is-open').forEach(function (x) { x.classList.remove('is-open'); }); });

    function match(p) {
      for (var k in F) { var sel = state.f[k]; if (!sel.length) continue; var vals = F[k].get(p); if (!sel.some(function (s) { return vals.indexOf(s) >= 0; })) return false; }
      if (state.q) {
        var hay = (p.id + ' ' + p.name + ' ' + p.short + ' ' + p.domain + ' ' + p.agency + ' ' + p.scope + ' ' + p.window + ' ' + p.ident + ' ' + p.methods.join(' ')).toLowerCase();
        var t = state.q.toLowerCase().split(/\s+/).filter(Boolean);
        for (var i = 0; i < t.length; i++) if (hay.indexOf(t[i]) < 0) return false;
      }
      return true;
    }
    var SORTS = {
      id: function (a, b) { return a.id.localeCompare(b.id); },
      tq: function (a, b) { return b.tq_rank - a.tq_rank || a.id.localeCompare(b.id); },
      start: function (a, b) { return (a.start_y || 9999) - (b.start_y || 9999) || a.id.localeCompare(b.id); },
      outcomes: function (a, b) { return b.n_outcomes - a.n_outcomes || a.id.localeCompare(b.id); },
      name: function (a, b) { return a.short.localeCompare(b.short); }
    };
    var current = [];
    function render() {
      current = PEC.programmes.filter(match).sort(SORTS[state.sort] || SORTS.id);
      var ids = {}; current.forEach(function (p, i) { ids[p.id] = i; });
      tiles.forEach(function (t) { var id = t.getAttribute('data-pid'); t.hidden = !(id in ids); t.style.order = id in ids ? ids[id] : 999; });
      grid.querySelector('.empty').hidden = current.length > 0;
      count.innerHTML = '<strong>' + current.length + '</strong> of ' + PEC.programmes.length + ' programmes and natural experiments';
      document.querySelectorAll('.fgroup').forEach(function (g) { var n = state.f[g.getAttribute('data-f')].length; g.querySelector('.n').textContent = n ? n : ''; });
      var ch = '';
      Object.keys(F).forEach(function (k) { state.f[k].forEach(function (v) { ch += '<span class="chip">' + U.esc(F[k].label + ': ' + v) + ' <button type="button" data-k="' + k + '" data-v="' + U.esc(v) + '" aria-label="Remove filter">\u00d7</button></span>'; }); });
      if (state.q) ch += '<span class="chip">Search: ' + U.esc(state.q) + ' <button type="button" data-k="q" aria-label="Clear search">\u00d7</button></span>';
      if (ch) ch += '<button type="button" class="textbtn" data-k="all">Clear all</button>';
      chips.innerHTML = ch;
      if (state.view === 'table') renderTable();
      var p2 = new URLSearchParams();
      Object.keys(F).forEach(function (k) { if (state.f[k].length) p2.set(k, state.f[k].join('|')); });
      if (state.q) p2.set('q', state.q); if (state.sort !== 'id') p2.set('sort', state.sort);
      var qs = p2.toString(); try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '')); } catch (e) {}
    }
    function renderTable() {
      tableHost.innerHTML = '<div class="table-wrap"><table class="t"><thead><tr><th>ID</th><th>Programme</th><th class="hide-sm">Domain</th><th class="hide-sm">Rollout</th><th>Timing data</th><th class="hide-sm">Evidence</th><th class="num">Outcomes</th></tr></thead><tbody>' +
        current.map(function (p) {
          return '<tr><td class="id">' + p.id + '</td><td class="wide"><a class="ttl" href="' + U.progUrl(p.id) + '">' + U.esc(p.short) + '</a><span class="sub">' + U.esc(p.agency) + '</span></td><td class="hide-sm">' + U.esc(p.macro) +
            '</td><td class="hide-sm">' + U.span(p) + '</td><td>' + U.meter(p.tq_rank) + '<span class="ml">' + p.tq + '</span></td><td class="hide-sm"><span class="ev" data-s="' + p.evidence_status + '">' + p.evidence_status + '</span></td><td class="num">' + p.n_outcomes + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    }
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return; var k = b.getAttribute('data-k');
      if (k === 'all') { Object.keys(F).forEach(function (x) { state.f[x] = []; }); state.q = ''; if (q) q.value = ''; document.querySelectorAll('.fpanel input').forEach(function (i) { i.checked = false; }); }
      else if (k === 'q') { state.q = ''; if (q) q.value = ''; }
      else { var v = b.getAttribute('data-v'), a = state.f[k]; a.splice(a.indexOf(v), 1); var cb = document.querySelector('.fgroup[data-f="' + k + '"] input[value="' + v.replace(/"/g, '\\"') + '"]'); if (cb) cb.checked = false; }
      render();
    });
    if (q) q.addEventListener('input', U.debounce(function () { state.q = q.value.trim(); render(); }, 120));
    if (sortSel) sortSel.addEventListener('change', function () { state.sort = sortSel.value; render(); });
    document.querySelectorAll('.viewtoggle button').forEach(function (b) {
      b.addEventListener('click', function () {
        state.view = b.getAttribute('data-view');
        document.querySelectorAll('.viewtoggle button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        grid.hidden = state.view !== 'grid'; tableHost.hidden = state.view !== 'table'; if (state.view === 'table') renderTable();
      });
    });
    var dl = document.getElementById('dl-csv');
    if (dl) dl.addEventListener('click', function () {
      U.download('pec-programmes-filtered.csv', U.toCSV(current, ['id', 'short', 'name', 'macro', 'domain', 'agency', 'scope', 'start_y', 'end_y', 'window', 'unit', 'treated', 'assign', 'timing_src', 'tq', 'evidence_status', 'methods', 'ident', 'threats', 'evidence']), 'text/csv');
    });
    render(); M.lazyTiles(grid);
  }

  /* ================================================================ PROGRAMME */
  function programme() {
    var pid = document.body.getAttribute('data-pid'), p = U.byId(pid); if (!p) return;
    var cv = document.getElementById('p-map');
    if (cv) {
      var tip = document.getElementById('p-map-tip');
      var map = new M.Map(cv, {
        interactive: true,
        onHover: function (id, e) {
          if (!id || !e) { U.tip.hide(); return; }
          var d = M.districts().find(function (x) { return x.id === id; });
          U.tip.show('<strong>' + U.esc(d.n) + '</strong>' + U.esc(fpMeaning(p, id)), e.clientX, e.clientY);
        }
      });
      map.set({ mode: 'footprint', prog: p });
      var lg = document.getElementById('p-legend'); if (lg) lg.innerHTML = fpLegend(p);
      var replay = document.getElementById('p-replay');
      if (replay && p.footprint) {
        replay.hidden = false;
        replay.addEventListener('click', function () {
          var k = 0, n = p.footprint.phases.length; map.set({ upTo: 0 });
          var t = setInterval(function () { k++; map.set({ upTo: k }); if (k > n) { clearInterval(t); map.set({ upTo: null }); } }, 650);
        });
      }
    }
    // table of contents
    var links = document.querySelectorAll('.toc a');
    if (links.length && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (ents) {
        ents.forEach(function (en) { if (en.isIntersecting) links.forEach(function (a) { a.classList.toggle('is-active', a.getAttribute('href') === '#' + en.target.id); }); });
      }, { rootMargin: '-35% 0px -60% 0px' });
      document.querySelectorAll('.p-sec[id]').forEach(function (s) { io.observe(s); });
    }
    // coverage
    var cal = document.getElementById('p-cal');
    if (cal && p.start_y) CH.calendar(cal, PEC.calendar, { from: 1998, to: 2026, win: [p.start_y, Math.max(p.end_y || p.start_y, p.start_y)] });
    // power
    bindMDE(document.getElementById('mde'), document.getElementById('mde-out'));
    // do-file
    var pre = document.getElementById('dofile');
    if (pre) {
      var code = dofile(p); pre.textContent = code;
      var b = document.getElementById('dl-do'); if (b) b.addEventListener('click', function () { U.download(p.id.toLowerCase() + '_starter.do', code, 'text/plain'); });
    }
    // claims
    U.claims(function (c) {
      var el = document.getElementById('claim-status'); if (!el) return;
      if (c[pid]) { el.hidden = false; el.innerHTML = 'Claimed on GitHub by ' + U.esc(c[pid].by) + ' \u2014 <a class="link" href="' + c[pid].url + '">see issue</a>'; }
    });
    M.lazyTiles(); U.initRails();
  }

  /* ================================================================ ATLAS */
  function atlas() {
    var cv = document.getElementById('atlas-map'); if (!cv) return;
    var years = PEC.meta.years, yi = years.length - 1, mode = 'density', prog = null;
    var panel = document.getElementById('atlas-panel'), legend = document.getElementById('atlas-legend');
    var yrEl = document.getElementById('atlas-yr'), slider = document.getElementById('atlas-slider');
    var lineageParents = {};
    (PEC.lineage || []).forEach(function (r) { if (r.pec_unit_id) lineageParents[r.pec_unit_id] = (lineageParents[r.pec_unit_id] || []).concat([r]); });
    var map = new M.Map(cv, {
      interactive: true, labels: true,
      onHover: function (id, e) {
        if (!id || !e) { U.tip.hide(); return; }
        var d = M.districts().find(function (x) { return x.id === id; }), extra = '';
        if (mode === 'density') extra = PEC.density[id][yi] + ' catalogued programmes in scope by ' + years[yi];
        else if (mode === 'footprint' && prog) extra = fpMeaning(prog, id);
        else if (mode === 'lineage') extra = lineageParents[id] ? 'Contains ' + lineageParents[id].map(function (r) { return r.district; }).join(', ') : 'No later splits recorded';
        U.tip.show('<strong>' + U.esc(d.n) + '</strong>' + U.esc(extra), e.clientX, e.clientY);
      },
      onClick: function (id) { map.sel = id; map.draw(); showDistrict(id); }
    });
    function redraw() {
      if (mode === 'density') {
        map.set({ mode: 'density', yearIndex: yi });
        legend.innerHTML = '<span>Programmes in scope</span><span class="ramp">' + M.COL.dens.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join('') + '</span><span>0 \u2192 41+</span>';
      } else if (mode === 'footprint') {
        map.set({ mode: 'footprint', prog: prog, upTo: null }); legend.innerHTML = fpLegend(prog);
      } else {
        var hl = {}; Object.keys(lineageParents).forEach(function (u) { hl[u] = lineageParents[u].some(function (r) { return r.created === ''; }) ? 'p2' : 'p1'; });
        map.set({ mode: 'highlight', units: hl });
        legend.innerHTML = '<span><i class="sw" style="background:' + M.COL.p1 + '"></i>Contains a district created after 2019 boundaries</span><span><i class="sw" style="background:' + M.COL.p2 + '"></i>Boundary-file artefact (Larkana)</span>';
      }
      document.querySelectorAll('[data-show-for]').forEach(function (n) { n.hidden = n.getAttribute('data-show-for').split(' ').indexOf(mode) < 0; });
      if (map.sel) showDistrict(map.sel);
    }
    function showDistrict(id) {
      var d = M.districts().find(function (x) { return x.id === id; }); if (!d) return;
      var y = years[yi], prov = { PB: 'Punjab', SD: 'Sindh', KP: 'Khyber Pakhtunkhwa', BA: 'Balochistan', GB: 'Gilgit-Baltistan', AJK: 'Azad Kashmir', ICT: 'Islamabad Capital Territory' }[d.p];
      var documented = [], scope = [];
      PEC.programmes.forEach(function (p) {
        var inScope = M.unitsFor(p.regions).indexOf(id) >= 0, fp = p.footprint;
        var ne = p.kind === 'Programme' ? '' : 'Natural experiment, not counted on the map';
        if (fp) {
          var docPh = fp.phases.filter(function (ph) { return ph.units.indexOf(id) >= 0 && ph.year <= y; });
          if (docPh.length) documented.push([p, docPh]);
          else if (inScope && fp.final === 'scope' && y >= fp.final_year && inFinal(fp, id)) scope.push([p, restLabel(fp) + ', covered by about ' + fp.final_year]);
          else if (inScope && fp.final === 'scope' && !inFinal(fp, id) && (p.start_y || 0) <= y) scope.push([p, 'In scope; date not documented, not counted on the map']);
          else if (inScope && fp.final === 'partial' && (p.start_y || 0) <= y) scope.push([p, 'Later phase; date not documented, not counted on the map']);
        } else if (inScope && (p.start_y || 0) <= y) scope.push([p, ne]);
      });
      var li = function (p, sub) { return '<li><a href="' + U.progUrl(p.id) + '"><span class="i">' + p.id + '</span><span>' + U.esc(p.short) + (sub ? '<span class="sub muted small" style="display:block">' + U.esc(sub) + '</span>' : '') + '</span></a></li>'; };
      var lin = lineageParents[id] ? '<p class="k">Districts inside this 2019 unit</p><ul>' + lineageParents[id].map(function (r) { return '<li><a href="../toolkit/index.html#crosswalk"><span class="i">' + (r.created || '\u2014') + '</span><span>' + U.esc(r.district) + '<span class="sub muted small" style="display:block">' + (r.created ? 'Created from ' + U.esc(r.parent_named) : 'Not separated in the boundary file') + ' \u2014 check: ' + U.esc(r.check) + '</span></span></a></li>'; }).join('') + '</ul>' : '';
      panel.innerHTML = '<p class="k" style="margin-top:0">' + U.esc(prov) + '</p><h2>' + U.esc(d.n) + '</h2>' +
        '<p class="muted small" style="margin-top:8px">By ' + y + ', ' + PEC.density[id][yi] + ' catalogued programmes include this district in a documented rollout list or their stated scope. Scope is not treatment: check each programme\u2019s rollout before using it.</p>' +
        (documented.length ? '<p class="k">Documented in a rollout list</p><ul>' + documented.map(function (x) { return li(x[0], x[1].map(function (ph) { return ph.label + ', ' + ph.year; }).join('; ')); }).join('') + '</ul>' : '') +
        lin + (scope.length ? '<p class="k">In stated scope by ' + y + ' (' + scope.length + ')</p><ul>' + scope.map(function (x) { return li(x[0], x[1]); }).join('') + '</ul>' : '');
    }
    document.querySelectorAll('[data-mode]').forEach(function (b) {
      b.addEventListener('click', function () {
        mode = b.getAttribute('data-mode');
        document.querySelectorAll('[data-mode]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        redraw();
      });
    });
    if (slider) { slider.max = years.length - 1; slider.value = yi; slider.addEventListener('input', function () { yi = +slider.value; yrEl.textContent = years[yi]; redraw(); }); }
    var play = document.getElementById('atlas-play');
    if (play) play.addEventListener('click', function () {
      var i = 0; var t = setInterval(function () { yi = i; slider.value = i; yrEl.textContent = years[i]; redraw(); i++; if (i >= years.length) clearInterval(t); }, 220);
    });
    var sel = document.getElementById('atlas-prog');
    if (sel) {
      sel.innerHTML = PEC.programmes.filter(function (p) { return p.footprint; }).map(function (p) { return '<option value="' + p.id + '">' + p.id + ' ' + U.esc(p.short) + '</option>'; }).join('') +
        '<option disabled>\u2014 scope only \u2014</option>' + PEC.programmes.filter(function (p) { return !p.footprint; }).map(function (p) { return '<option value="' + p.id + '">' + p.id + ' ' + U.esc(p.short) + '</option>'; }).join('');
      prog = U.byId(sel.value);
      sel.addEventListener('change', function () { prog = U.byId(sel.value); redraw(); });
    }
    var params = new URLSearchParams(location.search);
    if (params.get('p') && U.byId(params.get('p'))) { prog = U.byId(params.get('p')); if (sel) sel.value = prog.id; mode = 'footprint'; document.querySelectorAll('[data-mode]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-mode') === mode ? 'true' : 'false'); }); }
    if (yrEl) yrEl.textContent = years[yi];
    redraw();
  }

  /* ================================================================ INSIGHTS */
  function insights() {
    var P = PEC.programmes;
    var sw = document.getElementById('c-swim'); if (sw) CH.swimlane(sw, P);
    var era = document.getElementById('c-era');
    if (era) {
      var bands = [['Before 2005', 0, 2004], ['2005\u201309', 2005, 2009], ['2010\u201314', 2010, 2014], ['2015\u201319', 2015, 2019], ['2020 on', 2020, 2100]];
      CH.columns(era, bands.map(function (b) { var n = P.filter(function (p) { return p.start_y && p.start_y >= b[1] && p.start_y <= b[2]; }).length; return { k: b[0], v: n, hl: b[0] === '2015\u201319' }; }),
        { label: 'Programmes by start period', unit: 'programmes', kLabel: 'Start period', vLabel: 'Programmes' });
    }
    var heat = document.getElementById('c-heat');
    if (heat) {
      var rows = PEC.meta.macro_order, colsSet = {};
      PEC.outcomes.forEach(function (o) { colsSet[o.domain] = 1; });
      var cols = Object.keys(colsSet), cnt = {};
      PEC.matrix.forEach(function (m) { var p = U.byId(m.pid), k = p.macro + '|' + m.odomain; cnt[k] = (cnt[k] || 0) + 1; });
      CH.heatmap(heat, rows, cols, function (r, c) { return cnt[r + '|' + c]; }, { label: 'Programme–outcome pairs by programme domain and outcome domain' });
    }
    var ds = document.getElementById('c-ds');
    if (ds) {
      var use = {};
      PEC.matrix.forEach(function (m) { m.keys.forEach(function (k) { use[k] = (use[k] || 0) + 1; }); });
      var top = Object.keys(use).sort(function (a, b) { return use[b] - use[a]; }).slice(0, 15);
      var dname = {}; PEC.datasets.forEach(function (d) { dname[d.key] = d; });
      CH.hbars(ds, top.map(function (k) { var d = dname[k]; return { k: d ? d.dataset.split(' (')[0] : k, v: use[k], href: '../datasets/index.html#ds-' + k, note: d ? d.access : '' }; }),
        { label: 'Datasets referenced most often in the matrix', unit: 'programme\u2013outcome pairs', kLabel: 'Dataset', vLabel: 'Pairs' });
    }
    var cal = document.getElementById('c-cal'); if (cal) CH.calendar(cal, PEC.calendar, { from: 1990, to: 2026 });
    var opp = document.getElementById('opp');
    if (opp) {
      var tqs = ['High', 'Medium-high', 'Medium', 'Low'], evs = ['Unstudied', 'Limited', 'Published causal work'];
      var h = '<div class="h">Timing data</div>' + evs.map(function (e) { return '<div class="h">' + e + '</div>'; }).join('');
      tqs.forEach(function (t) {
        h += '<div class="rh">' + t + '</div>';
        evs.forEach(function (e) {
          var ps = P.filter(function (p) { return p.tq === t && p.evidence_status === e; });
          h += '<div class="c' + (t === 'High' && e === 'Unstudied' ? ' is-opportunity' : '') + '">' + ps.map(function (p) { return '<a href="' + U.progUrl(p.id) + '" title="' + U.esc(p.short) + '">' + p.id + ' ' + U.esc(p.short.length > 22 ? p.short.slice(0, 21) + '\u2026' : p.short) + '</a>'; }).join('') + '</div>';
        });
      });
      opp.innerHTML = h;
    }
    M.lazyTiles();
  }

  /* ================================================================ DATASETS */
  function datasets() {
    var cal = document.getElementById('ds-cal'), sel = document.getElementById('ds-prog');
    var draw = function () { var p = sel && sel.value ? U.byId(sel.value) : null; CH.calendar(cal, PEC.calendar, { from: 1990, to: 2026, win: p && p.start_y ? [p.start_y, Math.max(p.end_y || p.start_y, p.start_y)] : null }); };
    if (sel) {
      sel.innerHTML = '<option value="">No programme selected</option>' + PEC.programmes.filter(function (p) { return p.start_y; }).map(function (p) { return '<option value="' + p.id + '">' + p.id + ' ' + U.esc(p.short) + ' (' + U.span(p) + ')</option>'; }).join('');
      var pp = new URLSearchParams(location.search).get('p'); if (pp) sel.value = pp;
      sel.addEventListener('change', draw);
    }
    if (cal) draw();
    var cards = document.querySelectorAll('.ds-card'), act = {};
    document.querySelectorAll('[data-dsf]').forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-dsf'), v = b.getAttribute('data-v');
        act[k] = act[k] === v ? null : v;
        document.querySelectorAll('[data-dsf="' + k + '"]').forEach(function (x) { x.setAttribute('aria-pressed', act[k] === x.getAttribute('data-v') ? 'true' : 'false'); });
        var n = 0;
        cards.forEach(function (c) { var ok = Object.keys(act).every(function (kk) { return !act[kk] || c.getAttribute('data-' + kk) === act[kk]; }); c.hidden = !ok; if (ok) n++; });
        document.getElementById('ds-count').textContent = n;
      });
    });
  }

  /* ================================================================ TOOLKIT */
  function toolkit() {
    bindMDE(document.getElementById('mde'), document.getElementById('mde-out'));
    document.querySelectorAll('[data-dl-pre]').forEach(function (b) {
      b.addEventListener('click', function () { var pre = document.querySelector(b.getAttribute('data-dl-pre')); U.download(b.getAttribute('data-name'), pre.textContent, 'text/plain'); });
    });
  }

  /* ================================================================ SHORTLIST */
  function shortlist() {
    var host = document.getElementById('compare'), empty = document.getElementById('sl-empty');
    var draw = function () {
      var ids = U.shortlist.all(), ps = ids.map(U.byId).filter(Boolean);
      empty.hidden = ps.length > 0; host.hidden = !ps.length;
      document.getElementById('sl-tools').hidden = !ps.length;
      if (!ps.length) return;
      var rows = [['Programme', function (p) { return '<a class="link" href="' + U.progUrl(p.id) + '">' + p.id + ' ' + U.esc(p.short) + '</a>'; }],
        ['Rollout', function (p) { return U.esc(p.window); }], ['Unit', function (p) { return U.esc(p.unit); }],
        ['Assignment', function (p) { return U.esc(p.assign); }], ['Timing data', function (p) { return U.meter(p.tq_rank) + '<span class="ml">' + p.tq + '</span>'; }],
        ['Where to get dates', function (p) { return U.esc(p.timing_src); }], ['Identification', function (p) { return U.esc(p.ident); }],
        ['Main threats', function (p) { return U.esc(p.threats); }], ['Evidence', function (p) { return U.esc(p.evidence_status) + '<br><span class="muted small">' + U.esc(p.evidence) + '</span>'; }],
        ['Outcomes mapped', function (p) { return p.n_outcomes; }],
        ['', function (p) { return '<button class="textbtn" data-star="' + p.id + '">Remove</button>'; }]];
      host.innerHTML = '<table><tbody>' + rows.map(function (r) { return '<tr><th scope="row">' + r[0] + '</th>' + ps.map(function (p) { return '<td>' + r[1](p) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>';
    };
    document.addEventListener('click', function (e) { if (e.target.closest('[data-star]')) setTimeout(draw, 0); });
    document.getElementById('sl-csv').addEventListener('click', function () {
      U.download('pec-shortlist.csv', U.toCSV(U.shortlist.all().map(U.byId).filter(Boolean), ['id', 'short', 'name', 'window', 'unit', 'assign', 'timing_src', 'tq', 'ident', 'threats', 'evidence_status', 'evidence']), 'text/csv');
    });
    document.getElementById('sl-bib').addEventListener('click', function () {
      var bib = U.shortlist.all().map(U.byId).filter(Boolean).map(function (p) {
        return '@misc{pec_' + p.id.toLowerCase() + ',\n  author = {Hussain, Saqib},\n  year = {2026},\n  title = {' + p.name.replace(/[{}]/g, '') + ' (' + p.id + ')},\n  howpublished = {Pakistan Evidence Catalogue, version ' + PEC.meta.version + '},\n  url = {https://itssaqib.github.io/pakistan-evidence-catalogue/programmes/' + p.id.toLowerCase() + '.html}\n}';
      }).join('\n\n');
      U.download('pec-shortlist.bib', bib + '\n', 'text/plain');
    });
    document.getElementById('sl-clear').addEventListener('click', function () { U.store.set('pec_shortlist_v2', []); U.shortlist.sync(); draw(); });
    draw();
  }

  var routes = { home: home, browse: browse, programme: programme, atlas: atlas, insights: insights, datasets: datasets, toolkit: toolkit, shortlist: shortlist };
  if (routes[page]) routes[page]();
  window.PECPages = { mde: mde, dofile: dofile };
})();
