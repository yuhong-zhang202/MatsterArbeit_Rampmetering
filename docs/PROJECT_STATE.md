# Project State

**Last updated:** 2026-09-13
**Document role:** Current project snapshot. Replace stale operational information instead of using this file as a decision history.

## Current Phase

**Current Stage 6 state, 2026-09-13:** SG6-P was explicitly approved with the bound card/payload/policy; D1 passed after one registered technical retry, and D2 ML17/C17 completed. Independent raw-XML reconstruction and scientific review accepted a qualified `not_resolved` result: 69/74 seed17 required rules passed, five failed, and all seven registered sensitivity combinations failed. The approved early-stop rule prohibits starting seed23 under that card. SUMO usage is 4/6 starts (2 validation, 1 shared retry used), 38.306105 budget seconds and 223,178,564 budget bytes; netconvert/TraCI/GUI are zero. No further launch is currently released. Detailed D1/D2 chronology remains in WORKLOG and the immutable receipts.

**Acceptance and scientific limits:** SG6-R negative closeout remains pending user acceptance. H2 restored actual upstream traversal and observation, but the bounded registered joint suitability test failed. This does not establish absence of mainline impairment elsewhere, structural impossibility, or absence of control benefit. Formal design remains locked under the accepted Stage 6 sequence. The unsent Robert brief is a proposed consultation route, not a requirement to stop all diagnostic work.

**Latest user instruction and reassessment:** The user requested an Astra review of whether to stop or pursue a defensible solution and a written solution if available. Engineering/data review preserves the old-card stop while identifying concrete gaps: the priority-junction ramp movement conflicts with both M movements, the registered feeder excludes the near-merge end and internal segment, and R passage is heavily delayed into Post. The whole-B passage counts are 9/12, while the registered per-bin-certain sums are 8/11. The proposed recovery plan is `docs/STAGE6_ASTRA_REASSESSMENT_AND_RECOVERY_PLAN.md`; its effectiveness remains unverified. No new simulation, candidate implementation, changed threshold or Robert message was authorized by this review request.

**2026-09-13 independent re-review:** The user asked whether Stage 3/5 should be accepted; this is not recorded as T54 acceptance. Fresh raw-XML reconstruction retained the historical Stage 3 results. Four fail-closed defects were repaired with 33/33 offline tests and 15 rejected malformed-input cases; reanalysis of the fixed eight archives produced 96/96 byte-identical products. The review corrected missing evidence-ID mappings, disclosed five unpaired seed-contrast keys, and narrowed `specific_obstacle` to a bounded intended-use evidence gap, not a demonstrated structural cause or absence of mainline impairment. The current review and proposed acceptance are `docs/STAGE3_STAGE5_ASTRA_REVIEW_20260913.md` and `docs/EXPLORATORY_VALIDATION_T54_ACCEPTANCE_PACKAGE_REVISION_02.md`; they qualify the historical Stage 3/5 summaries below. Scientific review recommends accepting the revised package, with no open Blocker/Major for the bounded historical assessment. T54 remains pending user acceptance; later Stage 6 A archive analysis does not retroactively constitute T54 acceptance. No new simulation occurred in either review.

Preparation for the interim presentation: Stage 1 and the core literature/measurement-knowledge gate are complete. Stage 2 S0–S2, revised G1 D0–D7, targeted S3–S5 measurement validation and completion-plan C0–C5 are complete. The user explicitly approved G2 and closed Stage 2 as a finite uncontrolled diagnostic milestone; acceptance is recorded in `docs/STAGE2_COMPLETION_REPORT.md`. Broader exploration and formal-design readiness are not thereby complete. C17 and seven new C/ML/MH/RL runs are hash-archived. All seven new runs completed with SUMO/netconvert 1.26.0, zero retries or registered technical anomalies, full six-E1 coverage and eventual completion of all planned vehicles; 7/8 authorized starts were used. Archive-only revision_04 independently reconciled 232 files, 14,564 vehicles, 4,320 E1 rows, 4,200 R merge-bracket endpoints and 198 same-seed contrasts; 25 offline tests and final scientific review passed. Every run cleared by 2700 s but retained R/U insertion after demand end, so the post period is not a zero-inflow recovery design.

No formal experiment protocol is frozen, and no formal thesis experiment has started.

