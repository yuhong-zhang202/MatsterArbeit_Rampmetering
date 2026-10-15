"""Finite stop/E1/EOF fact extraction, never changes the frozen audit verdict."""
import sys,json,hashlib
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()))
from scripts.natural_actuator_qualification_20261015_v1 import streaming,provenance
from scripts.natural_service_audit_20261015_v1.actual import feedback_check
ROOT=Path.cwd();OUT=Path(__file__).parent;RAW=ROOT/'data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_02/outputs';IDS=('R_flow.108','R_flow.109','R_flow.110')
r=json.loads((OUT/'NATIVE_AUDIT_RESULT.json').read_text());receipt=json.loads((RAW/'bridge_receipt.json').read_text());assert receipt['last_completed_s']==receipt['last_accounted_s']==1262
facts=dict(classification='OBSERVED_STOP_PREFIX_NOT_QUALIFICATION',status='NOT_QUALIFIED_STOP_RETAINED',pre=[],post=[],native_counters={},scope='Only finite terminal/E1/EOF supplement; frozen audit UNKNOWN retained')
for i,p in enumerate(streaming.jsonl(RAW/'pre_steps.jsonl'),1):
 if p['time_s'] in (1260,1261):
  b=p['bound_snapshot'];facts['pre'].append(dict(line=i,time_s=p['time_s'],phase_requests=p['phase_requests'],phase={k:b[k] for k in ('program','motion_phase','motion','next_switch_before_s')},vehicles={v:b['terminal_before'].get(v) for v in IDS},receiver=b['receiver'],native_receiver_decision=b.get('native_receiver_decision'),entry_before={v:b['entry_following_before'].get(v) for v in IDS}))
counters=Counter();phases=Counter();lowest=None
for i,p in enumerate(streaming.posts(RAW/'post_steps.jsonl'),1):
 counters.update(p['native_event_counters']);phases[p['motion']]+=p['time_begin_s']>=600
 for vid,a in p['braking_observation']['actual_acceleration_m_s2'].items():
  if lowest is None or a<lowest['acceleration_m_s2']:lowest=dict(id=vid,time_begin_s=p['time_begin_s'],acceleration_m_s2=a)
 if p['time_begin_s'] in (1260,1261):
  facts['post'].append(dict(line=i,**{k:p.get(k) for k in ('time_begin_s','time_end_s','observed_time_s','motion','phase_observation','post_receiver','post_native_receiver_decision','reasons','terminal_reason','body_observation','actual_crossings')},vehicles={v:p['post_world'].get(v) for v in IDS},braking={k:{v:p['braking_observation'][k].get(v) for v in IDS} for k in ('actual_acceleration_m_s2','speed_difference_m_s2')}))
facts['native_counters']=dict(counters);facts['controlled_phase_seconds']=dict(phases);facts['minimum_actual_acceleration']=lowest
pre=facts['pre'][-1]['vehicles']['R_flow.109'];post=facts['post'][-1];v0=pre['speed_m_s'];v1=post['vehicles']['R_flow.109']['speed_m_s'];a=post['braking']['actual_acceleration_m_s2']['R_flow.109'];dv=post['braking']['speed_difference_m_s2']['R_flow.109'];assert abs(a-(v1-v0))<1e-12 and a==dv==-4.501
facts['stop_measurement']=dict(id='R_flow.109',before_s=1261,ACK_s=1262,signal=post['motion'],speed_before_m_s=v0,speed_after_m_s=v1,actual_acceleration_m_s2=a,speed_difference_m_s2=dv,normal_decel_limit_m_s2=4.5,existing_epsilon_m_s2=1e-6,excess_over_normal_limit_m_s2=-a-4.5,excess_over_existing_trigger_m_s2=-a-(4.5+1e-6),collision_proven=False,danger_or_numeric_false_positive_proven=False)
events=list(streaming.jsonl(RAW/'feedback_events.jsonl'));requests=[e for e in streaming.jsonl(RAW/'command_events.jsonl') if e['event']=='REQUESTED'];times=[e['global_s'] for e in events if e['event']=='E1_POST_ACK_EVENTS'];assert times==list(range(601,1262));decisions=feedback_check(events,1261,requests)
facts['complete_feedback_events']=dict(status='INDEPENDENT_COMPLETE_RECORDED_EVENT_PREFIX',observed_through_s=1261,window_count=len(decisions),windows=decisions,terminal_ACK_1262_event='NOT_OBSERVED_AFTER_STOP_NOT_SYNTHESIZED',native_XML_status=r['domains']['feedback_native_XML']['status'])
guard=json.loads((RAW.parent/'guardian_receipt.json').read_text());identity=json.loads((RAW/'owned_process_identity.json').read_text());card=json.loads((RAW/'card.json').read_text());release_sha=provenance.sha(RAW/'release.json');card_sha=provenance.sha(RAW/'card.json');w,n=identity['worker'],identity['native']
assert guard['run_id']==receipt['run_id']==identity['run_id']==card['spec']['run_id'];assert guard['card_sha256']==identity['card_sha256']==receipt['card_sha256']==card_sha;assert guard['release_sha256']==identity['release_sha256']==release_sha
provenance.guardian_receipt_limits(guard,card['guardian']);assert guard['worker_returncode']==1 and guard['stop_reason']=='WORKER_EXITED' and guard['native_identity_verified'] is True and guard['group_cleanup']['ownership_verified'] is True and guard['group_cleanup']['no_live_owned_members'] is True
assert identity['ownership_verified'] is True and identity['child_returncode_before'] is identity['child_returncode_after'] is None and w==guard['worker'] and w['status']==n['status']=='OBSERVED' and w['pid']==w['pgid']==w['sid']==n['pgid']==n['sid']
assert receipt['final_logs']['process_returncode']==0 and receipt['final_logs']['all_streams_bound'] is True and receipt['final_logs']['status']=='BOUND_NO_OBSERVED_NATIVE_MESSAGE'
facts['EOF_resource_observation']=dict(status='FINITE_NATIVE_EOF_CLEANUP_IDENTITY_FACTS_NOT_FROZEN_EOF_DOMAIN_PASS',guardian=guard,owned_identity=identity,native_process_returncode=0,native_logs=receipt['final_logs']['status'],original_reader_EOF=r['domains']['EOF_ownership'],guard_time_scope='monitored_elapsed_through_cleanup_s; not CLI or bridge timer',budget_settlement_performed=False)
refs=r.get('ordinary_reference_observations',[]);facts['reference_observation_summary']=dict(records=len(refs),roles=dict(Counter(e['role'] for e in refs)),meaning='repeated passive query observations with original legacy alarms retained, not unique hazards or safetyPASS')
facts['request_pending_summary']={key:value for key,value in receipt['command_records'].items() if value['status']!='ACK_OBSERVED'}
(OUT/'STOP_PREFIX_FACTS_V1.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts['stop_measurement']));print('feedback_windows',len(decisions));print('guardian_s',guard['monitored_elapsed_through_cleanup_s']);print('reference_roles',facts['reference_observation_summary'])
