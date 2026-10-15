"""Only selected existing 750 traces; no SUMO imports, setters or raw mutations."""
from pathlib import Path
import gzip,hashlib,json,time,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
TASK=ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/shortfall_investigation_v1'
DERIVED=ROOT/'data/processed/unified_alinea_actuator_20261013_v1/shortfall_engineering_v1'
RAW=ROOT/'data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/outputs'
STARTS=[1200+10*i for i in range(7)]
WANTED={t for b in STARTS for t in range(b,b+5)}|set(range(1260,1271))
LENGTH=204.49;INTERNAL_LENGTH=81.98

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def path_position(vehicle):
 lane=vehicle['lane'];pos=float(vehicle['pos'])
 if lane=='ramp_storage_0':return pos
 if lane==':ramp_mid_0_0':return LENGTH+pos
 if lane=='ramp_accel_0':return LENGTH+INTERNAL_LENGTH+pos
 raise ValueError('Selected trace route/lane unsupported: '+lane)

def main():
 start=time.monotonic();pre={};post={}
 for line in(RAW/'pre_steps.jsonl').open():
  r=json.loads(line)
  if r['time_s'] in WANTED:pre[r['time_s']]=r
 for line in(RAW/'post_steps.jsonl').open():
  r=json.loads(line)
  if r['time_end_s'] in WANTED:post[r['time_end_s']]=r
 fcd={};tls={}
 with gzip.open(RAW/'fcd.xml.gz','rb') as stream:
  for _,e in ET.iterparse(stream,events=('end',)):
   if e.tag=='timestep':
    t=int(float(e.get('time')));ack=t+1
    if ack in WANTED:fcd[ack]={v.get('id'):dict(v.attrib) for v in e.findall('vehicle') if v.get('id','').startswith('R_flow.') and int(v.get('id').split('.')[-1])<14}
    e.clear()
 with(RAW/'tls_states.xml').open('rb') as stream:
  for _,e in ET.iterparse(stream,events=('end',)):
   if e.tag=='tlsState':
    ack=int(float(e.get('time')))+1
    if ack in WANTED and e.get('id')=='ramp_mid':tls[ack]=dict(e.attrib)
    e.clear()
 acknowledgements={}
 for line in(RAW/'step_ack.jsonl').open():
  r=json.loads(line)
  if r['requested_target_s'] in WANTED:acknowledgements.setdefault(r['requested_target_s'],[]).append(r)
 cycles=json.loads((RAW/'bridge_receipt.json').read_text())['cycles'];selected=[]
 for i,b in enumerate(STARTS):
  ids=[f'R_flow.{2*i}',f'R_flow.{2*i+1}'];s=pre[b]['bound_snapshot'];local={x['vehicle_id']:x for x in s['vehicle_states']}
  traces=[]
  for ack in range(b,b+5):
   cars={}
   for vid in ids:
    q=fcd[ack][vid];native=post[ack]['post_world'][vid]
    assert q['lane']==native['lane_id'] and abs(float(q['speed'])-native['speed_m_s'])<=6e-9
    current=pre.get(ack,{}).get('bound_snapshot',{}).get('entry_following_before',{}).get(vid)
    cars[vid]={'FCD_BEGIN_s':ack-1,'FCD':q,'ACK_speed_m_s':native['speed_m_s'],
     'native_alpha_m_s2':post[ack]['braking_observation']['actual_acceleration_m_s2'][vid],
     'unwrapped_path_position_m':path_position(q),'following_query_at_this_ACK':current}
   assert len(acknowledgements[ack])==2 and acknowledgements[ack][-1]['actual_time_verified'] and acknowledgements[ack][-1]['actual_readback_s']==ack
   assert tls[ack]['state']==post[ack]['phase_observation']['state_after'] and tls[ack]['phase']==str(post[ack]['phase_observation']['phase_after'])
   traces.append({'ACK_s':ack,'cars':cars,'actual_TLS_BEGIN_label':tls[ack],
    'post_phase_observation':post[ack]['phase_observation'],'last_motion_interval':post[ack]['motion'],
    'actual_step_ACK_records':acknowledgements[ack]})
  second=ids[1];distance=LENGTH-local[second]['position_m'];movement=sum(post[a]['post_world'][second]['speed_m_s'] for a in range(b+1,b+5))
  actual_displacement=path_position(fcd[b+4][second])-local[second]['position_m']
  assert abs(movement-actual_displacement)<=5e-7
  entries=[x for a in range(b+1,b+5) for x in post[a]['actual_crossings']]
  assert len(entries)==cycles[i]['N_G'] and all(x['motion_signal_state']=='G' for x in entries)
  assert all(post[a]['motion']=='G' and tls[a]['state']=='G' for a in range(b+1,b+5))
  selected.append({'cycle_metadata':cycles[i],'at_G_begin_s':b,'front_id':ids[0],'second_id':ids[1],
   'storage_queue_count':len(s['storage']),'ingress_queue_count':sum(x['population']=='ingress' for x in s['vehicle_states']),
   'initial_front_state':local[ids[0]],'initial_second_state':local[ids[1]],'initial_receiver':s['receiver'],
   'second_distance_to_controlled_link_m':distance,'four_green_steps_motion_m':movement,
   'second_green_end_signed_position_relative_to_line_m':path_position(fcd[b+4][second])-LENGTH,
   'green_entries_actual':entries,'trace':traces})
 last=[]
 for ack in range(1260,1271):
  row=post[ack];last.append({'ACK_s':ack,'FCD_BEGIN_s':ack-1,'two_vehicles_FCD':{v:fcd[ack][v] for v in ['R_flow.12','R_flow.13']},
   'actual_TLS':tls[ack],'motion':row['motion'],'phase_observation':row['phase_observation'],
   'R13_native_alpha_m_s2':row['braking_observation']['actual_acceleration_m_s2']['R_flow.13'],
   'R13_delta_v_m_s2':row['braking_observation']['speed_difference_m_s2']['R_flow.13'],
   'post_receiver':row.get('post_receiver'),'post_native_receiver_decision':row.get('post_native_receiver_decision'),
   'actual_crossings':row['actual_crossings'],'numeric_stop_classifications':row.get('numeric_stop_classifications',[]),
   'legacy_braking_reasons':row.get('legacy_braking_reasons',[])})
 old=ROOT/'data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_01/outputs';before={}
 for line in(old/'pre_steps.jsonl').open():
  r=json.loads(line)
  if 1260<=r['time_s']<=1264:before[r['time_s']]=r['bound_snapshot']
 comparison=[]
 for t,s in before.items():
  now=pre[t]['bound_snapshot'];ids=['R_flow.12','R_flow.13']
  stateold={x['vehicle_id']:x for x in s['vehicle_states']};statenew={x['vehicle_id']:x for x in now['vehicle_states']}
  same=all(s['world'][v]==now['world'][v] for v in ids)
  # R12 leaves storage during the green; R13 remains covered in both versions.
  same=same and stateold['R_flow.13']==statenew['R_flow.13'] and s['motion']==now['motion']
  assert same
  comparison.append({'time_s':t,'two_vehicle_worlds_and_R13_local_state_exact_match':same,'scope':'Only pre-failure selected inputs; versions remain distinct'})
 card=json.loads((RAW/'card.json').read_text());manpath=ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/runs/UA_FIXED750_S17_02/RAW_FINAL_SHA256_V1.json';manifest=json.loads(manpath.read_text())
 new(DERIVED/'SEVEN_CYCLE_TRAJECTORY_V1.json',{'run_id':'UA_FIXED750_S17_02','clock':'FCD/TLS BEGIN k maps to ACK k+1; exact TraCI pre-state at Gbegin; no clock shift guessed',
  'source_digest':card['common_runtime_source_sha256'],'controlled_line_m':LENGTH,'cycles':selected,
  'raw_hashes_reused_from_frozen_manifest':{str((RAW/n).relative_to(ROOT)):manifest['files'][str((RAW/n).relative_to(ROOT))] for n in ['pre_steps.jsonl','post_steps.jsonl','fcd.xml.gz','tls_states.xml','step_ack.jsonl','bridge_receipt.json']},
  'manifest_sha256':sha(manpath),'scope':'Selected engineering derivation from already audited raw; no full inventory/raw re-audit'})
 new(DERIVED/'LAST_CYCLE_AND_VERSION_TIMELINE_V1.json',{'run_id':'UA_FIXED750_S17_02','ACK_trace':last,'old75001_selected_prefailure_comparison':comparison,
  'old_source_version':'61-source a2b25659','current_source_version':'64-source ea180197','versions_not_merged_as_qualification':True})
 sourcepaths=['src/candidate_a_unified_alinea_20261013/policy.py','src/candidate_a_unified_alinea_20261013/bridge.py','src/candidate_a_unified_alinea_20261013/adapter.py','src/candidate_a_native_receiver_wait_20261012/receiver_wait.py']
 checks={p:{'observed_sha256':sha(ROOT/p),'card_sha256':card['sources_sha256'][p],'matches':sha(ROOT/p)==card['sources_sha256'][p]} for p in sourcepaths}
 assert all(x['matches'] for x in checks.values())
 official=ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/SOURCE_RECEIPT.json';sr=json.loads(official.read_text());path='src/microsim/cfmodels/MSCFModel_Krauss.cpp';off=next(x for x in sr['sources'] if x['path']==path);cache=Path('/private/tmp/issue8_sumo_sources')/path
 assert sha(cache)==off['sha256']
 new(TASK/'EXTRACTION_RECEIPT_V1.json',{'status':'PASS_BOUNDED_SELECTED_JOIN','command':'.venv/bin/python '+str(Path(__file__).relative_to(ROOT)),
  'selected_ACK_frames':len(WANTED),'cycles':7,'last_cycle_steps':11,'four_G_motion_Euler_position_TLS_ACK_entry_checks':'PASS',
  'original_state_source_checks':checks,'official_Krauss_source':off,'official_cached_hash_matches':True,
  'derived_outputs':{str(p.relative_to(ROOT)):sha(p) for p in DERIVED.glob('*.json')},
  'native_runs':0,'tests_added_or_run':False,'raw_mutations':False,'runtime_mutations':False,'elapsed_s':time.monotonic()-start})
 print(json.dumps({'status':'PASS','selected_ACK_frames':len(WANTED),'second_G_end_signed_m':[x['second_green_end_signed_position_relative_to_line_m'] for x in selected],
 'last_second_distance':selected[-1]['second_distance_to_controlled_link_m'],'last_second_motion':selected[-1]['four_green_steps_motion_m'],'receipt_sha256':sha(TASK/'EXTRACTION_RECEIPT_V1.json')},ensure_ascii=False))
if __name__=='__main__':main()
