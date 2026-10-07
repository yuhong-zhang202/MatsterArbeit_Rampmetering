"""Final current-version accounting, all-attempt ledger and stratified resources."""
import csv,hashlib,json,statistics,shutil
from collections import Counter
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];T=ROOT/'results/tables/formal_development_20261007_v1';F=ROOT/'results/figures/formal_development_20261007_v1';LABEL='fix02_final'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(Path(p).open()))
def dump(name,rows):
 with (T/name).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 coverage=read(T/f'coverage_{LABEL}.csv');costs=read(T/f'class_costs_{LABEL}.csv');assert len(coverage)==18 and len(costs)==72
 assert len({(r['q_ramp'],r['seed'],r['treatment'],r['vehicle_class']) for r in costs})==72
 gates={};sources={};endpoints=[];windows=[];queue=[];exposures=[]
 for r in coverage:
  p=Path(r['processed']);sources[str(p/'summary.json')]=sha(p/'summary.json')
  if r['treatment']=='T0':continue
  g=json.load((p/'FIX02_DATA_GATE.json').open());gates[r['run_id']]=g;sources[str(p/'FIX02_DATA_GATE.json')]=sha(p/'FIX02_DATA_GATE.json')
  assert g['data_layer']=='PASS' and g['safety_and_rule_replay']=='PASS_OBSERVED_RUN'
  for e in json.load((p/'endpoint_vehicles.json').open()):endpoints.append(dict(run_id=r['run_id'],q_ramp=r['q_ramp'],seed=r['seed'],treatment=r['treatment'],**e))
  raw=ROOT/'data/raw/formal_development_20261007_v1'/r['run_id']/'outputs';controlrows=read(raw/'controller_steps.csv')
  for w in g['capacity_windows']:
   reasons=Counter(x['guard_reason'] for x in controlrows[w['begin']:w['end']] if x['guard_rejected_slot'].lower()=='true')
   assert sum(reasons.values())==w['denied_due_seconds']
   windows.append(dict(run_id=r['run_id'],q_ramp=r['q_ramp'],seed=r['seed'],treatment=r['treatment'],**w,denied_reasons_json=json.dumps(reasons,sort_keys=True)))
  city=json.load((p/'city_evidence.json').open());sources[str(p/'city_evidence.json')]=sha(p/'city_evidence.json')
  for group in ['R','U','X']:
   bins=[x for x in city['lane_bins'] if x['lane']=='shared_approach_0' and x['vehicle_class']==group and 1200<=x['begin']<3000]
   contexts=[x for x in city['all_U_slow_context'] if x['lane']=='shared_approach_0' and 1200<=x['time']<3000] if group=='U' else []
   exposures.append(dict(run_id=r['run_id'],q_ramp=r['q_ramp'],seed=r['seed'],treatment=r['treatment'],vehicle_class=group,begin=1200,end=3000,shared_vehicle_seconds=sum(x['vehicle_seconds'] for x in bins),shared_slow_lt1p389_vehicle_seconds=sum(x['slow_lt1p389_vehicle_seconds'] for x in bins),shared_stop_lt0p1_vehicle_seconds=sum(x['stop_lt0p1_vehicle_seconds'] for x in bins),U_shared_slow_during_urban_green=sum(x['urban_entry_green'] for x in contexts),U_shared_slow_green_nearest_front_R=sum(x['urban_entry_green'] and x['ahead_class']=='R' for x in contexts)))
  queue.append(dict(run_id=r['run_id'],q_ramp=r['q_ramp'],seed=r['seed'],treatment=r['treatment'],active_seconds=g['queue']['active_seconds'],transitions=json.dumps(g['queue']['transitions']),natural_release_observed=g['queue']['release_coverage'],strict_30s_shared_episodes=g['strict_continuous_30s_shared_episodes']))
 assert len(gates)==12 and len(windows)==72
 if endpoints:dump(f'endpoint_vehicles_{LABEL}.csv',endpoints)
 dump(f'shared_exposure_controls_{LABEL}.csv',exposures)
 dump(f'service_windows_{LABEL}.csv',windows);dump(f'override_coverage_{LABEL}.csv',queue)
 ledger=[]
 for p in sorted((ROOT/'artifacts/formal_development_20261007_v1/receipts').glob('*.json')):
  r=json.load(p.open());raw=ROOT/'data/raw/formal_development_20261007_v1'/r['run_id']/'outputs';started=(raw/'sumo.log').exists() and 'Simulation version' in (raw/'sumo.log').read_text();sources[str(p)]=sha(p)
  cp=ROOT/'artifacts/formal_development_20261007_v1/inputs'/r['run_id']/'card.json';card=json.load(cp.open());assert sha(cp)==r['card_sha256']
  current=r['run_id'] in gates or r['run_id']=='DEV_M3600_R900_S17_OPEN_A03'
  ledger.append(dict(run_id=r['run_id'],ramp_veh_h=r['ramp_veh_h'],seed=r['seed'],treatment=r['treatment'],status=r['status'],return_code=r['return_code'],SUMO_started=started,current_comparison=current,wall_s=r['wall_s'],manifest_output_bytes=r['output_bytes'],directory_bytes=sum(x.stat().st_size for x in raw.rglob('*') if x.is_file()),card_sha256=r['card_sha256'],guard_revision=card.get('guard_revision','PRE_FIX02'),source_versions_json=json.dumps(card['source_sha256'],sort_keys=True),receipt_sha256=sha(p),failure=json.dumps(r.get('failure')),stop_reason=r.get('stop_reason'),diagnosis=('LOCAL_SOCKET_PERMISSION_BEFORE_SUMO' if not started else 'POST_GREEN_INTERLOCK_T654' if r['status']=='FAILED' else 'NON_EQUIVALENT_PRE_FIX02_CONTROL' if not current else ''),replacement_run_id=('DEV_M3600_R900_S17_OPEN_A03' if r['run_id']=='DEV_M3600_R900_S17_OPEN_A02' else 'DEV_M3600_R750_S17_T1_A03' if r['run_id']=='DEV_M3600_R750_S17_T1_A02' else 'DEV_M3600_R900_S17_T2_A03' if r['run_id']=='DEV_M3600_R900_S17_T2_A02' else ''),role='CURRENT_SERIES' if current else 'PRESERVED_DIAGNOSTIC_OR_FAILURE'))
 dump(f'attempt_ledger_{LABEL}.csv',ledger)
 strata={}
 for t in ['OPEN','T1','T2']:
  selected=[r for r in ledger if r['current_comparison'] and r['status']=='COMPLETED' and r['treatment']==t]
  assert len(selected)==(1 if t=='OPEN' else 6)
  strata[t]=dict(n=len(selected),mean_wall_s=statistics.mean(r['wall_s'] for r in selected),min_wall_s=min(r['wall_s'] for r in selected),max_wall_s=max(r['wall_s'] for r in selected),mean_bytes=statistics.mean(r['manifest_output_bytes'] for r in selected),min_bytes=min(r['manifest_output_bytes'] for r in selected),max_bytes=max(r['manifest_output_bytes'] for r in selected))
 estimates={}
 for n in [60,90]:
  per=n//3;estimates[str(n)]=dict(assumed_runs_per_treatment=per,wall_mean_minutes=sum(s['mean_wall_s']*per for s in strata.values())/60,wall_observed_range_minutes=[sum(s[k]*per for s in strata.values())/60 for k in ['min_wall_s','max_wall_s']],mean_decimal_GB=sum(s['mean_bytes']*per for s in strata.values())/1e9,observed_range_decimal_GB=[sum(s[k]*per for s in strata.values())/1e9 for k in ['min_bytes','max_bytes']])
 totals={k:sum(int(r[k]) for r in costs) for k in ['planned','inserted','arrived','unfinished','undeparted']}
 assert totals['planned']==totals['arrived']+totals['unfinished']+totals['undeparted'] and totals['unfinished']==len(endpoints)
 contrasts=[]
 for q in ['750','900']:
  for seed in ['17','23','42']:
   rr={t:[r for r in costs if r['q_ramp']==q and r['seed']==seed and r['treatment']==t] for t in ['T0','T1','T2']}
   contrasts.append(dict(q_ramp=q,seed=seed,**{t:sum(float(r['system_time_T_s']) for r in rows) for t,rows in rr.items()}))
   contrasts[-1].update(T1_minus_T0=contrasts[-1]['T1']-contrasts[-1]['T0'],T2_minus_T0=contrasts[-1]['T2']-contrasts[-1]['T0'],T2_minus_T1=contrasts[-1]['T2']-contrasts[-1]['T1'])
 dump(f'total_cost_contrasts_{LABEL}.csv',contrasts)
 for name in ['render_fix02_final.py','summarize_fix02_final.py','compare_fix02_seed.py']:
  target=B/(name.removesuffix('.py')+'_source_snapshot_final.py');assert not target.exists();shutil.copyfile(B/name,target)
 result=dict(classification='DEVELOPMENT_CURRENT_FIX02_FINAL',coverage=18,class_rows=72,control_gates=12,totals=totals,all_run_totals_scope='Summed run accounting, not one shared population.',rate_windows=len(windows),rate_failures=sum(w['engineering_status']=='FAIL' for w in windows),rate_not_tested=sum(not w['eligible_continuous_supply'] for w in windows),strict30s_shared_episodes=sum(q['strict_30s_shared_episodes'] for q in queue),attempts=len(ledger),SUMO_starts=sum(r['SUMO_started'] for r in ledger),completed_attempts=sum(r['status']=='COMPLETED' for r in ledger),wall_s=sum(r['wall_s'] for r in ledger),raw_manifest_bytes=sum(r['manifest_output_bytes'] for r in ledger),raw_directory_bytes=sum(r['directory_bytes'] for r in ledger),stratified_resource_samples=strata,resource_estimates=estimates,resource_scope='Equal OPEN/T1/T2 mix:20 each for60,30 each for90. OPEN n=1. Means/ranges are descriptive arithmetic, not confidence intervals or future bounds. Excludes setup, analysis, review, retries and changed logging; no formal run authorization.',sources=sources,outputs={str(p):sha(p) for folder in [T,F] for p in folder.glob('*'+LABEL+'*') if p.is_file()},contrasts=contrasts,offline_repair_events=['FIX01 missing startup field repaired before worker; see engineering/TECHNICAL_FIX01.md; not a worker/SUMO attempt.','FIX02 pre/post condition correction; exact source versions are preserved in each card and attempt ledger.'],limits=['Development seeds17/23/42; no significance or acceptable-region inference.','Historical pre-FIX02 controls are diagnostic only; all attempts preserved.','R750/S17 old OPEN plotted panel independently raw-reaggregated because historical analyzer source drift; unchanged classifier not newly validated by that panel check.','Native TraCI safety/API values audited arithmetically; FCD rounded to0.01.','Stopped-only legacy sampled_service diagnostic is superseded for FIX02 qualification by branch-aware v15_service audit plus FIX02 adapter.'])
 with (B/'FINAL_DATA_RECEIPT_FIX02.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['sources','outputs','contrasts','limits']}))
if __name__=='__main__':main()
