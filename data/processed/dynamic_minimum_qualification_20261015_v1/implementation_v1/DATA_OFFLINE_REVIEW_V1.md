# Independent data review — approved native-gap diagnostic implementation

2026-10-15. Status: **GO_FOR_EXACT_CARD_REVIEW_ONLY**. No native execution authorization or actual tracking qualification is provided by this report. Exact final cards are not available at this report version; they require a separate readback receipt.

## Context and authority

AGENTS, PROJECT_STATE, DECISIONS, EXPERIMENT_PROTOCOL and relevant WORKLOG reviewed. Current work is an isolated technical diagnostic under USER_APPROVAL_V1.json (direct human “批准，请继续”), the reviewed proposal and MEASUREMENT_REVIEW_RESOLUTION_V1.md. Formal protocol remains empty/unfrozen. Stage 6, prior STOP/FAIL, A1 and service qualification states are unchanged. Original old dynamic cost 147.8151898329961 s is historical and separate from the new two-run 600 s envelope. Each new run remains 300 s, startup60 s, free disk5GB, no byte cap, end1296. No new SUMO run or raw audit was performed here.

## New analysis files and independent checks

New exact-ID actual/scope reader reuses repaired followup parsing and protected independent accounting/phase/Feedback/identity/FCD/body/arrival/EOF routines. It does not import the production Ledger as mathematical truth. Only UA_NATIVEGAP_DYNAMIC_S17_01 and UA_NATIVEGAP_ALINEA_S17_01 are accepted; original raw/results and the repaired historical reader are untouched.

current_gap.py independently binds vehicle/leader, clock, route, path geometry, modes, actual speeds, fresh leader pair and query arguments (unchanged leader emergency deceleration9). It recomputes the native-query hard floor and the full retained legacy +1.1 m comparison, with the existing 1e-9 arithmetic tolerance. Below-floor observations remain alarms. Only hard-floor-pass/legacy-fail records become a separate advisory; their raw values, legacy failure status and unsupported safety claim remain explicit. Empty lookahead observations have null query/pass values, not a successful secure-gap query. Unknown/missing or inconsistent fields are rejected. The new policy applies only to current-following records; original strict prospective/new-G admission and receiving-space checks remain in the execution and reused analysis path. This is not an independent proof of all microscopic SUMO decisions.

tracking.py reconstructs original request integrals, real entry counts and three residual terms at each complete packet boundary: selector forecast residual, midpacket request change and 2−actualN. Actual C/N over a partial interval remains separate from E for completed packets. Per-phase counts are null when that phase has no observed exposure; a measured zero remains zero. Four scheduled requests must actually apply within0…23 s. Period changes are not required when successive requests choose the same period. After final300 application, chronological complete-boundary reduction from any positive deficit must be observed; an explained but unrecovered deficit is insufficient. No instant-zero or invented percentage threshold is added. Real Feedback requires noninitial actual command application and uses the unchanged independent E1/own-previous calculation. Finite diagnostic status and data integrity are separate; all long-run/full-range qualification flags remain false.

## Actual offline verification

Command: `python3 -m unittest discover -s tests/dynamic_minimum_qualification_audit_20261015 -v`.

Final run: 3 methods PASS, 0.075 s, exit0, exact source hashes in OFFLINE_RECEIPT_V1.json and TEST_LOG_V2.txt. The earlier three-method PASS log is retained as TEST_LOG_V1.txt; before final freeze the recovery calculation was refined to require chronological recovery, then the same affected small suite was rerun. No failed test or native output was removed.

Coverage: joint current-gap floor/legacy-advisory cases plus wrong clock/mode/ID/policy/required floor/missing pass-field rejection; clear/null semantics; existing engineering helper synthetic dynamic and real Feedback records independently rechecked through mathematical and phase readers; three residual terms/final300 recovery/partial E/null; separate single300/combined600 budget, nonzero history and early-stop rejection. Synthetic entry trajectories are software fixtures, not physical service evidence. Their N14, request311/24 or application times are not native expectations or acceptance targets.

## Limits and next handoff

This work did not execute the complete actual native pipeline, inspect new raw data (none available), test the new bridge end-to-end or prove future safety/service. New precise card/source binding remains pending. A later native run must preserve all FCD/TLS/dual-ACK, source/input/environment, strict braking, complete identities/nonactive pools, yellow, body, normal terminal movement and four-stream EOF checks. Terminal AFTER nonactive pools remain a single-journal scope where no next same-time PRE exists. Private native decisions and binary/source equivalence are not newly proven. Missing command ACKs cannot be replaced by a derived physical application for full success.

No governance files were edited by the data agent. Parent owns the documentation impact update and required engineering/scientific review. Next step: exact final card/source readback, then scientific gate. No unconditional ALINEA release or budget settlement is implied.
