# -*- coding: utf-8 -*-
"""Programme detail pages (one per entry)."""
import json, os
from layout import page, esc, SITE, VERSION, RELEASED, AUTHOR, CONTACT, REPO

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
D = json.load(open(f"{ROOT}/data/catalogue.json", encoding="utf-8"))
PROGS, OUTS, DSETS, MX, META = D["programmes"], D["outcomes"], D["datasets"], D["matrix"], D["meta"]

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


SIGN_NOTE = {
    "+": "Increase expected",
    "-": "Decrease expected",
    "ambiguous": "Sign ambiguous — theory points both ways",
}


def sign_pill(sign):
    s = sign.lower()
    if s.startswith("ambiguous") or "ambiguous" in s:
        cls = "pill--claimed"
    elif s.startswith("-") or "reduction" in s or "faster" in s or "shorter" in s:
        cls = "pill--active"
    elif s.startswith("0"):
        cls = "pill--done"
    else:
        cls = "pill--open"
    return f'<span class="pill {cls}">{esc(sign)}</span>'


for idx, p in enumerate(PROGS):
    rows = mx_by_prog.get(p["id"], [])

    # ---- outcomes table ----
    orows = ""
    for m in rows:
        o = out_by_id.get(m["outcome_id"], {})
        ds_links = []
        for s in m["sources"]:
            d = ds_by_key[s["key"]]
            ds_links.append(f'<a href="../datasets/#{esc(s["key"])}">{esc(d["dataset"])}</a>')
        extras = [n for n in m["dataset_names"]
                  if not any(ds_by_key[s["key"]]["dataset"] in n for s in m["sources"])]
        ds_cell = "; ".join(ds_links)
        if extras:
            ds_cell += ('; ' if ds_cell else '') + "; ".join(esc(e) for e in extras)
        orows += f"""<tr>
          <td class="id">{esc(m['outcome_id'])}</td>
          <td class="wide"><strong>{esc(m['outcome'])}</strong>
            <span class="rowsub">{esc(o.get('domain',''))}</span></td>
          <td class="wide">{esc(m['mechanism'])}</td>
          <td style="white-space:nowrap">{sign_pill(m['expected_sign'])}</td>
          <td class="wide">{ds_cell}</td>
          <td class="wide">{esc(m['feasibility'])}</td>
        </tr>"""

    # ---- unique datasets for this programme ----
    seen, dlist = set(), []
    for m in rows:
        for s in m["sources"]:
            if s["key"] not in seen:
                seen.add(s["key"])
                dlist.append(ds_by_key[s["key"]])
    dlist.sort(key=lambda d: d["dataset"])
    ds_items = "".join(
        f'<li><a href="../datasets/#{esc(d["key"])}">{esc(d["dataset"])}</a>'
        f'<span class="rowsub">{esc(d["producer"])} &middot; {esc(d["district_id"])}</span></li>'
        for d in dlist)

    methods_tags = "".join(f'<span class="tag">{esc(m)}</span>' for m in p["methods"])
    region_tags = "".join(f'<span class="tag">{esc(r)}</span>' for r in p["regions"])

    prev_p = PROGS[idx - 1] if idx > 0 else None
    next_p = PROGS[idx + 1] if idx < len(PROGS) - 1 else None
    pager = '<div class="pager">'
    if prev_p:
        pager += (f'<a href="{prev_p["slug"]}.html"><span class="dir">Previous</span>'
                  f'{esc(prev_p["id"])} — {esc(prev_p["programme"])}</a>')
    else:
        pager += "<span></span>"
    if next_p:
        pager += (f'<a href="{next_p["slug"]}.html" style="text-align:right">'
                  f'<span class="dir">Next</span>{esc(next_p["id"])} — {esc(next_p["programme"])}</a>')
    else:
        pager += "<span></span>"
    pager += "</div>"

    citation = (f'Hussain, S. ({RELEASED[-4:]}). "{p["programme"]}" ({p["id"]}), '
                f'{SITE}, version {VERSION}.')

    body = f"""
<div class="wrap shell">
  <nav class="crumb" aria-label="Breadcrumb">
    <a href="../">Home</a><span>/</span><a href="./">Programmes</a><span>/</span>{esc(p['id'])}
  </nav>
</div>

<div class="wrap shell">
  <div class="pagehead">
    <p class="eyebrow"><span class="mono">{esc(p['id'])}</span> &middot; {esc(p['domain'])}
      &middot; {esc(p['kind'])}</p>
    <h1>{esc(p['programme'])}</h1>
    <p class="lede">{esc(p['staggering'])}. Rolled out by {esc(p['unit_class'].lower())}
      across {esc(p['n_districts'])}, {esc(p['rollout_window'][0].lower() + p['rollout_window'][1:])}.</p>
    <div style="margin-top:14px">
      <span class="pill pill--open">Status: Open</span>
      &nbsp;{meter(p['quality_rank'], p['quality_label'] + ' timing data')}
    </div>
  </div>

  <div class="grid grid--sidebar">
    <div>
      <h2>Rollout</h2>
      <svg class="timeline" id="tl" aria-label="Rollout window"></svg>
      <p class="small muted" style="margin-top:-6px">{esc(p['rollout_window'])}</p>

      <dl class="meta" style="margin-top:20px">
        <dt>Implementing agency</dt><dd>{esc(p['agency'])}</dd>
        <dt>Geographic scope</dt><dd>{esc(p['scope'])}<div style="margin-top:6px">{region_tags}</div></dd>
        <dt>Start year</dt><dd class="mono">{esc(p['start_year'])}</dd>
        <dt>Rollout window</dt><dd>{esc(p['rollout_window'])}</dd>
        <dt>Unit of rollout</dt><dd>{esc(p['rollout_unit'])}</dd>
        <dt>Treated units</dt><dd>{esc(p['n_districts'])}</dd>
        <dt>Type of staggering</dt><dd>{esc(p['staggering'])}</dd>
        <dt>Assignment rule</dt><dd>{esc(p['assignment'])}</dd>
        <dt>Designs it suits</dt><dd>{methods_tags}</dd>
      </dl>

      <h2 style="margin-top:36px">Treatment timing</h2>
      <div class="box">
        <p class="eyebrow">Where to get district-by-date data</p>
        <p style="margin-bottom:10px">{esc(p['timing_source'])}</p>
        <p class="small muted" style="margin:0">Assessed quality: <strong>{esc(p['timing_quality_note'])}</strong>.
        Verify against the primary document before use — dates in press coverage and programme
        retrospectives frequently disagree by a year.
        <a href="../timing/">How to obtain timing data &rarr;</a></p>
      </div>

      <h2 style="margin-top:36px">Identification</h2>
      <div class="prose"><p>{esc(p['identification'])}</p></div>

      <div class="callout">
        <p class="eyebrow">Main threats to identification</p>
        <p style="margin:0">{esc(p['threats'])}</p>
      </div>

      <h2 style="margin-top:36px">Existing evidence</h2>
      <div class="prose"><p>{esc(p['evidence'])}</p></div>

      <h2 style="margin-top:36px">Outcomes and data ({len(rows)})</h2>
      <p class="small muted" style="max-width:52em">Each row pairs an outcome with the mechanism
      that would produce it, the expected direction, and a dataset that measures it at a
      compatible resolution. Expected signs are hypotheses, not findings.</p>
      <div class="tablewrap" style="margin-top:16px">
        <table class="data">
          <caption>{len(rows)} outcomes mapped for {esc(p['id'])}</caption>
          <thead><tr>
            <th scope="col">ID</th><th scope="col">Outcome</th>
            <th scope="col">Mechanism / hypothesis</th>
            <th scope="col">Expected</th>
            <th scope="col">Dataset</th>
            <th scope="col">Feasibility note</th>
          </tr></thead>
          <tbody>{orows}</tbody>
        </table>
      </div>

      {pager}
    </div>

    <aside class="sidebar">
      <div class="box box--paper">
        <h3>At a glance</h3>
        <ul class="plain small">
          <li><strong>Timing quality</strong><br>{meter(p['quality_rank'], p['quality_label'])}</li>
          <li><strong>Outcomes mapped</strong><br><span class="mono">{len(rows)}</span></li>
          <li><strong>Datasets involved</strong><br><span class="mono">{len(dlist)}</span></li>
          <li><strong>Rollout unit</strong><br>{esc(p['unit_class'])}</li>
        </ul>
      </div>

      <div class="box">
        <h3>Claim this idea</h3>
        <p class="small">If you are working on this, say so and it will be marked here, so others
        do not duplicate the effort. Open a repository issue or send an email.</p>
        <p><a class="btn btn--accent btn--sm"
          href="mailto:{CONTACT}?subject=Claiming%20{esc(p['id'])}%20—%20{esc(p['programme'][:60])}&amp;body=Name%3A%0AAffiliation%3A%0AExpected%20timeline%3A%0ANotes%3A">Claim {esc(p['id'])}</a></p>
        <p class="small" style="margin-top:10px"><a href="../contribute/">Suggest a correction</a></p>
      </div>

      <div class="box">
        <h3>Datasets used here</h3>
        <ul class="plain small">{ds_items}</ul>
      </div>

      <div class="box">
        <h3>Cite this entry</h3>
        <div class="cite" id="cite">{esc(citation)}</div>
        <button class="copybtn" type="button" data-copy="#cite">Copy citation</button>
      </div>
    </aside>
  </div>
</div>
"""

    js = f"""<script>
PEC.timeline(document.getElementById('tl'), {json.dumps({
    'rollout_window': p['rollout_window'], 'start_year': p['start_year']})});
</script>"""

    desc = (f"{p['programme']} ({p['id']}): rollout {p['rollout_window']}. "
            f"{len(rows)} outcomes mapped with datasets and sources for causal evaluation.")[:300]

    write(f"programmes/{p['slug']}.html",
          page(body, f"{p['id']} — {p['programme']}", desc,
               base="../", active="programmes/", extra_js=js))

print(f"{len(PROGS)} programme pages written")
