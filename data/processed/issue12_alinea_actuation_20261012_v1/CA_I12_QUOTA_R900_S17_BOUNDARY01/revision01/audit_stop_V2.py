"""Run-specific frozen first R300 prefix audit; immutable raw, no native code."""
from pathlib import Path
import json,hashlib,gzip,xml.etree.ElementTree as ET,sys,collections
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'data/processed/issue12_alinea_actuation_20261012_v1'))
from audit_data_V3 import audit_rate_steps,audit_terminal
ENG=ROOT/'artifacts/issue12_alinea_actuation_20261012_v1/runs/CA_I12_QUOTA_R900_S17_BOUNDARY01/engineering'
RAW=ROOT/'data/raw/issue12_alinea_actuation_20261012_v1/CA_I12_QUOTA_R900_S17_BOUNDARY01/outputs'
def load(n):return json.loads((RAW/n).read_text())
def lines(n):return [json.loads(s) for s in (RAW/n).open()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise ValueError(msg)
m=json.loads((ENG/'RAW_FINAL_SHA256_V1.json').read_text());need(len(m['files'])==79,'manifest schema')
need(all(sha(ROOT/n)==h for n,h in m['files'].items()),'raw hash mismatch')
pre=lines('pre_steps.jsonl');post_raw=lines('post_steps.jsonl');post=[]
for row in post_raw:
 if 'retained_receipts' not in row:post.append(row);continue
 need(row is post_raw[-1] and row['last_completed_s']==row['last_accounted_s']==1206,'failure wrapper terminal binding')
 retained=row['retained_receipts'];need(len(retained)==1 and len(post)==1205 and retained[0]['time_begin_s']==1205 and retained[0]['time_end_s']==1206,'retained terminal step exact binding')
 post.extend(retained)
ack=lines('step_ack.jsonl');logs=lines('log_intervals.jsonl')
need(len(pre)==len(post)==1206 and len(ack)==2412,'prefix lengths')
tls={int(float(q.get('time'))):q.attrib for q in ET.parse(RAW/'tls_states.xml').getroot() if q.get('id')=='ramp_mid'}
stop_gap={};entries=[];arrivals=[];brake_min=0.;accel_min=0.;event_max=0;wait_count=0;supplied=0;min_gap_margin=None
lanes={};card=load('card.json');cfg=ET.parse(ROOT/card['package']/'scenario.sumocfg').getroot()
net=Path(cfg.find('./input/net-file').get('value'))
if not net.is_absolute():net=ROOT/card['package']/net
for edge in ET.parse(net).getroot().findall('edge'):lanes[edge.get('id')]=[v.get('id') for v in edge.findall('lane')]
trips=[v.attrib for v in ET.parse(RAW/'tripinfo.xml').getroot().findall('tripinfo')]
trip_by=collections.defaultdict(list)
for v in trips:trip_by[v['id']].append(v)
arrival_results=[]
def following(q,vid,t,world):
 need(isinstance(q,dict) and q.get('vehicle_id')==vid and q.get('time_s')==t,'entry following identity/time')
 need(q.get('speed_mode')==31 and q.get('lane_change_mode')==1621 and abs(q['actual_speed_m_s']-world[vid]['speed_m_s'])<1e-8,'entry mode/speed')
 need(q.get('status') in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','CLEAR_WITHIN_OBSERVED_LOOKAHEAD'),'entry current-gap denied or unknown')
 need(q['route']==['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'] and q['lookahead_m']==478.67 and q['future_safety_proven'] is False,'following bound scope')
 if q['status']=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD':
  need(q['fresh_getLeader_result'] is None or q['fresh_getLeader_result']==['',-1],'bounded clear empty result')
 if q['status']=='CURRENT_GAP_OBSERVED_WITHIN_BOUND':
  need(q['getSecureGap_args']['vehID']==vid and abs(q['getSecureGap_args']['speed']-q['actual_speed_m_s'])<1e-8,'query speed binding')
  need(q['gap_excluding_minGap_m']+1e-8>=q['actual_secure_gap_m']+1.1,'current-gap threshold')
for i,(b,r) in enumerate(zip(pre,post)):
 need(b['time_s']==i and r['time_begin_s']==i and r['time_end_s']==i+1 and r['accounting_complete'] is True,'ACK-time coverage')
 a0,a1=ack[2*i:2*i+2];need(a0['requested_target_s']==i+1 and a0['ACK_received'] is True and a1['actual_time_verified'] is True and a1['actual_readback_s']==i+1,'ACK journal')
 w=b['bound_snapshot']['world'];z=r['post_world'];ic=r['identity_change']
 need(set(w)-set(z)==set(ic['arrived_ids'])==set(ic['before_only_ids']),'arrived coverage')
 need(set(z)-set(w)==set(ic['after_only_ids']) and set(ic['after_only_ids'])<=set(ic['departed_ids']),'departure coverage')
 pending=r['terminal_arrival_pending'];need({q['vehicle_id'] for q in pending}==set(ic['arrived_ids']) and len(pending)==len(ic['arrived_ids']),'terminal metadata coverage')
 for q in pending:
  need(q==dict(b['bound_snapshot']['terminal_before'][q['vehicle_id']],time_begin_s=i,time_end_s=i+1,arrived_id_bound=True,status='PENDING_FINAL_TRIPINFO_LAST_MOVEMENT_AUDIT_NOT_ONLINE_COVERED'),'terminal before exact join')
  result=audit_terminal(q,trip_by[q['vehicle_id']],lanes);arrival_results.append(result);arrivals.append(q['vehicle_id'])
  need(result['status']=='PASS','terminal last-movement '+str(result))
 for vid in set(w)&set(z):
  dv=z[vid]['speed_m_s']-w[vid]['speed_m_s'];brake_min=min(brake_min,dv)
  need(abs(dv-r['braking_observation']['speed_difference_m_s2'][vid])<1e-8 and dv>=-4.5-1e-6,'normal brake difference')
 need(set(r['braking_observation']['speed_difference_ids'])==set(w)&set(z),'braking intersection coverage')
 need(set(r['braking_observation']['after_acceleration_ids'])==set(z),'post acceleration coverage')
 for a in r['braking_observation']['actual_acceleration_m_s2'].values():accel_min=min(accel_min,a);need(a>=-4.5-1e-6,'native acceleration')
 event_max=max(event_max,*r['native_event_counters'].values());need(not any(r['native_event_counters'].values()),'native counter')
 need(int(tls[i]['phase'])==r['phase_observation']['phase_after'] and tls[i]['state']==r['motion'],'motion TLS journal')
 if i>=1200:supplied+=bool(b['bound_snapshot']['storage'])
 for d,t,world in [(b['bound_snapshot'].get('native_receiver_decision'),i,w),(r.get('post_native_receiver_decision'),i+1,z)]:
  if d and d['decision']=='WAIT_NATIVE_FOLLOWING':following(d['current_following'],d['current_following']['vehicle_id'],t,world);wait_count+=1
  if d and d['decision']=='STOP_CURRENT_GAP_BOUND_DENIED':
   need(i==1205 and t==1206 and r['status']=='STOP_OBSERVED_AFTER_STEP' and r['reasons']==['POST_CURRENT_GAP_BOUND_DENIED'],'unbound rejected frame or missing STOP')
   q=d['current_following'];vid=q['vehicle_id'];leader=q['leader_id']
   need(q['status']=='STOP_CURRENT_GAP_BOUND_DENIED' and q['time_s']==t and vid=='R_flow.2' and leader=='R_flow.1' and q['speed_mode']==31 and q['lane_change_mode']==1621 and q['leader_speed_mode']==31 and q['leader_lane_change_mode']==1621,'STOP identity/mode/time')
   need(q['actual_speed_m_s']==world[vid]['speed_m_s'] and q['leader_speed_m_s']==world[leader]['speed_m_s'] and q['lane_id']==world[vid]['lane_id'] and q['leader_lane_id']==world[leader]['lane_id'],'STOP same world binding')
   need(q['getSecureGap_args']=={'vehID':vid,'speed':q['actual_speed_m_s'],'leaderSpeed':q['leader_speed_m_s'],'leaderMaxDecel':9.0,'leaderID':leader} and q['fresh_getLeader_result']==[leader,q['gap_excluding_minGap_m']],'STOP fresh primitive query binding')
   need(abs(q['physical_bumper_gap_m']-(q['gap_excluding_minGap_m']+q['min_gap_m']))<1e-8 and q['margin_m']==1.1 and abs(q['required_with_margin_m']-(q['actual_secure_gap_m']+1.1))<1e-8 and q['gap_excluding_minGap_m']<q['required_with_margin_m'],'STOP gap arithmetic')
   stop_gap=dict(q,post_time_s=t,excess_over_secure_without_project_margin_m=q['gap_excluding_minGap_m']-q['actual_secure_gap_m'],project_margin_deficit_m=q['required_with_margin_m']-q['gap_excluding_minGap_m'])
 for q in r['actual_entry_following']:
  following(q['before'],q['vehicle_id'],i,w);following(q['after'],q['vehicle_id'],i+1,z)
# FCD timestamp labels interval BEGIN while vehicle tuple is post-movement ACK.
with gzip.open(RAW/'fcd.xml.gz','rb') as f:
 frames=0
 for _,elem in ET.iterparse(f,events=('end',)):
  if elem.tag!='timestep':continue
  i=int(float(elem.get('time')));r=post[i];frame={v.get('id'):v.attrib for v in elem}
  need(set(frame)==set(r['post_world']),'FCD identity coverage')
  for vid,v in frame.items():
   need(v['lane']==r['post_world'][vid]['lane_id'] and abs(float(v['speed'])-r['post_world'][vid]['speed_m_s'])<=0.5e-8+1e-10,'FCD lane/speed binding')
  before=pre[i]['bound_snapshot']['world']
  ids=sorted(vid for vid,v in frame.items() if vid.startswith('R_flow.') and v['lane']==':ramp_mid_0_0' and vid in before and before[vid]['lane_id']=='ramp_storage_0')
  for vid in ids:entries.append(dict(vehicle_id=vid,time_begin_s=i,time_end_s=i+1,motion=tls[i]['state']))
  need(ids==sorted(q['vehicle_id'] for q in r['actual_crossings']),'FCD crossings exact')
  if i==1205:
   front=frame['R_flow.2'];leader=frame['R_flow.1'];need(front['lane']=='ramp_storage_0' and leader['lane']==':ramp_mid_0_0','STOP FCD lanes')
   gap=float(leader['pos'])-5.+204.49-float(front['pos'])-2.5
   need(abs(gap-stop_gap['gap_excluding_minGap_m'])<1.1e-8 and abs(float(front['pos'])-stop_gap['lane_position_m'])<0.51e-8,'STOP FCD positions/gap')
  frames+=1;elem.clear()
need(frames==1206,'FCD frame count')
account=audit_rate_steps(post[1200:],entries);need(account['status']=='PASS_ACCOUNTING_ONLY','independent rate audit '+str(account))
need(len(arrivals)==len(set(arrivals)) and set(arrivals)=={v['id'] for v in trips if float(v['arrival'])>=0},'completed trips/arrivals equality')
for rec in logs:
 for name,v in rec['streams'].items():
  raw=(RAW/name).read_bytes();lo,hi=v['byte_start'],v['byte_end']
  need(0<=lo<=hi<=len(raw) and hashlib.sha256(raw[:hi]).hexdigest()==v['prefix_sha256'] and hashlib.sha256(raw[lo:hi]).hexdigest()==v['fragment_sha256'],'log interval byte/hash')
last=logs[-1];need(last['stage']=='AFTER_NATIVE_CLOSE_PROCESS_EOF' and all(v['byte_end']==(RAW/n).stat().st_size for n,v in last['streams'].items()),'EOF coverage')
need(not (RAW/'yellow_scope.jsonl').exists() and not (RAW/'policy_duration_requests.jsonl').exists() and not (RAW/'first_red_checkpoint.json').exists(),'unobserved phases falsely supplied')
# Explicit demand file lists vehicles; pending/due/future separated, not aliases.
demand=ET.parse(ROOT/card['package']/'demand.rou.xml').getroot();planned={v.get('id'):float(v.get('depart')) for v in demand.findall('vehicle')}
inserted={v['id'] for v in trips if float(v['depart'])>=0};due={vid for vid,t in planned.items() if t<1206};future=set(planned)-due
unfinished=[v['id'] for v in trips if float(v['arrival'])<0 and float(v['depart'])>=0]
groups={}
for role in 'MRUX':
 filt=lambda ids:[x for x in ids if x.startswith(role+'_flow.')]
 groups[role]={'due_before1206':len(filt(due)),'future_at_or_after1206':len(filt(future)),'inserted':len(filt(inserted)),'due_not_inserted':len(filt(due-inserted)),'unfinished_in_network':len(filt(unfinished))}
queue=ET.parse(RAW/'queues.xml').getroot();qlast=list(queue)[-1];qrows={v.get('id'):v.attrib for v in qlast.findall('./lanes/lane') if v.get('id') in ('ramp_storage_0','shared_approach_0')}
summary={'classification':'INDEPENDENT_ACTUAL_PREFIX_AUDIT_NOT_QUALIFICATION','run_id':card['spec']['run_id'],'raw_manifest_sha256':sha(ENG/'RAW_FINAL_SHA256_V1.json'),'raw_files_checked':79,'last_actual_ACK':1206,'observed_control_seconds':6,'accounting':account,'independent_entries':entries,'terminal_arrivals':len(arrivals),'terminal_status_counts':dict(collections.Counter(v['status'] for v in arrival_results)),'braking_min_speed_difference_m_s2':brake_min,'native_min_acceleration_m_s2':accel_min,'native_event_counter_max':event_max,'conditional_WAIT_records':wait_count,'supplied_control_steps':supplied,'FCD_TLS_ACK_frames':frames,'native_log_final_EOF':'BOUND','log_records':len(logs),'yellow_screen_event':None,'N_y_observed':None,'N_r_observed':None,'rejected_current_gap':stop_gap,'demand_group_counts':groups,'queue_export_final_BEGIN':qlast.get('timestep'),'last_queue_rows':qrows,'service_command':900,'qRamp':card['spec']['qRamp'],'r_ALINEA':None,'complete_cycles':0,'first_red_checkpoint_completed':False,'remaining_cycles':[{'begin_s':1224,'C':None,'C_applied':None,'E':None,'N':None},{'begin_s':1248,'C':None,'C_applied':None,'E':None,'N':None}],'native_safety_proven':False,'rate_qualified':False,'technical_cause':'OBSERVED_POST_CURRENT_GAP_WITH_PROJECT_MARGIN_DENIED'}
(OUT/'PREFIX_DATA_RESULTS_V1.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'TERMINAL_LAST_MOVEMENT_RESULTS_V1.json').write_text(json.dumps(arrival_results,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('last_queue_rows','accounting')},indent=2))
print('accounting',account['accounting'])
