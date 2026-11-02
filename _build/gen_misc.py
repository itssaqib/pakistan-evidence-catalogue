# -*- coding: utf-8 -*-
"""Caveats, downloads, contribute, about, 404."""
import json, os, glob
from layout import page, esc, SITE, TAGLINE, VERSION, RELEASED, AUTHOR, AUTHOR_URL, CONTACT, REPO

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
D = json.load(open(f"{ROOT}/data/catalogue.json", encoding="utf-8"))
C = D["meta"]["counts"]
PROGS = D["programmes"]


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
# CAVEATS
# =============================================================================
CAV = [
 ("District boundaries move, and the change is invisible in the data",
  "Pakistan created new districts throughout the period this catalogue covers: Nankana Sahib in 2005, "
  "Chiniot in 2009, the seven ex-FATA tribal districts in 2018, and five more in Punjab alone in "
  "2022&ndash;23 (Kot Addu, Talagang, Murree, Wazirabad, Taunsa). The Bureau of Statistics reissues "
  "district codes when this happens.",
  "Harmonise to a constant boundary set before building the panel: collapse post-split children into "
  "their pre-split parent, and keep the crosswalk as a separate documented file. A silent boundary "
  "change looks exactly like a treatment effect, and reviewers will not catch it either."),
 ("Most of these programmes were targeted at districts that were already deteriorating",
  "Zewar-e-Taleem selected on low female literacy. Nashonuma selected on high stunting. The Public "
  "School Support Programme selected on low enrolment. Health facility outsourcing selected on poor "
  "performance. This is sensible policy and terrible for identification: it guarantees mean reversion, "
  "and the reversion often begins exactly at the treatment date, producing clean pre-trends.",
  "Plot the full event-study path, use honest DiD sensitivity analysis, match on baseline levels and "
  "trends, and where the targeting rule is a threshold on a measurable variable, exploit it as a "
  "discontinuity instead of assuming parallel trends."),
 ("Treatment is frequently not absorbing",
  "Contracting out of basic health units was reversed and re-awarded. The Saaf Pani programme was "
  "suspended during a corruption inquiry and relaunched. Local governments were dissolved and restored "
  "more than once. Standard staggered estimators assume once-treated-always-treated.",
  "Use an estimator that handles switching in and out, and document every reversal date explicitly "
  "rather than coding the programme as a single absorbing event."),
 ("Population composition is endogenous to several of these treatments",
  "Conflict, floods, new roads and new university campuses all move people between districts. If "
  "treatment changes who lives in the district, a district-level estimate confounds the treatment "
  "effect with a composition effect, and the bias can go either way.",
  "Test for sorting directly using the migration modules in PSLM and the census. Where sorting is "
  "present, report it as a result in its own right; where the treatment is large enough to move "
  "people, consider the receiving districts as the better-identified side of the question."),
 ("Administrative outcomes often improve because measurement improved",
  "Reported crime rises when the cost of registering a complaint falls. Teacher presence rises when "
  "monitoring digitises. Land transactions rise when the registry becomes usable. In each case part "
  "of the measured change is real and part is the measurement system changing at the same moment as "
  "the treatment.",
  "Pair every administrative outcome with an independent household-survey measure of the same "
  "construct where one exists, and treat the gap between them as informative rather than as noise."),
 ("Coverage of this catalogue is uneven by province",
  "Punjab publishes far more than the other provinces, so Punjab entries are better documented here. "
  "Balochistan is the thinnest, both in the catalogue and in the underlying survey infrastructure &mdash; "
  "several national household surveys have district-representative samples everywhere except there.",
  "Do not read the density of entries as the density of policy. Where a Balochistan entry is graded "
  "Low-Medium, that usually reflects what is published rather than what happened."),
 ("Dates reported in secondary sources disagree, routinely",
  "Programme retrospectives, agency websites and press coverage frequently differ by a year on when a "
  "phase began, and launch ceremonies are often held well before or after operational start.",
  "Every date in this catalogue carries a named source. Verify against the primary document before it "
  "enters a regression, and when sources conflict, say in the paper which one you used and why."),
 ("Expected signs here are hypotheses, not findings",
  "The direction given for each programme&ndash;outcome pair is derived from the stated mechanism. "
  "Several are deliberately marked ambiguous because theory points both ways. None of them is evidence.",
  "Treat the sign column as a prior to be tested, and pre-register it if you are going to. Where the "
  "catalogue says ambiguous, resist the temptation to pick the direction your result happens to take."),
]

