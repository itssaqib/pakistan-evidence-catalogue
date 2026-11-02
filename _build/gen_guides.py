# -*- coding: utf-8 -*-
"""Editorial pages: methods, timing, caveats, data, contribute, about, 404."""
import json, os
from layout import page, esc, SITE, TAGLINE, VERSION, RELEASED, AUTHOR, AUTHOR_URL, CONTACT, REPO

ROOT = "/home/claude/site/pakistan-evidence-catalogue"
D = json.load(open(f"{ROOT}/data/catalogue.json", encoding="utf-8"))
C = D["meta"]["counts"]


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
# METHODS
# =============================================================================
NOTES = [
 ("Do not use two-way fixed effects on its own",
  "With variation in treatment timing and any heterogeneity in effects across cohorts, the TWFE "
  "coefficient is a weighted average of 2&times;2 comparisons in which already-treated units serve "
  "as controls for later-treated units, and some of those weights are negative. Report the "
  "Goodman-Bacon decomposition to show how much of the estimate comes from that forbidden "
  "comparison, then estimate with Callaway&ndash;Sant'Anna, Sun&ndash;Abraham, "
  "de&nbsp;Chaisemartin&ndash;D'Haultf&oelig;uille, or Borusyak&ndash;Jaravel&ndash;Spiess. Show "
  "that they agree; where they do not, say why."),
 ("Choose the comparison group deliberately",
  "Never-treated and not-yet-treated districts give different estimands. Most large Pakistani "
  "programmes eventually reach every district, so the never-treated group is often empty or "
  "unusual &mdash; typically Balochistan or ex-FATA, which differ on everything. Prefer "
  "not-yet-treated comparisons, and say so explicitly rather than letting the software choose."),
 ("Pre-trends are necessary but not sufficient",
  "Many programmes here were deliberately targeted at districts doing badly: low literacy, high "
  "stunting, low enrolment. That guarantees mean reversion, which can look like a treatment effect "
  "and can also produce clean-looking pre-trends when the reversion begins exactly at treatment. "
  "Plot the full event-study path, run the Rambachan&ndash;Roth honest DiD sensitivity analysis, "
  "and consider matching on baseline levels and trends before estimating."),
 ("Cluster and infer carefully",
  "Pakistan has roughly 130&ndash;160 districts depending on the year and definition &mdash; enough "
  "for district-clustered standard errors in most cases. But several entries here have fewer than "
  "20 treated districts (Nashonuma phase 1, Safe Cities, Daanish Schools). For those, use wild "
  "cluster bootstrap or randomisation inference, and report the treated-cluster count prominently "
  "rather than in a footnote."),
 ("Get the boundaries right before anything else",
  "Harmonise every district to a constant-boundary definition, usually the 1998 or 2017 census set, "
  "and keep the crosswalk as a separate documented file. Ex-FATA needs its own decision: drop it, or "
  "treat the seven tribal districts as entering the panel in 2018. Whichever you choose, do it once "
  "and state it. A silent boundary change looks exactly like a treatment effect."),
 ("Watch for migration sorting",
  "District-level estimates assume the population is fixed. Conflict, floods, roads and university "
  "openings all move people. If treatment changes who lives in the district, the estimate confounds "
  "a treatment effect with a composition effect. Test it directly using the PSLM and census "
  "migration modules, and where sorting is present, report it as a finding rather than a caveat."),
 ("Treatment is often not absorbing",
  "Contracting out of basic health units was reversed and re-awarded. Saaf Pani was suspended "
  "mid-programme. Local governments were dissolved and restored. Standard staggered estimators "
  "assume an absorbing treatment. Where it is not, use the de&nbsp;Chaisemartin&ndash;D'Haultf&oelig;uille "
  "estimator, which handles switching in and out, and document every reversal date."),
 ("Distinguish the policy from its intensity",
  "Several entries are better modelled as a continuous dose &mdash; lady health worker coverage "
  "share, training slots per capita, broadband coverage share, flood inundation share &mdash; than "
  "as a binary switch. A binary indicator on a continuous treatment throws away most of the "
  "variation and usually attenuates the estimate."),
 ("Combine designs where the assignment rule allows it",
  "Several programmes have a rule-based eligibility threshold inside the district: the BISP proxy "
  "means test cut-off, the Punjab Education Foundation's Quality Assurance Test score, the Female "
  "School Stipend's 1998 literacy threshold, the NCOC's positivity thresholds. A within-district "
  "regression discontinuity alongside the across-district difference-in-differences tests the same "
  "hypothesis under different assumptions. Agreement between the two is far more persuasive than "
  "either alone."),
 ("Prefer sub-district treatment units when they exist",
  "Land records digitisation operated at tehsil level across 143 centres; health facility "
  "outsourcing and school handovers at facility and school level; filtration plants at plant level; "
  "broadband subsidies at project-lot level. Using the finer unit lets you include district "
  "&times; year fixed effects, which absorbs the district-level political and budgetary confounds a "
  "pure district design cannot. This is usually the single largest available improvement in "
  "credibility."),
 ("Frequency matters more than people expect",
  "Monthly facility data, quarterly district microfinance penetration, daily mandi prices, monthly "
  "nightlights and continuous citizen-feedback call records give far more power than the biennial "
  "household surveys, and let you separate anticipation from response. Where a high-frequency "
  "administrative outcome exists, make it the primary outcome and use the survey as corroboration."),
 ("Adjust for multiple hypotheses",
  "This catalogue lists many outcomes per programme by design. If you run all of them, adjust: "
  "pre-specify a small set of primary outcomes, group the rest into indices (Anderson sharpened "
  "q-values or Romano&ndash;Wolf stepdown), and report both adjusted and unadjusted p-values."),
]

