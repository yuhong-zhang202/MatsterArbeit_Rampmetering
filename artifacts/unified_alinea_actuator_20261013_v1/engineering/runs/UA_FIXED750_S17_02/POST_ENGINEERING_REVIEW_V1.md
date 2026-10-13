# UA_FIXED750_S17_02 engineering post-review V1

**Completed at ACK1270 / CLI exit0; GO for independent data → science post-review only. Actual service shortfall remains: E14/N13.**

## Bound execution

One native start, no retry; exec session51177, CLI PID20079 / owned SUMO20102, port54563. Card `fb4beb8a89d71c213a916dd57840abdd7b3bc8733552e7bd6dc6e1d921d6f192`; canonical release `457b56f32d8107fe3d9c54ad3389e0a4724e726d3b93a1b3c6dabece29d82290`; current64-record runtime `ea180197848843bd3cca7d326a7016454fe8bd0db406302a64ad11f03347b29b` over source commit1749e040. All64 current/snapshot hashes still match. Existing `.venv` and SUMO1.26 environment unchanged; no version command/install/extra tests or next card.

Actual command:

```text
.venv/bin/python scripts/candidate_a_unified_alinea_20261013_v1/cli.py --execute artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_FIXED750_S17_02/card.json --release artifacts/unified_alinea_actuator_20261013_v1/engineering/releases/UA_FIXED750_S17_02/EXECUTION_RELEASE.json
```

Fresh exact source/card/env/release gates PASS. Startup connected24.332838709s (limit60). Single300s/raw300000000B/free5000000000B preserved. Monitored elapsed including startup/cleanup **152.48386508296244s**. Raw parent frozen111files/**163770536B**, manifest `c8d6e35fd9144124447739dce8bd4598ff4f9f63cefc57b0e48458bb01d97815`; manifest is outside raw. No raw edit or removal. This raw identity remains conservatively reserved300s/300MB until independent data and scientific post gates; engineering does not settle its budget.

## Observed execution and honest vehicle accounting

Requested750 mapped720/T10; same Gmax4/y4/min-red2/quota2/seed17/end1270. Seven completed G4/Y4/R2 cycles. First six release2 each, seventh releases1 under MAX_GREEN_DEADLINE. All13 entries G; yellow/red entries0. Actual C=14.583333333333334, mapped-pending=applied=E14, N13, E−N1. Complete horizon makes this a real one-vehicle nominal shortfall, not an unobserved window or partial-cycle artifact. No green extension, timing change, quota forcing, seed selection or service qualification claim.

First-red checkpoint ACK1209 (red began1208), provisional bound at that point and final EOF bound after close. Seventy control clock/journal rows;1270 total post rows. Thirteen entrant bodies observed rear-clear, no censored body at terminal. 27 post WAIT classifications. All observed native collision/teleport counters0; no remaining stopping reasons. Final four native streams bound at process EOF, native returncode0, no critical/unrecognized native message. Runtime retains terminal-arrival audit as pending independent final-tripinfo verification:1337 normal arrived IDs in journal, not a realtime full exit-braking claim.

## Approved numerical event, not hidden normal-braking PASS

Exactly one explicit classification at BEGIN1264→ACK1265 for R_flow.13, first yellow of cycle7. Native speed4.69222772465427→0.19122772465426985, raw delta/native alpha both **−4.501 m/s²**. Storage position203.97137014006898→204.16259786472327m, vehicle length5m; route, technical_passenger, modes31/1621, all original dynamics, bound times/card/run/program I12_PACKET10/phase integer1/link, full world/body and fresh original current-gap checks recorded. Both before/after current-gap statuses observed within the unchanged emergency9 + margin1.1m bound. No new front entry from this vehicle.

`legacy_braking_reasons` retains ORDINARY_BRAKING_EXCEEDED:R_flow.13 and UNKNOWN_OR_EXCESSIVE_ACCELERATION:R_flow.13. Only these two reasons were removed from this run's active stopping set under the user's explicit approved finite-event exception, with raw values unchanged. Source-compatible conditional Euler1mm reference and `actual_branch_identified=false`/`native_safety_proven=false` are preserved separately. It does not establish which private native branch generated the event, general ordinary braking compliance, or safety qualification. Original750/01 strict STOP evidence remains untouched.

Original FrameCache Python UserWarning about floating-point step API appeared on the calling tool output and is retained in this execution history; it is not a native safety log or an environment change. First sandbox ps was denied, then authorized read-only ps obtained ownedPID; no re-launch occurred.

## Remaining gates and safest handoff

Independent data analyst must reconcile111hashes/complete inventory, FCD/TLS/ACK/crossings, measured numerical before/after bindings/legacyFAIL, 13tails/freshreceiver/logEOF, and1337 normal terminal arrivals with precision8 BEGIN/arrivalSpeed. Scientific reviewer then judges bounded technical scope and whether service shortfall blocks any original dynamic/closed-loop diagnostic. No next simulation, permission card or budget settlement here. Stage6/A1/CandidateA qualification/formal protocol unchanged. Parent owns STATE/WORKLOG updates.
