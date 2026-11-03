# -*- coding: utf-8 -*-
"""Generate every HTML page from data/catalogue.json."""
import json, os, re, html as _html
from urllib.parse import quote_plus as _q
from layout import page, esc, tile, rail, ICON, SITE_NAME, SITE_URL, AUTHOR, AUTHOR_URL, CONTACT, REPO, VERSION, RELEASED

HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(HERE)
SITE = _PARENT if os.path.exists(os.path.join(_PARENT, "assets", "css", "site.css")) else os.path.join(_PARENT, "out", "pakistan-evidence-catalogue")
D = json.load(open(os.path.join(SITE, "data", "catalogue.json"), encoding="utf-8"))
PROGS, OUTS, DSETS, MX, META, BIB = D["programmes"], D["outcomes"], D["datasets"], D["matrix"], D["meta"], D["bib"]
C = META["counts"]
P = {p["id"]: p for p in PROGS}
OUT = {o["id"]: o for o in OUTS}
DS = {d["key"]: d for d in DSETS}
CONTENT = json.load(open(os.path.join(HERE, "content_v1.json"), encoding="utf-8"))
RESERVED = {"P35"}  # not featured on the home page (the maintainer's own pipeline)


def write(rel, html):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)


def span(p):
    if not p["start_y"]:
        return "Continuous"
    if not p["end_y"] or p["end_y"] == p["start_y"]:
        return str(p["start_y"])
    return f"{p['start_y']}–{p['end_y']}"


def meter(rank):
    return '<span class="meter" aria-hidden="true">' + "".join(f'<i class="{"on" if i <= rank else ""}"></i>' for i in (1, 2, 3)) + "</span>"


def coll_head(title, sub="", link=None):
    l = f'<a class="coll-link" href="{link[0]}">{esc(link[1])}</a>' if link else ""
    s = f"<p>{sub}</p>" if sub else ""
    return f'<div class="coll-head"><h2>{esc(title)}</h2>{s}{l}</div>'


DATASET_LD = {
    "@context": "https://schema.org", "@type": "Dataset",
    "name": "Pakistan Evidence Catalogue",
    "description": f"A catalogue of {C['programmes']} public programmes and natural experiments in Pakistan rolled out district by district, "
                   f"with rollout windows, assignment rules, sources for treatment timing, {C['pairs']} programme-outcome pairs and "
                   f"{C['datasets']} datasets, plus a district crosswalk on constant 2019 boundaries.",
    "url": SITE_URL, "version": VERSION, "datePublished": "2026-11-04", "license": "https://creativecommons.org/licenses/by/4.0/",
    "creator": {"@type": "Person", "name": AUTHOR, "url": AUTHOR_URL},
    "keywords": ["Pakistan", "difference-in-differences", "staggered adoption", "impact evaluation", "district panel", "development economics"],
    "spatialCoverage": {"@type": "Place", "name": "Pakistan"}, "temporalCoverage": "1994/2024",
    "distribution": [
        {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE_URL + "data/programmes.csv"},
        {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE_URL + "data/programme_outcome_matrix.csv"},
        {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE_URL + "data/catalogue.json"},
        {"@type": "DataDownload", "encodingFormat": "application/x-stata-dta", "contentUrl": SITE_URL + "data/programmes.dta"},
        {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE_URL + "data/districts/district_crosswalk.csv"}],
}

# =============================================================================
# HOME
# =============================================================================
high = [p for p in PROGS if p["tq_rank"] == 3 and p["id"] not in RESERVED]
high_sorted = sorted(high, key=lambda p: (-(1 if p["footprint"] else 0), -p["n_outcomes"], p["id"]))
opps = [p for p in PROGS if p["tq_rank"] == 3 and p["evidence_status"] == "Unstudied" and p["id"] not in RESERVED]
FEATURE_OPP = [P[x] for x in ["P15", "P43", "P46"] if x in P]
most = sorted([p for p in PROGS if p["id"] not in RESERVED], key=lambda p: (-p["n_outcomes"], p["id"]))[:6]
fps = [p for p in PROGS if p["footprint"]]

def coll_card(p, base):
    return (f'<a class="coll-card tile" href="{base}programmes/{p["slug"]}.html" data-pid="{p["id"]}">'
            f'<div class="tile-media"><canvas aria-hidden="true"></canvas><span class="tile-id">{p["id"]}</span>'
            f'<span class="tile-badge">{span(p)}</span></div>'
            f'<h3>{esc(p["short"])}</h3><p>{esc(p["stagger"])}.</p>'
            f'<div class="meta">{esc(p["macro"])}, {esc(p["unit_class"].lower())} rollout, {p["n_outcomes"]} outcomes mapped</div></a>')

domain_rails = ""
for m in META["macro_order"]:
    ps = [p for p in PROGS if p["macro"] == m]
    if not ps:
        continue
    ps = sorted(ps, key=lambda p: (-p["tq_rank"], p["id"]))
    domain_rails += (f'<section class="section section--line">{"<div class=\"wrap\">"}'
                     f'{coll_head(m, f"{len(ps)} entries", (f"programmes/index.html?macro={m.replace(chr(38), "%26")}", "See all"))}'
                     f'{rail("".join(tile(p, "") for p in ps), m)}</div></section>')

opp_rows = ""
for t in ["High", "Medium-high", "Medium", "Low"]:
    opp_rows += f'<div class="rh">{t}</div>'
    for e in ["Unstudied", "Limited", "Published causal work"]:
        ps = [p for p in PROGS if p["tq"] == t and p["evidence_status"] == e]
        cls = " is-opportunity" if (t == "High" and e == "Unstudied") else ""
        opp_rows += f'<div class="c{cls}">' + "".join(
            f'<a href="programmes/{p["slug"]}.html" title="{esc(p["short"])}">{p["id"]}</a>' for p in ps) + "</div>"

