"""Source-bound descriptive checkpoint and cost/runtime ledger, no inference."""
import csv,json,hashlib,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/formal_development_20261007_v1';FIG=ROOT/'results/figures/formal_development_20261007_v1';LABEL='checkpoint_s17_hold'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:list(csv.DictReader(Path(p).open()))
coverage=read(TABLE/f'coverage_{LABEL}.csv');costs=read(TABLE/f'class_costs_{LABEL}.csv');paired=read(TABLE/f'paired_descriptive_{LABEL}.csv');valid=[r for r in coverage if r['status'] in ['REUSED_DATA','NEW_INDEPENDENTLY_AUDITED']]
assert len(coverage)==18 and len(valid)==10 and len(costs)==40 and len(paired)==60
assert len({(r['q_ramp'],r['seed'],r['treatment']) for r in coverage})==18
assert len({(r['q_ramp'],r['seed'],r['treatment'],r['vehicle_class']) for r in costs})==40
assert sum(r['status']=='FAILED_ATTEMPT_NO_EFFECT_DATA' for r in coverage)==1 and sum(r['status']=='NOT_RUN' for r in coverage)==7
assert not any('R750_S17_T1' in r['run_id'] for r in costs)
sources={};drifts=[]
for r in valid:
 p=Path(r['processed']);s=json.loads((p/'summary.json').read_text());sources[str(p/'summary.json')]=sha(p/'summary.json')
 for filename,expected in s['source_hashes'].items():
  f=Path(filename)
  if f.exists():
   observed=sha(f)
   if observed!=expected:
    assert r['run_id']=='M3600_R750_S17' and f.name=='analyze.py'
    drifts.append({'run_id':r['run_id'],'path':str(f),'historical_expected':expected,'current_observed':observed,'resolution':'All3080 plotted pooled M cells independently reaggregated from immutable FCD; sample counts and mean speeds identical. Other historical metrics not revalidated by this check.'})
   sources[str(f)]=observed
 for n in ['T2_DATA_GATE.json','OPEN_DATA_GATE.json']:
  if (p/n).exists():sources[str(p/n)]=sha(p/n)
reagg=BASE/'PANEL_R750_S17_RAW_REAGG/PANEL_REAGGREGATION.json';sources[str(reagg)]=sha(reagg)
ledger=[]
for f in sorted((ROOT/'artifacts/formal_development_20261007_v1/receipts').glob('*.json')):
 r=json.loads(f.read_text());raw=ROOT/'data/raw/formal_development_20261007_v1'/r['run_id']/'outputs';physical=sum(p.stat().st_size for p in raw.rglob('*') if p.is_file());sources[str(f)]=sha(f)
 started=(raw/'sumo.log').exists() and 'Simulation version' in (raw/'sumo.log').read_text()
 ledger.append(dict(run_id=r['run_id'],status=r['status'],return_code=r['return_code'],SUMO_started=started,wall_s=r['wall_s'],manifest_output_bytes=r['output_bytes'],directory_bytes=physical,role='Failed worker beforeSUMO' if not started else 'Failed interlock at654; no complete effects' if r['status']=='FAILED' else 'Completed4200; qualification separate',receipt_sha256=sha(f)))
