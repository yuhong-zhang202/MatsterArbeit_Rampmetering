# Candidate A native-phase smoke — minimal runtime bridge

**Implementation, three-role offline review and delivered-code clean checkout complete; awaiting user/Chat review. Native execution is NOT authorized.**

Baseline: `833ac18db2c6b256f2782631830c9c849e090681`, local branch `codex/candidate-a-native-smoke-proposal`.

The user accepted the [previous proposal](CANDIDATE_A_NATIVE_PHASE_SMOKE_PROPOSAL_20261011.md) and explicitly authorized completing the minimal real launch bridge and complete logging bindings, followed by engineering → data → scientific review and delivery of runnable changes for review. They explicitly withheld SUMO execution authorization. This implementation record supplements the historical preparation report; earlier source/test bindings remain valid for their original bytes.

## Required scope

Reuse Candidate A's existing input generation, observer, phase/ledger/crossing components. Keep the old production guard, worker, model, network and formal experiment configuration unchanged. The unsupported prospective-red envelope is advisory only inside the isolated diagnostic profile; necessary identity, signal, coverage, receiving-space and post-step stop checks remain required.

Identity: `CA_NATIVE_PHASE_R300_S17_SMOKE01`; demand M3600/R900/U360/X180 veh/h, servicecommand300 veh/h, seed17, step1s, activation1200s, G3/y3/r18. Preserve monitoring during initialization including native y→r around603s. Stop after the first activated1206→1207 red interval even if observations are clean: zero completecycles at that checkpoint. No automatic continuation, other rate/seed, full qualification, A1 proof task or formal experiment is included.

The previous yellow-context evidence supports only an inherited3s diagnostic candidate in the observed queued onset, not universal adequacy or native safety. Historical A07 STOP3, Candidate A NOT_QUALIFIED, A1 UNRESOLVED, actuator900 NOT_TESTED and Stage6 closure remain. Formal protocol remains0B/unfrozen.

## Review and authorization boundaries

The code must have a safe offline/default mode and a separate guarded native execution path. No current approval authorizes the native path. Before any future run, user authorization must bind the concrete run card/input/source/environment identity. No old consumed card/output may be reused. A package assembled offline is not a simulated result or an authorization receipt.

Native logs must be captured from actual process/log sources, bound by bytes, offsets, timing/barriers and EOF/finalization status. A caller-declared empty string does not establish completeness. Late critical messages or partial/missing/unverifiable logging remain unknown at the applicable coverage checkpoint; post monitoring cannot promise prevention of a violation already executed. Ordinary buffered information is handled at final EOF as described below.

No SUMO/TraCI/native execution, raw allocation, environment installation, production guard/formal design/upstream PR changes are permitted in this task. Raw and previous evidence stay immutable. Unrelated MemoryCore/private-email changes are excluded. No new GitHub Issue was supplied; this task currently prepares a local reviewable delivery.

## Implemented runtime bridge

The new [bridge](../../src/candidate_a_native_smoke_20261011/bridge.py), [card binding](../../src/candidate_a_native_smoke_20261011/bridge_card.py), [log capture](../../src/candidate_a_native_smoke_20261011/bridge_logs.py) and [resource watchdog](../../src/candidate_a_native_smoke_20261011/bridge_resources.py) reuse the unchanged Candidate A worker's observation, phase requests, child startup/connection helpers and the previously reviewed R2 adapter/CycleLedger. The [CLI](../../scripts/candidate_a_native_smoke_bridge_20261011_v1/cli.py) defaults to offline preparation/checking. It does not run SUMO at import or by default.

The tracked public A07 explicit demand is copied byte-for-byte; only diagnostic paths, end time and logging settings are adapted. Scheduled active rates are M3600/R900/U360/X180 veh/h. The XML contains 3000/600/300/150 vehicles respectively: **counts are not hourly rates**. R departures start at600s, spaced4s; the diagnostic ends1207s, before most scheduled demand. There is no measured insertion/throughput result in this task.

Initialization monitoring includes the native yellow-to-red transition near603s. At1200s, fresh red-phase, vehicle/mode/dynamics, lane/link/identity coverage and receiving-space checks precede `setProgram(CA_C24)` and `setPhase(0)`. The official G/y/r program then determines the transition; no direct forced-red state setter is used. After the first activated red motion1206→1207, the adapter pauses and the bridge closes the connection/owned child to finalize evidence. It cannot automatically resume; **zero complete cycles**, no rate qualification. Any later continuation requires a separately authorized identity/package.

Each ACK records its requested target separately. Actual simulation time must be read back and match before it is labeled completed. Failed or mismatched readback retains an acknowledged but unverified advancement, pending/accounted interval and evidence. Cleanup is bounded wait→terminate→wait→kill→wait. An independent sampled watchdog also acts if a TraCI call blocks. Its inherited180s wall,60s startup,300MB output and5GB disk-reserve settings are bound in the card; scheduling/cleanup delay prevents a hard real-time guarantee.

## Logging binding and limits

Four exclusive regular files preserve native stderr, stdout, error-log and log. Each starts at byte0, including startup/control queries. Interval records bind source path/device/inode, offset, growing-prefix SHA-256, raw fragments, UTF-8 and newline status. Shrink/replacement/rewrite, partial stderr and stderr/error-log events stop; no manufactured empty-message declaration substitutes for native bytes.

