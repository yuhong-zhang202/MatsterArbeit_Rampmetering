# FIX02 diagnosis: R750/S17 post-green abort

Date: 2026-10-07. **Diagnosis only: no fix, retry, parameter change or new SUMO start.** Formal protocol remains empty/unfrozen and Stage6 remains closed. The registered guard source and both historic V15 and new development source remain unchanged. This label identifies an unresolved technical finding, not an implemented repair.

## Actual attempt

`DEV_M3600_R750_S17_T1_A02` received the primary exact-card release and ran through the local TraCI permission path. At simulation time654, after the held green step[653,654), the post-green interlock requested termination before another step. Worker exit1; SUMO shut down normally with exit0. This is **FAILED_INCOMPLETE / SAFETY_INTERLOCK_ABORT**, not a completed4200s result.

Guardian wall24.979666s; retained output2,176,031B; no resource ceiling was reached. SUMO log reports654s,765 inserted,96 running and0 source waiting. These are partial-run counts, not the planned3950-vehicle final cohort. Original raw and manifest remain immutable. Receipt: `artifacts/formal_development_20261007_v1/receipts/DEV_M3600_R750_S17_T1_A02.json`; raw: `data/raw/formal_development_20261007_v1/DEV_M3600_R750_S17_T1_A02/outputs/`.

## Verified pre/post counterexample

R_flow.3 was already present in the pre653 storage snapshot; it was not a new vehicle missed by the pre-green population. R_flow.0 was the stopped front and crossed correctly and alone. Native evidence:

| State | R_flow.3 position | Speed | Distance to meter | Registered requirement | Margin |
|---|---:|---:|---:|---:|---:|
|Pre-green at653|114.69805754m|20.61937210m/s|89.79194246m|84.22373217m|+5.56821028m|
|Post-green at654|135.57582461m|20.87776707m/s|68.91417539m|70.40900681m|−1.49483142m|

The current pre-green follower rule is

`margin + (v + a)×1s + (v + a)^2/(2d)`.

The post-green immediate-red rule is

`margin + v_post×1s + v_post^2/(2d)`.

Using margin1.1m, a2.6m/s² and d4.5m/s², the pre rule allows the green; the post rule aborts. R_flow.3 advances20.87776707m during the green step. To satisfy the *observed* post requirement, its original distance would need91.28677388m, exceeding the actual89.79194246m.

This verifies that the implemented pre predicate does **not imply** the required post invariant. The pre rule budgets an acceleration-step displacement and braking, while the post rule still requires an additional red reaction-step displacement. Stochastic acceleration is bounded by the logged type value here; there is no stale sensor, timestep, newly inserted offender or count error needed to construct this counterexample. It does not prove an actual collision or unavoidable real braking failure: the registered conservative interlock stopped the experiment, and other leading vehicles may also affect SUMO braking.

Pure full-population replay yields pre `STOPPED_READY / allowed=True` and post `UNSAFE_GREEN_TO_RED / abort=True`. A minimal recorded-state case containing only the stopped R_flow.0 and fast R_flow.3 still demonstrates the same predicate gap. FCD label653 represents the after-step654 state; label652 agrees with the pre653 snapshot within0.01m/s output precision. The data analyst is independently binding these observations.

Source references: `src/stage6_safe_actuator_v10.py:45–58` (pre),`:61–75` (post),`:134–149` (follower then stopped-front release),`:198–229` (interlock); `scripts/formal_development_20261007_v1/v15_worker.py:507–592` (native pre sensing/held command),`:600–643` (post sensing),`:684–688` (logged abort). `FIX02_DIAGNOSIS.json` binds controller/FCD/error raw hashes, card SHA and immutable guard source SHA.

## Scope and repair boundary

A possible prospective repair would add a **new, stronger pre-release prediction** of the existing post-red invariant, counting both green-step advance and subsequent red reaction/braking. This is not permission to implement that formula: it changes the pinned guard's allow/refuse decisions and resulting treatment trajectories, and requires full coverage of current storage vehicles plus vehicles that might enter it during the green step. Its conservatism and feasibility must be independently checked before a new version/card and replacement run. It would not relax the post-red test or prove900 service capacity; tighter preconditions may make service weaker.

The locked safety source was qualified on prior R900 trajectories; this new R750 attempt is evidence that that observed qualification cannot simply be transferred to the R750 domain. Historical successful R900 results and the new R900 T2 descriptive data remain recorded within their original observed scope; neither establishes universal actuator correctness.

No blind identical retry, deletion of the failing car, safety-margin reduction, vehicle-model change, step/signal change or10% tolerance relaxation is justified. Whether a prospective pre/post consistency repair falls within the user's ordinary technical-repair authorization or requires an explicit guard-design scope decision is for the primary agent and scientific review. This engineer has not selected or applied a new rule.

## Current bounded checkpoint and next handoff

- New OPEN R900/S17 A03: completed4200; full neutral equivalence/data qualification independently PASS.
- New T2 R900/S17 A02: completed4200; data/mechanical/sampled safety PASS; six continuous-supply900-command windows **failed10% rate qualification**. Primary/scientific disposition permits only unchanged negative-rate characterization; `RATE_SHORTFALL_DIAGNOSIS.md` retains the mechanism and limitations.
- New T1 R750/S17 A02: safety abort654, full effect comparison unusable; no R750 T2 release.
- Old reuse audit9/9 remains preserved; it does not close the new R750 implementation domain.
- Cumulative new ledger: worker starts4, SUMO starts3, complete new combinations2, pre-SUMO sandbox failure1, safety-aborted incomplete attempt1. Prepared card suffixes do not count starts.
- Six additional S23/S42 cards were prepared offline only under the preceding instruction, with unchanged source/contract. `PREPARED_REMAINING_CARDS.json` binds their hashes. They are **not released**, and cannot be launched through this unresolved safety hold.
- Run resources remain180s/300MB, startup60s, total new raw4GB, free reserve5GB. Guardian receipts retain actual usage; no resource purchase or limit change occurred.

Engineering stops here pending primary/scientific classification of the pre/post gap. Do not mark this development trial complete: eight distinct new control combinations remain incomplete or unstarted (the R750 T1 abort plus seven other controls). Governance/worklog/final development disposition are owned by the primary agent.

## Offline verification and documentation correction

Executed `.venv/bin/python artifacts/formal_development_20261007_v1/engineering/diagnose_postgreen.py`: PASS, full and minimal pre-allow/post-abort counterexample, no SUMO import/start. Result is `FIX02_DIAGNOSIS.json`; original sources and existing raw unchanged.

`ENGINEERING_PLAN.md` now preserves its historical preregistration while explicitly clarifying an imprecise measurement sentence: a full `queue_override.csv` has4200 labels, but0..599 are precontrol placeholders and600..4199 comprise3600 actual registered queue observations. This corrects documentation only; output/source/parameter contracts were not modified.
