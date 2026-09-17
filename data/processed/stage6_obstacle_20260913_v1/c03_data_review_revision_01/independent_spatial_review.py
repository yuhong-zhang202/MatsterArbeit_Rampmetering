"""Independent stdlib XML spatial review, without production/engineering imports."""
import json,csv,hashlib,collections,re
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent;P=B/'c03_reuse_spatial_package_revision_01';ROOT=B.parents[2]
checks=[];hashes={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,yes):
 checks.append({'check':name,'passed':bool(yes)});assert yes,name
def bind(b):
 p=Path(b['path']);p=p if p.is_absolute() else ROOT/p
 check('hash:'+str(p),sha(p)==b['sha256']);hashes[str(p)]=b['sha256'];return p
import xml.etree.ElementTree as E
final=json.loads((P/'final_package_manifest.json').read_text());manifest=json.loads(bind(final['initial_manifest']).read_text());add=json.loads(bind(final['required_addendum']).read_text());eng=json.loads(bind(final['engineering_receipt']).read_text())
for b in manifest['input_bindings']+manifest['outputs']:bind(b)
check('package nonlaunch',final['launch_eligible'] is False and eng['launch_eligible'] is False)
net=bind(eng['selected_network']);root=E.parse(net).getroot();semantic=hashlib.sha256(E.tostring(root)).hexdigest();check('full parsed semantic hash',semantic==eng['semantic_sha256']=='29b7b3350e19462380ba44db1535e7aa426af7f4cb5ba355357f8628060ec635')
lanes={l.get('id'):(edge,l) for edge in root.findall('edge') for l in edge.findall('lane')};con=root.findall('connection');junctions=root.findall('junction');check('19/8/16/10',(len(lanes),sum(e.get('function')=='internal' for e,l in lanes.values()),len(con),len(junctions))==(19,8,16,10))
for i,c in enumerate(con):
 start=c.get('from')+'_'+c.get('fromLane');end=c.get('to')+'_'+c.get('toLane');via=c.get('via');check('connection endpoints'+str(i),start in lanes and end in lanes)
 if via:
  check('connection via lane'+str(i),via in lanes)
  v_edge,v_lane=lanes[via];follow=[x for x in con if x.get('from')==v_edge.get('id') and x.get('fromLane')==v_lane.get('index') and x.get('to')==c.get('to') and x.get('toLane')==c.get('toLane')];check('via successor continuity'+str(i),len(follow)==1)
check('priority M/R',[c.get('state') for c in con if c.get('from')=='main_up']==['M','M'] and [c.get('state') for c in con if c.get('from')=='ramp_accel']==['m'])
check('edge priority',[root.find("edge[@id='"+x+"']").get('priority') for x in ['main_up','ramp_accel']]==['3','2'])
tl=root.find("tlLogic[@id='urban_tls']");check('TLS60s four phases',[(float(x.get('duration')),x.get('state')) for x in tl.findall('phase')]==[(45,'Gr'),(3,'yr'),(9,'rG'),(3,'ry')])
check('TLS links',[(c.get('from'),c.get('linkIndex')) for c in con if c.get('tl')=='urban_tls']==[('cross_in','1'),('urban_in','0')])
# Independent diff checks compare full semantic trees, stronger than partial categories.
with (P/'compiled_semantic_diff.csv').open() as f:diff=list(csv.DictReader(f))
check('48 diff keys',len(diff)==len({(x['logical_run_id'],x['comparison_category']) for x in diff})==48)
for row in diff:
 a=Path(row['reference_path']);b=Path(row['compared_path']);check('diff bytes'+row['logical_run_id']+row['comparison_category'],sha(a)==row['reference_byte_sha256'] and sha(b)==row['compared_byte_sha256'])
 check('diff full XML'+row['logical_run_id']+row['comparison_category'],E.tostring(E.parse(a).getroot())==E.tostring(E.parse(b).getroot()) and row['semantic_equal']=='True' and row['unexplained_difference_count']=='0')
