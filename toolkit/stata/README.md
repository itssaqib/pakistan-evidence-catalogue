# Stata starter kit

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
