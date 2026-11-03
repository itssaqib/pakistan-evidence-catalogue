# -*- coding: utf-8 -*-
"""Write the Stata starter kit into toolkit/stata/ (explicit, line-by-line code)."""
import os, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(HERE)
SITE = _PARENT if os.path.exists(os.path.join(_PARENT, "assets", "css", "site.css")) else os.path.join(_PARENT, "out", "pakistan-evidence-catalogue")
OUT = os.path.join(SITE, "toolkit", "stata")
os.makedirs(OUT, exist_ok=True)

HDR = """* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* {title}
* =============================================================================
"""

FILES = {}

FILES["00_master.do"] = HDR.format(title="00 Master: paths and one-time package installs") + r"""
version 16
clear all
set more off

* --- Edit these two paths -----------------------------------------------------
global PEC   "C:/path/to/pakistan-evidence-catalogue"   // the folder you downloaded
global WORK  "C:/path/to/your/project"
global DATA  "$PEC/data"
global KIT   "$PEC/toolkit/stata"

* --- One-time installs (comment out once done) -------------------------------
ssc install csdid, replace
ssc install drdid, replace
ssc install did_imputation, replace
ssc install event_plot, replace
ssc install did_multiplegt_dyn, replace
ssc install eventstudyinteract, replace
ssc install avar, replace
ssc install bacondecomp, replace
ssc install reghdfe, replace
ssc install ftools, replace
ssc install boottest, replace
ssc install sdid, replace
ssc install rdrobust, replace
ssc install rddensity, replace
ssc install lpdensity, replace
net install honestdid, from("https://raw.githubusercontent.com/mcaceresb/stata-honestdid/main") replace

* --- Run the pipeline --------------------------------------------------------
* do "$KIT/01_harmonise_districts.do"
* do "$KIT/02_build_treatment.do"
* do "$KIT/10_staggered_did.do"
"""

FILES["01_harmonise_districts.do"] = HDR.format(title="01 Map any district name onto the 126 constant-boundary units") + r"""
* The catalogue's maps use geoBoundaries 2019 district polygons (126 units).
* Districts created later are folded into the 2019 unit that contains them,
* so a panel built on pec_unit_id has constant boundaries over time.
*
* Input : the dataset in memory, with a string district-name variable
* Output: pec_unit, pec_unit_id, province, relation; unmatched names listed
*
* Set the name of your district variable here:
local namevar "district"

* Build the merge key exactly as the catalogue does: lower case, "&" to "and",
* drop the words district / agency / tribal / frontier region, keep a-z and 0-9.
generate key = lower(`namevar')
replace key = subinstr(key, "&", "and", .)
replace key = ustrregexra(key, "\b(district|agency|tribal|frontier region)\b", "")
replace key = ustrregexra(key, "[^a-z0-9]", "")

merge m:1 key using "$DATA/districts/district_crosswalk.dta", ///
    keepusing(pec_unit pec_unit_id province relation) keep(master match)

* Anything left unmatched needs a row in district_crosswalk.csv (and a pull request!)
count if _merge == 1
display as text r(N) " observations have a district name not in the crosswalk"
tab `namevar' if _merge == 1, missing sort

drop _merge key

* Typical next step: collapse to constant boundaries, e.g.
* collapse (mean) y [aw = popweight], by(pec_unit_id year)
"""

FILES["02_build_treatment.do"] = HDR.format(title="02 From a rollout file to the variables the estimators need") + r"""
* rollout.csv: one row per district with columns
*     pec_unit_id, first_treated_year     (blank = never treated)
* panel.dta  : district-year panel with pec_unit_id, year and outcome y

import delimited using "$WORK/rollout.csv", varnames(1) clear stringcols(1)
tempfile roll
save `roll'

use "$WORK/panel.dta", clear
merge m:1 pec_unit_id using `roll', keep(master match) nogenerate

generate gvar = first_treated_year
replace  gvar = 0 if missing(gvar)                // csdid: 0 means never treated
generate Ei   = first_treated_year                // did_imputation: missing means never
generate rel_time = year - first_treated_year
generate D = (year >= first_treated_year) & !missing(first_treated_year)
generate never_treated = missing(first_treated_year)

egen id = group(pec_unit_id)
xtset id year

* Balance check: estimators below assume a balanced district-year panel
xtdescribe

save "$WORK/analysis.dta", replace
"""