The user authorized staged execution of `docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` on 2026-09-12, subject to its internal gates. Stage 3 archive-only diagnosis is complete with zero SUMO/netconvert starts. All 8 runs, 40 question units and G01–G07 passed after independent reconstruction and scientific review; the final report is `docs/STAGE3_BASELINE_DIAGNOSTIC_REPORT.md`. Q1 observability and Q3 shared R/U stopped exposure are supported within the synthetic scaffold, while Q2 freeway-side impairment and Q4 the intended two-sided trade-off remain `not_identified`. This is not formal evidence and does not freeze any experiment setting.

Stage 3 selected the conditional Stage 4 branch. On 2026-09-12 the user authorized T42 and then explicitly authorized T43 with “批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。” Tier 1 selected `run_q3650`; QM3650S17/S23 then completed sequentially. All four registered runs exited 0, have 29/29 archived files and passed 7/7 engineering audits; no retry occurred. Actual SUMO/netconvert/TraCI/GUI counts are 4/4/0/0; q3350 and all other points have zero starts. Tier-2 independent reconstruction matched 2,342/2,342 fields. The traceability Major was repaired with immutable snapshot SHA-256 `f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516`; snapshot-bound production/independent tests passed 116/116. Final scientific review passed, closed S4-FINAL-M01, reported open Blocker/Major/Minor 0/0/0 and accepted `supports_B_pattern_within_registered_points` within its strict exploratory scope. T43 and Stage 4 are closed; `docs/STAGE4_TARGETED_VALIDATION_REPORT.md` is the human-readable report. The review decision is recorded in `data/processed/stage4_qmain_sequential_20260912_v1/verification/T43_final_scientific_review_record_20260913.json` (SHA-256 `b73513dca5a0b535a8910ff4c779f410a13f0b165391b503b6e70c0475469726`) without changing the immutable evidence snapshot. Stage 5 T50–T53 are complete: O1–O6 are 6/6, G01–G08 have 8/8 passing completion results, 22/22 handover classes are qualified, T51 has open Blocker/Major/required Minor 0/0/0, and `docs/EXPLORATORY_VALIDATION_REPORT.md` recommends `completed / specific_obstacle` with `preliminary_ready=false`. T54 user acceptance is pending, so Stage 5 is not yet closed. Stage 6 A–D subsequently completed through the registered D2 early stop; this does not retroactively close T54. No ramp controller, formal protocol or Robert communication has been authorized.

The independent G2 re-review is recorded in `docs/STAGE2_G2_REVIEW_20260909.md`. Stale current-state and attempt-level analysis statuses were corrected; supplemental raw-data verification was saved and passed. No Blocker/Major was found for the finite diagnostic scope. The user has now accepted G2; baseline suitability for a formal ALINEA comparison remains unresolved.

The user-authorized bounded measurement repair is complete: internal-lane FCD accounting is supplemented, each E2 observes its own named lane with loaded coverage verified, and one matched technical regression retained identical traffic records. All 17 tests and the scientific review's five measurement checks passed within this technical scope. Road geometry, signal timing, behavioral parameters and formal storage/timing definitions were not changed. The subsequent Stage 2 C0–C5 work is complete and G2 is user-accepted; formal storage and timing selection remain unresolved.

The local technical environment and the fixed upstream ALINEA example have completed a technical smoke test. This technical evidence remains preliminary and does not change the formal experiment status.

The project-owned minimal uncontrolled freeway–ramp–urban scenario has also completed headless technical validation. It is a working technical scaffold only: all geometry, traffic demand, signal timing, duration, and seed values remain placeholders, and neither the low-load nor stress run is eligible for capacity analysis or thesis evidence.

A detailed bilingual analysis of the core `sumoITScontrol` paper has been completed under `literature/`. It identifies reusable controller and experiment-design concepts while keeping all project-specific routes and parameters provisional.

## Current Technical Environment

