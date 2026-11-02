# -*- coding: utf-8 -*-
"""Generate every HTML page for the catalogue site."""
import json, os, html, re
from layout import page, esc, SITE, TAGLINE, VERSION, RELEASED, AUTHOR, AUTHOR_URL, CONTACT, REPO

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
D = json.load(open(f"{ROOT}/data/catalogue.json", encoding="utf-8"))
PROGS, OUTS, DSETS, MX, META = D["programmes"], D["outcomes"], D["datasets"], D["matrix"], D["meta"]
C = META["counts"]

by_id = {p["id"]: p for p in PROGS}
out_by_id = {o["id"]: o for o in OUTS}
ds_by_key = {d["key"]: d for d in DSETS}
mx_by_prog = {}
for m in MX:
    mx_by_prog.setdefault(m["programme_id"], []).append(m)


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


def meter(rank, label):
    cells = "".join(f'<i class="{"on" if i <= rank else ""}"></i>' for i in (1, 2, 3))
    return (f'<span class="meter meter--{rank}" role="img" '
            f'aria-label="Timing data quality: {esc(label)}">{cells}</span>'
            f'<span class="meter-label">{esc(label)}</span>')


def crumb(base, items):
    parts = [f'<a href="{base}">Home</a>']
    for label, href in items[:-1]:
        parts.append(f'<a href="{href}">{esc(label)}</a>')
    parts.append(esc(items[-1][0]))
    return '<div class="wrap shell"><nav class="crumb" aria-label="Breadcrumb">' + \
           '<span>/</span>'.join(parts) + '</nav></div>'


# =============================================================================
# HOME
# =============================================================================
domain_counts = {}
for p in PROGS:
    domain_counts[p["domain"]] = domain_counts.get(p["domain"], 0) + 1
top_domains = sorted(domain_counts.items(), key=lambda x: -x[1])[:9]

ready = sorted([p for p in PROGS if p["quality_rank"] == 3],
               key=lambda p: -p["n_outcomes"])[:8]

ready_rows = ""
for p in ready:
    ready_rows += f"""<tr>
      <td class="id">{esc(p['id'])}</td>
      <td class="wide"><a class="rowtitle" href="programmes/{p['slug']}.html">{esc(p['programme'])}</a>
        <span class="rowsub">{esc(p['agency'])}</span></td>
      <td class="hide-sm">{esc(p['domain'])}</td>
      <td class="hide-sm">{esc(p['unit_class'])}</td>
      <td class="num">{p['n_outcomes']}</td>
    </tr>"""

