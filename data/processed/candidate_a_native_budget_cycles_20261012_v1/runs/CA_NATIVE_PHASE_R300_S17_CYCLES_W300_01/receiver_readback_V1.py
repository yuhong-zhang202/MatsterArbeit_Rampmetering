"""Bounded read-only actual W300 receiver/value/phase-exposure readback."""
import gzip,hashlib,json,math
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[5]
RUN='CA_NATIVE_PHASE_R300_S17_CYCLES_W300_01'
RAW=ROOT/'data/raw/candidate_a_native_budget_cycles_20261012_v1'/RUN/'outputs'
ENG=ROOT/'artifacts/candidate_a_native_budget_cycles_20261012_v1/runs'/RUN/'engineering'

def load(p):return json.loads(p.read_text())
def near(a,b):assert math.isclose(a,b,abs_tol=1e-9), (a,b)
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s]

def inspect():
 manifest=load(ENG/'RAW_FINAL_SHA256_V1.json')
 binding=load(ENG/'ENGINEERING_DELIVERY_BINDING_V1.json')
 assert len(binding['files'])==12
 for n,h in binding['files'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 assert hashlib.sha256((ENG/'ENGINEERING_DELIVERY_BINDING_V1.json').read_bytes()).hexdigest()=='b4b58f08978d32e23cfe2daa165cdf26e1a4c017bd3fd3f1398f97ec791e4297'
 pre=rows(RAW/'pre_steps.jsonl')[-1]['bound_snapshot']
 terminal=rows(RAW/'post_steps.jsonl')[-1];post=terminal['retained_receipts'][0]
 assert terminal['last_accounted_s']==terminal['last_completed_s']==1201 and post['time_begin_s']==1200 and post['time_end_s']==1201
 assert pre['receiver']['available'] is True and pre['receiver']['front_id']=='R_flow.0'
 receiver=post['post_receiver'];assert receiver['available'] is False and receiver['front_id']=='R_flow.1' and receiver['nearest_internal']=='R_flow.0'
 assert receiver['reason']=='LEADER_SECURE_GAP' and post['reasons']==['POST_GREEN_RECEIVER_DENIED']
 diag=load(ENG/'RECEIVER_STOP_DIAGNOSTIC_V1.json');assert diag['pre_receiver']==pre['receiver'] and diag['post_receiver']==receiver
 for source in diag['sources']:
  assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
  assert (ROOT/source['path']).read_text().splitlines()[source['begin_line']-1:source['end_line']]==source['text'].splitlines()
 v={r['vehicle_id']:r for r in pre['vehicle_states']};front=v['R_flow.1'];leader=v['R_flow.0']
 assert pre['world']['R_flow.0']['lane_id']==pre['world']['R_flow.1']['lane_id']=='ramp_storage_0'
 assert post['post_world']['R_flow.0']['lane_id']==':ramp_mid_0_0' and post['post_world']['R_flow.1']['lane_id']=='ramp_storage_0'
 assert post['post_world']['R_flow.1']['speed_m_s']==post['braking_observation']['actual_acceleration_m_s2']['R_flow.1']==0
 rear=receiver['nearest_internal_rear_clearance_m'];required=front['length_m']+front['min_gap_m'];near(required,receiver['required_front_clearance_m'])
 internalpos=rear+leader['length_m'];near(internalpos,diag['formula_inputs']['internal_leader_position_m'])
 gap=receiver['leader']['gap_excluding_minGap_m'];secure=receiver['leader']['secure_gap_m'];near(gap,204.49-front['position_m']+internalpos-leader['length_m']-front['min_gap_m'])
 assert rear<required and gap+1e-9<secure+1.1
 frames={}
 with gzip.open(RAW/'fcd.xml.gz','rb') as stream:
  for _,e in ET.iterparse(stream,events=('end',)):
   if e.tag=='timestep':
    t=float(e.get('time'))
    if t in (1199.,1200.):frames[str(t)]={n.get('id'):n.attrib for n in e.findall('vehicle') if n.get('id') in ('R_flow.0','R_flow.1')}
    e.clear()
 assert frames==diag['independent_native_FCD_selected_rounded_precision2']
 near(float(frames['1200.0']['R_flow.1']['pos']),195.99)
 assert abs(float(frames['1200.0']['R_flow.0']['pos'])-internalpos)<.005001
 assert post['actual_crossings']==[{'vehicle_id':'R_flow.0','crossing_time_lower_s':1200,'crossing_time_upper_s':1201,'time_interval':'(lower,upper]','cycle_id':0,'motion_signal_state':'G'}]
 helper=ROOT/'src/stage6_safe_actuator_v10.py';snapshot=RAW/'snapshots/src/stage6_safe_actuator_v10.py'
 assert helper.read_bytes()==snapshot.read_bytes()
 assert '"speed": front.speed_m_s + front.accel_m_s2 * STEP_S' in helper.read_text()
 queried_speed=front['speed_m_s']+front['accel_m_s2']*1
 near(queried_speed,2.6);near(secure,2.6)
 receipt=load(RAW/'bridge_receipt.json');elapsed=receipt['monitored_elapsed_through_cleanup_s'];assert elapsed<300 and receipt['resource_watchdog']=={'reason':None,'error':None,'poll_s':.2}
 logs=receipt['final_logs'];assert logs['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF' and logs['process_returncode']==0 and logs['all_streams_bound'] is True and logs['status']=='BOUND_NO_OBSERVED_NATIVE_MESSAGE'
 for name,item in logs['streams'].items():
  p=RAW/name;b=p.read_bytes();assert item['byte_start']==0 and item['byte_end']==len(b) and hashlib.sha256(b).hexdigest()==item['prefix_sha256']
 assert len(rows(RAW/'log_intervals.jsonl'))==2404
 assert all((RAW/n).stat().st_size==0 for n in ['sumo_stderr.log','sumo_stdout.log','sumo_error.log'])
 assert len(post['braking_observation']['actual_acceleration_m_s2'])==199
 cli_stderr=ENG/'CLI_STDERR_V1.txt'
 # Client warning bytes are bound by engineering, not native online STOP coverage.
 client_files=[n for n in binding['files'] if 'STDERR' in n.upper()]
 return {'status':'PASS_RECEIVER_CONTRACT_VALUE_BINDING_ONLY_NOT_PHYSICAL_SAFETY',
  'pre_front':'R_flow.0','post_front':'R_flow.1','internal_leader':'R_flow.0',
  'rear_clearance_m':rear,'required_clearance_m':required,'internal_front_position_m':internalpos,
  'leader_gap_excluding_minGap_m':gap,'ego_minGap_m':front['min_gap_m'],'bumper_gap_m':gap+front['min_gap_m'],
  'secure_gap_recorded_m':secure,'required_secure_plus_margin_m':secure+1.1,
  'secure_gap_query_speed_reconstructed_m_s':queried_speed,'actual_post_front_speed_m_s':0,
  'secure_gap_query_scope':'hypothetical one-step acceleration release check, not current stationary queue danger; no actual getSecureGap rerun; exact query not separately serialized',
  'both_receiver_predicates_reject':True,'leader_reason_overwrites_clearance_reason':True,
  'native_alarm_observed':False,'current_guard_STOP_observed':True,'physical_unsafe_proven':False,
  'direct_sampling_or_identity_bug_proven':False,'monitored_elapsed_through_cleanup_s':elapsed,
  'native_final_logs_status':logs['status'],'native_log_records':2404,'last_post_acceleration_ids':199,
  'raw_manifest_entries':len(manifest['files']),'engineering_files_verified':12,
  'client_stderr_online_coverage':'EXCLUDED_UNCHANGED; final separate client capture only','bound_client_files':client_files,
  'future_cycle1_cycle2_metrics':{'C':None,'C_applied':None,'E':None,'N':None,'C_minus_E':None,'E_minus_N':None},
  'cycle0_phase_exposure':[{'phase':'G','observed_seconds':1,'scheduled_seconds':3,'N':1,'observation':'PARTIAL'},
   {'phase':'y','observed_seconds':0,'scheduled_seconds':3,'N':None,'observation':'NOT_OBSERVED'},
   {'phase':'r','observed_seconds':0,'scheduled_seconds':18,'N':None,'observation':'NOT_OBSERVED'}],
  'interpretation':'Actual values satisfy current contract refusal. Post-monitor asks about nextfront after legal R0 entry, not initial admission R0. Changing whether this terminates current green is contract responsibility change; largerwall budget does not repair this.'}
if __name__=='__main__':print(json.dumps(inspect(),indent=2,allow_nan=False))
