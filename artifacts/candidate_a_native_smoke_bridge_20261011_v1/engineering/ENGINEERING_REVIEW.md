# Native phase smoke bridge — engineering delivery V5

## Status and authority

Minimal real-process/TraCI bridge code is implemented and statically bound; **no SUMO, native binary, actual TraCI connection or raw run was executed**. User accepted proposal `833ac18db2c6b256f2782631830c9c849e090681` and requested implementation for review, not runtime launch. Current canonical native authorization/release files are absent. `execute()` rejects before native import/process/output allocation. Default CLI prepares or checks offline. Private `_diagnostic_loop` is an injection seam for fake tests, not a supported independently authorized runtime entrypoint or security sandbox.

Context reviewed: AGENTS, PROJECT_STATE, DECISIONS, WORKLOG, empty EXPERIMENT_PROTOCOL, current proposal, R2 adapter and protected Candidate A worker/actor/guard/phase/configuration helpers. Stage 6 closeout is unchanged; formal protocol remains unfrozen, A1 unresolved and historical STOP3 preserved. No research, model, guard, old executor or upstream change.

## Implementation

New bridge reuses protected worker observe, phase requests, child launch/connect helpers and R2 adapter/CycleLedger. It copies tracked public A07 demand/native phase configuration, preserving demand bytes and G3/y3/r18. New package changes paths/end/logging only. Identity M3600/R900/U360/X180, seed17, service command300veh/h, activation1200, step1s, first activated red1206→1207 mandatory close/pause. Precontrol red603 remains monitored. Receiver/native-red admission is checked before green program/phase setters. No direct forced-red request, automatic continuation or rate qualification.

All old checks remain; only unsupported prospective envelope is the existing isolated R2 advisory. Post checks detect and preserve evidence after motion, not prove/prevent that step's safety. An empty-world fake test is pipeline verification, not dynamic/native vehicle safety evidence.

ACK is retained immediately with requested target; actual simulation time is read back and verified before labeling completed time or log intervals. Failed/mismatched readback retains ACK/target and unverified advancement rather than inventing actual time. Failure prefix, pending/accounted interval, original logs and manifests are retained. Owned child cleanup uses bounded wait→terminate→wait→kill→wait. A .2s sampled watchdog independently terminates the owned child on wall/output/disk caps even if an API call blocks. Scheduling and termination delays mean these are not exact hard-real-time bounds.

## Log scope and uncertainty

Regular-file stderr/stdout/log/error-log capture binds inode, device, source path, byte0 cursor, monotonically growing prefix, UTF8, newline and SHA. Startup, setters, queries, step ACK and close are covered. Pinned MsgHandler options add error-log receivers without removing stderr; no-warnings=false and aggregate-warnings=-1 preserve the reviewed synchronous CERR flush path. Exact source/compiler equivalence is **NOT_VERIFIED**; CERR before-ACK association remains a conditional engineering argument, not all-native-message/safety certification.

stdout and file logs are PROVISIONAL until normal owned process close, returncode0, wait and EOF. Ordinary buffered info may be bound only to the whole prefix. Missing/replaced/shrunk/partial streams, unknown EOF/nonzero close or critical late messages cannot clean-pass. Any stderr/error-log bytes stop. Critical or unrecognized event text in stdout/log remains unknown. Official MSNet516–537 only emits optional event statistics when counts are positive. The synthetic `Collisions: 0 / Teleports: 0` format has no verified native source, so V5 labels it **UNKNOWN_LOG_PARSING_UNVERIFIED**, with no claimed native anomaly; it is not accepted as a source-supported clean summary. No generic full log parser was introduced.

## Controlled corrections and environment

V1 8 tests passed; V2/V3/V4 each9 passed. Those earlier suites did not cover zero-summary classification or ACK/readback failure. V4 source/card/test bytes and incomplete system-Python environment are preserved in PRE_LOG_ZERO_AND_ENV_V4. Actual pre-fix zero counterexample is PRE_LOG_ZERO_COUNTEREXAMPLE_V4.json. The snapshot utility initially failed at Python module import after preservation; PYTHONPATH retry generated the counterexample without modifying preserved bytes.

V5 source/card adds only narrow log-expression/ACK fixes, private-loop boundary and project `.venv` environment rebinding. Current metadata is Python3.13.0, traci1.26.0, sumolib1.26.0, sumoITScontrol0.1.0. Binary hash matches inherited static receipt; no binary invocation. Environment binds interpreter, dependency .py files, binary and three top-level installed XSD files; it is not a complete OS/native-build or transitive-XSD audit. XML parses and installed option declarations were inspected; full XSD validation was not run (lxml absent, no installation authorized).

Resource180s wall/60s startup/300MB output/5GB reserve references are inherited from the protected runner SHA in card.resources_provenance. Exact future runtime approval must bind this card; hash receipts do not substitute for human authorization or native qualification. Prepared absolute paths are canonical-own-root checked before launch, so a foreign checkout cannot launch using another checkout's outputs/environment. Public preparation and tests use tracked inputs, never ignored A07 raw/private XML.

## Actual verification and handoff

- `.venv/bin/python -m unittest discover -s tests/candidate_a_native_smoke_bridge_20261011 -v`: **11/11 PASS**, fake process/connection and real temporary regular files only; log OFFLINE_TEST_LOG_V5.txt.
- `.venv/bin/python scripts/candidate_a_native_smoke_bridge_20261011_v1/cli.py --prepare`: PASS idempotent offline check; PREPARE_RECHECK_OUTPUT_V5.txt.
- same CLI `--check-card <canonical card>`: PASS; CARD_CHECK_OUTPUT_V5.json.
- `.venv/bin/python` calling `validate(card,require_environment=True)` without execute: PASS static own-root/binary/dependency/hash check, STATIC_RUNTIME_CARD_CHECK_V5.json; **not prelaunch/native PASS**.
-536 protected files and all7 R2 bound files: unchanged; PROTECTION_RECEIPT_V5.json. Existing raw run path does not exist. Source hashes, exact inputs, package/card and outputs: INPUT_BINDINGS_V5.json / OFFLINE_VERIFICATION_RECEIPT_V5.json.

New native smoke, real first-red behavior, runtime warning timing, child cleanup under real native faults and physical safety remain NOT_RUN/NOT_VALIDATED. Old A1 result is not reversed. No clean checkout claim yet; parent will perform actual independent checkout. Data and science review must complete before user reviews exact runnable card and chooses whether to authorize one native smoke. No continuation or formal experiment is authorized by this delivery.
