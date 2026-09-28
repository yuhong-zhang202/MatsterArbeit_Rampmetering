# Independent scientific prelaunch review — repaired v5 treatment attempt 1

**Disposition: PASS_PRELAUNCH for the exact card's bounded Stage 6 exploratory scope.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0.  
**Confidence:** High for scope, contract and input-binding consistency; Moderate for prospective causal interpretation, which remains contingent on the preregistered post-run gates.  
**Execution status:** This review does not launch SUMO. The card's execution authorization is present, but the runner is not launchable until its three specifically named review JSON receipts and exact-hash binding sidecar exist and verify.

## Context preflight and exact question

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`, plus the bounded Stage 6 plan, adopted witness contract, v5 engineering/data/scientific receipts, the prior treatment's `NOT_EVALUABLE` disposition and consumed D-006 record, the current FINAL card package, and this attempt's independent engineering and data/provenance reviews and read-only preflight.

The project is in exploratory Stage 6; O2 remains unresolved and the formal protocol is unchanged and unfrozen. The project snapshot and D-006 describe the earlier preparation-only/consumed authorization state. The current user message supersedes that operational snapshot for this distinct repaired attempt: it accepts 90 s / 75,000,000 decimal bytes with 100 ms polling and slight overshoot, and authorizes exactly one repaired treatment start. The earlier treatment retains its `NOT_EVALUABLE` result and consumed D-006 authorization. The question here is whether this exact repaired card is scientifically fit for its narrowly scoped start, and whether its post-run gate prevents interpreting post-R effects when pre-R trajectory matching fails.

## Exact-card review

- Scenario: `PAIR_3199_R720_DELAYED_S17`; new run/attempt ID: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`.
- Execution UUID: `b095cce4-baba-4c40-aa79-08b5e58b9ce1`.
- FINAL card SHA-256: `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.
- Runtime binding SHA-256: `4978450c6dd83f37377d1f1a454ba35d5944e4d7a0ed353ed5d43906793b4053`.
- Runner SHA-256: `0961912a46464eb9757ab245c26577e8f1de0985534f34db04a41a4dac45f9c8`.
- v5 repair review-receipt SHA-256: `e892bd7d7be026fbe56a3ef4675c1475427de910ae097d993e583fe8d257776a`.
- Witness contract SHA-256: `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- Card demand SHA-256: `b8aae801122e918731fb8e05a9aa8ca94873f02282d7f1afee57777f6bea96ea`.

The new attempt has a distinct output path and one-use consumption path. Read-only checks show both absent. The prior treatment's raw, card, output manifest and consumed authorization remain separate and are explicitly marked `NOT_EVALUABLE`, not reused or reinterpreted. The new attempt is tied to seed 17, qMain=3199.2 veh/h, qRamp=720 veh/h, A_OPEN, R window [540,1500), same accepted geometry, U/X, vehicle behavior and 2700 s horizon. The accepted resource terms exactly match the current user authorization; retry count is zero and maximum starts is one. Prohibited seed23, transition, other qMain/qRamp and B/C runs are explicitly listed.

## Scientific assessment

The exact card binds the adopted exploratory witness contract, not the formal protocol or the old `LOW_R_BACKGROUND_ACCEPTABLE` gate. It preserves the control's historical `NOT_EVALUABLE`, failed-screen and warning status and explicitly disclaims a clean normal baseline. The treatment contrast remains R-only under the reviewed v5 plan: the v5 receipt and exact-card input binding report 1,558/1,558 matching complete M/U/X records, with treatment-only identities exactly `R_flow.0–191` (192 records). The independent data prelaunch receipt confirms these counts and departures/routes/types/speedFactors. This verifies **planned input matching only**; it does not establish future realized insertion or trajectory equivalence.

The card preregisters the critical sequencing safeguard: compare M/U/X trajectories before first meaningful R merge exposure; any material unexplained pre-R divergence makes the pair `NOT_EVALUABLE`, and post-R witness analysis is allowed only if that gate passes. It also binds the contract's required event markers (R activation, scheduled and actual R departures, first near-merge arrival, meaningful merge exposure, M deterioration, State1 onset). This is the appropriate protection against attributing differences already present before R exposure to R. The card retains the contract's separate same-time/location/lane/cell comparison and alternative-cause checks for the post-run stage. No thresholds or scientific inputs were changed.

The card's sole start cannot itself establish a general breakdown probability, capacity, pure merging-friction effect, optimized demand pair, formal thesis result or clean baseline. It can support only the bounded exploratory disposition, and only after lifecycle, R exposure, pre-R matching, locked event, matched-control, alternative-cause and independent post-run reviews are completed. The planned sequence is scientifically defensible for the scoped existence test.

### Measurement review applicability

1. **Measurement target:** The adopted contract defines the target as matched M deterioration/event status at common time, location, lane and cell, with fixed horizon/window and explicit R-exposure ordering. Actual vehicle cohorts, sample coverage and treatment of incomplete vehicles must be reconciled after the run; not yet observed.
2. **Actual coverage:** Not verified prelaunch. The existing config/output roles and geometry are hash-bound, but runtime detector/FCD coverage and branch/internal-lane completeness require post-run evidence.
3. **Omitted/duplicated observations:** Not verified prelaunch. The future lifecycle/FCD ledger must account for all expected and realized identities and labelled lane/cell/time samples, including unfinished and waiting-to-insert cases where applicable.
4. **Independent reconciliation:** Not yet applicable to new results because no new raw exists. The adopted contract requires independent recomputation from immutable per-vehicle FCD and route/lane-change evidence, plus raw reconciliation of decisive R exposure intervals.
5. **Regression protection:** Not a measurement-code review. The reviewed v5 input checker has separate independent test evidence; post-run reconciliation must still surface missing labels, internal-lane/boundary coverage and incomplete-run cases rather than infer them from configuration.

These are future evidentiary gates, not prelaunch defects: the card does not claim those measurements have already been observed or verified.

## Findings and unresolved execution gate

No scientific Blocker, Major or required Minor was identified for the stated prelaunch question.

One **execution-provenance condition** remains outside this scientific disposition. The card's own `prelaunch_review_gate` requires JSON receipts at:

- `FINAL_ENGINEERING_PRELAUNCH_REVIEW.json`
- `FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json`
- `FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json`

and then `FINAL_PRELAUNCH_REVIEW_BINDING.json`, binding all three receipt hashes to this exact card SHA. The currently present independent engineering/data artifacts and this report use `INDEPENDENT_*` filenames; the read-only preflight says reviews are pending and `launchable_now=false`. Those independent reviews are PASS for this exact card, but the card-named receipts and binding sidecar were absent when checked. Therefore the user has authorized the one start, yet the runner's fail-closed launch condition is not yet satisfied. This is not a scientific finding and does not alter this PASS disposition.

## Recommendation

Scientific prelaunch review is **PASS_PRELAUNCH**, findings 0/0/0. Preserve this exact card and scientific inputs. Before an authorized launch is attempted, verify that the runner-recognized receipts and sidecar have been produced from the three exact-card PASS reviews, all hashes match, the output remains absent, and the read-only preflight reports launchable. Any launch then consumes the one-start authorization; no retry or progression is covered. No simulator, TraCI or netconvert process was started during this review.
