# PR13 reader P2 fix: two hard-stop classification defects

Result: PASS_SYNTHETIC_READER_INTEGRITY_ONLY; no native run/service qualification. Scope is the old finite reader only, separate from the forthcoming natural-demand implementation. No old processed evidence/binder/report was changed.

## Context and reviewed version

Context remains the new USER_AUTHORITY thesis-readiness goal, Stage6 closed exploratory, A1 UNRESOLVED/NOT_QUALIFIED and empty/unfrozen protocol. Current STATE still contains the prior finite task; root owns its integration. Required project files were read during this task stream and latest state/worklog rechecked. Reviewer actual commit6dc1680 was identified by root; exact committed reader preimage was retrieved with `git show 6dc1680:scripts/pr13_service_scope_audit_20261015/audit.py` into READER_6DC_PREIMAGE.py.

Root supplied two substantive findings: discussion_r4278071195 (overquota assessment incorrectly expected N>=2 target success), and discussion_r4278071201 (hard stop incorrectly required no prior assessments). These incorrectly rejected correctly preserved anomaly evidence. The new source version must not be confused with the original6dc reader or previous reader binding, which remain historical.

## Minimal reader change

`scripts/pr13_service_scope_audit_20261015/audit.py` now classifies completed actualN<2 as neutral target failure, N=2 as finite target observed, and N>2 as SERVICE_PACKET_QUOTA_EXCEEDED. Overquota requires a corresponding hard-stop receipt at that packet boundary and no later packet. It does not become a service pass.

For a hard current-packet failure, prior complete good assessments are accepted and required in sequence. Current assessment is absent if original reconciliation failed, or may be the explicit overquota assessment after successful original reconciliation. A current neutral assessment cannot mask a hard stop; the original error and terminal STOP status remain required. Existing exact interval/C/E/N/assessment binding, partial checks and no-neutral-continuation checks remain.

## Targeted verification and provenance

Command: `.venv/bin/python -m unittest discover -s tests/pr13_service_scope_audit_review_20261015 -p test_reader.py -v`

One focused method/group, final exit0,1 method,0.008s. It reuses saved synthetic regression bundles when present; it does not launch SUMO. Source for generating the two bundles is retained in the test.

- Overquota: existing finite Ledger finish_packet(...,3), assess_completed_packet and require_diagnostic_target produce actualC25/12,E2,N3,C−N−11/12 and ValueError SERVICE_PACKET_QUOTA_EXCEEDED at1210. The saved one_exact ACK template is explicitly rebound to three distinct synthetic crossings/post-world IDs with arithmetic N fields adjusted and ledger-generated assessment. Service context comes from that existing synthetic template. This is an arithmetic-ledger/reader-schema anomaly fixture, not an actual three-vehicle adapter trajectory or physical source/readiness proof. Provenance is embedded in overquota.json. The6dc reader rejects it; corrected reader accepts observation-accounting integrity and HARD_OR_UNKNOWN_GATE_STOP.
- Later hard stop: existing ScopeTests.run_fixture('two',end1212) through the actual finite adapter/inherited loop, with only Fake World M getAcceleration=-5 at1212. This has a first complete good packet and a second partial when the original braking gate fails. Actual reconstructed C5/2,E2,N4,C−N−3/2,end1212. No current assessment is emitted; the previous good assessment survives. The6dc reader rejects it; corrected reader accepts integrity and HARD_OR_UNKNOWN_GATE_STOP. Synthetic movement is not a SUMO safety result.
- Re-read all four previous saved bundles (empty,one_exact,partial,safety_priority) with the new reader; all accepted with their original target/hard/partial classifications and unchanged independent C/E/N reconstruction. No old fake suite rerun.
- Five focused invalid variants rejected: overquota falsely marked observed target, missing hard-stop class, misbound assessment endpoint, malformed ACK interval, and a current partial neutral assessment attempting to mask hard braking.

First command attempt exited1 after8.191s due to a test-harness typo `scope.UNDER` instead of exported `UNDER_TARGET`. Both new regression bundles, their6dc failure checks/new acceptance, four old saved audits and first four mutations completed before that harness failure. ATTEMPT1_TEST_PREIMAGE.py and ATTEMPT1_FAILURE.txt preserve the failure. Corrected only the harness name/current assessment template; final command reused those bundles, so the fake loop ran once, not again after correction. No claim that the first command passed or that a full old suite/native test was run.

## Boundaries and handoff

Generated source/test and new data files are hash bound in DATA_FIX_BINDING_V1.json. It binds the exact6dc reader preimage, old finite runtime/fixture dependencies, new reader/test, old saved input files, new bundles/result/failure receipts and this report. Binding hashes check file identity, not physical validity. Older data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1/ bindings still refer to the pre-P2 reader and must not be reused as a current-source certification.

No src runtime, simulation configuration, old154 source/card/raw, previous report/binding, research metric/protocol or governance file was edited. No SUMO, native start, merge, commit, push or review request. Natural-demand ordinary continuation qualification remains a separate outstanding task. Root should record this material data fix in its minimal worklog/state update and incorporate it into the authorized next review round. No additional tests are requested by this report.