cav_html = ""
for i, (h, what, do) in enumerate(CAV, 1):
    cav_html += f"""<div style="border-top:1px solid var(--rule);padding:22px 0">
<div class="grid" style="grid-template-columns:40px minmax(0,1fr);gap:20px">
  <div class="mono" style="color:var(--navy-300);font-size:15px">{i:02d}</div>
  <div>
    <h3>{h}</h3>
    <p class="small" style="max-width:56em">{what}</p>
    <p class="small" style="max-width:56em;margin:0;border-left:3px solid var(--accent);padding-left:14px">
      <strong>What to do:</strong> {do}</p>
  </div>
</div></div>"""

cav_body = crumb("Caveats") + head(
    "Guidance", "Standing caveats",
    "Eight problems that apply to this catalogue as a whole rather than to any single entry. Each "
    "programme page lists its own specific threats; these are the ones that recur everywhere.") + f"""
<div class="wrap shell">{cav_html}
  <div class="box" style="margin-top:32px">
    <h3>In short</h3>
    <p class="small" style="margin:0">The variation in this catalogue is real and largely unexploited.
    It is also, in most cases, not random. Programmes went where need was greatest or where political
    attention was, boundaries moved underneath the panel, and several treatments switched off again.
    None of that makes the designs infeasible &mdash; it makes the diagnostics load-bearing.</p>
  </div>
</div>
"""

write("caveats/index.html", page(cav_body, "Standing caveats",
      "Eight recurring threats to identification across the catalogue: boundary changes, targeting on "
      "the outcome, non-absorbing treatment, migration sorting and measurement endogeneity.",
      base="../", active=""))


# =============================================================================
# DOWNLOADS
# =============================================================================
def filesize(p):
    try:
        n = os.path.getsize(os.path.join(ROOT, p))
    except OSError:
        return ""
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0


FILES = [
 ("data/programmes.csv", "CSV", f"Programme inventory &mdash; {C['programmes']} rows, 24 columns"),
 ("data/programme_outcome_matrix.csv", "CSV", f"Programme &times; outcome matrix &mdash; {C['pairs']} rows"),
 ("data/outcomes.csv", "CSV", f"Outcome taxonomy &mdash; {C['outcomes']} rows"),
 ("data/datasets.csv", "CSV", f"Dataset catalogue &mdash; {C['datasets']} rows"),
 ("data/catalogue.json", "JSON", "Everything in one nested file, as the site itself consumes it"),
 ("data/programmes.json", "JSON", "Programme inventory with derived fields (regions, methods, quality rank)"),
 ("data/matrix.json", "JSON", "Matrix with expanded dataset names and source URLs"),
 ("data/outcomes.json", "JSON", "Outcome taxonomy"),
 ("data/datasets.json", "JSON", "Dataset catalogue"),
 ("data/meta.json", "JSON", "Version, release date and record counts"),
]

file_rows = ""
for path, fmt, desc in FILES:
    file_rows += f"""<div class="dl-file">
  <span class="fmt">{fmt}</span>
  <span class="nm"><a href="../{path}" download>{path.split('/')[-1]}</a>
    <span class="rowsub">{desc}</span></span>
  <span class="sz">{filesize(path)}</span>
</div>"""

