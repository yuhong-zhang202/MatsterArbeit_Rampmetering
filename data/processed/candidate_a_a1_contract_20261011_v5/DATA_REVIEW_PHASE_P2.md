# PR #9 P2 phase-index type correction — independent data review

2026-10-11. Project `data_analyst` `/root/issue8_data`. **Disposition: `PASS_FOR_BOUNDED_PR9_P2_PHASE_INDEX_TYPE_CORRECTION`, pending delivered-commit clean checkout and final scientific readback.** This concerns supplied-schema classification only; it neither changes A1's normative safety contract nor validates native traffic safety.

## Context and preserved history

New Context Preflight read AGENTS, PROJECT_STATE, DECISIONS, WORKLOG, empty/unfrozen EXPERIMENT_PROTOCOL and latest V5 scientific delivered-code readback. Baseline HEAD was `a41bf0fc57cb9aa971ac42bad191219c13d98d2e`; this repair addresses reviewer comment `4241992993` on original PR #9. Stage 6 closed/D-018, historical D-019, A1 UNRESOLVED_NEEDS_EVIDENCE/NOT_IMPLEMENTABLE_YET, A1/A2 unverified, STOP3, NOT_QUALIFIED, HOLD and 900 NOT_TESTED remain.

Owned only the independent checker and this new processed directory. [Pre-fix binding](PRE_FIX_DATA_BINDINGS.json) records the previous **seven** data files and V5 engineering binding; all **eight** hashes remain unchanged. [Old checker bytes](PRE_FIX_INDEPENDENT_CHECK_SOURCE.py) preserve SHA `3fe8dda4b33b148d968db86a82882650de29a30bd33ec1f5d0c317efb9696ae0`. Previous reports, receipts, source versions and failures were not overwritten.

[Independent pre-fix counterexamples](PRE_FIX_PHASE_TYPE_COUNTEREXAMPLES.json) actually show `phase_before=True` and `phase_before=1.0`, each combined with a locally bound nonempty red-ID list, incorrectly returning INELIGIBLE with `OBSERVED_RED_ANOMALY`. Python value equality let bool/float aliases pass the old `phase_before!=1` check. The current isolated helper requires the supplied phase index to be an exact integer before applying its existing value constraint. These counterexamples are synthetic schema inputs, not actual native red observations.

## Actual independent tests and results

After the engineering owner declared V6 stable, the analyst ran the complete checker **once**:

```sh
python3 scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py --output data/processed/candidate_a_a1_contract_20261011_v5/POST_PHASE_P2_INDEPENDENT_RECEIPT.json
```

[Independent receipt](POST_PHASE_P2_INDEPENDENT_RECEIPT.json) records active [V6 bindings](../../../artifacts/candidate_a_a1_contract_20261011_v1/review_fix_20261011/v6/INPUT_BINDINGS_V6.json), exact source/test/checker hashes and real commands with full output. The checker actually executes the complete unit suite and default public audit: **43/43 tests PASS, 0 FAIL, 0 ERROR, 0 SKIP; public audit PASS**, both return codes 0, Python 3.13.0 standard library. The engine's new two methods include its own phase subcases; this report separately counts the analyst's independent inputs.

All previous **53 mode/red combinations**, **19 red-schema probes** and **10 numerical/source-integer-domain probes** were re-executed and passed. The analyst added **38 independent phase-type/red combinations**, all passing:

| Independent challenge | Count | Result |
|---|---:|---|
| True/1.0/False/0.0/string `"1"`/None × empty/nonempty red list | 12 | UNKNOWN without `OBSERVED_RED_ANOMALY`. |
| True/1.0 × four mode/dynamics mismatches × empty/nonempty red list | 16 | UNKNOWN takes priority over local policy denials; no anomaly reason. |
| Exact integer phase 1, empty/nonempty red controls | 2 | Empty remains UNKNOWN for unproved global/native obligations; locally valid synthetic positive remains INELIGIBLE/anomaly. |
| Wrong integer phase 0/2 × empty/nonempty red | 4 | UNKNOWN/no anomaly. |
| True/1.0 with unknown receiver | 2 | UNKNOWN/no anomaly. |
| True/1.0 with a mode mismatch on another enumerated ingress vehicle | 2 | UNKNOWN/no anomaly. |

Thus **38/38 new +53/53 prior mode/red +19/19 prior red-schema +10/10 numeric probes PASS**. Counts refer to offline synthetic input/math checks, not simulation repetitions or native observation coverage. Invalid phase types cannot attach the observation label; valid integer controls and prior empty-red policy behavior remain intact. No ELIGIBLE path is enabled.

## Version identity and unchanged normal evidence

V6 engineering binding SHA `6e7044c6ca8b052660568485f3391b645c6948c75f984b092ccb97c446186724`; helper SHA `55b1c39a2d2466c2ab06d05cf327ed9db08a70f6c78a751c1d77c000ac94c3d8`; test SHA `e52afcc930a1e4b53831d2338a8d6023f522ad34c2a3835553d0c2deb62871b3`; independent checker SHA `024c206f383881516bded2ed203a0fb05b6031c923358fb5fb3a0bac76adff7f`. All active hashes match.

[Independent normal-data regression](PHASE_P2_NORMAL_DATA_REGRESSION.json) confirms **all 42 witness rows exactly equal** the V5 mapping: 27 storage +15 ingress, sole old refusal R_flow.1. Conditional scalar can-brake remains 42/42; complete actual native branches determined **0/42** and refused-red observations **0**. **536** protected old files have zero drift. The 1206 derived phase rows, six observation counts **[6,0,0,0,0,0]**, partial first-window C/applied C=0.5/E=0/N=1, five null/blank unobserved windows and zero completed cycles remain unchanged. No rate qualification follows.

## Limits and next gate

Default tests/checker require committed public evidence, no ignored raw and no network. They bind source receipts/excerpts and **derived** phase accounting. Supplied-schema consistency is not independent event authenticity, binary/source certification or observation of the refused 1206→1207 movement. The valid-positive fixture remains explicitly synthetic; historical local full-source/raw checks are not newly rerun or added to this public PASS.

The targeted P2 classification finding is addressed; unaddressed data-integrity Blocker/Major/required Minor: **0/0/0**, pending scientific review. Actual delivered-commit clean checkout remains the parent gate and is not claimed here. Complete future population, native branch inputs and joint finalized-speed/follower/receiver safety remain unverified. No SUMO/TraCI, production guard/actor/config, source stopping predicate, A1/A2 contract, raw, research-design/protocol or upstream change was performed by this analyst; no commit was made. Next is final scientific readback and bounded update of original Draft PR #9, then user/Chat/GitHub review. No execution authorization is implied.
