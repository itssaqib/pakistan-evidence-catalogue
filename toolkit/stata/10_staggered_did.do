* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 10 Staggered adoption: diagnostics, three robust estimators, sensitivity
* =============================================================================

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