home = f"""
<section class="stage hero" aria-label="District map of catalogued programmes">
  <div class="hero-map"><canvas id="hero-map" aria-label="Map of Pakistan's districts shaded by the number of catalogued programmes whose scope or documented rollout includes each district"></canvas></div>
  <div class="hero-veil"></div>
  <div class="map-legend hero-legend"><span>Fewer</span><span class="ramp" id="hero-ramp"></span><span>More programmes</span></div>
  <div class="year-dial" aria-live="polite">
    <div class="yr" id="hero-yr">2024</div>
    <div class="yr-label">Catalogued programmes whose stated scope or documented rollout includes each district</div>
    <div class="dial-controls">
      <button class="play-btn" id="hero-play" type="button" aria-label="Replay 2000 to 2024">{ICON["play"]}</button>
      <label class="sr-only" for="hero-slider">Year</label>
      <input id="hero-slider" type="range" min="0" max="24" value="24" step="1">
    </div>
  </div>
  <div class="hero-inner">
    <h1 class="hero-title">Pakistan, one district at a time</h1>
    <p class="hero-sub">{C['programmes']} programmes and natural experiments that reached districts at different times, with the rollout dates, outcomes and datasets needed to evaluate them.</p>
    <div class="hero-actions">
      <a class="btn" href="programmes/index.html">Browse the catalogue</a>
      <a class="btn btn--line" href="atlas/index.html">Open the atlas</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {coll_head("Where the dates are reliable", f"{C['high']} entries whose district rollout can be dated from existing sources. Hover a map to replay its documented phases.", ("programmes/index.html?tq=High", "See all " + str(C['high'])))}
    {rail("".join(tile(p, "") for p in high_sorted), "Programmes with reliable rollout dates")}
  </div>
</section>

<section class="section section--mist">
  <div class="wrap">
    {coll_head("Reliable dates, no causal study yet", f"{len(opps)} entries combine a datable rollout with no published causal evaluation. Three of them:", ("programmes/index.html?tq=High&evidence=Unstudied", "See all " + str(len(opps))))}
    <div class="collection">{"".join(coll_card(p, "") for p in FEATURE_OPP)}</div>
  </div>
</section>

<section class="split">
  <div>
    {coll_head("Most outcomes mapped")}
    <a class="feature-tile tile" href="programmes/{most[0]['slug']}.html" data-pid="{most[0]['id']}" style="display:block">
      <div class="tile-media"><canvas aria-hidden="true"></canvas><span class="tile-id">{most[0]['id']}</span><span class="tile-badge">{span(most[0])}</span></div>
      <h3>{esc(most[0]['short'])}</h3><p class="muted">{most[0]['n_outcomes']} outcomes, each with a mechanism, expected direction and dataset.</p></a>
    <ol class="rank-list">{"".join(f'<li><a href="programmes/{p["slug"]}.html">{esc(p["short"])}</a><span class="n">{p["n_outcomes"]}</span></li>' for p in most[1:6])}</ol>
  </div>
  <div>
    {coll_head("Districts on the map")}
    <a class="feature-tile tile" href="programmes/p07.html" data-pid="P07" style="display:block">
      <div class="tile-media"><canvas aria-hidden="true"></canvas><span class="tile-id">P07</span><span class="tile-badge">{span(P['P07'])}</span></div>
      <h3>{esc(P['P07']['short'])}</h3><p class="muted">{len(P['P07']['footprint']['phases'][0]['names'])} districts, listed by the Punjab Social Protection Authority.</p></a>
    <ol class="rank-list">{"".join(f'<li><a href="programmes/{p["slug"]}.html">{esc(p["short"])}</a><span class="n">{span(p)}</span></li>' for p in [x for x in fps if x["id"] != "P07"][:5])}</ol>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {coll_head("Where the opportunities are", "Every entry placed by how reliably its rollout can be dated and how much causal work exists. The shaded cell is the short list.", ("insights/index.html", "The catalogue in charts"))}
    <div class="opp" role="table" aria-label="Programmes by timing-data quality and existing evidence">
      <div class="h">Timing data</div><div class="h">Unstudied</div><div class="h">Limited</div><div class="h">Published causal work</div>
      {opp_rows}
    </div>
  </div>
</section>

{domain_rails}

<section class="invite">
  <div class="wrap">
    <h2>Built a rollout file?</h2>
    <p>A district-by-date treatment file for any entry saves the next researcher months. Share it and it will be hosted here with your name on it.</p>
    <div class="actions"><a class="btn" href="contribute/index.html">Contribute</a><a class="btn btn--line" href="contribute/index.html#claim">Claim an idea</a></div>
  </div>
</section>
"""
write("index.html", page(home, title=SITE_NAME, desc=f"{C['programmes']} public programmes and natural experiments in Pakistan rolled out district by district, with rollout dates, outcomes, datasets, maps and Stata code for causal evaluation.",
                         base="", active="", page_id="home", scripts=("geo", "map"), jsonld=DATASET_LD))

# =============================================================================
# BROWSE
# =============================================================================
FG = [("macro", "Domain"), ("region", "Province"), ("tq", "Timing data"), ("evidence", "Evidence"),
      ("unit", "Rollout unit"), ("method", "Design"), ("map", "Map"), ("kind", "Type")]
fgroups = "".join(f'<div class="fgroup" data-f="{k}"><button type="button" aria-expanded="false">{l} <span class="n"></span>{ICON["chev"]}</button><div class="fpanel"></div></div>' for k, l in FG)
browse = f"""
<div class="wrap"><div class="page-head">
  <h1>Programmes</h1>
  <p>{C['programmes']} entries with district-level or finer rollout variation. Start with timing data: it tells you whether the treatment date can be established from existing sources.</p>
</div></div>
<div class="filterbar"><div class="wrap"><div class="filterbar-inner">
  {fgroups}
  <div class="tools">
    <label class="sr-only" for="q">Search programmes</label><input id="q" type="search" placeholder="Search" autocomplete="off">
    <label class="sr-only" for="sort">Sort</label>
    <select id="sort"><option value="id">By ID</option><option value="tq">Timing data</option><option value="start">Start year</option><option value="outcomes">Outcomes mapped</option><option value="name">Name</option></select>
    <div class="viewtoggle" role="group" aria-label="View"><button type="button" data-view="grid" aria-pressed="true" aria-label="Grid view">{ICON["grid"]}</button><button type="button" data-view="table" aria-pressed="false" aria-label="Table view">{ICON["list"]}</button></div>
  </div>
</div></div></div>
<div class="wrap">
  <div class="chips" id="chips"></div>
  <div class="resultline"><span id="count" aria-live="polite"></span><button class="textbtn" type="button" id="dl-csv">Download these rows as CSV</button></div>
  <div class="grid" id="grid" style="display:grid">{"".join(tile(p, "../") for p in PROGS)}<div class="empty" hidden>No entries match these filters. Remove one to widen the search.</div></div>
  <div id="table-view" hidden style="padding-bottom:80px"></div>
</div>
"""
write("programmes/index.html", page(browse, title="Programmes", desc=f"Browse {C['programmes']} staggered programmes and natural experiments in Pakistan by domain, province, timing-data quality, evidence and design.",
                                    base="../", active="browse", page_id="browse", scripts=("geo", "map"), canonical="programmes/index.html"))

# =============================================================================
# PROGRAMME PAGES
# =============================================================================
SIGN_GROUP = lambda s: ("Ambiguous" if "ambiguous" in s.lower() else "Decrease" if s.startswith("-") or "reduction" in s.lower() or "faster" in s.lower() or "shorter" in s.lower()
                        else "Null or small" if s.startswith("0") else "Increase")
REG_NAME = {"ALL": "National", "PB": "Punjab", "SD": "Sindh", "KP": "Khyber Pakhtunkhwa", "BA": "Balochistan",
            "FATA": "Ex-FATA", "AJK": "Azad Kashmir", "GB": "Gilgit-Baltistan", "ICT": "Islamabad"}

