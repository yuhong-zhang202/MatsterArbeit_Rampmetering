"""Offline schema and input audit. Only /usr/bin/xmllint may be spawned."""
from pathlib import Path
import copy,hashlib,json,subprocess,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
XSD=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo/data/xsd')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
manifest=json.loads((OUT/'input_manifest_revision02.json').read_text());checks=[]
def check(cond,label):
    checks.append({'label':label,'passed':bool(cond)})
    if not cond:raise ValueError(label)
def bindcheck(b):check(sha(Path(b['path']))==b['sha256'],'hash:'+b['path'])
for b in manifest['source_bindings']+manifest['network_inputs']+[manifest['environment'],manifest['output_contract'],manifest['registration'],manifest['script']]:bindcheck(b)
env=json.loads((OUT/'environment_binding.json').read_text())
for b in [*env['binary'].values(),env['framework_info'],env['xmllint'],*env['schema_files']]:bindcheck(b)
schema=[]
def xsd(p,name,expected=True):
    cmd=['/usr/bin/xmllint','--nonet','--noout','--schema',str(XSD/name),str(p)]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
    ok=r.returncode==0
    schema.append({'argv':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'expected_schema_pass':expected,'matched_expectation':ok==expected})
    check(ok==expected,'schema:'+p.name)
for n,s in [('candidate.nod.xml','nodes_file.xsd'),('candidate.edg.xml','edges_file.xsd'),('candidate.con.xml','connections_file.xsd'),('candidate.tll.xml','tllogic_file.xsd'),('candidate.schema_revision02.netccfg','netconvertConfiguration.xsd')]:xsd(OUT/'network_inputs'/n,s)
nodes=ET.parse(OUT/'network_inputs/candidate.nod.xml').getroot();edges=ET.parse(OUT/'network_inputs/candidate.edg.xml').getroot();cons=ET.parse(OUT/'network_inputs/candidate.con.xml').getroot()
def topology_validate(ns,es,cs):
    nd={n.get('id'):n for n in ns};ed={e.get('id'):e for e in es}
    assert len(nd)==11==len(ns) and len(ed)==10==len(es)
    assert nd['merge_end'].get('x')=='900' and nd['freeway_merge'].get('x')=='600'
    pairs=set()
    for c in cs:
        a,b=c.get('from'),c.get('to');i,j=int(c.get('fromLane')),int(c.get('toLane'))
        assert (a,b,i,j) not in pairs;pairs.add((a,b,i,j))
        assert ed[a].get('to')==ed[b].get('from')
        assert 0<=i<int(ed[a].get('numLanes')) and 0<=j<int(ed[b].get('numLanes'))
    expected={('main_up','merge_section',0,1),('main_up','merge_section',1,2),('ramp_accel','merge_section',0,0),('merge_section','main_down',1,0),('merge_section','main_down',2,1)}
    assert {p for p in pairs if p[0] in {'main_up','ramp_accel','merge_section'}}==expected
    assert ed['merge_section'].find("lane[@index='1']").get('changeRight')=='authority'
    assert ed['ramp_accel'].get('shape')=='500,-15 550,-5 600,-6.4'
