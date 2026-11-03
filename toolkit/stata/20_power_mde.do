* =============================================================================
* Pakistan Evidence Catalogue - Stata starter kit, v2.0.0
* 20 Minimum detectable effect for a district panel DiD
* =============================================================================

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
