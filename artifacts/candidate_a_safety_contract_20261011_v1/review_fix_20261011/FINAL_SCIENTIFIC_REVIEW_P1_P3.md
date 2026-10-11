# PR #7 P1/P3 scientific re-review — 2026-10-11

**Disposition: `PASS_FOR_BOUNDED_PR7_P1_P3_CORRECTION`.** This records the read-only `scientific_reviewer` review after the `data_analyst` correction and final readback. It concerns audit portability and rate-list wording only. It does not approve A1/A2, relax the current guard, qualify Candidate A, or authorize a SUMO run.

## Reviewed evidence and delivery gate

The reviewer completed the project Context Preflight and reviewed the revised audit/test, versioned [data review](../../../data/processed/candidate_a_safety_contract_20261011_v2/DATA_REVIEW_P1_P3.md), original A07/V3 bindings, and the [clean-checkout receipt](DELIVERED_CODE_COMMIT_CLEAN_CHECKOUT_RECEIPT.json). Commit `9861bcbfcef5e027f452b01a6702d3738d95faeb` contains the five V2 processed files. An independent clean clone at exactly this commit had no ignored A07 raw; seven unit tests passed with zero failures/errors, and the default public audit returned `PASS` (exit 0). The reviewer confirmed these facts and lifted its prior delivery condition.

The default audit verifies the committed guardian/snapshot/cycles/crossings, bound V3 gate and six windows, 42 recorded witnesses, and 1206 contiguous rows in a **derived** thin phase ledger. It does not independently reconstruct the original raw `phase_steps.csv`. The separate `--verify-local-raw` check passed on the original local checkout and compared the thin fields with all 1206 raw rows; that check cannot be reproduced from a clean public checkout. Earlier V1 `5/5` receipt/review remain historical local-checkout records, not public reproducibility proof.

## Five measurement checks

| Check | Re-review conclusion |
|---|---|
| Target | PASS for the recorded A07 guard refusal, 1206 s prefix and six planned windows; no rejected red motion step was executed. |
| Coverage | PASS for 42 saved witnesses (27 storage, 15 ingress) and six-window observation accounting `[6,0,0,0,0,0]`. Future vehicle/foe coverage under A1/A2 remains **NOT_VERIFIED**. |
| Omission/duplication | PASS for unique saved witness identities, 1206 derived thin rows, one crossing and no complete cycle. The five wholly unobserved windows remain missing, not measured zero. |
| Independent accounting | PASS within the local raw replay and committed-evidence binding. Public clean-checkout audit checks the bound derivative, not independent reconstruction from raw. |
| Regression | Seven tests PASS in clean clone, including measured zero, partial, fully unobserved, and absence of ignored raw. These tests do not validate native red safety or an unimplemented A1/A2 contract. |

P3 wording now correctly identifies **four** unexecuted fixed rates: 450, 600, 750 and 900 veh/h. The recorded current-contract STOP3 and Candidate A `NOT_QUALIFIED` remain supported within their previous bounds. Neither a physical unsafe native-red result nor universal Candidate A infeasibility follows. No new SUMO/TraCI start occurred. Remaining action is user/Chat review of PR #7; any new safety contract or execution requires separate authorization.
