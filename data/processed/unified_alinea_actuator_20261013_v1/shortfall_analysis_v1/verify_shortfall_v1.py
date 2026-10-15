"""Bounded independent seven-cycle/41-ACK check of existing immutable750 data."""
from pathlib import Path
import json,hashlib,gzip,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise ValueError(msg)
def near(x,y,tol=1e-8):return abs(x-y)<=tol

def main():
 raw=ROOT/'data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/outputs';derived=ROOT/'data/processed/unified_alinea_actuator_20261013_v1/shortfall_engineering_v1';eng=ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/shortfall_investigation_v1'
 original=read(derived/'SEVEN_CYCLE_TRAJECTORY_V1.json');timeline=read(derived/'LAST_CYCLE_AND_VERSION_TIMELINE_V1.json');manifest=read(ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/runs/UA_FIXED750_S17_02/RAW_FINAL_SHA256_V1.json');binder=read(eng/'ENGINEERING_DELIVERY_BINDING_V1.json')
 need(sha(eng/'ENGINEERING_DELIVERY_BINDING_V1.json')=='78cca6f105bf12a23776ff39eceea845707fe455167c53081853cdba1d115b27','ENGINEERING_BINDING')
 for p,h in binder['files'].items():need(sha(ROOT/p)==(h['sha256'] if isinstance(h,dict) else h),'ENGINEERING_FILE_DRIFT')
 relevant=['pre_steps.jsonl','post_steps.jsonl','step_ack.jsonl','tls_states.xml','fcd.xml.gz','bridge_receipt.json','policy_phase_requests.jsonl'];hashes={}
 for n in relevant:
  p=raw/n;k=str(p.relative_to(ROOT));h=manifest['files'][k];h=h['sha256'] if isinstance(h,dict) else h;need(sha(p)==h,'RELEVANT_RAW_SHA');hashes[k]=h
 chosen=set()
 for c in original['cycles']:chosen.update(x['ACK_s'] for x in c['trace'])
 chosen.update(x['ACK_s'] for x in timeline['ACK_trace']);need(len(chosen)==41,'41_TARGETED_ACK_SCOPE');steps={t-1 for t in chosen};pre_times={c['at_G_begin_s'] for c in original['cycles']}|{t for t in chosen if t<1270}
 pre={};post={};acks={}
 for line in (raw/'pre_steps.jsonl').open():
  q=json.loads(line)
  if q['time_s'] in pre_times:need(q['time_s'] not in pre,'DUP_PRE');pre[q['time_s']]=q
 for line in (raw/'post_steps.jsonl').open():
  q=json.loads(line)
  if q['time_begin_s'] in steps:need(q['time_begin_s'] not in post,'DUP_POST');post[q['time_begin_s']]=q
 for i,line in enumerate((raw/'step_ack.jsonl').open()):
  if i//2 in steps:acks.setdefault(i//2,[]).append(json.loads(line))
 tls={}
 for e in ET.parse(raw/'tls_states.xml').getroot():
  if e.get('id')=='ramp_mid' and float(e.get('time')) in steps:
   k=int(float(e.get('time')));need(k not in tls,'DUP_TLS');tls[k]=e.attrib.copy()
 frames={}
 with gzip.open(raw/'fcd.xml.gz','rb') as f:
  for _,e in ET.iterparse(f,events=('end',)):
   if e.tag!='timestep':continue
   k=int(float(e.get('time')))
   if k in steps:need(k not in frames,'DUP_FCD');frames[k]={v.get('id'):v.attrib.copy() for v in e}
   e.clear()
 need(set(post)==set(acks)==set(tls)==set(frames)==steps,'SELECTED_FRAME_COVERAGE')
 receipt=read(raw/'bridge_receipt.json');known=read(ROOT/'data/processed/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/revision01/ACTUAL_NUMERIC_RESULTS_V2.json');table=[];trace=[]
 for c in original['cycles']:
  b=c['at_G_begin_s'];sid=c['second_id'];fid=c['front_id'];p=pre[b]['bound_snapshot'];need(c['cycle_metadata']==next(x for x in receipt['cycles'] if x['begin_s']==b),'CYCLE_RECEIPT')
  states={x['vehicle_id']:x for x in p['vehicle_states']};s=states[sid];need(s==c['initial_second_state'] and states[fid]==c['initial_front_state'],'G_BEGIN_REAL_STATE')
  need(c['storage_queue_count']==len(p['storage']) and c['initial_receiver']==p['receiver'] and p['receiver']['available'] is True,'G_BEGIN_SUPPLY_HEAD_RECEIVER')
  initial=s['position_m'];endframe=frames[b+3][sid];endpos=float(endframe['pos'])+(204.49 if endframe['lane']==':ramp_mid_0_0' else 0);advance=sum(post[t]['post_world'][sid]['speed_m_s'] for t in range(b,b+4));distance=204.49-initial;entries=[]
  for t in range(b,b+4):
   f=frames[t];r=post[t];ids=sorted(v for v,x in f.items() if v.startswith('R_flow.') and x['lane']==':ramp_mid_0_0' and v in (pre[t]['bound_snapshot']['world'] if t in pre else {}) and pre[t]['bound_snapshot']['world'][v]['lane_id']=='ramp_storage_0')
   need(ids==sorted(q['vehicle_id'] for q in r['actual_crossings']),'TARGETED_INDEPENDENT_ENTRY');entries+=ids;need(tls[t]['state']=='G' and tls[t]['phase']=='0' and tls[t]['programID']=='I12_PACKET10' and r['motion']=='G','FOUR_G_ACTUAL')
  need(near(distance,c['second_distance_to_controlled_link_m']) and near(advance,c['four_green_steps_motion_m']) and near(endpos-initial,advance,2e-8) and near(endpos-204.49,c['second_green_end_signed_position_relative_to_line_m'],2e-8),'G_PATH_DISPLACEMENT')
  need(set(entries)==set(c['cycle_metadata']['crossing_ids']) and len(entries)==c['cycle_metadata']['N_G'],'CYCLE_ACTUAL_N')
  table.append({'begin_s':b,'second_id':sid,'start_position_m':initial,'start_speed_m_s':s['speed_m_s'],'distance_to_line_m':distance,'four_G_advance_m':advance,'green_end_signed_distance_beyond_line_m':endpos-204.49,'N_G':len(entries),'queue_supply':len(p['storage']),'head_receiver_available':True,'second_entry_BEGIN':next((t for t in range(b,b+4) if sid in {x['vehicle_id'] for x in post[t]['actual_crossings']}),None),'G_close_reason':c['cycle_metadata']['green_end_reason']})
  for x in c['trace']:
   ack=x['ACK_s'];t=ack-1;r=post[t];need(x['actual_TLS_BEGIN_label']==tls[t] and x['actual_step_ACK_records']==acks[t] and x['post_phase_observation']==r['phase_observation'],'DERIVED_PHASE_ACK_JOIN')
   for vid,v in x['cars'].items():need(v['FCD']==frames[t][vid] and near(v['ACK_speed_m_s'],r['post_world'][vid]['speed_m_s']) and near(v['native_alpha_m_s2'],r['braking_observation']['actual_acceleration_m_s2'][vid]),'DERIVED_CAR_JOIN')
 for ack in sorted(chosen):
  t=ack-1;r=post[t];a=acks[t];need(len(a)==2 and a[0]['requested_target_s']==ack and a[0]['ACK_received'] is True and a[1]['actual_time_verified'] is True and a[1]['actual_readback_s']==ack,'SELECTED_ACTUAL_ACK')
  if 1260<=ack<=1270:
   v=frames[t]['R_flow.13'];trace.append({'ACK_s':ack,'FCD_BEGIN_s':t,'lane':v['lane'],'position_m':float(v['pos']),'speed_m_s':r['post_world']['R_flow.13']['speed_m_s'],'motion':tls[t]['state'],'actual_delta_v_m_s2':r['braking_observation']['speed_difference_m_s2']['R_flow.13'],'actual_alpha_m_s2':r['braking_observation']['actual_acceleration_m_s2']['R_flow.13']})
 need(table[-1]['N_G']==1 and table[-1]['G_close_reason']=='MAX_GREEN_DEADLINE' and all(x['second_entry_BEGIN']==x['begin_s']+3 for x in table[:-1]),'FOURTH_G_MARGIN_AND_FINAL_SHORTFALL')
 need(trace[4]['ACK_s']==1264 and trace[4]['position_m']<204.49 and trace[5]['ACK_s']==1265 and trace[5]['motion']=='y' and trace[5]['actual_alpha_m_s2']==-4.501,'NUMERIC_AFTER_G_DEFICIT')
 observed=pre[1264]['bound_snapshot']['numeric_stop_before']['R_flow.13'];need(observed['dynamics']['sigma']==.5,'OBSERVED_SIGMA_GETTER_RECORD')
 return {'status':'PASS_BOUNDED_SELECTED_TRACE_NOT_NEW_RUN','seven_cycles':table,'selected_ACKs':len(chosen),'last_cycle_ACK_trace':trace,'observed_R13_first_yellow_getter_state':observed,'parameter_provenance':'initial VehicleState actual getters; sigma/emergency/maxspeed explicitly serialized numeric_stop_beforeR13@1264. Krauss model/default and actual RNG branch not observed.','direct_shortfall_before_numeric_yellow':True,'software_fault_demonstrated':False,'possible_following_or_RNG_contributions_uniquely_identified':False,'head_receiver_PASS_not_exclusion_of_second_vehicle_following':True,'raw_hashes_checked':hashes,'not_rerun_full_arrivals_or_all_manifest':True,'existing_actual_E':known['accounting']['accounting']['E'],'existing_actual_N':known['accounting']['accounting']['N'],'native_runs':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
