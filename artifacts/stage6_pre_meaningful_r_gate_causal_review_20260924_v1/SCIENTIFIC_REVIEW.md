# Stage 6 pre-meaningful-R trajectory gate: independent causal review

**Status:** `PASS_TO_PROPOSE_VERSIONED_AMENDMENT`; independent `scientific_reviewer` methodological disposition `PASS`, Blocker/Major/required Minor `0/0/0`. This is a review record, not an adopted amendment or a revised treatment result. Confidence: High for the gate's causal logic; Moderate for the specific physical cause of the seven U trajectories.

## Scope and bound evidence

The review considered only the adopted Stage 6 exploratory witness contract and the repaired PAIR3199 attempt's pre-first-through-merge trajectory evidence. No t>=591 P/S/L, Candidate A/C, M deterioration or witness outcome was inspected. No simulator or data-processing run was performed in this review.

- Adopted contract: `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- Pre-merge data review: `artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/INDEPENDENT_DATA_POSTRUN_REVIEW.md`, SHA-256 `fcabdde57ceb07a181b0878007ebf2bbdf501d532f36555c9d7bdccad4a1c20e`.
- Historical scientific post-run disposition: `artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/SCIENTIFIC_POSTRUN_REVIEW_FINAL_REV1.md`, SHA-256 `95382de387c436dc0980dcc263b1e5a5ceb586abcfd0123ecdc428a9e0fac7a6`.

The data review reports 41,042/41,042 common M/U/X vehicle-second keys over t=[0,591); 40,844 exact FCD tuples and 198 differing tuples, all involving seven U identities. M and X match over that interval. The first U difference and first actual R departure are at t=540 on the shared `urban_in_0` approach; the first observed R through-lane entry is t=591. These are observed associations. They do not establish the physical cause of the U displacement.

## Causal judgement

The original operational gate is too strict **for the contract's R-admission-associated exploratory estimand** if it requires U trajectory equality after R has entered the shared approach. A treatment can change U through a source/approach pathway before its first freeway merge. Such a post-treatment U response should not be labeled a baseline confound merely because it precedes the freeway merge. The timing and shared location make a treatment-mediated response plausible, not proven; insertion order, stochastic behavior, lane change, measurement and source/downstream pathways remain alternatives.

The contract explicitly does not claim pure merge-friction identification. If a future analysis instead seeks the direct merge-pressure mechanism, an R-to-U-to-mainline/source pathway is a competing mechanism requiring separate adjudication. A revised gate must not automatically waive U differences or automatically count them as proof of a treatment effect.

The three stages should be explicit:

1. **t<540, pre-treatment:** require planned and realized common M/U/X identity, route/type/factor, actual-departure, trajectory and sample-coverage matching. The existing report's first difference at t=540 is consistent with this condition; a revision-specific independent raw recomputation is still needed.
2. **540<=t<591, post-treatment and pre-first-through-merge:** require M and a verified non-treatment-pathway X to remain matched, record every U difference and check R/U vehicle ordering, common approach/lane positions, insertion delays, source constraints, stochastic realization and measurement. Treat U as a possible treatment response while retaining source and downstream alternatives.
3. **t>=591, after first observed through-lane entry:** this boundary does not itself certify meaningful merge exposure. The adopted contract requires three consecutive complete 30 s bins with positive certain R entries; the recorded sequence `[570,600)`, `[600,630)`, `[630,660)` confirms T3 only at t=660. Locked P/S/L and event windows must stay unchanged, and any later attribution requires its own same-time/location comparison and alternative-cause checks.

## Versioning and reuse of existing raw

A separate, versioned amendment is scientifically warranted. It should state the estimand, the three-stage gate, U/source-path audit, unchanged T3/classifier/windows and failure conditions; bind the original contract hash and the already known pre-gate data; and be frozen before opening any post-591 outcome. Because the proposed rule follows an observed mismatch, any application to this existing pair must be labeled a **retrospective exploratory sensitivity analysis**. It cannot replace the original contract's historical `NOT_EVALUABLE` disposition. The amendment needs independent review and explicit user adoption before use.

Existing hash-bound FCD, vehroute, tripinfo, lane-change, E1/E2 and TLS records appear sufficient for an offline re-evaluation without a new SUMO start. This is conditional. An independent data review must first recompute both pre-merge periods from raw, including identity/sample/departure matching and R/U contact order; engineering must check source, lane/geometry and measurement coverage; scientific review must determine whether the U/source path leaves a material alternative explanation. Only after those checks pass may the amended analysis inspect later outcomes. If raw evidence cannot separate a physical R-to-U response from an insertion, stochastic or measurement artifact, or cannot bound its relation to later mainline change, retain `NOT_EVALUABLE`. The smallest additional action is an offline, vehicle-linked source/approach chronology and lane/geometry mapping.

## Preservation boundary

The adopted contract, P/S/L thresholds and all prior cards, raw data and `NOT_EVALUABLE` decisions remain unchanged. This review grants no simulation, reclassification, witness analysis or protocol adoption. SUMO/TraCI/netconvert starts for this task: `0/0/0`.
