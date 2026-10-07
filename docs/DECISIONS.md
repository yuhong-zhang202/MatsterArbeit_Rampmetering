# Research and Implementation Decisions

This file records choices explicitly approved by the user. A user-approved item is not automatically supervisor-confirmed or frozen. Formal experiment settings belong in `EXPERIMENT_PROTOCOL.md` and remain unset until separately authorized.

## D-001 — Evaluation-oriented thesis scope

- **Date:** 2026-08-31
- **Status:** `User-approved — provisional, pending Robert Hilbrich confirmation`
- **Decision:** Keep the ramp-metering sweet spot as the main research focus. Use ALINEA as the first controller and treat a simple urban-protection override only as a possible intervention for studying the sweet spot. Do not make complex controller development a core requirement unless Robert considers the evaluation-oriented contribution insufficient.
- **Boundary:** This does not establish the final research question, thesis title, controller implementation, or formal experiment design.

## D-002 — Provisional sweet-spot concept

- **Date:** 2026-08-31
- **Status:** `User-approved conceptual direction — pending Robert Hilbrich confirmation`
- **Decision:** Treat the sweet spot as a potentially non-empty acceptable region rather than a unique point. At a high level, candidate control choices must protect both freeway and urban-network performance to minimum acceptable levels; system-wide loss may then be compared within that region. A full Pareto analysis is not currently required.
- **Boundary:** Protection metrics, thresholds, weighting, robustness rules, and the formal definition remain unresolved. The sweet spot is a control-outcome concept conditional on demand and network conditions, not simply a favourable point in the `qMain × qRamp` demand plane.

## D-003 — Provisional minimal urban-spillback mechanism

- **Date:** 2026-08-31
- **Status:** `User-approved exploratory starting mechanism — not frozen`
- **Decision:** For the first project-owned scenario, distinguish freeway-mainline traffic (`M`), ramp-bound traffic (`R`), and urban through-traffic that does not use the freeway (`U`). Use a simple shared urban approach and downstream divergence so that a persistent ramp queue can cross the finite-storage boundary and impose measurable additional effects on `U` traffic.
- **Boundary:** Exact topology, lanes, lengths, traffic-signal placement, demands, queue definitions, detectors, and parameters remain proposed technical choices. The scenario must first be validated as exploratory work.

## D-004 — Preparation workflow before Stage 2

- **Date:** 2026-08-31
- **Status:** `User-approved workflow sequence`
- **Decision:** Complete Stage 1 technical instrumentation first, then pause simulation work to complete the core literature and measurement-knowledge gate, and only afterward begin Stage 2 with a few representative uncontrolled conditions.
- **Boundary:** This sequence does not approve Stage 2 demand values, measurement windows, clearance handling, Breakdown or Capacity Drop definitions, seeds, formal exclusion rules, or a full demand grid.

## D-005 — Scoped adoption of Stage 6 exploratory ramp-induced witness contract

- **Date:** 2026-09-23
- **Status:** `User-approved — Stage 6 exploratory pair only`
- **Decision:** Adopt `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md` for the exploratory matched pair `PAIR3199_CTRL_S17` + `PAIR_3199_R720_DELAYED_S17` only.
- **Boundary:** This is not part of `docs/EXPERIMENT_PROTOCOL.md`, does not alter the existing control's `NOT_EVALUABLE` status, fixed-screen failures, or low-speed/C warning history, and does not declare the control a clean normal baseline. It does not change the locked classifier, thresholds, scientific inputs, or authorize any treatment start. The treatment still requires its separately authorized resource contract and single-start approval.

## D-006 — One authorized PAIR3199 delayed-R treatment start

- **Date:** 2026-09-23
- **Status:** `User-approved — consumed`
- **Decision:** Authorize exactly one start of `PAIR_3199_R720_DELAYED_S17` from exact card `artifacts/stage6_pair_3199_s17_preparation_20260923_v1/PAIR_3199_R720_DELAYED_S17_CARD_FINAL_REV1.json`, SHA-256 `08160a2ad225ee9fcc2abcc11d509a88ecf554252f1fb17e35dc69b9404351d4`, with 120 s wall-clock and 90,000,000-byte output stop triggers, 100 ms output polling, slight polling overshoot accepted, and no retry.
- **Boundary:** This authorization is consumed by the completed single start. It covers no other demand, seed, controller, retry, or future run; it does not modify the formal protocol or any scientific input.

## D-007 — Scoped adoption of Stage 6 witness contract Amendment V1

