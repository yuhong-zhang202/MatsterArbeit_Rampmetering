"""Add output-only full-population evidence in preserved revision03 copies."""
from pathlib import Path
import copy,hashlib,json,subprocess,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent
def bind(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
m=json.loads((OUT/'input_manifest_revision02.json').read_text());changes=[];schema=[]
for a in m['attempts']:
    ad=Path(a['output_root']).parent;old=ad/'scenario.schema_revision02.sumocfg.template';new=ad/'scenario.schema_revision03.sumocfg.template'
    tree=ET.parse(old).getroot();base=copy.deepcopy(tree)
    ET.SubElement(tree.find('output'),'tripinfo-output.write-undeparted',{'value':'true'});ET.indent(tree,space='  ')
    with new.open('xb') as f:f.write(ET.tostring(tree,encoding='utf-8',xml_declaration=True)+b'\n')
    # Compare canonical tags/attributes, ignoring serialization whitespace.
    def semantic(r):return (r.tag,dict(r.attrib),[semantic(c) for c in r])
    check=copy.deepcopy(tree);check.find('output').remove(check.find('output/tripinfo-output.write-undeparted'))
    assert semantic(check)==semantic(base)
    cmd=['/usr/bin/xmllint','--nonet','--noout','--schema','/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo/data/xsd/sumoConfiguration.xsd',str(new)]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=20);assert r.returncode==0,r.stderr
    changes.append({'old':bind(old),'new':bind(new),'semantic_diff':[{'path':'/sumoConfiguration/output/tripinfo-output.write-undeparted','from':'absent(default_false)','to':'true'}],'remaining_semantics_identical':True})
    schema.append({'argv':cmd,'exit_code':r.returncode,'stderr':r.stderr})
    a['input_files']=[bind(new) if b['path']==str(old) else b for b in a['input_files']]
reg=json.loads((OUT/'executor_parameter_registration_revision02.json').read_text());reg['attempts']=m['attempts']
reg['never_inserted_source']='tripinfo write-undeparted=true; every planned ID required. Negative depart is explicit never-inserted marker, not missing-record inference; plannedtime may remain unavailable.'
save('executor_parameter_registration_revision03.json',reg)
m['registration']=bind(OUT/'executor_parameter_registration_revision03.json');m['supersedes']=bind(OUT/'input_manifest_revision02.json');m['revision']='03_undeparted_output_source'
m['output_only_change']={'reason':'Data reviewer identified inability to distinguish missing tripinfo from never-inserted planned identity without explicit records.','flag':'tripinfo-output.write-undeparted=true','local_schema_supported':True,'role_count_unchanged':17,'driver_scientific_inputs_changed':False,'changes':changes,'schema_results':schema,'negative_checks_inherited':bind(OUT/'offline_verification_receipt.json'),'vehroute_policy':'No separate undepar option; keep write-unfinished=true. Do not require never-inserted vehicle route record; use planned route source and tripinfo negative-depart marker.','neverinserted_plannedtime':'Do not infer from negative depart/departDelay; unknowns remain NA under revision04.'}
m['output_repair_script']=bind(Path(__file__))
save('input_manifest_revision03.json',m)
save('output_source_supplement_revision03.json',m['output_only_change'])
print('PASS: five output-only revisions schema-valid; all other XML semantics unchanged.')
