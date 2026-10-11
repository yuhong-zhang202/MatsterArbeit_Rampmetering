# Candidate A — phase self-loop investigation and SMOKE02 correction

**Minimal isolated correction prepared for user/Chat review. No SUMO execution is authorized or performed in this round.** The consumed SMOKE01, its failure evidence and historical STOP3 remain unchanged. Baseline: `09d77dab8d19f414277ade5b399675f0e4e13f01`. [Current task authority](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/USER_REQUEST_RECORD.json).

## What the 17 warnings mean

The retained SMOKE01 stderr has one warning for phase 2 of each `ramp_mid` program CA_C8–CA_C24. Each old program has three phases and specifies red phase `next="2"`: its only successor is itself. Independent XML parsing maps these 17 program/phase pairs exactly to the original warning lines. [Original warning evidence](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RUNTIME_NATIVE_WARNING_EXTRACT.txt), [original failure report](CANDIDATE_A_NATIVE_PHASE_SMOKE01_RESULT_20261011.md).

SUMO 1.26 official source, pinned commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`, emits this warning in `MSTrafficLightLogic::init` when a multi-phase program has one successor pointing to the same phase. The loader initializes collected network and additional programs, including inactive ones. This is a phase-graph initialization warning, **not a collision, braking or red-crossing finding**. [Warning condition](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/traffic_lights/MSTrafficLightLogic.cpp#L135-L159), [initialization call site](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/netload/NLJunctionControlBuilder.cpp#L518-L525).

The explicit `next` index controls the native successor. Repeatedly returning to the red phase therefore holds the same signal color; without an external phase/program change, that program does not resume green. [Native successor implementation](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/traffic_lights/MSSimpleTrafficLightLogic.cpp#L80-L109). Official source URLs, full-file hashes and five line-numbered excerpts are preserved in a [versioned source receipt](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/engineering/OFFICIAL_SOURCE_RECEIPT_R1.json); its earlier two-file receipt is retained.

This source evidence explains the configuration origin of the 17 warnings. It does not determine their exact emission wall-clock or delivery delay. SMOKE01 stopped before its first simulation-step ACK, so it supplies no motion evidence about the intended yellow/red transition. Source-to-installed-binary/compiler equivalence remains unverified.

## Minimum correction in a new diagnostic package

The old package is untouched. The new additional file keeps the two programs actually selected by the bridge; unused CA_C9–CA_C23 are omitted from this new file. A_OPEN and all existing network content remain in the unchanged network.

| Program | New configuration | Bounded purpose |
|---|---|---|
| CA_C8 | G3 / y3 / r600 s, successors 1 / 2 / 0 | Yellow requested at 600 s; red begins at 603 s. Its next green would be 1203 s, but the bridge replaces the program at 1200 s after the existing admission checks. |
| CA_C24 | G3 / y3 / r18 s, successors 1 / 2 / 0 | Green selected at 1200 s; yellow at 1203 s; red at 1206 s; mandatory close/pause after the 1206→1207 s interval. |

CA_C8 is a retained identifier, not an 8 s cycle in this diagnostic; its configured cycle is 606 s. Simply changing the old 2 s red to `next=0` would yield green at 605 s and break preparation, so that correction was rejected. The new finite hold preserves the **intended color schedule** through the preparation interval. It does not prove identical microscopic vehicle dynamics.

CA_C24 would return to green at 1224 s. That time is outside the fixed 1207 s diagnostic stop and is neither tested natively nor authorized. This package must not be used directly for multi-cycle service qualification. The 3 s yellow is unchanged; its general adequacy is not established by these offline tests.

The new bridge is a versioned copy of the reviewed bridge with exactly one import changed to the new profile. Observer, R2 adapter, admission, identity/vehicle coverage, receiving-space checks, step ACK/readback, warning capture, watchdog, cleanup and mandatory pause remain identical. [Copy receipt](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/engineering/BRIDGE_VERSIONED_COPY_RECEIPT.json). The prospective envelope retains its previously reviewed isolated shadow status; production guard and A1/A2 contracts are untouched.

Warnings are neither hidden nor whitelisted: `no-warnings=false`, `aggregate-warnings=-1`, and the original 17 warning bytes still trigger STOP before fake motion. Any other native warning or unknown log coverage can still stop a later authorized attempt.

## New identity and binding

- Run: **`CA_NATIVE_PHASE_R300_S17_SMOKE02`**; status `PREPARED_NOT_RELEASED`.
- [Exact card](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE02/card.json), SHA-256 **`a501e6005589de0d3ce6acd0fe7924ec84b589bec0849c4f3fcd3f51a4d552f3`**.
- Nominal active demand M3600/R900/U360/X180 veh/h; service command 300 veh/h; seed 17; step 1 s; activation 1200 s; end 1207 s. R300 in the name denotes the service command, not ramp demand.
- Demand is byte-identical to the existing public input: 4050 scheduled vehicles (M3000/R600/U300/X150). Counts are not active rates, actual insertions or observed throughput.
- Inherited resource references: 180 s wall time, 60 s startup, 300,000,000 B output cap and 5,000,000,000 B free-space requirement. They require future exact-card approval; this preparation does not grant it.
- New canonical authorization/release and raw run directory are absent. Execution rejects missing new authorization before native startup/raw allocation. Consumed SMOKE01 permission cannot authorize SMOKE02. Relocation requires controlled path rebinding, a new card and renewed approval.

## Verification and review evidence

[Engineering review](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/engineering/ENGINEERING_REVIEW.md): five necessary new offline tests passed; prepare, card check and read-only current-root environment binding passed. XML-driven fake events cover holding red, admission/replacement, first controlled red and 1207 s pause; original warning injection still stops. Old suites were not repeated. Native startup, full XSD/compiler equivalence and physical safety were not tested.

[Independent data review, current V2](../../data/processed/candidate_a_native_smoke_selfloop_fix_20261011_v1/FINAL_DATA_REVIEW_V2.md): the initial public audit and five new tests passed, followed by one necessary corrected public-checker execution. It verifies 29 bound files, five source excerpts, warning mapping, demand/count/rate separation, configuration arithmetic and missing-authorization rejection. The public audit needs neither ignored raw nor old executable permission. [Current reproducible checker](../../data/processed/candidate_a_native_smoke_selfloop_fix_20261011_v1/independent_selfloop_review_v2.py), [current versioned result](../../data/processed/candidate_a_native_smoke_selfloop_fix_20261011_v1/INDEPENDENT_RESULT_V2.json).

Engineering and data separately verified all 53 local SMOKE01 raw files unchanged (1,804,472 B); this is explicitly local-only. All 536 protected files, 7 R2 files, 26 V5 files and the old card remain unchanged. [Preservation receipt](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/engineering/OLD_EVIDENCE_PRESERVATION_RECEIPT.json). Original failed/unobserved records were not replaced with zeros or success.

The parent checked an isolated partial tracked-tree export: 587 files, 31,737,441 B, from precommit index tree `8914391c2452f85cf8bc48e4f9960b47cd3d268c`. Five new tests, the original public checker, default preparation, card check and expected foreign-runtime-path rejection all passed; raw contained only `.gitkeep`, with no executable authorization/release files. [Exact receipt](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/portability/PARTIAL_EXPORT_RECEIPT_V1.json). This is not a full clean Git clone, a tested commit or a native runtime relocation test. Final delivery must match the relevant tested bytes.

Initial scientific review found two **Minor metadata/text defects**: the V1 checker actually verified 29 files but a reused loop variable made its output say 150; the V1 main/data text said six excerpts instead of five. V1 checker/results/reviews/bindings, export logs and the [main report preimage](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/MAIN_REPORT_PRE_MINOR_CORRECTION_V1.md) remain intact. V2 separates binding and vehicle counts and adds output assertions; only the corrected public checker is rerun. The V1 export output's incorrect count is explicitly superseded, not silently edited. V2 is checked in the project workspace, **not separately rerun in the export**; unchanged phase/bridge tests retain their original scope. [Retained initial findings](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/SCIENTIFIC_FINDINGS_V1.md). No runtime source, card, guard, test suite or old evidence changes as part of this correction.

[Final read-only scientific review](../../artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1/FINAL_SCIENTIFIC_REVIEW.md) closes both Minor findings and permits delivery of the bounded offline correction to user/Chat review. No required finding remains. The reviewer verifies V2 and preserved V1 hashes, all 29 engineering bindings, the 587 export files and five original command logs; it does not repeat tests or run native SUMO. Offline delivery review is not user acceptance, runtime authorization or safety/service qualification.

## Interpretation and handoff

**Confirmed:** exact warning/configuration correspondence; official initialization predicate and successor mechanism; minimum new-package delta; preserved checks/old evidence; offline replay and binding checks passed. **Limited inference:** the specific self-loop warning condition has been removed from the new additional file. This does not predict a warning-free native run or prove vehicle dynamics equivalence. **Unresolved:** actual native startup and first-red behavior, native log timing/coverage, general yellow adequacy, physical safety and service qualification.

Next owner is user/Chat to review the exact new card, change scope and resource limits. A later single native attempt requires explicit new authorization; there is no automatic retry, continuation or full-cycle expansion. Candidate A NOT_QUALIFIED, A1 UNRESOLVED, historical bounded STOP3, actuator900 NOT_TESTED, existing Stage 6 closeout and empty/unfrozen formal protocol remain unchanged.

Documentation impact: this report, factual PROJECT_STATE/WORKLOG and README's new offline interface. DECISIONS, EXPERIMENT_PROTOCOL, AGENTS, supervisor records, thesis and upstream PRs are unchanged. No new Issue/PR/push or merge is part of this local delivery.
