# R900/S17 T2 rate shortfall: engineering disposition

Date: 2026-10-07. Classification: bounded development, not formal. New simulation starts during this diagnosis: **0**. Stage6 remains closed; D-019 controls this new work and the formal protocol is still empty/unfrozen.

## Finding

No ordinary arithmetic, timing, measurement or override implementation bug was identified in the inspected evidence. The implementation executes its registered V15 guard and pulse contract, but **does not qualify for tracking a continuously requested 900 veh/h within the fixed 10% gate in this run**. This is a demonstrated implementation-capability limitation under these trajectories. It is not proof that the physical ramp or freeway inherently cannot serve 900 veh/h, nor a proof of unrestricted safe operation outside this sample.

The independent data agent's `T2_DATA_GATE.json` and `v15_service_fcd_audit.json` report 600/600 intended single-front crossings, zero red/multiple/wrong-front crossings, independent guard/feedback/queue replay PASS and complete input/output accounting. The stopped-only historical helper's 724 findings were superseded by the correct moving/stopped V15 audit, not removed from history. Rate qualification is separate and remains FAIL in all six continuously supplied windows.

## Exact credit accounting

Each fixed 300s window requests 900 veh/h, hence75 vehicle credits. The independent engineering replay covers every PulseScheduler field at each control step600..4199 with **zero differences**. Green slots equal actual crossings in every window. The identity is:

`credit_before + command_credit = green_slots + dropped_credit + credit_after`.

| Window | Actual / green | Credit before → after | Dropped credit | Rate error |
|---|---:|---:|---:|---:|
|1200–1500|64|0.25 → 0.50|10.75|14.667%|
|1500–1800|64|0.50 → 0.50|11.00|14.667%|
|1800–2100|64|0.50 → 0.25|11.25|14.667%|
|2100–2400|66|0.25 → 0.75|8.50|12.000%|
|2400–2700|66|0.75 → 0.75|9.00|12.000%|
|2700–3000|66|0.75 → 1.00|8.75|12.000%|

This is not an interval-phase error: boundary credit can explain at most the recorded ±0.5 credit, whereas losses8.5–11.25 close each discrepancy. It is not green-slot underexecution or empty release. The ledger explicitly caps retained credit at1 after refusal to prevent catch-up bursts. Consequently some 0.25 credits are permanently discarded while the guard continues to refuse. This behavior is deliberate inherited code, not an override accounting defect. The ≥3s green-start spacing by itself permits a higher nominal rate than900; the observed refusals and discard matter here. Sources: `scripts/formal_development_20261007_v1/control.py:55–85`; `RATE_SHORTFALL_DIAGNOSIS.json`; analyst `capacity_credit_diagnostics.json`.

## What the guard refusals actually mean

All259 `LEADER_SECURE_GAP` and112 `INTERNAL_RECEIVER_CLEARANCE` due refusals within1200..3000 identify a preceding released R vehicle on **`:ramp_mid_0_0`**, the immediate internal connector after the meter. Thus these observations cannot be assigned exclusively to freeway merge congestion or a downstream physical capacity limit. They enforce a conservative envelope around consecutive metered vehicles.

Examples from the native unrounded pre-step logs:

- **t1202, R_flow.109:** its available leader gap11.269836m is below `secureGap + margin = 10.230085 + 1.1 = 11.330085m`. The deficit is approximately0.06025m. The preceding R_flow.108 is moving at7.99849m/s on the internal connector. The comparison follows the registered secure-gap query; changing margin or maximum-next-speed assumptions would change the safety policy.
- **t1206, R_flow.110:** the preceding vehicle's rear lies11.654846m after the meter. The moving-front envelope requires `length5 + minGap2.5 + maximum_entry4.309681 + margin1.1 = 12.909681m`. The11.436783m gap excluding minGap itself exceeds secure-gap-plus-margin9.783235m; the additional full-body entry envelope is the refusal. This explicitly does not predict the preceding vehicle's next-step advance. It is conservative immediate-receiver protection, not direct observation of a physically stationary downstream queue.
- **t1207, follower R_flow.111:** speed3.955138m/s, distance to meter10.233352m. The pre-green guard requires one full acceleration step plus normal braking: `1.1 + (3.955138+2.6) + (3.955138+2.6)^2/(2×4.5) = 12.429563m`. The2.196211m deficit correctly produces `FOLLOWER_STOP_DISTANCE` even while the preceding internal car moves at9.330033m/s. It protects the follower against the immediate return to red after a one-second green.
- **t1312, R_flow.132:** stopline distance5.000725m exceeds maximum possible one-step travel4.910652m; the front is not ready for the registered one-step crossing. This is a separate readiness refusal.

These inequalities were recomputed from the raw log. Independent FCD audit verifies actual front/follower identities and native sensor agreement within the archived output precision; getSecureGap arithmetic remains conditional on SUMO's logged API value. Source implementation: `src/stage6_safe_actuator_v10.py:45–58`,`:134–159`,`:172–189`; worker sensor collection/query/application: `scripts/formal_development_20261007_v1/v15_worker.py:507–592`.

Most discard increments coincide with the follower envelope:8.5/9.25/9.25/6.75/8.25/7.5 credits across the six windows. Internal receiver increments are2/1.75/2/1.5/0.5/1.25; secure-gap increments0.25/0/0/0.25/0.25/0. These are **bookkeeping associations, not causal shares of lost service**. Guards are checked sequentially and changing one refusal changes future trajectories; no counterfactual was run. The queued population is not equivalent to a safety-qualified front at every requested release time.

## Repair boundary and continuation

No parameter-preserving ordinary repair can currently be justified. Raising accumulated-credit retention, changing one-second pulse/minimum-red timing, changing guard envelopes or the900 cap, overriding refusals, changing model/step, or relaxing the10% gate would alter the registered design or acceptance boundary. They must not be presented as bug fixes or used to manufacture a PASS. An identical retry has no new technical reason.

Engineering recommends holding additional T2 seeds and the next staged R750 starts until the primary agent reconciles this failed execution-capability gate with independent scientific review. Preserve this run and all descriptive effect data. It may describe the behavior of **the registered900-command policy with realized service constraints**, but cannot be promoted to a rate-qualified900-service treatment or a formal sweet spot. Continuing unaffected T1/R750 development or studying the same limited T2 as an explicitly unqualified diagnostic policy is a methodology/scope decision for the primary agent; this report does not release either. If a redesigned actuator is selected later, it needs prospective authorization, a new version and renewed technical qualification, not post-outcome tuning of the present card.

## Verification and evidence

Executed only:

`.venv/bin/python artifacts/formal_development_20261007_v1/engineering/diagnose_rate_shortfall.py`

PASS: full logged pulse replay, window credit closure and green/actual agreement. Script cannot launch SUMO/TraCI; raw files are read-only. Output: `RATE_SHORTFALL_DIAGNOSIS.json`, including raw controller-log SHA-256. All existing traffic source/parameters/cards/raw remain unchanged. Original API warning and technical failures are retained. Current cumulative runtime ledger remains worker attempts3, SUMO starts2, completed new combinations2 (OPEN and T2 R900/S17).

Independent sources are under `data/processed/formal_development_20261007_v1/T2_R900_S17_A02/`: `T2_DATA_GATE.json`, `v15_service_fcd_audit.json`, `capacity_credit_diagnostics.json`. Primary agent owns updates to Project State, Decision/Worklog and final scientific disposition.