**Formal layered project memory is now established.** The user authorized importing the bounded reviewed project materials through a separately billed OpenAI API key. Tencent MemoryCore volume `tdai-ramp-metering-memory-v1`, service ID `ramp-metering-formal-memory-v1` and fixed team/agent/user identity persist L0=4, L1=6, L2=1 and L3 present. A fresh network-disabled container retrieved and semantically verified all four layers. Use `node scripts/memory/read_formal_memory.mjs` for a compact check and `node scripts/memory/read_formal_memory.mjs --full` for L1, the full L2 scenario body and L3. Project `.codex/config.toml` now exposes the same fixed read through an on-demand `read_project_memory` MCP tool; Codex recognized the server and a real network-disabled MCP-path recall passed. Current repository documents remain authoritative. This is not the official full MemoryProxy route: incremental capture, automatic per-turn injection, Hub business assets and automatic completed-session archiving remain unimplemented. See `docs/memory/OFFICIAL_CODEX_INTEGRATION_AUDIT_20260909.md`.

The user explicitly rejected routing ordinary Codex conversations through separately billed OpenAI API inference. Keep the Codex Pro/subscription provider unchanged. Memory recall remains an explicit local read with no model call. Do not proactively prepare or perform a memory update when a task or milestone ends; only begin the delta-package and approval workflow when the user explicitly asks to update Tencent memory. Any GPT API use then requires a disclosed file list, request/cost ceiling and fresh user approval. Automatic per-turn Proxy capture/injection is intentionally out of scope under this boundary.

The guarded manual incremental-update path has completed its first approved milestone update. It requires a unique session/update ID, an exact-hash `user-approved` manifest under `docs/memory/`, fixed project identity/model/request limits, an explicit per-run attempt cap and a non-existing receipt. Its dry-run path does not access Keychain, Docker, network, models or MemoryCore. Future paid updates remain unauthorized until the user requests an update, reviews its delta and complete L3 candidate, then approves that exact manifest and budget.

On 2026-09-10 the user first authorized local dry-run preparation, then explicitly approved the exact Stage 2-closeout delta/L3 hashes, `gpt-4.1-mini`, three-call ceiling and USD 0.0436608 ceiling. Update `stage2-closeout-20260910-v1` passed: L0 4→8, L1 6→9, L2 remained one document with changed content, and the reviewed complete L3 was written. A fresh network-disabled read returned all layers. Three calls used 13,052 prompt and 908 completion tokens; the receipt's conservative approved-rate estimate is USD 0.0066736, below the ceiling. Combined attempts are now 9/41 with 32 remaining. The exact receipt is `data/processed/memory_incremental_stage2-closeout-20260910-v1/receipt.json`. L1 contains three bounded new memories. Generated L2 correctly records Stage 2 closure but adds broad user-trait language and compresses decision timing; treat it as non-authoritative navigation only. L3 and repository documents carry the reviewed scientific state.

The formal seed normalized five authorized files with recorded hashes. GPT `gpt-4.1-mini` generated L1 and L2 through the native pipeline. The automatic L3 continuation did not complete under the 20,000-byte proxy gate after L2; the reviewed 3,921-character core summary was therefore written deterministically through MemoryCore's official `/v3/core/write` endpoint in a network-disabled container. Do not claim that L3 was GPT-generated. Six total model attempts are preserved across two ledgers: four zero-token failures (three invalid-key 401 responses and one inaccessible fixed-snapshot 403 response) plus two successful alias-model calls using 8,582 prompt and 1,322 completion tokens. Estimated token charge at the published rates is USD 0.005548; 35 of the original combined 41-attempt ceiling remain. The fixed snapshot ID was not visible to this API project, while the stable `gpt-4.1-mini` alias returned 200. Detailed evidence is in `docs/memory/FORMAL_PROJECT_MEMORY_20260909.md`.

The earlier dated auxiliary handoff remains in separate Docker volume `tdai-ramp-metering-snapshot-20260909`. Read it with `node scripts/memory/read_snapshot.mjs`; it is retained as historical fallback and is not the formal layered instance. Neither memory route changes Codex's provider configuration or accesses the separate LingoBridge volume.

- macOS 15.3 on Apple Silicon (Apple M3, arm64).
- SUMO and `sumo-gui` 1.26.0 from the EclipseSUMO macOS Framework.
- Session-level `SUMO_HOME`: `/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo`.
- Project `.venv`: Python 3.13.0 with `sumoITScontrol` 0.1.0, TraCI 1.26.0, and sumolib 1.26.0.
- Fixed upstream smoke-test source: `sumoITScontrol` tag `v0.1.0`, commit `5776c6c79a888a37e55079db63eedc7db0570863`.

## Technical Smoke-Test Status

