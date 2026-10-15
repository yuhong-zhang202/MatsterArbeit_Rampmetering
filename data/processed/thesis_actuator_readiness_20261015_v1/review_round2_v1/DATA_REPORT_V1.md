# Review round2: request lifecycle and hard-cause binding

Result: PASS_OFFLINE_REVIEW_FIX_INTEGRITY_ONLY. Two reader P2 fixes and independent setter-failure evidence checks are complete for PR13 review. No native/SUMO, new natural fake-loop, runtime edit, merge, commit, push, run card or new Issue was performed. Natural service/safety/lifecycle qualification remains NOT_TESTED.

## Context, reviewed source and initial reproduction

Repeated project context preflight: AGENTS, STATE, DECISIONS, empty/unfrozen EXPERIMENT_PROTOCOL and recent WORKLOG; new USER_AUTHORITY and prior engineering/data/science scope apply. Stage6 remains closed exploratory, A1 UNRESOLVED/NOT_QUALIFIED. STATE's last published review-pending snapshot precedes the new review evidence supplied by root; root owns factual synchronization. No new formal parameters are inferred.

Root identified completed GitHub review5527104163 against actual commit24ec690de67818355076247f9192ed48a75ad390. Substantive reader comments4278226984 and4278226992 are the bounded assignment. Exact24ec reader preimages were preserved as NATURAL_REVIEWED_PREIMAGE.py and FINITE_REVIEWED_PREIMAGE.py and independently compared to `git show 24ec690de67818355076247f9192ed48a75ad390:<path>`; hashes match (REVIEWED_SOURCE_READBACK_V1.json).

Before edits, a short import/audit command actually demonstrated three false acceptances by those original readers: initial command status changed from SUPERSEDED_WITHOUT_APPLICATION to ACK_OBSERVED while deleting SUPERSEDED; cycle application_delay_s changed999; later hard-stop receipt error replaced by DiagnosticStop:UNRELATED_CAUSE. OLD_COUNTEREXAMPLES_ACCEPTED_V1.json records these expected failed protections. Original evidence/binders were not altered.

## Natural reader lifecycle fix

`scripts/natural_service_audit_20261015_v1/actual.py` now independently reconstructs each command's immutable nested fields from chronological REQUESTED events, first preparation from selected packet boundaries, first actual application from actual first-G ACK bindings, replacement/supersession and final status. It compares the entire final command record, not just ID/application. SUPERSEDED, PREPARED and ACK event counts, identities, nested command, chronology, request/application/preparation times and delays are bound. Packet ACK request IDs and held ACK clock/program are checked independently; first-application events follow preparation.

Each cycle is also bound to actual selected request ID, original request time, its own begin/end/planned application, request age, historical first application and delay, plus current application status. Important semantic distinction: a held packet can retain command_applied_s600/application_delay_s0 for a request first applied earlier. Those fields describe the request's history; held current applied_request_id/rate remain null. The reader preserves this distinction and does not force historical times to null or invent a new G ACK.

The same five existing natural saved bundles are reused, without rerunning their fake loop. Independent C/E_scheduled/E_executed/Cselected/Capplied/N results remain unchanged: at641 C=Cselected41/4, E_scheduled10; emptyN0/E_exec10/Capplied41/4; supplyN5; lateN4; blockedN4/E_exec8/Capplied33/4. blocked640 is complete with C10/E_scheduled10/E_exec8/Capplied8/N4. Natural terminal unapplied pending is still NOT_TESTED by those five cases; no fabricated pending observation was added.

## Finite hard-cause fix and evidence-version boundary

`scripts/pr13_service_scope_audit_20261015/audit.py` now requires a nonquota after-step hard stop's actual terminal ACK reasons and exact error correspondence: DiagnosticStop: followed by those observed reasons in order; retained terminal_reason, when available, must agree. It cannot accept an arbitrary nonempty receipt.error. New projected ACKs retain reasons and terminal_reason.

One new V2 bundle was generated from the exact existing finite two-car fake fixture with a single terminal M acceleration=-5 at1212, through the actual finite loop; no SUMO. FINITE_LATER_HARD_V2.json preserves the actual terminal reasons ['UNKNOWN_OR_EXCESSIVE_ACCELERATION:M_flow.0'], matching both DiagnosticStop:UNKNOWN_OR_EXCESSIVE_ACCELERATION:M_flow.0 and terminal_reason. Prior good packet assessment and complete prefix accounting C5/2,E2,N4 remain. Only this existing fake fault was run once; later checks reread V2.

