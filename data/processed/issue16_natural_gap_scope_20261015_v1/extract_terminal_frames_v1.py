"""Existing raw only. Bounded648..650 evidence, never a simulator or safe-speed replay."""
import sys,json,gzip,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();RAW=ROOT/'data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_01/outputs';OUT=Path(__file__).parent
IDS=('R_flow.0','R_flow.1')
def jsonrows(name):
 with (RAW/name).open() as f:
  for i,l in enumerate(f,1):yield i,json.loads(l)
result={'scope':'EXISTING_NATIVE_TERMINAL_FRAMES_NOT_COUNTERFACTUAL_MOTION_OR_QUALIFICATION','pre':[],'post':[],'identity':[],'acks':[],'TLS':[],'FCD':[],'setters':[]}
for ln,r in jsonrows('pre_steps.jsonl'):
 if r['time_s'] not in (648,649):continue
 b=r['bound_snapshot'];result['pre'].append({'line':ln,'time_s':r['time_s'],'phase_requests':r['phase_requests'],'signal':{k:b[k] for k in ('program','phase_before','state_before','motion_phase','motion','next_switch_before_s')},'receiver':b['receiver'],'native_receiver_decision':b['native_receiver_decision'],'vehicles':{v:b['terminal_before'][v] for v in IDS},'entry_following_before':{v:b['entry_following_before'].get(v) for v in IDS},'storage_states':[x for x in b['vehicle_states'] if x['vehicle_id'] in IDS]})
for ln,w in jsonrows('post_steps.jsonl'):
 rows=w['retained_receipts'] if 'retained_receipts' in w else [w]
 for r in rows:
  if r['time_begin_s'] not in (648,649):continue
  keys=('time_begin_s','time_end_s','status','accounting_complete','motion','phase_observation','post_receiver','post_native_receiver_decision','actual_crossings','actual_entry_following','body_observation','reasons','terminal_reason','native_event_counters')
  s={'line':ln,**{k:r[k] for k in keys if k in r}}
  s['speeds']={v:r['post_world'][v] for v in IDS};s['braking']={k:{v:r['braking_observation'][k][v] for v in IDS} for k in ('actual_acceleration_m_s2','speed_difference_m_s2')};result['post'].append(s)
for ln,r in jsonrows('identity_journal.jsonl'):
 if r['time_s'] in (648,649,650):result['identity'].append({'line':ln,**{k:r[k] for k in ('time_s','stage','model_scope','setter_calls')},'vehicle_states':{v:r['vehicle_states'][v] for v in IDS}})
for ln,r in jsonrows('step_ack.jsonl'):
 if r['requested_target_s'] in (649,650):result['acks'].append({'line':ln,**r})
for ln,r in jsonrows('control_setters.jsonl'):
 if r['time_s'] in (648,649,650):result['setters'].append({'line':ln,**r})
for _,e in ET.iterparse(RAW/'tls_states.xml',events=('end',)):
 if e.tag=='tlsState' and e.get('id')=='ramp_mid' and float(e.get('time'))>=648:result['TLS'].append(dict(e.attrib))
 e.clear()
with gzip.open(RAW/'fcd.xml.gz','rb') as f:
 for _,e in ET.iterparse(f,events=('end',)):
  if e.tag=='timestep':
   if float(e.get('time')) in (648,649):result['FCD'].append({'label_s':float(e.get('time')),'motion_ACK_s':float(e.get('time'))+1,'vehicles':{v.get('id'):dict(v.attrib) for v in e if v.get('id') in IDS}})
   e.clear()
package=ROOT/'artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1/QUAL_NATURAL_ALINEA_R900_S17_01'
demand=ET.parse(package/'demand.rou.xml').getroot();result['vTypes']=[dict(x.attrib) for x in demand.findall('vType')];result['requested_vehicles']=[dict(v.attrib) for v in demand.findall('vehicle') if v.get('id') in IDS]
cfg=ET.parse(package/'scenario.sumocfg').getroot();network=Path(cfg.find('input/net-file').get('value'));net=ET.parse(network).getroot();result['network_lanes']=[dict(l.attrib) for e in net.findall('edge') for l in e.findall('lane') if l.get('id') in ('ramp_storage_0',':ramp_mid_0_0')]
q=result['post'][-1]['post_native_receiver_decision']['current_following'];pre=result['pre'][-1]['entry_following_before']['R_flow.1'];follower=result['post'][-1]['speeds']['R_flow.1']['speed_m_s'];leader=result['post'][-1]['speeds']['R_flow.0']['speed_m_s']
pR1=q['lane_position_m'];pR0=result['post'][-1]['actual_entry_following'][0]['after']['lane_position_m'];physical=204.49-pR1+pR0-5
assert abs(physical-q['physical_bumper_gap_m'])<1e-9
assert q['getSecureGap_args']['speed']==follower and q['getSecureGap_args']['leaderSpeed']==leader
result['derived']={'post_query_deficit_m':q['gap_excluding_minGap_m']-q['actual_secure_gap_m'],'pre_query_deficit_m':pre['gap_excluding_minGap_m']-pre['actual_secure_gap_m'],'path_bumper_gap_m':physical,'path_excluding_follower_minGap_m':physical-q['min_gap_m'],'native_motion_followSpeed_args':'NOT_RECORDED','native_actual_branch_leaderDecel':'NOT_RECORDED','postquery_is_previous_motion_input':False,'roles_changed_from_R0_storage_front_to_R1_storage_front':True}
(OUT/'TERMINAL_FRAMES_V1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['derived']))