check('diff six categories each8',set(collections.Counter(x['comparison_category'] for x in diff).values())=={8})
# Historical build chain, without invoking netconvert.
build=json.loads(bind(eng['build_receipts']).read_text());check('reuse netconvert planned actual0',build['mode']=='reuse_only' and build['netconvert']=={'actual':0,'authorization':False,'planned':0} and build['compiled_files_created']==0)
source_map=json.loads(bind(build['original_source_map']).read_text());mapped={x['original_absolute_path']:x for x in source_map['file_map']}
for x in build['original_build_input_chain']:
 p=bind(x['archived']);check('original map role '+x['role'],x['original_absolute_path'] in mapped and mapped[x['original_absolute_path']]['sha256']==sha(p))
 if x['role'] in ['scenario.nod.xml','scenario.edg.xml','scenario.con.xml','scenario.tll.xml']:check('unchanged build source '+x['role'],p.read_bytes()==(ROOT/'config/scenarios/stage6_h2_entry_v1'/x['role']).read_bytes())
summary=json.loads((net.parent/'summary.json').read_text());check('historical argv exact',summary['netconvert_command']==build['original_archived_netconvert_argv_NOT_EXECUTED'])
# Resolve every corrected source locator before comparing actual attributes.
with (P/'actual_observation_map.csv').open() as f:obs=list(csv.DictReader(f))
check('91 map unique',len(obs)==len({(x['kind'],x['id']) for x in obs})==91)
check('map denominator composition',collections.Counter(x['kind'] for x in obs)=={'E1':24,'lane':19,'connection':16,'junction':10,'E2':8,'TLS_phase':4,'domain':4,'route':4,'insertion':2})
fix={(x['kind'],x['id']):x for x in add['corrected_source_locators']};check('8 corrected locators',len(fix)==8)
resolved=[]
for row in obs:
 k=(row['kind'],row['id']);f=fix.get(k);p=bind(f['correct_source'] if f else {'path':row['source_path'],'sha256':row['source_sha256']});loc=f['locator'] if f else row['locator'];kind=row['kind']
 if p.suffix=='.json':
  doc=json.loads(p.read_text());val=doc[loc.lstrip('/')]
  expect=[float(row['begin_m']),float(row['end_m'])] if kind=='domain' else float(row['begin_m']);check('JSON locator '+str(k),val==expect)
 else:
  xroot=E.parse(p).getroot();elementloc,sep,attr=loc.partition('/@');found=xroot.findall(elementloc);check('XML unique locator '+str(k),len(found)==1);e=found[0]
  if kind=='route':check('route locator value '+row['id'],e.get(attr).split()==json.loads(row['details'])['edges'])
  elif kind=='junction':check('junction exact requests '+row['id'],{'attributes':dict(e.attrib),'requests':[dict(x.attrib) for x in e.findall('request')]}==json.loads(row['details']))
  else:check('element attrs '+str(k),dict(e.attrib)==json.loads(row['details']))
  if kind=='lane':check('lane length '+row['id'],float(row['end_m'])==float(e.get('length')) and row['edge']==lanes[row['id']][0].get('id'))
  if kind in ['E1','E2']:
   lane=e.get('lane');length=float(lanes[lane][1].get('length'));begin=float(e.get('pos'));begin=length+begin if begin<0 else begin;end=begin if kind=='E1' else float(e.get('endPos'));check('detector space '+row['id'],0<=begin<=end<=length and begin==float(row['begin_m']) and end==float(row['end_m']) and e.get('period')==row['period_s']=='30')
 resolved.append({'kind':kind,'id':row['id'],'path':str(p),'locator':loc,'verified':True})
 check('static status explicit '+str(k),row['verification']=='static_verified_runtime_V1_pending')
for mat in eng['materializations']:
 p=bind(mat['manifest']);m=json.loads(p.read_text());cfg=E.parse(p.parent/'scenario.sumocfg').getroot();check('single reused binary network '+mat['run_id'],Path(cfg.find('input/net-file').get('value'))==net and m['network']['sha256']==sha(net))
 check('runtime p guard '+mat['run_id'],cfg.find('processing/extrapolate-departpos').get('value')=='false')
 addroot=E.parse(p.parent/'scenario.add.xml').getroot();check('6E1/2E2 '+mat['run_id'],len(addroot.findall('inductionLoop'))==6 and len(addroot.findall('laneAreaDetector'))==2)
 flows={x.get('id'):x for x in E.parse(p.parent/'demand.rou.xml').getroot().findall('flow')};check('only M p100 '+mat['run_id'],flows['M_flow'].get('departPos')=='100' and all(flows[g+'_flow'].get('departPos')=='last' for g in ['R','U','X']))
