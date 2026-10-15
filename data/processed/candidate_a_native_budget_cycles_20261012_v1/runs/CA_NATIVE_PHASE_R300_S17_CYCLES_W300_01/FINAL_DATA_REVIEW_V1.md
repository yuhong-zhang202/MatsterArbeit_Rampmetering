# W300 independent postrun data review

2026-10-12 Europe/Berlin. **PASS_FOR_BOUNDED_RECEIVER_MONITOR_STOP_DATA_INTEGRITY_ONLY. No unresolved data-expression finding.** Actual firstred/three-cycle objective NOT_REACHED; this is not safety/service qualification. Current guard refused a next-vehicle receiving condition, not a wall-budget failure or proof of physical danger.

## Context, inputs and scope

Fresh AGENTS/STATE/DECISIONS/WORKLOG/known0B EXPERIMENT_PROTOCOL preflight. STATE initially lagged as actualstartpending; parent corrected it to actual1201 receiver STOP before substantive audit. User goal covers four sequential technical budgets subject to reviews and STOP/unknown conditions; Stage6/oldSTOP3/A1UNRESOLVED/CandidateANNOT_QUALIFIED/900NOT_TESTED remain. Only this new processed run namespace written. No SUMO/TraCI/version process, raw/controller/guard/model/phase/demand edit, olddata scan, optional old test suite or new run.

Execution source20e5e83ac059768320cdaa4c815d164e1022de45/card25dccfa39d3ff716823f6ce7ceee18eba1c0b8c6393ae464b6db1d2b61c70386. Engineering12-file binderb4b58f08978d32e23cfe2daa165cdf26e1a4c017bd3fd3f1398f97ec791e4297, frozen67raw/61,712,498bytes manifest9d87bca24c48b8536a2e5307fa8c957b4581eaa149a2eb876d2b07ccb05298df. All actual raw SHA/bytes and coverage matched; executed source snapshots and exact card bound. Full raw local-only; public processed summaries do not recreate it.

## Actual independent observations

Versioned run-specific audit V3 exit0 independently matches **1201 contiguous FCD timestamps0..1200, native rampTLS frames, pre/post world lane/speed/ID, actualACK1..1201 and2402ACKpairs**, including terminal retained reconciled row. FCDt is after movement for(t,t+1], matched to ACKt+1; no timestamp reassignment to obtain a desired count. One globally unique R_flow.0 enters storage→controlledinternal in **(1200,1201] under G**, cycle0. Exact crossingID/bracket/motion agrees with the ledger and native TLS. E1 downstream observations are not used for meter N.

Only **one controlled second** was observed: C=C_applied=1/12=0.08333333333333333vehicles; E=0, N=1, C−E=1/12, E−N=−1. E is the nominal packet posted at cycle completion1224, which was not reached; a crossing before E posting does not mean negative physical service or qualification. Cycle0 is PARTIAL1/24s, observedgreen1/3s/N1. Whole observed-prefix contributions N_y/N_r are0 because that prefix was green only; these must not be read as measured yellow/red phases. Phase-specific yellow/red discharge is null/NOT_OBSERVED in RECEIVER_READBACK_V1.json. Cycles1/2 (1224..1248 and1248..1272) and all their C/appliedC/E/N/deltas are null. 1203yellow,1206red,1207checkpoint and all complete cycles are NOT_REACHED. No missing observations filled with zero.

Only reported alarm is POST_GREEN_RECEIVER_DENIED on completed/accounted1201. Watchdogreason/errornull. Monitoredwall throughcleanup126.1785716250015s, below300s; nativeDuration100.89s and wholeCLI126.60562050002045s are distinct timing scopes in engineering records, not CPU shares or paired speedups. Exact native4stream finalEOF is BOUND_NO_OBSERVED_NATIVE_MESSAGE, returncode0/allstreamsbound; native stderr/stdout/error0B,sumolog1018B,2404captures independently bound at final byte counts/hashes. ParentCLI compatibility-warning bytes remain separately bound and outside perstep native onlineSTOP coverage. No universal warning-free claim.

