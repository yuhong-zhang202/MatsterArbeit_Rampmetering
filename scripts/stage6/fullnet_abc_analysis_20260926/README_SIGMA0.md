# M-only sigma=0 diagnostic analyzer

`analyze_sigma0.py` is for the separately reviewed altered-driving-model R0/A technical sensitivity. It does not start SUMO, reuse historical nonpairable A, declare a traffic phenomenon, or calculate a causal fraction of the default-model A result. It reads immutable raw, verifies full input/output receipts, and creates a **new** processed directory only after static, lifecycle, pre-R pairability and R-exposure gates pass. Failure exits code 2 with `STOP_NOT_EVALUABLE` and writes no outcome files. Keep the failed run's original raw and execution receipt.

Example after **both** sigma0 cards/runs exist:

```sh
python3 -B scripts/stage6/fullnet_abc_analysis_20260926/analyze_sigma0.py \
  --sigma-package artifacts/stage6_a_rng_isolation_diagnostic_20260926_v1/inputs \
  --default-package artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2 \
  --r0-card artifacts/stage6_a_rng_isolation_diagnostic_20260926_v1/FULLNET3350_R0_SIGMA0_S17_DIAG_V2_CARD.json \
  --a-card PATH_TO_EXACT_A_SIGMA0_CARD \
  --default-r0-card artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/FULLNET3350_R0_S17_REBUILD_V2_TECH_RETRY_CARD.json \
  --default-a-card artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/FULLNET3350_A_R900_S17_REBUILD_V2_CARD.json \
  --r0-raw data/raw/stage6_a_rng_isolation_diagnostic_20260926_v1/R0_SIGMA0/outputs \
  --a-raw data/raw/stage6_a_rng_isolation_diagnostic_20260926_v1/A_SIGMA0/outputs \
  --output-dir data/processed/stage6_a_rng_isolation_diagnostic_20260926_v1/NEW_VERSION
```

The script requires both sigma cards and immutable completed raw. It compares sigma demand to the manifest-bound default V2 package: all requested vehicles remain in the same order, and only the additional M type with `sigma="0"` plus M type references may differ. It compares add/config semantic XML after normalizing only file path locations; binary, schema and network hashes must match across cards. It checks both raw execution receipts and every listed output hash/size, then exact M/U/X `[0,540)` FCD attributes and pre-R realized departures. `M_flow.502` at actual t540 is excluded from this pre-R window. It requires every planned identity to appear, arrive, and all R to reach the through lane. These are bounded eligibility rules for this technical comparison.

After those gates, `SIGMA0_DIAGNOSTIC.json` contains fixed five-cell windows and full M cohort metrics, a 592–605 s negative-control table, a second negative-control table relative to the sigma pair's actual first R through entry, and a re-derived default V2 reference. CSV files contain all 450 fixed cell/bin contrasts, all 1,396 paired M trips, and the 14 predeclared seconds with every differing M ID and its coordinates/speed. No script output itself judges whether nonlocal differences have “largely disappeared” or releases B; a scientific reviewer must inspect spatial, temporal and altered-model limitations.

Test with `python3 -B -m unittest discover -s scripts/stage6/fullnet_abc_analysis_20260926 -p 'test_*.py' -v`. Current tests use synthetic XML/FCD and card fixtures; real sigma0 raw integration remains pending until the two authorized runs complete.
