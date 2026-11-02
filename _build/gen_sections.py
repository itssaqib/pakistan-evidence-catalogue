# -*- coding: utf-8 -*-
"""Remaining section pages."""
import json, os
from layout import page, esc, SITE, TAGLINE, VERSION, RELEASED, AUTHOR, AUTHOR_URL, CONTACT, REPO

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
D = json.load(open(f"{ROOT}/data/catalogue.json", encoding="utf-8"))
PROGS, OUTS, DSETS, MX, META = D["programmes"], D["outcomes"], D["datasets"], D["matrix"], D["meta"]
C = META["counts"]


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


def crumb(here):
    return f"""<div class="wrap shell"><nav class="crumb" aria-label="Breadcrumb">
<a href="../">Home</a><span>/</span>{esc(here)}</nav></div>"""


def head(eyebrow, h1, lede):
    return f"""<div class="wrap shell"><div class="pagehead">
<p class="eyebrow">{esc(eyebrow)}</p><h1>{esc(h1)}</h1>
<p class="lede">{lede}</p></div></div>"""


# =============================================================================
# MATRIX BROWSER
# =============================================================================
matrix_body = crumb("Outcome matrix") + head(
    "Catalogue", "Programme × outcome matrix",
    f"All {C['pairs']} programme–outcome pairs in one filterable table. Each row names the "
    "mechanism that would produce the outcome, the expected direction, the dataset that measures "
    "it, and an honest note on whether the analysis is actually feasible with existing data.") + f"""
<div class="wrap shell">
  <div class="with-rail">
    <aside>
      <label for="search" class="eyebrow" style="display:block">Search</label>
      <input class="searchbox" id="search" type="search"
             placeholder="e.g. stunting, land, out-of-pocket" autocomplete="off">
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
        <table class="data" id="mtable">
          <caption>Expected signs are hypotheses derived from the stated mechanism, not findings.</caption>
          <thead><tr>
            <th scope="col" class="sortable" data-sort="programme_id">ID <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="programme">Programme <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="outcome">Outcome <span class="arrow">&#8597;</span></th>
            <th scope="col" class="hide-sm">Mechanism</th>
            <th scope="col">Expected</th>
            <th scope="col" class="hide-sm">Dataset</th>
          </tr></thead>
          <tbody id="mbody"><tr><td colspan="6"><div class="loading">Loading matrix&hellip;</div></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>
"""

matrix_js = """<script>
PEC.load('matrix.json').then(function (mx) {
  function signClass(s) {
    s = (s || '').toLowerCase();
    if (s.indexOf('ambiguous') > -1) return 'pill--claimed';
    if (s.charAt(0) === '-' || s.indexOf('reduction') > -1 || s.indexOf('faster') > -1
        || s.indexOf('shorter') > -1) return 'pill--active';
    if (s.charAt(0) === '0') return 'pill--done';
    return 'pill--open';
  }
  function signGroup(s) {
    s = (s || '').toLowerCase();
    if (s.indexOf('ambiguous') > -1) return 'Ambiguous';
    if (s.charAt(0) === '-' || s.indexOf('reduction') > -1 || s.indexOf('faster') > -1
        || s.indexOf('shorter') > -1) return 'Decrease';
    if (s.charAt(0) === '0') return 'Null or small';
    return 'Increase';
  }
  mx.forEach(function (m) {
    m.sign_group = signGroup(m.expected_sign);
    m.dataset_text = (m.dataset_names || []).join('; ');
    m.dataset_keys_list = (m.sources || []).map(function (s) { return s.key; });
  });

  PEC.facetTable({
    records: mx,
    table: '#mtable', body: '#mbody', rail: '#rail', chips: '#chips',
    count: '#count', search: '#search', colspan: 6, noun: 'pairs',
    defaultSort: 'programme_id',
    download: '#dl-filtered',
    downloadName: 'pec-matrix-filtered.csv',
    downloadFields: ['programme_id','programme','domain','outcome_id','outcome','outcome_domain',
      'mechanism','expected_sign','dataset_text','feasibility'],
    searchFields: ['programme_id','programme','domain','outcome','outcome_domain','mechanism',
      'expected_sign','dataset_text','feasibility'],
    facetDefs: [
      { key: 'outcome_domain', label: 'Outcome domain', get: function (r) { return r.outcome_domain; } },
      { key: 'domain', label: 'Programme domain', get: function (r) { return r.domain; } },
      { key: 'sign_group', label: 'Expected direction', get: function (r) { return r.sign_group; },
        order: ['Increase','Decrease','Ambiguous','Null or small'] },
      { key: 'dataset_keys_list', label: 'Dataset', get: function (r) { return r.dataset_keys_list; } }
    ],
    row: function (m) {
      return '<tr>' +
        '<td class="id"><a href="../programmes/' + m.programme_id.toLowerCase() + '.html">' +
          PEC.esc(m.programme_id) + '</a></td>' +
        '<td class="wide"><a class="rowtitle" href="../programmes/' + m.programme_id.toLowerCase() +
          '.html">' + PEC.esc(m.programme) + '</a></td>' +
        '<td class="wide"><strong>' + PEC.esc(m.outcome) + '</strong>' +
          '<span class="rowsub">' + PEC.esc(m.outcome_domain) + '</span></td>' +
        '<td class="wide hide-sm">' + PEC.esc(m.mechanism) + '</td>' +
        '<td style="white-space:nowrap"><span class="pill ' + signClass(m.expected_sign) + '">' +
          PEC.esc(m.expected_sign) + '</span></td>' +
        '<td class="wide hide-sm small">' + PEC.esc(m.dataset_text) + '</td>' +
      '</tr>';
    }
  });
});
</script>"""

