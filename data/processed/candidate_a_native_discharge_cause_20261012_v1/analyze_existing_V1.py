"""Minimum existing two-run discharge trajectory analysis; raw files read-only."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,json,math,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent
WT=Path('/Users/yuhongzhang/.codex/worktrees/native-receiver-wait/Masterarbeit-Ramp-Metering')
RUNS=[('300','candidate_a_native_receiver_wait_20261012_v1','CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2','990386cf6d40d70b5f59d6754cde56555e7e7021f0910a8918373b19afb94199'),('360','candidate_a_native_wait_budget_series_20261012_v1','CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01','61aae130fa1d8dffaad693290d700da39eea7937641716a800aef7ab10a0d9b0')]
STORAGE='ramp_storage_0';INTERNAL=':ramp_mid_0_0';LENGTH=204.49

def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def lines(p):
 with p.open()as f:return[json.loads(s)for s in f if s.strip()]
def close(a,b):assert abs(a-b)<=.005001,(a,b)
def analyze(label,namespace,run,msha):
 manifest_path=WT/'artifacts'/namespace/'runs'/run/'engineering/RAW_FINAL_SHA256_V1.json';assert sha(manifest_path)==msha;manifest=load(manifest_path);selected={}
 for filename in ['pre_steps.jsonl','post_steps.jsonl','fcd.xml.gz','tls_states.xml','step_ack.jsonl']:
  names=[name for name in manifest['files'] if name.endswith('/outputs/'+filename)];assert len(names)==1;name=names[0];item=manifest['files'][name];expected=item['sha256']if isinstance(item,dict)else item;p=WT/name;assert sha(p)==expected;selected[filename]=p
 root=selected['pre_steps.jsonl'].parent;pre=lines(selected['pre_steps.jsonl']);post=lines(selected['post_steps.jsonl']);ack=lines(selected['step_ack.jsonl']);assert len(pre)==len(post)==1272
 verified=[r for r in ack if r.get('actual_time_verified')is True];assert [r['actual_readback_s']for r in verified]==list(range(1,1273))
 front_ids=[]
 for begin in [1200,1224,1248]:
  vehicles=sorted([v for v in pre[begin]['bound_snapshot']['vehicle_states']if v['population']=='storage'],key=lambda v:v['position_m'],reverse=True);assert len(vehicles)>=2;front_ids.append((vehicles[0]['vehicle_id'],vehicles[1]['vehicle_id']))
 wanted={vid for pair in front_ids for vid in pair};fcd={}
 with gzip.open(selected['fcd.xml.gz'],'rb')as f:
  for _,e in ET.iterparse(f,events=('end',)):
   if e.tag=='timestep':
    t=int(float(e.get('time')))
    if 1199<=t<=1271:fcd[t]={v.get('id'):{'lane_id':v.get('lane'),'position_m':float(v.get('pos')),'speed_m_s':float(v.get('speed'))}for v in e.findall('vehicle')if v.get('id')in wanted}
    e.clear()
 tls={}
 for _,e in ET.iterparse(selected['tls_states.xml'],events=('end',)):
  if e.tag=='tlsState'and e.get('id')=='ramp_mid':
   t=int(float(e.get('time')))
   if 1200<=t<=1271:assert t not in tls;tls[t]={'state':e.get('state'),'phase':int(e.get('phase')),'program':e.get('programID')}
   e.clear()
 assert set(tls)==set(range(1200,1272)) and Counter(v['state']for v in tls.values())=={'G':9,'y':9,'r':54}
 crossing=[c for r in post[1200:]for c in r['actual_crossings']];assert len(crossing)==3
 assert crossing==[{'vehicle_id':pair[0],'crossing_time_lower_s':1200+k*24,'crossing_time_upper_s':1201+k*24,'time_interval':'(lower,upper]','cycle_id':k,'motion_signal_state':'G'}for k,pair in enumerate(front_ids)]
 for t in range(1200,1272):
  r=post[t];p=pre[t]['bound_snapshot'];assert r['time_begin_s']==t and r['time_end_s']==t+1 and r['motion']==tls[t]['state']==('G'if(t-1200)%24<3 else'y'if(t-1200)%24<6 else'r')
  before=fcd[t-1];after=fcd[t];entrants={vid for vid,v in after.items()if v['lane_id']==INTERNAL and (vid not in before or before[vid]['lane_id']!=INTERNAL)};assert entrants=={c['vehicle_id']for c in r['actual_crossings']}
  assert all(vid in before and before[vid]['lane_id']==STORAGE for vid in entrants)
 trajectories=[];summaries=[]
 def at(vid,time):
  world=pre[time]['bound_snapshot']['world']if time<1272 else post[-1]['post_world'];w=world[vid];native=fcd[time-1][vid];assert w['lane_id']==native['lane_id'];close(w['speed_m_s'],native['speed_m_s']);position=native['position_m'];source='FCD_precision2'
  if time<1272:
   v=next((v for v in pre[time]['bound_snapshot']['vehicle_states']if v['vehicle_id']==vid and v['population']=='storage'),None)
   if v:position=v['position_m'];source='unrounded_pre_observation_same_actual_time';close(position,native['position_m'])
  if source=='FCD_precision2':
   entered=next((v for v in post[time-1]['actual_entry_following']if v['vehicle_id']==vid),None)
   if entered:position=entered['after']['lane_position_m'];source='unrounded_actual_entry_after';close(position,native['position_m'])
  return{'lane_id':w['lane_id'],'position_m':position,'position_source':source,'speed_m_s':w['speed_m_s'],'stopline_distance_m':LENGTH-position if w['lane_id']==STORAGE else -position if w['lane_id']==INTERNAL else None}
 for k,(first,second)in enumerate(front_ids):
  start=1200+k*24;finish=start+24;begin=pre[start]['bound_snapshot'];states={v['vehicle_id']:v for v in begin['vehicle_states']};first0,second0=at(first,start),at(second,start);endgreen=at(second,start+3);first3=at(first,start+3);endyellow=at(second,start+6);redend=at(second,finish)
  leadercheck=pre[start+3]['bound_snapshot']['entry_following_before'][second];receiver=pre[start+3]['bound_snapshot']['receiver'];first_y=post[start+3]['post_receiver']
  second_events=[c for c in crossing if c['vehicle_id']==second];event=second_events[0]if second_events else None
  for offset in range(25):
   time=start+offset
   for role,vid in [('first',first),('second',second)]:
    v=at(vid,time);q=pre[time]['bound_snapshot'].get('entry_following_before',{}).get(vid)if time<1272 else None
    trajectories.append({'budget_label':label,'run_id':run,'cycle_id':k,'role_at_cycle_start':role,'vehicle_id':vid,'actual_snapshot_time_s':time,'offset_s':offset,'preceding_interval_motion':post[time-1]['motion'],'next_interval_motion':pre[time]['bound_snapshot']['motion']if time<1272 else None,**v,'current_leader_id':q.get('leader_id')if q else None,'current_gap_excluding_minGap_m':q.get('gap_excluding_minGap_m')if q else None,'current_secure_gap_m':q.get('actual_secure_gap_m')if q else None,'following_observation_status':q.get('status')if q else None})
  summary={'budget_label':label,'run_id':run,'cycle_id':k,'green_begin_s':start,'first_id':first,'second_id':second,'first_initial_position_m':first0['position_m'],'first_initial_stopline_distance_m':first0['stopline_distance_m'],'first_initial_speed_m_s':first0['speed_m_s'],'second_initial_position_m':second0['position_m'],'second_initial_stopline_distance_m':second0['stopline_distance_m'],'second_initial_speed_m_s':second0['speed_m_s'],'initial_front_to_front_gap_m':first0['position_m']-second0['position_m'],'initial_bumper_gap_m':first0['position_m']-second0['position_m']-states[first]['length_m'],'second_speed_after_G1_m_s':at(second,start+1)['speed_m_s'],'second_speed_after_G2_m_s':at(second,start+2)['speed_m_s'],'second_speed_after_G3_m_s':endgreen['speed_m_s'],'second_green_end_position_m':endgreen['position_m'],'second_green_end_stopline_distance_m':endgreen['stopline_distance_m'],'second_green_total_advance_m':endgreen['position_m']-second0['position_m'],'leader_green_end_lane':first3['lane_id'],'leader_green_end_position_rounded_m':first3['position_m'],'leader_green_end_speed_m_s':first3['speed_m_s'],'leader_green_end_rear_clearance_m':receiver['nearest_internal_rear_clearance_m'],'required_front_clearance_m':receiver['required_front_clearance_m'],'green_end_prospective_receiver_available':receiver['available'],'green_end_current_gap_m':leadercheck['gap_excluding_minGap_m'],'green_end_actual_secure_gap_m':leadercheck['actual_secure_gap_m'],'green_end_following_status':leadercheck['status'],'receiver_available_after_first_yellow_second':first_y['available'],'second_yellow_end_position_m':endyellow['position_m'],'second_yellow_end_stopline_distance_m':endyellow['stopline_distance_m'],'second_yellow_end_speed_m_s':endyellow['speed_m_s'],'second_cycle_red_end_position_m':redend['position_m'],'second_cycle_red_end_speed_m_s':redend['speed_m_s'],'second_next_crossing_lower_s':event['crossing_time_lower_s']if event else None,'second_next_crossing_upper_s':event['crossing_time_upper_s']if event else None,'second_crossing_observation':'NEXT_CYCLE_OBSERVED'if event else'NOT_OBSERVED_BY_1272','actual_N_this_cycle':1,'nominal_E_this_cycle':2}
  assert second0['speed_m_s']==0 and at(second,start+1)['speed_m_s']==0 and endgreen['stopline_distance_m']>0 and not receiver['available']and first_y['available']and leadercheck['status']=='CURRENT_GAP_OBSERVED_WITHIN_BOUND'
  summaries.append(summary)
 mapping={'label':label,'run_id':run,'manifest_path':str(manifest_path),'manifest_sha256':msha,'relevant_inputs':[{'path':str(p),'sha256':sha(p)}for p in selected.values()],'crossings':crossing,'C':post[-1]['accounting']['C'],'C_applied':post[-1]['accounting']['C_applied'],'E':post[-1]['accounting']['E'],'N':post[-1]['accounting']['N'],'selected_trajectory_times':'1200..1272 snapshots; FCD label=actual_time−1; G/y/r intervals1200..1271'}
 return summaries,trajectories,mapping

def main():
 s=[];t=[];m=[]
 for case in RUNS:
  a,b,c=analyze(*case);s+=a;t+=b;m.append(c)
 def normalized(row):return{k:v for k,v in row.items()if k not in ['budget_label','run_id']}
 assert [normalized(r)for r in s[:3]]==[normalized(r)for r in s[3:]]
 assert [normalized(r)for r in t[:150]]==[normalized(r)for r in t[150:]]
 assert len(s)==6 and len(t)==300
 for name,rows in [('SIX_CYCLE_SUMMARY_V1.csv',s),('SELECTED_TRAJECTORIES_V1.csv',t)]:
  with(OUT/name).open('x',newline='')as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for name,data in [('SIX_CYCLE_SUMMARY_V1.json',s),('SELECTED_TRAJECTORIES_V1.json',t),('SOURCE_MAPPING_V1.json',{'runs':m,'selected_exact_trajectory_equal_between_runs':True,'observations_not_independent_stochastic_replicates':True,'no_new_simulation':True,'native_unlogged_decision_fields':['getStopSpeed','native final following/planned-speed constraints','effective carFollowModel ID','unique yellow branch cause'],'input_filter':'two latest manifests; only five related output files perrun; no oldfullaudit'})]:
  with(OUT/name).open('x')as f:json.dump(data,f,indent=2,allow_nan=False)
 print(json.dumps({'status':'PASS_MINIMUM_SIX_CYCLE_TRAJECTORY_BINDING','cycles':len(s),'trajectory_rows':len(t),'exact_selected_equality':True,'second_green_end_remaining_m':[r['second_green_end_stopline_distance_m']for r in s[:3]],'second_green_end_speed_m_s':[r['second_speed_after_G3_m_s']for r in s[:3]],'N_per_cycle':[r['actual_N_this_cycle']for r in s]},indent=2))
if __name__=='__main__':main()