SCHEMA = [
 ("id", "string", "Stable programme identifier, P01&ndash;P67. Cite this, not the row number."),
 ("programme", "string", "Programme or shock name as commonly used."),
 ("domain", "string", "Policy domain."),
 ("agency", "string", "Implementing agency or agencies."),
 ("scope", "string", "Geographic scope as stated by the programme."),
 ("start_year", "string", "First year of operation, including pilots."),
 ("rollout_window", "string", "Narrative description of the phasing, with dates where known."),
 ("rollout_unit", "string", "The unit that switches on &mdash; district, tehsil, facility, lot."),
 ("n_districts", "string", "Number of treated units, as narrative because it changes over phases."),
 ("staggering", "string", "The form the staggering takes."),
 ("assignment", "string", "How units were selected into each phase."),
 ("timing_source", "string", "Where district-by-date treatment data can be obtained."),
 ("timing_quality", "string", "Assessed reliability of the above, with reasoning."),
 ("quality_label", "string", "High / Medium-High / Medium / Low-Medium."),
 ("quality_rank", "integer", "3 / 2 / 1 / 0, for sorting."),
 ("identification", "string", "Candidate design and why it works here."),
 ("threats", "string", "Main threats to identification for this entry."),
 ("evidence", "string", "Published evaluations, where any exist."),
 ("regions", "list", "Normalised province and region tags."),
 ("unit_class", "string", "Normalised rollout unit."),
 ("era", "string", "Normalised start period."),
 ("methods", "list", "Designs the entry suits, derived from the identification note."),
 ("ready", "boolean", "True where quality_rank is 2 or 3."),
 ("n_outcomes", "integer", "Number of mapped outcomes in the matrix."),
]

schema_rows = "".join(
    f'<tr><td class="id">{esc(f)}</td><td class="small mono">{t}</td>'
    f'<td class="wide small">{d}</td></tr>' for f, t, d in SCHEMA)

data_body = crumb("Download") + head(
    "Data", "Downloads and schema",
    "Everything on this site is generated from these files. They are versioned, CC&nbsp;BY licensed, "
    "and will keep working if the site does not.") + f"""
<div class="wrap shell">
  <div class="grid grid--sidebar">
    <div>
      <h2>Files</h2>
      <div class="box box--paper">{file_rows}</div>

      <h2 style="margin-top:36px">Schema: programmes</h2>
      <p class="small muted">Column definitions for <code>programmes.csv</code> and
      <code>programmes.json</code>. The matrix, outcome and dataset files are documented in the
      repository README.</p>
      <div class="tablewrap" style="margin-top:14px">
        <table class="data">
          <thead><tr><th scope="col">Field</th><th scope="col">Type</th>
          <th scope="col">Meaning</th></tr></thead>
          <tbody>{schema_rows}</tbody>
        </table>
      </div>

      <h2 style="margin-top:36px">Reading the data in</h2>
      <div class="grid grid--2" style="margin-top:14px">
        <div>
          <p class="eyebrow">Stata</p>
          <pre class="cite" style="padding:14px">import delimited using ///
  "programmes.csv", ///
  varnames(1) encoding("utf-8") clear

keep if quality_rank >= 2
list id programme start_year, clean</pre>
        </div>
        <div>
          <p class="eyebrow">R</p>
          <pre class="cite" style="padding:14px">library(readr)
p &lt;- read_csv("programmes.csv")
subset(p, quality_label == "High",
       select = c(id, programme, start_year))</pre>
        </div>
      </div>

      <div class="callout" style="margin-top:28px">
        <p class="eyebrow">What is not here</p>
        <p class="small" style="margin:0">This catalogue holds metadata about programmes, not the
        district-by-date treatment files themselves. Those have to be obtained from the sources named
        on each programme page &mdash; see <a href="../timing/">finding treatment dates</a>. If you
        build one, <a href="../contribute/">contribute it</a> and it will be hosted here with
        attribution.</p>
      </div>
    </div>

    <aside class="sidebar">
      <div class="box box--paper">
        <h3>Version</h3>
        <ul class="plain small">
          <li><strong>Release</strong><br><span class="mono">{VERSION}</span></li>
          <li><strong>Date</strong><br>{RELEASED}</li>
          <li><strong>Licence</strong><br>CC BY 4.0</li>
          <li><strong>Records</strong><br><span class="mono">{C['programmes']}</span> programmes,
            <span class="mono">{C['pairs']}</span> pairs</li>
        </ul>
      </div>
      <div class="box">
        <h3>Cite the catalogue</h3>
        <div class="cite" id="cite">Hussain, S. ({RELEASED[-4:]}). {SITE}: {TAGLINE.lower()}. Version {VERSION}. {REPO}</div>
        <button class="copybtn" type="button" data-copy="#cite">Copy citation</button>
      </div>
      <div class="box">
        <h3>Changelog</h3>
        <ul class="plain small">
          <li><strong>{VERSION}</strong> &mdash; {RELEASED}<br>
            <span class="muted">First public release. {C['programmes']} programmes,
            {C['outcomes']} outcomes, {C['pairs']} pairs, {C['datasets']} datasets.</span></li>
        </ul>
      </div>
    </aside>
  </div>
</div>
"""

