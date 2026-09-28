# PAIR3199 matched-input repair — checker revision 4

**Disposition:** `PAIR3199_MATCHED_INPUTS_REPAIRED_PRELAUNCH_NOT_AUTHORIZED`. This is offline common-input construction only. It creates no exact run card and grants no execution authorization.

## Checker repair

v3 is preserved unchanged and superseded by v4 after independent engineering review identified a fail-closed bypass: extra top-level `<flow>` and nested vehicle `<param>` elements could pass its pair comparison. v4 rejects unsupported top-level nodes and every nested element; it also rejects comments/processing instructions, DTD/entity declarations, unknown or missing root/node attributes, mixed text, duplicate definitions and duplicate vehicle IDs. The accepted XML shape is strictly `routes` containing only `vType`, `route`, and `vehicle`, with the exact attribute sets generated for this pair.

The checker compares complete route and vType definition maps, with all attributes. Its policy field `checker_fail_closed: true` means unsupported XML or any invariant mismatch raises an error or yields `status=FAIL` (the CLI exits nonzero); `mismatch_detected` describes only the pair that was checked.

## Construction and preserved findings

The materializer rebuilt the v4 route files from existing immutable source files. It verifies original control/treatment route and vType definitions match before output. Shared M/U/X identities carry identical explicit desired departures, routes, types, high-precision speedFactors, and original departure position/lane/speed attributes. Integer-millisecond schedules mirror SUMO 1.26. Treatment contains exactly the additional R192 vehicles at 5 s spacing from 540 to 1,495 s. The route and vType definition maps are identical across both arms.

Static root causes remain: U/X omission followed treatment source order M,R,U,X and SUMO's logged ignored-flow warnings; M speedFactor mismatch followed unmaterialized stochastic per-vehicle values (2/1,333 exact matches, including 1/480 scheduled before R activation). The R-flow effect on the exact internal RNG draw order remains unproven without an instrumented run. No SUMO, TraCI, or netconvert was started.

## Verification

| Check | Result |
|---|---:|
| Control M/U/X | 1,333 / 150 / 75 |
| Treatment M/U/X/R | 1,333 / 150 / 75 / 192 |
| Common identities / full vehicle records | 1,558 / 1,558 |
| Desired integer departure schedule | 1,558 / 1,558 |
| Route/type and exact speedFactor | 1,558 / 1,558 |
| Complete route definitions (including edge lists/attributes) | 4 / 4 identical |
| Complete vType definitions (all attributes) | 1 / 1 identical |
| Treatment-only vehicle IDs | exactly R_flow.0–R_flow.191 |
| Regression tests | 9/9 PASS, including treatment-only flow, nested vehicle param, extra attribute, route and vType mutations |
| SUMO / TraCI / netconvert starts | 0 / 0 / 0 |

These checks cover inputs, not future insertion or trajectory realization. The previous one-start treatment authorization is consumed and remains consumed. Any future run requires a separately prepared exact card, fresh independent reviews, and new user authorization. No scientific input, classifier, threshold, witness contract, or formal protocol was changed.

## Provenance

See `COMMON_DEMAND_MANIFEST.json`, `INVARIANT_CHECK_REPORT.json`, and `PROVENANCE_RECEIPT.json`. The receipt binds generated route files, report, checker output, checker source and tests. Raw output and prior package versions were left unchanged; v4 supersedes v3.