write("matrix/index.html", page(matrix_body, "Outcome matrix",
      f"All {C['pairs']} programme-outcome pairs with mechanisms, expected signs, datasets and feasibility notes.",
      base="../", active="matrix/", extra_js=matrix_js))


# =============================================================================
# OUTCOMES
# =============================================================================
out_body = crumb("Outcomes") + head(
    "Catalogue", "Outcome taxonomy",
    f"{C['outcomes']} outcomes across 14 domains, each with a construction note, the unit it is "
    "measured at, how often it is observed, and the datasets that carry it.") + """
<div class="wrap shell">
  <div class="with-rail">
    <aside>
      <label for="search" class="eyebrow" style="display:block">Search</label>
      <input class="searchbox" id="search" type="search" placeholder="e.g. enrolment, mortality, wages" autocomplete="off">
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
        <table class="data" id="otable">
          <caption>Click an outcome to see every programme it is mapped to.</caption>
          <thead><tr>
            <th scope="col" class="sortable" data-sort="id">ID <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="domain">Domain <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="outcome">Outcome <span class="arrow">&#8597;</span></th>
            <th scope="col">Definition / construction</th>
            <th scope="col" class="hide-sm">Unit</th>
            <th scope="col" class="hide-sm">Frequency</th>
            <th scope="col" class="hide-sm">Datasets</th>
          </tr></thead>
          <tbody id="obody"><tr><td colspan="7"><div class="loading">Loading&hellip;</div></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>
"""

out_js = """<script>
PEC.load('outcomes.json').then(function (outs) {
  PEC.facetTable({
    records: outs,
    table: '#otable', body: '#obody', rail: '#rail', chips: '#chips',
    count: '#count', search: '#search', colspan: 7, noun: 'outcomes',
    defaultSort: 'id',
    download: '#dl-filtered', downloadName: 'pec-outcomes-filtered.csv',
    downloadFields: ['id','domain','outcome','definition','unit','frequency','datasets'],
    searchFields: ['id','domain','outcome','definition','unit','frequency','datasets'],
    facetDefs: [
      { key: 'domain', label: 'Domain', get: function (r) { return r.domain; } },
      { key: 'frequency', label: 'Frequency', get: function (r) { return r.frequency; } }
    ],
    row: function (o) {
      return '<tr>' +
        '<td class="id">' + PEC.esc(o.id) + '</td>' +
        '<td>' + PEC.esc(o.domain) + '</td>' +
        '<td class="wide"><a class="rowtitle" href="../matrix/?q=' +
          encodeURIComponent(o.outcome) + '">' + PEC.esc(o.outcome) + '</a></td>' +
        '<td class="wide small">' + PEC.esc(o.definition) + '</td>' +
        '<td class="hide-sm small">' + PEC.esc(o.unit) + '</td>' +
        '<td class="hide-sm small">' + PEC.esc(o.frequency) + '</td>' +
        '<td class="hide-sm small">' + PEC.esc(o.datasets) + '</td>' +
      '</tr>';
    }
  });
});
</script>"""

write("outcomes/index.html", page(out_body, "Outcomes",
      f"{C['outcomes']} outcomes across 14 domains with construction notes and source datasets.",
      base="../", active="", extra_js=out_js))


