# FIX02 implementation ready for independent review — HOLD

Date: 2026-10-07. DEVELOPMENT TECHNICAL REPAIR ONLY. No corrected SUMO run is released or performed. The primary agent reports that both continuation and replacement scientific-review agent calls failed with `agent thread limit reached`; the data fallback also failed with model capacity. This is an execution/review platform blocker, not evidence that the corrected implementation passes independent review.

## Context and bounded work

Reviewed AGENTS.md, current PROJECT_STATE, DECISIONS (D-018/D-019), the empty EXPERIMENT_PROTOCOL, recent WORKLOG entries, exact AUTHORIZATION.md, SCIENCE_FIX02_REPAIR_SCOPE.md, engineering plan/contract, FIX02 diagnosis, and directly affected sources. Current phase is bounded formal-design development preparation; Stage6 remains closed. The formal protocol remains 0B/unfrozen. D-019 authorizes the fixed demand/seed/treatment combinations and evidence-based technical repair; it does not authorize formal experiments or parameter retuning. The scientific scope note permits the minimum stronger precondition while preserving the post invariant and requires fresh exact review before launch.

This engineer designed a reversible patch; the primary mechanically applied it because this agent's direct write scope excludes live scripts. Only the development helper, worker, runner and offline tests were patched. Original `src/stage6_safe_actuator_v10.py`, original V15 sources, original parameter contract and all raw results remain unchanged. Pre-FIX02 exact source bytes, including the predecessor's partial helper, are archived in `pre_fix02_sources/` with `SOURCE_MANIFEST.json`; the repair addendum maps every original source to its archived bytes. Old cards are not rebound to new code.

## General bound and coverage

Let v be observed nonnegative speed, a the actual type acceleration, b normal deceleration, and dt=1s. The unchanged post predicate uses P(w)=0 for w<0.1m/s and P(w)=1.1+w+w²/(2b) otherwise. P is monotone nondecreasing. Under the fixed dynamics, next speed is at most v+a and green-step advance is at most v+a. Therefore requiring pre distance d >= (v+a)+P(v+a) gives d-advance >= P(next speed). This preserves the original post margin and criterion and explicitly budgets both the green-step movement and subsequent red reaction/braking. Stopped followers can accelerate during green and therefore receive this pre bound too.

The worker checks every current storage follower, and every vehicle currently on the sole upstream internal connector `:urban_diverge_1_0`, projecting its position by subtracting the checked113.08m connector length. Input routes/types and all compiled connections into storage are checked. At connection startup, ALINEA mode queries actual type maxSpeed, accel, tau and actionStepLength. It stops before stepping unless tau=actionStepLength=1 and maxSpeed+accel <113.08m. Thus vehicles further upstream or newly inserted on the fixed urban_in route cannot traverse the complete connector into storage in that one green step. Every observed connector vehicle is validated for identity, type, coordinate and actual speed bounds. Runtime proof values are written to `fix02_entrant_coverage.json`; full predictor populations are recorded in `guard_decision_json`.

