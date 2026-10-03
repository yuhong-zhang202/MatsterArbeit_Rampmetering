# Stage 4 sequential qMain targeted-validation registration proposal

Date: 2026-09-12  
Proposed batch: `stage4_qmain_sequential_20260912_v1`  
Status: **Completed — T43 and Stage 4 closed after immutable snapshot repair, 116/116 tests and final scientific PASS; Stage 5 handover is `specific_obstacle`**  
Classification: exploratory targeted validation; not a formal experiment

## 1. Registered question and decision value

```text
block_id: S4_B1_QMAIN_SEQUENTIAL
question_id: S4Q1_COEXISTENCE_BRACKET
```

Question: with qRamp and all other scenario settings fixed, did the coarse qMain anchors at 3200 and 3800 veh/h miss a registered point where a local exploratory mainline-impairment signature and non-zero R merge passage coexist?

Existing evidence:

- C17/C23 at qMain=3200 and qRamp=720: 36/40 R first-downstream observations in A=[0,1500).
- MH17/MH23 at qMain=3800 and qRamp=720: 0/0 R first-downstream observations in A.
- M-only internal A-window speed remains high across these anchors, and Q2 freeway impairment is not identified.
- M vehicles insert only about 0.1–287 m from the merge, so a real upstream freeway state is not observed.

Two observational explanations:

- A: the 600 veh/h spacing missed a registered intermediate point with both an exploratory local M impairment signature and non-zero R passage.
- B: within the registered points, R exclusion occurs before the specified local M signature; this pattern is consistent with the short near-merge insertion/merge structure but does not prove structural causation.

The experiment has decision value only if its sequence and stop rules are fixed before execution. A negative result is bounded to the registered points and cannot prove that no extremely narrow transition exists.

## 2. Sequential design

### Tier 1 — always first

Run qMain=3500 veh/h for seeds 17 and 23. This is the strict midpoint of the existing 3200/3800 bracket. Under the actual demand-number rule, planned M=1458, versus 1333 at 3200 and 1583 at 3800.

### Tier 2 — at most one pre-registered branch

After both Tier-1 runs pass technical and measurement qualification:

1. If both seeds have clear R passage and both have positive EJMI signature: stop; do not run Tier 2.
2. If both seeds have clear R passage and EJMI is not identified in both: run qMain=3650 for seeds 17/23.
3. If both seeds have clear R exclusion and EJMI is not positive in both: run qMain=3350 for seeds 17/23.
4. If R classification differs by seed, a run is unqualified, an R boundary is unresolved, EJMI results conflict by seed, or R/EJMI changes cannot be assigned to one branch: stop as `unresolved`; do not run Tier 2.

Only one Tier-2 branch may execute. The unused branch is recorded `cancelled_by_stop_rule`, not silently omitted.

Planned M counts for the 1500 s demand period use `int(round(qMain*1500/3600))`:

| qMain veh/h | planned M |
| ---: | ---: |
| 3200 | 1333 |
| 3350 | 1396 |
| 3500 | 1458 |
| 3650 | 1521 |
| 3800 | 1583 |

## 3. Logical runs and status

| run_id | role | qMain | seed | paired references | execution status |
| --- | --- | ---: | ---: | --- | --- |
| C17 | lower reused reference | 3200 | 17 | QM3500S17 | reused; no launch |
| C23 | lower reused reference | 3200 | 23 | QM3500S23 | reused; no launch |
| QM3500S17 | Tier-1 midpoint | 3500 | 17 | C17, MH17 | pending exact authorization |
| QM3500S23 | Tier-1 midpoint | 3500 | 23 | C23, MH23 | pending exact authorization |
| QM3350S17 | conditional lower midpoint | 3350 | 17 | C17, MH17 | conditional |
| QM3350S23 | conditional lower midpoint | 3350 | 23 | C23, MH23 | conditional |
| QM3650S17 | conditional upper midpoint | 3650 | 17 | C17, MH17 | conditional |
| QM3650S23 | conditional upper midpoint | 3650 | 23 | C23, MH23 | conditional |
| MH17 | upper reused reference | 3800 | 17 | QM3500S17 | reused; no launch |
| MH23 | upper reused reference | 3800 | 23 | QM3500S23 | reused; no launch |

At finalization, exactly two conditional runs are executed or all four are cancelled by a stop rule. They remain in the denominator for planned-run terminal status.

## 4. Fixed fields