PKGS = [
 ("csdid", "drdid", "Callaway&ndash;Sant'Anna group-time average treatment effects with doubly robust estimation.", "ssc install csdid, replace"),
 ("did_imputation", "", "Borusyak&ndash;Jaravel&ndash;Spiess imputation estimator &mdash; efficient under homogeneous trends.", "ssc install did_imputation, replace"),
 ("did_multiplegt_dyn", "", "de&nbsp;Chaisemartin&ndash;D'Haultf&oelig;uille &mdash; the one to use when treatment switches off again.", "ssc install did_multiplegt_dyn, replace"),
 ("eventstudyinteract", "", "Sun&ndash;Abraham interaction-weighted event study.", "ssc install eventstudyinteract, replace"),
 ("bacondecomp", "", "Goodman-Bacon decomposition. A diagnostic to report, never your headline estimate.", "ssc install bacondecomp, replace"),
 ("honestdid", "", "Rambachan&ndash;Roth sensitivity analysis for parallel trends.", "ssc install honestdid, replace"),
 ("reghdfe", "ppmlhdfe", "High-dimensional fixed effects; ppmlhdfe for count outcomes such as attacks or transactions.", "ssc install reghdfe ppmlhdfe, replace"),
 ("boottest", "", "Wild cluster bootstrap &mdash; essential when few clusters are treated.", "ssc install boottest, replace"),
 ("sdid", "synth_runner", "Synthetic difference-in-differences and synthetic control for the small-N treated cases.", "ssc install sdid synth_runner, replace"),
 ("rdrobust", "", "For the within-district discontinuity designs (PMT score, QAT score, literacy threshold).", "ssc install rdrobust, replace"),
]

notes_html = ""
for i, (h, b) in enumerate(NOTES, 1):
    notes_html += f"""<div style="border-top:1px solid var(--rule);padding:20px 0">
<div class="grid" style="grid-template-columns:40px minmax(0,1fr);gap:20px">
  <div class="mono" style="color:var(--navy-300);font-size:15px">{i:02d}</div>
  <div><h3>{h}</h3><p class="small" style="margin:0;max-width:56em">{b}</p></div>
</div></div>"""

