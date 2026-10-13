# UA_FIXED300_S17_02 — post-run engineering review

2026-10-13. **PASS_FOR_BOUNDED_ENGINEERING_EVIDENCE_DELIVERY_ONLY; data and scientific post-run reviews pending.** One native launch completed at the approved end1272, with no retry or next-mode launch. This does not qualify Candidate A, ALINEA, physical safety or sustained service.

## Context and execution identity

Current PROJECT_STATE, AGENTS, DECISIONS, empty/unfrozen formal protocol and recent WORKLOG were checked. The user-approved scope plus exact-card engineering/data/scientific GO and canonical release authorize this isolated technical run. The source checkpoint recorded in current project state is89434dcc815d93d956466373197461cdea5ca4e5; the actual61-record source digest is independently bound by the card and verified unchanged after execution.

Card SHA49bcb2863acf9c0334cbcd9e398521978f4436514ee8d2350390233db90fc4b6; common runtime SHAa2b25659131bae5d9628ff5ab2f35e0c89987705daa5ef84a67ce426967b4b2b; canonical release SHA91a38e3f52a19455087a717f1af5c1d15f1d0d150a42cf14cbceb40b3671ea31. The command used the existing project.venv Python, not the mismatched system Python. No installation, version switch or source/card adjustment occurred.

```
/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python scripts/candidate_a_unified_alinea_20261013_v1/cli.py --execute artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_FIXED300_S17_02/card.json --release artifacts/unified_alinea_actuator_20261013_v1/engineering/releases/UA_FIXED300_S17_02/EXECUTION_RELEASE.json
```

Fresh source/input/environment/release/resource gates passed; available disk was39,171,702,784B. The reviewed environment is recorded in the execution receipt/card; the actual native log reports SUMO1.26.0. Tool session30160, CLI PID6651, owned SUMO PID6680, port50160 were observed. Connection completed on attempt243 at25.376826667s, within the60s startup limit. These are connection polls against one existing child, not new SUMO launches. A sandboxed read-only ps query was denied; escalated read-only observation succeeded without restarting.

## Actual observations

The actual final ACK and last accounting time are1272. Tool and owned-process return codes are0. The monitored timer, including startup, loop and owned-child cleanup, is **152.051050667s**; the loop checkpoint timer is152.030126167s. SUMO's separate native-duration statistic is126.430s and must not replace the monitored budget value.

| Cycle | Actual intervals G/y/r | Actual entries G/y/r | Requested E | Complete |
|---|---|---|---|---|
|1200–1224|4/5/15s|2/0/0|2|yes|
|1224–1248|4/5/15s|2/0/0|2|yes|
|1248–1272|4/5/15s|2/0/0|2|yes|

Aggregate C=requested6, mapped-pending6, applied6, E6 and independently recorded N6. All derived differences are0. The source did not cap N or force equality. Green ends were observed at1204/1228/1252; all reasons are ACTUAL_QUOTA_ACK at the4s maximum, not evidence of earlier-than-deadline closure. The first controlled red interval begins1209; its durable first ACK checkpoint is1210. This follows the approved current Y5 timing and does not reuse the historical1207/Y2 meaning.

The runtime produced1272 complete post-step records and2544 ACK journal lines, including1272 verified target/readback pairs. All72 controlled post-signal bindings and expected/actual nextSwitch checks passed. The actual command `fixed300:1200` was first confirmed from the bound G ACK1201, with application begin1200 and delay0; preparation alone was not counted as application.

All three fresh admissions were recorded at1200/1224/1248 and had available receiving space. All six actual entrant IDs have observed rear-clear ACKs; no censored body remains. All recorded native collision/teleport counters were0 and runtime rows contain no STOP reasons. This is recorded monitor coverage, not a global future-safety theorem. The three cycles ended on red with nextSwitch1272; the fourth green was not executed.

The final owned-process EOF bound all four native log streams,2547 capture records, and963 late informational sumo.log bytes. stderr, stdout and sumo_error.log were empty. Final status is `BOUND_NO_OBSERVED_NATIVE_MESSAGE`; the watchdog has no reason/error. The logger's existing conditional per-step coverage and unproven binary/compiler equivalence limits remain.

## Evidence freeze and pending checks

`RAW_FINAL_SHA256_V1.json` freezes **108 files /163,251,073B**, including both reservation files and every output/snapshot/receipt. SHA186dc2ddfe3ecc16be21ce8b067df68a79d4377b58bd9b64e4832a461b3efe8e. It is written outside raw; raw is now workflow-immutable.

`EXECUTION_RECEIPT_V1.json` SHA26b866aba6f91a96d50ddb32eb05c9f04e99aa0d5465a857008375ec3f8f1530 binds exact command, source, inputs, environment, resources, actual cycles, ACKs, entry/rear-clear IDs and full EOF. All61 current sources and their raw snapshots match the card; all536 old protected files are unchanged.

There are **1335 normal-arrival pending records**. Their precision8/tripinfo final-movement audit must be independently completed; engineering does not call that online coverage or mark it passed. Independent FCD/TLS/arrival/phase/command audit and scientific interpretation remain pending.

No settlement was created. Until both independent post gates finish, the budget guardian conservatively reserves300s/300MB for this one raw allocation; the actual152.051s/163.251MB values are reported but not silently released as available budget. No750/dynamic/ALINEA card or permission was prepared during this run. Parent owns factual STATE/WORKLOG updates and any approved subsequent release.
