# Candidate A native-phase diagnostic smoke — proposal and minimal preparation

**Status: Proposed / preparation only / NOT authorized to run SUMO.**

Baseline: Draft PR #11 head `49d7c4a426e827342dd34be38d1f3ce2b397f8b0`.
Local review branch: `codex/candidate-a-native-smoke-proposal`.
Task authority: user's 2026-10-11 request to prepare a minimal diagnostic alternative and wait for explicit execution authorization. No new Issue was supplied; no upstream PR is edited, merged or retargeted.

## 1. Question and boundaries

The proposed smoke asks: under the existing vehicle model and network, what actually happens when the native static signal advances from yellow to red, if the old unsupported prospective-red envelope is recorded rather than used as an additional veto?

This is an observational engineering diagnostic, not a replacement A1 mathematical proof, safety certification, rate qualification or formal traffic experiment. The old A07 STOP3 and Candidate A NOT_QUALIFIED remain valid historical/current-contract records. Issue #10's Proposed NO-GO concerns establishing the stronger A1 certificate using current interfaces; it does not establish that native red is unsafe. This proposal does not reverse or approve that decision.

No production guard, existing worker, vehicle model, original configuration, raw evidence, formal protocol or research decision is changed. `docs/EXPERIMENT_PROTOCOL.md` remains empty/unfrozen. The new code cannot launch SUMO or advance a simulation.

## 2. Native mechanism and yellow review

Reuse the existing Candidate A phase envelope: G3 s / y3 s / r18 s for nominal packet size 2 and service command 300 veh/h, a 24 s cycle. The packet size is an accounting assumption, not evidence that two vehicles actually pass. Use the official static program/phase selection mechanism and its scheduled yellow-to-red event; do not force immediate red using `setRedYellowGreenState`.