Policy overquota is a distinct supported path: a completed N>2 assessment, exact ValueError:SERVICE_PACKET_QUOTA_EXCEEDED, boundary stop and no next packet. It does not mechanically require or fabricate adapter reasons that do not exist on that policy exception path. Previously generated pure-ledger/rebound synthetic overquota fixture remains explicitly synthetic, not physical movement evidence.

Old later_hard.json and old safety_priority.json lack projected reasons. They remain immutable and now explicitly reject with MISSING_HARD_CAUSE_EVIDENCE_OLD_PROJECTION_NOT_CERTIFIED. Their accounting history is preserved; their old projection cannot independently certify the stop cause under the repaired reader. No reasons were backfilled from receipt.error. Other prepare/UNKNOWN failure forms with only terminal_reason are outside this minimal supported cause-binding path and are conservatively incomplete/UNKNOWN, not automatically certified. No new failure-type matrix was added.

## Necessary offline verification

- Original-counterexample import command: exit0, three original false acceptances reproduced before edits.
- `.venv/bin/python -m unittest discover -s tests/natural_service_audit_20261015_v1 -p test_review_round2.py -v` — first affected group exit0,1method8.751s; generated the one V2 finite fake fault, audited five saved natural bundles and focused mutations. RESULT_V1.json retained.
- After packet-ACK request identity/order binding was tightened, same command final exit0,1method0.939s; V2 reused, no loop rerun. RESULT_V2.json includes14 focused rejections: superseded false ACK, missing SUPERSEDED, wrong nested command, wrong first preparation, missing PREPARED, wrong packet ACK request, wrong cycle delay, wrong held historical application time, wrong request time, wrong superseded nested command, unrelated hard error, missing hard reasons, wrong terminal reason and unrelated quota error. No unanticipated test failure occurred this round.
- `.venv/bin/python -m unittest discover -s tests/pr13_service_scope_audit_review_20261015 -p test_reader.py -v` — existing finite saved-data regression adjusted to explicitly expect old missing-cause noncertification; exit0,1method0.007s. No old evidence output was overwritten or loop run.

The first natural/finite preimages here are the reviewed faulty versions, preserved as original evidence; previous rounds' FAILs and source bindings remain unchanged. New source versions require the new binding, not old reader certificates.

## Independent read-only engineering setter boundary check

Engineering final source binding: artifacts/thesis_actuator_readiness_20261015_v1/engineering/review_round2_v1/ENGINEERING_BINDING_V1.json, SHA2569cace32950a7cff0404d167772e46ba8282962f149b473953c3ca49fc1feba29 (45files). Read only the four saved fixed_failure_bundles 0_setter,600_setter,600_readback,603_yellow and checked all bound file hashes. No engineering test/loop was rerun.

Command `.venv/bin/python data/processed/thesis_actuator_readiness_20261015_v1/review_round2_v1/check_setter_evidence.py` — exit0, FOUR_SAVED_SETTER_BOUNDARIES_PASS_NO_EXECUTION. Source script and result SETTER_BOUNDARY_READBACK_V1.json are retained.

The independent checks bind attempted setter, returned/partial success and final failed/UNKNOWN record; stop receipt exactly names its durable last setter. Actual clock/last verified ACK/accounted times are0/null/null,600/600/600,600/600/600 and603/603/603. No later advance or false G application occurred; at600 no movement G ACK exists even if an API returned. At0/600 the program can be installed before phase-call failure; this is preserved as partial control, not no effect. At600_readback phase remains UNKNOWN/null with getter error while other observed fields remain; no inferred expected phase replaces it. At603 expected yellow failed while actual getter still showsG/phase0. Failed-call effects remain UNKNOWN_POSSIBLE_PARTIAL_APPLICATION. Getter state is explicitly not movement ACK.

This is a saved API-fault boundary evidence check only. It does not expand the natural reader to a general pre-motion failure framework, native EOF, physics or safety qualification. No additional tests/matrix are requested.

## Handoff and limits

Generated/edited only the two readers, their bounded tests and new review_round2_v1 evidence. Runtime changes belong to engineering. New DATA_BINDING_V1.json binds exact current source/tests, reviewed preimages, V2 hard data, test results, this report, source readback and engineering final binding/evidence. Old raw/data/governance untouched.

Root should minimally record both repaired reader P2s, old projection limitations and actual review version in STATE/WORKLOG/problem records and request the authorized final bounded PR13 review after scientific reconciliation. Latest noSUMO/no-merge boundary remains; no natural-service/native qualification can be inferred. Safest next step is read-only scientific final review and the authorized existing PR publication/review, with remaining untested domains explicit.
