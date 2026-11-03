* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 00 Master: paths and one-time package installs
* =============================================================================

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