- **Date:** 2026-09-24
- **Status:** `User-approved — Stage 6 exploratory retrospective sensitivity analysis only`
- **Decision:** Adopt `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_AMENDMENT_V1.md` for the existing `PAIR3199_CTRL_S17` + `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1` raw comparison, labeled `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS`.
- **Boundary:** The parent contract and all historical `NOT_EVALUABLE` dispositions remain unchanged. P/S/L thresholds, Candidate A/C rules, event window, classifier and formal protocol remain unchanged. Adoption provides no simulation authorization and does not make a formal experiment decision. Any sensitivity result must retain its retrospective label.

## D-008 — Scoped adoption of Stage 6 second-tier stress escalation plan

- **Date:** 2026-09-24
- **Status:** `User-approved — Stage 6 bounded exploratory existence validation only`
- **Decision:** Adopt `artifacts/stage6_second_tier_stress_escalation_plan_20260924_v1/SECOND_TIER_STRESS_ESCALATION_PLAN.md` as the conditional second-tier branch after the currently authorized minimal qMain=3350.4 matched pair, subject to its independent review and stop rules. The plan was adopted before the minimal3350 treatment outcome was known.
- **Boundary:** Complete the 3350.4 R=0 control and, only if independently classified `LOW_R_BACKGROUND_ACCEPTABLE`, its matched delayed-R720 treatment first. Only an acceptable control plus a valid exposed `NO_WITNESS` pair may enter the adopted extension. A witness, self-congested control, `NOT_EVALUABLE`, or failed exposure scaling stops the scan. The extension is not part of `docs/EXPERIMENT_PROTOCOL.md`; no formal parameters are frozen. Geometry, vehicle behavior, classifier, thresholds and witness rules remain unchanged. Future exact cards, resources and required prelaunch reviews remain bound by the plan and user instructions.

## D-009 — Scoped adoption of CLEAN_ONSET_WITNESS_TEST

- **Date:** 2026-09-25
- **Status:** `User-approved — Stage 6 exploratory validation only`
- **Decision:** Adopt `artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/CLEAN_ONSET_WITNESS_TEST.md` (scientific review PASS_PLAN_ONLY, 0/0/0) as a separate bounded follow-up after the 3350/R900 `NOT_EVALUABLE` result. Its post-outcome origin must remain explicit; it is not formal protocol or preregistered before the 3350/R900 result.
- **Current authorization boundary:** Prepare Candidate A only: qMain3199.2, seed17, U=X=0, delayed R900 over `[540,1500)`, compared with the existing 3199/R0 control. This adoption authorizes preparation and prelaunch review only, not SUMO/Guardian/TraCI launch. The user has explicitly deferred R1080; no Candidate B preparation or execution is authorized now. Any run requires its own exact-card prelaunch PASS and explicit user execution authorization.
- **Plan boundary:** Reuse the existing `LOW_R_BACKGROUND_ACCEPTABLE` R0 control without calling it a clean normal baseline. Require all 1,333 M vehicles to match per vehicle; R240 is the only added exogenous demand. Before Candidate A release, freeze the existing 3199/R720 raw's unique first through-lane entry counts and extraction method at t=1440 and t=1500. Candidate B can be considered only after valid Candidate A `NO_WITNESS`, increased actual same-qMain merge exposure, and cleared alternatives, with separate user authorization. Absolute plan cap is two SUMO starts including technical failures. Locked classifier, 0.85 reference, P/S/L, geometry, vehicle behavior, historical results and formal protocol remain unchanged. D-009 is a scoped separate follow-up to the D-008 stop rule; it does not rewrite D-008's historical outcome or generalize its scope.

## D-010 — Scoped adoption of Candidate A T3 method clarification

- **Date:** 2026-09-25
- **Status:** `User-approved — Stage 6 exploratory retrospective sensitivity analysis only`
- **Decision:** Explicitly adopt `artifacts/stage6_clean_onset_3199_r900_t3_recheck_20260925_v1/T3_METHOD_CLARIFICATION_PROPOSAL.md` (SHA-256 `2fb81e792d54cd3361a5e02599deeca3f9dad2244b465b09829e9fc852fb15a7`) for the already existing `CLEAN3199_A_R900_DELAYED_S17` raw. The independent scientific recheck found 0/0/0 required package issues and `PASS_T3_RECONSTRUCTION_HOLD_OUTCOME` before adoption. This clarification arose after the run because auxiliary E1 at 20 m missed R vehicles that left the auxiliary lane before reaching it; E1 zero is not equivalent to no actual auxiliary entry.
- **Measurement and scope:** For a separately labelled `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS`, use the reviewed certain per-vehicle route-consistent auxiliary-entry reconstruction. T3 for this raw is 690 s. Preserve the literal D-009 E1-based rule and its historical `NOT_EVALUABLE / EXPOSURE_GATE_NOT_MET` receipt; no overwrite or retrospective claim of prospective preregistration. Keep E1 counts reported as detector diagnostics. This adoption authorizes offline continuation of the locked outcome and matched-control/alternative-cause review on the same raw only. P/S/L, 0.85 reference, event window, geometry, vehicle behavior and formal protocol are unchanged. No SUMO run, R1080, other qMain, seed23 or B/C is authorized.