for i, p in enumerate(PROGS):
    rows = [m for m in MX if m["pid"] == p["id"]]
    fp = p["footprint"]
    # phases
    if fp:
        ph_sorted = sorted(fp["phases"], key=lambda x: x["year"])
        items = ""
        for k, ph in enumerate(ph_sorted):
            src = f' <a class="link" href="{esc(ph["src"]["url"])}" rel="noopener">{esc(ph["src"]["title"])}</a>' if ph.get("src") else ""
            items += (f'<li data-k="{min(k + 1, 3)}"><span class="y">{ph["year"]}</span><span class="dot"></span>'
                      f'<span class="what">{esc(ph["label"])}<small>{esc(", ".join(ph["names"]))}.{src}</small></span></li>')
        if fp["final"] == "scope":
            fs = fp.get("final_src")
            rest = ("Remaining " + " and ".join(REG_NAME.get(r, r) for r in fp["final_regions"]) + " districts") if fp.get("final_regions") else "Remaining districts in scope"
            items += (f'<li data-k="3"><span class="y">{fp["final_year"]}</span><span class="dot"></span><span class="what">{rest}'
                      f'<small>{esc(fp.get("final_note", ""))}{(" " + "<a class=\"link\" href=\"" + esc(fs["url"]) + "\" rel=\"noopener\">" + esc(fs["title"]) + "</a>") if fs else ""}</small></span></li>')
        elif fp["final"] == "partial":
            items += ('<li data-k="scope"><span class="y">Later</span><span class="dot"></span><span class="what">Further districts'
                      '<small>Later phases reached more districts; their dates need the timing source below.</small></span></li>')
        rollout_html = f'<ol class="phases">{items}</ol>'
        if p["id"] == "P43":
            rollout_html += '<p class="small muted" style="margin-top:6px">New districts are shown on their 2019 parent units. Notification dates come from the district lineage table in the Toolkit; verify against provincial gazettes.</p>'
    else:
        rollout_html = ('<p class="lead" style="font-size:18px">No district-by-date list has been documented for this entry yet. '
                        'The map shows its stated scope only.</p>')
    refs = [b for b in BIB if p["id"] in b["pids"]]
    refs_html = ""
    if refs:
        refs_html = '<h3 style="margin-top:34px">References</h3><ul class="small" style="padding-left:1.1em;max-width:44rem">' + "".join(
            f'<li style="margin-bottom:8px">{esc(b["authors"])} ({b["year"]}). {esc(b["title"])}. <em>{esc(b["venue"])}</em>'
            f'{(" " + esc(b["vol"])) if b.get("vol") else ""}{(", " + esc(b["pages"])) if b.get("pages") else ""}. '
            + (f'<a class="link" href="{esc(b["url"])}" rel="noopener">Link</a>' if b.get("url") else f'<a class="link" href="https://scholar.google.com/scholar?q={esc(_q(b["title"]))}" rel="noopener">Find on Google Scholar</a> <span class="muted">(details to verify)</span>')
            + "</li>" for b in refs) + "</ul>"
    out_rows = "".join(
        f'<tr><td class="id">{m["oid"]}</td><td class="wide"><span class="ttl">{esc(m["outcome"])}</span><span class="sub">{esc(m["odomain"])}</span></td>'
        f'<td>{esc(m["mech"])}</td><td><span class="sign" data-g="{m["sign_group"]}">{esc(m["sign"])}</span></td>'
        f'<td class="wide">{"; ".join(("<a class=\"link\" href=\"../datasets/index.html#ds-" + k + "\">" + esc(DS[k]["dataset"].split(" (")[0]) + "</a>") for k in m["keys"]) or esc("; ".join(m["ds"]))}'
        f'<span class="feas">{esc(m["feas"])}</span></td></tr>' for m in rows)
    related = "".join(tile(P[r], "../") for r in p["related"] if r in P)
    prev_p, next_p = (PROGS[i - 1] if i > 0 else None), (PROGS[i + 1] if i < len(PROGS) - 1 else None)
    cite_txt = f"Hussain, S. (2026). {p['name']} ({p['id']}). Pakistan Evidence Catalogue, version {VERSION}. {SITE_URL}programmes/{p['slug']}.html"
    claim_url = (f"https://github.com/itssaqib/pakistan-evidence-catalogue/issues/new?template=claim.yml&title="
                 + _html.escape("[Claim] " + p["id"] + " " + p["short"]).replace(" ", "%20"))
    corr_url = (f"https://github.com/itssaqib/pakistan-evidence-catalogue/issues/new?template=correction.yml&title="
                + ("[Correction] " + p["id"] + " " + p["short"]).replace(" ", "%20"))
    corr_note = f'<div class="correction"><strong>Corrected in v2.0.</strong> {esc(p["correction"])}</div>' if p["correction"] else ""
    regions = ", ".join(REG_NAME.get(r, r) for r in p["regions"])
    body = f"""
<section class="stage p-stage">
  <div class="wrap">
    <div class="p-stage-grid">
      <div>
        <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="index.html">Programmes</a><span>/</span>{p['id']}</nav>
        <div class="p-kicker">{p['id']} &nbsp; {esc(p['macro'])}</div>
        <h1 class="p-title">{esc(p['short'])}</h1>
        <p class="p-lede">{esc(p['name'])}. {esc(p['window'])}.</p>
        <p class="claimed" id="claim-status" hidden></p>
        <div class="p-actions">
          <button class="btn" type="button" data-star="{p['id']}" aria-pressed="false">{ICON['star']}<span class="lbl">Save to shortlist</span></button>
          <a class="btn btn--line" href="#stata">Starter do-file</a>
          <a class="btn btn--line" href="{claim_url}" rel="noopener">Claim this idea</a>
        </div>
      </div>
      <div class="p-map">
        <canvas id="p-map" aria-label="Map of {esc(p['short'])}: documented rollout districts and stated scope"></canvas>
        <div class="map-legend" id="p-legend"></div>
        <button class="btn btn--sm btn--line" id="p-replay" type="button" hidden style="margin:0 0 26px">Replay rollout</button>
      </div>
    </div>
  </div>
</section>
<div class="wrap">
  <div class="facts">
    <div class="fact"><div class="k">Rollout</div><div class="v">{span(p)}<small>{esc(regions)}</small></div></div>
    <div class="fact"><div class="k">Unit</div><div class="v">{esc(p['unit_class'])}<small>{esc(p['treated'])}</small></div></div>
    <div class="fact"><div class="k">Timing data</div><div class="v">{meter(p['tq_rank'])} <span class="ml">{p['tq']}</span><small>{"Districts documented here" if fp else "Source named below"}</small></div></div>
    <div class="fact"><div class="k">Evidence</div><div class="v" style="font-size:17px"><span class="ev" data-s="{p['evidence_status']}" style="font-size:17px;color:#000">{p['evidence_status']}</span></div></div>
    <div class="fact"><div class="k">Outcomes</div><div class="v">{p['n_outcomes']}<small>mapped to datasets</small></div></div>
  </div>
  <div class="p-body">
    <nav class="toc" aria-label="On this page">
      <a href="#overview">Overview</a><a href="#rollout">Rollout</a><a href="#identification">Identification</a><a href="#outcomes">Outcomes</a>
      <a href="#coverage">Data coverage</a><a href="#power">Power</a><a href="#stata">Stata</a><a href="#cite">Cite and contribute</a>
    </nav>
    <div>
      <section class="p-sec" id="overview">
        <h2>Overview</h2>
        <p class="lead">{esc(p['ident'])}</p>
        <dl class="dl">
          <dt>Implementing agency</dt><dd>{esc(p['agency'])}</dd>
          <dt>Scope</dt><dd>{esc(p['scope'])}</dd>
          <dt>Rollout window</dt><dd>{esc(p['window'])}</dd>
          <dt>Unit of rollout</dt><dd>{esc(p['unit'])}</dd>
          <dt>Type of staggering</dt><dd>{esc(p['stagger'])}</dd>
          <dt>Assignment rule</dt><dd>{esc(p['assign'])}</dd>
          <dt>Designs it suits</dt><dd>{esc(", ".join(p['methods']))}</dd>
        </dl>
        {corr_note}
      </section>
      <section class="p-sec" id="rollout">
        <h2>Rollout</h2>
        {rollout_html}
        <div class="note"><div class="k">Where to get district-by-date data</div><p>{esc(p['timing_src'])}</p>
        <p class="small muted">Assessed quality: {esc(p['tq_note'])}. <a class="link" href="../guide/timing.html">How to obtain timing data</a></p></div>
        <p class="small" style="margin-top:18px"><a class="link" href="../atlas/index.html?p={p['id']}">Open this programme in the atlas</a></p>
      </section>
      <section class="p-sec" id="identification">
        <h2>Identification</h2>
        <h3>Main threats</h3><p style="max-width:44rem">{esc(p['threats'])}</p>
        <h3 style="margin-top:30px">Existing evidence</h3><p style="max-width:44rem">{esc(p['evidence'])}</p>
        {refs_html}
      </section>
      <section class="p-sec" id="outcomes">
        <h2>Outcomes and data</h2>
        <p class="muted" style="max-width:44rem">Each row pairs an outcome with the mechanism that would move it, the direction expected, and a dataset at a compatible resolution. Directions are hypotheses, not findings.</p>
        <div class="table-wrap" style="margin-top:20px"><table class="t otable"><thead><tr><th>ID</th><th>Outcome</th><th>Mechanism</th><th>Expected</th><th>Dataset and feasibility</th></tr></thead><tbody>{out_rows}</tbody></table></div>
      </section>
      <section class="p-sec" id="coverage">
        <h2>Data coverage</h2>
        <p class="muted" style="max-width:44rem">Survey waves before, during and after the rollout window ({span(p)}, shaded). Waves before the first phase identify pre-trends; waves inside the window carry the staggered comparison.</p>
        <div class="chart-block"><div class="chart" id="p-cal"></div>
          <div class="chart-legend"><span><i class="sw" style="background:var(--slate);border-radius:50%"></i>Survey wave</span><span><i class="sw" style="background:var(--slate);opacity:.22"></i>Continuous series</span><span><i class="sw" style="background:var(--gold);opacity:.4"></i>Rollout window</span></div>
          <p style="margin-top:12px"><button class="textbtn" type="button" data-table-toggle>Show as table</button></p><div class="chart-table"></div></div>
      </section>
      <section class="p-sec" id="power">
        <h2>Power</h2>
        <div class="calc">
          <form class="calc-form" id="mde" onsubmit="return false">
            <div class="field"><label for="mJ">Districts</label><input id="mJ" name="J" type="number" min="3" value="{p['mde']['J']}"><small>Constant 2019 boundaries in scope</small></div>
            <div class="field"><label for="mP">Share treated</label><input id="mP" name="P" type="number" min="0.02" max="0.98" step="0.01" value="{p['mde']['P']}"><small>{"From the documented district list" if (fp and fp['final']=='listed') else "0.5 suits a not-yet-treated comparison"}</small></div>
            <div class="field"><label for="mm">Pre periods</label><input id="mm" name="m" type="number" min="1" value="3"></div>
            <div class="field"><label for="mr">Post periods</label><input id="mr" name="r" type="number" min="1" value="3"></div>
            <div class="field"><label for="mphi">Serial correlation</label><input id="mphi" name="phi" type="number" min="0" max="0.95" step="0.05" value="0.4"><small>AR(1) residual correlation</small></div>
            <div class="field"><label for="ma">Significance</label><select id="ma" name="alpha"><option value="0.05">5%</option><option value="0.1">10%</option><option value="0.01">1%</option></select></div>
            <div class="field"><label for="mpw">Power</label><select id="mpw" name="power"><option value="0.8">80%</option><option value="0.9">90%</option></select></div>
          </form>
          <div class="calc-out" id="mde-out" aria-live="polite"><div class="big">—</div><div class="unit">minimum detectable effect, in residual standard deviations</div><p class="expl"></p><p class="formula"></p></div>
        </div>
        <p class="small muted" style="margin-top:16px;max-width:44rem">Difference-in-differences variance with serially correlated errors (Burlig, Preonas and Woerman 2020), AR(1) residuals, two-group equivalent. Heterogeneity-robust staggered estimators usually need somewhat more.</p>
      </section>
      <section class="p-sec" id="stata">
        <h2>Stata</h2>
        <p class="muted" style="max-width:44rem">A starter do-file for this entry: {("its documented districts as a rollout file, " if fp else "")}the harmonisation step, the robust estimators its design calls for, the sensitivity check and the power calculation.</p>
        <div class="code"><div class="code-bar"><span>{p['id'].lower()}_starter.do</span><span class="actions"><button class="btn btn--sm btn--line" type="button" data-copy="#dofile">Copy</button><button class="btn btn--sm" type="button" id="dl-do">Download</button></span></div><pre id="dofile"></pre></div>
      </section>
      <section class="p-sec" id="cite">
        <h2>Cite and contribute</h2>
        <div class="two-col">
          <div><h3>Cite this entry</h3><div class="code" style="margin-top:8px"><pre id="cite-txt" style="white-space:pre-wrap;font-family:inherit;font-size:14px">{esc(cite_txt)}</pre></div>
            <p style="margin-top:12px"><button class="textbtn" type="button" data-copy="#cite-txt">Copy citation</button></p></div>
          <div><h3>Working on it, or found an error?</h3><p>Claiming marks the entry on this page so others do not duplicate the work. Corrections with a primary source are the most useful contribution.</p>
            <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:16px"><a class="btn" href="{claim_url}" rel="noopener">Claim {p['id']}</a><a class="btn btn--line" href="{corr_url}" rel="noopener">Suggest a correction</a></div>
            <p class="small muted" style="margin-top:12px">Both open a GitHub form. No account? Email <a class="link" href="mailto:{CONTACT}?subject={p['id']}%20{p['short'].replace(' ', '%20')}">{CONTACT}</a>.</p></div>
        </div>
      </section>
    </div>
  </div>
</div>
<section class="section section--line"><div class="wrap">
  {coll_head("Related entries")}
  {rail(related, "Related entries")}
  <div style="display:flex;justify-content:space-between;gap:20px;margin-top:56px;font-size:14px">
    {f'<a href="{prev_p["slug"]}.html"><span class="muted small" style="display:block">Previous</span>{prev_p["id"]} {esc(prev_p["short"])}</a>' if prev_p else '<span></span>'}
    {f'<a href="{next_p["slug"]}.html" style="text-align:right"><span class="muted small" style="display:block">Next</span>{next_p["id"]} {esc(next_p["short"])}</a>' if next_p else '<span></span>'}
  </div>
</div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": f"{p['id']} {p['name']}",
          "about": p["name"], "isPartOf": {"@type": "Dataset", "name": SITE_NAME, "url": SITE_URL},
          "url": f"{SITE_URL}programmes/{p['slug']}.html", "license": "https://creativecommons.org/licenses/by/4.0/",
          "author": {"@type": "Person", "name": AUTHOR}}
    write(f"programmes/{p['slug']}.html", page(body, title=f"{p['id']} {p['short']}",
          desc=f"{p['name']}: {p['window']}. Rollout map, identification, {p['n_outcomes']} outcomes with datasets, power and Stata code."[:300],
          base="../", active="browse", page_id="programme", extra_body_attrs=f'data-pid="{p["id"]}"',
          scripts=("geo", "map", "charts"), og_image=f"assets/og/{p['slug']}.jpg", canonical=f"programmes/{p['slug']}.html", jsonld=ld))

# =============================================================================
# ATLAS
# =============================================================================
atlas = f"""
<h1 class="sr-only">District atlas</h1>
<div class="atlas">
  <section class="stage" aria-label="Interactive district map">
    <div class="atlas-controls">
      <div class="seg" role="group" aria-label="Map layer">
        <button type="button" data-mode="density" aria-pressed="true">Scope by year</button>
        <button type="button" data-mode="footprint" aria-pressed="false">Documented rollout</button>
        <button type="button" data-mode="lineage" aria-pressed="false">Boundary notes</button>
      </div>
      <div data-show-for="density" style="display:flex;gap:12px;align-items:center">
        <button class="play-btn" id="atlas-play" type="button" aria-label="Play 2000 to 2024">{ICON["play"]}</button>
        <label class="sr-only" for="atlas-slider">Year</label><input id="atlas-slider" type="range" min="0" max="24" value="24" style="accent-color:var(--gold);width:180px">
        <span id="atlas-yr" style="font-size:28px;font-weight:200">2024</span>
      </div>
      <div data-show-for="footprint" hidden><label class="sr-only" for="atlas-prog">Programme</label><select id="atlas-prog"></select></div>
    </div>
    <div class="atlas-controls"><div class="map-legend" id="atlas-legend"></div></div>
    <div class="atlas-map"><canvas id="atlas-map" aria-label="Pakistan district map; select a district for details"></canvas></div>
  </section>
  <aside class="atlas-panel" id="atlas-panel" aria-live="polite">
    <p class="k" style="margin-top:0">District atlas</p>
    <h2>Select a district</h2>
    <p class="muted" style="margin-top:12px">The map shows Pakistan's {C['districts']} districts on 2019 boundaries. Three layers:</p>
    <ul class="small" style="list-style:disc;padding-left:1.1em;margin-top:10px">
      <li style="border:0;padding:3px 0"><strong>Scope by year</strong>: how many catalogued programmes include each district in their stated scope or documented rollout. Scope is not treatment: national programmes count everywhere from their start year.</li>
      <li style="border:0;padding:3px 0"><strong>Documented rollout</strong>: districts named in a source for each phase of {C['footprints']} programmes.</li>
      <li style="border:0;padding:3px 0"><strong>Boundary notes</strong>: 2019 units that contain districts created later, from the crosswalk.</li>
    </ul>
    <p class="small muted" style="margin-top:16px">Punjab looks dense partly because Punjab documents more. The density of entries reflects what is published, not only what happened.</p>
  </aside>
