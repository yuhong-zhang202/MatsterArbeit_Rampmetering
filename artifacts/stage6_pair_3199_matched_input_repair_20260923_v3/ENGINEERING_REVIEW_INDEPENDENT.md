# Independent engineering review — PAIR3199 matched-input repair v3

**Disposition: NOT PASS — one required fail-closed checker issue.**
**Findings:** Blocker 0 / Major 1 / required Minor 0.
**Confidence:** High for the observed checker behavior and current package hashes; Moderate for the old speedFactor RNG mechanism, which remains unproven.
**Scope:** Read-only review of v3 construction/checker, tests, provenance and the prior treatment engineering/data evidence. No files other than this review were changed. No SUMO, TraCI or netconvert was run.

## Context and evidence

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the PAIR3199 final treatment card and engineering/data post-run reports, plus v3 `MATCHED_INPUT_REPAIR_REPORT.md`, manifest, invariant report, provenance receipt, independent data/scientific reviews, materializer and tests. The previous treatment authorization is consumed; the formal protocol remains unfrozen. No run is authorized by this package.

Prior `sumo.log` and data review support the U/X cause: SUMO reported that the unsorted route file caused it to ignore `U_flow` and `X_flow`, and raw identity reconciliation found all 225 U/X identities absent. V3's globally departure-sorted explicit common vehicles addresses this mechanism.

The prior M speedFactor mismatch is addressed prospectively at input level by assigning every common identity the recorded lexical factor from the control's `vehroute.xml` to both arms. The old treatment's changed factor realization is consistent with a changed stochastic construction/draw sequence, but the precise RNG draw-order mechanism is not proven. The input binding avoids relying on same-seed RNG to reproduce these factors; it does not guarantee future trajectory or all simulation-time random-decision equivalence.

## Verified package behavior

- Recomputed SHA-256 values match the receipt for the checker, test file and both v3 demand files.
- Existing v3 XML passes the checker: M/U/X = 1,333/150/75 in each arm, 1,558/1,558 common IDs/records and speedFactors, and treatment-only IDs exactly R_flow.0–R_flow.191.
- The targeted unittest suite passes 6/6. It covers valid inputs, missing U identity, common speedFactor mismatch, missing explicit speedFactor, changed route edge list and changed vType attribute.
- Code inspection found no subprocess, SUMO, TraCI or netconvert launch path in the materializer/checker.

## Required issue — accepted XML content outside the checked inventory can bypass R-only validation

`parse_materialized()` reads only direct `<vType>`, `<route>` and `<vehicle>` elements. It does not reject additional route-file records such as `<flow>`, `<trip>`, `<person>`, or distributions, nor does it compare nested content under a `<vehicle>`, `<vType>`, or `<route>`. The checked vehicle sets and full-record comparison therefore do not prove that those unchecked records are absent/equal.

I verified the failure with temporary copies only: adding a treatment-only `<flow id="UNAUTHORIZED" ...>` to the v3 treatment file still returns `PASS`; adding a treatment-only `<param>` child to common `M_flow.0` also returns `PASS`. These are concrete violations of the required “treatment-only difference = R” fail-closed invariant. Existing generated files contain neither mutation, but a checker advertised for future preflight must reject them rather than silently ignore them.

**Required closure:** enforce an explicit allowed XML grammar/inventory for these route files, rejecting all unsupported top-level records and nested vehicle content; or fully canonicalize and compare all semantically relevant XML subtrees while permitting only the exact 192 R vehicle additions. Also compare complete route/vType subtrees or reject child content if the accepted source schema has none. Add mutation regressions for unauthorized treatment `<flow>` (and at least one other unchecked record), common-vehicle child, and nested definition content. Recompute report and receipts after any repair.

## Disposition and limits

The present v3 files are statically matched at the required common per-vehicle fields and have consistent hashes, but the checker does **not yet** establish the requested fail-closed treatment-only-R invariant under relevant XML mutations. Engineering review is therefore **NOT PASS** until the issue above is closed and independently rechecked. This review does not alter the v3 inputs, authorize a new card, authorize execution, or interpret the previous treatment as witness/no-witness.
