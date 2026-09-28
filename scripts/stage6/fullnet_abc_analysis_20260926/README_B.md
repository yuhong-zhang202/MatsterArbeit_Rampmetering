# Default-model A versus B exploratory audit

`analyze_b.py` reads the matched default-model V2 A and future B raw. It does not run SUMO or use the sigma0 A as a comparator. It verifies manifest/card/raw hashes, exact A/B demand bytes, semantic config equality except WAUT `A_OPEN` versus `B_MODERATE`, then strict `[0,540)` M/U/X trajectory and actual departure equality. Post-activation M outcomes are parsed only after these gates and some actual B R merge-section exposure. Failure exits 2 before writing outcome files.

After the single authorized B run completes, use a **new** processed directory:

```sh
python3 -B scripts/stage6/fullnet_abc_analysis_20260926/analyze_b.py \
  --package artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2 \
  --a-card artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/FULLNET3350_A_R900_S17_REBUILD_V2_CARD.json \
  --b-card artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/FULLNET3350_B_R900_S17_REBUILD_V2_CARD.json \
  --a-raw data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/A/outputs \
  --b-raw data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/B/outputs \
  --output-dir data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/b_outcome/NEW_VERSION
```

Outputs retain all 450 paired fixed cell/bin rows, every planned vehicle in A and B with completion and censoring flags, all 30-second E2 ramp-storage/shared-boundary bins, and M-only passage cutoffs. External insertion delay and completed network residence are separate. A queue detector's zero jam length alone does not establish no physical queue; interpret with raw trajectories, occupancy and unfinished vehicles. The script produces descriptive data, not an automatic `B_SUPPORTED` decision. A scientific reviewer must adjudicate whether local M gains are consistent with full-route outcomes and whether R/U cost is acceptable before C can proceed.

Run the project analysis tests with `python3 -B -m unittest discover -s scripts/stage6/fullnet_abc_analysis_20260926 -p 'test_*.py' -v`. Synthetic tests cover full fixed-bin coverage and complete-cohort censoring. The new B raw integration is pending.
