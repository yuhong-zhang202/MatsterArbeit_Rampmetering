# Issue #10 bounded engineering review

Result: **STOP_A1_UNDER_CURRENT_INTERFACE**, an engineering NO-GO recommendation for user review, not an approved safety-contract or research decision. Under the unchanged protected actuator/model, current pre-red public observations plus the source-supported bounds verified in this one investigation do not establish the required joint ordinary-braking, non-crossing, follower, lane-change and receiving-lane certificate. This is **not** a proof that every stronger conservative construction is impossible; that claim is NOT_PROVED. No unsafe native red outcome, Candidate A physical impossibility, or A1/A2 qualification is inferred.

## Context and scope

Read AGENTS, project-state/decisions/worklog, empty formal protocol, Issue10 full source, Issue8 contract/proof obligations/source ledger/A07 snapshot, protected safety/actor/worker and prior V6 scientific review. Stage6 closeout stays unchanged; formal protocol is 0 bytes, future execution remains HOLD. No missing required context; empty protocol prohibits formal execution. Exact investigation baseline: `7ce8f5e19d737117dc6f25165993fc436244c599`. This report belongs to static implementation-feasibility investigation only.

Read-only official SUMO v1_26_0 commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3` sources were genuinely retrieved (18 fresh files), plus exact previously retrieved files independently rehashed. Permanent physical-line excerpts and full-file SHA receipt are published. Full source bytes remain temporary local references; no private/raw data was uploaded. Installed metadata is traci/sumolib1.26.0, sumoITScontrol0.1.0, Python3.13.0; the SUMO binary hash matches the protected prior receipt. Compiler/build-to-source equivalence is NOT_VERIFIED; no binary was launched or C++ built.

## Decisive observations

- Native event processing precedes movement planning and execution. Exact DriveProcessItem, vSafe/vSafeMin and final speed are computed inside the upcoming step, rather than returned by the checked pre-step getters. See N_EVENT/N_POST/N_DPI/N_EXEC/N_FINAL excerpts.
- `getLastActionTime` exists; last-action timing is queryable, not inherently hidden. Lane-position, route, effective type/scalar modes and current neighborhoods can close several earlier witness-input gaps if freshly bound. Stored A07 fields do not contain all those observations.
- `getNextLinks` reconstructs route/best-lane queries using hypothetical speed-limit arguments; `getJunctionFoes` adjusts a previous-step approach cache. Neither is a future native reservation/request certificate. `getSpeedWithoutTraCI` and lane-change state retain prior results.
- `getStopSpeed` uses FUTURE calculation, unlike the CURRENT emergency-relaxation branch; supplied-query stop/follow/secure-gap output cannot be equated to finalized native joint motion.
- Device presence and explicit junction-model parameter getters can help branch exclusions. Empty explicit parameter is not zero effective source default. SaveState serializes current state but the checked paths do not return future DPI/final movement; it was not invoked. Serialization/device state was not exhaustively audited.
- Conditional front-link geometry/offset and local Krauss random bounds are useful subproofs. They do not compose into the required ordinary-deceleration/follower/downstream guarantee. Source lower bounds may admit emergency braking; an interval admitting a speed below the normal-braking lower limit cannot certify all outcomes. The two matrix examples are analytical insufficiency examples, not observed native trajectories.

The 69-row ledger explicitly groups additional friction/stops/startup/influencer/RNG and length/minGap/class binding limits. It is not an exhaustive schema or a claim every missing field is inaccessible. P0-P10, M/R/U/X and followers/ingress/receivers/foes are all addressed with their finite scope and unresolved obligations.

## Verification and retained history

One small public static verifier checks source/excerpt hashes and references, P0-P10 coverage, unchanged prior public audit, 42 witness mappings and 536 protected files. The first draft pass (68 rows) is retained as STATIC_VERIFICATION_OUTPUT.json; independent data review requested explicit non-exhaustive dependency disclosure. Final R1 pass (69 rows) is STATIC_VERIFICATION_OUTPUT_R1.json and current INPUT_BINDINGS.json. No source predicate, mathematical helper, safety contract, guard or old evidence changed. There are no new unit/synthetic suites or old43-test reruns.

Final command: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/candidate_a_a1_proof_gap_20261011_v1/verify_public.py`. PASS, 0 failed checks, 0 SUMO/TraCI starts, 0 native builds, 0 production-file drift. Six windows retain observed steps `[6,0,0,0,0,0]`; observed zeros, partial first window and five unobserved windows are unchanged. A07 still has 42 conditional projections, 0 determined actual branches, UNKNOWN unexecuted red outcome and preserved current-contract STOP3. R900 remains NOT_TESTED; no new rate qualification. Parent must separately record an actual clean-checkout execution; this review does not claim one.

## Minimal handoff and stop

Q1 current getters partially close inputs, but the future joint certificate is not closed. Q2 current enumeration is technically plausible with explicit world/route/loaded/pending/neighbor exclusions, but not certified by the sparse A07 witness alone. Q3 the combined ordinary-braking/follower/lane-change/transition/receiver proof remains unresolved. Stop the current bounded interface investigation here.

Next is a **user/Robert discussion**, choosing a simpler sourced actuator/signal operation or authorizing a separate internal-observation **design-feasibility proposal**. Such a proposal would need a sufficient joint interval or a noninterfering within-step observation/pause design; after-step logging alone cannot repair a prospective gate. No implementation is authorized. Estimated discussion/static review cost: 2–4 engineering hours; if separately requested, instrumentation-design investigation: 1–3 engineering days, with actual core build/maintenance cost not yet reliably estimated. Core/model changes, weaker safety assumptions, altered actor/guard or a simulation request require new explicit scope/approval.
