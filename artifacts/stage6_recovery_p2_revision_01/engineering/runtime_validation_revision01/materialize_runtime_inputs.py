#!/usr/bin/env python3
"""Materialize fixed three-attempt seed17 subset. No simulator invocation."""
import hashlib,json,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering');ENG=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering';BASE=ENG/'runtime_validation_revision01';NETWORK=ENG/'build_attempts/BUILD02/network.net.xml'
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
assert bind(NETWORK)['sha256']=='e47b0f94521414e55d0e5337b87204dc38d98a0a3a7c5466f2a5883f80b52710'
lanes={l.get('id'):l for l in E.parse(NETWORK).getroot().findall('edge/lane')};assert lanes['ramp_storage_0'].get('length')=='204.49'
attempts=[]
for oldid,newid,arm,role in [('P1B_SMOKE_R720_S17_attempt1','RV_SMOKE_R720_S17_attempt1','R720','smoke'),('P1B_R0_S17_attempt1','RV_R0_S17_attempt1','R0','validation'),('P1B_R720_S17_attempt1','RV_R720_S17_attempt1','R720','validation')]:
 old=ENG/'attempts'/oldid;inp=BASE/'inputs'/newid;inp.mkdir(parents=True,exist_ok=False);run=BASE/'runs'/newid;out=run/'outputs';assert not run.exists()
 (inp/'demand.rou.xml').write_bytes((old/'demand.rou.xml').read_bytes())
 add=(old/'scenario.add.xml.template').read_text().replace(str(old/'outputs'),str(out)).replace('PENDING_COMPILED_RAMP_STORAGE_LENGTH','204.49');(inp/'scenario.add.xml').write_text(add)
 cfg=(old/'scenario.schema_revision03.sumocfg.template').read_text().replace(str(ENG/'build_attempts/BUILD01/network.net.xml'),str(NETWORK)).replace(str(old/'outputs'),str(out)).replace(str(old/'demand.rou.xml'),str(inp/'demand.rou.xml')).replace(str(old/'scenario.add.xml.NOT_MATERIALIZED'),str(inp/'scenario.add.xml'))
 tree=E.fromstring(cfg);E.SubElement(tree.find('report'),'xml-validation',{'value':'always'});E.indent(tree);E.ElementTree(tree).write(inp/'scenario.sumocfg',encoding='utf-8',xml_declaration=True)
 roles=json.loads((old/'output_roles.json').read_text());roles=json.loads(json.dumps(roles).replace(str(old/'outputs'),str(out)).replace('PENDING_COMPILED_RAMP_STORAGE_LENGTH','204.49'));roles['status']='FINAL_STATIC_BOUND_RUNTIME_UNTESTED';put(inp/'output_roles.json',roles)
 identity=json.loads((old/'expected_identity_manifest.json').read_text());identity.update(attempt_id=newid,logical_run_id=newid.removesuffix('_attempt1'),role=role);put(inp/'expected_identity_manifest.json',identity)
 attempts.append({'attempt_id':newid,'logical_run_id':identity['logical_run_id'],'role':role,'arm':arm,'seed':17,'planned_counts':identity['planned_counts'],'inputs':[bind(inp/n) for n in ['demand.rou.xml','scenario.add.xml','scenario.sumocfg','output_roles.json','expected_identity_manifest.json']],'source_template_bindings':[bind(old/n) for n in ['demand.rou.xml','scenario.add.xml.template','scenario.schema_revision03.sumocfg.template','output_roles.json','expected_identity_manifest.json']],'run_root':str(run),'output_root':str(out),'argv':['/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo','-c',str(inp/'scenario.sumocfg')],'cwd':str(ROOT),'status':'not_started','launch_eligible':False,'time':{'begin':0,'end':2700,'step_length':1,'demand_begin':0,'demand_end':1500},'requires_previous_attempts':[a['attempt_id'] for a in attempts]})
put(BASE/'runtime_input_manifest.json',{'status':'STATIC_MATERIALIZED_PENDING_REVIEW','network':bind(NETWORK),'attempts':attempts,'calls':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'scientific_scope':'one seed17 descriptive mechanism contrast; smoke not replication; no full P1 closure','input_delta':['new isolated paths','BUILD02 network binding','E2 endPos204.49','xml-validation always runtime schema policy; no traffic dynamics change'],'original_demand_bytes_unchanged':True})
print(json.dumps({'attempts':[a['attempt_id'] for a in attempts],'manifest':bind(BASE/'runtime_input_manifest.json')},indent=2))