Official references: [SUMO traffic lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html), [TraCI traffic-light control](https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html). Event order is grounded in pinned SUMO 1.26 source commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`, including [MSNet.cpp](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSNet.cpp#L832-L893). Sources and excerpt hashes are in [engineering receipt](../../artifacts/candidate_a_native_smoke_proposal_20261011_v1/engineering/SOURCE_GUIDANCE_RECEIPT.json). These sources support the mechanism, not a safety guarantee for this configuration.

Historical A07 yellow begins with motion at 1203 s, while its pre-step snapshot still says G. At that onset, 27 storage plus 15 ingress vehicles were observed; the fastest approaching vehicle was 2.699775598613039 m/s with projected gap 5.008379646428438 m. At 1204 s it accelerated to 3.795129974108697 m/s. The terminal 1206 s creep speed alone therefore cannot justify yellow duration. Three executed yellow steps recorded zero crossings; the refused 1206→1207 red step has no observed motion/crossing result.

For context only, assuming a literal 1 s reaction followed by constant 4.5 m/s² braking yields approximately 1.600 s and 3.510 m at the onset speed. SUMO tau/actionStep=1 s is **not** proof of that reaction assumption. At the nominal storage speed limit 22.22 m/s, the same estimate is 5.938 s; ingress 18.05 m/s gives 5.011 s. Stopping and clearing are different alternatives, so these numbers prove neither universal adequacy nor native danger. Three seconds is retained solely as an inherited diagnostic starting candidate for the observed queued context; later cycles and faster approaches remain unverified. No speed limit, margin or yellow duration is retuned.

Exact extract, calculations, source hashes, original extraction failure and corrected retry are retained in [independent yellow review](../../data/processed/candidate_a_native_smoke_proposal_20261011_v1/YELLOW_CONTEXT_REVIEW.md). Public reproduction checks the selected submitted extract; optional local checking verifies four immutable raw hashes. Public checking does not recreate the full raw extraction.

## 3. Smallest proposed policy change

Only the old `1.1 m + illustrative reaction distance + continuous braking distance` prospective-red envelope becomes **SHADOW_ADVISORY in this isolated diagnostic profile**. Record its actual witness and refusal result; do not silently remove it from production or interpret its refusal as a native collision prediction.

All other required checks remain blocking:

| Before motion | After motion |
|---|---|
| Exact time, controlled link, native program/phase/state and geometry | Read back time, program, phase, link and receiver state |
| Vehicle IDs, population, route, type, modes and local dynamics | Attribute new/disappeared IDs to departures/arrivals; preserve actual executed prefix even on failure |
| Storage/ingress/internal coverage and bounded entrant premises | Count unique internal entries under every color; stop on uncovered, duplicate or red crossings |
| Known downstream receiving space; deny a new green if unavailable | Collision/teleport checks; native emergency warnings; ordinary braking checks on all surviving visible vehicles |
| Missing or inconsistent observations deny preparation | Missing/incomplete observations deny reconciliation and further motion |

The new interface uses the protected observer through dependency injection; its own code does not establish native observer completeness. Loaded/pending and entering vehicle checks depend on the protected route/geometry/speed premises. The future launch bridge must bind exact observation and warning intervals. A declared warning receipt is not independent proof that no warning was omitted. Post-step monitors detect an anomaly **after** it happened; they do not promise prevention. Required receiver/coverage and logging integration must be checked before any real launch.

## 4. Proposed identity and staged observation

| Field | Proposed value |
|---|---|
| New run ID | `CA_NATIVE_PHASE_R300_S17_SMOKE01` — never reuse A07 |
| Demand | M3600 / R900 / U360 / X180 veh/h |
| Meter command | R300 = 300 veh/h service command, not ramp demand |
| Seed / step | 17 / 1 s |
| Initialization | A_OPEN before 600 s; native yellow then holding red; activation at 1200 s |
| Activated program | CA_C24, G3 / y3 / r18 s |
| First required review gate | After first activated red motion `(1206,1207]` |
| Conditional continuation cap | 1272 s, at most three full 24 s cycles including the first |

**First stage:** monitor initialization including yellow-to-red around 603 s; record onset speed/gap, phase scheduling, shadow witness and all post checks. At activated yellow-to-red 1206→1207, stop immediately if anything is unknown or abnormal. Even if observationally clean, pause at 1207 for user and independent review. This first checkpoint contains **zero full metering cycles**; no rate or full-cycle conclusion is possible.

**Only after separately approved continuation:** a future reviewed bridge may continue to at most 1272 s, stopping before a fourth cycle begins. The current adapter cannot resume after its mandatory pause; continuation is intentionally not implemented. There is no automatic continuation to 4200 s, other rates/seeds or Candidate B. Several cycles are a possible subsequent diagnostic scope, not the currently authorized execution.

Each actual output package must be new and append-only. Preserve source/input/config hashes, software versions, phase requests and actual readback, per-step vehicle/receiver inventory, native warning byte/time intervals, crossings and the stop reason. Do not allocate a run package or write raw before authorization.

## 5. Accounting and stop decisions

Reuse Candidate A CycleLedger, PhaseEnvelope, motion-phase prediction and all-color crossing records. Record command C, applied C, completed nominal E and **measured N**, with explicit duration and cycle completeness. Do not equate nominal packet size with N. Red N must be zero for an observationally clean smoke; unknown crossing coverage is a stop, not zero. Entirely unobserved periods use null; an observed zero remains zero; partial cycles stay partial. Preserve failed and unreconciled steps rather than filling their missing results.

Before activation at 1200 s, initialization crossings are recorded separately in per-step receipts; they are not included in the activated CycleLedger's C/E/N totals. Report these measurement scopes explicitly.

Stop on identity/route/mode/dynamics/coverage/receiver uncertainty, wrong program/link/phase, duplicate or uncovered entry, red entry, collision, teleport, native emergency warning or excessive/unknown braking. The ordinary-braking diagnostic uses the existing 4.5 m/s² model bound and separately checks speed differences and reported acceleration; floating comparison tolerance is numerical, not a new safety allowance. No failure leads to automatic contract relaxation or timing changes.

An eventual clean smoke would establish only absence of monitored anomalies in its observed prefix. It would not prove A1 joint safety, adequate service at R300 or R900, ALINEA readiness, formal experimental authorization or a sweet spot.

## 6. Delivered minimal code and outstanding integration

- [Step adapter](../../src/candidate_a_native_smoke_20261011/adapter.py): isolated `prepare_step` / `reconcile_step`; reuses existing accounting and guard witness; consumes injected observations. No TraCI import, simulationStep, signal setter or native launcher.
- [Plan-only CLI](../../scripts/candidate_a_native_smoke_20261011_v1/plan.py): emits the Proposed identity/policy and rejects launch options.
- [Offline tests](../../tests/candidate_a_native_smoke_20261011/test_adapter.py): synthetic interfaces verify selected binding/stop/accounting cases only. They are not traffic or native safety evidence.

**Not implemented:** native launch bridge, exact runtime package/environment binding, integration of the protected observer and complete native warning stream, actual first-red observations, approved continuation/resume. These are explicit prelaunch gaps, not hidden PASS conditions. The present delivery is reviewable preparation, not a runnable smoke.

After the user reviews this proposal, any bridge implementation must remain narrowly scoped and preserve the same stop checks. Running SUMO still requires explicit user authorization after the concrete bridge and prelaunch record are reviewable. No additional A1 mathematical safety-proof task is proposed.

## 7. Verification and documentation

Required review sequence: simulation_engineer → data_analyst → scientific_reviewer. Versioned source/testing and independent review receipts are stored under `artifacts/candidate_a_native_smoke_proposal_20261011_v1/` and `data/processed/candidate_a_native_smoke_proposal_20261011_v1/`. Actual command outcomes and their source bindings, not this plan, determine verification coverage. Original failed checks remain preserved. No SUMO or TraCI launch occurred.

All three reviews completed; [final read-only scientific review](../../artifacts/candidate_a_native_smoke_proposal_20261011_v1/FINAL_SCIENTIFIC_REVIEW.md) returned **PASS_FOR_BOUNDED_NATIVE_PHASE_SMOKE_PREPARATION_ONLY**, with no unresolved required finding. This gate covers preparation, not prelaunch readiness, native safety or rate qualification.

Actual tested code commit: `c4a70b1582db4d9778d84ce555317de8f14e9fc0`. A fresh local no-hardlinks, single-branch checkout, containing only `.gitkeep` under raw, ran these commands once with Python 3.13.0 and bytecode writes disabled:

| Offline check | Actual result | Scope |
|---|---|---|
| `python -m unittest discover -s tests/candidate_a_native_smoke_20261011 -v` | 10 PASS, 0 FAIL/ERROR/SKIP | Fake connection, binding/stop/accounting cases; includes plan-only CLI rejection |
| `python data/processed/candidate_a_native_smoke_proposal_20261011_v1/review_yellow.py` | Exit 0 / PASS | Selected public extract and conditional calculations |
| `python data/processed/candidate_a_native_smoke_proposal_20261011_v1/review_adapter.py` | Exit 0 / PASS, 4 probes | Current seven engineering bindings, 536 protected files, selected accounting/stop cases |

See [actual clean-checkout receipt](../../artifacts/candidate_a_native_smoke_proposal_20261011_v1/DELIVERED_CODE_CLEAN_CHECKOUT_RECEIPT.json) and [archived exact outputs](../../artifacts/candidate_a_native_smoke_proposal_20261011_v1/CLEAN_OUTPUT_ARCHIVE_BINDING.json). Original-local optional raw-hash checking passed separately; it was intentionally not run in the raw-free checkout. Native signal/physics and launch integration were not tested; the unchanged historical 43-test suite was not rerun. Later documentation/receipt-only commits do not change these tested code bytes and are not described as separately tested execution versions.

PROJECT_STATE receives only the factual preparation status; WORKLOG records this bounded work. DECISIONS, formal protocol, AGENTS and supervision records are unchanged. Unrelated MemoryCore/private-email work is excluded from this delivery. Next handler: user/Chat reviews this proposal and its explicit integration gap. Suggestions here do not constitute execution authorization.
