# Independent data/provenance prelaunch review — repaired v5 attempt 1

**Disposition: PASS_PRELAUNCH. Blocker/Major/required Minor = 0/0/0. Confidence: High for static binding and provenance.**

## Scope and context

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the adopted Stage 6 exploratory witness contract, the v5 matched-input review and receipts, the exact FINAL card package, and the independent engineering review. The project remains in exploratory Stage 6; the formal protocol is unfrozen. The state/worklog snapshot predates the active user's newer one-start authorization and therefore still describes the former preparation-only status. This review follows the newer explicit authorization but does not itself launch or open the runner gate.

The prior `PAIR_3199_R720_DELAYED_S17` raw remains a separate `NOT_EVALUABLE` attempt with consumed D-006 authorization. It is not reused or reinterpreted. This review writes only this report and its adjacent JSON, neither of which is a runner-recognized review-gate filename.

## Exact card and provenance

- Attempt/run ID: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`.
- Execution UUID: `b095cce4-baba-4c40-aa79-08b5e58b9ce1`.
- Exact card SHA-256: `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.
- Runtime binding SHA-256: `4978450c6dd83f37377d1f1a454ba35d5944e4d7a0ed353ed5d43906793b4053`.
- Runner SHA-256: `0961912a46464eb9757ab245c26577e8f1de0985534f34db04a41a4dac45f9c8`.
- Treatment demand SHA-256: `b8aae801122e918731fb8e05a9aa8ca94873f02282d7f1afee57777f6bea96ea`.
- Identity manifest SHA-256: `085d74f7bf12b1340f2a4ad90c2ae16074b91ffd5c98780c50321ffdb01d5cbd`.
- Additional/config/output-role hashes match the exact card: `f5156ffc1df7115c131bd2cef7bf3c119d86d57d781174a8ade565fb819f49ee`, `2a16baa12bd1abcaae9bff46a8b48f9365064e87e05ae1d416ba695157d9538d`, and `3c69a6e38184683455d2103c35a80405877a8b015261ccf13891706842b36ee3`.
- Network SHA-256: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`.
- Witness-contract SHA-256: `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- v5 source receipt/invariant-report SHA-256: `3a2531c3bbf3d9d69ac6c94f0f2663b67b47ffde7ce36c7ea0e1a943b74e32c9` / `509f1a46873b6922ce22e18f4100fa2dcb84a632d80ee9a014750efc6c857d54`.
- Matched-control card, data review, execution receipt, and output-manifest hashes all match their FINAL-card binding: `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`, `6c8c2a381a5a2fc1102953ed58a5a1cd022a0c22789b0bbbd486d86a7b0ac799`, `a6a1a67282ff9e19f0205ce4b681cef34315bc04ad65f9588d7b269fadcfd336`, `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`.

## Independent static invariant check

Ran the v5 fail-closed checker against the v5 control demand and the exact FINAL-card treatment demand:

```text
.venv/bin/python scripts/stage6/pair3199_common_demand.py \
  --control artifacts/stage6_pair_3199_matched_input_repair_20260923_v5/control/demand.rou.xml \
  --treatment artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/inputs/treatment/demand.rou.xml
```

Result: **PASS**, no failures. M/U/X IDs, desired integer-ms departure schedules, routes, vTypes, explicit speedFactors, and complete route/vType definitions match **1,558/1,558**. Counts are M=1,333, U=150, X=75 on each arm; control R=0. The only treatment-only identities are exactly `R_flow.0`–`R_flow.191` (192 total), with the card's `[540,1500)` schedule and 5,000 ms repetition offset. There are no control-only identities.

This establishes planned-input equality only. It does **not** establish realized insertion, pre-R trajectory equivalence, or post-R causal attribution. The card correctly preregisters the pre-meaningful-R trajectory gate; any unexplained material pre-R M/U/X divergence makes the pair `NOT_EVALUABLE` before post-R witness interpretation.

## Execution-path and resource checks

- The new exact-card output directory does not exist.
- Its one-use consumption directory does not exist and contains no reservation.
- The prior attempt remains at its separate output path. Its output-manifest SHA-256 remains `92dbe5627f8afbfe26f50bc8d62207ca9a9ed579c6f707481079d8ad795228dd`, matching the prior immutable execution receipt; its `NOT_EVALUABLE` status is preserved.
- New attempt limits are bound to 90 seconds and 75,000,000 decimal bytes, polled at 100 ms with slight stop overshoot accepted. Maximum starts=1; technical retries=0.
- Engineering's read-only R02 preflight reports no process started and `launchable_now=false` while the remaining fresh reviews and binding sidecar are pending.
- SUMO/TraCI/netconvert starts for this review: **0/0/0**.

**Limit:** No realized data exists at the new path, so lifecycle, insertion, actual R merge exposure, and trajectory matching remain strictly post-run checks.
