# Independent development data report — FIX02, 2026-10-07

Status: **18/18 authorized cells accounted for; independent data and observed safety/rule audit complete. Final scientific synthesis review remains the primary agent's gate.** DEVELOPMENT ONLY. Formal protocol remains empty/unfrozen; no formal inference or sweet-spot decision.

## Context and version boundary

Read AGENTS.md, PROJECT_STATE.md, DECISIONS.md (D-018/D-019), the intentionally empty EXPERIMENT_PROTOCOL.md, relevant WORKLOG entries, exact AUTHORIZATION.md, analysis contract and scientific FIX02/remaining-eight releases. D-019 authorizes only M3600/R750 or900/U360/X180, seeds17/23/42, T0/T1/T2 at4200s. Stage6 closure is unchanged. No parameter, raw, simulation, governance or thesis file was edited by this analysis.

Six qualified OPEN baselines and12 common FIX02 controls form the current comparison. R900/S17 OPEN uses the new fully neutral run; the other five are reliable old OPEN reuse. Four pre-FIX02 controlled outcomes cannot be reused: native observed green counterexamples refute corrected-command equivalence. They remain historical/diagnostic, including the original rate failures. The failed654s attempt contributes no4200s effect estimate. Prior checkpoint tables and figures are preserved.

## Input validation and transformations

Each controlled card matches its completed raw receipt; every manifest file hash/size, input demand/network and paired seed is checked. All classes retain every planned vehicle. For planned departure p, actual departure d and arrival a, restricted system cost is min(a,4200)−p, source wait is min(d,4200)−p, and in-network cost is their difference; unavailable future events are censored at4200, never imputed as real arrivals. Independent cumulative summary integrals reconcile totals. Full class table includes mean system time per requested vehicle, not completed-only mean.

Pre600 paired trajectories match; 2856 lane occupancy windows match XML at the original0.0050001 percentage-point tolerance. Event occupancy and nominal ALINEA recurrence are independently replayed; final T2 command and trigger/release counters match the registered rule. Controller pre-step t matches FCD label t−1. Across12 controls, 43200 complete entrant snapshots and every actual-green post-state population were checked against FCD. Native FIX02 precondition arithmetic, unchanged post criterion, pulse credit/drop accounting and actual stopline crossings pass. 6288 greens yielded the intended single front, with no red/multiple/wrong-front crossing; minimum observed post margin is0.857185m. These are observations on these runs, not a universal safety proof. SecureGap and type dynamics remain conditional on recorded version-bound TraCI values; rounded FCD is not treated as exact dynamics.

No failed/missing/anomalous run is silently discarded. Current coverage18, class rows72, controlled fixed service windows72. Run-accounting sums: planned72000, inserted72000, arrived71591, unfinished409, undeparted0. These sum distinct runs, not one population. Endpoint IDs, lane/position/speed and per-class counts are retained.

## Observed service and within-demand costs

The registered10% service screen has **71/72 failing windows**, with0 not tested for continuous supply; observed eligible errors span7.59%–40.00%. The sole passing window is R750/S23/T1 [2100,2400):43 actual crossings versus46.529768 requested,7.586043%error. That run still fails its overall all-window screen. Refused states and dropped credit are separately retained. Denial-reason counts do not causally allocate lost crossing counts. A completed, fully reconciled negative-capability run remains valid development evidence, but is not qualified900-service implementation.

Whole planned-cohort restricted system time, vehicle-seconds:

|Ramp veh/h|Seed|OPEN|T1|T2|T2−T1|Unfinished T1/T2|
|---|---|---:|---:|---:|---:|---:|
|750|17|306854|579622|575140|-4482|0/0|
|750|23|305410|607444|582152|-25292|0/0|
|750|42|303560|604597|578653|-25944|0/0|
|900|17|556391|881319|876315|-5004|66/62|
|900|23|417743|904315|891536|-12779|75/68|
|900|42|507666|891784|886504|-5280|69/69|

These are paired descriptive differences within the same demand and seed. No p-values, confidence intervals, acceptance thresholds or across-demand policy ranking were introduced. Complete class/source/in-network contrasts are in the paired table. Do not infer general superiority from three development seeds.

The override table preserves every transition, active duration and natural release observation. R750/S17 demonstrated activation and release; R900/S17 did not naturally release. Other seeds are reported separately; offline branch tests remain distinct from traffic evidence. Risk extent is measured from R low-speed vehicle rears in storage/internal connector coordinates; storage vehicle count is not a stopped-queue count. The strict >=30s continuous shared-chain episode total is0; shared-road exposure cannot explain all U source/system cost causally.

## All actual attempts and resources

The new-development ledger contains16 worker attempts, 15 observed SUMO starts and14 completed4200s executions, including preserved diagnostic runs. Total guardian wall875.307s; manifest payload1323070588bytes, physical raw directories1323153268bytes. These differ because receipts are additional files. Prepared A01 cards and FIX01 offline startup-field repair are not counted as worker/SUMO starts. The socket failure,654s interlock abort and their replacements retain distinct rows and version hashes.

Future draft projections use completed current OPEN n=1, T1 n=6, T2 n=6 strata. **60runs =30OPEN+30T1;90runs =30OPEN+30T1+30T2.** Mean arithmetic estimates:60≈54.46min/3.769GB;90≈84.47min/6.872GB. Observed-sample arithmetic ranges:60 46.02–69.50min/3.498–4.002GB;90 70.95–104.71min/6.336–7.351GB. OPEN n=1 is a material limitation. These are not confidence intervals, upper bounds or approval. Setup, analysis, review, retries and future logging changes are excluded. Prior receipt's20each60-run estimate is preserved as an alternative mix, superseded for the draft projection.

## Reproducibility, figures and limits

Sources/gates/table hashes: FINAL_DATA_RECEIPT_FIX02_V2.json (actual draft resource composition). Plot inputs: render_provenance_fix02_final.json and DIAGNOSTIC_RENDER_RECEIPT_FIX02.json. Per-run audit folders preserve parser source snapshots; final renderer and summary snapshots are adjacent. Existing R750/S17 OPEN analyzer source drift was resolved for its3080 plotted pooled cells by prior raw reaggregation with zero numerical difference; this does not revalidate every historical classifier. All figures retain common axes/units and use current FIX02 series only, except the explicitly labelled historical failed-envelope diagnostic.

Tables: shared_exposure_controls_fix02_final.csv(36 control-only class rows for[1200,3000)), coverage_fix02_final.csv(18), class_costs_fix02_final.csv(72), paired_descriptive_fix02_final.csv, total_cost_contrasts_fix02_final.csv, service_windows_fix02_final.csv(72), endpoint_vehicles_fix02_final.csv, override_coverage_fix02_final.csv(12), attempt_ledger_fix02_final.csv. Figures: two mainline grids, twelve command/service/risk panels, two class-cost panels, endpoint residuals, service errors and historical failure envelope. Mean per-requested and all costs are traceable to class and vehicle records.

Safest next step: independent scientific synthesis review and user/supervisor discussion of service limits, common endpoint and formal design. No further simulation, parameter tuning, formal inference, clearance extension, email or protocol freeze follows from this data report. Primary owns PROJECT_STATE/WORKLOG and final project handoff.


Visual verification: mainlineR900 grid, R750/S42/T2 command-risk panel, R900 class-cost panel, endpoint and service-error plots inspected; axes, units and source values agree. All19PNG files pass image decoding and final table/hash checks. Remaining same-template panels were checked programmatically, not individually visually inspected.