write("data/index.html", page(data_body, "Downloads",
      "Download the catalogue as CSV or JSON, with full column documentation and import snippets for Stata and R.",
      base="../", active="data/"))


# =============================================================================
# CONTRIBUTE
# =============================================================================
contrib_body = crumb("Contribute") + head(
    "Participation", "Contribute, claim or correct",
    "This catalogue is more useful if it is shared and corrected. Four ways to take part, in rough "
    "order of how much they help.") + f"""
<div class="wrap shell">
  <div class="grid grid--2">
    <div>
      <div class="box box--paper">
        <p class="eyebrow">Most valuable</p>
        <h3>Contribute a treatment-timing file</h3>
        <p class="small">If you have assembled a district-by-date rollout file for any entry here,
        contributing it saves the next researcher months. It will be hosted with your name on it and
        a DOI, and the programme page will link to it.</p>
        <p><a class="btn btn--accent btn--sm" href="mailto:{CONTACT}?subject=Timing%20file%20contribution">Send a timing file</a></p>
      </div>

      <div class="box" style="margin-top:16px">
        <h3>Claim an idea</h3>
        <p class="small">If you are actively working on an entry, say so and it will be marked
        <span class="pill pill--claimed">Claimed</span> with your name and expected timeline, so others
        do not duplicate the work. Claiming does not reserve anything &mdash; it is a coordination
        signal, not a property right.</p>
        <p><a class="btn btn--sm" href="mailto:{CONTACT}?subject=Claiming%20an%20entry&amp;body=Entry%20ID%3A%0AName%3A%0AAffiliation%3A%0AExpected%20timeline%3A">Claim an entry</a></p>
      </div>

      <div class="box" style="margin-top:16px">
        <h3>Correct a date or a claim</h3>
        <p class="small">Dates in secondary sources disagree routinely. If you have a primary document
        that contradicts something here, that correction is worth more than a new entry. Include the
        document or a citation.</p>
        <p><a class="btn btn--ghost btn--sm" href="mailto:{CONTACT}?subject=Correction%20to%20the%20catalogue">Submit a correction</a></p>
      </div>

      <div class="box" style="margin-top:16px">
        <h3>Suggest a programme</h3>
        <p class="small">Coverage is strongest for Punjab and thinnest for Balochistan. Suggestions
        from the under-covered provinces are especially welcome. The bar is simple: did it reach
        different places at different times, and can that be dated?</p>
        <p><a class="btn btn--ghost btn--sm" href="mailto:{CONTACT}?subject=Suggested%20programme">Suggest a programme</a></p>
      </div>
    </div>

    <div>
      <h2>What an entry needs</h2>
      <p class="small muted">Nothing here is hard to supply, but an entry without a timing source is
      not usable, so that field is the one that matters.</p>
      <ul class="plain small">
        <li><strong>Name and implementing agency</strong> &mdash; as officially used.</li>
        <li><strong>Geographic scope</strong> &mdash; national, or which provinces.</li>
        <li><strong>Rollout window</strong> &mdash; when phases began and ended, with dates.</li>
        <li><strong>Rollout unit</strong> &mdash; district, tehsil, facility, scheme lot.</li>
        <li><strong>Assignment rule</strong> &mdash; how units were picked for each phase. If there
          was a threshold on a measurable variable, say so; that is the most valuable single fact.</li>
        <li><strong>Timing source</strong> &mdash; the register, document or dataset where the
          district-by-date schedule can actually be found.</li>
        <li><strong>Known evaluations</strong> &mdash; so the catalogue does not send people to
          re-do finished work.</li>
      </ul>

      <h2 style="margin-top:36px">How contributions are handled</h2>
      <ol class="small" style="padding-left:20px">
        <li>Submissions are reviewed against the primary source named.</li>
        <li>Accepted entries go into the next versioned release, with the contributor credited on the
        entry and in the changelog.</li>
        <li>Corrections to existing entries are applied with a note recording what changed.</li>
        <li>Contributed data files are released under CC&nbsp;BY 4.0 unless you specify otherwise.</li>
      </ol>

      <div class="callout" style="margin-top:28px">
        <p class="eyebrow">On co-authorship</p>
        <p class="small" style="margin:0">Contributing to the catalogue is not a claim on anyone's
        paper, and does not create one. If you want to work together on a specific entry, that is a
        separate conversation &mdash; <a href="mailto:{CONTACT}?subject=Collaboration%20enquiry">say
        so directly</a> rather than through a contribution.</p>
      </div>
    </div>
  </div>
</div>
"""

