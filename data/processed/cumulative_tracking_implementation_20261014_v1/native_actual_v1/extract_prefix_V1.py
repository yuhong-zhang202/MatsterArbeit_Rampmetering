"""Bounded post-audit extraction; raw remains read-only. No simulation or tests."""
import csv,gzip,hashlib,json,pathlib,xml.etree.ElementTree as ET
from fractions import Fraction
ROOT=pathlib.Path.cwd(); OUT=ROOT/'data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1'
RAW=ROOT/'data/raw/cumulative_tracking_implementation_20261014_v1/UA_CUMULATIVE750_S17_01/outputs'
ENG=ROOT/'artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1'
def load(p): return json.loads(p.read_text())
def write(n,d):
 p=OUT/n
 with p.open('x') as f: json.dump(d,f,indent=2);f.write('\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
d=load(OUT/'ACTUAL_RESULTS_V1.json'); scope=load(RAW/'failure_snapshot.json')['last_yellow_scope']; row=next(x for x in scope['rows'] if x['vehicle_id']=='R_flow.15')
frame=None
with gzip.open(RAW/'fcd.xml.gz','rb') as f:
 for _,e in ET.iterparse(f,events=['end']):
  if e.tag=='timestep':
   if float(e.attrib['time'])==1271: frame=next(v.attrib.copy() for v in e if v.attrib.get('id')=='R_flow.15')
   e.clear()
assert frame is not None
assert abs(float(frame['pos'])-row['position_m'])<=5.1e-9 and abs(float(frame['speed'])-row['speed_m_s'])<=5.1e-9
v=row['speed_m_s'];b=row['normal_decel_m_s2'];dt=row['action_step_s'];length=row['length_m'];dist=204.49-row['position_m'];yellow=scope['yellow_s']
stopdist=v*dt+v*v/(2*b);cleart=dt+v/(2*b)+length/v
stop=dist>0 and (v<=b*dt or dist>=stopdist)
clear=v>0 and cleart<=yellow and dist+length<=v*(yellow-dt)
assert not stop and not clear and row['stop_possible']==stop and row['clear_possible']==clear
with (RAW/'post_steps.jsonl').open('rb') as f:
 f.seek(max(0,(RAW/'post_steps.jsonl').stat().st_size-400000));last= json.loads(f.read().splitlines()[-1])
assert last['time_end_s']==1272 and last['motion']=='G' and last['phase_observation']['state_after']=='G'
tls=[e.attrib for e in ET.parse(RAW/'tls_states.xml').getroot() if e.attrib.get('id')=='ramp_mid']
assert tls[-1]['time']=='1271.000' and tls[-1]['phase']=='0' and tls[-1]['state']=='G'
cycles=d['accounting']['cycles']; first=cycles[:5]
assert all(x['completed'] for x in first) and sum(x['N'] for x in first)==10 and sum(x['E'] for x in first)==10 and first[-1]['end_s']==1248
with (OUT/'OBSERVED_CYCLES_V1.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['begin_s','planned_end_s','T','completed','N','N_G','N_y_observed','N_r_observed','E_complete_only','G_s','y_s','r_s']);w.writeheader()
 for x in cycles:
  ex=x['phase_exposure_s'];w.writerow(dict(begin_s=x['begin_s'],planned_end_s=x['end_s'],T=x['period_s'],completed=x['completed'],N=x['N'],N_G=x['N_G'],N_y_observed=x['N_y'] if ex['y'] else None,N_r_observed=x['N_r'] if ex['r'] else None,E_complete_only=x['E'],G_s=ex['G'],y_s=ex['y'],r_s=ex['r']))
write('PREFIX_AND_SCREEN_READBACK_V1.json',{'status':'GO_FOR_OBSERVED_PREFIX_EVIDENCE_DELIVERY_ONLY','reader_exit':1,'reader_status':d['status'],'runtime_stop':d['runtime_error'],'first_48s':{'C_exact':str(Fraction(750*48,3600)),'E':10,'N':10,'complete_packets':5,'periods':[x['period_s'] for x in first]},'whole_72s':d['accounting']['accounting'],'complete_packets':7,'partial_packets':1,'end1296_observed':False,'first_successful_T8':cycles[2],'last_partial_T8':cycles[-1],'R15':{'raw_scope':row,'FCD_BEGIN1271':frame,'ACK':1272,'yellow_s':yellow,'independent_stop_screen_m':stopdist,'independent_clear_time_s':cleart,'stop_possible':stop,'clear_possible':clear,'last_TLS':tls[-1],'last_post_phase':last['phase_observation'],'first_Y_motion_executed':False},'coverage':{'independent_entries':len(d['independent_actual_entries']),'body_censored_ids':d['body_censored_ids'],'normal_arrivals':len(d['terminal_results']),'all_normal_arrivals_PASS':all(x['status']=='PASS' for x in d['terminal_results']),'missing_or_unknown':d['missing_or_unknown'],'observed_post_motion_alarms':d['observed_alarms'],'log_EOF_verified':d['log_EOF_verified'],'terminal_AFTER_pools_independent':False},'unobserved_after1272':{'N':None,'E':None,'C_observed':None},'native_safety_proven':False,'rate_qualified':False})
binder=load(ENG/'ENGINEERING_DELIVERY_BINDING_V1.json')
checks={}
for rel,item in binder['files'].items():
 p=ROOT/rel;checks[rel]={'sha256':sha(p),'bytes':p.stat().st_size,'match':sha(p)==item['sha256'] and p.stat().st_size==item['bytes']}
assert all(x['match'] for x in checks.values())
write('ACTUAL_AUDIT_COMMAND_RECEIPT_V1.json',{'command':'.venv/bin/python -B scripts/cumulative_tracking_audit_20261014_v1/actual.py --manifest artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1/RAW_FINAL_SHA256_V1.json --card artifacts/cumulative_tracking_implementation_20261014_v1/engineering/packages_v5/UA_CUMULATIVE750_S17_01/card.json --output data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1','session_id':30763,'actual_exit_code':1,'attempt_count':1,'elapsed_s':None,'reader_sha256':sha(ROOT/'scripts/cumulative_tracking_audit_20261014_v1/actual.py'),'result_sha256':sha(OUT/'ACTUAL_RESULTS_V1.json'),'engineering_binder_checks':checks,'raw_sha_verification':'161 files verified by single actual reader; not repeated by this extraction','no_SUMO_or_source_changes':True})
print('BOUNDED_EXTRACTION_PASS',stopdist,cleart)
