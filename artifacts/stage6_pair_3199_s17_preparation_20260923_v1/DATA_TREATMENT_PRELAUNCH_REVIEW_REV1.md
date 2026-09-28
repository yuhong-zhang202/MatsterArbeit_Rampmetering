# Independent data/provenance prelaunch review — PAIR_3199_R720_DELAYED_S17

**Disposition: PASS.** Blocker/Major/required Minor = **0/0/0**. Confidence: High for static data/provenance binding. This is a prelaunch static review only; it is not execution authorization and makes no claim about future treatment data.

## Context and scope

Project context reviewed: `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`. Scope was limited to the exact treatment card, its input/runtime/runner bindings, the user-adopted Stage 6 exploratory witness contract and its independent scientific PASS, and the existing PAIR3199 control card, execution evidence, raw manifest, data/lifecycle review and processed-data hash receipt. No SUMO, TraCI, netconvert, R04, classifier, or new raw-data analysis was run.

## Exact-card and input verification

Treatment card `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV1.json` recomputes to SHA-256 `263c63f356b02353655a5e8e06eb7089d527e82f8137f45a8ecaf63054fd38a4`, matching the requested card identity. Its fields specify qMain=3199.2 veh/h, M=1333 on [0,1500), U=150, X=75, seed17, A_OPEN, 1 s step, 2700 s horizon, and delayed R=192 on [540,1500), equivalent to qRamp=720 veh/h. `PAIR_INPUT_DIFF.json` declares the sole scientific demand difference to be the R source; common M/U/X flows, route/type source, network hash, seed, TLS and horizon agree. Operational differences are run IDs and exclusive output paths.

Recomputed input hashes match the card: demand `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`; additional `13dc69427f24014e02c4ded173ba5d2db12ebf2666c0b77f2cc486a19755332a`; network `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`; output roles `7dab35372984ccd3e7f103afaaf0dff59ecf4df6dc13d4c66dea5190fa77155d`; sumocfg `70a082e81a32f3a759a8b26cd9cbf426358d7cf4f40eedcef72d3f272d851072`; expected-identity manifest `a69ba23ed1a82957904c8abc4aee774decf94d0210c07d29d051c0162f7aef1b`.

The card binds witness-contract SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`, matching the current contract file and its independent scientific review. The card scopes that contract to this Stage 6 exploratory pair and marks formal protocol status unfrozen. It explicitly does not require `LOW_R_BACKGROUND_ACCEPTABLE` for treatment release, identifies the control as not a clean normal baseline, preserves its historical NOT_EVALUABLE and Candidate C warning labels, and records all five required chronology markers: R activation, first R departure, first meaningful merge exposure, first M deterioration, and State1 onset. This accords with the user's task-limited adoption.

Runtime sidecar, runner and runtime evidence hashes in the treatment binding were recomputed and match: sidecar `184f640de731c3da26593e2da55ab81d5bb23232cb6e7a4c9a37645648d94a41`; R02 runner `76175f1361bd007b5d9d7382b625fd0c3b81b2022022e4093ec5aa747685cdf3`. The resource proposal is metadata only: 120 s and 90,000,000 decimal bytes, treatment-scoped, 100 ms polled stop trigger with possible overshoot, status `PROPOSED_NOT_AUTHORIZED`. It is not an analysis threshold or authorization.

## Matched-control provenance and preserved history

The treatment card's control bindings recompute exactly: control FINAL_REV1 card SHA `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`; lifecycle review SHA `6c8c2a381a5a2fc1102953ed58a5a1cd022a0c22789b0bbbd486d86a7b0ac799`; execution receipt SHA `a6a1a67282ff9e19f0205ce4b681cef34315bc04ad65f9588d7b269fadcfd336`; output manifest SHA `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`.

Against the existing independent control hash receipt, all **27/27 raw files** and **25/25 processed outputs** recompute to their recorded SHA-256 values. The bound control review reports lifecycle/raw integrity PASS, explicit R=`PASS_ZERO`, 1,333 M / 150 U / 75 X scheduled, inserted and arrived, P/S/L=`NO_QUALIFYING_EVENT`, Candidate A absent, Candidate C=`EARLY_WARNING_PRESENT_NOT_STATE1`, fixed PRE screen 3/30 PASS, fixed control screen 17/150 PASS, and final `LOW_R_BACKGROUND_ACCEPTABLE=NOT_EVALUABLE`. The separate scientific post-run review retains the same NOT_EVALUABLE outcome and the unresolved low-speed history. These labels are neither overwritten nor recoded here. The control remains a candidate comparator under the adopted exploratory contract, not a certified normal baseline.

The prior control data review's inherited metadata finding DM-01 (one required minor about the immutable control card's nonempty unresolved-prelaunch field) remains recorded in the original control review. It does not indicate a raw hash mismatch and has not been altered or silently cleared by this treatment review.

## Exclusivity, limitations, and conclusion

At review time the treatment output directory and its run-specific R02 consumption/reservation file are absent. The exact-card/read-only-preflight receipts state `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launch_authorized=false`, and `simulator_process_started=false`. The requested static checks therefore pass; this review does not validate future raw completeness, lifecycle, actual R departure or merge exposure, event chronology, or treatment-control effects. Those remain post-run checks under the adopted witness contract.

No raw or processed data, card, input, control history, classifier, threshold, or protocol was modified. Data/provenance disposition: **PASS (0/0/0)** for this exact treatment prelaunch binding.