SUMO documents maxSpeed as an absolute type speed cap, including when speedFactor exceeds1, and default car-following acceleration as bounded by accel. These support the implementation bound; live values still require runtime verification. Sources: [VehicleSpeed](https://sumo.dlr.de/docs/Simulation/VehicleSpeed.html), [vehicle/type definitions](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html), read2026-10-07. This is not scientific justification of those model parameters.

**Proof limits:** the intended front retains the legacy route, receiving-gap and one-step reachability checks. Its moving-front reachability is a heuristic; the follower proof does not guarantee that the intended front crosses. The unchanged post interlock still checks wrong/multiple/empty crossings and all remaining storage vehicles, and aborts before the next step on failure. No safe-red margin, interlock, signal duration, dynamics, feedback, queue policy, credit scheduler or rate acceptance threshold was weakened. More conservative refusal may lower service. No900-service qualification or traffic-effect claim follows from this repair.

## Verification evidence

- `.venv/bin/python -B -m unittest discover -s scripts/formal_development_20261007_v1 -p test_offline.py -v`: PASS,15 tests. Covers the failure counterexample, exact distance boundaries, stopped/moving follower cases, monotonic bound, entrant refusal/coverage boundaries, unchanged front/interlock, original worker interface, queue hysteresis/nominal state and pulse credit.
- `ast.parse` of all six development Python files: PASS; no bytecode or SUMO start needed.
- `.venv/bin/python -B artifacts/formal_development_20261007_v1/engineering/verify_fix02_evidence.py`: PASS. Exact raw full-population pre653 replay rejects R_flow.3: gap89.7919424582785m versus corrected requirement107.44310427279231m. The historical observed post failure remains intact. Deterministic fake TraCI observation verifies connector position110.08−113.08=−3m. New card preflight passes and its raw directory is absent.
- `.venv/bin/python -B artifacts/formal_development_20261007_v1/engineering/verify_fix02_open_path.py`: PASS. Specializing the complete old/new worker AST to mode=NOOP yields exact equality. Added live queries and logging are inside ALINEA branches. Pure imports and card-field validation are the only outside-branch changes. Existing empirical OPEN A03 neutrality plus this static branch proof supports continued OPEN reuse subject to independent reconciliation; this is not a new empirical neutrality run.
- `.venv/bin/python -B scripts/formal_development_20261007_v1/runner.py prepare --ramp 750 --seed 17 --treatment T1 --attempt 3`: PREPARED_NO_SIMULATION.
- `.venv/bin/python -B scripts/formal_development_20261007_v1/runner.py preflight --card artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R750_S17_T1_A03/card.json`: PASS_STATIC_PREFLIGHT_NO_SIMULATION.
- `git diff --check`: PASS. New untracked sources were separately parsed/tested; this command alone does not validate them.

Machine evidence: `OFFLINE_VERIFICATION_FIX02.json`, `FIX02_EXACT_VERIFICATION.json`, `FIX02_OPEN_EQUIVALENCE.json`. These are engineering checks; independent final scientific/data review is still unavailable. No new worker attempt, SUMO start, or raw output was created in this repair task. Previous failed/incomplete/negative-rate evidence and execution accounting are preserved.

## Exact prospective bindings

Prospective card: `artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R750_S17_T1_A03/card.json`.

- Card SHA256: `9f4bda513b06171f0f817e4a5c5b25e1041b2d06df5d86ba415cab71ba67e5fd`.
- Corrected helper SHA256: `636125577811cfbb266e4136cb7a2de08f7d010006c1d92457f321ba819b62a9`.
- Corrected worker SHA256: `f90e181707b0be69f733988885ae093a47dbbf8fe0a4d916b623253d1b082a43`.
- Repair addendum SHA256: `3b002f0ed82f233efe24968cf72963e311caf78c10224909dfe43f3882fba5a9`.
- Unchanged original parameter contract SHA256: `31f439c1a83f724259d7a74a382b3d03b6cb82378ec145b85431739655ca07f3`.
- Unchanged original post-guard source SHA256: `c48b743972e44cdac8d53b6276efeed75c8bcd45a36c13940735e9d3f317f2d7`.

The complete six development-source plus three immutable-source hashes are bound in both the card and `FIX02_EXACT_VERIFICATION.json`. Runner preflight requires the exact source set, including the helper, original contract hash, guard revision and addendum hash. Old pending cards fail the new revision validation and remain HOLD. Runtime limits remain180s per attempt,60s startup,300MB per run,4GB new raw,5GB free reserve,0.2s polling.

## Reuse and continuation

The data agent's preliminary native-log replay reported actual old green slots newly refused by the stronger storage-follower bound in all three old R900 T1 seeds and new R900/S17 T2. Such a difference disproves command/pulse equivalence regardless of additional entrant uncertainty. Do not pool old control outcomes with the corrected guard. Preserve these as historical/diagnostic evidence; any replacements must use the same authorized combinations. The completed old-safety and10% rate-failure findings are not erased. A frozen independent reuse audit is still required; this engineer does not relabel preliminary agent output as a final gate.

The safest next step is independent read-only science review of this derivation, code, card and proof limits, plus the data agent's exact-helper-bound reuse audit. When agent capacity returns, review this already prepared package; do not regenerate cards or rerun offline tests absent changes. The current preflight command above is the reproducible read-only card check. Only after an explicit primary/scientific exact-card release may the primary provide a release JSON and authorize the guardian launch. No launch command is provided as currently executable authorization.

The R750/S17 T1 A03 run is a technical replacement for the preserved A02 safety failure. Its actual runtime entrant dynamics, intended-front behavior, full4200s completion, occupancy, crossings, service windows and vehicle accounting remain unverified. If it passes required gates, prepare subsequent same-scope corrected cards sequentially. If it fails, preserve the failure and diagnose new evidence; do not retune or blindly repeat.

Documentation impact: primary owns the required concise WORKLOG/PROJECT_STATE development checkpoint updates. No governance, protocol, thesis, processed-data or result file was changed by this engineer. No scientific review is claimed to have occurred after this implementation.
