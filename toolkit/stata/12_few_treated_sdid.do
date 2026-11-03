* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 12 Few treated units: synthetic difference-in-differences
* =============================================================================

* For programmes with a handful of treated districts (Safe Cities, Daanish Schools,
* first-phase pilots). Requires a balanced panel.
use "$WORK/analysis.dta", clear

sdid y id year D, vce(placebo) reps(500) seed(20261104) method(sdid) graph
sdid y id year D, vce(placebo) reps(500) seed(20261104) method(sc)
sdid y id year D, vce(placebo) reps(500) seed(20261104) method(did)

* Report all three; a large gap between sc and did is informative in itself.