FILES["10_staggered_did.do"] = HDR.format(title="10 Staggered adoption: diagnostics, three robust estimators, sensitivity") + r"""
use "$WORK/analysis.dta", clear
xtset id year

* --- 1. Diagnostic: weights on already-treated controls in two-way FE -------
bacondecomp y D, ddetail

* --- 2. Callaway-Sant'Anna (not-yet-treated comparison, doubly robust) -------
csdid y, ivar(id) time(year) gvar(gvar) notyet method(dripw)
estat simple
estat group
estat event, window(-5 5) estore(cs_event)
csdid_plot, title("Callaway-Sant'Anna")

* --- 3. Borusyak-Jaravel-Spiess imputation ------------------------------------
did_imputation y id year Ei, horizons(0/5) pretrends(5) autosample cluster(id)
event_plot, default_look graph_opt(title("Imputation estimator"))

* --- 4. Sun-Abraham interaction-weighted event study (lead 1 omitted) ---------
generate lead5 = rel_time == -5
generate lead4 = rel_time == -4
generate lead3 = rel_time == -3
generate lead2 = rel_time == -2
generate lag0  = rel_time == 0
generate lag1  = rel_time == 1
generate lag2  = rel_time == 2
generate lag3  = rel_time == 3
generate lag4  = rel_time == 4
generate lag5  = rel_time == 5
eventstudyinteract y lead5 lead4 lead3 lead2 lag0 lag1 lag2 lag3 lag4 lag5, ///
    cohort(first_treated_year) control_cohort(never_treated) ///
    absorb(i.id i.year) vce(cluster id)

* --- 5. Rambachan-Roth sensitivity on the Callaway-Sant'Anna event study -----
estimates restore cs_event
matrix list e(b)
* With window(-5 5) the coefficient vector is Pre_avg Post_avg Tm5..Tm1 Tp0..Tp5,
* so the pre-period estimates are positions 3-7 and the post-period ones 8-13.
honestdid, pre(3/7) post(8/13) mvec(0(0.5)2) coefplot

* --- 6. Fewer than ~20 treated districts: wild cluster bootstrap --------------
reghdfe y D, absorb(id year) vce(cluster id)
boottest D, cluster(id) reps(9999) seed(20261104) nograph
"""

FILES["11_rd_threshold.do"] = HDR.format(title="11 Regression discontinuity at an eligibility threshold") + r"""
* Use for programmes with a rule on a running variable:
*   BISP proxy-means score (P02), PEF Quality Assurance Test (P23),
*   Punjab Female School Stipend 1998 literacy threshold (P08), Zewar-e-Taleem (P07).
* The data here are unit-level (household, school, district), not the panel.

use "$WORK/rd_sample.dta", clear
local cutoff = 16.17        // example: BISP PMT cut-off used in the first poverty census

* Sharp RD (eligibility = treatment)
rdrobust y score, c(`cutoff') kernel(triangular) bwselect(mserd) vce(cluster cluster_id)
rdplot   y score, c(`cutoff') binselect(es) graph_options(title("Outcome at the threshold"))

* Fuzzy RD (eligibility shifts take-up)
rdrobust y score, c(`cutoff') fuzzy(treated) kernel(triangular) bwselect(mserd) vce(cluster cluster_id)

* Manipulation of the running variable
rddensity score, c(`cutoff')

* With district-level running variables there are few units near the cut-off:
* prefer local-randomisation inference (rdlocrand package, rdrandinf command).
"""

FILES["12_few_treated_sdid.do"] = HDR.format(title="12 Few treated units: synthetic difference-in-differences") + r"""
* For programmes with a handful of treated districts (Safe Cities, Daanish Schools,
* first-phase pilots). Requires a balanced panel.
use "$WORK/analysis.dta", clear

sdid y id year D, vce(placebo) reps(500) seed(20261104) method(sdid) graph
sdid y id year D, vce(placebo) reps(500) seed(20261104) method(sc)
sdid y id year D, vce(placebo) reps(500) seed(20261104) method(did)

* Report all three; a large gap between sc and did is informative in itself.
"""

