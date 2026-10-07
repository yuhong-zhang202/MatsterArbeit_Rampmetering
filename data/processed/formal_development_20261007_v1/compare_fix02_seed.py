"""Descriptive within-demand, within-seed contrasts from qualified FIX02 data."""
import argparse,csv,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ramp',type=int,required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--t1',required=True);ap.add_argument('--t2',required=True);ap.add_argument('--tag',required=True);a=ap.parse_args()
 paths={t:B/v/'FIX02_DATA_GATE.json' for t,v in [('T1',a.t1),('T2',a.t2)]};gates={t:json.load(p.open()) for t,p in paths.items()}
 for t,d in gates.items():
  assert d['data_layer']=='PASS' and d['safety_and_rule_replay']=='PASS_OBSERVED_RUN' and d['classification']=='DEVELOPMENT_ONLY_FIX02'
  assert f'_R{a.ramp}_S{a.seed}_{t}_' in d['run_id']
 baseline=next(r for r in json.load((B/'reuse_audit.json').open())['runs'] if r['run_id']==f'M3600_R{a.ramp}_S{a.seed}' and r['treatment']=='T0');assert baseline['eligible_existing_data']
 metric={'system_time_T_s':'scheduled_system_time_observed_total_s','source_wait_T_s':'external_wait_observed_total_s','in_network_T_s':'in_network_observed_total_s'}
 data={'T0':{r['vehicle_class']:r for r in baseline['classes']}}
 for t,d in gates.items():
  data[t]={r['vehicle_class']:{**r,**{k:r[v] for k,v in metric.items()}} for r in d['cohort']}
 records=[]
 for group in ['M','R','U','X','ALL']:
  rr={t:({k:sum(row[k] for row in rows.values()) for k in ['planned','inserted','arrived','unfinished','undeparted',*metric]} if group=='ALL' else rows[group]) for t,rows in data.items()}
  assert len({r['planned'] for r in rr.values()})==1
  for k in metric:
   row=dict(ramp=a.ramp,seed=a.seed,vehicle_class=group,metric=k,units='vehicle_seconds',planned=rr['T0']['planned'])
   for t in ['T0','T1','T2']:row[t]=rr[t][k]
   row.update(T1_minus_T0=rr['T1'][k]-rr['T0'][k],T2_minus_T0=rr['T2'][k]-rr['T0'][k],T2_minus_T1=rr['T2'][k]-rr['T1'][k]);records.append(row)
 target=ROOT/'results/tables/formal_development_20261007_v1'/f'paired_costs_{a.tag}.csv'
 with target.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 receipt=dict(classification='DEVELOPMENT_DESCRIPTIVE_PAIRED_WITHIN_DEMAND_SEED',source_sha256={str(p):sha(p) for p in [*paths.values(),B/'reuse_audit.json']},script_sha256=sha(Path(__file__)),table=str(target),table_sha256=sha(target),rows=len(records),unfinished_by_treatment={t:{c:r['unfinished'] for c,r in rows.items()} for t,rows in data.items()},interpretation='Restricted all-planned-cohort costs through4200s, not completed-only. Rate-screen failures remain NOT_QUALIFIED and do not become qualified900 service. No formal inference, causal city-delay decomposition, or sweet-spot acceptance. Legacy controls excluded.')
 with (B/f'PAIRED_COSTS_RECEIPT_{a.tag}.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps([r for r in records if r['metric']=='system_time_T_s']))
if __name__=='__main__':main()