topology_validate(nodes,edges,cons);check(True,'input_topology_intent')
flow_common={};spec_seen=set()
for a in manifest['attempts']:
    for b in a['input_files']:bindcheck(b)
    ad=Path(a['output_root']).parent
    xsd(ad/'demand.rou.xml','routes_file.xsd');xsd(ad/'scenario.schema_revision02.sumocfg.template','sumoConfiguration.xsd')
    xsd(ad/'scenario.add.xml.template','additional_file.xsd',False)
    d=ET.parse(ad/'demand.rou.xml').getroot();cfg=ET.parse(ad/'scenario.schema_revision02.sumocfg.template').getroot();add=ET.parse(ad/'scenario.add.xml.template').getroot()
    flows=d.findall('flow');fs={f.get('id')[0]:f for f in flows}
    check([f.get('id')[0] for f in flows]==(['M','U','X'] if a['arm']=='R0' else ['M','R','U','X']),'flow_order_'+a['attempt_id'])
    for cls,n in a['planned_counts'].items():check((int(fs[cls].get('number')) if cls in fs else 0)==n,'count:'+a['attempt_id']+cls)
    common=[ET.tostring(fs[c]) for c in ['M','U','X']]
    if flow_common:check(common==next(iter(flow_common.values())),'common_flows_exact_'+a['attempt_id'])
    flow_common[a['attempt_id']]=common
    check(cfg.find('random_number/seed').get('value')==str(a['seed']),'seed_'+a['attempt_id'])
    check(cfg.find('input/net-file').get('value')==manifest['compiled_network']['path'],'network_future_path_'+a['attempt_id'])
    check(not Path(cfg.find('input/net-file').get('value')).exists(),'no_compiled_network_'+a['attempt_id'])
    check(cfg.find('input/additional-files').get('value').endswith('NOT_MATERIALIZED'),'disabled_template_'+a['attempt_id'])
    check(len(add.findall('inductionLoop'))==9 and len(add.findall('laneAreaDetector'))==2,'detector_counts_'+a['attempt_id'])
    check(len({x.get('id') for x in add if x.get('id')})==11,'unique_detector_ids_'+a['attempt_id'])
    check((ad/'scenario.add.xml.template').read_text().count('PENDING_COMPILED_RAMP_STORAGE_LENGTH')==1,'only_one_additional_pending_field_'+a['attempt_id'])
    r=json.loads((ad/'output_roles.json').read_text());check(len(r['required_xml_roles'])==17,'roles17_'+a['attempt_id'])
    check(len({e['path'] for e in r['required_xml_roles']})==17,'unique_output_paths_'+a['attempt_id'])
    ids=json.loads((ad/'expected_identity_manifest.json').read_text());check(sum(map(len,ids['expected_vehicle_ids'].values()))==sum(a['planned_counts'].values()),'expected_population_'+a['attempt_id'])
    spec_seen.add((a['role'],a['arm'],a['seed']))
check(spec_seen=={('smoke','R720',17),('validation','R0',17),('validation','R720',17),('validation','R0',23),('validation','R720',23)},'exact5planned_attempts')
# Meaningful failure fixtures target dangerous configuration drift.
negative=[]
for name,mut in [('aux0_exit',lambda ns,es,cs:ET.SubElement(cs,'connection',{'from':'merge_section','to':'main_down','fromLane':'0','toLane':'0'})),('wrong_M_target',lambda ns,es,cs:next(c for c in cs if c.get('from')=='main_up').set('toLane','0')),('missing_permission',lambda ns,es,cs:es.find("edge[@id='merge_section']/lane").set('changeRight','passenger')),('wrong_nominal_length',lambda ns,es,cs:ns.find("node[@id='merge_end']").set('x','901')),('wrong_R_shape',lambda ns,es,cs:es.find("edge[@id='ramp_accel']").set('shape','500,-15 550,-5'))]:
    ns,es,cs=copy.deepcopy(nodes),copy.deepcopy(edges),copy.deepcopy(cons);mut(ns,es,cs)
    try:topology_validate(ns,es,cs)
    except (AssertionError,ValueError,AttributeError):negative.append({'case':name,'rejected':True})
    else:raise AssertionError('negative fixture admitted '+name)
reg=json.loads((OUT/'executor_parameter_registration_revision02.json').read_text())
check(reg['launch_eligible'] is False and not any(reg['authorized_starts'].values()),'launch_fail_closed')
save('offline_verification_receipt.json',{'status':'PASS_PREBUILD_ONLY','checks':checks,'check_count':len(checks),'schemas':schema,'schema_summary':{'complete_XML_passed':sum(x['expected_schema_pass'] for x in schema),'intentionally_unfinalized_additional_templates_rejected':sum(not x['expected_schema_pass'] for x in schema)},'negative_fixtures':negative,'new_processes':'xmllint only; no SUMO/netconvert/TraCI/GUI','compiled_network':'not_created_not_verified','simulation_calls':dict(SUMO=0,netconvert=0,TraCI=0,GUI=0),'lxml':'unavailable; no installation; system xmllint used with --nonet','confidence':'High for bounded offline input checks; runtime feasibility unknown'})
print(json.dumps({'status':'PASS_PREBUILD_ONLY','checks':len(checks),'schema_calls':len(schema),'negative_cases':len(negative)}))
