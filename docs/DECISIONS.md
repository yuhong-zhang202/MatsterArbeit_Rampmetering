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
