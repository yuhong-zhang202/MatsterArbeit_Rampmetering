"""Independent raw XML and rule reconstruction. No production imports."""
import json,math,hashlib,itertools,re,csv
from pathlib import Path
import xml.etree.ElementTree as E
R=Path.cwd();B=R/'data/processed/stage6_obstacle_20260913_v1';D=B/'d2_data_review_revision_01';G=B/'d2_engineering_seed17_revision_01'
def js(p):return json.loads(Path(p).read_text())
def binding(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(name,x):
 with (D/name).open('x') as f:json.dump(x,f,indent=2,sort_keys=True,allow_nan=False)
checks=[]
def ck(n,x):assert x,n;checks.append(n)
def verify(b):ck('hash:'+b['path'],binding(b['path'])['sha256']==b['sha256'])
def recursive_bindings(v):
 if isinstance(v,dict):
  if 'path' in v and 'sha256' in v:verify(v)
  else:
   for z in v.values():recursive_bindings(z)
 elif isinstance(v,list):
  for z in v:recursive_bindings(z)
def mean(xs):return math.fsum(xs)/len(xs) if xs else None
REGIONS={'main_up':['main_up_0','main_up_1'],'merge_M':[':freeway_merge_1_0',':freeway_merge_1_1'],'main_down':['main_down_0','main_down_1'],'ramp':['ramp_storage_0',':urban_diverge_1_0',':ramp_mid_0_0','ramp_accel_0',':freeway_merge_0_0'],'shared':['shared_approach_0'],'urban_in':['urban_in_0',':urban_tls_0_0'],'urban_out':[':urban_diverge_0_0','urban_out_0'],'cross':['cross_in_0',':urban_tls_1_0','cross_out_0']}
LANE_GROUPS={l:('M' if k in ('main_up','merge_M') else 'MR' if k=='main_down' else 'R' if k=='ramp' else 'RU' if k in ('shared','urban_in') else 'U' if k=='urban_out' else 'X') for k,ls in REGIONS.items() for l in ls}
def bracket(ss,edge,p):
 for a,b in zip(ss,ss[1:]):
  if a[1].rsplit('_',1)[0]==edge and b[1].rsplit('_',1)[0]==edge and a[2]<p<=b[2]:return [a[0],b[0]]
 return None
def member(z,a,b):
 if z[0]>=a and z[1]<b:return 'certain'
 if z[1]>=a and z[0]<b:return 'possible_only'
 return 'outside'
def cohort(traj,trips,edge,start,end,window=(300,1500)):
 records=[];outside=0;not_entry=0
 for vid,ss in sorted(traj.items()):
  if vid[0]!='M':continue
  entry=bracket(ss,edge,start)
  if entry is None:not_entry+=1;continue
  state=member(entry,*window)
  if state=='outside':outside+=1;continue
  exit=bracket(ss,edge,end)
  if exit is None:
   assert ss[-1][0]==2699 and ss[-1][1].rsplit('_',1)[0]==edge and ss[-1][2]<end and trips[vid]['arrival']<0
   interval={'lower':max(0,ss[-1][0]-entry[1]),'upper':None,'bound_state':'unbounded','last_confirmed_s':ss[-1][0]}
  else:interval={'lower':max(0,exit[0]-entry[1]),'upper':exit[1]-entry[0],'bound_state':'bounded'}
  records.append({'vehicle_id':vid,'entry_bracket':entry,'exit_bracket':exit,'cohort_state':state,**interval})
 definite=[x for x in records if x['cohort_state']=='certain'];optional=[x for x in records if x['cohort_state']=='possible_only']
 # Complete subset enumeration is independent of the production sorted-prefix optimization.
 assert len(optional)<=18,'Oracle subset budget requires review, never drop optional vehicles'
 candidates=[]
 for k in range(len(optional)+1):
  for sub in itertools.combinations(optional,k):
   union=definite+list(sub)
   if union:candidates.append((len(union),mean([r['lower'] for r in union]),math.inf if any(r['upper'] is None for r in union) else mean([r['upper'] for r in union])))
 if not candidates:bounds={'value_state':'no_contributors','lower':None,'upper':None,'certain_count':0}
 else:
  lo=min(candidates,key=lambda x:x[1]);hi=max(candidates,key=lambda x:x[2]);bounds={'value_state':'observed','lower':lo[1],'upper':None if math.isinf(hi[2]) else hi[2],'bound_state':'unbounded' if math.isinf(hi[2]) else 'bounded','lower_denominator':lo[0],'upper_denominator':hi[0],'certain_count':len(definite),'possible_only_count':len(optional)}
 return {'records':records,'bounds':bounds,'not_observed_entry':not_entry,'outside_window':outside}
recursive_bindings(js(G/'d2_final_manifest.json'));registration=js(B/'validation_card_draft_revision_03.json');ck('science_card_pin',binding(B/'validation_card_draft_revision_03.json')['sha256']=='d0ef6270f5bdd687621ab3513e9ba533c979a6ea37dbd9e8efd268b5234d1dfb')
results={}
for condition,attempt,nM in [('ML','S6_V1_ML_S17_attempt3',1083),('C','S6_V1_C_S17_attempt1',1333)]:
 A=B/'c04_launch_preparation_revision_03/attempts'/attempt;receipt=js(A/'execution_receipt.json');mat=js(A/'materialization_manifest.json');recursive_bindings(receipt['output_bindings']);recursive_bindings(mat)
 ck(condition+'_identity',receipt['run_id']==f'S6_V1_{condition}_S17' and receipt['role']=='validation' and receipt['condition']==condition and str(receipt['seed'])=='17' and receipt['execution_status']=='completed' and receipt['exit_code']==0 and receipt['evidence_scope']=='real_executed_output')
 sm=js(A/'executed_source_map.json');ck(condition+'_source_map',all(receipt[k]==v for k,v in sm.items()))
 header=(A/'outputs/tripinfo.xml').read_text()[:65536];cfg=E.fromstring(re.findall(r'<sumoConfiguration\b[^>]*>.*?</sumoConfiguration>',header,re.S)[0]);ck(condition+'_runtime_seed_end',cfg.find('.//seed').get('value')=='17' and cfg.find('.//end').get('value')=='2700')
 for field,name in [('route-files','demand.rou.xml'),('tripinfo-output','outputs/tripinfo.xml')]:ck(condition+'_header_'+field,cfg.find('.//'+field).get('value')==str(A/name))
 ck(condition+'_no_diagnostics',all(not re.search(r'\b(?:Warning|Error)\b',(A/'outputs'/n).read_text()) for n in ('sumo.log','sumo_error.log','process.stderr.log')))
 expected={f'{g}_flow.{i}' for g,n in {'M':nM,'R':300,'U':150,'X':75}.items() for i in range(n)};trips={}
 for el in E.parse(A/'outputs/tripinfo.xml').getroot():
  vid=el.get('id');assert vid in expected and vid not in trips
  trips[vid]={k:float(el.get(k)) for k in ('depart','arrival','departDelay','departPos','duration','timeLoss')};trips[vid]['departLane']=el.get('departLane');assert all(math.isfinite(v) for v in trips[vid].values() if isinstance(v,float))
 ck(condition+'_complete_trip_IDs',set(trips)==expected)
 lengths={l.get('id'):float(l.get('length')) for l in E.parse(mat['network']['path']).getroot().findall('.//lane')};traj={v:[] for v in expected};grid=[];stop={k:{g:[0]*2700 for g in 'MRUX'} for k in REGIONS};region_of={l:k for k,ls in REGIONS.items() for l in ls}
 for event,el in E.iterparse(A/'outputs/fcd.xml',events=('end',)):
  if el.tag!='timestep':continue
  t=float(el.get('time'));assert t==len(grid);grid.append(int(t));t=int(t);seen=set()
  for vehicle in el:
   vid=vehicle.get('id');lane=vehicle.get('lane');pos=float(vehicle.get('pos'));speed=float(vehicle.get('speed'));assert vid in expected and vid not in seen and lane in lengths and vid[0] in LANE_GROUPS[lane] and math.isfinite(pos) and math.isfinite(speed) and 0<=pos<=lengths[lane]+.02 and speed>=0
   seen.add(vid);traj[vid].append([t,lane,pos,speed])
   if speed<=.1:stop[region_of[lane]][vid[0]][t]+=1
  el.clear()
 ck(condition+'_FCD2700',grid==list(range(2700)))
 for vid,ss in traj.items():
  tr=trips[vid];wanted=list(range(math.ceil(tr['depart']),min(2700,math.ceil(tr['arrival'])) if tr['arrival']>=0 else 2700)) if tr['depart']>=0 else []
  ck(condition+'_continuous_'+vid,[z[0] for z in ss]==wanted)
 xml={};e1={}
 for name,b in receipt['output_bindings'].items():
  if not name.endswith('.xml'):continue
  root=E.parse(b['path']).getroot();xml[name]={'root':root.tag,'records':len(root)}
  expectedroot='detector' if '_e1_' in name or '_e2.' in name else {'fcd.xml':'fcd-export','queues.xml':'queue-export','sumo_summary.xml':'summary','tripinfo.xml':'tripinfos','vehroute.xml':'routes','tls_states.xml':'tlsStates'}[name];expectedN=90 if expectedroot=='detector' else len(expected) if name in ('tripinfo.xml','vehroute.xml') else 2700
  ck(condition+'_XML_'+name,root.tag==expectedroot and len(root)==expectedN)
  if expectedroot=='detector':
   for i,el in enumerate(root):assert el.get('id')==name[:-4] and float(el.get('begin'))==30*i and float(el.get('end'))==30*(i+1)
  if '_e1_' in name:
   entered=contrib=weighted=0
   for el in root:
    en=float(el.get('nVehEntered'));co=float(el.get('nVehContrib'));sp=float(el.get('speed'));assert en>=0 and co>=0 and en.is_integer() and co.is_integer() and (sp>=0 or (co==0 and sp==-1));entered+=en;contrib+=co;weighted+=sp*co
   e1[name[:-4]]={'entered_count':entered,'contrib_count':contrib,'entered_rate':entered*3600/2700,'contrib_rate':contrib*3600/2700,'contributor_speed':weighted/contrib if contrib else None}
  if name=='tls_states.xml':
   for i,el in enumerate(root):
    phase=0 if i%60<45 else 1 if i%60<48 else 2 if i%60<57 else 3
    assert float(el.get('time'))==i and el.get('state')==('Gr','yr','rG','ry')[phase] and int(el.get('phase'))==phase and el.get('id')=='urban_tls'
 ck(condition+'_14XML',len(xml)==14)
 bins=[[] for _ in range(20)];counts=[0]*20;rpass=[];rpcounts=[0]*20
 for vid,ss in sorted(traj.items()):
  if vid[0]=='M':
   tr=trips[vid];assert tr['departLane'] in ('main_up_0','main_up_1') and abs(tr['departPos']-100)<=.02
   entry=bracket(ss,'main_up',200)
   for i in range(20):counts[i]+=bool(entry and member(entry,300+60*i,360+60*i)=='certain')
   for t,l,pos,speed in ss:
    if 300<=t<1500 and l in ('main_up_0','main_up_1') and 200<=pos<1200:bins[(t-300)//60].append(speed)
  if vid[0]=='R':
   for a,b in zip(ss,ss[1:]):
    if not a[1].startswith('main_down_') and b[1].startswith('main_down_'):
     rpass.append({'vehicle_id':vid,'entry_bracket':[a[0],b[0]]})
     for i in range(20):rpcounts[i]+=member([a[0],b[0]],300+60*i,360+60*i)=='certain'
     break
 ru=[sum(stop['shared']['R'][t]>0 and stop['shared']['U'][t]>0 for t in range(300+60*i,360+60*i)) for i in range(20)]
 inlet=all(0<=tr['depart']<1500 and tr['departDelay']<=1.01 for vid,tr in trips.items() if vid[0]=='M')
 endpoints={str(t):{'planned':len(expected),'entered':sum(0<=tr['depart']<t for tr in trips.values()),'arrived':sum(0<=tr['arrival']<t for tr in trips.values())} for t in (1500,2700)}
 for ep in endpoints.values():ep.update(in_network=ep['entered']-ep['arrived'],outside=ep['planned']-ep['entered'],membership='strictly_before_endpoint')
 feeder=cohort(traj,trips,'main_up',200,1200);common=cohort(traj,trips,'main_down',100,700)
 result={'condition':condition,'run_id':receipt['run_id'],'receipt':binding(A/'execution_receipt.json'),'XML':xml,'FCD_sample_count':sum(len(ss) for ss in traj.values()),'feeder':feeder,'common':common,'bin_means':[mean(b) for b in bins],'bin_speed_sums':[math.fsum(b) for b in bins],'bin_speed_sample_counts':[len(b) for b in bins],'certain_counts':counts,'r_counts':rpcounts,'r_passages':rpass,'ru_labels':ru,'inlet_pass':inlet,'M_max_reported_delay':max(tr['departDelay'] for vid,tr in trips.items() if vid[0]=='M'),'endpoints':endpoints,'e1':e1,'regional_stops':stop,'U_exposed_unique':sum(any(l=='shared_approach_0' and speed<=.1 and stop['shared']['R'][t]>0 for t,l,pos,speed in ss) for vid,ss in traj.items() if vid[0]=='U')}
 results[condition]=result;save(condition+'_raw_oracle.json',result)
def evaluate(ref,chal,tt=1.10,speed=.95,persistence=3,half=.05,cv=.05):
 mu=mean(ref['bin_means']);variance=math.fsum((x-mu)**2 for x in ref['bin_means'])/19
 first=math.fsum(ref['bin_speed_sums'][:10])/sum(ref['bin_speed_sample_counts'][:10]);last=math.fsum(ref['bin_speed_sums'][10:])/sum(ref['bin_speed_sample_counts'][10:]);halfchange=abs(last/first-1);disp=math.sqrt(variance)/mu
 rb=ref['feeder']['bounds'];cb=chal['feeder']['bounds'];refpass=rb['certain_count']>=500 and min(ref['certain_counts'])>=20 and halfchange<=half and disp<=cv
 primary=rb['certain_count']>=500 and cb['certain_count']>=500 and rb['upper'] is not None and cb['lower'] is not None and cb['lower']>tt*rb['upper']
 ratios=[b/a if a is not None and b is not None and a>0 else None for a,b in zip(ref['bin_means'],chal['bin_means'])];counts=[min(a,b) for a,b in zip(ref['certain_counts'],chal['certain_counts'])]
 blocks=[i for i in range(21-persistence) if all(ratios[j] is not None and ratios[j]<=speed and counts[j]>=20 for j in range(i,i+persistence))]
 subs=sorted({j for i in blocks for j in range(i,i+persistence-2)});r=[j for j in subs if sum(chal['r_counts'][j:j+3])>=10 and min(chal['r_counts'][j:j+3])>=1];ru=[j for j in subs if min(chal['ru_labels'][j:j+3])>=1];q=sorted(set(r)&set(ru))
 return {'S_REF_QUAL':refpass,'reference_half_change':halfchange,'reference_CV':disp,'reference_half_means':[first,last],'S_M_INFLOW':ref['inlet_pass'] and chal['inlet_pass'],'M_PRIMARY':primary,'M_SUPPORT_blocks':blocks,'R_SUPPORT_blocks':r,'RU_SUPPORT_blocks':ru,'Q4_blocks':q,'bin_speed_ratios':ratios,'bin_certain_counts_minimum':counts,'scientific_result':'supported_bounded' if refpass and ref['inlet_pass'] and chal['inlet_pass'] and primary and q else 'not_resolved'}
options={'primary':{},'TT05':{'tt':1.05},'TT15':{'tt':1.15},'SPEED90':{'speed':.9},'SPEED98':{'speed':.98},'PERSIST240':{'persistence':4},'REF_STRICT':{'half':.03,'cv':.04},'REF_LOOSE':{'half':.07,'cv':.06}}
comparisons={key:evaluate(results['ML'],results['C'],**kwargs) for key,kwargs in options.items()};save('independent_pair_and_sensitivities.json',comparisons)
keys=list(csv.DictReader((B/'b02_registered_rule_keys_revision_02.csv').open()));ck('fixed_denominator',(len(keys),sum(r['applicable']=='true' for r in keys),sum(r['required_for_resolution']=='true' for r in keys))==(352,150,148))
save('raw_oracle_receipt.json',{'status':'PASS_RAW_RECONSTRUCTION','checks':len(checks),'check_names':checks,'source_receipts':[r['receipt'] for r in results.values()],'independent_algorithm':'No production imports. TT optional membership uses exhaustive subsets; speed means use fsum, CV uses explicit ddof1 sum; common blocks explicitly enumerated.','all_seven_sensitivities_supported':all(v['scientific_result']=='supported_bounded' for k,v in comparisons.items() if k!='primary'),'scientific_result':comparisons['primary']['scientific_result'],'simulation_calls':0})
print(json.dumps({'ML_bounds':results['ML']['feeder']['bounds'],'C_bounds':results['C']['feeder']['bounds'],'primary':comparisons['primary'],'sensitivity':{k:v['scientific_result'] for k,v in comparisons.items() if k!='primary'}},indent=2))
