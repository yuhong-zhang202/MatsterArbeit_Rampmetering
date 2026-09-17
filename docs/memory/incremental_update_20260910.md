# Masterarbeit-Ramp-Metering — reviewed incremental memory candidate 2026-09-10

Project identity: `Masterarbeit-Ramp-Metering`  
Update status: `dry-run candidate; not approved for paid execution or memory write`  
Previous formal seed: `docs/memory/formal_import_bundle_20260909.md`

## Authority and scope

This delta records changes after the 2026-09-09 formal seed. It is auxiliary memory input, not academic evidence. Current repository documents remain authoritative. Approval attached to this candidate permits local dry-run validation only. It does not permit Keychain access, Docker execution, network access, a paid model call, L0/L1/L2 generation, or L3 writeback.

Evidence labels used below are `observed`, `calculated`, `proposed`, `user-approved`, `supervisor-confirmed`, `frozen`, and `unknown`.

## Superseded state

- `observed`: The old L3 statement “Stage 2 exploratory uncontrolled checks are incomplete” is stale. The user explicitly accepted G2 and closed Stage 2 as a finite uncontrolled diagnostic milestone.
- `observed`: Stage 2 closure does not mean the broader exploratory-validation phase is complete, does not establish suitability for formal ALINEA comparison, and does not authorize later work.
- `observed`: The earlier six-row diagonal G1 package remains superseded and unauthorized. Old upstream E1 values affected by insertion overlap remain ineligible for traffic-state inference.

## Stage 2 accepted milestone

- `user-approved`: User approval was: “批准 G2，正式关闭 Stage 2。” The accepted scope is the bounded C/ML/MH/RL uncontrolled diagnostic only.
- `observed`: Eight logical records were completed: C17 was reused and seven new SUMO runs were started. The authorized ceiling was eight new starts; seven were used and no technical retry was used. All new runs used SUMO/netconvert 1.26.0, seeds 17/23, and the same 0/1500/1200-second finite-horizon arrangement.
- `observed`: All planned vehicles eventually entered and arrived before 2700 s. Every run still had R/U vehicles entering after demand ended at 1500 s, so clearance was not a zero-inflow recovery period and final completion does not prove demand-period realization.
- `observed`: The archive contains 232 reconciled files. Final archive-only analysis reconciled 14,564 run-vehicle records, 4,320 E1 rows, 2,912 cohort rows, 2,100 R first-downstream observations with 4,200 bracketing endpoints, and 198 matched-seed contrasts. Scientific review found no Blocker or Major within the declared finite diagnostic scope.
- `observed`: At qRamp=720 veh/h, lowering qMain from 3200 to 2600 produced more R first-downstream observations before 1500 s, less R/U outside accumulation at 1500 s, and more U arrivals in both seeds. Raising qMain from 3200 to 3800 produced zero R first-downstream observations before 1500 s in both seeds, more R/U outside accumulation, and fewer U arrivals, while the measured M-only internal section retained high passage and speed.
- `observed`: At qMain=3200 veh/h, lowering qRamp from 720 to 360 strongly reduced R/U outside counts and increased U arrivals, but changed R first-downstream observations only by +2/0, increased U in-network counts by 14/13, and did not produce a consistent M-speed direction. It cannot be summarized as improvement in every urban or freeway measure.
- `calculated`: These directions are early two-seed sensitivity descriptions. They are not statistical robustness results.

## Evidence limits retained after closure

- `unknown`: Freeway Breakdown, Capacity Drop, steady state, capacity, causal urban loss, and a sweet spot have not been established.
- `unknown`: Ordinary E1 outputs do not prove per-vehicle zero omission or duplication; exact aggregate flow schedule timing and a complete mid-run outside-waiting curve are unverified.
- `observed`: The two internal M-only E1 loops are valid for their declared aggregate merge-entry scope. They do not represent an extended upstream feeder state.
- `proposed`: The 0/1500/1200-second arrangement may remain a finite-horizon candidate. It is not a selected or frozen formal timing design.
- `unknown`: The current synthetic scenario's suitability for a formal uncontrolled-versus-ALINEA comparison remains unresolved.
- `frozen`: No formal experiment setting is frozen. `docs/EXPERIMENT_PROTOCOL.md` is empty and no formal thesis experiment has started.

## Proposed exploratory-validation route