pkg_rows = ""
for a, b, desc, cmd in PKGS:
    names = f'<code>{a}</code>' + (f' &middot; <code>{b}</code>' if b else '')
    pkg_rows += f"""<tr><td style="white-space:nowrap">{names}</td>
<td class="wide small">{desc}</td>
<td class="small mono" style="white-space:nowrap">{esc(cmd)}</td></tr>"""

methods_body = crumb("Methods") + head(
    "Guidance", "Identification playbook",
    "Twelve things worth settling before estimating anything with the variation in this catalogue. "
    "None of it is novel; all of it is routinely skipped.") + f"""
<div class="wrap shell">
  <div class="prose" style="margin-bottom:8px">
    <p>Staggered rollout is not a free identification strategy. In this setting it comes with three
    recurring problems &mdash; programmes targeted at districts that were already deteriorating,
    administrative boundaries that move, and treatments that switch off again &mdash; and each one
    produces a result that looks clean and is wrong.</p>
  </div>
  {notes_html}
</div>

<section class="section section--tint" id="estimators">
  <div class="wrap shell">
    <p class="eyebrow">Toolkit</p>
    <h2>Stata packages worth having installed</h2>
    <p class="small muted" style="max-width:52em">Equivalents exist in R
    (<code>did</code>, <code>didimputation</code>, <code>fixest::sunab</code>,
    <code>HonestDiD</code>, <code>synthdid</code>).</p>
    <div class="tablewrap" style="margin-top:20px">
      <table class="data">
        <thead><tr><th scope="col">Package</th><th scope="col">What it does</th>
        <th scope="col">Install</th></tr></thead>
        <tbody>{pkg_rows}</tbody>
      </table>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap shell">
    <div class="grid grid--2">
      <div>
        <h2>A minimal starting specification</h2>
        <p class="small muted">Replace the placeholders and run the diagnostics before the headline
        regression, not after.</p>
        <pre class="cite" style="padding:16px;overflow-x:auto">* 1. Build on constant boundaries first
use district_panel.dta, clear
xtset district_1998 year

* 2. Define cohort = first year treated (missing = never treated)
bysort district_1998: egen gvar = min(cond(treat==1, year, .))
recode gvar (.=0)

* 3. Diagnostic: how much comes from the forbidden comparison?
xtdidregress (y) (treat), group(district_1998) time(year)
bacondecomp y treat, ddetail

* 4. Estimate properly
csdid y, ivar(district_1998) time(year) gvar(gvar) ///
      method(dripw) notyet
estat event, window(-5 5)
csdid_plot

* 5. Sensitivity to violations of parallel trends
honestdid, pre(1/5) post(6/11) mvec(0(0.25)1) coefplot</pre>
      </div>
      <div>
        <h2>Reporting checklist</h2>
        <ul class="plain small">
          <li>State the boundary definition and the year it is fixed to.</li>
          <li>Report the number of treated clusters, not just the number of observations.</li>
          <li>Name the comparison group: never-treated, not-yet-treated, or both.</li>
          <li>Show the Goodman-Bacon decomposition alongside the modern estimator.</li>
          <li>Plot the full event-study path, including the leads you did not like.</li>
          <li>Say where the treatment date came from, and how confident you are in it.</li>
          <li>Test for migration sorting wherever the treatment could move people.</li>
          <li>Document every treatment reversal; do not quietly treat it as absorbing.</li>
          <li>Pre-specify primary outcomes; adjust the rest for multiple testing.</li>
        </ul>
        <div class="callout" style="margin-top:24px">
          <p class="eyebrow">Also read</p>
          <p class="small" style="margin:0"><a href="../caveats/">Standing caveats</a> for the
          setting-specific problems, and <a href="../timing/">finding treatment dates</a> for how to
          obtain the variation in the first place.</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""

write("methods/index.html", page(methods_body, "Methods",
      "An identification playbook for staggered district-level designs in Pakistan: estimator choice, "
      "comparison groups, boundary harmonisation, clustering and reporting.",
      base="../", active="methods/"))


# =============================================================================
# TIMING SOURCES
# =============================================================================
TIMING = [
 ("Provincial gazette notifications",
  "The legally authoritative record of when a district was created, when a law was extended, when a "
  "facility was notified. Punjab, Sindh, KP and Balochistan each publish a gazette; back issues are "
  "held by provincial law departments and the Punjab series is partly digitised.",
  "punjablaws.gov.pk", "https://punjablaws.gov.pk",
  "Slow but definitive. Use it to settle disagreements between secondary sources, not as your first stop."),
 ("Annual Development Programme scheme registers",
  "Every publicly funded scheme &mdash; a rescue station, a road package, a filtration plant, a "
  "hospital upgrade &mdash; appears as a line item with a district, an approval date and a completion "
  "status. This is the most under-used treatment-timing source in Pakistan.",
  "pnd.punjab.gov.pk", "https://pnd.punjab.gov.pk",
  "Published annually as PDFs. Scraping ten years of ADP books yields a district–scheme–date panel for dozens of programmes at once."),
 ("PC-1 approval and PC-4 completion documents",
  "The PC-1 states the intended district phasing; the PC-4 records what was actually completed and "
  "when. Held by the Planning Commission and provincial P&amp;D departments.",
  "pc.gov.pk", "https://www.pc.gov.pk",
  "Request through the department. The PC-4 is the one that matters, because plans slip."),
 ("Right to Information requests",
  "KP (2013), Punjab (2013), Sindh (2016) and Balochistan (2021) all have RTI statutes with statutory "
  "response deadlines. A request naming the exact register you want &mdash; for example, the date of "
  "operationalisation of each Arazi Record Centre &mdash; is often the fastest route to a clean "
  "treatment-timing file.",
  "infocom.punjab.gov.pk", "https://infocom.punjab.gov.pk",
  "Ask for a specific existing record, not for analysis. Requests that ask an official to compile something new are usually refused."),
 ("Programme management information systems",
  "BISP/NSER, Sehat Sahulat, the Punjab Land Records Authority, PITB, the Punjab Education Foundation, "
  "PSDF, and the provincial EMIS and DHIS systems all hold unit-level records with dates. Access runs "
  "through a research agreement or data-sharing MoU, not a public download.",
  "See the dataset catalogue", "../datasets/",
  "A World Bank, J-PAL or university affiliation materially improves the odds. Budget three to six months."),
 ("World Bank and ADB project documents",
  "Project Appraisal Documents, numbered Implementation Status Reports and Implementation Completion "
  "Reports record the actual district phasing of donor-financed programmes, often in an annex.",
  "documents.worldbank.org", "https://documents.worldbank.org",
  "The ISR sequence is especially useful: successive reports show the rollout progressing, which effectively date-stamps it."),
 ("Third-party and process evaluations",
  "Evaluation series and published papers frequently contain the district rollout table as an "
  "appendix. Malik, van de Poel &amp; van Doorslaer (2017) is the clearest example: they assembled "
  "the health-unit contracting rollout dates across 75 districts.",
  "opml.co.uk", "https://www.opml.co.uk",
  "Always check the replication package before assembling a rollout file from scratch."),
 ("Press archives",
  "Dawn, The News, Express Tribune and Business Recorder report launch ceremonies with dates and "
  "district lists. Some programme phases are documented almost exclusively this way.",
  "dawn.com/archive", "https://www.dawn.com/archive",
  "Useful for triangulation, unreliable alone &mdash; a launch ceremony is not an operational start."),
 ("Satellite and crowd-sourced verification",
  "Where administrative dates are unavailable or untrustworthy, nightlights, OpenStreetMap edit "
  "history and mobile coverage polygons can date the arrival of infrastructure independently.",
  "eogdata.mines.edu", "https://eogdata.mines.edu",
  "Best used to validate an administrative date rather than to replace it."),
]

trows = ""
for name, what, where_label, where_url, note in TIMING:
    trows += f"""<tr>
  <td class="wide"><strong>{name}</strong></td>
  <td class="wide small">{what}</td>
  <td class="small" style="white-space:nowrap"><a href="{esc(where_url)}" rel="noopener">{where_label}</a></td>
  <td class="wide small muted">{note}</td>
