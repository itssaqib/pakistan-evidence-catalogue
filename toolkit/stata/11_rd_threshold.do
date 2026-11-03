* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 11 Regression discontinuity at an eligibility threshold
* =============================================================================

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
