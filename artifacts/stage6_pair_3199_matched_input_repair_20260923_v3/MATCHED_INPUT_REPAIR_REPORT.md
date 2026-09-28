# PAIR3199 matched-input repair — checker revision 3

**Disposition:** `PAIR3199_MATCHED_INPUTS_REPAIRED_PRELAUNCH_NOT_AUTHORIZED`. This is offline input construction only. There is no run card, execution authorization, or new start authorization.

## Root-cause record

- **U/X omission:** the old treatment route source orders `M_flow`, delayed `R_flow`, `U_flow`, `X_flow`. SUMO logged that it ignored `U_flow` and `X_flow` because the source was not departure-sorted. Those 225 identities are absent in the old treatment raw; the control with M/U/X ordering realized them.
- **M speedFactor mismatch:** the old common `technical_passenger` vType does not explicitly fix individual `speedFactor`; existing `vehroute.xml` shows only 2/1,333 exact M matches across arms, including 1/480 M vehicles scheduled before 540 s. Same seed therefore did not bind random values to identity. The added R flow is consistent with a changed construction-time random realization, but the exact RNG instance/draw order remains unproven from existing source/logs. SUMO was not rerun. The tagged v1_26_0 `MSBaseVehicle.cpp` confirms explicit `pars->speedFactor` takes precedence over the supplied factor at vehicle construction.
- **Precision control:** v2 is superseded and retained unchanged. It used factors from two-decimal tripinfo, which can hide exact mismatches. v3 continues to bind the exact lexical values from immutable `vehroute.xml`.

## v3 construction and fail-closed checks

The existing control's M/U/X identities and precise speedFactors are materialized in both arms, with each vehicle's desired depart, route, type, departure position/lane/speed explicit. Integer schedules mirror SUMO 1.26 semantics. The materializer first compares full source route/vType attribute maps across the original control and treatment files, then both generated route files carry those identical definitions. The treatment's only extra vehicle records are R_flow.0–R_flow.191 at 5 s intervals from 540 through 1,495 s. No geometry, demand count/rate/window, classifier, thresholds, witness contract, or formal protocol was edited.

The checker compares per-vehicle records and complete route/vType definition maps, including edge lists and every XML attribute. It rejects mismatches, missing/extra definitions or vehicles, invalid schedules, missing speedFactors, unsorted files and any treatment-only ID outside the exact R set. `checker_fail_closed: true` means the checker returns a failing status and exits nonzero whenever an invariant mismatch is detected; `mismatch_detected` separately reports whether this checked pair contains such a mismatch.

## Static verification

| Check | Result |
|---|---:|
| Control M/U/X | 1,333 / 150 / 75 |
| Treatment M/U/X/R | 1,333 / 150 / 75 / 192 |
| Common IDs and complete vehicle records | 1,558 / 1,558 |
| Integer desired departures | 1,558 / 1,558 |
| Route/type and exact speedFactor | 1,558 / 1,558 |
| Route definitions including edges/attributes | 4 / 4 identical |
| vType definitions including attributes | 1 / 1 identical |
| Original control/treatment source route and vType definitions | 4 routes and 1 vType identical |
| Treatment-only vehicle IDs | exactly R_flow.0–R_flow.191 |
| Fail-closed tests, including route-edge and vType mutation | 6/6 PASS |
| SUMO / TraCI / netconvert starts | 0 / 0 / 0 |

These checks validate files, not a future run's insertion success or trajectory equivalence. The prior treatment one-start authorization is consumed and remains consumed. Any future use requires a new exact card, independent reviews and a separate user authorization.

## Provenance

Hashes are in `COMMON_DEMAND_MANIFEST.json` and `PROVENANCE_RECEIPT.json`; checker results are in `INVARIANT_CHECK_REPORT.json`. No raw output was edited. The adopted exploratory witness contract and formal protocol remain unchanged.