home_body = f"""
<section class="hero">
  <div class="wrap shell">
    <div class="grid grid--7-5">
      <div>
        <p class="eyebrow">Research infrastructure</p>
        <h1>Policies in Pakistan that arrived district by district &mdash; and the evidence they make possible.</h1>
        <p class="lede">An open catalogue of {C['programmes']} programmes and natural experiments rolled out unit by unit
        over time, each with its rollout window, assignment rule, the source for its treatment dates, and the
        outcomes and datasets that can be used to evaluate it.</p>
        <div class="hero-links">
          <a href="programmes/">Browse the catalogue</a>
          <a href="programmes/?quality_label=High">Start with the {C['high']} best-documented</a>
          <a href="data/">Download the data</a>
        </div>
      </div>
      <div>
        <div class="box box--paper">
          <p class="eyebrow">Programmes by start year</p>
          <svg class="chart" id="chart-era" aria-label="Programmes by start year"></svg>
          <p class="small muted" style="margin-top:12px">Rollout start dates cluster after devolution in 2010
          and again under the 2019&ndash;22 expansion of social protection and health insurance.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="wrap shell">
  <div class="statstrip">
    <div class="stat"><span class="n">{C['programmes']}</span><span class="l">Programmes &amp; shocks</span></div>
    <div class="stat"><span class="n">{C['pairs']}</span><span class="l">Programme &times; outcome pairs</span></div>
    <div class="stat"><span class="n">{C['outcomes']}</span><span class="l">Outcomes defined</span></div>
    <div class="stat"><span class="n">{C['datasets']}</span><span class="l">Datasets mapped</span></div>
    <div class="stat"><span class="n">{C['high']}</span><span class="l">With reliable treatment dates</span></div>
  </div>
</div>

<section class="section">
  <div class="wrap shell">
    <div class="grid grid--7-5">
      <div class="prose">
        <h2>What this is for</h2>
        <p>Pakistan ran an unusual number of large public programmes that reached districts at
        different times: health insurance activated division by division, land records digitised
        tehsil by tehsil, cash transfers gated by the date a district's poverty census finished.
        That staggering is the variation causal inference needs, and most of it has never been used.</p>
        <p>The binding constraint is rarely the idea. It is knowing <em>when</em> each district was
        treated, and whether an outcome exists at the same resolution. This catalogue answers both
        questions for each entry, and says plainly where the answer is weak.</p>
        <p><a href="about/">More about the catalogue and how it was built</a></p>
      </div>
      <div>
        <div class="box">
          <p class="eyebrow">Three things to read first</p>
          <ul class="plain">
            <li><a href="methods/">Identification playbook</a> &mdash; why two-way fixed effects
              is the wrong default here, and what to use instead.</li>
            <li><a href="timing/">Finding treatment dates</a> &mdash; ADP scheme registers, PC-4
              completion reports, RTI requests and what each actually yields.</li>
            <li><a href="caveats/">Standing caveats</a> &mdash; boundary changes, targeting on the
              outcome, migration sorting, non-absorbing treatment.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="wrap shell">
    <p class="eyebrow">Best-documented entries</p>
    <h2>Where the treatment dates are already reliable</h2>
    <p class="small muted" style="max-width:52em">These {C['high']} entries have a datable,
    verifiable rollout schedule. For the rest, the catalogue names what would have to be obtained
    and how. Showing the eight with the most mapped outcomes.</p>
    <div class="tablewrap" style="margin-top:20px">
      <table class="data">
        <caption>Programmes with high-quality treatment-timing data</caption>
        <thead><tr>
          <th scope="col">ID</th><th scope="col">Programme</th>
          <th scope="col" class="hide-sm">Domain</th>
          <th scope="col" class="hide-sm">Rollout unit</th>
          <th scope="col" style="text-align:right">Outcomes</th>
        </tr></thead>
        <tbody>{ready_rows}</tbody>
      </table>
    </div>
    <p style="margin-top:16px"><a href="programmes/?quality_label=High">See all {C['high']} &rarr;</a></p>
  </div>
</section>

<section class="section">
  <div class="wrap shell">
    <div class="grid grid--7-5">
      <div>
        <p class="eyebrow">Coverage</p>
        <h2>By policy domain</h2>
        <svg class="chart" id="chart-domain" aria-label="Programmes by domain"></svg>
      </div>
      <div>
        <div class="box">
          <h3>Use the data directly</h3>
          <p class="small">Everything on this site is generated from four files. They are versioned,
          CC&nbsp;BY licensed, and stable.</p>
          <div class="dl-file"><span class="fmt">CSV</span><span class="nm"><a href="data/programmes.csv">programmes.csv</a></span><span class="sz">{C['programmes']} rows</span></div>
          <div class="dl-file"><span class="fmt">CSV</span><span class="nm"><a href="data/programme_outcome_matrix.csv">programme_outcome_matrix.csv</a></span><span class="sz">{C['pairs']} rows</span></div>
          <div class="dl-file"><span class="fmt">CSV</span><span class="nm"><a href="data/datasets.csv">datasets.csv</a></span><span class="sz">{C['datasets']} rows</span></div>
          <div class="dl-file"><span class="fmt">JSON</span><span class="nm"><a href="data/catalogue.json">catalogue.json</a></span><span class="sz">everything</span></div>
          <p class="small" style="margin-top:14px"><a href="data/">All downloads and the schema &rarr;</a></p>
        </div>
      </div>
    </div>
  </div>
</section>
"""

home_js = """<script>
PEC.load('programmes.json').then(function (progs) {
  var eras = ['Pre-2005','2005-2009','2010-2014','2015-2019','2020 onwards'];
  var counts = eras.map(function (e) {
    return { label: e.replace(' onwards','+'), value: progs.filter(function(p){return p.era===e;}).length };
  });
  PEC.columnChart(document.getElementById('chart-era'), counts, { height: 200 });

  var dom = {};
  progs.forEach(function (p) { dom[p.domain] = (dom[p.domain]||0) + 1; });
  var rows = Object.keys(dom).map(function (k) { return { label: k, value: dom[k] }; })
    .sort(function (a,b) { return b.value - a.value; }).slice(0, 10);
  PEC.barChart(document.getElementById('chart-domain'), rows, { padL: 200 });
});
</script>"""

write("index.html", page(home_body, "Home", TAGLINE + " — an open catalogue of "
                         f"{C['programmes']} programmes and natural experiments in Pakistan.",
                         base="", active="", extra_js=home_js))

