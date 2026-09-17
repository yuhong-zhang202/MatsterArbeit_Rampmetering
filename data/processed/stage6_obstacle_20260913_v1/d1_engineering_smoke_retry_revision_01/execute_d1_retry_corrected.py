"""One released retry with only a process-local SUMO_HOME correction."""
from pathlib import Path
import os,hashlib,json
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
out=Path(__file__).resolve().parent
pre=o.read_json(out/'retry_prelaunch_receipt.json')
for key in ('scientific_release','approval','launch_card','proposed_card','gate_policy','parent_execution_receipt','parent_technical_receipt','xsd_dependencies','materialization'):o.verify_binding(pre[key])
for binding in o.read_json(o.verify_binding(pre['xsd_dependencies']))['files']:o.verify_binding(binding,Path(pre['SUMO_HOME_realpath']))
card_path=o.verify_binding(pre['launch_card']);card=x.validate_launch_card(card_path,require_approval=True)
assert x.payload_sha(card)==pre['stable_payload_sha256']
journal=x.Journal(Path(card['budget_journal_directory']))
assert journal.counters()==pre['initial_budget_counters']
# Repeat the complete local dependency traversal, including every reference.
import xml.etree.ElementTree as ET
assert o.bind(out/'retry_prelaunch_receipt.json')['sha256']=='2d472c32b9e064afe374aa5d4a80bd4e503fd07b7562d45ad2553c71be398a21'
home=Path(pre['SUMO_HOME_realpath']);assert home.resolve()==home
manifest=o.read_json(o.verify_binding(pre['xsd_dependencies']));seen={};edges=[]
def visit(path):
    path=path.resolve();assert path.is_relative_to(home/'data/xsd') and path.is_file()
    if path in seen:return
    seen[path]=o.bind(path)
    for element in ET.parse(path).getroot().iter():
        if element.tag in ('{http://www.w3.org/2001/XMLSchema}include','{http://www.w3.org/2001/XMLSchema}import','{http://www.w3.org/2001/XMLSchema}redefine'):
            location=element.get('schemaLocation');assert location and '://' not in location
            target=(path.parent/location).resolve();edges.append({'from':str(path),'to':str(target),'kind':element.tag.split('}')[-1]});visit(target)
for name in manifest['root_schemas']:visit(home/'data/xsd'/name)
assert manifest['files']==[seen[path] for path in sorted(seen)] and manifest['edges']==edges
assert len(seen)==18 and len(edges)==21
mp=o.verify_binding(pre['materialization']);o.verify_materialization(mp,o.BATCH);material=o.read_json(mp)
binary=Path(pre['binary']['path'])
assert binary==o.SUMO_BINARY and binary.resolve()==binary and material['binary']==pre['binary']
assert o.sha256(binary)==pre['binary']['sha256']=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179'
assert not (mp.parent/'execution_claim.json').exists() and not any((mp.parent/'outputs').iterdir())
assert journal.counters()['reserved_or_unknown']==0 and journal.counters()['retry']==0
x.exclusive_json(out/'corrected_prelaunch_receipt.json',{'status':'PASS_PRELAUNCH','prior_stops':[o.bind(out/'preflight_stop_receipt.json'),o.bind(out/'preflight_stop_receipt_02.json')],'original_prelaunch':o.bind(out/'retry_prelaunch_receipt.json'),'corrected_script':o.bind(Path(__file__)),'wrapper_correction':'XSD verifier uses bound SUMO_HOME; binary path/realpath and direct SHA comparison','XSD_files_reparsed':18,'XSD_references_reparsed':21,'all_XSD_hashes_identical':True,'binary':material['binary'],'materialization':o.bind(mp),'live_counters':journal.counters(),'attempt2_claim_absent':True,'attempt2_outputs_empty':True,'concurrent_simulator_processes':[],'process_check_command':'tool /bin/ps -axo pid=,comm=','SUMO_starts_this_preflight':0})
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