</tr>"""

timing_body = crumb("Treatment timing") + head(
    "Guidance", "Finding treatment dates",
    "The binding constraint on most of these ideas is not the question, it is knowing which district "
    "was treated when. Nine routes, roughly in order of reliability, with what each actually yields.") + f"""
<div class="wrap shell">
  <div class="callout">
    <p class="eyebrow">The practical order</p>
    <p class="small" style="margin:0">Start with the published evaluation or World Bank ISR sequence
    &mdash; someone may already have built the file. Then ADP scheme registers, which are public and
    under-used. Then an RTI request naming a specific register. Treat press archives as triangulation
    only, and verify everything against a primary document before it goes into a regression.</p>
  </div>

  <div class="tablewrap" style="margin-top:24px">
    <table class="data">
      <caption>Routes to district-by-date treatment data</caption>
      <thead><tr>
        <th scope="col">Source</th><th scope="col">What it gives you</th>
        <th scope="col">Where</th><th scope="col">Practical note</th>
      </tr></thead>
      <tbody>{trows}</tbody>
    </table>
  </div>
</div>

<section class="section">
  <div class="wrap shell">
    <div class="grid grid--2">
      <div>
        <h2>Drafting an RTI request that works</h2>
        <p class="small">The commonest reason a request fails is that it asks an official to produce
        analysis rather than hand over a record that already exists. Name the register, the custodian
        and the fields.</p>
        <pre class="cite" style="padding:16px;overflow-x:auto;white-space:pre-wrap">To: Public Information Officer, [Department]