FILES["13_switching_treatment.do"] = HDR.format(title="13 Treatment that switches off again") + r"""
* Contracting reversed (P16), programme suspended (P20), local governments
* dissolved and restored (P41). Standard staggered estimators assume treatment
* is absorbing; this one does not.
use "$WORK/analysis.dta", clear

did_multiplegt_dyn y id year D, effects(5) placebo(3) cluster(id)

* Document every switch-off date in the rollout file: one row per district-spell
* (pec_unit_id, start_year, end_year) and expand to D_it before running.
"""

FILES["20_power_mde.do"] = HDR.format(title="20 Minimum detectable effect for a district panel DiD") + r"""
* Burlig, Preonas & Woerman (2020, JDE) variance for difference-in-differences
* with serially correlated errors, here with AR(1) residuals in closed form.
* Result is in residual standard-deviation units of the outcome.

scalar J     = 126      // districts (constant 2019 boundaries; Punjab alone = 34)
scalar P     = 0.5      // share of districts treated
scalar m     = 3        // pre-treatment periods (survey waves or years)
scalar r     = 3        // post-treatment periods
scalar phi   = 0.4      // AR(1) serial correlation of the residual
scalar alpha = 0.05
scalar power = 0.80

scalar S1m  = cond(m < 2, 0, phi*((m-1) - m*phi + phi^m)/(1-phi)^2)
scalar S1r  = cond(r < 2, 0, phi*((r-1) - r*phi + phi^r)/(1-phi)^2)
scalar psiB = cond(m < 2, 0, 2*S1m/(m*(m-1)))          // mean covariance within pre
scalar psiA = cond(r < 2, 0, 2*S1r/(r*(r-1)))          // mean covariance within post
scalar psiX = ((1-phi^m)/(1-phi)) * (phi*(1-phi^r)/(1-phi)) / (m*r)   // pre-post
scalar V    = (1/(P*(1-P)*J)) * ((m+r)/(m*r) + (m-1)/m*psiB + (r-1)/r*psiA - 2*psiX)
scalar MDE  = (invttail(J-2, alpha/2) + invttail(J-2, 1-power)) * sqrt(V)

display as text "Minimum detectable effect: " as result %5.3f MDE " residual SD"

* Check: with phi = 0 and m = r = 1 this reduces to the two-period formula
* MDE = (t_a + t_b) * sqrt(2 / (P*(1-P)*J)).
"""

README = """# Stata starter kit

Plain, line-by-line do-files that run in order. Edit the two paths in `00_master.do` first.

| File | What it does |
|------|--------------|
| `00_master.do` | Paths and one-time package installs |
| `01_harmonise_districts.do` | Maps any district name onto the 126 constant-boundary units used by the catalogue's maps |
| `02_build_treatment.do` | Turns a rollout file (`pec_unit_id, first_treated_year`) into `gvar`, `Ei`, `rel_time`, `D` |
| `10_staggered_did.do` | Goodman-Bacon diagnostic, Callaway-Sant'Anna, Borusyak-Jaravel-Spiess, Sun-Abraham, honest DiD, wild bootstrap |
| `11_rd_threshold.do` | Sharp and fuzzy RD at an eligibility threshold, with a density test |
| `12_few_treated_sdid.do` | Synthetic DiD for programmes with a handful of treated districts |
| `13_switching_treatment.do` | de Chaisemartin-D'Haultfoeuille estimator when treatment switches off |
| `20_power_mde.do` | Minimum detectable effect for a district panel DiD (Burlig, Preonas & Woerman 2020) |

Each programme page on the site also generates a starter do-file pre-filled with that
programme's documented rollout districts, suggested outcomes and power defaults.

These files have been written carefully but not run against your data. Check package help
files (`help csdid`, `help did_imputation`) when versions change.
"""

for name, txt in FILES.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\r\n").write(txt.lstrip("\n"))
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(README)

with zipfile.ZipFile(os.path.join(SITE, "toolkit", "pec-stata-kit.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for name in list(FILES) + ["README.md"]:
        z.write(os.path.join(OUT, name), arcname="pec-stata-kit/" + name)
    z.write(os.path.join(SITE, "data", "districts", "district_crosswalk.dta"), arcname="pec-stata-kit/district_crosswalk.dta")

print("stata files:", len(FILES), "+ README + zip")
