#!/usr/bin/env python3
"""Read-only end-to-end card/output isolation regression; no launch."""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
B=Path(__file__).absolute().parent;ROOT=B.parents[2]
EXPECTED=ROOT/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt3'
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def validate(card_path):
 card=json.loads(card_path.read_text());a=card['attempt'];manifest=json.loads(Path(card['input_manifest']['path']).read_text())
 assert a['attempt_id']=='O2_C_S17_450_attempt3','wrong attempt ID'
 assert a['run_root']==str(EXPECTED),'card run root points to wrong attempt'
 assert a['output_root']==str(EXPECTED/'outputs'),'card output root mismatch'
 assert manifest['run_root']==a['run_root'] and manifest['output_root']==a['output_root'],'card/input-manifest root mismatch'
 assert not EXPECTED.exists(),'attempt2 root is not fresh'
 package=card_path.parent;cfg=ET.parse(package/'inputs/scenario.sumocfg').getroot();additional=ET.parse(package/'inputs/scenario.add.xml').getroot()
 paths=[]
 for root in [cfg,additional]:
  for e in root.iter():
   for value in e.attrib.values():
    if '/data/raw/' in value:
     assert Path(value).parent==EXPECTED/'outputs','writer escapes attempt2 output root'
     paths.append(value)
 assert len(paths)==len(set(paths))==20,'XML writer count/uniqueness mismatch'
 roles=json.loads((package/'inputs/output_roles.json').read_text())['required_xml_roles']
 assert len(roles)==18 and len({r['path'] for r in roles})==18,'18 unique roles required'
 assert {r['path'] for r in roles}==set(paths)-{str(EXPECTED/'outputs/sumo.log'),str(EXPECTED/'outputs/sumo_error.log')},'roles and actual writers differ'
 assert cfg.find('input/route-files').get('value')==str(package/'inputs/demand.rou.xml'),'wrong demand input path'
 assert cfg.find('input/additional-files').get('value')==str(package/'inputs/scenario.add.xml'),'wrong additional input path'
 prior=json.loads((package/'prior_attempt_accounting.json').read_text())
 for row in prior['previous_raw_files']:assert bind(Path(row['path']))==row,'attempt1 changed'
 assert sum(x['bytes'] for x in prior['previous_raw_files'])==118166,'prior bytes changed'
 return {'status':'PASS','card_sha256':bind(card_path)['sha256'],'attempt_id':a['attempt_id'],'run_root':a['run_root'],'output_root':a['output_root'],'run_root_exists':False,'XML_writers_verified':len(paths),'XML_roles_verified':len(roles),'prior_raw_files_verified':len(prior['previous_raw_files']),'prior_bytes':118166,'writer_paths':paths}
if __name__=='__main__':
 result=validate(B/'O2_DIAGNOSTIC_CARD.json')
 rejected=B.parent/'engineering_attempt02/O2_DIAGNOSTIC_CARD.json'
 try:validate(rejected)
 except AssertionError as exc:result['prior_bad_card_regression']={'status':'REJECTED_AS_REQUIRED','card':bind(rejected),'reason':str(exc)}
 else:raise AssertionError('old invalid card was not rejected')
 result['executor_observer_probe_byte_identity']={name:(B/name).read_bytes()==(B.parent/'engineering_attempt02'/name).read_bytes() for name in ['startup_probe.py']}
 assert all(result['executor_observer_probe_byte_identity'].values())
 result['real_SUMO_starts']=0;result['TraCI_connections']=0
 with (B/'path_isolation_receipt.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(result,sort_keys=True))
