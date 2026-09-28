import json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import runtime_executor as e
BASE=Path(__file__).resolve().parent;ENG=BASE.parent
m=json.loads((BASE/'runtime_input_manifest.json').read_text());env=json.loads((ENG/'environment_binding.json').read_text());checks=[]
def check(name,val):checks.append({'check_id':name,'status':'PASS' if val else 'FAIL'})
for b in env['schema_files']:e.verify(b)
for a in m['attempts']:
 aid=a['attempt_id'];d=BASE/'inputs'/aid
 for b in a['inputs']+a['source_template_bindings']:e.verify(b)
 check(aid+'.no_existing_run',not Path(a['run_root']).exists())
 check(aid+'.demand_byte_identity',e.digest(d/'demand.rou.xml')==a['source_template_bindings'][0]['sha256'])
 for name,xsd in [('scenario.sumocfg','sumoConfiguration.xsd'),('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd')]:
  argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(Path(e.SUMO_HOME)/'data/xsd'/xsd),str(d/name)];p=subprocess.run(argv,capture_output=True,text=True);checks.append({'check_id':aid+'.xsd.'+name,'status':'PASS' if p.returncode==0 else 'FAIL','argv':argv,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 cfg=ET.parse(d/'scenario.sumocfg').getroot();check(aid+'.write_undeparted',cfg.find('output/tripinfo-output.write-undeparted').get('value')=='true');check(aid+'.no_teleport',cfg.find('processing/time-to-teleport').get('value')=='-1');check(aid+'.window',[cfg.find('time/'+x).get('value') for x in ['begin','end','step-length']]==['0','2700','1']);check(aid+'.seed',cfg.find('random_number/seed').get('value')=='17')
 net=ET.parse(cfg.find('input/net-file').get('value')).getroot();lanes={l.get('id'):float(l.get('length')) for l in net.findall('edge/lane')};add=ET.parse(d/'scenario.add.xml').getroot();dets=[x for x in add if x.tag in ['inductionLoop','laneAreaDetector']];check(aid+'.detectors11',len(dets)==11)
 for x in dets:
  check(aid+'.detector.'+x.get('id'),x.get('lane') in lanes and 0<=float(x.get('pos'))<lanes[x.get('lane')] and (x.tag!='laneAreaDetector' or float(x.get('endPos'))<=lanes[x.get('lane')]) and x.get('period')=='30' and str(Path(x.get('file')).parent)==a['output_root'])
 roles=json.loads((d/'output_roles.json').read_text());rr=roles.get('roles',roles.get('output_roles',[]));check(aid+'.roles17',len(rr)==17)
 route=ET.parse(d/'demand.rou.xml').getroot();counts={f.get('id'):int(f.get('number')) for f in route.findall('flow')};check(aid+'.population',sum(counts.values())==sum(a['planned_counts'].values()))
 check(aid+'.no_pending_token',not any(s in (d/'scenario.sumocfg').read_text()+(d/'scenario.add.xml').read_text() for s in ['pending_build','{{','BUILD01']))
check('exact_order',[a['attempt_id'] for a in m['attempts']]==e.ORDER)
receipt={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','checks':checks,'count':len(checks),'schema_bindings':env['schema_files'],'validator':e.binding(__file__),'input_manifest':e.binding(BASE/'runtime_input_manifest.json'),'real_SUMO_starts':0,'real_netconvert_starts':0}
e.durable(BASE/'static_validation_receipt.json',receipt);print(json.dumps({'status':receipt['status'],'checks':len(checks),'failed':[x['check_id'] for x in checks if x['status']=='FAIL']}))