# =============================================================================
# PROGRAMME INDEX
# =============================================================================
prog_body = f"""
{crumb("../", [("Programmes", "")])}
<div class="wrap shell">
  <div class="pagehead">
    <p class="eyebrow">Catalogue</p>
    <h1>Programmes and natural experiments</h1>
    <p class="lede">{C['programmes']} entries with district-level or finer rollout variation.
    Filter on timing-data quality first &mdash; that column tells you whether the treatment date
    can be pinned down with existing sources or needs a data-collection effort of its own.</p>
  </div>

  <div class="with-rail">
    <aside>
      <label for="search" class="eyebrow" style="display:block">Search</label>
      <input class="searchbox" id="search" type="search" placeholder="e.g. land records, health insurance, flood"
             autocomplete="off">
      <div id="rail" class="rail" style="border:0;padding:0;margin-top:20px;position:static;max-height:none"></div>
    </aside>

    <div>
      <div id="chips" class="chips"></div>
      <div class="resultbar">
        <span class="n" id="count"></span>
        <span class="spacer"></span>
        <button class="copybtn" id="dl-filtered" type="button">Download these rows (CSV)</button>
      </div>
      <div class="tablewrap">
        <table class="data" id="ptable">
          <caption>Click a column heading to sort. Timing quality indicates how reliably the
          treatment date can be established from existing sources.</caption>
          <thead><tr>
            <th scope="col" class="sortable" data-sort="id">ID <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="programme">Programme <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable hide-sm" data-sort="domain">Domain <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable hide-sm hide-md" data-sort="start_year">Start <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable hide-sm" data-sort="unit_class">Unit <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="quality_rank" data-dir="desc">Timing quality <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="n_outcomes" data-dir="desc" style="text-align:right">Outcomes <span class="arrow">&#8597;</span></th>
          </tr></thead>
          <tbody id="pbody"><tr><td colspan="7"><div class="loading">Loading catalogue&hellip;</div></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>
"""

prog_js = """<script>
PEC.load('programmes.json').then(function (progs) {
  PEC.facetTable({
    records: progs,
    table: '#ptable', body: '#pbody', rail: '#rail', chips: '#chips',
    count: '#count', search: '#search', colspan: 7, noun: 'programmes',
    defaultSort: 'id',
    download: '#dl-filtered',
    downloadName: 'pec-programmes-filtered.csv',
    downloadFields: ['id','programme','domain','agency','scope','start_year','rollout_window',
      'rollout_unit','n_districts','staggering','assignment','timing_source','timing_quality',
      'identification','threats','evidence','regions','unit_class','era','methods','n_outcomes'],
    searchFields: ['id','programme','domain','agency','scope','rollout_window','rollout_unit',
      'staggering','assignment','timing_source','identification','threats','evidence','methods','regions'],
    facetDefs: [
      { key: 'quality_label', label: 'Timing data quality', get: function (r) { return r.quality_label; },
        order: ['High','Medium-High','Medium','Low-Medium'] },
      { key: 'kind', label: 'Type', get: function (r) { return r.kind; } },
      { key: 'domain', label: 'Domain', get: function (r) { return r.domain; } },
      { key: 'regions', label: 'Province / region', get: function (r) { return r.regions; } },
      { key: 'unit_class', label: 'Rollout unit', get: function (r) { return r.unit_class; } },
      { key: 'era', label: 'Start period', get: function (r) { return r.era; },
        order: ['Pre-2005','2005-2009','2010-2014','2015-2019','2020 onwards','Continuous'] },
      { key: 'methods', label: 'Design suited to', get: function (r) { return r.methods; } }
    ],
    row: function (p) {
      return '<tr>' +
        '<td class="id">' + PEC.esc(p.id) + '</td>' +
        '<td class="wide"><a class="rowtitle" href="' + p.slug + '.html">' + PEC.esc(p.programme) + '</a>' +
          '<span class="rowsub">' + PEC.esc(p.agency) + '</span></td>' +
        '<td class="hide-sm">' + PEC.esc(p.domain) + '</td>' +
        '<td class="hide-sm hide-md id">' + PEC.esc(p.start_year) + '</td>' +
        '<td class="hide-sm">' + PEC.esc(p.unit_class) + '</td>' +
        '<td style="white-space:nowrap">' + PEC.meter(p.quality_rank, p.quality_label) + '</td>' +
        '<td class="num">' + p.n_outcomes + '</td>' +
      '</tr>';
    }
  });
});
</script>"""

write("programmes/index.html",
      page(prog_body, "Programmes",
           f"All {C['programmes']} staggered district-level programmes and natural experiments in Pakistan, "
           "filterable by domain, province, rollout unit and timing-data quality.",
           base="../", active="programmes/", extra_js=prog_js))

print("home + programme index written")
