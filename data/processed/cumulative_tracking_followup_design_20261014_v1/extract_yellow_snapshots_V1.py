"""Existing snapshots only. Y3 reevaluation is not a counterfactual simulation."""
import json,csv,pathlib,hashlib,math
from fractions import Fraction
ROOT=pathlib.Path.cwd();OUT=ROOT/'data/processed/cumulative_tracking_followup_design_20261014_v1'
RAW=ROOT/'data/raw/cumulative_tracking_implementation_20261014_v1/UA_CUMULATIVE750_S17_01/outputs'
ACT=ROOT/'data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1/ACTUAL_RESULTS_V1.json'
def load(p):return json.loads(p.read_text())
def lines(p):return [json.loads(x) for x in p.read_text().splitlines()]
def write(n,d):
 with (OUT/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
a=load(ACT);attempts=lines(RAW/'yellow_scope_attempts.jsonl');requests=lines(RAW/'policy_phase_requests.jsonl');cycles=a['accounting']['cycles'];phases=a['phase_audit']['cycles'];rows=[];summary=[]
for s in attempts:
 t=s['time_s']; c=next(c for c in cycles if c['begin_s']<t<=c['end_s']); ph=next(p for p in phases if p['begin_s']==c['begin_s']);ids=[x['vehicle_id'] for x in s['rows']]
 assert len(ids)==len(set(ids)) and set(ids)==set(s['covered_ids']) and all(x['time_s']==t for x in s['rows'])
 originalfail=[];newfail=[];paths={'stop_only':0,'clear_only':0,'both':0,'neither':0}
 for x in s['rows']:
  v=x['speed_m_s'];dt=x['action_step_s'];b=x['normal_decel_m_s2'];l=x['length_m'];d=x['distance_to_meter_m']
  assert all(math.isfinite(z) for z in (v,dt,b,l,d)) and b>0 and dt>0 and l>0 and v>=0
  stop=d>0 and (v<=b*dt or d>=v*dt+v*v/(2*b))
  tc=dt+v/(2*b)+l/v if v>0 else None
  def clear(y):return v>0 and tc<=y and d+l<=v*(y-dt)
  oldclear=clear(s['yellow_s']);newclear=clear(3)
  assert stop==x['stop_possible'] and oldclear==x['clear_possible']
  k='both' if stop and oldclear else 'stop_only' if stop else 'clear_only' if oldclear else 'neither';paths[k]+=1
  if not(stop or oldclear):originalfail.append(x['vehicle_id'])
  if not(stop or newclear):newfail.append(x['vehicle_id'])
  rows.append(dict(attempt_time_s=t,vehicle_id=x['vehicle_id'],population=x['population'],position_m=x['position_m'],speed_m_s=v,length_m=l,decel_m_s2=b,dt_s=dt,distance_m=d,original_Y_s=s['yellow_s'],stop_screen_pass=stop,original_clear_pass=oldclear,same_snapshot_Y3_clear_pass=newclear,same_snapshot_Y3_pass=stop or newclear,clear_time_s=tc))
 close=[q for q in requests if q['time_s']==t and any(i['method']=='setPhase' and i['value']==1 for i in q['requests'])]
 gend='QUOTA_SET_PHASE_1' if close else 'MAX_GREEN_DEADLINE_PREPARATION' if t-c['begin_s']==c['max_green_s'] else 'UNRESOLVED'
 summary.append(dict(time_s=t,cycle_begin_s=c['begin_s'],period_s=c['period_s'],original_Y_s=s['yellow_s'],G_elapsed_s=t-c['begin_s'],G_end_record_evidence=gend,cycle_N_actual=c['N'],cycle_completed=c['completed'],phase_exposure_s=c['phase_exposure_s'],first_Y_motion_observed=ph['green_end_s'] is not None,attempt_stage=s['attempt_stage'],covered_vehicles=len(ids),paths_original=paths,original_failed_ids=originalfail,same_snapshot_Y3_failed_ids=newfail,same_snapshot_Y3_all_pass=not newfail))
with (OUT/'ALL_BOUND_VEHICLE_SCREENS_V1.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('ALL_ATTEMPTS_V1.json',{'classification':'EXISTING_STATE_REEVALUATION_NOT_COUNTERFACTUAL_SIMULATION','attempt_count':len(summary),'vehicle_snapshots':len(rows),'attempts':summary,'original_runtime_STOP_preserved':a['runtime_error'],'unobserved_after1272':{'N':None,'yellow_or_red_behavior':None},'new_native_results':None})
# Nominal two-car packets only; no actual discharge guarantee.
maths={'T9_nominal_veh_h':str(Fraction(7200,9)),'T10_nominal_veh_h':str(Fraction(7200,10)),'two_packet_catalogue_nominal_range':[720,800],'750_mixture':{'T9_packets':2,'T10_packets':3,'time_s':48,'nominal_cars':10,'rate_veh_h':750},'900_unreachable_with_T9_T10_two_car_only':True,'below720_unreachable_with_full_contiguous_T9_T10_two_car_only':True,'300_two_car_period_required_s':str(Fraction(7200,300)),'900_two_car_period_required_s':str(Fraction(7200,900)),'example750_sequence':[10,9,10,9,10],'example_completed_boundary_errors_C_minus_E':[str(Fraction(750*sum([10,9,10,9,10][:i]),3600)-2*i) for i in range(1,6)],'assumptions':'Contiguous complete packets, N=2 assumed for nominal arithmetic only; future demand held at750. No actual policy validation.'}
write('NOMINAL_CATALOGUE_ARITHMETIC_V1.json',maths)
print(json.dumps({'attempts':len(summary),'rows':len(rows),'summary':summary,'arithmetic':maths},indent=2))
