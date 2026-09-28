#!/usr/bin/env python3
"""Materialize inactive final BUILD card; never starts traffic tools."""
import hashlib
import json
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
B=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering'
def binding(p):
 p=Path(p); return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def put(name,d):
 with (B/name).open('x') as f: json.dump(d,f,indent=2,sort_keys=True); f.write('\n')
worklog=ROOT/'docs/WORKLOG.md'
text=worklog.read_text(); start=text.index('## 2026-08-31 — Stage 1 merge instrumentation'); end=text.index('\n## ',start+4)
put('historical_worklog_evidence_snapshot.json',{'source_at_capture':binding(worklog),'section':text[start:end],'role':'Immutable exact excerpt; original mutable WORKLOG may append later. Count is three described Stage1 runs, not lifetime total.'})
sources=[binding(B/'historical_worklog_evidence_snapshot.json')]
expected={
 'data/processed/stage2_completion_20260909_v1/execution_ledger.json':'b8653755666f0bbc5a1b265f6c3928486732dcfcb3ad7870744ab96b7c0db27a',
 'artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused/summary.json':'4e80da39f4e3000122d30eb8f0d05500c8e6aa4491a9e91bc3f928d8f6cca4b1',
 'artifacts/stage2_completion_20260909_v1/runtime_archive/C23_attempt1/summary.json':'c781fd57b6cef5e96e9f2cba2bed5353b37b80752c761af0f0ca1a1bdf875028',
 'data/processed/stage4_qmain_sequential_20260912_v1/execution_ledger.json':'79d5fbc107faf3088d8ff86ce5fff2f1b588ade52a6d7ad8efbea2e7199880dd',
 'data/processed/stage6_obstacle_20260913_v1/c04_launch_preparation_revision_03/attempts/S6_V1_C_S17_attempt1/execution_receipt.json':'4ebe5ba781b45d5ac51b66b25907a91cea02a6d720b2fb365d96632c48c5764c'}
for path,sha in expected.items():
 row=binding(ROOT/path); assert row['sha256']==sha; sources.append(row)
put('budget_reconciliation.json',{
 'status':'reconciled_with_explicit_exclusions','scope':'Specified project evidence only; not exact lifetime total',
 'source_bindings':sources,
 'reconciliation_provenance':'Parent relay of independent data_analyst read-only audit, 2026-09-19; source hashes rechecked by engineering. Stage2 cumulative14 is broader than the seven-start completion ledger alone.',
 'stage_counts':[
  {'stage':'Stage1 instrumentation','SUMO_lower_bound':3,'netconvert':'unknown','TraCI':'unknown','GUI':'unknown','basis':'Three explicitly described low/custom/stress runs; excludes earlier scaffold/ALINEA/GUI and unitemized integration calls'},
  {'stage':'Stage2 including prior measurement work','SUMO_lower_bound':14,'netconvert_lower_bound':8,'TraCI_lower_bound':1,'GUI':'unknown','basis':'Parent/data cumulative reconstruction; completion ledger records seven new SUMO starts; C17+C23 bound summaries demonstrate netconvert usage. No-step TraCI probe counted separately; do not infer another SUMO start from it.'},
  {'stage':'Stage4','SUMO':4,'netconvert':4,'TraCI':0,'GUI':0,'count_quality':'exact registered stage'},
  {'stage':'Old Stage6 approved D1/D2','SUMO':4,'netconvert':0,'TraCI':0,'GUI':0,'count_quality':'exact registered stage'},
  {'stage':'Recovery P0/P1/P2','SUMO':0,'netconvert':0,'TraCI':0,'GUI':0,'count_quality':'current added traffic-tool starts; fake Python tests excluded'}],
 'specified_scope_lower_bounds':{'SUMO':25,'netconvert':12,'TraCI':1,'GUI':'unknown'},
 'explicit_exclusions':['Earlier ALINEA/scaffold integration runs not reconciled per process','Early GUI attempts cannot be counted exactly','Stage1 netconvert count unknown','No-step TraCI probe does not by itself imply a separate SUMO start','Unitemized early integration tests may add starts','These lower bounds are not a complete project total'],
 'new_card_budget_only':{'netconvert_starts':1,'SUMO':0,'TraCI':0,'GUI':0,'retry':0,'monitored_timeout_s':30,'observed_output_stop_bytes':100000000},
 'prior_unused_budget_transfer':False,'confidence':'High for bound ledger scope and current zero starts; incomplete lifetime reconciliation explicitly retained'})