</div>
"""
write("atlas/index.html", page(atlas, title="Atlas", desc="Interactive district map of Pakistan: programme scope by year, documented rollout districts and boundary changes since 2019.",
                               base="../", active="atlas", page_id="atlas", scripts=("geo", "map"), canonical="atlas/index.html"))

# =============================================================================
# INSIGHTS
# =============================================================================
def block(title, sub, inner, legend="", table=True, anchor=""):
    return (f'<div class="chart-block"{(" id=\"" + anchor + "\"") if anchor else ""}><div class="chart-head"><div><h3>{esc(title)}</h3><p>{sub}</p></div>'
            + (f'<div class="chart-tools"><button class="textbtn" type="button" data-table-toggle>Show as table</button></div>' if table else "")
            + f'</div>{inner}{legend}<div class="chart-table"></div></div>')

opp_full = '<div class="table-wrap" style="border-top:0"><div class="opp" id="opp" role="table" aria-label="Programmes by timing-data quality and evidence" style="min-width:760px"></div></div>'
mult = '<div class="multiples">' + "".join(tile(p, "../") for p in fps) + "</div>"
insights = f"""
<div class="wrap"><div class="page-head"><h1>Insights</h1><p>The catalogue in seven views. Every chart has a table version; hover any mark for details.</p></div></div>
<section class="section" style="padding-top:20px"><div class="wrap">
  {block("Where the opportunities are", "Each entry placed by how reliably its rollout can be dated and how much causal work exists. The shaded cell combines reliable dates with no causal study.", opp_full, table=False)}
  {block("Rollout windows, 1994 to 2026", "Bars run from the first to the latest year mentioned in each rollout window; gold dots mark documented phases. Bold labels have reliable timing data.", '<div class="chart" id="c-swim"></div>',
         '<div class="chart-legend"><span><i class="sw" style="background:var(--slate);border-radius:6px"></i>Rollout window</span><span><i class="sw" style="background:var(--gold);border-radius:50%"></i>Documented phase</span></div>')}
  {block("When programmes started", "Start years cluster after the 18th Amendment (2010) and again in the 2015 to 2019 expansion of health insurance and social protection.", '<div class="chart" id="c-era"></div>')}
  {block("What has been mapped against what", "Programme–outcome pairs by programme domain and outcome domain. Darker cells hold more hypotheses; empty cells are untested combinations.", '<div class="chart" id="c-heat"></div>', '<div class="chart-legend"></div>', anchor="outcomes")}
  {block("The datasets doing the work", "Datasets referenced most often across the 322 programme–outcome pairs.", '<div class="chart" id="c-ds"></div>')}
  {block("Survey calendar", "District-identified waves of the main surveys and continuous series. Open a programme page to see these against its rollout window.", '<div class="chart" id="c-cal"></div>',
         '<div class="chart-legend"><span><i class="sw" style="background:var(--slate);border-radius:50%"></i>Survey wave</span><span><i class="sw" style="background:var(--slate);opacity:.22"></i>Continuous series</span></div>')}
  {block("Documented footprints", f"The {C['footprints']} entries with districts named in a source. Hover a map to replay its phases.", mult, table=False)}