- Static input, checksum, import, and dependency validation passed.
- The ALINEA GUI run completed with reliable SUMO-generated visual evidence: at simulation time 600 s the scene contained 47 vehicles and traffic light `J0` reported state `G`.
- The completed GUI run executed 8,400 simulation steps, called `execute_control(...)` 8,400 times, and recorded 69 controller updates.
- Headless runs with seeds 2 and 3 both exited with status 0 and completed the same 8,400-step control chain.
- All runtime models, detector XML files, summaries, and GUI evidence were written under `/private/tmp`; no smoke-test output was written to `data/raw/` or used as thesis evidence.
- The upstream example emits technical warnings, including missing yellow phases, vehicle `tau` below the simulation step, collision teleports, emergency braking, and use of the deprecated TraCI `getCurrentTime()` API. These warnings did not prevent the smoke test from completing, but the upstream example must not be reused as a formal experiment configuration without separate review and correction.

## Project-Owned Minimal Scenario Status

- The scenario contains a two-lane freeway, one entrance ramp, a fixed-time upstream urban signal, and separate `M`, `R`, `U`, and technical cross-traffic `X` routes.
- `R` and `U` share a one-lane urban approach before diverging, so a persistent ramp queue can cross the finite-storage boundary and physically obstruct `U` traffic.
- Static validation, network construction, route checks, vehicle accounting, output-ID consistency, signal-state checks, and two headless integration runs passed with SUMO 1.26.0.
- The corrected merge geometry produces no `netconvert` warning and no artificial connection-speed reduction. Both headless runs reported no SUMO warnings, collisions, teleports, emergency-braking warnings, or route errors.
- In the low-load technical run, all 330 planned vehicles entered the network and no stopped `R` vehicle was observed beyond the finite-storage boundary.
- In the deliberately overloaded stress run, `R` and `U` were simultaneously stopped on the shared approach for 607 one-second steps, demonstrating that the intended physical spillback mechanism can be triggered. Only 1,035 of 1,235 planned vehicles entered the network, including approximately 49% of planned `R` and `U` vehicles; the run therefore cannot support capacity, breakdown, performance, or sweet-spot conclusions.
- Both profiles explicitly report `capacity_analysis_eligible=false`. The technical checks distinguish successful execution from complete demand insertion and scientific usability.
- Automatic `sumo-gui` snapshot attempts exited normally but produced unusable images, so visual network inspection remains unverified. This does not invalidate the headless technical checks, but visual inspection should be completed before relying on a scenario diagram or interpreting detailed geometry.

## Stage 1 Instrumentation Status

- Four lane-specific E1 detectors now observe the freeway immediately upstream and downstream of the merge at a technical 30-second aggregation period.
- `qMain` and `qRamp` can be supplied as paired command-line inputs; `qUrban=360 veh/h` and technical cross traffic `qX=180 veh/h` remain fixed placeholders.
- Each run reports requested demand, planned vehicles, actual departures and insertion rates, arrivals, vehicles still in the network, and vehicles not inserted.
- The output separately reports eligibility for fixed-window detector description, vehicle-outcome interpretation, and capacity analysis. A passing technical execution check is not treated as scientific eligibility.
- Independent validation confirmed the E1 flow, speed, occupancy, `nVehContrib`, and `nVehEntered` summaries against the raw XML.
- Low and custom technical runs passed the fixed-window detector-description gate but failed the vehicle-outcome gate because at least one vehicle class exceeded the provisional end-truncation limit. The stress run failed both gates because of incomplete insertion and severe truncation. All runs remain `capacity_analysis_eligible=false`.
- Nine unit and real headless integration tests pass. Stage 1 is closed only as technical infrastructure; it establishes no Breakdown, Capacity Drop, capacity, causal urban-loss, or sweet-spot result.

## Stage 2 Exploratory Timing Checks