- `proposed`: `docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` defines six required outputs and eight evidence/quality gates, followed by Stage 3 archive-only diagnosis, conditional Stage 4 bounded targeted validation, Stage 5 exploratory assessment closeout, and Stage 6 a formal-design proposal for Robert review.
- `proposed`: Stage 3 would add zero SUMO/netconvert starts and use archived evidence to complete spatial-temporal behavior diagnosis, measurement contracts, demand/vehicle accounting, sensitivity checks, and intended-use claims.
- `proposed`: Stage 4 is conditional. It may be marked not required if Stage 3 answers the registered questions; otherwise its exact intervention, matched comparison and run budget require a separate approved registration card. The plan's maximum is a management ceiling, not a scientific sample-size claim.
- `proposed`: Stage 5 separates “exploratory assessment completed” from “scenario preliminary_ready”. A result may instead be `specific_obstacle` or `unresolved`; completing assessment does not force a favorable validity result.
- `proposed`: Stage 6 would classify which parameters and metrics can carry forward, draft the project's formal design, and prepare specific questions for Robert. Sending material, changing `docs/EXPERIMENT_PROTOCOL.md`, freezing a protocol, and running formal experiments each require their own authorization.
- `observed`: The user has authorized preparation of the completion framework only. Stages 3–6 have not been authorized for execution.

## Research and supervisor boundaries

- `user-approved`: Decisions D-001 through D-004 remain provisional and unchanged: evaluation-oriented scope, acceptable-region sweet-spot concept, minimal M/R/U urban-spillback mechanism, and the Stage 1/literature/Stage 2 preparation sequence.
- `supervisor-confirmed`: Robert Hilbrich supports the starting direction of sumoITScontrol, ALINEA, a simple freeway/on-ramp/small urban network, uncontrolled demand exploration near breakdown, Krauß defaults as a starting point, and validation of actual high-demand insertion. He identifies the finite-storage conflict and possible reduction/override of metering to protect the subordinate network as interesting.
- `unknown`: Robert has not confirmed the final research question, title, acceptable-region definition, formal metrics, demand ranges, seeds, timing, controller settings, override rule, or experiment protocol.

## Current next action and hard boundaries

- `proposed`: Review and explicitly approve or reject Stage 3's archive-only analysis contract. Do not treat this memory dry-run as Stage 3 authorization.
- `observed`: No new simulation, data reanalysis, controller implementation, external supervisor message, formal protocol change, or research-decision change is part of this memory preparation.
- `user-approved`: Ordinary Codex conversations must remain on the existing subscription provider. Tencent project memory is updated only on explicit request; each paid milestone update requires a fresh exact-file, hash, call-count and cost approval.

## Source manifest

The delta was prepared from these current files. Hashes are SHA-256 of the exact local bytes inspected on 2026-09-10:

- `docs/PROJECT_STATE.md` — `37d6ff5406165cc0cb30d27fa0f88b4f0211a8a1baeb8cb4bdd3ef6eb8f9450e`
- `docs/DECISIONS.md` — `4e440204b812a9ed28181b6b4aa54818ca5e7a39d207aeaadcab12cf8cb00d7a`
- `docs/SUPERVISOR_FEEDBACK.md` — `49d8d410f5c68e56c023b9e0f92b23cdf00bde55658e993a4f7ce5be996ec446`
- `docs/supervision/2026-08-25_robert_hilbrich_reply.md` — `e788f4c12d36118fab865ed6fe9a7f1f1d6a7255d907daf4fc2d1850ed4c5023`
- `docs/STAGE2_COMPLETION_REPORT.md` — `b76a76c0491e71c3839d65f1bbe6443795ec51bf1600ed1793bea84f06ee5cce`
- `docs/STAGE2_G2_REVIEW_20260909.md` — `cc90716ed085b5d38d3fa78c93dc0dfa367b5e6efe58cbaa2b5a0f321a30af29`
- `docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` — `9f61fd7347ed78e4329647768b88a93636c1bb9da395b18245daa13a7550c62a`
- `literature/EXPLORATORY_VALIDATION_REVIEW_20260909.md` — `53177bc96c363986325841f3636bd1adb64f90431c8aec2855230888a232ee2e`
- `docs/EXPERIMENT_PROTOCOL.md` — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty)
