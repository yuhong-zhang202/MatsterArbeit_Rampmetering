"""Execute one explicit D2 cell only; no loop and no scientific evaluation."""
from pathlib import Path
import hashlib,json,os,sys
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
OUT=Path(__file__).resolve().parent
allowed={'S6_V1_ML_S17_attempt3':(1,2),'S6_V1_C_S17_attempt1':(2,3)}
assert len(sys.argv)==2 and sys.argv[1] in allowed
attempt_id=sys.argv[1];index,prior_starts=allowed[attempt_id]
audit=OUT/attempt_id;audit.mkdir()
base=o.BATCH/'c04_launch_preparation_revision_03'
card_path=o.BATCH/'d1_engineering_smoke_revision_01/approved_launch_card.json'
card=x.validate_launch_card(card_path,require_approval=True)
assert o.bind(base/'proposed_launch_card.json')['sha256']=='6dad07d6862eb6dfd6ca5ffd4bd09ccffa3563ff63106b67a983dcbaba765067'
assert x.payload_sha(card)=='4f65deb5ee65eb23ff071d6b79e85d1afcff1dd12fd50242cc7ed07b2161a1d3'
assert o.bind(base/'launch_gate_policy.json')['sha256']=='d57cd0a14bbb5d38f1539c7bf2460191caebaa15964ef1d7b6a83217a3784eab'
assert o.bind(base/'sg6p_user_approval.json')['sha256']=='8db02823acb7307826c86baa901658ba1fad5e5434b29bcd321e50a298eedb2d'
entry=card['attempts'][index];assert entry['attempt_id']==attempt_id
journal=x.Journal(Path(card['budget_journal_directory']));counters=journal.counters()
assert counters['sumo']==prior_starts and counters['validation']==prior_starts-2 and counters['retry']==1 and counters['reserved_or_unknown']==0
gate_path=journal.directory/'smoke_acceptance.json';gate=o.read_json(gate_path)
assert gate['accepted'] is True and gate['evidence_scope']=='real_executed_output' and gate['launch_payload_sha256']==x.payload_sha(card)
for binding in gate['evidence_bindings']:o.verify_binding(binding)
mp=o.verify_binding(entry['materialization']);o.verify_materialization(mp,o.BATCH);mat=o.read_json(mp)
binary=Path(mat['binary']['path']);assert binary==o.SUMO_BINARY and binary.resolve()==binary
assert o.sha256(binary)==mat['binary']['sha256']=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179'
assert not (mp.parent/'execution_claim.json').exists() and not any((mp.parent/'outputs').iterdir())
xsd_path=o.BATCH/'d1_engineering_smoke_retry_revision_01/xsd_dependency_manifest.json'
assert o.bind(xsd_path)['sha256']=='88ab7073ff68505fa43db144c505fdbbeb7236dd697cc41e3500eae41b6fb5c9'
xsd=o.read_json(xsd_path);home=Path(xsd['SUMO_HOME_realpath']);assert home.resolve()==home
assert len(xsd['files'])==18 and len(xsd['edges'])==21
for binding in xsd['files']:o.verify_binding(binding,home)
before=dict(os.environ);os.environ['SUMO_HOME']=str(home);effective=dict(os.environ)
diff={key:{'before':before.get(key),'after':effective.get(key)} for key in before.keys()|effective.keys() if before.get(key)!=effective.get(key)}
assert set(diff)=={'SUMO_HOME'} and diff['SUMO_HOME']['after']==str(home)
x.exclusive_json(audit/'prelaunch_receipt.json',{'status':'PASS_PRELAUNCH','attempt_id':attempt_id,'materialization':entry['materialization'],'argv':entry['argv'],'binary':mat['binary'],'launch_card':o.bind(card_path),'gate':o.bind(gate_path),'gate_evidence':gate['evidence_bindings'],'XSD_manifest':o.bind(xsd_path),'environment_diff':diff,'before_environment_sha256':hashlib.sha256(o.encode(before)).hexdigest(),'effective_environment_sha256':hashlib.sha256(o.encode(effective)).hexdigest(),'full_environment_values_not_exported':True,'initial_counters':counters,'concurrent_simulator_processes':[],'process_check':'tool /bin/ps -axo pid=,comm= immediately before this command','script':o.bind(Path(__file__))})
try:
    receipt=x.execute_attempt(card_path,attempt_id,journal,x.RealProcessAdapter(enable=True))
finally:
    if 'SUMO_HOME' in before:os.environ['SUMO_HOME']=before['SUMO_HOME']
    else:os.environ.pop('SUMO_HOME',None)
    assert dict(os.environ)==before
    x.exclusive_json(audit/'environment_restoration_receipt.json',{'restored':True,'environment_sha256':hashlib.sha256(o.encode(dict(os.environ))).hexdigest(),'prelaunch':o.bind(audit/'prelaunch_receipt.json')})
rp=mp.parent/'execution_receipt.json'
result={'execution_receipt':o.bind(rp),'execution_status':receipt['execution_status'],'reason':receipt['reason'],'budget_counters':journal.counters(),'next_validation_released_by_this_script':False,'scientific_analysis_calls':0,'main352_rows_written':0,'sensitivity14_rows_written':0}
if receipt['execution_status']=='completed':
    result['source_identity']=x.verify_executed_source(o.bind(rp),entry['run_id'])
    result['technical_identity_check']='passed'
    result['engineering_recommendation']='PASS_TECHNICAL_ONLY'
else:
    result['engineering_recommendation']='FAIL_STOP';result['technical_identity_check']='not_qualified'
result['attempt_wallclock_s']=journal.counters()['wallclock_s']-counters['wallclock_s']
result['attempt_budget_archive_bytes']=journal.counters()['archive_bytes']-counters['archive_bytes']
result['final_attempt_bytes']=x.attempt_bytes(mp.parent)
x.exclusive_json(audit/'engineering_receipt.json',result)
x.exclusive_json(audit/'attempt_manifest.json',{'engineering_receipt':o.bind(audit/'engineering_receipt.json'),'archive_files':[o.bind(p) for p in sorted(mp.parent.rglob('*')) if p.is_file()],'audit_files':[o.bind(p) for p in sorted(audit.iterdir()) if p.is_file()]})
print(json.dumps({'attempt_id':attempt_id,'status':receipt['execution_status'],'reason':receipt['reason'],'counters':journal.counters(),'engineering_receipt':o.bind(audit/'engineering_receipt.json')},indent=2))
raise SystemExit(0 if receipt['execution_status']=='completed' else 2)
