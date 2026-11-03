* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 02 From a rollout file to the variables the estimators need
* =============================================================================

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