Pinned SUMO1.26 source supports synchronous `OutputDevice_CERR::postWriteHook` stderr flush; `no-warnings=false` and `aggregate-warnings=-1` retain the reviewed path. This is **conditional synchronous CERR-before-ACK coverage**, tied to source/options/selected binary. Source-to-installed-binary/compiler equivalence remains unverified. File logs/stdout are provisional until normal owned-child exit0 and complete EOF. Ordinary buffered information can then be bound to the whole prefix, without invented per-step timing. Late critical messages, abnormal shutdown, missing EOF or unrecognized event text cannot clean-pass. [Official-source receipt](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/LOG_SOURCE_RECEIPT_R1.json).

An independent synthetic `Collisions: 0 / Teleports: 0` challenge exposed ambiguous V4 classification. Official MSNet516–537 emits optional event statistics only for positive counts; this zero format is not verified native output. V5 reports `UNKNOWN_LOG_PARSING_UNVERIFIED`, without claiming an observed native anomaly. The original challenge, V4 source/card and environment failure remain preserved; this is a parser-boundary correction, not a SUMO traffic result. A narrow ACK/readback regression was also added. Earlier V1–V4 tests do not cover these new cases.

## Offline interface and future launch gate

```sh
.venv/bin/python scripts/candidate_a_native_smoke_bridge_20261011_v1/cli.py --prepare
.venv/bin/python scripts/candidate_a_native_smoke_bridge_20261011_v1/cli.py --check-card artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE01/card.json
```

Existing unconsumed cards are checked idempotently, not overwritten. V2/V3/V4 snapshots and controlled update records preserve previous bindings. Prepared XML contains host-absolute paths; offline public checks are portable, but native launch checks its own checkout paths. A relocated checkout requires a controlled new card and renewed user authorization; this delivery does not certify portable native execution.

The supported native entry is `execute()`, gated before native imports/spawn/raw allocation by canonical `AUTHORIZATION_NATIVE_EXECUTION.json` and `engineering/EXECUTION_RELEASE.json`, binding run ID, exact card/source/input/environment and all three reviews. **Both are absent.** Future CLI shape is `--execute <card> --release <canonical release>`; this is an interface description, not an instruction or permission to execute. Receipt declarations are provenance gates, not cryptographic proof of human approval or an operating-system sandbox. The private fake-loop seam is not a supported runtime bypass.

Current card SHA-256: `7f74fa8cecb94a81e0d86a2ac2422fd10fa0ffcb3d7cf39a16bfa7d7f53b89d0`. Static environment: Python3.13.0, traci/sumolib1.26.0, sumoITScontrol0.1.0; interpreter, dependency Python files, selected SUMO binary and three installed top-level XSDs are bound. No dependency installation or native binary invocation occurred. This is not a full OS/native-build/transitive-XSD certificate. Full XSD validation was not run because lxml is absent. [Engineering review and exact verification](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/ENGINEERING_REVIEW.md), [V5 receipt](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/OFFLINE_VERIFICATION_RECEIPT_V5.json).

## Verification checkpoint

Engineering V5: **11/11 offline tests PASS**, fake connections/processes and actual temporary regular files only. Offline prepare/check and static own-root environment/hash check PASS;536 protected files and7 R2 bound files unchanged. Native starts0, actual TraCI connections0, allocated raw run0, formal runs0. These tests verify launch gating, log/accounting/failure plumbing; the empty fake world cannot validate native vehicle dynamics, real yellow/red response, physical safety or service capacity.

Independent [data review](../../data/processed/candidate_a_native_smoke_bridge_20261011_v1/FINAL_DATA_REVIEW.md) passes11 tests/6 representative probes and both offline CLI commands;26 engineering/48 data/536 protected/7 R2 bindings match. Two actual checker-assumption failures and fixes are preserved separately. Read-only [scientific review](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/FINAL_SCIENTIFIC_REVIEW.md): `PASS_FOR_BOUNDED_NATIVE_BRIDGE_OFFLINE_IMPLEMENTATION_DELIVERY`, subject to the delivered-code clean-checkout gate, unresolved Blocker/Major/required Minor0/0/0. ACK-time and log-wording findings were addressed.

Actual tested code `87d905b0c6aa6852447e21dfb0eb0ee4f4cd8789` in a fresh local no-hardlinks/single-branch checkout passed the11-test suite,6-probe public checker, default prepare, card check and expected foreign-root native-path rejection, each command once. Tracked status empty; raw only`.gitkeep`, no ignored A07 raw or current native output/authorization/release. [Actual output/receipt](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/clean_checkout/RECEIPT.json), SHA-256`70b2a122187a177fe9f0d44a2accb70d56cb12a291b8209c02a61b940da69414`. [Independent scientific readback](../../artifacts/candidate_a_native_smoke_bridge_20261011_v1/FINAL_DELIVERY_SCIENTIFIC_READBACK.md) matched real checkout HEAD, five output SHAs and all bound source/data/protected files without rerunning tests; the offline delivery gate is closed. Later changes only documentation/receipts; this final document head is not a separately executed implementation version.

Native warning timing, real child faults, first-red physical response and full actuator qualification remain NOT_RUN/NOT_VALIDATED. Old STOP3 remains bounded by its original guard and is not evidence that native red is unsafe.

## Documentation impact

PROJECT_STATE/WORKLOG and README record the new offline/runtime interface and review status. DECISIONS, EXPERIMENT_PROTOCOL, AGENTS, supervisor records and thesis structure remain unchanged. Technical and offline PASS must not be recorded as native safety/qualification or formal-experiment readiness. Next owner is user/Chat reviewing the implementation; any native smoke requires explicit subsequent authorization.