- Warm-up, measurement and post-demand clearance are now configurable separately. Their durations are not selected or frozen.
- Five preliminary runs used seed 17 only. All scheduled vehicles eventually entered and arrived, but this does not establish that scheduled demand was realized during measurement.
- Independent raw-output validation found that the `qMain=3200/qRamp=720 veh/h`, 600/600/900-second run inserted only 26 ramp-bound vehicles during measurement (156 veh/h); 94 ramp-bound and 47 urban-through vehicles entered only during clearance. The original final-insertion gate therefore cannot establish demand-window realization.
- Clearance stops new scheduled demand; vehicles already waiting outside the network can still enter. In-network travel time alone omits this departure delay.
- Timing alternatives changed several durations and total demand together. They are diagnostic runs, not controlled evidence selecting a duration. Follow-up uses different observation windows on the same retained trajectory, without new simulation runs.
- A 600-second warm-up excludes the first observed stopped ramp-bound vehicle on the shared approach at 412 seconds and the first stopped urban-through vehicle there at 414 seconds in the high-demand baseline. These events are not automatically startup artifacts. Local queue flattening or stable freeway speed does not establish global stability.
- Independent reaggregation of the longest retained trajectory (`/private/tmp/minimal_uncontrolled_eozyn46f`) found ramp-bound waiting-to-insert counts of 43, 95 and 150 at 900, 1200 and 1500 seconds, respectively (urban-through: 22, 48 and 75), despite similar mean freeway speeds across nested windows. Demand ended at 1500 seconds, the last vehicle entered at 2245 seconds and the last arrival was at 2401 seconds. These are single-trajectory diagnostics, not recommended durations or independent replications.
- No freeway Breakdown, Capacity Drop, causal urban loss or sweet spot has been established. Static compiled-geometry review and a bounded 390–430 s saved-trajectory replay are complete. The replay passed independent record reconciliation and browser interaction checks; broader dynamic inspection and live GUI validation remain outstanding. All outputs remain exploratory, with no formal protocol frozen.
- The corrected reporting separates final insertion completeness from demand-period realization (`not_evaluated` because no acceptance criterion is approved); overall quality is not fully evaluated. All five corrected summaries passed final consistency validation, with independent raw-data validation and scientific-semantics review completed. Detailed provenance and the same-trajectory comparisons are recorded in `docs/STAGE2_TIMING_DIAGNOSTIC.md`.
- A subsequent read-only queue-origin diagnostic is complete: in the longest trajectory, first stopped ramp vehicles occurred at the acceleration-segment end (46 s), storage segment (192 s), and shared approach (412 s); a stopped urban vehicle followed on the shared approach at 414 s. Compiled priority connections and representative vehicle tracks support an upstream-propagation interpretation, not a formal causal effect or freeway Breakdown claim. Low demand also has repeated merge-end stopping, but no storage/shared-approach stopped vehicles or ramp/urban insertion backlog.
- Scientific review identified a prerequisite for further storage interpretation: the compiled path from the shared boundary to the ramp end includes 113.08 m and 81.98 m internal lanes, 204.49 m of `ramp_storage`, and 95.32 m of `ramp_accel` (494.87 m total). Neither the named storage edge alone nor the full path length is an approved effective queue-storage capacity. Actual geometry, allowed storage and observation coverage must be checked visually before selecting storage or timing parameters. This does not establish a network error; no configuration has changed.
- The final static geometry figure (`results/figures/stage2_geometry_20260909_v4.png`) has passed primary visual inspection and scientific review. Versions before v4 are superseded. The subsequent authorized repair adds explicit internal/external FCD groups and verifies new E2 coverage of 0–238.80 m on the shared lane and 0–204.49 m on the storage lane. Legacy 250 m E2 successor coverage remains unverified; legacy E2 values are not directly comparable to the repaired observations. Authoritative accounting v2 and paired semantic comparison v3 are under `data/processed/stage2_internal_accounting_20260909/`; earlier mixed instantaneous accounting fields are superseded, not deleted. See `docs/STAGE2_TIMING_DIAGNOSTIC.md` for provenance and limitations.

## Current Working Topic

Use SUMO and `sumoITScontrol` to investigate the sweet spot of freeway ramp metering: the balance between preventing congestion on the freeway and avoiding queue spillback into the connected urban road network.

**Status:** `Supervisor-supported working direction — final research question and scope remain to be refined before registration`

## User-Endorsed Provisional Research Framework

The user has approved the following provisional framework for continued preparation:

- retain the ramp-metering sweet spot as the main research focus: the balance between protecting freeway operation and avoiding persistent queue spillback into the connected urban network;
- distinguish freeway-mainline (`M`), ramp-bound (`R`), and urban through-traffic (`U`) in the initial system concept;
- treat `qMain × qRamp` as the common demand-condition backbone, not as the sweet spot itself;
- conceptualize the sweet spot as an acceptable control-outcome region, rather than a unique point, in which minimum freeway and urban protection requirements are met before comparing system-wide loss;
- use an evaluation-oriented scope: uncontrolled baseline, standard ALINEA, and only if the explored conflict is present, a simple and transparent urban-protection override;
- treat the override as an intervention for examining or improving the sweet spot, not as the thesis topic itself;
- accept that the explored conditions may show no need for an override or no feasible sweet-spot region.