</div></section>
"""
write("insights/index.html", page(insights, title="Insights", desc="The Pakistan Evidence Catalogue in charts: opportunity matrix, rollout timelines, outcome coverage, dataset usage and survey calendar.",
                                  base="../", active="insights", page_id="insights", scripts=("geo", "map", "charts"), canonical="insights/index.html"))

# =============================================================================
# DATASETS
# =============================================================================
def ds_card(d):
    tags = [d["access_class"], f"District ID: {d['district']}", d["panel"]]
    users = sorted({m["pid"] for m in MX if d["key"] in m["keys"]})
    return (f'<article class="ds-card" id="ds-{d["key"]}" data-access="{esc(d["access_class"])}" data-district="{esc(d["district"])}" data-panel="{esc(d["panel"])}">'
            f'<h3>{esc(d["dataset"])}</h3><div class="prod">{esc(d["producer"])}</div>'
            f'<div class="tags">{"".join(f"<span class=\"tag\">{esc(t)}</span>" for t in tags)}</div>'
            f'<p class="cov"><strong style="font-weight:400">Coverage.</strong> {esc(d["coverage"])}</p>'
            f'<p class="small muted">{esc(d["notes"])}</p>'
            f'<div class="acts"><a href="{esc(d["url"] if d["url"].startswith("http") else "https://" + d["url"].split(" ;")[0].strip())}" rel="noopener">Source</a>'
            f'<span class="muted" style="text-transform:none;letter-spacing:0">Used by {len(users)} entries</span></div></article>')

dsf = lambda k, vals: "".join(f'<button class="btn btn--sm btn--line" type="button" data-dsf="{k}" data-v="{esc(v)}" aria-pressed="false">{esc(v)}</button>' for v in vals)
datasets = f"""
<div class="wrap"><div class="page-head"><h1>Datasets</h1><p>{C['datasets']} datasets that measure outcomes at district resolution or finer. The access route matters as much as the dataset: several need a research agreement, not a download.</p></div></div>
<section class="section" style="padding-top:20px"><div class="wrap">
  <div class="chart-block"><div class="chart-head"><div><h3>Survey calendar</h3><p>Pick a programme to see how many waves fall before, during and after its rollout.</p></div>
    <div class="chart-tools"><label class="sr-only" for="ds-prog">Programme</label><select id="ds-prog" style="font:inherit;font-size:14px;border:0;border-bottom:1px solid var(--line-2);padding:6px 0;max-width:340px"></select><button class="textbtn" type="button" data-table-toggle>Show as table</button></div></div>
    <div class="chart" id="ds-cal"></div><div class="chart-table"></div></div>
</div></section>
<section class="section section--line"><div class="wrap">
  <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:26px">
    <span class="dsf-label">Access</span>{dsf("access", ["Open download", "On request", "Restricted"])}<span class="dsf-label">District identifier</span>{dsf("district", ["Yes", "Partial", "Derivable"])}<span class="dsf-label">Panel</span>{dsf("panel", ["Panel-ready", "Few waves", "Cross-section"])}
    <span class="small muted" style="margin-left:auto"><span id="ds-count">{C['datasets']}</span> datasets</span>
  </div>
  <div class="ds-grid">{"".join(ds_card(d) for d in sorted(DSETS, key=lambda d: d["dataset"]))}</div>
