"""Bounded real-run phase/WAIT/log/resource evidence readback; no simulation."""
from pathlib import Path
from collections import Counter
import hashlib,json,gzip,math,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[5];RUN='CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2'
RAW=ROOT/'data/raw/candidate_a_native_receiver_wait_20261012_v1'/RUN/'outputs'
ENG=ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/runs'/RUN/'engineering'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(s)for s in p.read_text().splitlines() if s]
def checked(mapping):
 for n,h in mapping.items():assert sha(ROOT/n)==h,n
 return len(mapping)
def inspect():
 pre=rows(RAW/'pre_steps.jsonl');post=rows(RAW/'post_steps.jsonl');receipt=load(RAW/'bridge_receipt.json');card=load(RAW/'card.json');engineering=load(ENG/'EXECUTION_RECEIPT_V1.json')
 assert len(pre)==len(post)==1272 and receipt['error']=='' and receipt['last_accounted_s']==1272
 controlled=post[1200:];phase=Counter(r['motion']for r in controlled);assert dict(phase)=={'G':9,'y':9,'r':54}
 phase_cycles=[]
 for k in range(3):
  selected=controlled[k*24:(k+1)*24];counts=Counter(r['motion']for r in selected);assert counts=={'G':3,'y':3,'r':18}
  phase_cycles.append({'cycle_id':k,'observed_seconds':24,'observed_G_s':3,'observed_y_s':3,'observed_r_s':18,'C':2.,'C_applied':2.,'E':2,'N':1,'N_G':1,'N_y':0,'N_r':0,'E_minus_N':1})
 pre_wait=[{'time_begin_s':p['time_s'],'record':p['bound_snapshot']['native_receiver_decision']}for p in pre if (p['bound_snapshot'].get('native_receiver_decision')or{}).get('decision')=='WAIT_NATIVE_FOLLOWING']
 post_wait=[{'time_begin_s':r['time_begin_s'],'actual_query_time_s':r['time_end_s'],'record':r['post_native_receiver_decision']}for r in post if (r.get('post_native_receiver_decision')or{}).get('decision')=='WAIT_NATIVE_FOLLOWING']
 assert [r['time_begin_s']for r in pre_wait]==[1201,1202,1225,1226,1249,1250]
 assert [r['time_begin_s']for r in post_wait]==[1200,1201,1202,1224,1225,1226,1248,1249,1250]
 selected=load(ENG/'ACTUAL_WAIT_AND_ENTRY_OBSERVATIONS_V1.json');assert selected['WAIT_post_records']==post_wait and selected['WAIT_post_count']==9
 actual_entries=[record for row in post for record in row['actual_entry_following']];assert selected['actual_entries']==actual_entries and len(actual_entries)==3
 net=ET.parse(ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml').getroot();geometry={lane.get('id'):float(lane.get('length'))for lane in net.findall('.//lane')}
 for record in pre_wait+post_wait:
  q=record['record']['current_following'];assert q['getSecureGap_args']['speed']==q['actual_speed_m_s'] and q['getSecureGap_args']['leaderSpeed']==q['leader_speed_m_s']
  assert q['gap_excluding_minGap_m']+1e-9>=q['actual_secure_gap_m']+1.1 and record['record']['prospective_available'] is False
  assert q['path_geometry_m']=={lane:geometry[lane]for lane in q['path_geometry_m']}
 first=post_wait[0]['record'];assert first['current_following']['actual_speed_m_s']==0 and first['current_following']['actual_secure_gap_m']==0 and first['original_prospective_receiver']['leader']['secure_gap_m']==2.6
 for entry in actual_entries:
  for side in ['before','after']:assert entry[side]['path_geometry_m']=={lane:geometry[lane]for lane in entry[side]['path_geometry_m']}
 requests=[q for p in pre if p['time_s']>=1200 for q in p['phase_requests']];assert [(q['time_s'],q['method'],q['value'])for q in requests]==[(1200,'setProgram','CA_C24'),(1200,'setPhase',0)]
 admission=rows(RAW/'admission.jsonl');assert [r['time_s']for r in admission]==[1200,1224,1248] and all(r['receiver']['available'] is True for r in admission)
 checkpoint=load(RAW/'first_red_checkpoint.json');assert checkpoint['time_s']==checkpoint['last_accounted_s']==1207 and checkpoint['log_scope']=='PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED' and checkpoint['log_capture']['stage']=='FIRST_RED_CHECKPOINT_PROVISIONAL_UNTIL_EOF'
 assert post[1206]['motion']=='r' and post[1206]['status']=='MANDATORY_FIRST_RED_CHECKPOINT_PENDING'
 assert post[-1]['phase_observation']['state_after']=='r' and post[-1]['phase_observation']['next_switch_after_s']==1272
 assert receipt['first_red_checkpoint_verified'] is True and receipt['resource_watchdog']=={'reason':None,'error':None,'poll_s':.2}
 logs=receipt['final_logs'];assert logs['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF' and logs['all_streams_bound'] is True and logs['process_returncode']==0 and logs['status']=='BOUND_NO_OBSERVED_NATIVE_MESSAGE'
 for n,item in logs['streams'].items():assert item['byte_start']==0 and item['byte_end']==(RAW/n).stat().st_size and sha(RAW/n)==item['prefix_sha256']
 assert len(rows(RAW/'log_intervals.jsonl'))==2547
 assert all((RAW/n).stat().st_size==0 for n in ['sumo_stderr.log','sumo_stdout.log','sumo_error.log'])
 values=[v for r in post for v in r['braking_observation']['actual_acceleration_m_s2'].values()];diffs=[v for r in post for v in r['braking_observation']['speed_difference_m_s2'].values()];assert min(values)==min(diffs)==-4.5
 assert all(all(v==0 for v in r['native_event_counters'].values())for r in post)
 assert [r['application_delay_s']for r in receipt['cycles']]==[0,24,48] and all(r['command_requested_s']==1200 for r in receipt['cycles']) and receipt['control_accounting']['mapping_command_latency']==0
 counts={'current77':checked(load(ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/INPUT_BINDINGS_V2.json')['files']),'old59':checked(load(ROOT/'artifacts/candidate_a_native_budget_cycles_20261012_v1/engineering/INPUT_BINDINGS_V1.json')['files']),'protected536':checked(load(ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files'])};assert counts=={'current77':77,'old59':59,'protected536':536}
 resource=ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/disk_recovery_after_specific_approval';before=load(resource/'PRE_REPLACEMENT_RECEIPT_V1.json');after=load(resource/'POST_REPLACEMENT_RECEIPT_V1.json');plan=resource.parent/'RESOURCE_ACTION_PLAN_V1.json';auth=resource.parent/'RESOURCE_ACTION_HUMAN_AUTHORIZATION_V1.json'
 assert sha(plan)==before['plan_sha256'] and sha(auth)==before['human_authorization_sha256'] and len(before['exact_six_files'])==6
 archive_checks={}
 for entry in before['exact_six_files']:
  work=Path(entry['worktree_file']);primary=Path(entry['primary_original_file']);archive=Path(entry['planned_archive'])
  assert work.is_symlink() and work.resolve()==primary.resolve() and sha(primary)==entry['source_sha256']==sha(work)
  if str(archive) not in archive_checks:
   h=hashlib.sha256();size=0
   with gzip.open(archive,'rb')as f:
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
   assert h.hexdigest()==entry['source_sha256'] and size==entry['bytes'];archive_checks[str(archive)]={'compressed_sha256':sha(archive),'decompressed_sha256':h.hexdigest(),'decompressed_bytes':size}
 assert len(archive_checks)==2 and after['exclude_six_file_type_changes_from_code_commit_or_transplant'] is True and after['observed_net_free_change_bytes']==138223616
 return {'status':'PASS_ACTUAL_WAIT_PHASE_QUERY_LOG_BINDINGS_ONLY','pre_WAIT_count':6,'post_WAIT_count':9,'first_actual_WAIT':first,'phase_exposure_s':dict(phase),'cycles':phase_cycles,'actual_entries_count':3,'checkpoint_s':1207,'checkpoint_elapsed_monitored_s':checkpoint['elapsed_monitored_wall_s'],'loop_terminal_s':receipt['loop_terminal_elapsed_s'],'monitored_cleanup_s':receipt['monitored_elapsed_through_cleanup_s'],'whole_CLI_s':engineering['whole_CLI_elapsed_s'],'actual_72s_descriptive_discharge_veh_h':3*3600/72,'requested_veh_h':300,'service_qualified':False,'minimum_acceleration_covered_m_s2':min(values),'minimum_speed_difference_covered_m_s2':min(diffs),'actual_acceleration_vehicle_intervals':len(values),'speed_difference_vehicle_intervals':len(diffs),'counter_max':0,'log_final_EOF_status':logs['status'],'log_records':2547,'command_request_age_s':[0,24,48],'new_changed_command_delay':'NOT_OBSERVED_CONSTANT_COMMAND','actual_minus_applied_command_integral':0,'protected_counts':counts,'resource_recovery_checks':archive_checks,'six_type_changes_excluded_from_transplant':True,'resource_recovery_free_delta_bytes':138223616,'later_system_free_bytes_not_attributed_to_recovery':engineering['free_bytes_after'],'new_native_starts_by_this_check':0,'negativecontrol_tests_reused_not_rerun':True}
if __name__=='__main__':print(json.dumps(inspect(),indent=2,allow_nan=False))