These items are user-approved provisional directions recorded in `docs/DECISIONS.md`. They are not supervisor-confirmed or frozen. Robert Hilbrich still needs to confirm the formal sweet-spot concept, contribution scope, research-question wording, and final experimental design.

## Current Supervision Situation

- **Robert Hilbrich:** Current day-to-day supervisor. In the reply received on 2026-08-25, he supported the overall working direction, initial framework and controller choice, deliberately simple synthetic scenario, and uncontrolled demand-grid starting phase.
- **Kai Nagel:** Expected to participate in the interim presentation and final defense, as reported by the student.
- **Peter Wagner:** Originally proposed and supervised the topic but is no longer able to continue supervising for health reasons, as reported by the student. His earlier emails remain historical project guidance and do not constitute Robert Hilbrich’s approval.

## Historical Research Starting Point Confirmed by Peter Wagner

Peter Wagner explicitly recommended:

- reading the `sumoITScontrol` paper and getting its algorithm implementation to run;
- beginning with a synthetic SUMO example;
- scanning `qMain` and `qRamp`;
- examining travel times, speeds, densities, and capacity limits;
- adding a ramp-metering algorithm after establishing the uncontrolled baseline;
- checking whether control improves the uncontrolled case;
- paying particular attention to effects in a connected urban road network;
- determining the urban-network details later through discussion;
- examining real German examples while remaining cautious about the difficulty of obtaining and using real data.

These points are historical guidance from Peter Wagner. They are not equivalent to confirmation by the current supervisor.

## Current Supervisor-Supported Starting Concept

The current supervisor-supported starting concept is to:

- use `sumoITScontrol` as the initial framework and ALINEA as the first controller;
- build a deliberately simple synthetic system containing one freeway, one entrance ramp, and a small upstream urban network with an initially fixed-time traffic signal;
- scan the uncontrolled `qMain × qRamp` demand space first and inspect behaviour around traffic breakdown;
- compare uncontrolled and controlled cases under matched conditions after establishing the baseline;
- begin with SUMO's standard Krauß car-following model and default parameters rather than forcing behaviour without empirical calibration data;
- check whether the scenario produces plausible breakdown and capacity drop, then investigate car following, lane changing and merging, ramp geometry, and demand if it does not;
- configure and validate vehicle insertion so realized high demand is not capped by insertion settings, using `departPos="last"`, `departLane="best"`, and `departSpeed="max"` as starting guidance;
- focus the research refinement on when metering should be reduced or overridden to avoid spillback into the subordinate network despite freeway capacity pressure.

This establishes a working direction, not a frozen scientific design. Exact geometry, demand ranges, metrics, seeds, controller settings, override rule, and formal sweet-spot definition remain unresolved.

## Recorded Decisions

`docs/DECISIONS.md` records the user-approved provisional research directions and the preparation sequence: complete Stage 1, then pause for the core literature gate, and only afterward begin Stage 2 representative uncontrolled checks.

None is supervisor-confirmed or frozen, and none establishes a formal experiment parameter.

## Formal Experiment Status

- No formal experiment protocol is frozen.
- No formal experiment batch has started.
- Environment checks, official examples, exploratory runs, and smoke tests are not formal thesis experiments.
- Outputs from such preliminary runs must not be presented as thesis evidence.

## Pending Research and Organizational Clarification

The following issues still require project development, discussion, or institutional clarification:

- the final research-question wording and title proposals for the interim presentation;
- whether Robert Hilbrich accepts the evaluation-oriented contribution and the main-question/sub-question hierarchy;
- whether Robert Hilbrich accepts an acceptable-region sweet-spot concept based on minimum freeway and urban protection requirements followed by system-loss comparison;
- whether plausible breakdown and capacity drop emerge from the initial Krauß-default scenario;
- the formal definition, metrics, and robustness requirements of the sweet spot;
- the exact geometry and storage of the ramp and the small connected urban network;
- whether urban demand and ramp storage become primary experiment dimensions or sensitivity conditions;
- the formal experimental parameters, ranges, and replication design;
- the formal override logic for protecting the subordinate network;
- confirmation from the chair or examination rules that the thesis may be written in English;
- the exact date of the interim presentation and subsequent registration.