</div></section>
"""
write("datasets/index.html", page(datasets, title="Datasets", desc="Survey calendar and catalogue of 55 datasets for district-level evaluation in Pakistan, with coverage, district identifiers and access routes.",
                                  base="../", active="datasets", page_id="datasets", scripts=("charts",), canonical="datasets/index.html"))

# =============================================================================
# TOOLKIT
# =============================================================================
def size(rel):
    try:
        n = os.path.getsize(os.path.join(SITE, rel))
    except OSError:
        return ""
    return f"{n/1024:.0f} KB" if n < 1024 * 1024 else f"{n/1024/1024:.1f} MB"

DL = [("data/programmes.csv", "CSV", "Programmes", f"{C['programmes']} rows with every field"),
      ("data/programme_outcome_matrix.csv", "CSV", "Programme × outcome matrix", f"{C['pairs']} rows"),
      ("data/outcomes.csv", "CSV", "Outcome taxonomy", f"{C['outcomes']} outcomes"),
      ("data/datasets.csv", "CSV", "Dataset catalogue", f"{C['datasets']} datasets"),
      ("data/documented_footprints.csv", "CSV", "Documented rollout districts", "One row per programme, phase and district, with sources"),
      ("data/programmes.dta", "DTA", "Programmes for Stata", "Stata 14+ format, labelled"),
      ("data/programme_outcome_matrix.dta", "DTA", "Matrix for Stata", ""),
      ("data/documented_footprints.dta", "DTA", "Footprints for Stata", ""),
      ("data/catalogue.json", "JSON", "Everything, nested", "As the site uses it"),
      ("data/references.bib", "BIB", "References", "BibTeX for the catalogue and cited studies"),
      ("toolkit/pec-stata-kit.zip", "ZIP", "Stata starter kit", "Do-files and the crosswalk .dta")]
dl_rows = "".join(f'<div class="dlrow"><span class="fmt">{f}</span><span class="nm">{esc(n)}<small>{esc(s)}</small></span><span class="sz">{size(r)}</span>'
                  f'<a class="btn btn--sm btn--line" href="../{r}" download>Download</a></div>' for r, f, n, s in DL)
CW = [("data/districts/district_crosswalk.csv", "CSV", "District crosswalk", "200 name variants mapped to 126 boundary units"),
      ("data/districts/district_crosswalk.dta", "DTA", "District crosswalk for Stata", "Merge on key"),
      ("data/districts/boundary_units.csv", "CSV", "Boundary units", "126 districts with province and centroid"),
      ("data/districts/district_lineage.csv", "CSV", "District lineage", "Districts created after the boundary vintage, with containment checks")]
cw_rows = "".join(f'<div class="dlrow"><span class="fmt">{f}</span><span class="nm">{esc(n)}<small>{esc(s)}</small></span><span class="sz">{size(r)}</span>'
                  f'<a class="btn btn--sm btn--line" href="../{r}" download>Download</a></div>' for r, f, n, s in CW)
lin_rows = "".join(f'<tr><td>{esc(r["district"])}</td><td>{esc(r["province"])}</td><td>{r["created"] or "—"}</td><td>{esc(r["parent_named"])}</td>'
                   f'<td>{esc(r["contained_in_unit"])}</td><td>{esc(r["check"])}</td><td>{esc(r["confidence"])}</td></tr>' for r in D["lineage"])
stata_dir = os.path.join(SITE, "toolkit", "stata")
stata_files = sorted(f for f in os.listdir(stata_dir) if f.endswith(".do"))
stata_html = ""
for k, f in enumerate(stata_files):
    code = open(os.path.join(stata_dir, f), encoding="utf-8").read()
    stata_html += (f'<details class="code" style="margin-top:12px"{" open" if k == 0 else ""}><summary class="code-bar" style="cursor:pointer;list-style:none"><span><strong style="color:#000;font-weight:400">{f}</strong></span>'
                   f'<span class="actions"><button class="btn btn--sm btn--line" type="button" data-copy="#sk{k}">Copy</button><a class="btn btn--sm" href="stata/{f}" download>Download</a></span></summary>'
                   f'<pre id="sk{k}">{esc(code)}</pre></details>')
toolkit = f"""
<div class="wrap"><div class="page-head"><h1>Toolkit</h1><p>Data downloads, a district crosswalk on constant boundaries, a Stata starter kit and a power calculator.</p></div></div>
<section class="section" id="downloads" style="padding-top:20px"><div class="wrap">
  {coll_head("Downloads", f"Version {VERSION}, {RELEASED}. CC BY 4.0. The site is generated from these files.")}
  <div class="downloads">{dl_rows}</div>
</div></section>
<section class="section section--mist" id="crosswalk"><div class="wrap">
  {coll_head("District crosswalk", "Pakistan's district list changes almost every year. The crosswalk maps 200 spellings, former names and post-2019 districts onto 126 constant boundary units, so panels built on it do not break when a district splits.")}
  <div class="two-col">
    <div class="prose">
      <h3>How it works</h3>
      <p>The map boundaries are geoBoundaries' 2019 district polygons. Every district created since then is folded into the 2019 unit that contains its headquarters. Each assignment was tested by point-in-polygon on the headquarters coordinates; the <em>check</em> column says whether the test agrees with the parent district on record.</p>
      <p>Two artefacts of the boundary file are documented rather than hidden: Larkana is not a separate polygon (its headquarters falls inside the Qambar Shahdadkot unit), and Azad Kashmir and Karachi are single units.</p>
      <p>Merge on <code>key</code>: lower case, ampersand to "and", the words district, agency, tribal and frontier region removed, letters and digits only. <code>01_harmonise_districts.do</code> does this for you.</p>
      <p class="small muted">Status: version 0.1. Rows marked low confidence or "check" need verifying against provincial gazette notifications. Corrections are very welcome.</p>
    </div>
    <div><div class="downloads">{cw_rows}</div></div>
  </div>
  <div class="table-wrap" style="margin-top:36px"><table class="t"><caption>Districts created after the boundary vintage, and the 2019 unit containing each.</caption><thead><tr><th>District</th><th>Province</th><th>Created</th><th>Parent on record</th><th>Contained in unit</th><th>Check</th><th>Confidence</th></tr></thead><tbody>{lin_rows}</tbody></table></div>
</div></section>
<section class="section" id="stata"><div class="wrap">
  {coll_head("Stata starter kit", "Explicit, line-by-line do-files. Every programme page also generates a do-file pre-filled with that entry's documented districts and design.", ("pec-stata-kit.zip", "Download the kit"))}
  {stata_html}
</div></section>
<section class="section section--mist" id="power"><div class="wrap">
  {coll_head("Power calculator", "Minimum detectable effect for a district panel difference-in-differences with serially correlated errors.")}
  <div class="calc">
    <form class="calc-form" id="mde" onsubmit="return false">
      <div class="field"><label for="mJ">Districts</label><input id="mJ" name="J" type="number" min="3" value="126"><small>126 national; 34 Punjab; 31 KP; 22 Sindh; 27 Balochistan</small></div>
      <div class="field"><label for="mP">Share treated</label><input id="mP" name="P" type="number" min="0.02" max="0.98" step="0.01" value="0.5"></div>
      <div class="field"><label for="mm">Pre periods</label><input id="mm" name="m" type="number" min="1" value="3"></div>
      <div class="field"><label for="mr">Post periods</label><input id="mr" name="r" type="number" min="1" value="3"></div>
      <div class="field"><label for="mphi">Serial correlation</label><input id="mphi" name="phi" type="number" min="0" max="0.95" step="0.05" value="0.4"><small>AR(1) residual correlation</small></div>
      <div class="field"><label for="ma">Significance</label><select id="ma" name="alpha"><option value="0.05">5%</option><option value="0.1">10%</option><option value="0.01">1%</option></select></div>
      <div class="field"><label for="mpw">Power</label><select id="mpw" name="power"><option value="0.8">80%</option><option value="0.9">90%</option></select></div>
    </form>
    <div class="calc-out" id="mde-out" aria-live="polite"><div class="big">—</div><div class="unit">minimum detectable effect, in residual standard deviations</div><p class="expl"></p><p class="formula"></p></div>
  </div>
  <p class="small muted" style="margin-top:16px;max-width:46rem">Burlig, F., Preonas, L. and Woerman, M. (2020). Panel data and experimental design. <em>Journal of Development Economics</em> 144. Closed form for AR(1) errors; the same calculation is in <code>20_power_mde.do</code>.</p>