## D-011 — Scoped adoption of PHENOMENON_LEVEL_ABC_GATE

- **Date:** 2026-09-26
- **Status:** `User-approved — Stage 6 exploratory validation only`
- **Decision:** The user explicitly adopted `artifacts/stage6_phenomenon_level_abc_gate_20260925_v1/PHENOMENON_LEVEL_ABC_GATE.md` (reviewed file SHA-256 `d202b0451d53b808202132f5d97213cba9eb75ffb6b196dc2c7869a21b201f3a`; independent scientific review `PASS_FOR_PROPOSED_STAGE6_EXPLORATORY_SCOPE`, open Blocker/Major/required Minor `0/0/0`) for Stage 6 exploratory evaluation of the measurable A/B/C phenomenon chain. Confirmed State1 is no longer the sole Stage 6 exploratory acceptance condition; P/S/L and the 0.85 onset reference remain diagnostics.
- **Boundary:** This adoption does not reclassify or overwrite historical P/S/L, `NO_WITNESS` or `NOT_EVALUABLE` results, does not change scientific inputs or `docs/EXPERIMENT_PROTOCOL.md`, and is not supervisor confirmation, formal experiment approval, a run authorization or permission to tune qMain/qRamp/controllers after outcomes. A separately reviewed bounded full-network A/B/C plan and any later exact-card/resource/execution authorizations are distinct steps.


## D-012 — Scoped exploratory capability closeout and formal-design handoff

- **Date:** 2026-10-03 (Europe/Rome)
- **Status:** `Rejected by user — superseded by D-013; historical scientific scoped-PASS retained`
- **Historical authorization interpretation (withdrawn):** The user requested checking the early criteria and, once satisfied, formally recording exploration ended and updating documents/Dashboard; clarified that the phase demonstrates thesis-relevant phenomena before large formal experiments and checks modelling-error alternatives, in light of Robert's latest reply; then explicitly requested “OK，请核对旧证据的适用性后重新评估结项”. The user subsequently explicitly rejected this limited closeout. It must not be treated as current user acceptance.
- **Historical closeout record (withdrawn):** Record current Stage6 scenario-capability exploration `COMPLETE_WITH_LIMITATIONS`, with formal experiment design next/not started. Engineering transfer12/12 checks confirm mechanism-relevant shared network/default/routes/city signals/insertion/detector semantics; independent oldV2 A/B22 raw recheck supports sharedR/U obstruction/internal cost; new18-run three-seed uncontrolled results support mainline critical-state capability. Final independent scientific review is `PASS_FOR_SCOPED_EXPLORATORY_CLOSEOUT`, no open material blocker for this purpose. Relevant evidence is in `docs/探索验证阶段/STAGE6_EXPLORATORY_CAPABILITY_CLOSEOUT_20261003.md`.
- **Scope:** Different operating conditions may support the two capability layers; identical demand or prior successful ALINEA/ABC/sweetspot is not required. D-011 retains its historical approval and unmet results, but is not the current capability-closeout prerequisite under the user's clarified purpose. No oldState1/T54/SG6-R result is retrospectively reclassified; originalRI3350 NOT_PAIRABLE/A_NOT_EVALUABLE remains. City evidence is single-seed, continuousall-connector spillback unproven, oldnonlocalM coupling unresolved; no newR900 city-effect prediction, quantified controller benefit or real-world calibration.
- **Execution boundary:** No further exploratory simulation is needed or authorized. Formal design/protocol parameters remain Proposed; EXPERIMENT_PROTOCOL is empty/unfrozen, formal runs not started. This closeout does not authorize a controller/pilot/formal run, freeze a protocol, send a message, update external apps or publish.


## D-013 — Current-version standard-metering validation required before exploratory closeout