# Derive route lane sets from ordinary route edges plus selected compiled via chains.
route_sets={};internal_sequences={}
for row in [r for r in obs if r['kind']=='route']:
 path=bind(fix[(row['kind'],row['id'])]['correct_source']);edges=E.parse(path).getroot().find("route[@id='"+row['id']+"_route']").get('edges').split();s=set();internals=[]
 for edge in edges:s.update(l.get('id') for l in root.find("edge[@id='"+edge+"']").findall('lane'))
 for a,b in zip(edges,edges[1:]):
  cc=[c for c in con if c.get('from')==a and c.get('to')==b];check('route adjacency '+row['id']+a+b,bool(cc))
  vv=[c.get('via') for c in cc];s.update(vv);internals+=vv
 route_sets[row['id']]=s;internal_sequences[row['id']]=internals
 check('derived lane set '+row['id'],s==set(add['route_lane_sets'][row['id']]))
check('19 lane route union',set.union(*route_sets.values())==set(lanes))
check('R enters main_down0',[c.get('toLane') for c in con if c.get('from')=='ramp_accel' and c.get('to')=='main_down']==['0'])
check('M R downstream overlap',route_sets['M']&route_sets['R']=={'main_down_0','main_down_1'})
check('RU common prefix',route_sets['R']&route_sets['U']=={'urban_in_0',':urban_tls_0_0','shared_approach_0'})
check('internal sequence R',internal_sequences['R']==add['route_partition_checks']['R_internal_sequence'])
for lane in ['main_up_0','main_up_1']:check('p100 feeder E1 relation '+lane,100<200<1200<float(lanes[lane][1].get('length'))-1 and abs((float(lanes[lane][1].get('length'))-1)-1393.87)<1e-8)
for lane in ['main_down_0','main_down_1']:check('common inside edge '+lane,0<=100<700<float(lanes[lane][1].get('length')))
check('engineering149 checks',len(eng['checks'])==149 and sum(c['passed'] for c in eng['checks'])==149)
check('no tool authorization',eng['simulation_invocations']=={'GUI':0,'SUMO':0,'TraCI':0,'netconvert':0} and json.loads((P/'pending_launch_chain.json').read_text())['launch_eligible'] is False)
with (D/'resolved_observation_locators.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=resolved[0]);w.writeheader();w.writerows(resolved)
receipt={'status':'PASS_static_reuse_data_review','confidence':'High_static_XML_only','open_findings':{'Blocker':0,'Major':0,'Minor':0},'checks':checks,'denominators':{'lanes':19,'internal_lanes':8,'connections':16,'map_rows':91,'resolved_map_rows':len(resolved),'semantic_diff_rows':48,'engineering_check_rows':149,'materializations':4,'E1_each':6,'E2_each':2,'new_compiled_files':0,'netconvert_planned':0,'netconvert_actual':0},'selected_network':{'path':str(net),'sha256':sha(net),'semantic_sha256':semantic},'reviewed_package_final_manifest':{'path':str(P/'final_package_manifest.json'),'sha256':sha(P/'final_package_manifest.json')},'all_bound_inputs':hashes,'limits':['Requires final_package_manifest and mandatory locator/partition addendum together; initial map alone contains superseded locator shorthand','Potential downstream R lane set includes both lanes; immediate ramp connection enters lane0 only','Static FCD/detector configuration and path coverage do not prove V1 runtime vehicle coverage or behavior','No compiled network rebuild or simulator was run','Runtime source/executor/observation/scientific acceptance remain pending per launch chain'],'oracle':'independent standard-library XML traversal, full-tree comparison, source locator resolution and route-set derivation; no production or engineering import','SUMO':0,'netconvert':0,'TraCI':0,'GUI':0}
with (D/'independent_spatial_receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
print('PASS checks',len(checks),'hash',sha(D/'independent_spatial_receipt.json'))
