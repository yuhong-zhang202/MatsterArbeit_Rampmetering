"""Preserve first draft and use exact local XSD root names in revision02."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent
def bind(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def convert(old,new,tag):
    r=ET.parse(old).getroot();assert r.tag=='configuration';r.tag=tag;ET.indent(r,space='  ')
    with new.open('xb') as f:f.write(ET.tostring(r,encoding='utf-8',xml_declaration=True)+b'\n')
manifest=json.loads((OUT/'input_manifest.json').read_text())
save('initial_schema_finding.json',{'status':'initial_draft_schema_failure_preserved','input_manifest':bind(OUT/'input_manifest.json'),'observed':'xmllint rejected candidate.netccfg root configuration; local official XSD global root is netconvertConfiguration. sumoConfiguration.xsd analogously declares sumoConfiguration.','repair':'Change root names only in new revision02 copies, keep initial files. No scientific input/config values changed.','simulator_invocations':0})
old=OUT/'network_inputs/candidate.netccfg';new=old.with_name('candidate.schema_revision02.netccfg');convert(old,new,'netconvertConfiguration')
manifest['network_inputs']=[bind(new) if b['path']==str(old) else b for b in manifest['network_inputs']]
for a in manifest['attempts']:
    ad=Path(a['output_root']).parent;old=ad/'scenario.sumocfg.template';new=ad/'scenario.schema_revision02.sumocfg.template';convert(old,new,'sumoConfiguration')
    a['input_files']=[bind(new) if b['path']==str(old) else b for b in a['input_files']]
reg=json.loads((OUT/'executor_parameter_registration.json').read_text());reg['attempts']=manifest['attempts']
save('executor_parameter_registration_revision02.json',reg)
manifest['registration']=bind(OUT/'executor_parameter_registration_revision02.json')
manifest['repair_script']=bind(Path(__file__))
manifest['supersedes']=bind(OUT/'input_manifest.json')
manifest['revision']='02_schema_exact_roots'
save('input_manifest_revision02.json',manifest)
print('PASS: six configuration copies corrected; initial input manifest retained.')