</div></section>
<section class="section" id="cite"><div class="wrap">
  {coll_head("Cite the catalogue")}
  <div class="code" style="max-width:52rem;margin:0 auto"><pre id="cite-all" style="white-space:pre-wrap">@misc{{hussain2026pec,
  author = {{Hussain, Saqib}},
  year   = {{2026}},
  title  = {{Pakistan Evidence Catalogue: Staggered District-Level Programmes for Causal Impact Evaluation}},
  note   = {{Version {VERSION}}},
  url    = {{{SITE_URL}}}
}}</pre></div>
  <p style="text-align:center;margin-top:14px"><button class="textbtn" type="button" data-copy="#cite-all">Copy BibTeX</button></p>
</div></section>
"""
write("toolkit/index.html", page(toolkit, title="Toolkit", desc="Downloads (CSV, JSON, Stata), a Pakistan district crosswalk on constant 2019 boundaries, a Stata starter kit for staggered DiD and a power calculator.",
                                 base="../", active="toolkit", page_id="toolkit", canonical="toolkit/index.html", jsonld=DATASET_LD))

# =============================================================================
# GUIDE: methods, timing, caveats
# =============================================================================
guide_nav = lambda cur: ('<div class="wrap" style="display:flex;justify-content:center;gap:28px;padding-bottom:10px;font-size:13px;text-transform:uppercase;letter-spacing:.08em">'
                         + "".join(f'<a href="{h}"{" style=\"border-bottom:2px solid var(--gold)\"" if h == cur else ""}>{l}</a>' for h, l in
                                   [("index.html", "Methods"), ("timing.html", "Treatment dates"), ("caveats.html", "Caveats")]) + "</div>")
notes = "".join(f'<div class="guide-item"><div><h3>{h}</h3><p>{b}</p></div></div>' for h, b in CONTENT["NOTES"])
pkgs = "".join(f'<tr><td style="white-space:nowrap">{a}{(", " + b) if b else ""}</td><td>{desc}</td><td class="small" style="white-space:nowrap">{esc(cmd)}</td></tr>' for a, b, desc, cmd in CONTENT["PKGS"])
methods = f"""
<div class="wrap"><div class="page-head"><h1>Guide</h1><p>Twelve things to settle before estimating anything with the variation in this catalogue. None of it is novel; all of it is routinely skipped.</p></div></div>
{guide_nav("index.html")}
<section class="section" style="padding-top:30px"><div class="wrap"><div class="guide-list">{notes}</div></div></section>
<section class="section section--mist"><div class="wrap">
  {coll_head("Packages", "Stata packages for each step. R equivalents: did, didimputation, fixest::sunab, HonestDiD, synthdid.", ("../toolkit/index.html#stata", "Get the starter kit"))}
  <div class="table-wrap"><table class="t"><thead><tr><th>Package</th><th>What it does</th><th>Install</th></tr></thead><tbody>{pkgs}</tbody></table></div>
</div></section>
"""
write("guide/index.html", page(methods, title="Guide", desc="Identification playbook for staggered district-level designs in Pakistan: estimators, comparison groups, boundaries, clustering and reporting.",
                               base="../", active="guide", page_id="guide", canonical="guide/index.html"))

trows = "".join(f'<tr><td class="wide"><span class="ttl">{n}</span></td><td class="wide">{w}</td><td style="white-space:nowrap"><a class="link" href="{esc(u)}" rel="noopener">{wl}</a></td><td class="wide small">{note}</td></tr>'
                for n, w, wl, u, note in [(t[0], t[1], t[2], t[3] if t[3].startswith("http") else "../datasets/index.html", t[4]) for t in CONTENT["TIMING"]])
timing = f"""
<div class="wrap"><div class="page-head"><h1>Treatment dates</h1><p>The binding constraint on most of these ideas is knowing which district was treated when. Nine routes, roughly in order of reliability.</p></div></div>
{guide_nav("timing.html")}
<section class="section" style="padding-top:30px"><div class="wrap">
  <div class="note" style="margin:0 0 30px"><div class="k">The practical order</div><p>Start with published evaluations and World Bank implementation reports: someone may already have built the file. Then Annual Development Programme scheme registers, which are public and under-used. Then a Right to Information request naming a specific register. Treat press reports as triangulation only.</p></div>
  <div class="table-wrap"><table class="t"><thead><tr><th>Source</th><th>What it gives you</th><th>Where</th><th>Practical note</th></tr></thead><tbody>{trows}</tbody></table></div>
</div></section>
<section class="section section--mist"><div class="wrap two-col">
  <div><h3 style="font-size:22px;font-weight:500">An RTI request that works</h3><p style="margin-top:10px">Ask for a record that already exists, not for analysis. Name the register, the custodian and the fields.</p>
  <div class="code"><pre style="white-space:pre-wrap">To: Public Information Officer, [Department]
Under Section 10, Punjab Transparency and
Right to Information Act 2013

I request a copy of the following existing record:

1. The register or database recording the date on
   which each [facility / centre / scheme] under
   [programme] became operational, listing district,
   tehsil, unit name and date of operationalisation.

2. Covering the period [start] to [end].

I am content to receive it in any electronic format
in which it is already held. I do not require any
new compilation or analysis.</pre></div></div>
  <div><h3 style="font-size:22px;font-weight:500">How timing data is graded</h3>
  <dl class="dl"><dt>High</dt><dd>Dates are published, or sit in a named register someone has already assembled. Verifying takes hours.</dd>
  <dt>Medium-high</dt><dd>Dates exist in administrative records and can be obtained with a request or a document search. Weeks.</dd>
  <dt>Medium</dt><dd>Dates exist but are scattered across sources that disagree. Expect to reconcile and document judgement calls.</dd>
  <dt>Low</dt><dd>No reliable district dating known. Needs primary collection or a satellite proxy.</dd></dl></div>
