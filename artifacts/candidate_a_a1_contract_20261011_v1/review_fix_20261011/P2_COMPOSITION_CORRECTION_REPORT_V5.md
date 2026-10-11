# PR #9 P2 mode/dynamics red-evidence binding correction — V5

2026-10-11. Authorized repair on original Draft PR #9, starting head 618a6265da25fb533b6db88bd2aeddc311417aed. Finding: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241919567 . No new Issue.

## Repair and version boundary
Valid nonempty red IDs combined with MODE_OUTSIDE_PINNED_CONTRACT or DYNAMICS_OUTSIDE_PINNED_CONTRACT now return UNKNOWN with RED_CROSSING_EVIDENCE_UNBOUND_TO_STATE and no OBSERVED_RED_ANOMALY. Empty-red mismatch keeps the prior policy INELIGIBLE. Other legitimate policy denials are not globally converted to UNKNOWN. Valid bound synthetic positive remains INELIGIBLE/anomaly; no ELIGIBLE path.

Only isolated diagnostic, public audit binding, independent checker and tests change. Native predicates, A1/A2 normative contract, production guard/actor/config, raw and formal design stay unchanged. Previous V4 tests did not cover this nonempty-red composition; their broad consistent-state coverage is superseded in this respect, not retrospectively rewritten. Exact previous sources/bindings, 16 engineering and four independent actual pre-fix counterexamples are retained under v5/v4_source_snapshot and processed V4. Old reports/receipts remain historical.

## Verification
Engineering V5: 41 PASS/0 FAIL/ERROR/SKIP, with four new methods and 56 internal composition subcases. Independent data: 53 new combinations plus 19 prior red-schema and 10 numeric probes PASS; public audit PASS. These are distinct synthetic counts, not traffic observations. Python 3.13.0 stdlib; commands and full source/input SHA-256 in [engineering receipt](v5/OFFLINE_TEST_RECEIPT_V5.json) and [data review](../../../data/processed/candidate_a_a1_contract_20261011_v4/DATA_REVIEW_MODE_P2.md).

42 saved witnesses remain identical (27 storage/15 ingress); conditional canBrake 42/42, actual full native branch 0/42, refused-red observations 0. Six windows retain [6,0,0,0,0,0], first partial C/applied C=.5/E=0/N=1, five unobserved null/blank, zero complete cycles. 536 protected files unchanged. Default audit binds committed public receipts/excerpts and derived thin ledger; it does not reconstruct ignored raw or authenticate synthetic crossings as native events.

Engineering → data → scientific source/data review PASS within this bounded classification repair. Actual delivered-code clean-checkout verification pending; final delivery receipt will record actual commit and location independently of inner checker generic pending fields. No runtime verification claimed.

## Remaining state and handoff
A1 UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET, A1/A2 unverified, current-contract STOP3/NOT_QUALIFIED/HOLD, highest qualified rate unknown and 900 NOT_TESTED remain. SUMO/TraCI starts 0. Formal protocol remains empty/unfrozen. Stage 6 prior closeout retained. Complete inventory/native branches/joint follower-receiver proof is still absent. User/Chat next reviews this Draft; next-step suggestions do not authorize execution. No upstream PR changes.
