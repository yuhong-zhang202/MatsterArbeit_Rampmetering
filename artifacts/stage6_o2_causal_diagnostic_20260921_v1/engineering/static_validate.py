#!/usr/bin/env python3
"""Static validation only. No simulator invocation or TraCI connection."""
import ast,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
B=Path(__file__).absolute().parent;R=B.parents[2]
OLD=R/'artifacts/stage6_targeted_validation_20260920_v1/engineering/inputs/TV_C_S17_attempt1'
H=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo')
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
checks=[]
def ck(n,v):checks.append({'check':n,'status':'PASS' if v else 'FAIL'});assert v,n
ck('demand_byte_identity',(B/'inputs/demand.rou.xml').read_bytes()==(OLD/'demand.rou.xml').read_bytes())
old=ET.parse(OLD/'scenario.add.xml').getroot();new=ET.parse(B/'inputs/scenario.add.xml').getroot()
for root in (old,new):
 for e in root.iter():
  for k in ('file','dest'):
   if k in e.attrib:e.set(k,Path(e.get(k)).name)
ck('all_additional_behavior_and_schema_attributes_equal',ET.tostring(old)==ET.tostring(new))
x=ET.parse(OLD/'scenario.sumocfg').getroot();y=ET.parse(B/'inputs/scenario.sumocfg').getroot()
for root in (x,y):
 root.find('time/end').set('value','450')
 for e in root.iter():
  if '/Users/' in e.get('value',''):e.set('value',Path(e.get('value')).name)
y.find('output').remove(y.find('output/fcd-output.max-leader-distance'))
for root in (x,y):
 for e in root.iter():
  if e.text is not None and not e.text.strip():e.text=None
  if e.tail is not None and not e.tail.strip():e.tail=None
ck('config_only_permitted_changes',ET.tostring(x)==ET.tostring(y))
newcfg=ET.parse(B/'inputs/scenario.sumocfg').getroot();net=Path(newcfg.find('input/net-file').get('value'))
ck('network_exact_hash',bind(net)['sha256']=='887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca')
ck('new_end_450',newcfg.find('time/end').get('value')=='450')
ck('step1_seed17',newcfg.find('time/step-length').get('value')=='1' and newcfg.find('random_number/seed').get('value')=='17')
ck('leader600',newcfg.find('output/fcd-output.max-leader-distance').get('value')=='600')
ck('new_raw_absent',not (R/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt1').exists())
for p in (B/'inputs').glob('*'):
 if p.suffix in ('.xml','.sumocfg'):
  root=ET.parse(p).getroot()
  for e in root.iter():
   for key,value in e.attrib.items():
    if '/data/raw/' in value:ck('isolated_output:'+p.name+':'+e.tag,'/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt1/outputs/' in value)
xml=[]
for name,schema in [('scenario.sumocfg','sumoConfiguration.xsd'),('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd')]:
 argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(H/'data/xsd'/schema),str(B/'inputs'/name)]
 p=subprocess.run(argv,capture_output=True,text=True);xml.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});ck('XSD:'+name,p.returncode==0)
# Verify existence and getter-only dispatch in installed1.26 without creating a connection.
sys.path.insert(0,str(H/'tools'));import traci,inspect
import importlib.util
spec=importlib.util.spec_from_file_location('observer_local',B/'observer.py');mod=importlib.util.module_from_spec(spec);sys.path.insert(0,str(B));spec.loader.exec_module(mod)
api={'vehicle':['getLeader','getMinGap','getTypeID','getRoute','getRouteIndex','getLaneID','getLanePosition','getPosition','getAngle','getSpeed','getAcceleration','getLength','getNextTLS','getNextLinks','getJunctionFoes'],
 'simulation':['getTime','getDeltaT','getCollidingVehiclesIDList','getStartingTeleportIDList','getEndingTeleportIDList','getEmergencyStoppingVehiclesIDList','getDepartedIDList','getArrivedIDList'],
 'trafficlight':['getProgram','getPhase','getRedYellowGreenState'],'lane':['getLinks']}
api_results=[]
for domain,names in api.items():
 for name in names:
  method=getattr(getattr(traci,domain),name);code=inspect.getsource(method)
  ck('getter_dispatch:'+domain+'.'+name,'_getUniversal' in code and '_setCmd' not in code)
  api_results.append({'api':domain+'.'+name,'signature':str(inspect.signature(method)),'source':inspect.getsourcefile(method),'line':inspect.getsourcelines(method)[1],'source_excerpt':code})
# Bind every recursively imported schema rather than just a top-level XSD.
seen=set()
def schema_walk(p):
 p=p.resolve()
 if p in seen:return
 seen.add(p)
 for e in ET.parse(p).getroot():
  q=e.get('schemaLocation')
  if q:schema_walk(p.parent/q)
for n in ['sumoConfiguration.xsd','additional_file.xsd','routes_file.xsd']:schema_walk(H/'data/xsd'/n)
result={'status':'PASS','checks':checks,'xml_checks':xml,'api_checks':api_results,'schema_bindings':[bind(p) for p in sorted(seen)],'SUMO_starts':0,'TraCI_connections':0,'netconvert':0,'GUI':0,'scope':'static only; runtime alignment and neutrality remain unverified'}
with (B/'static_validation_receipt.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':'PASS','checks':len(checks),'XSD':len(xml),'API':len(api_results),'schema_files':len(seen)}))
