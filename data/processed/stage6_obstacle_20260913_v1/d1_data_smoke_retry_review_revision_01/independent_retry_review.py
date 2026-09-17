import json,hashlib,math,re
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path.cwd();B=ROOT/'data/processed/stage6_obstacle_20260913_v1';D=B/'d1_data_smoke_retry_review_revision_01';G=B/'d1_engineering_smoke_retry_revision_01';C=B/'d1_engineering_smoke_revision_01';A=B/'c04_launch_preparation_revision_03/attempts/S6_V1_ML_S17_attempt2'
def js(p):return json.loads(Path(p).read_text())
def bind(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
def verify(b):ck('hash:'+b['path'],bind(b['path'])['sha256']==b['sha256'])
def save(name,data):
 with (D/name).open('x') as f:json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
def num(raw):
 v=float(raw);assert math.isfinite(v);return v
manifest=js(G/'retry_final_manifest.json')
for key in ('archive_files','evidence_files','budget_events'):
 for binding in manifest[key]:verify(binding)
eng=js(G/'smoke_technical_receipt.json');r=js(A/'execution_receipt.json');mat=js(A/'materialization_manifest.json');card=js(C/'approved_launch_card.json');source=js(A/'executed_source_map.json')
ck('source_map_match',all(r[k]==v for k,v in source.items()))
ck('identity',r['attempt_id']=='S6_V1_ML_S17_attempt2' and r['run_id']=='S6_V1_ML_S17' and r['role']=='retry' and r['version']=='V1' and r['condition']=='ML' and str(r['seed'])=='17' and r['evidence_scope']=='real_executed_output')
for field in ('binary','network','source_manifest'):
 ck('mat:'+field,r[field]==mat[field]);verify(r[field])
ck('launch',r['launch_card']==bind(C/'approved_launch_card.json') and r['argv']==card['retry_options'][0]['argv'])
for binding in r['files'].values():verify(binding)
for binding in r['output_bindings'].values():verify(binding)
header=(A/'outputs/tripinfo.xml').read_text()[:65536];config=E.fromstring(re.findall(r'<sumoConfiguration\b[^>]*>.*?</sumoConfiguration>',header,re.S)[0])
for tag,value in [('seed','17'),('end','2700'),('step-length','1'),('net-file',mat['network']['path']),('route-files',mat['files']['demand.rou.xml']['path'])]:ck('runtime:'+tag,config.find('.//'+tag).get('value')==value)
network=E.parse(mat['network']['path']).getroot();lanes={n.get('id'):num(n.get('length')) for n in network.findall('.//lane')}
expected={f'{g}_flow.{i}' for g,n in {'M':1083,'R':300,'U':150,'X':75}.items() for i in range(n)}
trips={}
for el in E.parse(A/'outputs/tripinfo.xml').getroot():
 vid=el.get('id');assert vid in expected and vid not in trips
 trips[vid]={k:num(el.get(k)) for k in ('depart','arrival','departDelay','departPos')};trips[vid]['departLane']=el.get('departLane')
ck('trip_IDs',set(trips)==expected)
trajectories={v:[] for v in expected};frames=[];samples=0
for event,el in E.iterparse(A/'outputs/fcd.xml',events=('end',)):
 if el.tag!='timestep':continue
 t=num(el.get('time'));assert t==len(frames);frames.append(t);seen=set()
 for vehicle in el:
  vid=vehicle.get('id');lane=vehicle.get('lane');pos=num(vehicle.get('pos'));speed=num(vehicle.get('speed'));assert vid in expected and vid not in seen and lane in lanes and 0<=pos<=lanes[lane]+.02 and speed>=0
  seen.add(vid);trajectories[vid].append((int(t),lane,pos));samples+=1
 el.clear()
ck('FCD_grid',frames==list(range(2700)))
for vid,tr in trips.items():
 labels=[z[0] for z in trajectories[vid]];ck('identity_continuity:'+vid,labels==list(range(math.ceil(tr['depart']),math.ceil(tr['arrival']))))
roots={'fcd.xml':('fcd-export','timestep',2700),'queues.xml':('queue-export','data',2700),'sumo_summary.xml':('summary','step',2700),'tls_states.xml':('tlsStates','tlsState',2700),'tripinfo.xml':('tripinfos','tripinfo',1608),'vehroute.xml':('routes','vehicle',1608)}
for n in r['output_bindings']:
 if '_e1_' in n or '_e2.' in n:roots[n]=('detector','interval',90)
roles={}
for name,(root,child,count) in roots.items():
 tree=E.parse(A/'outputs'/name).getroot();ck('XML:'+name,tree.tag==root and len(tree.findall(child))==count and len(tree)==count);roles[name]={'root':root,'records':count}
 if root=='detector':
  for i,el in enumerate(tree):
   assert el.get('id')==name[:-4] and num(el.get('begin'))==i*30 and num(el.get('end'))==(i+1)*30
   if '_e1_' in name:
    for field in ('nVehContrib','nVehEntered'):assert num(el.get(field))>=0 and num(el.get(field)).is_integer()
    assert num(el.get('speed'))>=0 or (num(el.get('speed'))==-1 and num(el.get('nVehContrib'))==0)
ck('14roles',len(roles)==14)
for i,el in enumerate(E.parse(A/'outputs/tls_states.xml').getroot()):
 phase=0 if i%60<45 else 1 if i%60<48 else 2 if i%60<57 else 3
 assert num(el.get('time'))==i and el.get('state')==['Gr','yr','rG','ry'][phase] and int(el.get('phase'))==phase and el.get('id')=='urban_tls'
links={el.get('linkIndex'):(el.get('from'),el.get('to')) for el in network.findall('connection') if el.get('tl')=='urban_tls'};ck('TLS_links',links=={'0':('urban_in','shared_approach'),'1':('cross_in','cross_out')})
def crossing(ss,edge,p):
 lane_set={edge+'_0',edge+'_1'}
 for before,after in zip(ss,ss[1:]):
  if before[1] in lane_set and after[1] in lane_set and before[2]<p<=after[2]:return [before[0],after[0]]
 return None
records=[]
for vid in sorted(expected):
 tr=trips[vid];ss=trajectories[vid];row={'vehicle_id':vid,'group':vid[0],**tr,'entered':tr['depart']>=0,'arrived':tr['arrival']>=0,'sample_count':len(ss),'last_confirmed_label':ss[-1][0] if ss else None,'endpoint2700_state':'arrived_before_endpoint' if 0<=tr['arrival']<2700 else 'in_network' if tr['depart']>=0 else 'outside','domains':{}}
 if vid[0]=='M':
  assert tr['departLane'] in ('main_up_0','main_up_1') and abs(tr['departPos']-100)<=.02
  for name,edge,a,b in [('feeder','main_up',200,1200),('common','main_down',100,700)]:
   lo=crossing(ss,edge,a);hi=crossing(ss,edge,b);state='observed_traversal' if lo is not None and hi is not None else 'not_observed_entry' if lo is None else 'right_censored' if ss and ss[-1][0]==2699 and ss[-1][1] in (edge+'_0',edge+'_1') and ss[-1][2]<b and tr['arrival']<0 else 'unresolved_missing_exit'
   row['domains'][name]={'entry_bracket':lo,'exit_bracket':hi,'state':state,'inside_sample_count':sum(lane in (edge+'_0',edge+'_1') and a<=pos<b for t,lane,pos in ss)}
 records.append(row)
engineering_records=js(G/'smoke_per_id_technical_records.json')['records'];ck('1608_per_ID_all_fields_recomputed',records==engineering_records)
endpoints={}
for t in (1500,2700):
 entered=sum(0<=tr['depart']<t for tr in trips.values());arrived=sum(0<=tr['arrival']<t for tr in trips.values());endpoints[str(t)]={'planned':1608,'entered':entered,'arrived':arrived,'outside':1608-entered,'in_network':entered-arrived,'membership':'strictly_before_endpoint'}
ck('endpoints',endpoints==eng['raw_time_grid']['endpoint_states']);ck('sample_count',samples==eng['FCD_sample_count'])
previous=None;events=[]
for i,path in enumerate(sorted(Path(card['budget_journal_directory']).glob('event_*.json'))):
 ev=js(path);ck('journal_chain_'+str(i),ev['sequence']==i and ev['previous']==previous);previous=bind(path);events.append(ev)
last=events[-1];attempts=last['state']['attempts'];ck('one_failed_attempt',len(attempts)==2 and attempts[0]['state']=='technical_failed' and attempts[1]['state']=='completed' and attempts[1]['attempt_id']==r['attempt_id'] and all(a['start_observed'] is True for a in attempts))
ck('budget_commit',last['metadata']['output_bindings']==r['output_bindings'] and last['metadata']['reason']=='completed')
ck('no_gate_release',not (Path(card['budget_journal_directory'])/'smoke_acceptance.json').exists())
warning=(A/'outputs/process.stderr.log').read_text().strip();ck('registered_failure',r['execution_status']=='completed' and r['reason']=='completed' and r['exit_code']==0 and warning=='')
ms=[row for row in records if row['group']=='M'];schema_root=Path(mat['binary']['path']).parent.parent/'share/sumo';schema_files=[schema_root/'data/xsd'/n for n in ('sumoConfiguration.xsd','routes_file.xsd','additional_file.xsd')];ck('local_version_matched_schema_exists',all(p.is_file() for p in schema_files))
# All original failed-attempt evidence remains immutable.
prior=js(C/'d1_manifest.json')
for binding in prior['archive_files']+prior['evidence_files']+prior['budget_events']:verify(binding)
for name in ('preflight_stop_receipt.json','preflight_stop_receipt_02.json'):
 stop=js(G/name);ck('preflight0:'+name,stop['SUMO_starts_this_task']==0 and stop['retry_consumed'] is False and stop['attempt2_execution_claim_absent'] is True and stop['budget_counters']['reserved_or_unknown']==0 and stop['environment_mutated'] is False)
xmlmanifest=js(G/'xsd_dependency_manifest.json');env=js(G/'effective_process_environment_receipt.json');home=Path(env['environment_diff']['SUMO_HOME']['after'])
ck('only_environment_diff',set(env['environment_diff'])=={'SUMO_HOME'} and home==schema_root)
# Reconstruct the entire local dependency closure without a production verifier.
seen={};edges=[]
def visit(path):
 path=path.resolve();assert path.is_relative_to(home/'data/xsd') and path.is_file()
 if path in seen:return
 seen[path]=bind(path)
 for element in E.parse(path).getroot().iter():
  if element.tag in ('{http://www.w3.org/2001/XMLSchema}include','{http://www.w3.org/2001/XMLSchema}import','{http://www.w3.org/2001/XMLSchema}redefine'):
   relative=element.get('schemaLocation');assert relative and '://' not in relative
   target=(path.parent/relative).resolve();edges.append({'from':str(path),'to':str(target),'kind':element.tag.split('}')[-1]});visit(target)
for name in xmlmanifest['root_schemas']:visit(home/'data/xsd'/name)
ck('XSD_closure',xmlmanifest['files']==[seen[p] for p in sorted(seen)] and xmlmanifest['edges']==edges and len(seen)==18 and len(edges)==21)
ck('diagnostics_zero',all(not re.search(r'\b(?:Error|Warning)\b',(A/'outputs'/name).read_text()) for name in ('sumo.log','sumo_error.log','process.stderr.log')) and (A/'outputs/sumo_error.log').stat().st_size==0)
usage={'sumo':len(attempts),'smoke':sum(a['role']=='smoke' for a in attempts),'retry':sum(a['role']=='retry' for a in attempts),'validation':sum(a['role']=='validation' for a in attempts),'actual_starts_observed':sum(a.get('start_observed',False) for a in attempts),'reserved_or_unknown':sum(a['state'] in ('reserved','unknown') for a in attempts),'wallclock_s':sum(a['wallclock_s'] for a in attempts),'archive_bytes':sum(a['archive_bytes'] for a in attempts)}
ck('budget_recomputed',usage==eng['budget_counters'] and usage['sumo']==2 and usage['retry']==1 and usage['validation']==0)
# Same scientific/model inputs: path-only differences for attempted-output locations.
first=A.with_name('S6_V1_ML_S17_attempt1');old=js(first/'materialization_manifest.json')
for key in ('network','binary','source_manifest','card','implementation','measurement_implementation','execution_implementation'):ck('same:'+key,old[key]==mat[key])
for name,binding in mat['files'].items():ck('runtime_path_only:'+name,Path(binding['path']).read_bytes().replace(str(A).encode(),str(first).encode())==Path(old['files'][name]['path']).read_bytes())
ck('per_ID_same_as_failed_smoke',records==js(B/'d1_data_review_revision_01/per_id_recomputed_records.json'))
result={'decision':'pass_smoke_technical_data_only','confidence':'High','open_findings':{'Blocker':0,'Major':0,'Minor':0},'closed_finding':'D1-D-T01 SUMO_HOME warning absent after matched-version process environment repair','checks_passed':len(checks),'engineering_receipt':bind(G/'smoke_technical_receipt.json'),'engineering_manifest':bind(G/'retry_final_manifest.json'),'execution_receipt':bind(A/'execution_receipt.json'),'XSD_manifest':bind(G/'xsd_dependency_manifest.json'),'runtime_XML':roles,'FCD_sample_count':samples,'M':{'planned':1083,'entered':sum(v['entered'] for v in ms),'p_min':min(v['departPos'] for v in ms),'p_max':max(v['departPos'] for v in ms),'max_reported_departDelay_s':max(v['departDelay'] for v in ms),'feeder_traversals':sum(v['domains']['feeder']['state']=='observed_traversal' for v in ms),'common_traversals':sum(v['domains']['common']['state']=='observed_traversal' for v in ms),'unresolved_or_censored':sum(any(d['state']!='observed_traversal' for d in v['domains'].values()) for v in ms)},'endpoints':endpoints,'TLS_links':links,'budget_independently_recomputed':usage,'diagnostic_count':0,'XSD_files':18,'XSD_references':21,'environment':env['environment_diff'],'preserved_attempt1_and_two_preflight_stops':True,'environment_recovery_evidence':'Corrected wrapper snapshots before/after environment, asserts only SUMO_HOME differs, and restores/asserts before environment in finally. Raw full environments are intentionally not exported; external OS-level independent retrospective proof is unavailable.','actions':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0,'science_entrypoint_calls':0,'main352_rows_written':0,'sensitivity14_rows_written':0,'validation_released':False},'boundaries':['Smoke only; excluded from scientific validation and all352+14 denominators.','All 1608 per-ID fields independently reconstructed and equal engineering receipt; equality with attempt1 does not retroactively qualify failed attempt1.','Finite inlet/coverage checks do not resolve the scientific obstacle.','Global retry is now exhausted; no further retry release.','Only data gate recommendation; parent/scientific review must control validation release.']}
save('per_id_recomputed_records.json',records);save('data_smoke_retry_receipt.json',result);save('checks.json',checks);save('review_manifest.json',{'files':[bind(p) for p in sorted(D.iterdir()) if p.is_file()],'authoritative_receipt':bind(D/'data_smoke_retry_receipt.json')})
print(json.dumps({k:v for k,v in result.items() if k not in ('runtime_XML','boundaries')},indent=2))
print(bind(D/'data_smoke_retry_receipt.json'));print(bind(D/'review_manifest.json'))
