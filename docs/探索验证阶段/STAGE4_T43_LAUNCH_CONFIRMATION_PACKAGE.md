# Stage 4 T43 launch confirmation package

Date: 2026-09-12  
Batch: `stage4_qmain_sequential_20260912_v1`  
Classification: bounded exploratory targeted validation; not a formal experiment  
Status: **Completed — four registered runs, snapshot-bound final analysis and scientific review passed; T43/Stage 4 closed**

## 1. Authorization and current execution state

The user authorized this package with: “批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。” Authorization covers only the registered sequential qMain block, its archive and its registered offline analysis. It does not authorize a controller, additional points or seeds, a formal experiment, protocol freezing, thesis claims or communication with Robert.

Tier 1 QM3500S17 and QM3500S23 completed sequentially with exit code 0, 29/29 archived files and 7/7 engineering audits each. Independent reconstruction matched 2,342/2,342 fields. Both seeds were `clear_passage` with 14/11 bracketed R events and EJMI `not_identified`; scientific review confirmed the unique registered action `run_q3650` under decision SHA-256 `e0fb31613c2af5375aa6d6148da7a9c67ef5efacde1c0e822b806b6bc2d54b91`. Tier 2 subsequently passed its gate and QM3650S17/QM3650S23 completed. Final analysis and scientific review closed T43/Stage 4. Actual SUMO/netconvert/TraCI/GUI counts are `4/4/0/0`; retries are 0. The immutable final evidence snapshot is authoritative for final results.

## 2. Exact sequence

1. Run Tier 1 sequentially: `qMain=3500`, seeds `17` and `23`.
2. Analyze and apply the pre-registered rule:
   - clear R passage plus positive EJMI in both seeds: stop;
   - clear R passage and EJMI not identified in both seeds: run `qMain=3650`, seeds `17/23`;
   - clear R exclusion and EJMI not positive in both seeds: run `qMain=3350`, seeds `17/23`;
   - seed disagreement, qualification failure or any unregistered combination: stop `unresolved`.
3. At most one Tier-2 pair may run. The other pair is `cancelled_by_stop_rule`.
4. Apply the frozen final-state matrix and proceed to Stage 5; do not add points or seeds.

All 3350/3500/3650 EJMI comparisons use the same-seed original C/MH references at 3200/3800. EJMI is exploratory and cannot be reported as Breakdown, Capacity Drop, capacity or causal evidence.

## 3. Fixed settings

```text
qRamp=720 veh/h; qUrban=360 veh/h; qX=180 veh/h
warmup=0 s; demand window A=[0,1500); B=[300,1500)
post=[1500,2700); full=[0,2700)
profile=low; seeds={17,23}; controller=none
step=1 s; E1/E2 period=30 s; FCD/TLS/queue=1 Hz
geometry, routes, vTypes, signal program and behavior unchanged
```

Only `qMain` may change according to §2.

## 4. Exact commands

Common executable and runner:

```text
/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python
/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/src/scenarios/run_minimal_uncontrolled.py
/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo
/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert
```

For each permitted pair, substitute the exact numeric tuple from the table into the fixed command:

```text
/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/src/scenarios/run_minimal_uncontrolled.py --profile low --q-main <qMain> --q-ramp 720 --seed <seed> --warmup-s 0 --measurement-duration-s 1500 --demand-end-s 1500 --post-demand-clearance-s 1200 --sumo-binary /Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo --netconvert-binary /Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert
```

| Pair | qMain | seed | permission state |
| --- | ---: | ---: | --- |
| QM3500S17 | 3500 | 17 | Tier 1 after T43 approval |
| QM3500S23 | 3500 | 23 | Tier 1 after T43 approval |
| QM3350S17 | 3350 | 17 | only if the registered lower-branch rule fires |
| QM3350S23 | 3350 | 23 | only with QM3350S17 as the complete pair |
| QM3650S17 | 3650 | 17 | only if the registered upper-branch rule fires |
| QM3650S23 | 3650 | 23 | only with QM3650S17 as the complete pair |

No other substitution is valid. Runs execute one at a time and are hash-archived before the next launch.

## 5. Budget and retry

```text
regular SUMO starts: 2 minimum, 4 maximum
regular netconvert operations: 2 minimum, 4 maximum
one same-parameter technical retry across the whole block
hard SUMO start cap: 5
hard netconvert operation cap: 5
```

The retry is allowed only for a diagnosed load/output-I/O failure that produced no scientifically usable complete result. An unfavorable, unclear or non-Breakdown traffic result is not retryable.

## 6. Frozen machine evidence

```text
registration_payload d934b62903081163495b7e17cf72c52786e1dfb864aa5d9a9d3eb5c2eb9a952a
measurement_contract b3bf7abec5a9e6cfc29edb81de58ec5cc86c9e0fd132e88a9cd6999a456a91c9
source_registry 96ee4a20f8130ede9a14ff9a40292a0c1d588770bbf1b37ad1ac455b3a1c538b
execution_ledger f4fad2661a4638e2045d5d74b50418e068758f08d271705d3cccbcebecaa51bf
stage4_adapter d8a1f3832588678a8054507ef8b0c74060ba39585a2c4c03bf268c966b4702f8
production_tests 5849b61192c4c6dae0051e2b8b559a3fe3e626e2c9fd9a00737801dbc5d1a67b
independent_tests c8ee32f5e8da72695076228736d5aa290542bd34d56dd459817d25e5c82c101e
engineering_verification 4e1e2f8d621e35f4927dbc5f29a706dce838a7e20ecb3c4459efd12a174860fb
independent_verification_revision_08 9289b6a6276711bd7a7e27870fc4dd1aac463a28c0052bfa1096cfac6e4a8515
analysis_review_revision_08 f77d05f80305b42d5937123b87f4699fda26bf2bfdb536dda149bd3dac7c74cc
```

Verification: 52/52 production and 29/29 independent tests passed; four reference archives passed 7/7 audits; scientific review passed with open Blocker/Major/Minor `0/0/0`.

## 7. Current authorization state

```text
T43 status: completed_final_scientific_review_passed
authorization quote: 批准按 docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md 执行 T43。
actual SUMO/netconvert/TraCI/GUI: 4/4/0/0
Tier 1 attempt IDs/runtime paths/source-map hashes: recorded in runtime_source_registry.json
Tier 2 branch: QM3650S17/QM3650S23 completed; independent analysis and scientific review passed
```

The exact user words and approved registration/contract/registry hashes were written before launch. Any hash mismatch, nonregistered counter, incomplete authorization envelope or unreviewed Tier-2 branch stops execution.
