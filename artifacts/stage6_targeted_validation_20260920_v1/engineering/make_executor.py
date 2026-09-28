from pathlib import Path
b=Path(__file__).resolve().parent;old=Path('artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision04/runtime_executor.py').read_text()
header=old[:old.index('def preflight(')]
header=header.replace('Fail-closed one-at-a-time launcher for a fixed smoke + seed17 pair, no retries.','Fail-closed targeted validation launcher. Two technical fixtures then A/B/C; no automatic retries.')
header=header.replace("BASE=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision04'","BASE=ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering'")
header=header.replace("NETWORK_SHA='e47b0f94521414e55d0e5337b87204dc38d98a0a3a7c5466f2a5883f80b52710'","NETWORK_SHA='887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca'")
start=header.index('ORDER=');end=header.index('def require',start)
header=header[:start]+'''ORDER=['TV_SMOKE_B_LC_ON_S17_attempt1','TV_SMOKE_B_LC_OFF_S17_attempt1','TV_A_S17_attempt1','TV_B_S17_attempt1','TV_C_S17_attempt1']
LIMITS={'SUMO_starts':5,'retry':0,'seed23_starts':0,'netconvert':0,'TraCI':0,'GUI':0,'per_attempt_monitored_s':180,'total_monitored_s':900,'per_attempt_observed_bytes':1500000000,'total_observed_bytes':7500000000}
REQUIRED=['source_binding_exact','execution_complete_2700','output_role_set_exact','xml_roots_and_timegrids','planned_identity_coverage','departed_route_and_fcd_consistency','population_conservation','actual_lane_and_connection_consistency','detector_output_contract','tls_state_contract','output_manifest_complete','m_insertion_contract','native_lanechange_contract','meter_state_and_crossing_contract']
'''+header[end:]
pre='''def preflight(card_path,approval_path,attempt_id,environment):
 no_symlink(card_path);no_symlink(approval_path)
 card=json.loads(Path(card_path).read_text());approval=json.loads(Path(approval_path).read_text());sha=digest(card_path)
 require(card.get('kind')=='TARGETED_FIVE_START_RUNTIME_CARD' and card.get('approved') is False,'wrong card kind/status')
 require(card.get('limits')==LIMITS,'wrong limits')
 require(approval.get('status')=='authorized-under-user-task' and approval.get('card_sha256')==sha and approval.get('card_path')==str(card_path),'authorization/card mismatch')
 require(approval.get('scope')=='two technical fixtures then seed17 A/B/C' and approval.get('max_SUMO_starts')==5 and approval.get('synthetic_test_only') is False,'scope mismatch')
 require(approval.get('user_task_binding')==card['user_task_binding'] and approval.get('review_receipt'),'authorization provenance missing')
 verify(approval['user_task_binding']);validate_review(approval['review_receipt'],sha)
 require(environment.get('SUMO_HOME')==SUMO_HOME and not any(k.startswith(('DYLD_','LD_')) for k in environment),'unsafe environment')
 require(card['binary']['path']==str(BINARY) and card['binary']['sha256']==BINARY_SHA,'wrong binary')
 require(card['network']['sha256']==NETWORK_SHA,'wrong common network')
 require(card['executor']['path']==str(Path(__file__).absolute()),'wrong executor')
 for row in card['bindings']:verify(row)
 for row in [card['binary'],card['network'],card['executor'],card['test_receipt'],card['static_receipt'],card['input_manifest'],card['user_task_binding']]:verify(row)
 require(json.loads(Path(card['static_receipt']['path']).read_text())['status']=='PASS','static check failed')
 tests=json.loads(Path(card['test_receipt']['path']).read_text());require(tests['status']=='PASS' and tests['executor_sha256']==digest(__file__) and tests['real_SUMO_starts']==0,'test binding failed')
 require([a['attempt_id'] for a in card['attempts']]==ORDER and attempt_id in ORDER,'sequence mismatch')
 require(card['attempts']==json.loads(Path(card['input_manifest']['path']).read_text())['attempts'],'input manifest mismatch')
 raw=ROOT/'data/raw/stage6_targeted_validation_20260920_v1'
 for a in card['attempts']:
  require(a['seed']==17 and a['argv']==[str(BINARY),'-c',str(BASE/'inputs'/a['attempt_id']/'scenario.sumocfg')],'unregistered argv/seed')
  require(a['run_root']==str(raw/a['attempt_id']) and a['output_root']==str(raw/a['attempt_id']/'outputs'),'wrong output root')
  for row in a['inputs']:verify(row)
  cfg=ET.parse(a['argv'][2]).getroot();require(cfg.find('input/net-file').get('value')==card['network']['path'],'different network')
  require([cfg.find('time/'+k).get('value') for k in ['begin','end','step-length']]==['0','2700','1'] and cfg.find('random_number/seed').get('value')=='17','timing mismatch')
  no_symlink(a['run_root'])
 previous=card['attempts'][:ORDER.index(attempt_id)]
 for a in previous:
  run=Path(a['run_root']);rr=json.loads((run/'execution_receipt.json').read_text());require(rr['status']=='process_completed_pending_gate','prior technical/physical failure blocks card')
  validate_gate(BASE/'gates'/(a['attempt_id']+'.json'),a,sha)
 if ORDER.index(attempt_id)>=2:
  from measurement_helpers import normalized_xml_digest
  neutral=json.loads((BASE/'gates/logger_neutrality.json').read_text())
  require(neutral.get('status')=='PASS' and neutral.get('card_sha256')==sha and neutral.get('compared_roles')==17,'logger neutrality not passed')
  verify(neutral['analysis_version_binding'])
  for a in card['attempts'][:2]:require(neutral['receipt_hashes'][a['attempt_id']]==digest(Path(a['run_root'])/'execution_receipt.json'),'neutrality source changed')
  roles=json.loads((BASE/'inputs'/ORDER[1]/'output_roles.json').read_text())['required_xml_roles']
  for role in roles:
   name=role['role'];left=Path(card['attempts'][0]['output_root'])/name;right=Path(card['attempts'][1]['output_root'])/name
   require(normalized_xml_digest(left)==normalized_xml_digest(right),'logger changed non-lanechange output '+name)
 for a in card['attempts'][ORDER.index(attempt_id):]:require(not Path(a['run_root']).exists(),'current/future attempt already consumed')
 if raw.exists():require(set(x.name for x in raw.iterdir())<=set(ORDER),'unregistered attempt in task raw root')
 previous_time=sum(json.loads((Path(a['run_root'])/'execution_receipt.json').read_text())['wallclock_s'] for a in previous)
 previous_bytes=sum(size(Path(a['run_root'])) for a in previous)
 require(previous_time<LIMITS['total_monitored_s'] and previous_bytes<LIMITS['total_observed_bytes'],'task budget exhausted')
 return card,approval,card['attempts'][ORDER.index(attempt_id)],previous_time,previous_bytes

'''
body=old[old.index('def _run('):]
(b/'runtime_executor.py').write_text(header+pre+body)
test=Path('artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision04/test_runtime_executor.py').read_text().replace('len(e.ORDER),3','len(e.ORDER),5').replace('len(set(e.REQUIRED)),12','len(set(e.REQUIRED)),14')
(b/'test_runtime_executor.py').write_text(test)