Under Section 10, Punjab Transparency and
Right to Information Act 2013

I request a copy of the following existing record:

1. The register or database recording the date on
   which each [facility / centre / scheme] under
   [programme name] became operational, listing for
   each entry: district, tehsil, name of the unit,
   and date of operationalisation.

2. Covering the period [start] to [end].

I am content to receive this in any electronic
format in which it is already held, including a
spreadsheet export. I do not require any new
compilation or analysis.</pre>
      </div>
      <div>
        <h2>How this catalogue grades timing data</h2>
        <ul class="plain small">
          <li><strong>High</strong> &mdash; dates are published or exist in a named register that has
          already been assembled by someone; verification is a matter of hours.</li>
          <li><strong>Medium-High</strong> &mdash; dates exist in administrative records and are
          obtainable with a request or a document search, typically weeks.</li>
          <li><strong>Medium</strong> &mdash; dates exist but are scattered across sources that
          disagree; expect to reconcile and document judgement calls.</li>
          <li><strong>Low-Medium</strong> &mdash; no reliable district-level dating known; would
          require primary data collection or a satellite-based proxy.</li>
        </ul>
        <p class="small" style="margin-top:16px">
          <a href="../programmes/?quality_label=High">Browse the {C['high']} High entries &rarr;</a>
        </p>
        <div class="box" style="margin-top:20px">
          <h3>Have you built one of these files?</h3>
          <p class="small">If you have assembled a district-by-date rollout file, contributing it here
          saves the next person the same months of work &mdash; with full attribution.</p>
          <p><a class="btn btn--accent btn--sm" href="../contribute/">Contribute a timing file</a></p>
        </div>
      </div>
    </div>
  </div>
</section>
"""

write("timing/index.html", page(timing_body, "Finding treatment dates",
      "Nine routes to district-by-date treatment data in Pakistan: gazettes, ADP registers, PC-4 "
      "reports, RTI requests, programme MIS, donor documents and satellite verification.",
      base="../", active=""))

print("methods + timing written")
