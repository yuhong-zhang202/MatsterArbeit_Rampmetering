# PR #9 second P2 — vehicle-contract/red-observation composition V5

2026-10-11. User-authorized original PR repair, no new Issue. Baseline `618a6265da25fb533b6db88bd2aeddc311417aed` on `codex/issue-8-a1-eligibility-contract`. Reviewer source: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241919567 .

## Context Preflight and scope

Read AGENTS, current PROJECT_STATE, DECISIONS including D-018/D-019, WORKLOG current PR9/V4 entries, EXPERIMENT_PROTOCOL (0 bytes), V4 engineering/final delivered-code scientific records, current helper/audit/test and reviewer original comment. Stage6 remains closed, formal protocol unfrozen. A1 UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET; A1/A2 unverified; current-contract STOP3, NOT_QUALIFIED, HOLD, highest qualified rate unknown and900NOT_TESTED remain. Parent owns docs/state/worklog/PR; analyst owns independent checker/processed_v4. Unrelated MemoryCore/worklog/private-mail changes preserved.

## Actual pre-repair evidence and limited correction

V4 stored out-of-contract speed/lane-change modes and action-step/tau mismatches in policy `deny`, so its `unknown`-only red-state gate failed to reject the composition with valid nonempty known IDs. Real pre-repair calls on preserved V4 bytes reproduce16 failed expectations (four mismatched fields x four roles), all INELIGIBLE with unsupported OBSERVED_RED_ANOMALY. PRE_REPAIR_COUNTEREXAMPLES_V5.json retains exact synthetic inputs/results; v4_source_snapshot preserves byte-exact contract/audit/test and original V4 binding. These are software-schema counterexamples, not native observations.

V5 adds only MODE_OUTSIDE_PINNED_CONTRACT and DYNAMICS_OUTSIDE_PINNED_CONTRACT to the red-state binding gate **when a valid bound crossing list is nonempty**. Such compositions return UNKNOWN without OBSERVED_RED_ANOMALY. Existing deny reasons remain for transparent policy context. Empty crossing lists still produce original mode/dynamics policy INELIGIBLE. Pinned-state valid positive crossings still produce policy INELIGIBLE/anomaly. Other genuine policy denials (e.g. receiver blocked, committed front) are not globally converted to UNKNOWN. V4 malformed/unbound/stale UNKNOWN rules and noELIGIBLE boundary remain. No new schema/provenance certificate, physical threshold, native source predicate or normative A1/A2 contract change.

## Actual offline verification

`python3 -m unittest discover -s tests/candidate_a_a1_contract_20261011_v1 -v`: **41PASS / 0FAIL / 0ERROR / 0SKIP**. Four new methods exercise56 explicit combinations:

| Composition | Cases | Expected |
|---|---:|---|
| four fields x front/follower/ingress/receiver with nonempty known crossings |16|UNKNOWN, no anomaly|
| matched16 cases with empty crossings |16|original policyINELIGIBLE, no anomaly|
| four roles x pinned empty/pinned positive/positive+receiverblocked |12|UNKNOWN / INELIGIBLE / INELIGIBLE; last two retain valid anomaly|
| four roles x all mismatches+receiverblocked / othervehicle modes+committedfront / othervehicle dynamics |12|UNKNOWN, no anomaly, preserved relevant deny reasons|

The prior37 methods remain and pass. `python3 scripts/candidate_a_a1_contract_20261011_v1/audit_public.py`: PASS using new INPUT_BINDINGS_V5.json, offline public-only; all42 A07 mappings equalV4. Protected baseline536files checked,0drift. Of47 prior V4 bound entries, exactly3 authorized helper/audit/test files changed;44 remaining bytes unchanged. V5 adds historical V4 snapshots and actual pre-repair receipt to the active binding without modifying prior records. Scoped `git diff --check -- <three owned code/test paths>` PASS.

OFFLINE_TEST_RECEIPT_V5.json records actual argv/stdout/stderr/version/platform/source/test/input hashes. Python3.13.0 standardlibrary only. No nativeC++ build/execution, SUMO/TraCI starts0, no installation or environment change. Test execution/import validates these isolated Python edits; no separate py_compile or simulations were needed. Actual delivered-code cleancheckout remains parent-owned and pending at this engineering checkpoint. Data/scientific independent re-review is required before final delivery.

## Scientific and preservation boundaries

No existing guard, actor, production runner, network, phase, model, raw, source excerpt, arithmetic rule, report, receipt, approved decision, formal protocol or upstream PR modified.42savedwitnesses/27+15population/fullbranch0/refusedredobservations0, sixwindows[6,0,0,0,0,0],0completecycles remain. Supplied schema binding is not independently authenticated native event evidence. Full population/ordinary braking/follower/receiver safety gaps remain; this correction cannot establish runtime safety, qualification or sweet spot.

Engineering stops writing helper/audit/tests and hands stableV5 to analyst, then scientificreviewer. Parent synchronizes factual current-pointer/state/worklog, performs actual delivered-code check, updates original DraftPR9 and replies to this reviewer. No future runtime authorization, merge or user acceptance is implied.