assert len(ledger)==4 and sum(r['SUMO_started'] for r in ledger)==3
with (TABLE/f'attempt_ledger_{LABEL}.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
complete=[r for r in ledger if r['status']=='COMPLETED'];assert len(complete)==2
meanwall=sum(r['wall_s'] for r in complete)/2;meanbytes=sum(r['manifest_output_bytes'] for r in complete)/2
estimates={str(n):{'observed_sample_count':2,'wall_mean_minutes':n*meanwall/60,'wall_observed_sample_range_minutes':[n*min(r['wall_s'] for r in complete)/60,n*max(r['wall_s'] for r in complete)/60],'output_mean_decimal_GB':n*meanbytes/1e9,'output_observed_sample_range_decimal_GB':[n*min(r['manifest_output_bytes'] for r in complete)/1e9,n*max(r['manifest_output_bytes'] for r in complete)/1e9]} for n in [60,90]}
outputs={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for directory in [TABLE,FIG] for p in directory.glob('*'+LABEL+'*') if p.is_file()}
snapshot=BASE/f'render_descriptive_source_snapshot_{LABEL}.py'
with snapshot.open('x') as f:f.write((BASE/'render_descriptive.py').read_text())
receipt={'classification':'DEVELOPMENT_DESCRIPTIVE_CHECKPOINT','coverage':{'expected':18,'valid_complete':10,'failed_no_complete_data':1,'not_run':7},'row_counts':{'class_costs':40,'paired_descriptive':60,'attempts':4},'sources':sources,'historical_source_drift_resolution':drifts,'outputs':outputs,'render_script_snapshot_sha256':sha(snapshot),'report_script_sha256':sha(__file__),'runtime_estimates_provisional':estimates,'runtime_estimates_scope':'Only two completed new attempts OPEN andT2; arithmetic extrapolation, not resource approval or future upper bound. Excludes analysis/review/setup/future output changes/retries.','visual_checks':['R900 space-time','R900S17 T2 command/actual/storage/risk/active','R750S17 failed pre/post envelope'],'limitations':['Development data, no formal inference or sweet-spot decision.','10 complete combinations are not10 independent seeds.','T2 only seed17; rate capacity remainsNOT_QUALIFIED_10PCT.','One affected historical panel rawreaggregated; remaining plotted historical panels are source-bound existing derivations.']}
with (BASE/f'CHECKPOINT_ANALYSIS_RECEIPT_{LABEL}.json').open('x') as f:json.dump(receipt,f,indent=2)
cc={t:{r['vehicle_class']:float(r['system_time_T_s']) for r in costs if r['q_ramp']=='900' and r['seed']=='17' and r['treatment']==t} for t in ['T0','T1','T2']}
for v in cc.values():v['ALL']=sum(v.values())
lines=[]
for g in ['M','R','U','X','ALL']:lines.append(f"|{g}|{cc['T0'][g]:.0f}|{cc['T1'][g]:.0f}|{cc['T2'][g]:.0f}|{cc['T2'][g]-cc['T0'][g]:+.0f}|{cc['T2'][g]-cc['T1'][g]:+.0f}|")
endpoint={k:sum(int(r[k]) for r in costs) for k in ['planned','inserted','arrived','unfinished','undeparted']};assert endpoint==dict(planned=40200,inserted=40200,arrived=40200,unfinished=0,undeparted=0)
text=f'''# Development trial data checkpoint — 2026-10-07

**Status: HOLD / partial development characterization; not completed.** Stage6 closeout and empty/unfrozen formal protocol are unchanged. No formal statistics or acceptance decision is made here.

## Coverage and exclusions

The18 authorized demand×treatment×seed cells currently contain **10 valid complete combinations,1 failed attempt with no complete effect evidence,7 not run**. These are6 OPEN,3 historical qualifiedR900 T1,and1 newR900/S17 T2. New neutral OPEN replaces the old equivalentR900/S17 coverage cell rather than adding a replicate. All10 complete runs finish4200s: summed across distinct combinations planned/inserted/arrived={endpoint['planned']}/{endpoint['inserted']}/{endpoint['arrived']}, unfinished/undeparted0/0. These sums are run accounting, not one shared vehicle population.

Failed R750/S17T1 A02 is retained in coverage and runtime/storage; no4200 cost or controller effect is imputed. At simulation654,765 inserted,669 arrived,96 still in-network(M74/R12/U7/X3). Tripinfo contains766 records:765 departed plus1 M_flow.654 depart−1/vaporized=end termination record, separately classified. It is not counted as physical insertion, collision disappearance or successful arrival. Three new SUMO executions plus one pre-SUMO failed worker are distinguished below; old reuse does not launch simulation.

## R900/S17 paired descriptive costs

Whole planned-cohort restricted system time through4200s, vehicle-seconds, including source delay. All vehicles completed in these three runs.

|Group|OPEN T0|V15 T1|Queue override T2|T2−T0|T2−T1|
|---|---:|---:|---:|---:|---:|
{chr(10).join(lines)}

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

This batch has4 worker attempt receipts:3 SUMO starts(2 completed4200,1 safety failure654),1 pre-SUMO socket failure. Actual manifest output sum{sum(r['manifest_output_bytes'] for r in ledger):,}bytes; physical output-directory sum including execution receipts{sum(r['directory_bytes'] for r in ledger):,}bytes. Guardian wall total{sum(r['wall_s'] for r in ledger):.3f}s. Individual details are in the attempt ledger; worker wall is not SUMO-only CPU time.

Only the **two completed new runs** support the rough projection: OPEN39.692s/21.104MB, T234.713s/52.057MB(decimal). Mean extrapolation60runs≈{estimates['60']['wall_mean_minutes']:.2f}min and{estimates['60']['output_mean_decimal_GB']:.3f}GB;90runs≈{estimates['90']['wall_mean_minutes']:.2f}min and{estimates['90']['output_mean_decimal_GB']:.3f}GB. Observed-sample arithmetic ranges are60:{estimates['60']['wall_observed_sample_range_minutes'][0]:.2f}–{estimates['60']['wall_observed_sample_range_minutes'][1]:.2f}min/{estimates['60']['output_observed_sample_range_decimal_GB'][0]:.3f}–{estimates['60']['output_observed_sample_range_decimal_GB'][1]:.3f}GB;90:{estimates['90']['wall_observed_sample_range_minutes'][0]:.2f}–{estimates['90']['wall_observed_sample_range_minutes'][1]:.2f}min/{estimates['90']['output_observed_sample_range_decimal_GB'][0]:.3f}–{estimates['90']['output_observed_sample_range_decimal_GB'][1]:.3f}GB. These are **provisional arithmetic, not statistical intervals, future bounds or run authorization**. They omit development/setup, analysis, rendering, scientific review, retries and changed future logging. Three-seed formal runtime or storage is not inferred from legacy cached reuse.

## Files and handoff

- Tables: `results/tables/formal_development_20261007_v1/*checkpoint_s17_hold.csv`.
- Figures: `results/figures/formal_development_20261007_v1/*checkpoint_s17_hold.png`.
- Full source/output/runtime receipt: `CHECKPOINT_ANALYSIS_RECEIPT_checkpoint_s17_hold.json`; render provenance and source snapshot retained.
- New completed gates: `OPEN_R900_S17_A03/OPEN_DATA_GATE.json`, `T2_R900_S17_A02/T2_DATA_GATE.json` and `capacity_credit_diagnostics.json`.
- Failed raw reconciliation: `FAILED_R750_S17_T1_A02_audit3/FAILED_ATTEMPT_AUDIT.json`, endpoint vehicles and source snapshot.
- Affected historical panel resolution: `PANEL_R750_S17_RAW_REAGG/PANEL_REAGGREGATION.json` and reaggregated plotting cells.

Safest next step: finish engineering and read-only scientific disposition of the pre/post safety contradiction, retain the capability limitation, then let the primary agent record HOLD or issue the already authorized bounded repair/retry with a source-version boundary. No new simulation or governance file was changed by the data analyst. The primary agent owns PROJECT_STATE/WORKLOG and final research interpretation.
'''
with (BASE/'DATA_CHECKPOINT_REPORT.md').open('x') as f:f.write(text)
print(json.dumps({'report':str(BASE/'DATA_CHECKPOINT_REPORT.md'),'endpoint_totals':endpoint,'wall_s':sum(r['wall_s'] for r in ledger),'output_directory_bytes':sum(r['directory_bytes'] for r in ledger),'estimates':estimates}))