Serialized braking values/IDs checked over the observedprefix:143,720 before∩after speed-difference vehicle-intervals;1,263 before-only/arrived exclusions; final after-population accelerationIDs199. No extra brake/collision/teleport/red-crossing alarm found in serialized observations. Last movement of arrived/before-only vehicles is excluded; recorded accelerations are TraCI values, not independent full physical safety proof. Final receiver STOP occurs before any controlledyellow/red test.

## Receiver value binding and mechanism

receiver_readback_V1.py exit0 matches actual pre/post/engineering selected FCD and source excerpts. Beforecontrol frontR0 had available=True; both R0/R1 were stopped in storage. Afterone legalR0 entry, nextfront is **R1**, stopped at195.9879543879801m; leaderR0 is oninternal at0.3142695877042456m, speed/acceleration1.3153111228020862m/s andm/s². FCDprecision2 independently shows R0internalpos0.31/speed1.32; R1storagepos195.99/speed0.00. The observed front identity changed, without stale/unbound IDs found.

Both existing predicates reject the **next entry**:

- Internal leaderrear clearance=0.3142695877042456−5=**−4.685730412295754m**, belowfrontlength5+minGap2.5=**7.5m**. The entered vehicle's front crossed while its rear still spans the stopline.
- getLeader gap excludes egominGap: **1.3163151997241584m** < recordedsecureGap2.6 + unchangedmargin1.1=**3.7m**. Actual bumpergap reconstruction is1.3163151997241584+2.5≈**3.8163151997241584m**; do not misstate the excluded gap as full bumpergap or subtract minGap twice. Worker first marks INTERNAL_RECEIVER_CLEARANCE then overwrites reason with LEADER_SECURE_GAP; both failed values are preserved.

The bound secure_gap_query source uses frontcurrentSpeed+accel×1s, so for stationaryR1 it queries **hypothetical2.6m/s prospective release**, not actual0m/s. Query inputs are reconstructed from source/observed state; the complete query tuple is not separately serialized and no native getter was rerun. Recorded getSecureGap result2.6m is evidence of that implementation's returned value, not a newly derived stationary-queue safety threshold. This STOP does not establish the stopped queue is physically dangerous.

Confirmed: the current monitor acted on bound, genuinely insufficient next-entry values under its current contract. No sampling/identity/phase-prediction defect was demonstrated. Unresolved: whether a nextfront's unavailable prospective release should terminate an already-active nativegreen, rather than merely describe temporary queueing. That is guard-responsibility semantics; no data audit authorizes deleting/relaxing it. Absence of native alarms does not prove continuation safe, SUMO unsafe or CandidateA infeasible. Morebudget cannot itself change this receiver predicate.

## Actual parser failures, corrections and verification

Original generic audit V1 exit1/UNKNOWN because it expected raw_root+raw_immutable_after_owned_process_exit fields while the engineering freeze uses immutable_raw_root/run_id/file_count. V2 exactmanifest/wrapper adaptation exit1/UNKNOWN because entries are {sha256,bytes}, not hashstrings. Neither result demonstrated raw drift: the comparison assumptions were wrong. Both actual output/receipt/source versions remain. V3 checks exact frozen manifest digest, dictkeys/hash/bytes and unwraps only one terminal receipt with pendingNone, completeaccounting and exacttime. V3 audit passed. No raw/ledger/controller change.

One minimal schema-regression method executed actual V3 AST clauses on tiny valid/invalid {sha256,bytes} entries and terminalwrapper cases, exit0. Existing engineering11/measurement5/old8 suites not rerun. All these versions and receipts remain; shared prelaunch tool was not silently overwritten. No additional optional checks or native rerun.

## Handoff

Data delivery suitable for read-only scientific postreview, with no unresolved data finding. Actual user objective incomplete: only W300 ran; W360/420/480 unstarted. Retain receiver STOP and seek a separately reviewed responsibility/contract decision before further runs; neither larger allowance nor automatic technical retry remedies it under unchanged checks. No formal evidence, sweetspot, full native safety or sustainedrate qualification follows from this one controlledgreen second.