card=json.loads((B/'SG6_BUILD_request_card_draft.json').read_text())
card.update(kind='SG6_BUILD_REQUEST_FINAL_OFFLINE',status='Proposed_ready_for_user_review_not_execution',approved=False,authorized_starts=0,launch_eligible=False)
card['supersedes_for_review']=binding(B/'SG6_BUILD_request_card_draft.json')
card['project_cumulative_budget']={'status':'reconciled_with_explicit_exclusions','evidence':binding(B/'budget_reconciliation.json'),'unused_historical_budget_transferred':False}
card['execution_contract']={'executor':binding(B/'build01_executor.py'),'test_script':binding(B/'test_build01_executor.py'),'test_receipt':binding(B/'fake_process_tests_revision02/test_receipt.json'),'contract_document':binding(B/'BUILD01_EXECUTOR_CONTRACT.md'),'watchdog_poll_s':0.05,'termination_grace_s':1,'kill_confirmation_wait_s':1,'approval_sidecar_required':True,'sidecar_binds_final_card_sha':True,'atomic_directory_claim':'BUILD01 exclusive mkdir; fsync reservation before Popen','all_claimed_attempts_consumed':True,'automatic_retry':False,'stderr':'verbatim persistent separate log; no suppression','crash_without_terminal_receipt':'terminal_unknown_consumed; manual process inspection; never relaunch'}
card['monitoring_note']='100000000 bytes is an observed stop line, not an OS hard quota.50ms polling; no defensible finite maximum overshoot.30s triggers termination; up to1s TERM wait then1s KILL confirmation plus scheduling delay. All excess/partial data preserved. Sidecar must expressly approve this monitoring semantics; if absolute caps required this executor is blocked.'
card['requires_explicit_user_resolution']=['Approve one netconvert build only, exact finalcard SHA and binary/input bindings','Acknowledge polling_50ms_possible_overshoot_preserved semantics; this is not a100MB hard storage quota','Acknowledge hard-killed wrapper can leave surviving child; claim remains consumed and needs manual inspection']
card['execution_command_after_separate_approval']={'argv':[str(ROOT/'.venv/bin/python'),str(B/'build01_executor.py'),'--card',str(B/'SG6_BUILD_request_card_revision02.json'),'--approval',str(B/'SG6_BUILD_user_approval.json'),'--execute'],'cwd':str(ROOT),'environment':{'SUMO_HOME':card['environment_overrides']['SUMO_HOME']},'status':'NOT_EXECUTED; approval sidecar absent'}
put('SG6_BUILD_request_card_revision02.json',card)
put('SG6_BUILD_approval_sidecar_TEMPLATE_NOT_APPROVED.json',{
 'status':'NOT_APPROVED','synthetic_test_only':False,'scope':'SG6-BUILD BUILD01 only','card_path':str(B/'SG6_BUILD_request_card_revision02.json'),'card_sha256':binding(B/'SG6_BUILD_request_card_revision02.json')['sha256'],'max_netconvert_starts':1,'monitoring_semantics':'UNDECIDED','user_approval_quote':None,'approved_at':None,'note':'Create a separate actual sidecar only after real user approval of this exact card and monitoring semantics. This template is inactive.'})
print(json.dumps({'final_card':binding(B/'SG6_BUILD_request_card_revision02.json'),'budget':binding(B/'budget_reconciliation.json'),'test_receipt':binding(B/'fake_process_tests_revision02/test_receipt.json')},indent=2))