- **Date:** 2026-10-03 (Europe/Rome)
- **Status:** `User-approved scope correction — design authorized; parameters Proposed and new runs not authorized`
- **Source:** The user explicitly said: “我希望在当前版本的基础上设计临界点的标准 ramp metering 比较，补充探索验证阶段的证据。不接受有限范围完成”.
- **Decision:** Restore Stage6 `PARTIAL / PLANNING_CURRENT_VERSION_CONTROL_VALIDATION`. The primary exploration evidence should be one coherent current-version series: existing uncontrolled demand localization, then matched standard ramp-metering comparison at a scientifically selected critical operating point. Historical fixed22/28ABC results remain method-development/history evidence and cannot replace the current controlled evidence required for acceptance. D-012's limited closeout is rejected.
- **Design scope:** Reuse valid current OPEN baselines, preserve network/default behavior/explicit vehicle attributes/request schedules/urbanTLS/windows, and compare standardALINEA with measured actuation and complete mainline/ramp/urban costs and queue exposure. Numeric choices, seed coverage and revised completion gates must be stated as Proposed and independently reviewed. The user has not required manufacturing ABC or guaranteed sweetspot success.
- **Boundary:** This authorizes design and current-state/document/Dashboard correction. It does not approve exact ALINEA parameters, implementation, simulation cards, a pilot/formal run, protocol freeze or thesis-structure changes. Formal protocol remains empty/unfrozen. Keep all original inputs/raw/results and scientific historical classifications; report negative/mixed results and unresolved evidence honestly.

## D-014 — Execute the bounded current-version standard-metering plan

- **Date:** 2026-10-03.
- **Status:** `User-approved execution direction — conditional sequential gates remain mandatory`.
- **Source:** User references STAGE6_CURRENT_VERSION_STANDARD_METERING_PLAN_20261003.md and explicitly requests “请严格按照该方案执行”.
- **Decision:** Implement and review S0/S1, then execute eligible S2–S4 technical/exploratory runs and S5 analysis/review under the plan. No repeated blanket permission is required for already specified steps once their release gates pass. Exact inputs/code/cards and implementation-specific service/crossing rules must be reviewed before the applicable start. Existing numerical candidates may be prospectively locked for this exploratory comparison only after their declared scientific/technical checks.
- **Boundary:** No formal protocol freeze or formal runs, no unreviewed parameter/model/demand change, automatic retry, cap reset, unconditional batch, guaranteed positive response or automatic exploration acceptance. The plan's failures/stops and full requested-cohort accounting remain binding. D-013's design-only permission describes the previous turn; this explicit new request expands permission to gated execution.

## D-015 — Repair technical failures and continue the authorized sequence

- **Date:** 2026-10-03.
- **Status:** `User-approved technical repair and gated continuation`.
- **Source:** User comments on “S17中性运行未能建立TraCI连接”: “技术问题的话，排查然后解决，非技术问题再停下”; then “解决完然后继续未完成的工作”.
- **Decision:** Continue root-cause diagnosis/minimal technical repair, appropriate no-SUMO regression tests and necessary bounded technical/replacement starts under new revision cards and independent releases, then resume incomplete S2–S5. The earlier no-automatic-retry rule prevents blind restart; it does not prohibit an explicitly authorized reviewed repair attempt.
- **Boundary:** Current19/40 total and1/8 control-technical counts are not reset; oldfailedraw/card preserved. No unreviewed scientific parameter/demand/model changes, formal freeze/runs or invented traffic result. If diagnosis cannot establish an appropriate repair, report what evidence is missing and design only the smallest discriminating technical check.

## D-016 — Technical repair starts recorded separately from experiment allowance

Date:2026-10-03. Status:User-approved, bounded resource-accounting correction. Source: user reply “技术故障排查和解决不占用次数”, followed by “解决后先尝试重试，避免不必要的测试浪费额度，重点放在仿真”.

Technical diagnosis/repair starts, including connection/measurement NOOP validation, are retained in the physical launch ledger but excluded from the experiment-start allowance. Prior failures are not erased or relabeled as completed experiments. Existing18 uncontrolled experiment starts remain counted; no controlled experiment has yet started. Future actual controller trials count as experiments, including failed controller starts unless explicitly technical and documented; classification cannot be based on whether results are favourable. Original per-run120s,250MB and shared8GB raw limits, matching, prelaunch review and sequential data/scientific gates remain. Avoid optional testing and unsupported blind retries; perform minimal necessary repair followed by a reviewed single technical retry. This explicit user resource correction supersedes D-015's technical-start cap conflict; no formal protocol change.

## D-017 — Design and execute a safe, rate-capable standard metering comparison

Date: 2026-10-03. Status: User-approved research direction and gated exploratory execution.

Source: The user references `STAGE6_SAFETY_AND_RATE_TRACKING_GPT_SOL_HANDOFF_20261003.md` and requests: “根据该文档继续设计能安全实现所需速率的标准执行器，并执行新方案，技术问题不占有预算次数，避免不必要的测试浪费额度，重点放在仿真结果，推进到三次控制仿真有明确可用结果为止”.

