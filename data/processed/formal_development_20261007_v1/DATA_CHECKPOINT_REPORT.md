# Development trial data checkpoint — 2026-10-07

**Status: HOLD / partial development characterization; not completed.** Stage6 closeout and empty/unfrozen formal protocol are unchanged. No formal statistics or acceptance decision is made here.

## Coverage and exclusions

The18 authorized demand×treatment×seed cells currently contain **10 valid complete combinations,1 failed attempt with no complete effect evidence,7 not run**. These are6 OPEN,3 historical qualifiedR900 T1,and1 newR900/S17 T2. New neutral OPEN replaces the old equivalentR900/S17 coverage cell rather than adding a replicate. All10 complete runs finish4200s: summed across distinct combinations planned/inserted/arrived=40200/40200/40200, unfinished/undeparted0/0. These sums are run accounting, not one shared vehicle population.

Failed R750/S17T1 A02 is retained in coverage and runtime/storage; no4200 cost or controller effect is imputed. At simulation654,765 inserted,669 arrived,96 still in-network(M74/R12/U7/X3). Tripinfo contains766 records:765 departed plus1 M_flow.654 depart−1/vaporized=end termination record, separately classified. It is not counted as physical insertion, collision disappearance or successful arrival. Three new SUMO executions plus one pre-SUMO failed worker are distinguished below; old reuse does not launch simulation.

## R900/S17 paired descriptive costs

Whole planned-cohort restricted system time through4200s, vehicle-seconds, including source delay. All vehicles completed in these three runs.

|Group|OPEN T0|V15 T1|Queue override T2|T2−T0|T2−T1|
|---|---:|---:|---:|---:|---:|
|M|467230|230515|231628|-235602|+1113|
|R|58984|365441|196684|+137700|-168757|
|U|19888|110473|50255|+30367|-60218|
|X|10289|10486|10288|-1|-198|
|ALL|556391|716915|488855|-67536|-228060|

T2 has less mainline cost thanOPEN and much smallerR/U cost thanT1 in this one development seed. It still imposes moreR/U cost thanOPEN. No robust sweet spot or acceptable threshold is established. T2 total488855=source34205+in-network454650s; independent cumulative accounting residuals0. Prior9 reuse costs were independently recalculated and reconciled.

## T2 mechanical, data and service distinction

- Complete high-precision mapped observations match FCD(t−1) for3600 control pre-steps; actual vehicle lengths/risk coordinates and both hysteresis transitions replay. Override active1132–3454(2322s). Nominal ALINEA recurrence remains independent of final rate.334 rounded-FCD speed-boundary cases retain precision uncertainty.
-600 qualified greens,600 correct front crossings, red/multiple/wrong-front0; moving448/stopped152. The old stopped-only service helper generated inapplicable geometry flags; original output is retained and supplementary V15 branch-specific FCD audit passes. SecureGap remains conditional on logged SUMO API values.
-Final credit880.628543894=600greens+279.628543894dropped+1remaining. Post-green minimum margin0.7635m. All six fixed300s windows have continuous storage supply and final requested75; actual64/64/64/66/66/66. **10% rate capability NOT_QUALIFIED**: shortfalls14.667%/12%; none removed. Receiving constraints and follower safety both occur; denial/drop associations are not causal decomposition of lost crossing counts.
-During1200–3000, shared-road slow exposureR990/U393veh-s; U312 during city green, of which273 with nearest observed frontR. This is observed shared exposure, not uniquely identified spillback causation. Strict continuous>=30s meter-to-shared chain remains negative.

## R750/S17 safety failure

Raw/card/input/output manifests and54 available high-precision control snapshots pass reconciliation. Pre600 exactly matches pairedOPEN. In interval[653,654), R_flow.0 correctly crosses, but R_flow.3, already observed in the pre-green storage population, changes from pre gap89.791942m versus requirement84.223732m(margin+5.568210) to post gap68.914175m versus requirement70.409007m(margin−1.494831). Both exact sensors match rounded FCD. The pre condition does not guarantee the post condition on this trace; it is not merely an unseen new entrant. Engineering/scientific review must decide technical repair or hold. No later policy/seed is qualified from this partial run.

## Reproducibility and plot scope

Three descriptive CSV tables plus an attempt ledger and ninePNG figures retain missing/failed panels. Figures show common30s/100m M speed, group system costs, nominal/final/actual discharge, storage vehicle count(distinct from stopped queue), override risk/state and the failure envelope. MainlineR900, T2 command/risk and failed-envelope images were visually inspected; labels/units/layout distinguish missing data and failure.

One concrete historical source drift was detected: R750/S17 summary's original boundary-analysis SHA371aa35f… differs from current6594bbf…. Costs remain independently raw-calculated. All3080 plotted pooled mean-speed cells of that affected panel were independently reaggregated from the original4200 FCD records: samples and means match exactly(max speed residual0). Original files remain unchanged. This verifies that panel's numerical input; it does not revalidate every historical classifier or metric. Other historical panels retain matching source-bound derivations. Machine receipt records expected/current drift, resolution, sources and output SHA hashes.

## Runtime/storage observations and provisional scale

This batch has4 worker attempt receipts:3 SUMO starts(2 completed4200,1 safety failure654),1 pre-SUMO socket failure. Actual manifest output sum75,337,828bytes; physical output-directory sum including execution receipts75,354,965bytes. Guardian wall total99.809s. Individual details are in the attempt ledger; worker wall is not SUMO-only CPU time.

Only the **two completed new runs** support the rough projection: OPEN39.692s/21.104MB, T234.713s/52.057MB(decimal). Mean extrapolation60runs≈37.20min and2.195GB;90runs≈55.80min and3.292GB. Observed-sample arithmetic ranges are60:34.71–39.69min/1.266–3.123GB;90:52.07–59.54min/1.899–4.685GB. These are **provisional arithmetic, not statistical intervals, future bounds or run authorization**. They omit development/setup, analysis, rendering, scientific review, retries and changed future logging. Three-seed formal runtime or storage is not inferred from legacy cached reuse.

## Files and handoff

- Tables: `results/tables/formal_development_20261007_v1/*checkpoint_s17_hold.csv`.
- Figures: `results/figures/formal_development_20261007_v1/*checkpoint_s17_hold.png`.
- Full source/output/runtime receipt: `CHECKPOINT_ANALYSIS_RECEIPT_checkpoint_s17_hold.json`; render provenance and source snapshot retained.
- New completed gates: `OPEN_R900_S17_A03/OPEN_DATA_GATE.json`, `T2_R900_S17_A02/T2_DATA_GATE.json` and `capacity_credit_diagnostics.json`.
- Failed raw reconciliation: `FAILED_R750_S17_T1_A02_audit3/FAILED_ATTEMPT_AUDIT.json`, endpoint vehicles and source snapshot.
- Affected historical panel resolution: `PANEL_R750_S17_RAW_REAGG/PANEL_REAGGREGATION.json` and reaggregated plotting cells.

Safest next step: finish engineering and read-only scientific disposition of the pre/post safety contradiction, retain the capability limitation, then let the primary agent record HOLD or issue the already authorized bounded repair/retry with a source-version boundary. No new simulation or governance file was changed by the data analyst. The primary agent owns PROJECT_STATE/WORKLOG and final research interpretation.
