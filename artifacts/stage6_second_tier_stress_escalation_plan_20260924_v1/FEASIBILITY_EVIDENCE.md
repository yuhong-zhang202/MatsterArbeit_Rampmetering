# Read-only feasibility evidence for the second-tier proposal

**Scope:** Existing reviewed records only. No new simulation, route generation, result reclassification or execution card was used.

## Observed R720 realization

The reviewed minimal3199 U=X=0 delayed-R720 treatment scheduled 192 R identities in `[540,1500)`. All 192 inserted and arrived; actual R departures span 540–1495 s with zero departure delay. The first R was observed on the shared approach at 541 s, ramp storage at 566 s, acceleration lane at 578 s and auxiliary merge section at 582 s; the first native through-lane change was at 583 s. Auxiliary E1 counted 4, 3 and 6 entries in the first three positive complete 30 s intervals and T3 was confirmed at 660 s. E2 ramp-storage/shared-boundary each recorded 192 entries, maximum `vehicleNumber` 8 and reported jam length 0. The queue export lacks a usable lane-occupancy sequence. The 220 R through-lane lane-change **records** are events, not 220 unique merged vehicles.

This proves R720 realization in one reviewed qMain=3199.2 minimal pair. It does not establish R900/R1080 insertion, receiving-space capacity, or R throughput at qMain3350.4 with U=X=0.

## Static network and demand arithmetic

The bound network has a single-lane R path through urban input, shared approach, ramp storage (204.49 m), acceleration lane (99.07 m) and a 294.51 m merge section with one auxiliary and two M through lanes. These lengths are not throughput estimates. Historical U/X-positive A_OPEN R720 runs inserted/arrived their R vehicles, but that does not prove higher-rate U=X=0 capacity.

At fixed `[540,1500)` (960 s), nominal R720/900/1080 correspond to 192/240/288 planned vehicles. At a fixed 1500 s M demand window, qMain3350.4/3499.2/3650.4 correspond to 1396/1458/1521 planned M vehicles. Higher-rate realization remains unknown until a future separately reviewed run.

## Planning implication

Compare unique R IDs at their first through-lane entry and the fixed auxiliary E1 intervals, with planned/inserted/arrived/unfinished and departure-delay reconciliation. Higher nominal qRamp alone is not evidence of stronger merge pressure. Preserve the original event classifier and matched-control requirements. New resource limits require a new proposal: the existing 75,000,000-byte treatment trigger was validated for R720 only.

## Source bindings

- Original minimal plan: `artifacts/stage6_minimal_ramp_induced_breakdown_existence_test_20260924_v1/PLAN.md` — SHA-256 `06b0f04f1144ef8497b4d64906ae27b1377b544abd6e0639133c8d85a3fabc23`.
- Minimal3199 data/lifecycle report: `data/processed/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_v5/DATA_LIFECYCLE_POSTRUN_REPORT.json` — SHA-256 `cef61be96edcc374351646e8698583fbf1b80807b05dbbbc5d3b265a8cffcfae`.
- Minimal3199 independent scientific disposition: `artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/SCIENTIFIC_POSTRUN_REVIEW_REV1.json` — SHA-256 `291570279be3bef29b31bf079455ff140e91b5c68254ad252eeba81a2e9b004e`.
- Accepted network: `artifacts/stage6_targeted_validation_20260920_v1/engineering/build_attempts/TV_BUILD01/network.net.xml` — SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`.

Independent `simulation_engineer` and `data_analyst` agents reviewed the existing engineering and data evidence separately and reported no evidence of R900/R1080 capacity. Historical facts and demand arithmetic have High confidence; future rate realization remains Unknown.