Decision: Revise the actuator design to attain a defensible feasible service range safely, then execute a reviewed, matched current-version comparison for seeds 17, 23 and 42. Reuse the existing valid OPEN baselines only if the simulation inputs and no-intervention behavior remain equivalent. Preserve the sequential technical, data and independent scientific gates; a failed S17 gate requires mechanism diagnosis before proceeding. Count technical repair starts separately under D-016 while retaining every physical start and raw result.

Boundary: This direction authorizes prospective exploratory design and eligible reviewed runs; it does not assert that the former 1200 veh/h bound is physically achievable, approve a particular new phase/rate parameter before design review, guarantee favorable outcomes, close Stage 6, freeze `EXPERIMENT_PROTOCOL.md`, or authorize formal experiments. No outcome-driven parameter tuning or unexplained repeat simulations.

## D-018 — Close current-version Stage 6 exploration and enter formal design

Date: 2026-10-03. Status: `User-condition satisfied; exploratory completion recorded after independent scientific PASS`.

Authorization: The user required checking the original and supplemented exploratory criteria, then explicitly instructed that, if every required item is supported, exploration should be formally ended and the related files and Dashboard updated. The user rejected the earlier limited D-012 closeout, required current-version standard metering evidence (D-013), authorized its gated execution (D-014–D-017), and requested an explicit closure decision once evidence sufficed. This is the conditional authorization for the present record, not an invented new supervisor approval.

Evidence and decision: The existing 18-run uncontrolled search localizes a sampled M3600/R750–900 transition; the reviewed V15 actuator completed matched OPEN/control pairs at M3600/R900 for seeds17/23/42 with safety, rate tracking, detector, pre-control pairability and complete 4050-vehicle gates independently passed. All three show M protection with increased R/U system cost and current-version R slow presence on the shared road plus directly observed U slow behind R during urban green. Independent scientific review judged the full exploratory purpose met: `completed / preliminary_ready` for **formal experiment design**. Exact data and limits are recorded in `docs/探索验证阶段/STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md` and the three-seed reports. Stop exploratory runs now; further runs require a new formal-design reason, not merely availability.

Limits: The prespecified ≥30 s continuous slow-chain remains negative in all three seeds; no sweet spot or total-network net benefit was found for this tested policy. Source waiting is separated from shared-road exposure. This is one demand and three observed seeds, with S17 used during actuator development; it is not an independent formal confirmation, precise capacity estimate, real-world calibration or Robert-confirmed parameter set. Do not retrospectively mark old RI3350/ABC, strict State1/T54 or D-012 as passed. `docs/EXPERIMENT_PROTOCOL.md` remains empty/unfrozen; formal parameters, additional seeds/demand range and formal simulations await explicit design review and approval.

## D-019 — Execute the bounded formal-design development trial

Date: 2026-10-07. Status: `User-approved development execution; engineering/data/scientific gates remain`.

Source: the user-provided goal objective, preserved exactly at `artifacts/formal_development_20261007_v1/AUTHORIZATION.md`, SHA-256 `19c0dea1120384913bcac46f987070c9ecf78b0d88e0cfac12c37e217cf356d9`.

Authorization: implement and evaluate OPEN, existing V15 ALINEA and the same controller plus one simple queue-protection override at M3600/R750 and R900, U360/X180, seeds17/23/42, common4200s. At most12 development control combinations and6 corresponding OPEN baselines; strictly matched qualified old results may be reused. Temporary queue thresholds/confirmation/hysteresis may be selected from current geometry/observations and registered before new trial results, then executed after engineering/scientific review without individual parameter approval. T1 development reference is11%,70veh/h/percentage-point,30s,300/900/900veh/h and1s; override rQ900, with independent bounded nominal state. These are development references, not formal/supervisor-confirmed parameters.

Execution is sequential: S17 R900 then R750, qualify the real implementation/data, then unchanged policy at23/42. Ordinary evidence-based technical repairs/retries are authorized and recorded separately from coverage, with failures preserved. No technical retry without new evidence; congestion, unfinished vehicles and poor effects do not justify retuning or stochastic rerolls.

Boundaries: Stage6 remains closed; no general demand search, R825/M3500, second controller candidate, formal seeds101–110/201–210, formal matrix, protocol filling/freezing, supervisor communication or purchased resources. Network/model/step/signal timing/900 cap/policy-definition changes require a new user decision. Exact runtime/storage rules must be set from present resources and old receipts before launch; old resource cards are not automatic authorization. Stop after the development evidence and handoff, awaiting user/supervisor discussion.
