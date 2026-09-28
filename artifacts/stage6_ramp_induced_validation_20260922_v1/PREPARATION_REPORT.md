# Offline preparation report — RI3350 control

Status: **PREPARATION_BLOCKED / DRAFT_NOT_AUTHORIZED**  
Review scope: offline readiness artifacts only; no simulation execution authorization.

## R01 → R03 → R05 → R06 → R07 closeout

- **R01 — bounded PASS.** The static semantic diff verifies the intended M/U/X equivalence and removal of the R demand from the control input; detector/TLS/WAUT semantics are preserved. Control output paths remain placeholders. No XSD or runtime validation was performed. Receipt: `r01_r03/r01_static_audit_receipt.json`.
- **R03 — plan/fixture PASS; observed pairing UNKNOWN.** Pairing checks fail closed when required fields are absent, and mismatch fixtures cover missing speedFactor and unequal values. No transition outputs exist to assess realized matching. Receipt: `r01_r03/r03_pairing_readiness_receipt.json`.
- **R05 — logic-fixture PASS; production application pending.** The fixed 30-row PRE screen, complete-key requirement, event-mask handling, strict integer parsing, and missing-data UNKNOWN behavior have synthetic fixtures. No production raw parser / locked-classifier adapter or control raw application is included; R04 remains partial.
- **R06 — interval/coverage-helper fixture PASS; route mapping and application pending.** Empty crossing is zero only after byte-hash, source-coverage, and exact scheduled-versus-lifecycle R identity reconciliation. Unknown coverage propagates as UNKNOWN. Future route-progress construction, parser attestations, and real R raw application remain pending.
- **R07 — bounded coverage audit PASS, G6 not cleared.** Existing outputs support conditional evidence review but do not establish the registered same-R-blocker / same-U-victim / space-time / linked-U-delay predicate. A connector coverage gap remains. `NOT_ESTABLISHED/UNKNOWN` is not evidence of no obstruction or urban safety.
- **R09 — bounded review PASS.** Engineering and data checks, followed by independent scientific review, support only the offline artifact statuses above. The review explicitly retains all application and G6 limitations; it does not authorize a run.

The R05/R06 receipt binds the helper, tests, and contract hashes and records 16 synthetic tests passing; the R07 receipt binds its script/data audit and fixture. Final review re-read the hashes/receipt but did not independently rerun tests. Static audit/fixture passage is not a substitute for runtime, raw-data, or scientific-outcome validation.

## Remaining card blockers

- R02: isolated one-start runner is not implemented.
- R04: complete path-isolated locked-classifier adapter and new-output validation are incomplete.
- R05/R06 production parser/adapters and control/raw application are pending.
- R01/card binding: output destinations, exact runtime binary identity, resource stop-line, and launch argv are unresolved.
- R03 realized pairing remains unknown; R07 G6 remains `NOT_ESTABLISHED/UNKNOWN` and blocks baseline suitability.

The card remains revision 2 `DRAFT_NOT_AUTHORIZED`, with no command, `execution_authorized=false`, `max_starts=1`, zero technical retries, and progression disabled. No SUMO, netconvert, or TraCI was started; no scientific input, classifier, geometry, demand, or formal protocol changed. A later exact card approval would still be required after blockers are resolved.
