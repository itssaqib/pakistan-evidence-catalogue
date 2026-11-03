* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 13 Treatment that switches off again
* =============================================================================

* Contracting reversed (P16), programme suspended (P20), local governments
* dissolved and restored (P41). Standard staggered estimators assume treatment
* is absorbing; this one does not.
use "$WORK/analysis.dta", clear

did_multiplegt_dyn y id year D, effects(5) placebo(3) cluster(id)

* Document every switch-off date in the rollout file: one row per district-spell
* (pec_unit_id, start_year, end_year) and expand to D_it before running.
