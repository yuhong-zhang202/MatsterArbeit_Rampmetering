from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,sys
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
BASE=ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering'
OLD=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering'
HOME=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo')
def bind(p):
 p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def xml(p,root):
 E.indent(root);p.write_bytes(E.tostring(root,encoding='utf-8',xml_declaration=True))
inputs=BASE/'network_inputs';inputs.mkdir()
sources=[]
for ext in ['nod','edg','con','tll']:
 old=OLD/'network_inputs'/f'candidate.{ext}.xml';sources.append(bind(old));new=inputs/old.name
 if ext in ['edg','con']:new.write_bytes(old.read_bytes())
 else:
  root=E.parse(old).getroot()
  if ext=='nod':
   node=root.find("node[@id='ramp_mid']");assert node.get('type')=='priority';node.set('type','traffic_light');node.set('tl','ramp_mid')
  else:
   for name,phases in [('A_OPEN',[(60,'G')]),('B_MODERATE',[(22,'G'),(3,'y'),(35,'r')]),('C_STRONG',[(12,'G'),(3,'y'),(45,'r')])]:
    tl=E.SubElement(root,'tlLogic',id='ramp_mid',type='static',programID=name,offset='0')
    for duration,state in phases:E.SubElement(tl,'phase',duration=str(duration),state=state)
  xml(new,root)
root=E.parse(OLD/'network_inputs/candidate.schema_revision02.netccfg').getroot()
for el in root.find('input'):el.set('value',str(inputs/Path(el.get('value')).name))
run=BASE/'build_attempts/TV_BUILD01'
root.find('output/output-file').set('value',str(run/'network.net.xml'));xml(inputs/'candidate.netccfg',root)
schema={'nod':'nodes_file.xsd','edg':'edges_file.xsd','con':'connections_file.xsd','tll':'tllogic_file.xsd'}
checks=[]
import subprocess
for ext,s in schema.items():
 argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(HOME/'data/xsd'/s),str(inputs/f'candidate.{ext}.xml')]
 r=subprocess.run(argv,capture_output=True,text=True);checks.append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr
save(BASE/'source_preflight.json',{'status':'PASS','scope':'new task, exploratory protocol remains empty','source_bindings':sources,'context_bindings':[bind(ROOT/p) for p in ['AGENTS.md','docs/PROJECT_STATE.md','docs/DECISIONS.md','docs/EXPERIMENT_PROTOCOL.md','docs/WORKLOG.md']],'schema_checks':checks,'deltas':['ramp_mid node priority→traffic_light tl=ramp_mid','three static ramp_mid programs A/B/C added; urban program unchanged'],'SUMO_calls':0,'TraCI_calls':0,'GUI_calls':0})
print('source package PASS',inputs)
