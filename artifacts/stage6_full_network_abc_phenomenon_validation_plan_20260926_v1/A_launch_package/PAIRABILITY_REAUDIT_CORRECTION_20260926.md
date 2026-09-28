# FULL_NETWORK_R0_A_PAIRABILITY_REAUDIT_CORRECTION

**Status:** Independent read-only correction of the historical prelaunch audit. Original audit, card, raw, and post-run records remain preserved.  
**Corrected prelaunch classification for the exact A input versus existing R0:** `NOT_PAIRABLE`.  
**Post-run A disposition:** `A_NOT_EVALUABLE` remains valid.  
**Independent scientific review:** Blocker 1, Major 1, required Minor 0; High confidence in both dispositions.

## Error in the original static audit

The R0 source demand requests `departLane="best"` and `departSpeed="max"` for M/U/X, and `departPos="last"` for U/X. The A materialized demand instead supplies numeric per-vehicle departure lane, position, and speed copied from R0 `vehroute.xml`. Those numeric fields are **realized outputs of the R0 simulation**, not the R0 requested departure rules. Their identity-wise equality to R0 output cannot establish equal exogenous inputs. This difference was visible before A launch and should have failed the plan's static input-equivalence gate. The earlier `PAIRABLE_WITH_EXPLICIT_LIMITATION` and `PASS_WITH_EXPLICIT_LIMITATIONS` preparation judgments overstated pairability; under the audit's original A/B/C choices the correct static disposition is `NOT_PAIRABLE`.

The 3/3 A draft preflight regressions checked authorization and stale route/output paths. They did not test the semantic equivalence of `best/max/last` flow rules and fixed numeric vehicle inputs. The runner, runtime, configuration hashes, output manifest, and one-start engineering integrity findings remain valid.

## Raw-observed consequences and limits

- A explicitly requests `departSpeed=14.0817` m/s for `U_flow.1`. At t=10 s SUMO rejected that departure because of a slow lane ahead; R0 inserted the same identity at t=10 s under its symbolic rule. This is a concrete, log-supported proximate mechanism for at least one U insertion failure.
- A lost 57/150 U insertions overall, including 19 before R activation at 540 s. Pre-540 actual departures were R0/A M 502/502, U 54/35, X 27/27. Of the common pre-540 identities, actual departure time differed for 114/502 M and 12/27 X.
- M FCD first differs at 12 s, U at 13 s and X at 108 s. Exact same-time FCD tuple agreement of M 497/34,470, U 80/2,008 and X 468/1,394 is a strict diagnostic, not a physical effect size. A coarser difference check (different lane, or position difference >10 m, or speed difference >2 m/s) still flags M 28.5%, U 18.5%, X 11.8% of common rows. The pre-R mismatch therefore does not rest on decimal exactness.
- `M_flow.502` had desired departure 539.148 s and actual departure 540.00 s in both arms. It correctly remains outside `[0,540)` actual departure and FCD counts.

The fixed numeric departure policy explains the demonstrated `U_flow.1` insertion failure and is a plausible contributor to other pre-R differences. The complete mechanism behind all M/X trajectory divergence and any exact RNG-consumption path is **unresolved**. No post-540 phenomenon, R merge-exposure total, P/S/L or 0.85 outcome was examined in this re-audit.

## Result and record handling

The A raw cannot be compared causally with the existing R0 under the adopted pre-R gate. `A_NOT_EVALUABLE` and stopping before B/C remain correct; the A raw provides neither positive nor negative evidence for the full-network A phenomenon. R0's historical `CONTROL_NOT_EVALUABLE` remains unchanged. No rerun, new run card, scientific-input change, classifier change, or formal-protocol change is authorized by this correction.

Reviewed sources: R0 `control_input/demand_control.rou.xml` and R0 `vehroute.xml`; A `data_binding/demand_A_materialized.rou.xml`, A `sumo_error.log`, R0/A tripinfo and FCD, the raw-bound pre-R data report, and the A execution/output receipts. The re-audit started SUMO/Guardian/TraCI/netconvert 0/0/0/0.
