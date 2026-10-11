# PR #9 P2 red-observation input-expression correction

2026-10-11. Original PR #9 / Issue #8; baseline efe870e74fd44922ab20fbc68255e3d0687195b9, branch codex/issue-8-a1-eligibility-contract, base remains PR #7 branch. User explicitly authorized repair on original PR without a new Issue. [Reviewer P2](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241840268).

## Defect and exact correction

The former truthiness check accepted malformed/unbound red IDs and wrote INELIGIBLE/OBSERVED_RED_ANOMALY. A valid-looking list with stale state returned UNKNOWN but still carried that unverified observation reason. Real pre-repair synthetic probes and exact old helper/audit/tests/checker bytes are preserved; these are not traffic observations.

The isolated offline diagnostic now requires an explicit list of unique nonempty/non-whitespace string IDs, belonging to the valid affected inventory equal to enumerated vehicle IDs, and no unknown source/time/phase/link/vehicle/receiver state before attaching the anomaly. Missing/malformed/foreign/duplicate IDs or state mismatch yield UNKNOWN without OBSERVED_RED_ANOMALY. Valid empty list remains UNKNOWN/noanomaly; valid positive bound synthetic input yields policy INELIGIBLE. No ELIGIBLE path is added. The old positive test incorrectly used foreign ID `front`; it now uses actual fixture ID `synthetic_front`.

This implements the already specified missing/unbound→UNKNOWN distinction. It does not change the A1/A2 safety contract, native source predicates, numerical/physical margins, phase timings, production guard/actor/worker/config or research design. Schema binding is not independent authentication of actual native event provenance; no per-crossing timestamp/link field or native telemetry is fabricated.

## Versioned evidence and public scope

Current [V4 input binding](v4/INPUT_BINDINGS_V4.json), [engineering receipt](v4/OFFLINE_TEST_RECEIPT_V4.json), [engineering review](v4/ENGINEERING_REVIEW_V4.md) and [correction receipt](v4/CORRECTION_RECEIPT_V4.json) preserve V3 exact source/binding and pre-repair failures. [Historical61 delivery hashes](PRE_FIX_DELIVERY_BINDINGS.json) and original main-report bytes remain archived. Current [independent data review](../../../data/processed/candidate_a_a1_contract_20261011_v3/DATA_REVIEW_P2.md) and final binding retain the old checker and all original data/bindings. No old receipt/result/review is overwritten. V3-only default binding pointers in prior reports remain historical; active public audit/checker now use V4.

Engineering and independent analyst actually executed **37 PASS / 0 FAIL / 0 ERROR / 0 SKIP** and public audit PASS. Independent **19 red-observation probes +10 numerical probes PASS**: invalid/missing/stateunbound→UNKNOWN without anomaly; validempty→UNKNOWN; validpositive→policyINELIGIBLE. Python3.13.0 stdlib, no ignoredraw/network dependency. All42 saved A07 mappings equal V3,27storage+15ingress, actualfullnativebranches0/42/refusedredobservation0. Sixwindows remain[6,0,0,0,0,0],partialC/appliedC.5,E0,N1,fivemissingnull,0cycles.536protectedfiles unchanged.

Public audit binds published receipts/excerpts and derived thinphase data. It cannot reconstruct complete original raw phase data, certify a native binary, or validate red movement/future-world/follower/receiver safety. Prior actual V3 code-commit cleanclone remains historical; the new V4 delivered-code clone is a separate gate, recorded below after execution.

## Review and handoff

Engineering→data→[scientific source/data review](SCIENTIFIC_REVIEW_P2_SOURCE_DATA.md) complete: PASS_FOR_BOUNDED_PR9_P2_RED_OBSERVATION_EXPRESSION_CORRECTION, no unresolved delivery findings; actual delivered-code gate remains separately pending. Factual PROJECT_STATE/WORKLOG and the main report's verification pointer are updated; normative specification untouched. DECISIONS, EXPERIMENT_PROTOCOL(0B), AGENTS, originalraw, historicalresults and upstreamPRs unchanged.

**A1 UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET**, A1/A2 unverified, current-contractSTOP3, NOT_QUALIFIED,HOLD,unknownhighestqualifiedrate and900NOT_TESTED remain. SUMO/TraCI/nativeC++starts0. This correction supplies no new traffic evidence or safety approval. User/Chat review next; no future static/runtime/smoke execution is automatically authorized.

## Delivered-code verification and final review

Actual tested code commit **a88f234541db7aa640048342e297efcc92888b63** was cloned independently with `--no-hardlinks --single-branch`. The independent checker actually ran37tests/publicaudit/19red+10numericprobes, allPASS; ignoredA07raw absent andtrackedstatus empty. [Actual clean-checkout receipt](DELIVERED_P2_CODE_CLEAN_CHECKOUT_RECEIPT.json) preserves argv/output/source/inputSHA and embedded independent result; [final scientific readback](FINAL_SCIENTIFIC_REVIEW_P2.md) verifies the actual clone/JSON/hash and closes the gate. Later only docs/receipt updates preserve all code/47input/7data/536protected hashes; no final documentationHEAD test is falsely claimed.

Current correction complete for review, with no unresolved delivery findings. OriginalV3historical cleanclone and allprevious reviewcheckpoints remain as their actualtestedversions. CurrentV4 is bound here, withP2 addressed butno newtraffic/safety evidence. NextoriginalDraftPRupdate/replyanduser/Chatreview; no newreviewtrigger/merge/Issueclose orscopechange.