</div></section>
"""
write("guide/timing.html", page(timing, title="Treatment dates", desc="Nine routes to district-by-date treatment data in Pakistan, an RTI template, and how timing data is graded.",
                                base="../", active="guide", page_id="guide", canonical="guide/timing.html"))

cav = "".join(f'<div class="guide-item"><div><h3>{h}</h3><p>{w}</p><p class="do"><strong style="font-weight:500">What to do.</strong> {d}</p></div></div>' for h, w, d in CONTENT["CAV"])
caveats = f"""
<div class="wrap"><div class="page-head"><h1>Caveats</h1><p>Eight problems that apply to the catalogue as a whole. Each programme page lists its own threats; these recur everywhere.</p></div></div>
{guide_nav("caveats.html")}
<section class="section" style="padding-top:30px"><div class="wrap"><div class="guide-list">{cav}</div></div></section>
"""
write("guide/caveats.html", page(caveats, title="Caveats", desc="Recurring threats to identification: boundary changes, targeting on the outcome, switching treatment, migration sorting, measurement.",
                                 base="../", active="guide", page_id="guide", canonical="guide/caveats.html"))

# =============================================================================
# ABOUT, CONTRIBUTE, SHORTLIST, 404
# =============================================================================
corrections = "".join(f'<li><strong style="font-weight:500">{p["id"]} {esc(p["short"])}.</strong> {esc(p["correction"])}</li>' for p in PROGS if p["correction"])
about = f"""
<div class="wrap"><div class="page-head"><h1>About</h1><p>What the catalogue is, how it was built, and what it is not.</p></div></div>
<section class="section" style="padding-top:20px"><div class="wrap two-col">
  <div class="prose">
    <h2>Why it exists</h2>
    <p>Pakistan ran an unusual number of large public programmes that reached different places at different times. Health insurance activated division by division across Punjab within a year. Cash transfers were gated by the date each district's poverty census finished. Districts were created, merged and renamed throughout.</p>
    <p>That is the variation causal inference needs, and most of it has never been used. The reason is rarely the question. It is that establishing when each district was treated is a research project in itself, and there is no way to know in advance whether an outcome exists at the same resolution.</p>
    <p>The catalogue collects both facts for {C['programmes']} entries, maps {C['pairs']} programme–outcome pairs against {C['datasets']} datasets, and grades how reliable the timing data is, including where it is not reliable at all.</p>
    <h2>How it was built</h2>
    <p>From agency websites and annual reports, provincial development programme registers, World Bank and ADB project documents, third-party evaluations and the published literature. Rollout lists appear on the map only when a named source lists the districts; everything else is shown as stated scope.</p>
    <p>District boundaries are geoBoundaries' 2019 polygons (public domain), simplified to about one kilometre with shared borders preserved, and projected in an equal-area projection.</p>
    <h2>What it is not</h2>
    <p>It is not a census of Pakistani public policy: Punjab is documented far better than Balochistan. It is not a store of treatment-timing data, except where districts are listed with sources. And it is not evidence: the expected directions are hypotheses, and nothing here has been estimated.</p>
  </div>
  <div>
    <div class="callout"><h3 style="font-size:20px;font-weight:500">Maintainer</h3><p style="margin-top:8px"><a class="link" href="{AUTHOR_URL}">{AUTHOR}</a>, applied microeconomist working on conflict, political economy and state capacity in South Asia.</p><p><a class="link" href="mailto:{CONTACT}">{CONTACT}</a></p></div>
    <div style="margin-top:28px"><h3 style="font-size:20px;font-weight:500">Changes in version 2.0</h3>
      <ul class="small" style="padding-left:1.1em;margin-top:12px"><li>District maps for every entry, with {C['footprints']} documented rollout footprints and their sources.</li><li>District crosswalk and lineage table on constant 2019 boundaries.</li><li>Stata starter kit, per-programme do-files, .dta exports and a power calculator.</li><li>Evidence status, related entries and dataset panel-readiness for every record.</li>{corrections}</ul></div>
    <div style="margin-top:28px"><h3 style="font-size:20px;font-weight:500">Design</h3><p class="small" style="margin-top:8px">Typeset in Jost (SIL Open Font License), self-hosted. Map and chart colours were checked for colour-vision deficiency and contrast.</p></div>
  </div>
</div></section>
"""
write("about/index.html", page(about, title="About", desc="Why the Pakistan Evidence Catalogue exists, how it was built, what it is not, and what changed in version 2.0.",
                               base="../", active="about", page_id="about", canonical="about/index.html"))

gh = "https://github.com/itssaqib/pakistan-evidence-catalogue/issues/new?template="
contribute = f"""
<div class="wrap"><div class="page-head"><h1>Contribute</h1><p>Four ways to take part, in order of how much they help. Each opens a short form on GitHub; email works too.</p></div></div>
<section class="section" style="padding-top:20px"><div class="wrap">
  <div class="collection" style="grid-template-columns:repeat(2,1fr);gap:0">
    <div style="padding:34px 34px 34px 0;border-bottom:1px solid var(--line)"><h3 style="font-size:22px">Share a rollout file</h3><p style="margin-top:10px">A district-by-date treatment file for any entry. It will be hosted here with your name and the programme page will link to it.</p><a class="btn" style="margin-top:18px" href="{gh}timing-file.yml">Share a file</a></div>
    <div style="padding:34px 0 34px 34px;border-bottom:1px solid var(--line);border-left:1px solid var(--line)" id="claim"><h3 style="font-size:22px">Claim an idea</h3><p style="margin-top:10px">Working on an entry? Claiming marks it on the programme page so others know. It coordinates; it does not reserve.</p><a class="btn" style="margin-top:18px" href="{gh}claim.yml">Claim an entry</a></div>
    <div style="padding:34px 34px 34px 0"><h3 style="font-size:22px">Correct a date or a claim</h3><p style="margin-top:10px">Secondary sources disagree routinely. A correction backed by a primary document is worth more than a new entry.</p><a class="btn btn--line" style="margin-top:18px" href="{gh}correction.yml">Suggest a correction</a></div>
    <div style="padding:34px 0 34px 34px;border-left:1px solid var(--line)"><h3 style="font-size:22px">Suggest a programme</h3><p style="margin-top:10px">Coverage is thinnest for Sindh, Balochistan and Gilgit-Baltistan. The test: did it reach different places at different times, and can that be dated?</p><a class="btn btn--line" style="margin-top:18px" href="{gh}new-programme.yml">Suggest a programme</a></div>
  </div>
  <p class="small muted" style="margin-top:30px;text-align:center">No GitHub account? Email <a class="link" href="mailto:{CONTACT}">{CONTACT}</a>. Contributions are released under CC BY 4.0 unless you say otherwise. Contributing is not a claim on anyone's paper.</p>
</div></section>
"""
write("contribute/index.html", page(contribute, title="Contribute", desc="Share a rollout file, claim an idea, correct a date or suggest a programme for the Pakistan Evidence Catalogue.",
                                    base="../", active="", page_id="contribute", canonical="contribute/index.html"))

shortlist = f"""
<div class="wrap"><div class="page-head"><h1>Shortlist</h1><p>Programmes you have saved, side by side. The list lives in this browser only.</p></div></div>
<section class="section" style="padding-top:10px"><div class="wrap">
  <div id="sl-tools" hidden style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-bottom:26px"><button class="btn btn--sm" type="button" id="sl-csv">Download CSV</button><button class="btn btn--sm btn--line" type="button" id="sl-bib">Download BibTeX</button><button class="btn btn--sm btn--line" type="button" id="sl-clear">Clear</button></div>
  <div class="compare" id="compare" hidden></div>
  <div id="sl-empty" class="empty" style="padding:40px 0 60px">Nothing saved yet. Use the star on any map tile or programme page.<br><br><a class="btn" href="../programmes/index.html">Browse programmes</a></div>
</div></section>
"""
write("shortlist/index.html", page(shortlist, title="Shortlist", desc="Your saved programmes, compared side by side.", base="../", active="", page_id="shortlist", canonical="shortlist/index.html"))

nf = """
<div class="wrap"><div class="page-head" style="padding:90px 0 120px"><h1>Page not found</h1>
<p>The link may be out of date. Programme pages are at /programmes/p01.html to /programmes/p67.html.</p>
<p style="margin-top:28px"><a class="btn" href="/pakistan-evidence-catalogue/index.html">Go to the catalogue</a></p></div></div>
"""
write("404.html", page(nf, title="Page not found", desc="Page not found.", base="/pakistan-evidence-catalogue/", page_id="404"))

print("pages written:", sum(len(f) for _, _, f in os.walk(SITE) if True) and len([1 for r, _, fs in os.walk(SITE) for f in fs if f.endswith(".html")]))
