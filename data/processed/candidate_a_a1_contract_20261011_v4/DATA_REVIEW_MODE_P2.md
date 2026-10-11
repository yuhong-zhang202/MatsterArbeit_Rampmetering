# PR #9 P2 mode/dynamics and red-observation combination — independent data review

2026-10-11. Project `data_analyst` `/root/issue8_data`. **Disposition: `PASS_FOR_BOUNDED_PR9_P2_MODE_DYNAMICS_RED_STATE_BINDING_CORRECTION`, pending delivered-commit clean checkout and scientific final readback.** This is an isolated offline classification correction, not a new safety contract or native safety result.

## Context, ownership and preserved evidence

New Context Preflight read AGENTS, PROJECT_STATE, DECISIONS, WORKLOG, empty/unfrozen EXPERIMENT_PROTOCOL and the previous PR #9 P2 final scientific review. Baseline was `618a6265da25fb533b6db88bd2aeddc311417aed`. Stage 6 closed/D-018, historical D-019, A1 UNRESOLVED_NEEDS_EVIDENCE/NOT_IMPLEMENTABLE_YET, A1/A2 unverified, STOP3, NOT_QUALIFIED, HOLD and 900 NOT_TESTED remain. No formal experimental analysis or protocol decision was performed.

Owned only the isolated independent checker and this new processed directory. [Pre-fix bindings](PRE_FIX_DATA_BINDINGS.json) preserve hashes for all **seven** previous processed files plus the V4 engineering binding; all **eight** hashes remain unchanged. [Old checker bytes](PRE_FIX_INDEPENDENT_CHECK_SOURCE.py) preserve SHA `450eae3747cea1677168a8c3d4f8d17fd49e4f28c98cea69a8b2a49987df1f0d`. Prior reports, receipts, bindings and failure records were not rewritten.

Before repair, [independent counterexamples](PRE_FIX_MODE_DYNAMICS_COUNTEREXAMPLES.json) actually reproduced four well-formed nonempty-red combinations: `speed_mode=0`, `lane_change_mode=0`, `action_step_s=2`, `tau_s=0.5`. Each incorrectly returned INELIGIBLE with `OBSERVED_RED_ANOMALY`; the expected whole-state binding classification is UNKNOWN without that anomaly reason. These were synthetic fixtures, not recorded traffic.

## Actual post-repair verification

After the engineering owner declared V5 stable, the analyst executed once:

```sh
python3 scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py --output data/processed/candidate_a_a1_contract_20261011_v4/POST_MODE_P2_INDEPENDENT_RECEIPT.json
```

[Independent receipt](POST_MODE_P2_INDEPENDENT_RECEIPT.json) binds the active [V5 engineering inputs](../../../artifacts/candidate_a_a1_contract_20261011_v1/review_fix_20261011/v5/INPUT_BINDINGS_V5.json), source/test/checker hashes, actual commands and complete stdout/stderr. The check executed the complete current unit suite and default public audit: **41/41 tests PASS; 0 FAIL, 0 ERROR, 0 SKIP; public audit PASS**, both return codes 0, using Python 3.13.0 standard library. Test-method counts and synthetic probe counts do not represent simulation repetitions or independent native observations.

The previous **19 red-schema probes** and **10 numerical/source-integer-domain probes** were re-executed unchanged and all passed. The analyst separately added **53 mode/red combination probes**, all passing:

| Independent combination | Count | Actual required behavior |
|---|---:|---|
| Four changed fields × front/follower/ingress/receiver roles × nonempty/empty red list | 32 | The 16 nonempty cases return UNKNOWN with no anomaly; the 16 empty-list cases retain old policy INELIGIBLE without anomaly. |
| Each of four changed fields on another enumerated follower/ingress/receiver, while red ID belongs to unchanged front | 12 | UNKNOWN; the entire supplied state is unbound, not just the vehicle whose ID is in the red list. No anomaly reason. |
| All four mismatches with positive red; same mismatches with empty red; multiple mismatches across two vehicles | 3 | Positive combinations UNKNOWN/no anomaly; empty-list policy control INELIGIBLE/no anomaly. |
| Mode mismatch combined with missing receiver, missing numeric vehicle field, malformed red list or stale measurement | 4 | UNKNOWN takes precedence; no anomaly reason. |
| Unchanged valid nonempty and empty controls | 2 | Valid bound synthetic positive remains INELIGIBLE/anomaly; empty remains UNKNOWN/no anomaly for unproved native/global obligations. |

Thus **53/53 new combinations +19/19 prior red-schema probes +10/10 numeric probes PASS**. This checks that the correction is selective: it does not erase empty-red policy denials, attach native-observation language to inconsistent mode/dynamics state or enable ELIGIBLE. The engine's 41 methods and its internal parameterized cases are separately recorded in its test log; this report does not conflate those counts with the analyst's 53 combinations.

## Identity, regression and interpretation boundaries

Active V5 binding SHA `f3d26d0df8a0e8c01f010953703d57f812b7e7213a83c5080e1d507c0a0e09b1`; tested helper SHA `8a0aa391471428305cb614f7c59391db9c427f099e98b4348b8d998b97a63ef6`; test SHA `2c6b5d2012be79ca58e264b54eb81c8cec0db295476b8ff9f4513907d51971f4`; independent checker SHA `3fe8dda4b33b148d968db86a82882650de29a30bd33ec1f5d0c317efb9696ae0`. All active file hashes match. [Independent normal-data regression](MODE_P2_NORMAL_DATA_REGRESSION.json) verifies that all **42** witness rows exactly equal the pre-fix V4 mapping.

Saved coverage stays **27 storage +15 ingress**, sole old guard refusal R_flow.1. Conditional scalar can-brake remains 42/42, actual full native branches determined **0/42**, refused-red observations **0**. All **536** protected old files match. The 1206 derived phase rows, six observation counts **[6,0,0,0,0,0]**, first partial C/applied C=0.5/E=0/N=1, five null/blank unobserved windows and zero complete cycles remain unchanged. No rate qualification is inferred.

Default tests/analysis read committed public evidence without ignored raw or network. They check supplied-schema consistency, bound source receipts/excerpts and derived phase accounting. The synthetic valid-positive case is not an A07 red crossing and is not independent event authentication. Historical local full-source/raw checks are retained with their earlier limits, not newly rerun or included in this public PASS. Parent must separately authenticate the actual delivered-commit clean checkout; that gate is not claimed here.

Required P2 classification finding is addressed within scope; unaddressed data-integrity Blocker/Major/required Minor: **0/0/0**, pending scientific review. Native stopping equations, A1/A2 contract, production guard/actor/config, raw and formal research design were not changed. No SUMO/TraCI/native movement or commit was performed by this analyst. Complete future affected inventory and joint native braking/follower/receiver safety still require evidence. Safest next step is scientific readback, clean delivery verification and bounded update of original Draft PR #9, then further user/Chat/GitHub review. No future runtime execution is authorized.