## Current Blockers and Boundaries

Robert Hilbrich's reply removes the previous scope-response blocker and supports proceeding with the simple scenario and initial uncontrolled exploration.

The final research question, formal parameters, metrics, replication design, and override rule remain unresolved, so the scientific design and experiment protocol must not yet be frozen.

There is no remaining blocker to reproducing the fixed upstream smoke test or the project-owned headless minimal-scenario check. The upstream demo warnings remain technical limitations, and visual inspection of the new scenario remains incomplete because the automatic GUI snapshots were unusable.

## Work That May Proceed Now

- maintain the local project structure and collaboration rules;
- archive original project and supervisor materials;
- use the completed core-paper analysis and continue reading the official documentation needed for project-owned scenario design;
- review the upstream ALINEA example warnings and decide the smallest technically defensible corrections for a future project-owned scenario;
- build the deliberately simple project-owned freeway–ramp–urban scenario using reversible, documented choices;
- perform environment checks, scenario validation, and explicitly exploratory uncontrolled runs to establish whether intended demand is realized and plausible breakdown and capacity drop occur;
- repeat the fixed environment check or smoke test when tool versions change.

## Work Deferred Until Formal Design Approval

- formal or thesis-evidence demand-grid experiments;
- formal data production;
- freezing `docs/EXPERIMENT_PROTOCOL.md`;
- treating default model parameters as scientifically justified choices;
- drawing thesis conclusions from preliminary runs;
- large-scale drafting of results or discussion chapters.

## Next Actions

The subsequent Robert-oriented review, including all three durations, is recorded in `docs/STAGE2_G1_REVIEW_20260909.md`. The user-approved targeted S3–S5 is complete; final evidence is in `docs/STAGE2_S3_S5_VALIDATION_REPORT.md`. Two observation-only E1 loops on the M-only internal merge lanes loaded successfully in SUMO 1.26.0. One matched run completed at `/private/tmp/minimal_uncontrolled__5s3s06d`; actual SUMO starts were one and technical retries zero. FCD, tripinfo, TLS, vehroute and the old four E1 outputs were semantically unchanged from the reference. Scientific review accepts the new aggregate merge-entry measurement within its declared scope, with per-vehicle E1 completeness still not verified. Breakdown and Capacity Drop remain not established. Retain 0/1500/1200 only as a finite-horizon candidate. The old six-row G1 package remains superseded and unauthorized.

S0–S2, revised G1 D0–D7, targeted S3–S5 and completion-plan C0–C6 are complete. The user accepted G2 with the words “批准 G2，正式关闭 Stage 2。” The approved C/ML/MH/RL matrix and processing are complete; seven new starts were used and no retry was needed. No additional run, point, seed, timing change, threshold or research definition is approved.

1. Preserve the qualified Stage 6 D2 `not_resolved` outcome and old-card stop. Seed23 remains unexecuted; no unused budget is released. T54 and SG6-R negative closeout retain their existing pending user-acceptance status.
2. The latest user authorized the Astra reassessment and written recovery proposal. The proposed route is `docs/STAGE6_ASTRA_REASSESSMENT_AND_RECOVERY_PLAN.md`: P0 archive-only topology, ramp-supply, local-mainline and gate-dependency diagnosis; P1 one justified candidate; P2 only under a new approved exact card. The full P0 implementation is proposed, not already completed by this limited review.
3. Correct interpretation: whole-B certain R passages are ML9/C12; registered per-bin-certain sums are 8/11. TT intervals are measurement bounds, not statistical confidence intervals; failed conservative10% evidence does not establish a true effect below10%. These corrections do not change old machine rules.
4. Consult Robert with a concrete mechanism diagnosis and proposed alternative; offline diagnosis need not wait for a reply. New geometry implementation, network builds and simulation require their applicable user-approved plan/card. Sending the brief, changing the research scope, and freezing the protocol remain unauthorized.
5. Formal-design drafting remains locked by the current Stage 6 sequence until a newly supported baseline receives the applicable scientific and user acceptance. Do not treat the former generic permission to draft while exploring as overriding that later instruction.