write("contribute/index.html", page(contrib_body, "Contribute",
      "Contribute a treatment-timing file, claim an entry you are working on, correct a date, or "
      "suggest a programme for the catalogue.",
      base="../", active="contribute/"))


# =============================================================================
# ABOUT
# =============================================================================
about_body = crumb("About") + head(
    "About", "About this catalogue",
    "What it is, how it was built, what it is not, and who maintains it.") + f"""
<div class="wrap shell">
  <div class="grid grid--sidebar">
    <div class="prose">
      <h2>Why it exists</h2>
      <p>Pakistan ran an unusual number of large public programmes that reached different places at
      different times. Health insurance activated division by division across Punjab inside twelve
      months. Land records digitised tehsil by tehsil across 143 centres. Cash transfers were gated by
      the date each district's poverty census finished, and payments began in some districts before the
      census had ended in others. Districts were created, merged and renamed throughout.</p>
      <p>That is the variation causal inference needs, and most of it has never been used. The reason
      is rarely that the question is uninteresting. It is that establishing <em>when</em> each district
      was treated is a research project in itself, and there is no way to know in advance whether an
      outcome exists at the same resolution. Both facts sit in scattered agency reports, project
      documents and evaluation appendices.</p>
      <p>This catalogue collects them in one place, for {C['programmes']} programmes and natural
      experiments, with {C['pairs']} programme&ndash;outcome pairs and {C['datasets']} datasets mapped
      against them &mdash; and grades how reliable the timing data actually is, including where the
      answer is that it is not reliable at all.</p>

      <h2>How it was built</h2>
      <p>Entries were assembled from agency websites and annual reports, provincial Annual Development
      Programme scheme registers, World Bank and ADB project appraisal and implementation documents,
      third-party evaluations, and the published academic literature. Where an evaluation had already
      assembled a district rollout table &mdash; as Malik, van&nbsp;de&nbsp;Poel and van&nbsp;Doorslaer did for
      health-unit contracting across 75 districts &mdash; the catalogue points at it rather than
      duplicating it.</p>
      <p>Each entry carries the source for its timing data and an assessment of how usable that source
      is, on a four-point scale documented on the <a href="../timing/">timing page</a>. Of the
      {C['programmes']} entries, {C['high']} are graded High and {C['ready'] - C['high']} Medium-High.
      The remainder are included deliberately: either because the gap is worth knowing about, or so
      that you can rule them out quickly.</p>

      <h2>What it is not</h2>
      <p>It is not a census of Pakistani public policy. Coverage is strongest for Punjab, which
      publishes the most, and thinnest for Balochistan, which publishes the least and is also missing
      from the district-representative samples of several national surveys. The density of entries
      reflects what is documented, not what happened.</p>
      <p>It is not a repository of treatment-timing data. It tells you where that data can be found; it
      does not host it, except where contributors have supplied files.</p>
      <p>It is not evidence. The expected signs attached to each programme&ndash;outcome pair are
      hypotheses derived from the stated mechanism, several of them deliberately ambiguous. Nothing
      here has been estimated.</p>

      <h2>Reusing it</h2>
      <p>Everything is released under a Creative Commons Attribution 4.0 licence. Take the CSVs, build
      on them, fork the site. The one thing worth asking: if you correct something, send the correction
      back, so the next person inherits the fixed version rather than repeating the error.</p>
      <p><a href="../contribute/">How to contribute or correct &rarr;</a></p>
    </div>

    <aside class="sidebar">
      <div class="box box--paper">
        <h3>Maintainer</h3>
        <p class="small" style="margin-bottom:10px"><strong>{AUTHOR}</strong><br>
        <span class="muted">Applied microeconomist working on conflict, political economy and state
        capacity in South Asia.</span></p>
        <ul class="plain small">
          <li><a href="{AUTHOR_URL}">itssaqib.github.io</a></li>
          <li><a href="mailto:{CONTACT}">{CONTACT}</a></li>
        </ul>
      </div>
      <div class="box">
        <h3>Version</h3>
        <ul class="plain small">
          <li><strong>Release</strong> <span class="mono">{VERSION}</span></li>
          <li><strong>Date</strong> {RELEASED}</li>
          <li><strong>Licence</strong> CC BY 4.0</li>
        </ul>
        <p class="small" style="margin-top:12px"><a href="../data/">Downloads and changelog &rarr;</a></p>
      </div>
      <div class="box">
        <h3>Before you use an entry</h3>
        <p class="small" style="margin:0">Read the <a href="../caveats/">standing caveats</a>. The
        boundary-change warning in particular is not boilerplate &mdash; five new Punjab districts in
        2022&ndash;23 alone, plus seven ex-FATA districts in 2018.</p>
      </div>
    </aside>
  </div>
</div>
"""