```text
qRamp=720 veh/h
qUrban=360 veh/h
qX=180 veh/h
warmup_s=0
demand_end_s=1500
simulation_end_s=2700
clearance_s=1200
windows: A=[0,1500), B=[300,1500), Post=[1500,2700), Full=[0,2700)
profile=low
seeds={17,23}
step_length=1 s
E1/E2 period=30 s
FCD/TLS/queue observation=1 Hz
departPos=last; departLane=best; departSpeed=max
time-to-teleport=-1; collision.action=warn
controller=none
urban TLS=fixed existing program
scenario_variant_path=config/scenarios/minimal_uncontrolled (unchanged base; no variant)
```

The only intervention is qMain according to the pre-registered sequence. Geometry, route, priority, vType, behavior, signal, qRamp, qUrban, qX, durations, seeds and outputs are fixed.

## 5. Exploratory joint mainline-impairment signature

Name: `EJMI sufficient signature`. It is an exploratory sufficient discriminator for this Stage 4 block. It is not Breakdown, Capacity Drop, a formal congestion threshold, a confidence interval or a thesis result.

Qualification for each candidate run:

- `outside_M(1500)=0` with planned/entered/arrived identity reconciliation;
- M-only internal E1 and FCD coverage complete for A and B;
- no unexplained warning, collision, teleport, route, identity, lane or interval anomaly;
- same configuration/input hashes except qMain and generated demand;
- candidate qMain strictly inside 3200/3800.

Metrics:

- `v`: contribution-weighted speed across the two M-only internal E1 lanes, m/s;
- `occ`: arithmetic mean of the two lane occupancy percentages, percentage points. Occupancies are not summed and are not called density.

For every candidate `x ∈ {3350,3500,3650}`, use the same-seed original C/MH references (`3200` and `3800`), never an adjacent Stage 4 candidate. For each seed and W in {A,B}, candidate x must satisfy:

```text
v_x,W < min(v_C,W, v_MH,W) - delta_v,W
occ_x,W > max(occ_C,W, occ_MH,W) + delta_occ,W
```

Pre-registered descriptive margins, derived from the maximum existing two-seed reference difference:

| Window | delta_v | delta_occ |
| --- | ---: | ---: |
| A | 0.5516661889683938 m/s | 0.1658 percentage points |
| B | 0.5020140721737434 m/s | 0.17725 percentage points |

Persistence requirement within B for the same seed:

- at least one aligned 120 s block whose two 60 s sub-bins both have speed below the same-clock C/MH envelope and occupancy above it;
- the reaggregated 120 s block retains both directions;
- at least three of its four 30 s sub-bins retain both directions.

EJMI is positive at a demand point only if A/B aggregate margins and persistence pass in both seeds. Any other qualified result is `not_identified`; a qualification or seed-consistency failure is `unresolved`. It must never be reported as evidence that impairment is absent.

## 6. R passage classification

- Single-seed clear passage: at least one identity-resolved, bracketed first-downstream R event in A.
- Two-seed clear passage: both seeds meet the single-seed definition.
- Two-seed clear exclusion: both have zero such events and complete FCD, identity, spatial-boundary and A-window coverage.
- One zero/one nonzero, missing coverage or unresolved bracket: `unresolved`.

No arbitrary “partial passage” count threshold is used. Exact counts and event-time distributions are reported. Arrival=0 is not required for exclusion; arrival is a consistency check. A contradiction between first-downstream and arrival evidence is a measurement failure.

## 7. Required observations and denominators

For every logical run: planned/entered/outside/in-network/arrived for M/R/U/X at 1500 and 2700; `planned_demand_vehph` from scheduled counts; `realized_entry_vehph_A` from covered class-specific entered counts at 1500 s; M-only internal and downstream E1 `q` from `nVehEntered`, contribution-weighted speed and arithmetic-mean lane occupancy; M stopped episodes and positions; M depart-position range; R first-downstream events and previous frames; R-region propagation; shared R/U stopped exposure; TLS context; warning and coverage audit. Planned demand, realized entry and detector flow are distinct quantities and must not share an `actual_input` label.

First tier denominators:

- 6/6 logical runs terminal: C/MH references plus two q3500 runs;
- new runs 2/2;
- 48/48 class-endpoint units (`6 runs × 4 classes × 2 endpoints`);
- four adjacent matched-seed comparisons (3200→3500 and 3500→3800, each two seeds).

If Tier 2 executes:

- 8/8 used logical runs terminal; new runs 4/4;
- 64/64 class-endpoint units;
- six adjacent matched-seed comparisons over the sorted four used qMain points.

Time bins are observations, not stochastic replicates. Seeds are shown separately; two seeds do not establish power, confidence intervals or statistical robustness.

## 8. Result actions and stopping

`supports_A_within_registered_points`: at least one registered internal qMain point has positive EJMI and clear R passage in both seeds. Stop the block and proceed to Stage 5 suitability assessment. Do not call it Breakdown or capacity.

`supports_B_pattern_within_registered_points`: across the qualified registered sequence, clear R exclusion occurs before any positive EJMI. Stop scanning and proceed to Stage 5 as a likely `specific_obstacle`. This is a pattern consistent with explanation B, not causal proof of geometry/insertion mechanism.

`unresolved`: seed disagreement, incomplete input/coverage, measurement contradiction, non-branchable R/EJMI combination, or no discriminating result after the one allowed Tier-2 branch. Stop and proceed to Stage 5 with a bounded unresolved package; do not add points or seeds.

No missing Breakdown, unfavorable result, non-clearance, low insertion, seed disagreement or opposite direction permits a technical retry.

## 9. Exact commands

Common executable paths:

```text
PYTHON=/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python
RUNNER=/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/src/scenarios/run_minimal_uncontrolled.py
SUMO=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo
NETCONVERT=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert
```

For each new run, execute the following argv with the registered q and seed substituted:

```text
PYTHON RUNNER --profile low --q-main <3350|3500|3650> --q-ramp 720 --seed <17|23> --warmup-s 0 --measurement-duration-s 1500 --demand-end-s 1500 --post-demand-clearance-s 1200 --sumo-binary SUMO --netconvert-binary NETCONVERT
```

Tier 1 uses only q=3500. Tier 2 may use only q=3350 or only q=3650 according to §2. All tokens resolve to the absolute paths above before launch and the final argv is stored in the ledger.

## 10. Runtime identity, archive and checks

Batch directories:

```text
data/processed/stage4_qmain_sequential_20260912_v1/
artifacts/stage4_qmain_sequential_20260912_v1/runtime_archive/<attempt_id>/
results/tables/stage4_qmain_sequential_20260912_v1/
results/figures/stage4_qmain_sequential_20260912_v1/
```

Before each launch: read ledger and authorization; reserve budget; record current runtime-directory set; verify all code/input/binary hashes; require output/archive target absent. Execute one attempt at a time. Bind the unique new runtime using `summary.json` plus set difference; verify q, seed, windows, argv and version. Archive atomically, write source map, verify 100% hashes, then analyze. Never fall back silently to `/private/tmp`.

Technical checks: required outputs present/nonempty; identities and endpoint equations; time/interval coverage; no unexplained warning/error/collision/teleport/emergency-braking/route failure; exact single-factor config diff; original runtime unchanged after archive.

## 11. Budget and retry

```text
regular_new_sumo_starts: minimum 2, maximum 4
technical_retry_allowance: 1 across the block
hard_sumo_start_cap: 5
regular_netconvert_operations: minimum 2, maximum 4
hard_netconvert_operation_cap: 5
```

One same-parameter retry is permitted only after a specifically identified load or output-I/O failure leaves no scientifically usable complete result. Seed, q, argv, source/input/binary hashes and analysis contract must be identical. An attempt with uncertain launch status continues to consume its reserved start. All attempts remain recorded.

## 12. Frozen source references and pending implementation

Current reviewed hashes:

```text
run_minimal_uncontrolled.py 7cd29eeba5fff64c43cb71ba3b9f3477938f8d4e246ab158e4f20293dbd3f983
internal_lane_accounting.py a8bbc12d161d98c73ad5088baf8cc052c5231333bb87c36a576f77aac26715e4
archive_stage2_runtime.py df6d4620b9b65482df7224bf7db4bf12ceb04ccf0a7a30c92408c65f187f38eb
scenario.nod.xml b1577412ba28470abe3270913833a4053ca6be174f2eede55de77aa5b8a2c923
scenario.edg.xml d6c7d6df0b8a5afc60a8bfedd796b9d14baa56ec44cf322e3129f976396cff53
scenario.con.xml d154948200c9b4d9a3d54bf04647357daaff0e6a19293f19fcef457ee4ae4ea5
scenario.tll.xml 89f25ab5020e4f2df2fc035233b038c89cc80cf748f6dca19b5584e829df3ecc
scenario.add.xml 8189e35c5d8224b91b6de57e3bcaf0a7a43139e73af0f50e2ea73d2224d80828
scenario.sumocfg 0e0f99a7af694e7f448efdb66837143100478da2151ae83ba3e1c6772a811db0
sumo 3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179
netconvert 919f8491518379daeaf2e215a96e58edb4bed4894cbf6ef948788170d5bea9b5
```

