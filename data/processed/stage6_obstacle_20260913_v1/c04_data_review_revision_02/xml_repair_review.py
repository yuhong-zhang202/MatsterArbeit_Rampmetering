import sys,json,ast,hashlib
from pathlib import Path
import xml.etree.ElementTree as E
from unittest.mock import patch
ROOT=Path.cwd();sys.path.insert(0,str(ROOT));D=ROOT/'data/processed/stage6_obstacle_20260913_v1/c04_data_review_revision_02'
from src.scenarios import stage6_h2_execution as x,stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m
js=lambda path:json.loads(Path(path).read_text());checks=[]
def check(name,fn):
 try:fn()
 except (o.EvidenceError,E.ParseError):checks.append({'name':name,'rejected':True});return
 raise AssertionError(name+' accepted')
def save(path,data):
 with path.open('x') as f:json.dump(data,f,indent=2,sort_keys=True)
source=D/'independent_fake_chain/attempts/S6_V1_ML_S17_attempt3';mat=js(source/'materialization_manifest.json')
paths={n:p for n,p in x.expected_outputs(mat).items() if n.endswith('.xml')};assert len(paths)==14
original={name:path.read_bytes() for name,path in paths.items()}
assert x.validate_required_xml_outputs(mat)['status']=='passed'
for name,path in paths.items():
 for label,raw in [('empty',b''),('malformed',b'<broken>'),('wrong_root',b'<wrong_role/>')]:
  try:path.write_bytes(raw);check(name+'_'+label,lambda:x.validate_required_xml_outputs(mat))
  finally:path.write_bytes(original[name])
 # Role swap includes same-root detector identity collisions.
 other=next(n for n in paths if n!=name and (('_e1_' in n or '_e2.' in n)==('_e1_' in name or '_e2.' in name)))
 try:path.write_bytes(original[other]);check(name+'_role_swap',lambda:x.validate_required_xml_outputs(mat))
 finally:path.write_bytes(original[name])
assert x.validate_required_xml_outputs(mat)['status']=='passed'
# Load only own already-inspected fixture definitions; no producer or real entrypoint.
tree=ast.parse((D/'independent_review.py').read_text());definitions=ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('Clock','Proc','emit','Adapter')],type_ignores=[])
exec(compile(definitions,'own_fixture_definitions','exec'),globals())
class EmptyQueue(Adapter):
 def start(self,argv,directory,*,launch_card_path):
  proc=super().start(argv,directory,launch_card_path=launch_card_path);(directory/'outputs/queues.xml').write_text('');return proc
F=D/'empty_queue_end_to_end';F.mkdir();card=x.prepare_launch_card(F);cp=F/'proposed_launch_card.json';j=x.Journal(F/'budget_journal');cl=Clock()
with patch('subprocess.Popen',side_effect=AssertionError('ALL PROCESS STARTS FORBIDDEN')):
 first=x.execute_attempt(cp,card['attempts'][0]['attempt_id'],j,Adapter(),clock=cl,sleep=cl.sleep,allow_fixture=True)
 assert first['execution_status']=='completed'
 save(j.directory/'smoke_acceptance.json',{'accepted':True,'evidence_scope':'synthetic_fixture','launch_payload_sha256':x.payload_sha(card),'evidence_bindings':[o.bind(cp)]})
 entry=card['attempts'][1];r=x.execute_attempt(cp,entry['attempt_id'],j,EmptyQueue(),clock=cl,sleep=cl.sleep,allow_fixture=True)
 assert r['execution_status']=='technical_failure' and r['reason']=='invalid_required_xml' and r['required_xml_validation']['status']=='failed'
 rp=Path(entry['materialization']['path']).parent/'execution_receipt.json'
 check('failed_XML_receipt_rejected',lambda:x.verify_executed_source(o.bind(rp),r['run_id'],allow_fixture=True))
 names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{q}_l{k}.xml' for q in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for k in (0,1)}
 bindings={n:r['output_bindings'][n] for n in names};bindings['network.net.xml']=r['network'];target=F/'blocked_analysis'
 check('failed_XML_no_qualified_analysis',lambda:m.analyze_to_new_directory(bindings,r['run_id'],target,execution_receipt=o.bind(rp),allow_fixture=True))
 assert not (target/'analysis_manifest.json').exists() and (target/'analysis_error.json').is_file()
save(D/'xml_repair_receipt.json',{'status':'PASS','checks':checks,'rejected':len(checks),'14_XML_roles':list(paths),'invalid_XML_execution_status':r['execution_status'],'qualified_analysis_absent':True,'fake_calls':2,'simulator_calls':0,'closes':'C04-D-M01'})
print('56 XML negative probes + 2 integration rejection probes PASS')
