# Stage 4 targeted validation report

Date: 2026-09-13  
Batch: `stage4_qmain_sequential_20260912_v1`  
Classification: completed exploratory targeted validation; not a formal experiment  
Final registered action: `supports_B_pattern_within_registered_points`  
Stage 5 handover: `specific_obstacle`

## 1. Question and execution

Stage 4 tested whether the coarse qMain anchors at 3200 and 3800 veh/h had missed a registered intermediate point where non-zero ramp passage and a local exploratory mainline-impairment signature coexist. qRamp=720, qUrban=360, qX=180, seeds 17/23, controller, geometry, signal, vehicle behavior and the 0/1500/2700 s horizon were fixed.

The user authorized the exact T43 package. Tier 1 ran qMain=3500 for seeds 17/23. Both seeds showed A-window R passage and no EJMI, so the registered rule selected qMain=3650 for the same seeds and cancelled qMain=3350. All four new attempts completed with no retry.

```text
SUMO/netconvert/TraCI/GUI: 4/4/0/0
regular starts used: 4/4
technical retries used: 0/1
registered logical runs terminal: 10/10
used valid run manifests: 8/8
archived files: 116/116
class-endpoint units: 64/64
matched-seed adjacent comparisons: 6/6
```

## 2. Result

| qMain | seed 17 R A events | seed 23 R A events | R status | EJMI |
| ---: | ---: | ---: | --- | --- |
| 3500 | 14 | 11 | both `clear_passage` | both `not_identified` |
| 3650 | 0 | 0 | both `clear_exclusion` | both `not_identified` |

At qMain=3650, A-window R first-downstream events and arrivals are zero with complete coverage. This is a finite-window classification. At 1500 s, 121/120 R vehicles had entered and 179/180 were still waiting outside; at 2700 s, all 300 R vehicles in each run had entered, passed downstream and arrived. `clear_exclusion` therefore means no observed passage in A=[0,1500), not permanent exclusion or failure to complete.

The EJMI speed, occupancy and persistence conditions failed for all four candidates. For q3650, internal A-window speed/occupancy were 31.941 m/s and 8.0023% for seed 17, and 31.613 m/s and 8.1075% for seed 23. `not_identified` means the pre-registered sufficient signature was not met; it does not mean the mainline had no impairment.

The registered decision and an independent oracle both return `supports_B_pattern_within_registered_points`: within the registered points, R changes from A-window passage to A-window exclusion before any registered EJMI is identified.

## 3. Measurement and verification

All four new runs passed the complete observation contract: endpoint accounting; planned and realized entry; internal and downstream E1; M stopping and positions; R propagation; shared R/U stopped exposure; TLS context; warnings and coverage. Tier-2 raw XML reconstruction matched 2,342/2,342 fields. Final regression totals were 74/74 production plus 42/42 independent tests.

The final evidence chain uses only `data/processed/stage4_qmain_sequential_20260912_v1/final_evidence_ledger_snapshot.json`, SHA-256 `f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516`. Its embedded ledger canonical SHA-256 is `265ec48b66947ad22e771cad9477f639a9d1b4523c0addb5c05f2303c8ba21bd`. The mutable operational ledger is not a normative final-analysis input. Snapshot-bound final artifacts are under:

- `data/processed/stage4_qmain_sequential_20260912_v1/analysis/final/revision_04/`
- `results/tables/stage4_qmain_sequential_20260912_v1/final/revision_03/`
- `results/figures/stage4_qmain_sequential_20260912_v1/final/revision_03/`
- `data/processed/stage4_qmain_sequential_20260912_v1/verification/T43_final_snapshot_bound_independent_verification_revision_01.json`

Engineering, independent-data and final scientific reviews report open Blocker/Major/Minor = 0/0/0. The five measurement checks passed within the registered exploratory scope.

## 4. Scientific boundary

Supported within this synthetic scaffold and registered points:

- q3500 has non-zero A-window R passage in both seeds;
- q3650 has zero A-window R passage in both seeds with complete coverage;
- all four candidates fail the registered EJMI sufficient signature;
- R and U share stopped exposure on the urban approach.

Not supported:

- absence or presence of freeway Breakdown, Capacity Drop or a capacity threshold;
- permanent ramp exclusion;
- a causal explanation based on geometry, priority, insertion or lane changing;
- causal additional U loss due to R spillback;
- a sweet spot, controller benefit or thesis-ready result.

The mainline vehicles still enter close to the merge, the design has zero warm-up, delayed vehicles continue entering after 1500 s, and every point has only two seeds. These limitations prevent promotion to formal experimental readiness.

## 5. Closure and handover

T43 and Stage 4 are closed. No scientific reason remains for another Stage 4 run, and the regular run budget is exhausted. Q1 observability and Q3 shared-road exposure remain `supported` within scope; Q2 freeway-side impairment and Q4 the same-scenario two-sided trade-off remain `not_identified`.

Stage 5 should classify exploratory assessment as `completed / specific_obstacle`: the current scaffold excludes demand-window R passage before it shows the registered local mainline impairment signature. This identifies a concrete obstacle to the intended freeway-protection versus urban-backup study; it does not identify the obstacle's structural cause.

The final read-only scientific review is recorded in `data/processed/stage4_qmain_sequential_20260912_v1/verification/T43_final_scientific_review_record_20260913.json` (SHA-256 `b73513dca5a0b535a8910ff4c779f410a13f0b165391b503b6e70c0475469726`). The mutable operational index and its closeout verification are non-normative; the immutable evidence snapshot remains unchanged.