# =============================================================================
# DATASETS
# =============================================================================
ds_cards = ""
for d in sorted(DSETS, key=lambda x: x["dataset"]):
    ds_cards += f"""
<div class="box box--paper" id="{esc(d['key'])}" style="margin-bottom:16px">
  <p class="eyebrow"><span class="mono">{esc(d['key'])}</span> &middot; {esc(d['type'])}</p>
  <h3 style="margin-bottom:6px"><a href="{esc(d['url'])}" rel="noopener">{esc(d['dataset'])}</a></h3>
  <p class="small muted" style="margin-bottom:12px">{esc(d['producer'])}</p>
  <dl class="meta" style="grid-template-columns:150px minmax(0,1fr);font-size:14px">
    <dt>Unit</dt><dd>{esc(d['unit'])}</dd>
    <dt>Coverage</dt><dd>{esc(d['coverage'])}</dd>
    <dt>District ID</dt><dd>{esc(d['district_id'])}</dd>
    <dt>Access</dt><dd>{esc(d['access'])}</dd>
  </dl>
  <p class="small" style="margin-top:12px"><strong>Notes:</strong> {esc(d['notes'])}</p>
  <p class="small" style="margin-top:8px">
    <a href="../matrix/?q={esc(d['key'])}">Programmes using this dataset &rarr;</a>
  </p>
</div>"""

ds_body = crumb("Datasets") + head(
    "Catalogue", "Dataset catalogue",
    f"{C['datasets']} datasets that can measure outcomes at district resolution or finer — who "
    "produces them, what years they cover, whether a district identifier exists, and how to get "
    "access. The access route matters more than the dataset: several of these require a research "
    "agreement, not a download.") + f"""
<div class="wrap shell">
  <div class="with-rail">
    <aside>
      <label for="search" class="eyebrow" style="display:block">Search</label>
      <input class="searchbox" id="search" type="search" placeholder="e.g. survey, satellite, administrative" autocomplete="off">
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
        <table class="data" id="dtable">
          <thead><tr>
            <th scope="col" class="sortable" data-sort="key">Key <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable" data-sort="dataset">Dataset <span class="arrow">&#8597;</span></th>
            <th scope="col" class="sortable hide-sm" data-sort="type">Type <span class="arrow">&#8597;</span></th>
            <th scope="col" class="hide-sm">Coverage</th>
            <th scope="col">District ID</th>
            <th scope="col" class="hide-sm">Access</th>
          </tr></thead>
          <tbody id="dbody"><tr><td colspan="6"><div class="loading">Loading&hellip;</div></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<section class="section">
  <div class="wrap shell">
    <h2 style="margin-bottom:6px">Full entries</h2>
    <p class="small muted" style="margin-bottom:24px">Every dataset in detail, alphabetically.</p>
    {ds_cards}
  </div>
</section>
"""

ds_js = """<script>
PEC.load('datasets.json').then(function (ds) {
  ds.forEach(function (d) {
    d.access_class = /free/i.test(d.access) ? 'Free or open'
      : (/restricted|request|agreement|licen/i.test(d.access) ? 'Request or agreement' : 'Other');
    d.has_district = /^yes/i.test(d.district_id) ? 'Yes' :
      (/partial|province|coarse|cluster|city|rto|aggregate/i.test(d.district_id) ? 'Partial' : 'Derivable');
  });
  PEC.facetTable({
    records: ds,
    table: '#dtable', body: '#dbody', rail: '#rail', chips: '#chips',
    count: '#count', search: '#search', colspan: 6, noun: 'datasets',
    defaultSort: 'dataset',
    download: '#dl-filtered', downloadName: 'pec-datasets-filtered.csv',
    downloadFields: ['key','dataset','producer','type','unit','coverage','district_id','access','url','notes'],
    searchFields: ['key','dataset','producer','type','unit','coverage','district_id','access','notes'],
    facetDefs: [
      { key: 'type', label: 'Dataset type', get: function (r) { return r.type; } },
      { key: 'access_class', label: 'Access', get: function (r) { return r.access_class; } },
      { key: 'has_district', label: 'District identifier', get: function (r) { return r.has_district; },
        order: ['Yes','Partial','Derivable'] }
    ],
    row: function (d) {
      return '<tr>' +
        '<td class="id">' + PEC.esc(d.key) + '</td>' +
        '<td class="wide"><a class="rowtitle" href="#' + PEC.esc(d.key) + '">' +
          PEC.esc(d.dataset) + '</a><span class="rowsub">' + PEC.esc(d.producer) + '</span></td>' +
        '<td class="hide-sm small">' + PEC.esc(d.type) + '</td>' +
        '<td class="hide-sm small">' + PEC.esc(d.coverage) + '</td>' +
        '<td class="small">' + PEC.esc(d.district_id) + '</td>' +
        '<td class="hide-sm small">' + PEC.esc(d.access) + '</td>' +
      '</tr>';
    }
  });
});
</script>"""

write("datasets/index.html", page(ds_body, "Datasets",
      f"{C['datasets']} datasets for district-level evaluation in Pakistan, with coverage, district identifiers and access routes.",
      base="../", active="datasets/", extra_js=ds_js))

print("matrix, outcomes, datasets written")