write("about/index.html", page(about_body, "About",
      f"About the {SITE}: why it exists, how it was built, what it is not, and who maintains it.",
      base="../", active=""))


# =============================================================================
# 404
# =============================================================================
nf_body = f"""
<div class="wrap shell">
  <div class="pagehead" style="padding-top:48px">
    <p class="eyebrow">Error 404</p>
    <h1>That page is not here</h1>
    <p class="lede">The link may be out of date, or the entry may have been renumbered between
    releases. Programme identifiers are stable from version {VERSION} onward.</p>
  </div>
  <div class="grid grid--2">
    <div class="box">
      <h3>Try one of these</h3>
      <ul class="plain">
        <li><a href="/pakistan-evidence-catalogue/programmes/">All {C['programmes']} programmes</a></li>
        <li><a href="/pakistan-evidence-catalogue/matrix/">Programme &times; outcome matrix</a></li>
        <li><a href="/pakistan-evidence-catalogue/datasets/">Dataset catalogue</a></li>
        <li><a href="/pakistan-evidence-catalogue/data/">Downloads</a></li>
      </ul>
    </div>
    <div class="box">
      <h3>Looking for a specific entry?</h3>
      <p class="small">Programme pages are at <code>/programmes/p01.html</code> through
      <code>/programmes/p{C['programmes']}.html</code>. If a link is broken,
      <a href="mailto:{CONTACT}?subject=Broken%20link">report it</a>.</p>
    </div>
  </div>
</div>
"""

write("404.html", page(nf_body, "Page not found", "Page not found.", base="/pakistan-evidence-catalogue/", active=""))

print("caveats, data, contribute, about, 404 written")