Existing scenario runner supports the registered commands; no scenario/runner change is proposed. Stage 3 analyzer cannot be reused unchanged because it enforces Stage 3 identity, zero-start budget and exactly eight old runs. The user authorized T42 offline implementation and three-specialist review with “批准，继续stage 4” after the authorization request explicitly separated T42 from later T43 launch approval. T42 is complete: the Stage 4 adapter, immutable registration payload, measurement contract, source registry and ledger passed engineering, independent-data and scientific review. The immutable registration payload is the sole machine-bound scientific contract; this Markdown document is the current human-readable card and is deliberately not part of a circular hash dependency.

```text
registration_payload: data/processed/stage4_qmain_sequential_20260912_v1/registration_payload.json
registration_payload_sha256: d934b62903081163495b7e17cf72c52786e1dfb864aa5d9a9d3eb5c2eb9a952a
required_observations_payload_sha256: 61d1a6921feb501f641d97ebc3faa462ba183d9df04bd0d1622f497112b8754e
analysis_contract: data/processed/stage4_qmain_sequential_20260912_v1/measurement_contract.json
analysis_contract_sha256: b3bf7abec5a9e6cfc29edb81de58ec5cc86c9e0fd132e88a9cd6999a456a91c9
source_registry_sha256: 96ee4a20f8130ede9a14ff9a40292a0c1d588770bbf1b37ad1ac455b3a1c538b
execution_ledger_sha256: f4fad2661a4638e2045d5d74b50418e068758f08d271705d3cccbcebecaa51bf
stage4_adapter: src/analysis/analyze_stage4_qmain.py
stage4_adapter_sha256: d8a1f3832588678a8054507ef8b0c74060ba39585a2c4c03bf268c966b4702f8
stage4_production_test_sha256: 5849b61192c4c6dae0051e2b8b559a3fe3e626e2c9fd9a00737801dbc5d1a67b
stage4_independent_test_sha256: c8ee32f5e8da72695076228736d5aa290542bd34d56dd459817d25e5c82c101e
engineering_verification_sha256: 4e1e2f8d621e35f4927dbc5f29a706dce838a7e20ecb3c4459efd12a174860fb
independent_verification_revision_08_sha256: 9289b6a6276711bd7a7e27870fc4dd1aac463a28c0052bfa1096cfac6e4a8515
analysis_review_revision_08_sha256: f77d05f80305b42d5937123b87f4699fda26bf2bfdb536dda149bd3dac7c74cc
T42_authorization_quote: 批准，继续stage 4
T42_status: passed_52_production_plus_29_independent_tests
T42_open_blocker_major_minor: 0/0/0
T43_authorization_quote: 批准按 docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md 执行 T43。
T43_launch_status: completed_final_scientific_review_passed
actual_sumo_starts: 4
actual_netconvert_starts: 4
actual_traci_connections: 0
actual_gui_starts: 0
```

## 13. Specialist review

- `simulation_engineer`: implemented the batch-specific adapter and all measurement, reference, branch, budget, hash and four-counter guards; 52/52 production tests passed.
- `data_analyst`: independently reconstructed all four references, tested 13,203 registered final-state combinations and closed the final mechanical review; 29/29 independent tests passed.
- `scientific_reviewer`: passed T42 with open Blocker/Major/Minor = 0 after the reference-map, final-matrix, observation-contract, detector-drift and planned-versus-realized-input repairs.

T42 reviews are complete and T43 is explicitly authorized. Tier 1 attempts QM3500S17/QM3500S23 have runtime identities, source maps and manifest receipts. Independent reconstruction matched 2,342/2,342 fields; scientific review confirmed both seeds `clear_passage`, EJMI `not_identified` and the unique action `run_q3650`. The Tier-2 gate subsequently passed; QM3650S17/QM3650S23 completed and the final snapshot-bound analysis and scientific review passed. T43/Stage 4 are closed with 4/4/0/0 starts and no retry; no further launch is implied by this historical card.
