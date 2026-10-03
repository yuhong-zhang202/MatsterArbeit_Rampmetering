# Stage 3 archive-only baseline diagnostic report

Date: 2026-09-12  
Batch: `stage3_baseline_diagnostic_20260912_v2`  
Classification: **exploratory archive diagnosis; not a formal experiment**

```text
execution_status: T30-T35 completed
new_sumo_starts: 0
new_netconvert_starts: 0
stage3_result: completed_with_targeted_stage4_recommendation
scenario_design_readiness: not_identified
formal_experiment_status: not_started
```

## 1. Decision-facing result

Stage 3 completed the prescribed analysis of the eight accepted Stage 2 runs without starting SUMO, netconvert, TraCI or GUI. Source coverage, measurement metadata, vehicle accounting, five-question diagnosis, processing verification, time aggregation and four intended-use assessments are complete within the declared synthetic finite-horizon scope.

The evidence supports two limited findings. First, the required M/R/U flow, stock and stopped-state observations are available within the registered lanes and windows (`Q1=supported`). Second, R and U were observed technically stopped on the shared approach at the same 1 Hz labels in all eight runs, totalling 7,120 independently reconstructed sampled seconds (`Q3=supported`). This is observational exposure, not proof that ramp spillback caused additional U loss.

The evidence does not identify the freeway side of the intended trade-off (`Q2=not_identified`). A-window M-only internal speeds remain approximately 30.02–31.71 m/s while measured q tracks requested mainline input; there is no approved Breakdown definition, Capacity Drop result or realistic upstream feeder state. Therefore the same-scenario basis for a freeway-protection versus urban-protection study is also not identified (`Q4=not_identified`).

The T35 branch is one targeted Stage 4 proposal addressing Q2. Stage 3 does not authorize that simulation, and Stage 5 cannot yet close as `preliminary_ready`.

Core quantitative and processing claims: **High confidence**. Q1/Q3 meaning within the stated scope: **Moderate confidence**. Formal scenario suitability: **Unknown**.

## 2. Authorization and preservation

The user instructed execution of Stage 3–6 according to `docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md`. The plan's internal gates remain binding: Stage 4 cannot launch with an incomplete registration card or without exact run authorization; Robert material cannot be sent without explicit authorization.

The first metadata attempt, `stage3_baseline_diagnostic_20260912_v1`, stopped before creating a contract or ledger because it expected the C17 seed at the wrong summary level. Its `INCOMPLETE.json` is retained. Version v2 cross-checks the Stage 2 ledger, source map, historical command and available summary field. No source, Stage 2 output or raw data was modified.

## 3. Outputs and gates

| Output | Stage 3 status | Evidence |
| --- | --- | --- |
| O1 scenario/measurement contract | complete | 19 lanes, six E1, two coverage-only E2, TLS links and R path coordinates |
| O2 demand/vehicle accounting | complete | 32/32 run-class units, 64/64 endpoints, 14,564 identities |
| O3 condition diagnosis | complete | 40/40 question units; five final tables; two discrete figures |
| O4 suitability assessment | complete initial assessment | Q1/Q3 supported; Q2/Q4 not identified; 4/4 reviewer opinions |
| O5 timing/sensitivity | complete | A/B/Post/Full; 96/96 values; 48/48 series; 6 contrasts; 8 seed units |
| O6 design handover | draft | carry-forward and unresolved register in §8; final ≥20-item register belongs to Stage 5 |

| Gate | Status | Denominator and limit |
| --- | --- | --- |
| G01 | `passed` | 8/8 runs; 232/232 files; 128/128 required outputs; identity conflicts 0 |
| G02 | `passed` | 32/32 run-class; 64/64 endpoints; residual/duplicate/unknown failures 0 |
| G03 | `passed` | 21,600/21,600 FCD labels; 4,320/4,320 E1 intervals; E2 coverage-only |
| G04 | `passed` | 40/40 records; repaired ordered propagation 8/8; contradictions 0 |
| G05 | `passed` | 12/12 modes; 18 production + 4 independent tests; core reconstruction complete |
| G06 | `passed` | 6/6 contrasts; 8/8 seed units; 96/96 values; 48/48 series; 43 inconsistent signs retained |
| G07 | `passed` | 4/4 assessments with evidence, alternatives, limitations and reviewer opinion |
| G08 | `not_verified` | Stage 5 inventory and final handover classification have not occurred |

Passing G04/G07 means diagnosis is complete; it does not convert `not_identified` into support.

## 4. Network and measurement boundary

The compiled R path order used for propagation, written downstream to upstream, is:

```text
ramp_accel [1042.35,1137.67]
→ ramp_mid_internal [960.37,1042.35]
→ ramp_storage [755.88,960.37]
→ ramp_diverge_internal [642.80,755.88]
→ shared_approach [404.00,642.80]
```

