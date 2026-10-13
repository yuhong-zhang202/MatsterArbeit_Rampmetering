"""Bounded frozen-resource-prefix evidence audit; no simulator imports."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
TASK=ROOT/'artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/native_execution_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open() as f:
  for line in f:
   if line.strip():yield json.loads(line)
def main():
 mp=TASK/'RAW_FINAL_SHA256_V1.json';assert sha(mp)=='9f0a55efb1c0279782635f5556c9fe4101b50fb9a85328e779405b26b00a38dd';m=json.loads(mp.read_text());parent=ROOT/m['parent'];raw=parent/'outputs';actual={str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()};assert actual==set(m['files']) and len(actual)==130
 for n,h in m['files'].items():assert sha(ROOT/n)==h['sha256'] and (ROOT/n).stat().st_size==h['bytes']
 total=sum(v['bytes'] for v in m['files'].values());out=sum(v['bytes'] for n,v in m['files'].items() if Path(n).is_relative_to(raw.relative_to(ROOT)));assert total==m['bytes']==300852929 and out==m['outputs_subtree_bytes']==300851878
 bp=TASK/'POST_ENGINEERING_BINDING_V1.json';assert sha(bp)=='3a750b15fb20dcbe581d48e7a10e9119e055a6181d41f9fa454a4f043cd5c8e8'
 for n,h in json.loads(bp.read_text())['files_sha256'].items():assert sha(ROOT/n)==h
 rec=json.loads((raw/'bridge_receipt.json').read_text());assert rec['status']=='STOP_UNKNOWN_LOG_FINALIZATION' and rec['native_started'] is True and rec['last_completed_s']==rec['last_accounted_s']==1038 and rec['final_logs'] is None and rec['cycles']==[] and rec['control_accounting'] is None and rec['first_red_checkpoint_verified'] is False
 a=list(rows(raw/'step_ack.jsonl'));assert len(a)==2076
 for i in range(1038):
  x,y=a[2*i:2*i+2];assert x['requested_target_s']==y['requested_target_s']==i+1 and x['ACK_received'] is y['ACK_received'] is True and x['actual_time_verified'] is False and x['actual_readback_s'] is None and y['actual_time_verified'] is True and y['actual_readback_s']==i+1
 post_count=0;accounted=0;wrapper_count=0
 for item in rows(raw/'post_steps.jsonl'):
  post_count+=1
  if 'retained_receipts' in item:wrapper_count+=1;selected=item['retained_receipts']
  else:selected=[item]
  for q in selected:
   assert q['time_begin_s']==accounted and q['time_end_s']==accounted+1 and q['accounting_complete'] is True;accounted+=1
 assert accounted==1038
 commands=list(rows(raw/'command_events.jsonl'));assert len(commands)==1 and commands[0]['event']=='REQUESTED' and commands[0]['global_request_s']==1200
 logs=list(rows(raw/'log_intervals.jsonl'));assert logs[-1]['stage']=='AFTER_SIMULATION_STEP_ACK' and logs[-1]['time_end_s']==1038 and not any(q['stage']=='AFTER_NATIVE_CLOSE_PROCESS_EOF' for q in logs)
 ex=json.loads((TASK/'ACTUAL_EXECUTION_RECEIPT_V1.json').read_text());assert ex['CLI_exit_code']==1 and ex['native_start_count']==1 and ex['auto_retry_count']==0 and all(v is None for v in ex['explicit_unobserved_accounting'].values())
 major={n:(raw/n).stat().st_size for n in ('identity_journal.jsonl','pre_steps.jsonl','post_steps.jsonl','log_intervals.jsonl','fcd.xml.gz')}
 return dict(status='GO_LIMITED_FROZEN_RESOURCE_STOP_EVIDENCE_ONLY',run_id=m['run_id'],manifest_sha256=sha(mp),raw_file_count=130,parent_bytes=total,outputs_bytes=out,reservation_bytes=total-out,parent_excess_over_old_cap=total-300000000,outputs_excess_over_old_cap=out-300000000,trigger_instant_bytes=None,major_file_bytes=major,major_three_fraction_of_outputs=sum(major[n] for n in ('identity_journal.jsonl','pre_steps.jsonl','post_steps.jsonl'))/out,last_actual_ACK_s=1038,last_accounted_s=accounted,ACK_records=len(a),post_container_records=post_count,failure_wrapper_records=wrapper_count,requested_command_NOT_applied=commands,control_accounting=ex['explicit_unobserved_accounting'],controlled_cycles_observed=False,final_logs=None,log_capture_records=len(logs),last_capture_stage=logs[-1]['stage'],full_native_EOF_status='UNKNOWN_NOT_ESTABLISHED',native_exit_code=None,CLI_exit_code=1,monitored_s=rec['monitored_elapsed_through_cleanup_s'],full_reader_run='NOT_RUN_BOUNDED_PREACTIVATION_SCOPE_NO_FULL_WARMUP_SAFETY_AUDIT',native_safety_proven=False,rate_qualified=False,new_native_runs_by_data=0,old_failure_preserved=True)
if __name__=='__main__':print(json.dumps(main(),indent=2))
