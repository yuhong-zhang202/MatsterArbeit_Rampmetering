# CLEAN3199_A_R900_DELAYED_S17 — retrospective exploratory sensitivity analysis

**Final scientific disposition: `NOT_EVALUABLE` (High confidence).** This analysis follows the user's D-010 adoption of the reviewed T3 measurement clarification. It is an analysis of existing Stage 6 exploratory raw, not a prospective or formal experiment. The original D-009 auxiliary-E1 rule and historical `NOT_EVALUABLE / EXPOSURE_GATE_NOT_MET` receipt remain untouched and independently interpretable.

## Scope and provenance

- Treatment: `CLEAN3199_A_R900_DELAYED_S17`, qMain=3199.2 veh/h, delayed R900 on `[540,1500)`, seed17, U=X=0. Matched comparator: the existing minimal3199 R=0 control. M planned identity, desired/actual departure, route, vType, speedFactor and departure delay match by vehicle. M=1,333 in each arm, R=240 only in treatment; all arrived, zero unfinished.
- Before R activation (`t<540`), 32,513 matched M vehicle-second trajectory records are exact. The original raw manifests verify 25/25 files in each arm. No new simulation was started.
- The D-010 clarification addresses a measured spatial mismatch: auxiliary E1 is at 20 m and misses R vehicles that leave the auxiliary lane sooner. The full reviewed per-vehicle certain-entry ledger establishes T3 at **690 s**; the literal D-009 E1 counts remain 8/0/13 and fail. First R through-lane FCD observation is t=584. R900 has 209/225 unique first through-lane identities by inclusive t=1440/1500, above the pre-frozen same-qMain R720 comparator 167/183.

## Locked outcomes and matched comparison

- Unchanged P and S have **zero duration-qualified merge-core events** in the primary window; Candidate A=0. Candidate C core warning bins are retained: treatment/control 34/19 within `[720,1500)` and 42/20 across the full 2,700 s. Candidate C is diagnostic, not State1 qualification.
- Treatment has **six duration-qualified L core episodes** with first low bins in the fixed `[720,1440)` onset window (cell13 onset 720; cell14 onsets 720, 1140, 1380; cell15 onsets 990, 1380). Every episode has an ineligible immediately preceding three-bin reference. The control has no duration-qualified P/S/L episode. An additional cell15 L episode starting at 690 lies outside the primary onset window and is retained in the full event ledger; it was not selected or suppressed to improve the result.
- The full 22-cell × two-lane × 90-bin matched table is retained. For example, cell14 treatment/control speed ratios are 0.625/0.750 in `[720,750)` and 0.704/0.883 in `[750,780)`. This is a descriptive matched difference, not a qualifying locked onset. Certain R entries continue during the six L windows.
- The first global M trajectory divergence and first R through-lane FCD observation share the t=584 label; their within-frame ordering is unresolved. A separate upstream source-region difference occurs by t=594 in seven M vehicles, before clarified T3=690. Actual M `departLane` differs for 73 IDs during t=630–711 and `departSpeed` for 327 IDs from t=594 onward, despite matched planned M attributes and actual departure times. The first two L windows directly contain 37/38 of the source-lane-changed IDs. These are post-treatment dynamic differences, not proof of an exogenous input mismatch, but source/RNG/order feedback remains an unresolved alternative to a pure merge-friction account.

## Alternative causes and precision

Engineering review found no R insertion starvation (240/240 R depart delay=0), no R ramp TLS restriction (`A_OPEN/G` throughout), complete and readable FCD/E1/E2 output files, no obvious terminal downstream tailback, and no raw/config/lifecycle mismatch. FCD covers the mapped M lanes; E1 retains its documented point-detector spatial limit. These checks support technical integrity but do not resolve the source-region attribution issue.

For cell13's `[660,690)` reference bin, the locked ratio computed from archived two-decimal FCD speed is 0.849931, below 0.85. A bounded ±0.005 m/s serialization audit gives a possible pre-serialization ratio interval `[0.849779, 0.850083]`; latent eligibility is therefore `UNDECIDABLE_PRECISION`. The locked archived-data reference status remains FAIL. The five other L reference failures remain below 0.85 under the same bound, so the final category does not hinge on cell13 rounding. No threshold or classifier was changed.

## Decision boundary

Under the locked D-009 outcome rule, a duration-qualified low episode with ineligible immediate reference is `ONSET_REFERENCE_UNRESOLVED / NOT_EVALUABLE`. The six L episodes preclude a clean `NO_WITNESS`; P/S supply no established witness; the source-region alternative also prevents a pure merge-pressure attribution. Independent scientific review therefore returns **`NOT_EVALUABLE`**, Blocker/Major/required Minor **0/2/0**. The result does not authorize R1080 or a new demand scan. Stage 6 remains `PARTIAL`; formal protocol remains unfrozen.

Detailed per-vehicle and per-bin evidence: `data/processed/stage6_clean_onset_3199_r900_retrospective_sensitivity_20260925_v2/`; precision supplement: `data/processed/stage6_clean_onset_3199_r900_retrospective_precision_20260925_v1/`; clarified T3 ledger: `data/processed/stage6_clean_onset_3199_r900_t3_recheck_20260925_v1/`.
