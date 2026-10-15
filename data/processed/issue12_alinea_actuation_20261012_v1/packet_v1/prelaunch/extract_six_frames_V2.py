"""Six existing Y5 frames only: Y2 same-state arithmetic, not native Y2."""
from pathlib import Path
import json,hashlib,gzip,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[5];O=Path(__file__).resolve().parent
RAW=R/'data/raw/issue12_alinea_actuation_20261012_v1/CA_I12_QUOTA_R300_S17_FIX01/outputs'
ENG=R/'artifacts/issue12_alinea_actuation_20261012_v1/runs/CA_I12_QUOTA_R300_S17_FIX01/engineering'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ENG/'RAW_FINAL_SHA256_V1.json').read_text())['files']
inputs=['fcd.xml.gz','pre_steps.jsonl','post_steps.jsonl','yellow_scope.jsonl','tls_states.xml']
assert all(sha(RAW/n)==manifest[str((RAW/n).relative_to(R))] for n in inputs)
closes=(1204,1228,1252);acks={v for t in closes for v in (t,t+1)}
pre={};post={};entries={}
for s in (RAW/'pre_steps.jsonl').open():
 q=json.loads(s)
 if q['time_s'] in acks:pre[q['time_s']]=q['bound_snapshot']
for s in (RAW/'post_steps.jsonl').open():
 q=json.loads(s)
 if q['time_end_s'] in acks:post[q['time_end_s']]=q
 for e in q['actual_crossings']:entries[e['vehicle_id']]=e
fcd={}
with gzip.open(RAW/'fcd.xml.gz','rb') as f:
 for _,e in ET.iterparse(f,events=('end',)):
  if e.tag=='timestep':
   ack=int(float(e.get('time')))+1
   if ack in acks:fcd[ack]={v.get('id'):v.attrib.copy() for v in e}
   e.clear()
assert set(fcd)==acks
tls={int(float(q.get('time')))+1:q.attrib for q in ET.parse(RAW/'tls_states.xml').getroot() if q.get('id')=='ramp_mid'}
for t in closes:
 assert post[t]['motion']==tls[t]['state']=='G' and post[t+1]['motion']==tls[t+1]['state']=='y'
 assert tls[t]['programID']==tls[t+1]['programID']=='I12_QUOTA24'
ys=[json.loads(s) for s in (RAW/'yellow_scope.jsonl').open()]
tables=[];body=[]
for screen,t in zip(ys,closes):
 assert screen['time_s']==t and screen['covered_ids']==sorted(q['vehicle_id'] for q in screen['rows'])
 world=pre[t]['world'];meta=pre[t]['terminal_before']
 assert set(fcd[t])==set(world)==set(post[t]['post_world'])
 expected={vid for vid,w in world.items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')}
 assert set(screen['covered_ids'])==expected
 rows=[]
 for q in screen['rows']:
  vid=q['vehicle_id'];offset=113.08 if q['population']=='ingress' else 0
  assert abs(q['position_m']-(float(fcd[t][vid]['pos'])-offset))<.51e-8
  assert abs(q['speed_m_s']-float(fcd[t][vid]['speed']))<.51e-8
  assert q['length_m']==meta[vid]['length_m'] and q['normal_decel_m_s2']==4.5 and q['action_step_s']==1
  v=q['speed_m_s'];d=204.49-q['position_m'];b=q['normal_decel_m_s2'];L=q['length_m']
  stop=d>0 and (v<=b or d>=v+v*v/(2*b))
  timing=None if v==0 else 1+v/(2*b)+L/v
  clear=v>0 and timing<=2 and d+L<=v*(2-1)
  rows.append(dict(vehicle_id=vid,population=q['population'],ACK_time_s=t,position_m=q['position_m'],speed_m_s=v,length_m=L,distance_m=d,stop_possible=stop,Y2_body_clear_screen_s=timing,clear_possible=clear,status='PASS_SAME_STATE_Y2_SCREEN' if stop or clear else 'UNKNOWN_Y2_SCREEN'))
 assert all(q['status']=='PASS_SAME_STATE_Y2_SCREEN' for q in rows)
 tables.append(dict(Gclose_ACK=t,approaching_count=len(rows),all_same_state_Y2_PASS=True,rows=rows))
 # Independent line-spanning body inventory: head crossed into internal, tail<0.
 spanning=[]
 for vid,w in world.items():
  if w['lane_id']!=':ramp_mid_0_0':continue
  m=meta[vid];pos=float(fcd[t][vid]['pos']);L=m['length_m']
  assert m['type_id']=='technical_passenger' and m['route']==['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down']
  if pos>=L:continue
  assert vid in entries and entries[vid]['motion_signal_state']=='G' and entries[vid]['crossing_time_upper_s']<=t
  next_meta=pre[t+1]['terminal_before'][vid];next_fcd=fcd[t+1][vid]
  assert next_fcd['lane']==next_meta['lane_id']==':ramp_mid_0_0'
  next_rear=float(next_fcd['pos'])-next_meta['length_m']
  spanning.append(dict(vehicle_id=vid,Gclose_ACK=t,entry_interval_s=[entries[vid]['crossing_time_lower_s'],entries[vid]['crossing_time_upper_s']],entry_motion='G',lane_id=w['lane_id'],position_m=pos,length_m=L,speed_m_s=float(fcd[t][vid]['speed']),rear_to_line_m=pos-L,existing_first_Y5_ACK=t+1,existing_first_Y5_position_m=float(next_fcd['pos']),existing_first_Y5_speed_m_s=float(next_fcd['speed']),existing_first_Y5_rear_to_line_m=next_rear,body_cleared_by_first_existing_Y5_ACK=next_rear>=0,front_new_crossing_under_y=False))
 assert set(spanning[i]['vehicle_id'] for i in range(len(spanning)))=={vid for vid,w in world.items() if w['lane_id']==':ramp_mid_0_0' and float(fcd[t][vid]['pos'])<meta[vid]['length_m']}
 body.extend(spanning)
result={'classification':'SIX_EXISTING_Y5_FRAMES_SAME_STATE_Y2_ARITHMETIC_ONLY','current_native_Y2_executions':0,'frames_ACK':sorted(acks),'approaching_tables':tables,'spanning_bodies':body,'new_Y2_future_clearance_proven':False,'invented_bodyclear_deadline_added':False,'input_SHA256':{str((RAW/n).relative_to(R)):sha(RAW/n) for n in inputs}}
(O/'SIX_FRAME_RESULTS_V1.json').write_text(json.dumps(result,indent=2)+'\n')
print('approaching',[(t['Gclose_ACK'],t['approaching_count'],t['all_same_state_Y2_PASS']) for t in tables]);print(json.dumps(body,indent=2))
