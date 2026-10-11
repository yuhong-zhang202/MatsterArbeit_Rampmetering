# PR #9 third P2 — exact JSON integer phase validation V6

2026-10-11. User-authorized repair on original DraftPR9, no newIssue. Baseline `a41bf0fc57cb9aa971ac42bad191219c13d98d2e`, branch `codex/issue-8-a1-eligibility-contract`. Reviewer original source: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241992993 .

## Context Preflight

Read simulation_engineer instructions/AGENTS, current PROJECT_STATE, DECISIONS including D-018/D-019, current WORKLOG, 0-byte EXPERIMENT_PROTOCOL, finalV5scientificdelivery readback, actual reviewer text and current isolated helper/audit/test. Stage6 closed; A1 UNRESOLVED_NEEDS_EVIDENCE/NOT_IMPLEMENTABLE_YET, A1/A2 unverified. Current-contract STOP3/NOT_QUALIFIED/HOLD/highestqualifiedrateunknown/900NOT_TESTED retained. No formal protocol or runtime authorization. Only known unrelated MemoryCore/worklog/private-mail changes observed and preserved. Parent owns docs/PR/current state; analyst owns checker/new processed_v5.

## Pre-repair observation and minimal fix

Python considers True==1 and1.0==1. Preserved exact V5 helper/audit/test and binder bytes in v5_source_snapshot. PRE_REPAIR_COUNTEREXAMPLES_V6.json contains6actual synthetic calls: True/1.0/int1 crossed with empty/knownpositive ID lists. Two nonempty bool/float cases failed the expected UNKNOWN/noanomaly and returned INELIGIBLE/OBSERVED_RED_ANOMALY. The matched integer controls and empty-list cases retained for context. These are executable schema counterexamples, not native traffic observations.

V6 requires `type(phase_before) is int` before existing phase1/y/predictedr value checks; otherwise PHASE_MISMATCH enters UNKNOWN and existing red-state binding suppresses unsupported OBSERVED_RED_ANOMALY. Exact builtin-int is justified by this supplied JSON diagnostic schema (JSON integer decodes to Python int), and matches existing exact-int mode validation. It excludes bool (an int subclass) and float1.0; no coercion or expanded scalar semantics. Custom Python int subclasses are outside this JSON schema and are conservatively unknown. Integer1 with empty crossings remainsUNKNOWN; integer1 with validboundpositive remainspolicyINELIGIBLE/anomaly. No other typed fields, native equations, normative safety contract or state-binding policy altered.

## Actual offline verification

- `python3 -m unittest discover -s tests/candidate_a_a1_contract_20261011_v1 -v`: **43PASS/0FAIL/0ERROR/0SKIP**. Two new methods exercise24cases:10invalid/wrong phase values (True/False/1.0/0.0/None/string/dict/list/int0/int2) x empty/positive crossings=20, missingphase x2=2, integer1 matchedcontrols x2=2. Original41methods including prior red-schema/mode/dynamics compositions remain and pass.
- `python3 scripts/candidate_a_a1_contract_20261011_v1/audit_public.py`: PASS, defaultV6/offline/public-only. All42A07mapping rows equalV5; no actual fullbranch/red-observation added.
- Scoped `git diff --check -- <three owned source/test paths>` PASS. Protected536baselinehashes0drift. Of52priorV5bindings, only3authorizedhelper/audit/testbytes changed;49others unchanged. Newbinder adds preserved V5snapshot and pre-repair evidence; earlierbindings/results/receipts are untouched.

OFFLINE_TEST_RECEIPT_V6.json records actual argv/output/version/platform/source/test/binder/output hashes. Python3.13.0 standardlibrary only. Import/execution in complete suite validates isolated edits; no separate py_compile/nativeC++build or execution. SUMO/TraCIstarts0, no environment/install change. These are original-checkout tests; actual delivered-code cleancheckout is parent-owned and not claimed. Independent data/science follow after stablebytes.

## Boundaries and handoff

This is input typing, not newly authenticated native event evidence or complete safety proof.42savedwitnesses/27+15/fullnativebranch0/actualrefusedredobservations0/sixwindows[6,0,0,0,0,0]/0cycles remain. A1 fullpopulation, branch/action/device inputs, jointordinarybraking/follower/receiver proof gaps remain. No existing guard/actor/config/model/raw/native source/arithmetic/safetycontract/research/DECISIONS/protocol/upstreamPR change.

Engineering stops helper/audit/test writes, sends stableV6 to independent analyst then scientificreviewer. Parent handles current factual docs, actual delivery verification and originalPR9/reviewer response. No merge, user acceptance or future execution authorization is implied.
