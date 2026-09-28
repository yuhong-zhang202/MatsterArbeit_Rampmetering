import json,copy,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import runtime_executor as e
B=Path(__file__).resolve().parent;E=B.parent;O=B.with_name('runtime_validation_revision01');m=json.loads((B/'runtime_input_manifest.json').read_text());checks=[];ns='{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'
def c(n,ok,**kw):checks.append(dict(check_id=n,status='PASS' if ok else 'FAIL',**kw))
def hint(root,xsd):
 if root.get(ns)!='http://sumo.dlr.de/xsd/'+xsd:raise ValueError('missing/wrong explicit SUMO schema hint')
for a in m['attempts']:
 d=B/'inputs'/a['attempt_id'];oldid=a['attempt_id'].replace('RV3_','RV_',1);old=O/'inputs'/oldid
 for name,xsd in [('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd')]:
  root=ET.parse(d/name).getroot();hint(root,xsd);c(a['attempt_id']+'.hint.'+name,True)
  bad=copy.deepcopy(root);bad.attrib.pop(ns)
  try:hint(bad,xsd);c(a['attempt_id']+'.negative_missing_hint.'+name,False)
  except ValueError:c(a['attempt_id']+'.negative_missing_hint.'+name,True)
  bad.set(ns,'http://sumo.dlr.de/xsd/wrong.xsd')
  try:hint(bad,xsd);c(a['attempt_id']+'.negative_wrong_hint.'+name,False)
  except ValueError:c(a['attempt_id']+'.negative_wrong_hint.'+name,True)
  root.attrib.pop(ns);oldroot=ET.parse(old/name).getroot()
  for x in root.iter():
   for key,val in list(x.attrib.items()):x.set(key,val.replace(str(B),str(O)).replace(a['attempt_id'],oldid))
  c(a['attempt_id']+'.semantic_identity.'+name,ET.tostring(root)==ET.tostring(oldroot))
 for name,xsd in [('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd'),('scenario.sumocfg','sumoConfiguration.xsd')]:
  argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(Path(e.SUMO_HOME)/'data/xsd'/xsd),str(d/name)];p=subprocess.run(argv,capture_output=True,text=True);c(a['attempt_id']+'.xsd.'+name,p.returncode==0,argv=argv,stderr=p.stderr)
 cfg=(d/'scenario.sumocfg').read_text().replace(str(B),str(O)).replace(a['attempt_id'],oldid);c(a['attempt_id']+'.all_config_values_identical',cfg==(old/'scenario.sumocfg').read_text())
 c(a['attempt_id']+'.new_run_absent',not Path(a['run_root']).exists())
 for row in a['inputs']:e.verify(row)
 c(a['attempt_id']+'.input_hashes',True)
 identities=json.loads((d/'expected_identity_manifest.json').read_text());c(a['attempt_id']+'.identity_binding',identities['attempt_id']==a['attempt_id'] and identities['logical_run_id']==a['logical_run_id'])
role=json.loads((E/'environment_binding.json').read_text());sources=[Path(e.SUMO_HOME)/'tools/sumolib/xml/__init__.py',Path(e.SUMO_HOME)/'tools/game/rail/stops.add.xml']
r={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','checks':checks,'count':len(checks),'real_SUMO_starts':0,'real_netconvert_starts':0,'validator':e.binding(__file__),'schema_bindings':role['schema_files'],'local_syntax_sources':[e.binding(x) for x in sources],'input_manifest':e.binding(B/'runtime_input_manifest.json'),'known_limit':'canonical SUMO URI format verified locally; actual runtime schema resolution remains untested'};e.durable(B/'static_validation_receipt_revision02.json',r);print(json.dumps({'status':r['status'],'checks':len(checks),'failed':[x['check_id'] for x in checks if x['status']=='FAIL']}))
