# PR #9 reviewer P2 — engineering correction V4

2026-10-11. Baseline `efe870e74fd44922ab20fbc68255e3d0687195b9`, branch `codex/issue-8-a1-eligibility-contract`. Original PR correction explicitly authorized; no new Issue or scientific decision. Reviewer: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241840268 .

## Preflight and bounded scope

Read project/agent instructions, current PROJECT_STATE, DECISIONS including D-018/D-019, WORKLOG recent Issue8/delivery entries, 0-byte EXPERIMENT_PROTOCOL, Issue8 snapshot, V3 scientific review/final delivered-code readback, current helper/audit/tests and actual reviewer comment. Stage6 remains closed. A1 is UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET; A1/A2 unverified. STOP3, NOT_QUALIFIED, HOLD, highest qualified rate unknown, 900 NOT_TESTED remain. No new formal or runtime authorization. Existing MemoryCore/worklog/private-mail work preserved. Parent owns current report/state/worklog/PR; analyst owns independent checker/processed outputs.

## Real defect and correction

The V3 truthiness check classified synthetic malformed string/true/dict/duplicate/empty/foreign IDs as INELIGIBLE with OBSERVED_RED_ANOMALY. Valid known IDs in stale time/source states returned UNKNOWN but retained the unsupported observed-anomaly reason. These actual pre-repair invocations are retained in PRE_REPAIR_COUNTEREXAMPLES.json; exact V3 helper/audit/tests and original binding bytes are in v3_source_snapshot. They are synthetic schema tests, not new native traffic observations.

V4 requires a unique list of nonempty/non-whitespace string IDs, a valid unique nonempty-ID affected inventory equal to enumerated vehicle IDs, and crossings within that inventory. Existing local source/time/phase/program/link/vehicle/receiver checks must have no UNKNOWN reasons before anomaly is attached. Missing/malformed/unbound/inconsistent inputs yield UNKNOWN without OBSERVED_RED_ANOMALY. Valid [] remains UNKNOWN without anomaly. Valid known positive IDs in an otherwise consistent supplied state yield demonstrable policy INELIGIBLE. Unknown evidence still takes precedence; no ELIGIBLE path is introduced. Supplied schema consistency is not independent attestation of real native crossing provenance or complete future coverage.

Only isolated helper validation, public-audit current binding pointer and tests changed. Native source predicates, arithmetic domains, existing guard/actor/config and all A1/A2 contract definitions remain unchanged. The formerly positive test used unbound `front`; it now uses the actual synthetic inventory ID `synthetic_front`, preserving a meaningful positive control instead of accepting the original test's unbound evidence.

## Actual verification

- `python3 -m unittest discover -s tests/candidate_a_a1_contract_20261011_v1 -v`: 37 PASS / 0 FAIL / 0 ERROR / 0 SKIP. Four added methods cover missing/None/string/bool/dict/duplicate/empty/whitespace/nonstring IDs, malformed/foreign/inconsistent inventory, stale source/time/event/phase/link/invalid vehicle/receiver states, valid empty and valid bound positive controls. Existing 33 method coverage remains, with the bound-positive fixture corrected.
- `python3 scripts/candidate_a_a1_contract_20261011_v1/audit_public.py`: PASS using V4; default public-only with no ignored raw/network dependency. All42 A07 mappings equal V3; saved full native branches0/42/red outcome unobserved remain.
- Protected baseline rehash:536 checked,0 drift. Of42 V3 bindings, exactly3 authorized helper/audit/test files changed; other39 inputs unchanged. V4 additionally binds preserved historical bytes and pre-repair evidence.
- Scoped `git diff --check`: PASS, no output. No py_compile needed beyond actual execution/import by complete suite; no native C++ build or execution. SUMO/TraCI starts0.

OFFLINE_TEST_RECEIPT_V4.json records actual commands, Python3.13.0/platform, source/test/input hashes and output hashes. INPUT_BINDINGS_V4.json is the active public binding; V3 binding/receipt/log/output and other original histories are not overwritten. These are original-checkout tests; actual delivered-commit clean-checkout is parent-owned and not claimed here. Independent data/scientific re-review is pending at this engineering checkpoint.

## Disposition and handoff

P2 implementation correction ready for independent data/science review. No current-contract STOP3 or runtime safety conclusion changes. 42 historical witnesses and 6/0/0/0/0/0 window coverage are untouched; no new actual red observation. A1 global population/finalized speed/follower/receiver proof gaps remain. Parent must synchronize current factual documents, record actual delivered-code verification, update original Draft PR #9 and respond to reviewer. Next-step suggestions confer no simulation, contract or formal research authorization.
