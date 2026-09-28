# B_REBALANCED28 exact-card prelaunch review

**Date:** 2026-09-26  
**Card:** `inputs/RUN_CARD.json`, SHA-256 `2de27a60cb273795a41cf0bb5a7271fda122326bd09606651c661216e359e96d`  
**Scope:** one exploratory scientific start only. No traffic outcome or Stage 6 completion is inferred here.

## Independent review dispositions

- `simulation_engineer`: `PASS_ENGINEERING_PRELAUNCH`. Read-only runner preflight, input/manifest/card/binary/schema/network/A-receipt hashes, three XML XSD checks, 20 unique new raw output references, absent raw/reservation, 28G+3y+29r WAUT semantics and 120 s/100 MB/100 ms one-use limits checked. Actual TLS behavior and traffic remain unverified.
- `data_analyst`: `PASS_STATIC_DATA_PRELAUNCH`. Default V2 A and B28 demand SHA-256 identical (`12e2e4e003089dad489a2ea1323cd44ef54dea39f994f1bb5fe61e45c7f03be0`), 1396 M/240 R/150 U/75 X, common seed17/network/config/detectors. Only added ramp program/WAUT and arm paths differ. Raw-bound analyzer added at `scripts/stage6/analyze_rebalanced28.py`; 8/8 focused tests pass. It checks all-class duplicate FCD records and inserted-versus-observed IDs, reporting explicit boundary exceptions; old A raw has complete FCD ID coverage with none. New B28 raw has not yet been assessed.
- `scientific_reviewer`: `PASS_SCIENTIFIC_PRELAUNCH` for the one fixed candidate and exact card, after checking independent hashes, matched external inputs, one-variable intervention, protected historical dispositions, fixed metrics and early nonlocal RNG stop rule. The reviewer found an R upstream-lane measurement omission; the analyst added `urban_in_0` and `:urban_tls_0_0` to R-specific coverage and a regression. Postrun duplicate/coverage checks were requested and added. Scientific review does not predict a positive B outcome or release C12G.

## Launch boundary

The next action is the single exact-card B28 start. The runner consumes a reservation before spawning SUMO and writes only to the new `data/raw/stage6_moderate_rebalance_20260926_v1/B_REBALANCED28/outputs/` path. If a technical pretraffic failure occurs, preserve it and use a new versioned package/card only after re-review. If traffic completes, verify hashes, actual program, full vehicle lifecycle, strict pre-540 pairability and actual R exposure before reading post-R outcome. The old 22G negative B result, original C12G HOLD, and historical `A_NOT_EVALUABLE` stay unchanged.
