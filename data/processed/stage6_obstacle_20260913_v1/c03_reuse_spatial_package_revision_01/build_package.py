"""Read-only source inspection; writes exclusive C03 derived artifacts only."""
from pathlib import Path
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m

OUT = Path(__file__).resolve().parent
B = o.BATCH
inputs = {}
checks = []

def bound(path):
    b = o.bind(path)
    inputs[b['path']] = b
    return b

def check(name, truth, evidence=''):
    checks.append({'check': name, 'passed': bool(truth), 'evidence': evidence})
    o.require(bool(truth), name)

def write_json(name, data):
    with (OUT/name).open('xb') as f:
        f.write(o.encode(data))

def write_csv(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def semantic(root):
    return hashlib.sha256(ET.tostring(root)).hexdigest()

card = o.load_card()
bound(o.CARD)
o.verify_candidate()
bound(o.CANDIDATE/'source_manifest.json')
for name in o.SOURCE_NAMES:
    bound(o.CANDIDATE/name)
bound(Path(o.__file__))
bound(Path(m.__file__))
bound(B/'c02_engineering_revision_03/engineering_receipt.json')
approval_sources = []
for source in (o.ROOT/'docs/WORKLOG.md', o.ROOT/'docs/PROJECT_STATE.md', B/'ledger.json'):
    origin = o.bind(source)
    snapshot = OUT/(source.name+'.snapshot')
    with snapshot.open('xb') as f:
        f.write(source.read_bytes())
    approval_sources.append({'origin_at_capture': origin, 'preserved_snapshot': bound(snapshot)})
worklog = (OUT/'WORKLOG.md.snapshot').read_text()
check('user approval quote preserved', 'Stage 6 B registration accepted; C00–C02 authorized' in worklog and '批准，请继续' in worklog)
ledger = o.read_json(OUT/'ledger.json.snapshot')
check('ledger SG6-L passed', any(x['step_id']=='S6-C02' and x['status']=='SG6-L_passed' for x in ledger['steps']))
check('ledger current counters all zero', all(x==0 for x in ledger['simulation_invocations'].values()))

registry_binding = next(x for x in card['artifact_bindings'] if Path(x['path']).name=='source_registry.csv')
registry_path = o.verify_binding(registry_binding)
bound(registry_path)
registry = list(csv.DictReader(registry_path.open()))
selected = next(x for x in registry if x['run_id']=='C17')
archive = Path(selected['archive_path'])
net_path = archive/'network.net.xml'
net_info = o.verify_network(net_path, selected['network_sha256'])
bound(net_path)
net = ET.parse(net_path).getroot()
lanes = {e.get('id'): e for e in net.findall('.//lane')}
edges = {e.get('id'): e for e in net.findall('edge')}
connections = net.findall('connection')
check('all nineteen lanes partitioned', set(lanes)==set(m.LANE_CLASS) and set(lanes)==set().union(*m.REGIONS.values()))
source_map_path = o.verify_binding({'path':selected['source_map_path'],'sha256':selected['source_map_sha256']})
bound(source_map_path)
source_map = o.read_json(source_map_path)
mapped = {str(o.ROOT/x['archive_relative_path']): x for x in source_map['file_map']}
chain = []
for name in ('scenario.nod.xml','scenario.edg.xml','scenario.con.xml','scenario.tll.xml','network.net.xml','summary.json','netconvert.stdout.log','netconvert.stderr.log'):
    path = archive/name
    entry = mapped[str(path)]
    o.verify_binding({'path':str(path),'sha256':entry['sha256']})
    chain.append({'role':name,'archived':bound(path),'original_absolute_path':entry['original_absolute_path']})
summary = o.read_json(archive/'summary.json')
build_header = ET.fromstring(re.search(r'<netconvertConfiguration\b[^>]*>.*?</netconvertConfiguration>',net_path.read_text(),re.S).group())
for tag, name in (('node-files','scenario.nod.xml'),('edge-files','scenario.edg.xml'),('connection-files','scenario.con.xml'),('tllogic-files','scenario.tll.xml'),('output-file','network.net.xml')):
    expected = mapped[str(archive/name)]['original_absolute_path']
    check('original build header '+tag,build_header.find('.//'+tag).get('value')==expected)
    check('original build argv '+tag,summary['netconvert_command'][summary['netconvert_command'].index('--'+tag)+1]==expected)
    if name!='network.net.xml':
        check('candidate original topology source '+name,(archive/name).read_bytes()==(o.CANDIDATE/name).read_bytes())
check('original build fixed flags',build_header.find('.//no-turnarounds').get('value')=='true' and build_header.find('.//junctions.corner-detail').get('value')=='5')
check('archived netconvert error log empty',(archive/'netconvert.stderr.log').stat().st_size==0)

diffs=[]
materials=[]
for row in card['logical_runs']:
    if row['version']=='V0':
        physical = next(x for x in registry if x['run_id']==row['parent_source_id'])
        path = Path(physical['archive_path'])/'network.net.xml'
        o.verify_binding({'path':str(path),'sha256':physical['network_sha256']})
    else:
        mp=B/'c01_materializations_revision_03'/(row['run_id']+'_attempt1')/'materialization_manifest.json'
        verification=o.verify_materialization(mp,B)
        material=o.read_json(mp)
        materials.append({'run_id':row['run_id'],'manifest':bound(mp),'verification':verification})
        for b in material['files'].values():
            bound(o.verify_binding(b))
        path=o.verify_binding(material['network'])
        check('unique compiled reuse '+row['run_id'],path==net_path)
    bound(path)
    candidate_net=ET.parse(path).getroot()
    check('semantic identity '+row['run_id'],semantic(candidate_net)==semantic(net))
    for category,xpath in [('root','.'),('edges_and_lanes','edge'),('connections','connection'),('junction_requests','junction'),('TLS_program','tlLogic'),('location','location')]:
        left=net if xpath=='.' else net.findall(xpath)
        right=candidate_net if xpath=='.' else candidate_net.findall(xpath)
        payload=lambda x: ET.tostring(x) if isinstance(x,ET.Element) else b''.join(ET.tostring(v) for v in x)
        equal=payload(left)==payload(right)
        check('compiled '+row['run_id']+' '+category,equal)
        diffs.append({'logical_run_id':row['run_id'],'version':row['version'],'comparison_category':category,'reference_path':str(net_path),'compared_path':str(path),'reference_byte_sha256':o.sha256(net_path),'compared_byte_sha256':o.sha256(path),'reference_semantic_sha256':semantic(net),'compared_semantic_sha256':semantic(candidate_net),'semantic_equal':equal,'unexplained_difference_count':0,'byte_difference_explanation':'same file' if path==net_path else 'Historical XML comment build timestamp/runtime paths differ; parsed full net tree is identical.'})
write_csv('compiled_semantic_diff.csv',diffs)

observations=[]
def obs(kind,identity,source,locator,**fields):
    observations.append({'kind':kind,'id':identity,'source_path':str(source),'source_sha256':o.sha256(source),'locator':locator,'verification':'static_verified_runtime_V1_pending',**fields})

for edge in edges.values():
    for lane in edge.findall('lane'):
        lid=lane.get('id')
        region=next(r for r,ls in m.REGIONS.items() if lid in ls)
        obs('lane',lid,net_path,f"edge[@id='{edge.get('id')}']/lane[@id='{lid}']",lane=lid,edge=edge.get('id'),internal=edge.get('function')=='internal',priority=edge.get('priority','inherited_connection'),begin_m=0,end_m=lane.get('length'),classes=m.LANE_CLASS[lid],final_region=region,coverage='FCD 1Hz labels; unique final region; lane-position coordinates',details=json.dumps(dict(lane.attrib),sort_keys=True))
for index,c in enumerate(connections):
    via=c.get('via','')
    if via:
        check('via exists '+str(index),via in lanes)
        via_edge=next(e.get('id') for e in edges.values() if any(l.get('id')==via for l in e.findall('lane')))
        check('via successor continuity '+str(index),any(x.get('from')==via_edge and x.get('to')==c.get('to') and x.get('toLane')==c.get('toLane') for x in connections))
    obs('connection',str(index),net_path,f'connection[{index+1}]',lane=f"{c.get('from')}_{c.get('fromLane')}",via=via,successor=f"{c.get('to')}_{c.get('toLane')}",priority=c.get('state'),tls=c.get('tl',''),tls_link=c.get('linkIndex',''),coverage='compiled connection and via continuity',details=json.dumps(dict(c.attrib),sort_keys=True))
for j in net.findall('junction'):
    obs('junction',j.get('id'),net_path,f"junction[@id='{j.get('id')}']",coverage='junction type/incoming/internal lanes and exact request bitfields',details=json.dumps({'attributes':dict(j.attrib),'requests':[dict(r.attrib) for r in j.findall('request')]},sort_keys=True))
tls=net.find('tlLogic')
for i,phase in enumerate(tls.findall('phase')):
    obs('TLS_phase',str(i),net_path,f"tlLogic[@id='urban_tls']/phase[{i+1}]",tls='urban_tls',coverage='link0 urban_in RU; link1 cross X; saved TLS 1Hz future runtime check',details=json.dumps(dict(phase.attrib),sort_keys=True))
check('TLS links',[c.get('linkIndex') for c in connections if c.get('tl')]=='1 0'.split())
for material in materials:
    add_path=Path(material['manifest']['path']).parent/'scenario.add.xml'
    add=ET.parse(add_path).getroot()
    for detector in add:
        if detector.tag not in ('inductionLoop','laneAreaDetector'):
            continue
        lane=detector.get('lane');length=float(lanes[lane].get('length'));start=float(detector.get('pos'));start=start if start>=0 else length+start
        end=float(detector.get('endPos',start));end=end if end>=0 else length+end
        check(material['run_id']+' detector bounds '+detector.get('id'),0<=start<=end<=length)
        if detector.tag=='laneAreaDetector':
            check(material['run_id']+' E2 exact named lane '+detector.get('id'),start==0 and end==length)
        note='aggregate entered versus contribution populations; no ordinary E1 per-ID guarantee' if detector.tag=='inductionLoop' else 'exact named lane only, no internal successors; FCD covers excluded internal lanes'
        if detector.get('id').startswith('merge_upstream'):
            note+='; V1 1293.87m downstream of p100 and 193.87m downstream of feeder end; V0 origin-insertion contaminated; not feeder inlet or requested-demand rate'
        obs('E1' if detector.tag=='inductionLoop' else 'E2',material['run_id']+':'+detector.get('id'),add_path,f"{detector.tag}[@id='{detector.get('id')}']",lane=lane,begin_m=round(start,8),end_m=round(end,8),period_s=detector.get('period'),coverage=note,details=json.dumps(dict(detector.attrib),sort_keys=True))
for edge,domain,begin,end,classes in [('main_up','V1_feeder',200,1200,'M'),('main_down','V0_V1_common',100,700,'M')]:
    for lane in edges[edge].findall('lane'):
        check('domain contained '+domain+lane.get('id'),0<begin<end<float(lane.get('length')))
        obs('domain',domain+':'+lane.get('id'),o.CANDIDATE/'entry_contract.json',domain,lane=lane.get('id'),begin_m=begin,end_m=end,classes=classes,coverage='FCD lane-position half-open domain and conservative crossing brackets; common is background, not H2 main criterion')
for lane in ('main_up_0','main_up_1'):
    obs('insertion','V1_M:'+lane,o.CANDIDATE/'entry_contract.json','M_departPos_m',lane=lane,begin_m=100,end_m=100,classes='M',coverage='numeric departPos100; extrapolate false; future actual tripinfo/FCD position qualification required; 100m before feeder start')
for group,route in o.ROUTES.items():
    route_edges=route.split();paths=[]
    for a,z in zip(route_edges,route_edges[1:]):
        links=[c for c in connections if c.get('from')==a and c.get('to')==z]
        check('route continuous '+group+':'+a+'->'+z,bool(links))
        paths.append({'from':a,'to':z,'via':[c.get('via') for c in links],'state':[c.get('state') for c in links]})
    obs('route',group,o.CANDIDATE/'entry_contract.json','registered source routes',classes=group,coverage='all ordinary edge pairs and internal via chains compiled; no realized V1 route claimed',details=json.dumps({'edges':route_edges,'connections':paths},sort_keys=True))
write_csv('actual_observation_map.csv',observations)

pending=[
 {'stage':'C04 before SG6-P','item':'V1 executed-output source map and receipt','acceptance':'Bind approved logical run/version/ML-C role/seed/attempt and materialization, binary/argv/compiled/source hashes, actual output role inventory and execution receipt; reject cross-seed/role/path substitution.'},
 {'stage':'C04 before SG6-P','item':'V1 source-map -> analysis -> identity -> pair -> 352/14 integration','acceptance':'Implement actual V1 source adapter; offline end-to-end identity and error fixtures then independent review; current archive entry and real V1 pair remain fail-closed pending_C04_D. Fixed 352 keys/148 required main plus14 required sensitivity, no denominator deletion.'},
 {'stage':'C04 before SG6-P','item':'executor/watchdog/recovery','acceptance':'Implement exact approved argv without hidden build, durable reserved/running/unknown/finished events, aggregate ceilings, timeout/output-size signals and OS recovery; zero-SUMO offline tests before any launch. Current code contains pure decision helpers only.'},
 {'stage':'C04 before SG6-P','item':'exact launch card and user approval','acceptance':'Concrete current source/analysis/binary/network/materialization hashes, budget, order and stop branches; rebind future source changes, preserve old revisions; no simulator authorization from C03.'},
 {'stage':'D smoke and validation','item':'runtime spatial and output evidence','acceptance':'Actual numeric100 insertion and complete feeder path, no fallback/new insertion blocking,19-lane identities/TLS/E1/E2 loading, complete frames/endpoints, anomalies. Static coverage cannot pass runtime behavior or scientific resolution.'},
 {'stage':'C04/D','item':'number-flow exact quantization','acceptance':'Retain registered pending limit until exact implementation evidence; max reported departDelay qualification alone is not a no-blockage proof.'}
]
write_json('pending_launch_chain.json',{'launch_eligible':False,'pending':pending})
write_json('build_receipts.json',{'mode':'reuse_only','planned':0,'actual':0,'netconvert':{'planned':0,'actual':0,'authorization':False},'SUMO':0,'TraCI':0,'GUI':0,'compiled_files_created':0,'selected_unique_network':bound(net_path),'semantic_sha256':semantic(net),'original_source_map':bound(source_map_path),'original_build_input_chain':chain,'original_archived_netconvert_argv_NOT_EXECUTED':summary['netconvert_command'],'original_version_evidence':summary['netconvert_version'],'historical_build_time_is_not_current_execution':True})
write_json('engineering_receipt.json',{'stage':'C03','engineering_result':'PASS','scope':'existing compiled-network reuse and static spatial acceptance only; no rebuild or launch','confidence':'High','launch_eligible':False,'card':bound(o.CARD),'approval_context':approval_sources,'selected_network':bound(net_path),'semantic_sha256':semantic(net),'materializations':materials,'counts':{'unique_reused_network':1,'V0_networks_compared':4,'V1_materializations_compared':4,'semantic_diff_rows':len(diffs),'unexplained_semantic_differences':0,'lanes':len(lanes),'internal_lanes':sum(e.get('function')=='internal' for e in edges.values() for lane in e.findall('lane')),'connections':len(connections),'observation_map_rows':len(observations),'E1_per_materialization':6,'E2_per_materialization':2,'required_static_domains_mapped':4,'checks':len(checks),'passed':len(checks)},'checks':checks,'pending_launch_chain':o.bind(OUT/'pending_launch_chain.json'),'build_receipts':o.bind(OUT/'build_receipts.json'),'simulation_invocations':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'limits':['No current executable or version command invoked. Version evidence is historical archived metadata.','No V1 runtime coverage, source-map integration, executor behavior or scientific result established.','Existing upstream E1 is not a feeder-entry detector and remains invalid as V0 requested inflow.','C03 engineering PASS requires independent data/scientific acceptance before parent closes C03.']})
write_json('manifest.json',{'artifact_kind':'C03_reuse_only_static_spatial_package','launch_eligible':False,'input_bindings':list(inputs.values()),'outputs':[o.bind(p) for p in sorted(OUT.iterdir()) if p.is_file()],'no_source_or_historical_output_modified':True})
print(json.dumps({'receipt':o.bind(OUT/'engineering_receipt.json'),'manifest':o.bind(OUT/'manifest.json'),'checks':len(checks),'observation_rows':len(observations),'semantic_diff_rows':len(diffs)},indent=2))