Ramp-end, internal, storage and shared event sets are disjoint. All eight runs show first stopped-R observations in this order. The evidence is consistent with technical stopped occupation appearing progressively upstream, but 1 Hz labels do not prove one continuous physical queue or causation.

Mainline vehicles use `departPos="last"` and actually insert approximately **0.1–287 m from the merge**. The scaffold does not observe a realistic long upstream freeway feeder. M-only internal E1 therefore describes local aggregate merge-entry passage, not a freeway-wide state. TLS link state is movement-specific context and does not identify the cause of stopping.

## 5. Processing, corrections and independent verification

The analyzer uses streaming FCD parsing, a complete frame registry, disjoint region/same-vehicle episodes, window slices with censor flags, R first-downstream brackets, TLS context, endpoint accounting and 30/60/120-second E1 reaggregation.

Scientific review found one Major in the first propagation implementation: an internal group mixed storage-upstream and storage-downstream lanes and overlapped another event set. Old run/aggregate revision_01 and related reviews remain superseded. The repaired code derives order from the contract, checks continuity/disjointness and has ordered/reversed fixtures. New run revision_02 and aggregate revision_03 report 8/8 ordered observations. Final review closed the Major.

Independent code that does not import production aggregation/episode functions matched 14,564 identities, 246,175 lane/class/time cells, 99,955 episodes, 2,100 R events, 7,120 shared R/U labels, 96 sensitivity values and all eight propagation states. A later correction changed 355 `stopped_episode_support` unit labels to `sampled_region_stop_support_s`; numeric changes were zero. Final figures use discrete points/bars.

## 6. Q1–Q4

| Question | Status | Finding and boundary |
| --- | --- | --- |
| Q1 observability | `supported` | flow and stock/state quantities observable in declared scope; no realistic upstream feeder |
| Q2 freeway side | `not_identified` | no approved merge-consistent mainline impairment signature; no Breakdown/Capacity Drop result |
| Q3 urban side | `supported` | R/U shared-road stopped exposure in 8/8; causal additional U loss not established |
| Q4 same-scenario relevance | `not_identified` | Q3 exists but Q2 does not; the two-sided control trade-off is not demonstrated |

Input realization, near-merge insertion, TLS context and lane coverage were checked. Downstream blockage and detailed merge/lane-change mechanism remain unresolved. Two seeds and time rebinning are descriptive only.

## 7. Behavioral implication

At qRamp=720, raising qMain from 3200 to 3800 suppresses demand-period R first-downstream observations from 36/40 to 0/0 while M local passage and speed remain high. This is evidence of access competition or ramp starvation within the scaffold. It is not evidence of freeway Breakdown, capacity improvement or successful freeway protection.

The original coarse qMain anchors cannot distinguish whether an unobserved transition region contains both mainline impairment and non-zero R passage, or whether the current insertion/merge structure excludes R before mainline impairment becomes visible.

## 8. O6 draft handover

Carry forward within the scaffold: archive identity/hashes; M/R/U/X accounting; compiled lane/R-path map; TLS-link context; E1 aggregation; frame/episode/first-R/censoring rules; matched-seed structure; independent raw reconstruction.

Carry forward with qualifications: `speed<=0.1 m/s` only as technical stop; 0/1500/1200 only as a finite-horizon candidate; two seeds only as descriptive; R/U co-occurrence only as exposure; current geometry/Krauß settings only as exploratory.

Unresolved: mainline impairment definition; Breakdown/Capacity Drop role; realistic upstream state; causal R-induced U loss/counterfactual; safe storage; formal metrics, thresholds, timings and seeds; ALINEA/override settings; formal sweet-spot and robustness rule.

## 9. T35 branch and next gate

Prepare one Stage 4 qMain-axis registration to distinguish:

- A: coarse 3200/3800 spacing missed a transition with mainline impairment and non-zero R passage;
- B: the current near-merge insertion/merge structure tends to exclude R before observable mainline impairment.

The registration must fix qMain sequence, two-seed stop rule, M impairment definition, R-access classification, denominators, hashes, commands and budget. Stage 4 starts remain zero until the exact complete card is explicitly authorized.

Stage 5 cannot yet classify `preliminary_ready`. Stage 6 may prepare provisional inheritance/design questions, but cannot freeze a formal design while Q2/Q4 remain unresolved.

## 10. Specialist routing

- `simulation_engineer`: source/contract/implementation, Major repair and technical verification; all findings addressed; simulation starts 0.
- `data_analyst`: C17 gate, eight-run processing, tables/figures, sensitivity and independent reconstruction; unit/reviewer metadata corrected in new revisions.
- `scientific_reviewer`: read-only method, Major/Minor, Q1–Q4 and branch review; final open Blocker/Major 0.

