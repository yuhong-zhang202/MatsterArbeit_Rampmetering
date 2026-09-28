import json,copy,subprocess,xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
import runtime_executor as e
from repair_optional_filters import repair
B=Path(__file__).resolve().parent;O=B.with_name('runtime_validation_revision03');E=B.parent;m=json.loads((B/'runtime_input_manifest.json').read_text());checks=[];ns='{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'
def c(name,ok,**kw):checks.append(dict(check_id=name,status='PASS' if ok else 'FAIL',**kw))
for a in m['attempts']:
 aid=a['attempt_id'];oldid=aid.replace('RV4_','RV3_',1);d=B/'inputs'/aid;old=O/'inputs'/oldid
 for row in a['inputs']+a['source_template_bindings']:e.verify(row)
 c(aid+'.all_input_hashes',True)
 for name in ['scenario.sumocfg','demand.rou.xml']:
  normalized=(d/name).read_text().replace(str(B),str(O)).replace('RV4_','RV3_');c(aid+'.byte_semantics.'+name,normalized==(old/name).read_text())
 newtext=(d/'scenario.add.xml').read_text().replace(str(B),str(O)).replace('RV4_','RV3_');expected,count=repair((old/'scenario.add.xml').read_text());c(aid+'.exact_allowed_additional_delta',newtext==expected and count==22)
 add=ET.parse(d/'scenario.add.xml').getroot();dets=[x for x in add if x.tag in ['inductionLoop','laneAreaDetector']];c(aid+'.11_unfiltered_detectors',len(dets)==11 and all('vTypes' not in x.attrib and 'nextEdges' not in x.attrib for x in dets))
 for name,xsd in [('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd'),('scenario.sumocfg','sumoConfiguration.xsd')]:
  root=ET.parse(d/name).getroot()
  if name!='scenario.sumocfg':c(aid+'.schema_hint.'+name,root.get(ns)=='http://sumo.dlr.de/xsd/'+xsd)
  argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(Path(e.SUMO_HOME)/'data/xsd'/xsd),str(d/name)];p=subprocess.run(argv,capture_output=True,text=True);c(aid+'.xsd.'+name,p.returncode==0,argv=argv,stderr=p.stderr)
 identities=json.loads((d/'expected_identity_manifest.json').read_text());roles=json.loads((d/'output_roles.json').read_text())['required_xml_roles'];c(aid+'.identity_contract',identities['attempt_id']==aid and identities['logical_run_id']==a['logical_run_id']);c(aid+'.17_roles',len(roles)==17 and len({x['path'] for x in roles})==17 and all(str(Path(x['path']).parent)==a['output_root'] for x in roles));c(aid+'.fresh_run_root',not Path(a['run_root']).exists())
fixtures=[('<inductionLoop id="x" vTypes="" nextEdges="" />','<inductionLoop id="x" />',2),('<laneAreaDetector vTypes="car truck" nextEdges="a b" />','<laneAreaDetector vTypes="car truck" nextEdges="a b" />',0),('<inductionLoop vTypes="car" nextEdges="" />','<inductionLoop vTypes="car" />',1),('<laneAreaDetector vTypes="" nextEdges="a" />','<laneAreaDetector nextEdges="a" />',1),('<route vTypes="" nextEdges="" />','<route vTypes="" nextEdges="" />',0),('<inductionLoop name="" vTypes="" />','<inductionLoop name="" />',1),('<inductionLoop vTypes=" " nextEdges="a" />','<inductionLoop vTypes=" " nextEdges="a" />',0)]
for i,(src,expected,count) in enumerate(fixtures):c('filter_repair_regression_'+str(i),repair(src)==(expected,count))
h=json.loads((B/'prior_attempt_ledger.json').read_text());c('history_starts2_max5',h['actual_prior_SUMO_starts']==2 and h['maximum_cumulative_runtime_SUMO_starts']==5);c('history_time_decimal',h['prior_SUMO_wallclock_decimal_s']=='22.032722626005124');c('remaining_budget_no_reset',Decimal(h['remaining_time_decimal_s'])==Decimal('527.341159457995676') and h['remaining_bytes']==4499970801 and e.LIMITS['total_monitored_s']==549.3738820840008 and e.LIMITS['total_observed_bytes']==4500023552)
for row in h['files']:e.verify(row)
c('both_failed_archives_unchanged',True)
receipt={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','checks':checks,'count':len(checks),'validator':e.binding(__file__),'repair_function':e.binding(B/'repair_optional_filters.py'),'input_manifest':e.binding(B/'runtime_input_manifest.json'),'semantics_evidence':e.binding(B/'evidence/OPTIONAL_FILTER_SEMANTICS.md'),'schema_binding':e.binding(Path(e.SUMO_HOME)/'data/xsd/additional_file.xsd'),'real_SUMO_starts':0,'real_netconvert_starts':0,'runtime_loading':'not_yet_tested'};e.durable(B/'static_validation_receipt.json',receipt);print(json.dumps({'status':receipt['status'],'checks':len(checks),'failed':[x['check_id'] for x in checks if x['status']=='FAIL']}))
