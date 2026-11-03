* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 01 Map any district name onto the 126 constant-boundary units
* =============================================================================

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
