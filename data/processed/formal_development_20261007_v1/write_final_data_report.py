"""Write the independent descriptive report from sealed final data artifacts."""
import csv,hashlib,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];T=ROOT/'results/tables/formal_development_20261007_v1';F=ROOT/'results/figures/formal_development_20261007_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.load((B/'FINAL_DATA_RECEIPT_FIX02.json').open());costs=list(csv.DictReader((T/'class_costs_fix02_final.csv').open()));w=list(csv.DictReader((T/'service_windows_fix02_final.csv').open()));q=list(csv.DictReader((T/'override_coverage_fix02_final.csv').open()));tot=d['totals']
 rows=[]
 for c in d['contrasts']:
  r=c['q_ramp'];s=c['seed'];rr={t:sum(int(x['unfinished']) for x in costs if (x['q_ramp'],x['seed'],x['treatment'])==(r,s,t)) for t in ['T1','T2']}
  rows.append(f"|{r}|{s}|{c['T0']:.0f}|{c['T1']:.0f}|{c['T2']:.0f}|{c['T2_minus_T1']:+.0f}|{rr['T1']}/{rr['T2']}|")
 strata=d['stratified_resource_samples'];est=d['resource_estimates'];versions=['FIX02_GREEN_ADVANCE_PLUS_POST_RED'];gates=[json.load(p.open()) for p in B.glob('FIX02_T[12]_R*_S*_A03/FIX02_DATA_GATE.json')];assert len(gates)==12
 post=min(g['actuator']['min_post_green_stop_margin_m'] for g in gates);gre=sum(g['actuator']['counts']['greens'] for g in gates);sc=sum(g['entrant_and_post_sensors']['prestep_snapshots'] for g in gates);occupancy=sum(g['feedback_xml']['checked_lane_intervals'] for g in gates)
 errors=[100*float(x['relative_error']) for x in w if x['eligible_continuous_supply']=='True'];ranges=f'{min(errors):.2f}%–{max(errors):.2f}%'
 text=f'''# Independent development data report — FIX02, 2026-10-07

Status: **18/18 authorized cells accounted for; independent data and observed safety/rule audit complete. Final scientific synthesis review remains the primary agent's gate.** DEVELOPMENT ONLY. Formal protocol remains empty/unfrozen; no formal inference or sweet-spot decision.

## Context and version boundary

Read AGENTS.md, PROJECT_STATE.md, DECISIONS.md (D-018/D-019), the intentionally empty EXPERIMENT_PROTOCOL.md, relevant WORKLOG entries, exact AUTHORIZATION.md, analysis contract and scientific FIX02/remaining-eight releases. D-019 authorizes only M3600/R750 or900/U360/X180, seeds17/23/42, T0/T1/T2 at4200s. Stage6 closure is unchanged. No parameter, raw, simulation, governance or thesis file was edited by this analysis.

Six qualified OPEN baselines and12 common FIX02 controls form the current comparison. R900/S17 OPEN uses the new fully neutral run; the other five are reliable old OPEN reuse. Four pre-FIX02 controlled outcomes cannot be reused: native observed green counterexamples refute corrected-command equivalence. They remain historical/diagnostic, including the original rate failures. The failed654s attempt contributes no4200s effect estimate. Prior checkpoint tables and figures are preserved.

## Input validation and transformations

Each controlled card matches its completed raw receipt; every manifest file hash/size, input demand/network and paired seed is checked. All classes retain every planned vehicle. For planned departure p, actual departure d and arrival a, restricted system cost is min(a,4200)−p, source wait is min(d,4200)−p, and in-network cost is their difference; unavailable future events are censored at4200, never imputed as real arrivals. Independent cumulative summary integrals reconcile totals. Full class table includes mean system time per requested vehicle, not completed-only mean.

Pre600 paired trajectories match; {occupancy} lane occupancy windows match XML at the original0.0050001 percentage-point tolerance. Event occupancy and nominal ALINEA recurrence are independently replayed; final T2 command and trigger/release counters match the registered rule. Controller pre-step t matches FCD label t−1. Across12 controls, {sc} complete entrant snapshots and every actual-green post-state population were checked against FCD. Native FIX02 precondition arithmetic, unchanged post criterion, pulse credit/drop accounting and actual stopline crossings pass. {gre} greens yielded the intended single front, with no red/multiple/wrong-front crossing; minimum observed post margin is{post:.6f}m. These are observations on these runs, not a universal safety proof. SecureGap and type dynamics remain conditional on recorded version-bound TraCI values; rounded FCD is not treated as exact dynamics.

No failed/missing/anomalous run is silently discarded. Current coverage18, class rows72, controlled fixed service windows72. Run-accounting sums: planned{tot['planned']}, inserted{tot['inserted']}, arrived{tot['arrived']}, unfinished{tot['unfinished']}, undeparted{tot['undeparted']}. These sum distinct runs, not one population. Endpoint IDs, lane/position/speed and per-class counts are retained.

## Observed service and within-demand costs

The registered10% service screen has **{d['rate_failures']}/{d['rate_windows']} failing windows**, with{d['rate_not_tested']} not tested for continuous supply; observed eligible errors span{ranges}. Refused states and dropped credit are separately retained. Denial-reason counts do not causally allocate lost crossing counts. A completed, fully reconciled negative-capability run remains valid development evidence, but is not qualified900-service implementation.

Whole planned-cohort restricted system time, vehicle-seconds:

|Ramp veh/h|Seed|OPEN|T1|T2|T2−T1|Unfinished T1/T2|
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

These are paired descriptive differences within the same demand and seed. No p-values, confidence intervals, acceptance thresholds or across-demand policy ranking were introduced. Complete class/source/in-network contrasts are in the paired table. Do not infer general superiority from three development seeds.

The override table preserves every transition, active duration and natural release observation. R750/S17 demonstrated activation and release; R900/S17 did not naturally release. Other seeds are reported separately; offline branch tests remain distinct from traffic evidence. Risk extent is measured from R low-speed vehicle rears in storage/internal connector coordinates; storage vehicle count is not a stopped-queue count. The strict >=30s continuous shared-chain episode total is{d['strict30s_shared_episodes']}; shared-road exposure cannot explain all U source/system cost causally.

## All actual attempts and resources

The new-development ledger contains{d['attempts']} worker attempts, {d['SUMO_starts']} observed SUMO starts and{d['completed_attempts']} completed4200s executions, including preserved diagnostic runs. Total guardian wall{d['wall_s']:.3f}s; manifest payload{d['raw_manifest_bytes']}bytes, physical raw directories{d['raw_directory_bytes']}bytes. These differ because receipts are additional files. Prepared A01 cards and FIX01 offline startup-field repair are not counted as worker/SUMO starts. The socket failure,654s interlock abort and their replacements retain distinct rows and version hashes.

Future equal-treatment-mix projections use completed **current** OPEN n={strata['OPEN']['n']}, T1 n={strata['T1']['n']}, T2 n={strata['T2']['n']} strata.60runs means20 each;90means30 each. Mean arithmetic estimates:60≈{est['60']['wall_mean_minutes']:.2f}min/{est['60']['mean_decimal_GB']:.3f}GB;90≈{est['90']['wall_mean_minutes']:.2f}min/{est['90']['mean_decimal_GB']:.3f}GB. OPEN n=1 is a material limitation. Detailed observed ranges are sample arithmetic, not confidence intervals, upper bounds or approval. Setup, analysis, review, retries and future logging changes are excluded. The old two-run checkpoint mean is not used.

## Reproducibility, figures and limits

Sources/gates/table hashes: FINAL_DATA_RECEIPT_FIX02.json. Plot inputs: render_provenance_fix02_final.json and DIAGNOSTIC_RENDER_RECEIPT_FIX02.json. Per-run audit folders preserve parser source snapshots; final renderer and summary snapshots are adjacent. Existing R750/S17 OPEN analyzer source drift was resolved for its3080 plotted pooled cells by prior raw reaggregation with zero numerical difference; this does not revalidate every historical classifier. All figures retain common axes/units and use current FIX02 series only, except the explicitly labelled historical failed-envelope diagnostic.

Tables: coverage_fix02_final.csv(18), class_costs_fix02_final.csv(72), paired_descriptive_fix02_final.csv, total_cost_contrasts_fix02_final.csv, service_windows_fix02_final.csv(72), endpoint_vehicles_fix02_final.csv, override_coverage_fix02_final.csv(12), attempt_ledger_fix02_final.csv. Figures: two mainline grids, twelve command/service/risk panels, two class-cost panels, endpoint residuals, service errors and historical failure envelope. Mean per-requested and all costs are traceable to class and vehicle records.

Safest next step: independent scientific synthesis review and user/supervisor discussion of service limits, common endpoint and formal design. No further simulation, parameter tuning, formal inference, clearance extension, email or protocol freeze follows from this data report. Primary owns PROJECT_STATE/WORKLOG and final project handoff.
'''
 p=B/'DATA_REPORT_FIX02_FINAL.md'
 with p.open('x') as f:f.write(text)
 snapshot=B/'write_final_data_report_source_snapshot.py';assert not snapshot.exists();shutil.copyfile(Path(__file__),snapshot)
 with (B/'FINAL_REPORT_ARTIFACT_MANIFEST.json').open('x') as f:json.dump(dict(report_sha256=sha(p),script_sha256=sha(Path(__file__)),tables={str(p):sha(p) for p in T.glob('*fix02_final*')},figures={str(p):sha(p) for p in F.glob('*fix02_final*')}),f,indent=2)
 print(p)
if __name__=='__main__':main()
