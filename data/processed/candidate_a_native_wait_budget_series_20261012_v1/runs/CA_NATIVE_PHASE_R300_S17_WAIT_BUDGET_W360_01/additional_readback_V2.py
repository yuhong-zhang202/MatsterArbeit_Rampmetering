"""Bounded W360 record/source/phase/EOF readback; no simulation or old tests."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[5];RUN='CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01';RAW=ROOT/'data/raw/candidate_a_native_wait_budget_series_20261012_v1'/RUN/'outputs';ENG=ROOT/'artifacts/candidate_a_native_wait_budget_series_20261012_v1/runs'/RUN/'engineering'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def rows(p):return[json.loads(x)for x in p.read_text().splitlines()if x]
def inspect():
 pre=rows(RAW/'pre_steps.jsonl');post=rows(RAW/'post_steps.jsonl');receipt=load(RAW/'bridge_receipt.json');card=load(RAW/'card.json');eng=load(ENG/'EXECUTION_RECEIPT_V1.json');observations=load(ENG/'ACTUAL_WAIT_AND_ENTRY_OBSERVATIONS_V1.json')
 assert len(pre)==len(post)==1272 and receipt['error']=='' and receipt['last_accounted_s']==1272
 phase=Counter(r['motion']for r in post[1200:]);assert phase=={'G':9,'y':9,'r':54}
 cycles=[]
 for k in range(3):
  interval=post[1200+k*24:1224+k*24];assert Counter(r['motion']for r in interval)=={'G':3,'y':3,'r':18}
  ids=[c['vehicle_id']for r in interval for c in r['actual_crossings']];assert ids==['R_flow.'+str(k)]
  cycles.append({'cycle_id':k,'begin_s':1200+k*24,'end_s':1224+k*24,'observed_G_s':3,'observed_y_s':3,'observed_r_s':18,'C':2,'C_applied':2,'E':2,'N':1,'N_G':1,'N_y':0,'N_r':0,'E_minus_N':1})
 postwait=[{'time_begin_s':r['time_begin_s'],'actual_query_time_s':r['time_end_s'],'record':r['post_native_receiver_decision']}for r in post if(r.get('post_native_receiver_decision')or{}).get('decision')=='WAIT_NATIVE_FOLLOWING'];prewait=[p['time_s']for p in pre if(p['bound_snapshot'].get('native_receiver_decision')or{}).get('decision')=='WAIT_NATIVE_FOLLOWING']
 assert len(postwait)==9 and len(prewait)==6 and [(r['time_begin_s'],r['post_decision'])for r in observations['actual_post_WAIT_records']]==[(r['time_begin_s'],r['record'])for r in postwait]
 entry=[e for r in post for e in r['actual_entry_following']];assert [e for row in observations['actual_entry_bound_before_after_records']for e in row['actual_entry_following']]==entry and len(entry)==3
 donor=load(ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/engineering/ACTUAL_WAIT_AND_ENTRY_OBSERVATIONS_V1.json')
 assert donor['actual_entries']==entry and donor['WAIT_post_records']==postwait and donor['control_accounting']==receipt['control_accounting']
 eq=load(ROOT/'artifacts/candidate_a_native_wait_budget_series_20261012_v1/engineering/COMMON_CORE_INPUT_EQUIVALENCE_V1.json')
 assert len(eq['common_core_sha256'])==31
 for n,h in eq['common_core_sha256'].items():assert sha(ROOT/n)==h and sha(RAW/'snapshots'/n)==h
 donorcard=load(ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/card.json');assert card['sources_sha256']!=donorcard['sources_sha256'] and card['environment']==donorcard['environment']
 requests=[q for p in pre if p['time_s']>=1200 for q in p['phase_requests']];assert[(q['time_s'],q['method'],q['value'])for q in requests]==[(1200,'setProgram','CA_C24'),(1200,'setPhase',0)]
 assert [r['time_s']for r in rows(RAW/'admission.jsonl')]==[1200,1224,1248]
 checkpoint=load(RAW/'first_red_checkpoint.json');assert checkpoint['time_s']==1207 and checkpoint['log_scope']=='PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED'and post[1206]['motion']=='r'
 assert receipt['first_red_checkpoint_verified']and post[-1]['phase_observation']['state_after']=='r'and post[-1]['phase_observation']['next_switch_after_s']==1272
 logs=receipt['final_logs'];assert logs['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF'and logs['status']=='BOUND_NO_OBSERVED_NATIVE_MESSAGE'and logs['all_streams_bound']and logs['process_returncode']==0
 for n,r in logs['streams'].items():assert r['byte_start']==0 and r['byte_end']==(RAW/n).stat().st_size and r['prefix_sha256']==sha(RAW/n)
 assert len(rows(RAW/'log_intervals.jsonl'))==2547 and all((RAW/n).stat().st_size==0 for n in ['sumo_stderr.log','sumo_stdout.log','sumo_error.log'])
 assert receipt['resource_watchdog']=={'reason':None,'error':None,'poll_s':.2} and receipt['monitored_elapsed_through_cleanup_s']<360
 acc=[v for r in post for v in r['braking_observation']['actual_acceleration_m_s2'].values()];diff=[v for r in post for v in r['braking_observation']['speed_difference_m_s2'].values()];assert min(acc)==min(diff)==-4.5 and all(all(v==0 for v in r['native_event_counters'].values())for r in post)
 assert [r['application_delay_s']for r in receipt['cycles']]==[0,24,48] and receipt['control_accounting']['mapping_command_latency']==0
 return{'status':'PASS_W360_ACTUAL_PHASE_SOURCE_WAIT_EOF_BINDING','pre_WAIT_count':6,'post_WAIT_count':9,'entered_vehicle_before_after_records':6,'phase_exposure_s':dict(phase),'cycles':cycles,'commonruntime31_snapshot_equal':True,'whole_source_snapshot_equal_to300':False,'crossing_and_selected_WAIT_queries_equal_to300':True,'full_all_world_trajectory_equality':'NOT_ADDITIONALLY_TESTED','checkpoint_s':1207,'checkpoint_monitored_elapsed_s':checkpoint['elapsed_monitored_wall_s'],'loop_terminal_s':receipt['loop_terminal_elapsed_s'],'monitored_cleanup_s':receipt['monitored_elapsed_through_cleanup_s'],'whole_CLI_s':eng['whole_CLI_elapsed_s'],'actual_72s_descriptive_service_veh_h':150,'requested_veh_h':300,'C':6,'C_applied':6,'E':6,'N':3,'E_minus_N':3,'service_qualified':False,'native_safety_proven':False,'min_covered_acceleration_m_s2':min(acc),'min_speed_difference_m_s2':min(diff),'native_event_counter_max':0,'command_field_age_s':[0,24,48],'new_command_latency':'NOT_OBSERVED_CONSTANT_REQUEST','negativecontrol_tests_reused_not_rerun':True,'new_native_starts_by_data':0}
if __name__=='__main__':print(json.dumps(inspect(),indent=2,allow_nan=False))
