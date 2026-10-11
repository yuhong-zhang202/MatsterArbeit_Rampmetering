# PR #9 P2 independent data re-review

2026-10-11. Project `data_analyst` `/root/issue8_data`. **Disposition: `PASS_FOR_BOUNDED_PR9_P2_RED_OBSERVATION_EXPRESSION_CORRECTION`, pending delivered-commit clean checkout and scientific readback.** This concerns the isolated diagnostic's handling of supplied red-observation IDs. It does not validate A1/A2, establish an actual native-red anomaly or change current-contract STOP3.

## Context and version control

New Context Preflight read AGENTS, PROJECT_STATE, DECISIONS, WORKLOG, empty/unfrozen EXPERIMENT_PROTOCOL and PR #9's latest delivered-code scientific readback. Baseline HEAD was `efe870e74fd44922ab20fbc68255e3d0687195b9`. Stage 6 closed/D-018, historical D-019, A1 UNRESOLVED_NEEDS_EVIDENCE/NOT_IMPLEMENTABLE_YET, NOT_QUALIFIED, HOLD and 900 NOT_TESTED remain. This is exploratory offline data/schema validation, not formal experimental analysis.

Owned only the independent checker and this **new** processed directory. [Pre-fix historical binding](PRE_FIX_DATA_BINDINGS.json) records the six previous data files and original V3 engineering binding; all seven hashes remain unchanged. [Old independent checker bytes](PRE_FIX_INDEPENDENT_CHECK_SOURCE.py) preserve SHA `f0c4075450e16022de63becae90cc8bd352df6cda09141e97abc6a97bc733f5c`. Prior DATA_REVIEW, final bindings, receipts and all recorded failures remain historical evidence; the current checker uses a newly versioned V4 engineering binding rather than silently updating them.

[Independent pre-fix counterexamples](PRE_FIX_RED_IDS_COUNTEREXAMPLES.json) actually reproduce malformed string, dict, non-string member, empty ID and unbound ID incorrectly returning INELIGIBLE with `OBSERVED_RED_ANOMALY`. These are synthetic schema inputs, not observed traffic.

## Actual independent validation

[Post-fix independent receipt](POST_P2_INDEPENDENT_RECEIPT.json) records active [V4 input hashes](../../../artifacts/candidate_a_a1_contract_20261011_v1/review_fix_20261011/v4/INPUT_BINDINGS_V4.json), exact tested source/test/checker hashes, real commands, return codes and full outputs. [Normal-data regression](P2_NORMAL_DATA_REGRESSION.json) independently compares the old V3 and new V4 witness mappings.

The analyst executed the following once after the engineering owner declared the V4 files stable:

```sh
python3 scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py --output data/processed/candidate_a_a1_contract_20261011_v3/POST_P2_INDEPENDENT_RECEIPT.json
```

That command actually ran the complete current offline unit suite and default public audit. **37/37 tests PASS, 0 FAIL, 0 ERROR, 0 SKIP; public audit PASS, both command return codes 0.** Python 3.13.0 standard library only. Ten numerical/source-integer-domain probes were re-executed and all passed, including finite extreme fail-closed and 32766/32767-step boundaries.

The analyst additionally constructed **19 independent red-ID schema probes**:

| Cases | Count | Observed result |
|---|---:|---|
| String/dict/non-string member/empty ID/whitespace ID/duplicate ID/unbound ID/None/bool | 9 | UNKNOWN; no `OBSERVED_RED_ANOMALY` reason. |
| Missing red-ID field | 1 | UNKNOWN; no anomaly reason. |
| Stale measurement time or next switch, mismatched source/link/program/inventory, nonfinite state time | 7 | UNKNOWN; no anomaly reason. |
| Valid empty red-ID list with otherwise locally consistent state | 1 | UNKNOWN for existing unproved native/global obligations; no anomaly reason. |
| Valid unique red ID bound to supplied vehicle/inventory and locally consistent state | 1 | INELIGIBLE with `OBSERVED_RED_ANOMALY`. |

**19/19 PASS.** The final positive case is a deliberately supplied **synthetic** observation record used to validate classification. It is not an actual A07 red crossing. No counterfactual red movement or new native observation was produced.

The repair checks the existing schema's source/time/measurement/switch/phase/program/link/vehicle/inventory consistency and red-list shape; it introduces no additional crossing timestamp/link field. Therefore this is validation of supplied schema consistency, not independent authentication or reconstruction of the crossing event. Real event provenance and post-step observation remain obligations of any future separately authorized runtime implementation.

## Preservation and evidence limits

All active V4 input hashes match, including helper SHA `b60a62fd92bbc514cb2a7dc248bf7ba311d1229f52c834123da3cb93177d84de`, test SHA `9fbac0171385dfdf8cbc607aa4b20c85eb8c069832c11a1f237fa39c75b04502` and engineering binding SHA `ccdbf53c391563824bcb40ebee375309ff29cf6e6e74814ee53e5dcd607fe1c2`. Independent checker SHA is `450eae3747cea1677168a8c3d4f8d17fd49e4f28c98cea69a8b2a49987df1f0d`.

All **42** saved witness mappings exactly equal the prior independent V3 mapping: 27 storage +15 ingress; sole old guard refusal R_flow.1; conditional scalar can-brake 42/42, actual full native branches determined 0/42. **536** protected existing files have zero drift. The 1206 derived rows, six window counts `[6,0,0,0,0,0]`, partial first-window C/applied C=0.5/E=0/N=1, five null/blank unobserved windows and zero complete cycles remain unchanged. No rate qualification is inferred.

Default analysis and tests read committed public evidence only, without ignored raw or runtime network access. They bind published source receipts/excerpts and **derived** phase data. Historical local full-source/raw checks are not newly executed and are not folded into this public PASS. The parent will record the delivered-commit clean-clone test separately; this report does not claim that gate has already run.

The P2 data-expression finding is addressed within this scope; unaddressed data-integrity Blocker/Major/required Minor: **0/0/0**, pending final scientific review. A1/A2 safety, complete future inventory and joint native braking/receiver/follower bounds remain unverified. No SUMO/TraCI starts, production guard/config changes, raw changes, protocol change or research-design decision occurred. Safest next step is scientific readback and bounded update of original Draft PR #9, then user/Chat/GitHub review. No execution authorization follows.
