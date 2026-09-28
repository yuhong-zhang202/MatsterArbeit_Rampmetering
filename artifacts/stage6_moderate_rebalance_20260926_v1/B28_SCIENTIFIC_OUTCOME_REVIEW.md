# Independent B_REBALANCED28 scientific outcome disposition

**Date:** 2026-09-26  
**Reviewer:** project `scientific_reviewer`, read-only raw spot reaggregation after completed engineering/data audits.  
**Disposition:** `B_PROTECTION_NOT_SUPPORTED_IN_TESTED_PAIR`; D-011 B `NOT_IDENTIFIED`; Stage 6 remains `PARTIAL`. Confidence High for the measured fixed-pair sign and complete-cohort costs; physical cause of the default-model M difference Unknown. This versioned record archives the independent review previously reported in `docs/PROJECT_STATE.md` and `docs/WORKLOG.md`; it does not revise raw or the original B22 review.

## Eligibility and observed outcome

Card SHA-256 `2de27a60cb273795a41cf0bb5a7271fda122326bd09606651c661216e359e96d`; one 2700-s completed start, 22/22 raw hashes, actual 28G+3y+29r and all M1396/R240/U150/X75 inserted/FCD-observed/arrived. A/B28 requested demand is byte-identical, and 38,810 `[0,540)` M/U/X FCD tuples plus 583 departures match. Actual R merge entries by1500 are A226/B28 222, so the realized cumulative R contrast is small.

The reviewer independently parsed raw FCD, tripinfo and E2: fixed active M core speed A26.96405/B28 25.37589 m/s, M core sample count 16,528/17,544, M1396 mean trip 73.56375/74.28510 s and timeLoss B28−A +0.727 s; first downstream M count by1500 is 1,345 in both. No coherent freeway protection is observed. R240 mean trip B28−A +15.642 s, ramp-storage E2 jam-positive 34/90 bins maximum7 (A0); U150 mean trip is unchanged. These are single-seed descriptive differences, not a controller effect estimate.

Earliest common M difference occurs at t594 about 234 m ahead of A's first R, and by t599 22 M at x<1000 m differ. This repeats an early nonlocal default-model divergence, so the physical cause of the unfavorable M sign is unidentified. A large aggregate improvement, had one appeared, would not have overridden that confound under the prospective plan. The 28G result does not prove no moderate controller can work.

## Five measurement checks and scope

Target definition PASS: M-only x=[1300,1800) fixed cells, vehicle-second weighting, full M/R/U/X cohorts, external waiting separate. Named E2 coverage PASS only on `ramp_storage_0` and `shared_approach_0`; runtime interval coverage is complete but continuous front across internal connectors is not proved. Omission/duplication PASS: full 2700-s FCD, all identities and outcomes, no uninserted/unfinished, exact pre-R; a later independent read-only per-vehicle continuity supplement found zero interior gaps, duplicate ID/seconds or depart/arrival endpoint exceptions in A or B28 (`B28_FCD_CONTINUITY_SUPPLEMENT.md`). Independent raw reconciliation PASS for core/trip/E2 quantities. Regression protection PASS for analyzer's timestamp, merge lanes, upstream R, missing/duplicate FCD and incomplete cohorts; any future continuous-spillback claim needs a separate mapped-front test.

The original 22G arm has still larger R/U costs than B28, but was itself negative in the intended B role and cannot be silently relabeled as a prospectively tested C. Without a B freeway benefit, the full freeway–ramp–urban trade-off is not established. The original C12G remains HOLD. The prespecified B28 candidate chain stops here. A later, separately reviewed altered-model sigma0 B22 missing-cell diagnostic was allowed solely to investigate mechanism sensitivity; it does not revise this default-model disposition.

**Evidence:** `data/processed/stage6_moderate_rebalance_20260926_v1/outcome_v1/B28_OUTCOME_DATA_REVIEW.md`, `A_B28_SUMMARY.json`, immutable raw and receipt under this artifact's `inputs/`, and the prospective plan in this directory. The independent reviewer directly reaggregated raw FCD/tripinfo/E2; no source or result was overwritten.
