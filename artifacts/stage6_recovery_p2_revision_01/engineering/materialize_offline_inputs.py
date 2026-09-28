"""P2 offline input materialization. No simulator or netconvert invocation exists."""
from pathlib import Path
import csv,hashlib,json,plistlib,shutil,xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
P1=ROOT/'data/processed/stage6_obstacle_20260913_v1/recovery_candidate_design_revision_01'
TABLE=ROOT/'results/tables/stage6_recovery_candidate_revision_01/engineering'
OLD=ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused'
FRAME=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0')
SUMO_HOME=FRAME/'EclipseSUMO/share/sumo'
XSD=SUMO_HOME/'data/xsd'
PENDING='PENDING_COMPILED_RAMP_STORAGE_LENGTH'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def save(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
def xml(p,root):
    ET.indent(root,space='  ')
    with p.open('xb') as f:f.write(ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n')
def rows(name):return list(csv.DictReader((TABLE/name).open()))
auth=json.loads((P1/'p2_authorization.json').read_text())
assert 'isolated input materialization' in auth['authorized_now']
reg=json.loads((P1/'p1_registration_draft.json').read_text())
assert len(reg['design_fields'])==39
for b in reg['bindings']:
    p=ROOT/b['path'];assert sha(p)==b['sha256']
inst=json.loads((P1/'engineering/instrumentation_and_tls_supplement.json').read_text())
networkdir=OUT/'network_inputs';networkdir.mkdir()
nodes=ET.Element('nodes')
for r in rows('candidate_nodes.csv'):
    a={k:r[k] for k in ['id','x','y','type']}
    if r['tl']:a['tl']=r['tl']
    ET.SubElement(nodes,'node',a)
xml(networkdir/'candidate.nod.xml',nodes)
edges=ET.Element('edges')
lane_rows=rows('candidate_lanes.csv')
for r in rows('candidate_edges.csv'):
    a={'id':r['edge_id'],'from':r['from_node'],'to':r['to_node'],'numLanes':r['lanes'],'priority':r['priority'],'speed':r['speed_m_s'],'width':r['width_m'],'spreadType':r['spreadType'],'shape':r['reference_shape_original_coordinates']}
    e=ET.SubElement(edges,'edge',a)
    for l in lane_rows:
        if l['edge_id']==r['edge_id'] and l['changeRight']!='not_set_default':ET.SubElement(e,'lane',{'index':l['lane_index'],'changeRight':l['changeRight']})
xml(networkdir/'candidate.edg.xml',edges)
cons=ET.Element('connections')
for r in rows('candidate_connections.csv'):ET.SubElement(cons,'connection',{k:r[k] for k in ['from','to','fromLane','toLane']})
xml(networkdir/'candidate.con.xml',cons)
with (networkdir/'candidate.tll.xml').open('xb') as f:f.write((OLD/'scenario.tll.xml').read_bytes())
build_output=OUT/'build_attempts/BUILD01/network.net.xml'
netcfg=ET.Element('configuration')
for sec,vals in [('input',{'node-files':str(networkdir/'candidate.nod.xml'),'edge-files':str(networkdir/'candidate.edg.xml'),'connection-files':str(networkdir/'candidate.con.xml'),'tllogic-files':str(networkdir/'candidate.tll.xml')}),('output',{'output-file':str(build_output)}),('junctions',{'no-turnarounds':'true','junctions.corner-detail':'5'})]:
    s=ET.SubElement(netcfg,sec)
    for k,v in vals.items():ET.SubElement(s,k,{'value':v})
xml(networkdir/'candidate.netccfg',netcfg)
route_table=rows('candidate_routes.csv')
specs=[{'logical_run_id':'P1B_SMOKE_R720_S17','arm':'R720','seed':17,'role':'smoke','planned_counts':{'M':1333,'R':300,'U':150,'X':75}}]+[{**r,'role':'validation'} for r in reg['logical_validation_matrix']]
attempts=[]
for spec in specs:
    aid=spec['logical_run_id']+'_attempt1';ad=OUT/'attempts'/aid;ad.mkdir(parents=True)
    od=ad/'outputs' # reserved path only; no output or fake archive created
    demand=ET.Element('routes');ET.SubElement(demand,'vType',{'id':'technical_passenger','vClass':'passenger'})
    for r in route_table:ET.SubElement(demand,'route',{'id':r['class']+'_route','edges':r['route']})
    for cls in ['M','R','U','X']:
        number=spec['planned_counts'][cls]
        if number==0:continue
        rr=next(r for r in route_table if r['class']==cls)
        ET.SubElement(demand,'flow',{'id':cls+'_flow','type':'technical_passenger','route':cls+'_route','begin':'0','end':'1500','number':str(number),'departPos':rr['departPos'],'departLane':rr['departLane'],'departSpeed':rr['departSpeed']})
    xml(ad/'demand.rou.xml',demand)
    add=ET.Element('additional');roles=[]
    for e in inst['E2']:
        attrs={'id':e['id'],'lane':e['lane'],'pos':'0','endPos':str(e['endPos']) if isinstance(e['endPos'],float) else PENDING,'period':'30','timeThreshold':'1','speedThreshold':str(5/3.6),'jamThreshold':'10','friendlyPos':'false','vTypes':'','nextEdges':'','file':str(od/(e['id']+'.xml'))}
        ET.SubElement(add,'laneAreaDetector',attrs)
        roles.append({'role':e['id']+'.xml','path':attrs['file'],'root':'detector','kind':'E2','detector_id':e['id'],'lane':e['lane'],'pos':0,'endPos':attrs['endPos'],'period_s':30})
    for e in inst['E1']:
        attrs={'id':e['id'],'lane':e['lane_design_id'],'pos':str(e['pos_m']),'period':'30','length':'0','friendlyPos':'false','vTypes':'','nextEdges':'','file':str(od/(e['id']+'.xml'))}
        ET.SubElement(add,'inductionLoop',attrs)
        roles.append({'role':e['id']+'.xml','path':attrs['file'],'root':'detector','kind':'E1','detector_id':e['id'],'lane':e['lane_design_id'],'pos':int(e['pos_m']),'period_s':30})
    ET.SubElement(add,'timedEvent',{'type':'SaveTLSStates','source':'urban_tls','dest':str(od/'tls_states.xml')})
    xml(ad/'scenario.add.xml.template',add)
    cfg=ET.Element('configuration')
    sections={'input':{'net-file':str(build_output),'route-files':str(ad/'demand.rou.xml'),'additional-files':str(ad/'scenario.add.xml.NOT_MATERIALIZED')},'time':{'begin':'0','end':'2700','step-length':'1'},'processing':{'time-to-teleport':'-1','collision.action':'warn','collision.check-junctions':'true','extrapolate-departpos':'false'},'output':{'fcd-output':str(od/'fcd.xml'),'queue-output':str(od/'queues.xml'),'summary-output':str(od/'sumo_summary.xml'),'tripinfo-output':str(od/'tripinfo.xml'),'vehroute-output':str(od/'vehroute.xml'),'tripinfo-output.write-unfinished':'true','vehroute-output.write-unfinished':'true','precision':'2'},'random_number':{'seed':str(spec['seed'])},'report':{'log':str(od/'sumo.log'),'error-log':str(od/'sumo_error.log'),'no-step-log':'true'}}
    for sec,vals in sections.items():
        s=ET.SubElement(cfg,sec)
        for k,v in vals.items():ET.SubElement(s,k,{'value':v})
    xml(ad/'scenario.sumocfg.template',cfg)
    for n,r in [('fcd.xml','fcd-export'),('queues.xml','queue-export'),('sumo_summary.xml','summary'),('tripinfo.xml','tripinfos'),('vehroute.xml','routes'),('tls_states.xml','tlsStates')]:roles.append({'role':n,'path':str(od/n),'root':r,'kind':'trajectory_or_status'})
    assert len(roles)==17 and len({r['role'] for r in roles})==17
    save(ad/'output_roles.json',{'status':'pending_execution','required_xml_roles':roles,'required_role_count':17,'zero_expected_R':'R0 permits no R records, never missing role','internal_fcd':'P2 smoke must verify all actual lanes including internals','full_time_contract':'FCD/TLS/summary/queue expected labels0..2699; detector0..2700 intervals; empty traffic is not missing frames'})
    ids={cls:[f'{cls}_flow.{i}' for i in range(n)] for cls,n in spec['planned_counts'].items()}
    save(ad/'expected_identity_manifest.json',{'logical_run_id':spec['logical_run_id'],'attempt_id':aid,'role':spec['role'],'seed':spec['seed'],'arm':spec['arm'],'planned_counts':spec['planned_counts'],'expected_vehicle_ids':ids,'source':'number-flow identity contract; planned departure schedule not independently reconstructed','no_runtime_result':True})
    attempts.append({**spec,'attempt_id':aid,'input_files':[bind(ad/n) for n in ['demand.rou.xml','scenario.add.xml.template','scenario.sumocfg.template','output_roles.json','expected_identity_manifest.json']],'output_root':str(od),'launch_eligible':False,'network':{'path':str(build_output),'sha256':None,'status':'pending_separately_approved_build'},'pending_fields':[PENDING,'compiled_network_hash','final_additional_path','compiled_acceptance','final_runtime_input_hashes','SUMO_launch_budget_and_approval']})
info=FRAME/'Resources/Info.plist';version=plistlib.loads(info.read_bytes())['CFBundleShortVersionString']
binary={n:{**bind(FRAME/'EclipseSUMO/bin'/n),'version':version,'version_provenance':'framework Info.plist (binary not invoked)'} for n in ['netconvert','sumo']}
schemas={}
def schema_collect(p):
    if str(p) in schemas:return
    schemas[str(p)]=bind(p)
    for e in ET.parse(p).getroot():
        if e.tag.endswith(('include','import','redefine')) and e.get('schemaLocation'):
            dep=(p.parent/e.get('schemaLocation')).resolve();assert dep.is_relative_to(XSD);schema_collect(dep)
for n in ['nodes_file.xsd','edges_file.xsd','connections_file.xsd','tllogic_file.xsd','netconvertConfiguration.xsd','routes_file.xsd','sumoConfiguration.xsd','additional_file.xsd']:schema_collect(XSD/n)
save(OUT/'environment_binding.json',{'binary':binary,'framework_info':bind(info),'SUMO_HOME':str(SUMO_HOME),'schema_files':list(schemas.values()),'no_binary_invocations':True,'version_limit':'Package metadata identifies1.26.0; no new --version process call; compare binary SHA to prior executed1.26.0 receipt','python':{'executable':str(ROOT/'.venv/bin/python'),'use':'XML materialization and offline checks only'},'xmllint':bind(Path('/usr/bin/xmllint'))})
save(OUT/'output_role_contract.json',{'status':'prebuild_only','role_count':17,'attempts':[{'attempt_id':a['attempt_id'],'logical_run_id':a['logical_run_id'],'output_roles':bind(Path(a['output_root']).parent/'output_roles.json'),'expected_identities':bind(Path(a['output_root']).parent/'expected_identity_manifest.json')} for a in attempts],'scientific_contract':bind(P1/'data/measurement_contract_revision04.md'),'field_registry':bind(ROOT/'results/tables/stage6_recovery_candidate_revision_01/data/measurement_fields_revision04.csv')})
save(OUT/'executor_parameter_registration.json',{'status':'offline_registration_disabled','launch_eligible':False,'authorized_starts':dict(netconvert=0,SUMO=0,TraCI=0,GUI=0),'candidate':'B_shared_edge_auxiliary_300m','attempts':attempts,'sequence':[a['attempt_id'] for a in attempts],'process_environment':{'SUMO_HOME':str(SUMO_HOME),'restore_after_each_run':True},'retry':'at_most_one_global_transient_environment_process_failure_only; exact_attempt_expansion_pending_launch_card','stop_rules':{'collision_teleport':'stop_complete_evidence_but_comparison_unsuitable_physical_event','evidence_error':'stop_evidence_incomplete','valid_negative':'continue_registered_second_seed','emergency_braking_alone':'record_not_auto_stop'},'no_executor_implemented':True,'build_approval':'required_before_netconvert','SUMO_approval':'required_after_compiled_acceptance_and_exact_launch_card','pending_budgets':['build_counts_wallclock_disk','SUMO_counts_wallclock_disk','cumulative_project_reconciliation']})
source_bindings=[bind(P1/n) for n in ['p2_authorization.json','p1_registration_draft.json','p1_scientific_review.json','data/measurement_contract_revision04.md','engineering/engineering_handoff_manifest.json','engineering/instrumentation_and_tls_supplement.json']]+[bind(TABLE/n) for n in ['candidate_nodes.csv','candidate_edges.csv','candidate_lanes.csv','candidate_connections.csv','candidate_routes.csv','candidate_new_detectors.csv','p2_build_verification_checklist.csv']]+[bind(OLD/n) for n in ['network.net.xml','scenario.tll.xml']]
save(OUT/'input_manifest.json',{'status':'MATERIALIZED_PREBUILD_NOT_LAUNCHABLE','source_bindings':source_bindings,'network_inputs':[bind(p) for p in sorted(networkdir.iterdir())],'attempts':attempts,'environment':bind(OUT/'environment_binding.json'),'output_contract':bind(OUT/'output_role_contract.json'),'registration':bind(OUT/'executor_parameter_registration.json'),'script':bind(Path(__file__)),'compiled_network':{'path':str(build_output),'exists':False,'sha256':None},'calls':dict(netconvert=0,SUMO=0,TraCI=0,GUI=0)})
print(json.dumps({'status':'PREBUILD_READY_FOR_OFFLINE_CHECKS','attempts':len(attempts),'network_inputs':5,'roles_each':17,'schema_dependencies':len(schemas)}))
