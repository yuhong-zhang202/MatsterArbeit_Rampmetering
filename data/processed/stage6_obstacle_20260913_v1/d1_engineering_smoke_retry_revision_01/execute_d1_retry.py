"""One released retry with only a process-local SUMO_HOME correction."""
from pathlib import Path
import os,hashlib,json
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
out=Path(__file__).resolve().parent
pre=o.read_json(out/'retry_prelaunch_receipt.json')
for key in ('scientific_release','approval','launch_card','proposed_card','gate_policy','parent_execution_receipt','parent_technical_receipt','xsd_dependencies','materialization'):o.verify_binding(pre[key])
for binding in o.read_json(o.verify_binding(pre['xsd_dependencies']))['files']:o.verify_binding(binding)
card_path=o.verify_binding(pre['launch_card']);card=x.validate_launch_card(card_path,require_approval=True)
assert x.payload_sha(card)==pre['stable_payload_sha256']
journal=x.Journal(Path(card['budget_journal_directory']))
assert journal.counters()==pre['initial_budget_counters']
before=dict(os.environ)
assert before.get('SUMO_HOME')==pre['environment_diff']['SUMO_HOME']['before']
os.environ['SUMO_HOME']=pre['SUMO_HOME_realpath']
after=dict(os.environ)
diff={key:{'before':before.get(key),'after':after.get(key)} for key in before.keys()|after.keys() if before.get(key)!=after.get(key)}
assert diff=={'SUMO_HOME':{'before':pre['environment_diff']['SUMO_HOME']['before'],'after':pre['SUMO_HOME_realpath']}}
x.exclusive_json(out/'effective_process_environment_receipt.json',{'prelaunch':o.bind(out/'retry_prelaunch_receipt.json'),'environment_diff':diff,'before_environment_sha256':hashlib.sha256(o.encode(before)).hexdigest(),'effective_environment_sha256':hashlib.sha256(o.encode(after)).hexdigest(),'full_environment_values_not_exported':True,'scope':'real adapter inherits exactly this wrapper environment','executor':o.bind(Path(x.__file__))})
try:
 receipt=x.execute_attempt(card_path,'S6_V1_ML_S17_attempt2',journal,x.RealProcessAdapter(enable=True))
finally:
 if 'SUMO_HOME' in before:os.environ['SUMO_HOME']=before['SUMO_HOME']
 else:os.environ.pop('SUMO_HOME',None)
 assert dict(os.environ)==before
print(json.dumps({'execution_status':receipt['execution_status'],'reason':receipt['reason'],'exit_code':receipt['exit_code'],'budget_counters':receipt['budget_counters'],'xml_status':receipt['required_xml_validation']['status'],'receipt':o.bind(Path(receipt['materialization']['path']).parent/'execution_receipt.json')},indent=2))
