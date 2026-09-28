import json,hashlib,copy
from pathlib import Path
R=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering');E=R/'artifacts/stage6_recovery_p2_revision_01/engineering';O=E/'runtime_validation_revision01';P=E/'runtime_validation_revision02';B=E/'runtime_validation_revision03';B.mkdir(exist_ok=False)
def bind(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
m=json.loads((O/'runtime_input_manifest.json').read_text());attempts=[]
for a in m['attempts']:
 n=copy.deepcopy(a);oldid=a['attempt_id'];newid=oldid.replace('RV_','RV3_',1);d=B/'inputs'/newid;d.mkdir(parents=True)
 for x in a['inputs']:
  src=Path(x['path']);s=src.read_text().replace(str(O),str(B)).replace(oldid,newid).replace(a['logical_run_id'],a['logical_run_id'].replace('RV_','RV3_',1))
  if src.name in ['scenario.add.xml','demand.rou.xml']:
   root,xsd=('additional','additional_file.xsd') if src.name=='scenario.add.xml' else ('routes','routes_file.xsd')
   s=s.replace('<'+root+'>','<'+root+' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/'+xsd+'">',1)
  (d/src.name).write_text(s)
 n['attempt_id']=newid;n['logical_run_id']=a['logical_run_id'].replace('RV_','RV3_',1);n['run_root']=str(B/'runs'/newid);n['output_root']=str(B/'runs'/newid/'outputs');n['argv'][2]=str(d/'scenario.sumocfg');n['inputs']=[bind(d/Path(x['path']).name) for x in a['inputs']];n['source_template_bindings']=a['inputs'];n['requires_previous_attempts']=[x['attempt_id'] for x in attempts];attempts.append(n)
put(B/'runtime_input_manifest.json',dict(m,attempts=attempts,status='STATIC_SCHEMA_HINT_REPAIR_PENDING_REVIEW',input_delta=['root schema hints on additional/routes only','independent input/output identity paths'],original_demand_bytes_unchanged=False,original_demand_semantics_unchanged=True))
failed=O/'runs/RV_SMOKE_R720_S17_attempt1';rr=json.loads((failed/'execution_receipt.json').read_text());priorfiles=[bind(p) for p in sorted(failed.rglob('*')) if p.is_file()];priorbytes=sum(x['bytes'] for x in priorfiles)
put(B/'prior_attempt_ledger.json',{'scope':'runtime recovery only, not project lifetime','actual_prior_SUMO_starts':1,'actual_prior_netconvert_starts_in_P2':2,'prior_SUMO_wallclock_s':rr['wallclock_s'],'prior_SUMO_directory_bytes':priorbytes,'prior_execution_receipt':bind(failed/'execution_receipt.json'),'files':priorfiles,'old_cards':[bind(O/'RUNTIME_VALIDATION_CARD.json'),bind(P/'RUNTIME_VALIDATION_CARD.json')],'old_manifests':[bind(O/'runtime_delivery_manifest.json'),bind(P/'runtime_delivery_manifest.json')],'failure':'additional schema declaration absent; traffic timesteps0','new_user_instruction':'smoke排查原因然后继续尝试','new_bounded_starts':3,'maximum_cumulative_runtime_SUMO_starts':4})
s=(P/'runtime_executor.py').read_text().replace("BASE=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision01'","BASE=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision03'").replace("'RV_","'RV3_")
s=s.replace("'total_monitored_s':540",f"'total_monitored_s':{540+rr['wallclock_s']!r}").replace("'total_observed_bytes':4500000000",f"'total_observed_bytes':{4500000000+priorbytes}")
s=s.replace("card['static_receipt'],*card['schema_bindings']","card['static_receipt'],card['prior_attempt_ledger'],*card['schema_bindings']")
s=s.replace("previous_time=sum(","history=json.loads(Path(card['prior_attempt_ledger']['path']).read_text())\n require(history['actual_prior_SUMO_starts']==1 and history['maximum_cumulative_runtime_SUMO_starts']==4,'wrong prior accounting')\n for row in history['files']:verify(row)\n previous_time=history['prior_SUMO_wallclock_s']+sum(")
s=s.replace("previous_bytes=sum(","previous_bytes=history['prior_SUMO_directory_bytes']+sum(")
s=s.replace("physical.get('observer')=='primary'","physical.get('observer')=='primary' and physical.get('source_path') and isinstance(physical.get('observed_unix'),(int,float))")
(B/'runtime_executor.py').write_text(s)
s=(P/'test_runtime_executor.py').read_text().replace("'observer':'primary'}","'observer':'primary','source_path':'synthetic.log','observed_unix':0}")
(B/'test_runtime_executor.py').write_text(s)
s=(P/'RUNTIME_CONTRACT.md').read_text().replace('Revision02 retains revision01 input bytes and the three as-yet-unclaimed run directories.','Revision03 repairs schema-root hints only and uses new RV3 attempt identities and directories. Revision01/02 and the failed first smoke remain immutable.').replace('RV_','RV3_').replace('Entire scope: 540 s and 4,500,000,000-byte observed stop line.',f'New three-attempt allowance: 540 s and 4,500,000,000 bytes. Including the already-consumed failed smoke: maximum4 SUMO starts, {540+rr["wallclock_s"]} s and {4500000000+priorbytes} bytes monitored cumulative envelope. The old smoke actually consumed {rr["wallclock_s"]} s and {priorbytes} bytes; its immutable evidence is bound in prior_attempt_ledger.json. Prior unused launch slots do not separately add to this scope.')
s+='\n\nSchema repair: standard SUMO root declarations reference http://sumo.dlr.de/xsd/additional_file.xsd and routes_file.xsd; local SUMO1.26 XSD files are hash-bound. Local bundled sumolib.xml.buildHeader generates this exact URI format. The existing xml-validation=always remains enabled. Static tests require these root hints in addition to external-XSD validation; the actual SUMO schema-resolution/traffic load remains a runtime gate.\n'
(B/'RUNTIME_CONTRACT.md').write_text(s)
print(B)
