"""Independent C02 review: production is SUT only, never used as expected-value oracle."""
import sys,csv,json,math,hashlib,itertools,copy,statistics,xml.etree.ElementTree as E
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent.parent;ROOT=B.parents[2];sys.path.insert(0,str(ROOT))
from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m
checks=[];findings=[]
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open() as f:return list(csv.DictReader(f))
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)});assert condition,name
def reject(name,fn):
 try:fn()
 except (o.EvidenceError,ValueError,TypeError,FileExistsError,KeyError):checks.append({'name':name,'passed':True});return
 checks.append({'name':name,'passed':False});findings.append({'id':name,'severity':'Major','observed':'invalid input was accepted'})
def xml(name,root):
 p=D/name
 with p.open('xb') as f:f.write(E.tostring(root))
 return p
def binding(x):
 p=Path(x['path']);p=p if p.is_absolute() else ROOT/p
 check('hash:'+str(p),sh(p)==x['sha256']);return p
src_hash={str(p.relative_to(ROOT)):sh(p) for p in [ROOT/'src/scenarios/stage6_h2_offline.py',ROOT/'src/analysis/stage6_h2_measurement.py']}
card=json.loads((B/'validation_card_draft_revision_03.json').read_text());check('card fixed',sh(B/'validation_card_draft_revision_03.json')=='d0ef6270f5bdd687621ab3513e9ba533c979a6ea37dbd9e8efd268b5234d1dfb')
for x in card['artifact_bindings']:binding(x)
eng=json.loads((B/'c02_engineering_revision_03/engineering_receipt.json').read_text())
for x in eng['files']:binding(x)
matfile=binding(eng['materializations']);mats=json.loads(matfile.read_text())['results'];seen=[]
for x in mats:
 p=binding(x['manifest']);z=json.loads(p.read_text());seen.append((z['run_id'],z['attempt_id'],str(p.parent)))
 for k in ['card','source_manifest','implementation','measurement_implementation','network','binary']:binding(z[k])
 for v in z['files'].values():binding(v)
 flows={f.get('id'):f.attrib for f in E.parse(p.parent/'demand.rou.xml').getroot().findall('flow')}
 expected=1083 if '_ML_' in z['run_id'] else 1333
 check('flow:'+z['run_id'],[int(flows[g+'_flow']['number']) for g in 'MRUX']==[expected,300,150,75] and flows['M_flow']['departPos']=='100' and flows['U_flow']['departPos']=='last')
 cfg=E.parse(p.parent/'scenario.sumocfg').getroot();check('runtime grid:'+z['run_id'],cfg.find('time/end').get('value')=='2700' and cfg.find('processing/extrapolate-departpos').get('value')=='false')
 check('runtime seed:'+z['run_id'],cfg.find('random_number/seed').get('value')==z['run_id'].split('_S')[-1])
check('4 unique materializations',len(seen)==len(set(seen))==4 and len({x[1] for x in seen})==4)
keys=read(B/'b02_registered_rule_keys_revision_02.csv');sens=read(B/'b02_registered_sensitivity_keys_revision_02.csv')
check('352/150/148/202/14',(len(keys),sum(x['applicable']=='true' for x in keys),sum(x['required_for_resolution']=='true' for x in keys),sum(x['applicable']=='false' for x in keys),len(sens))==(352,150,148,202,14))
# G01/G02 source identity and registered conditions.
p=D/'bad_hash.txt';p.write_text('source');reject('G01 hash drift',lambda:o.verify_binding({'path':str(p),'sha256':'0'*64}))
reject('G02 unregistered seed',lambda:o.registered_run(card,'S6_V1_ML_S99'))
# G03/G04 tiny exact FCD grid with independent expected samples.
net=ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/ML17_attempt1/network.net.xml';lengths={n.get('id'):float(n.get('length')) for n in E.parse(net).getroot().findall('.//lane')}
ids={'M_flow.0'};trips={'M_flow.0':{'depart':0.,'arrival':-1.,'departPos':100.,'departDelay':0.,'departLane':'main_up_0'}}
def fcd():
 r=E.Element('fcd-export')
 for t in range(4):E.SubElement(E.SubElement(r,'timestep',time=str(t)),'vehicle',id='M_flow.0',lane='main_up_0',pos=str(100+100*t),speed='10')
 return r
for tag,mut in [('missing_speed',lambda r:r[0][0].attrib.pop('speed')),('nan',lambda r:r[0][0].set('speed','nan')),('negative',lambda r:r[0][0].set('speed','-1')),('unknown_ID',lambda r:r[0][0].set('id','M_flow.9')),('unknown_lane',lambda r:r[0][0].set('lane','bad')),('duplicate',lambda r:r[0].append(copy.deepcopy(r[0][0]))),('missing_frame',lambda r:r.remove(r[1])),('extra_frame',lambda r:r.append(copy.deepcopy(r[-1]))),('identity_disappearance',lambda r:r[-1].remove(r[-1][0]))]:
 r=fcd();mut(r);p=xml('fcd_'+tag+'.xml',r);reject('G03/04 '+tag,lambda p=p:m.read_fcd(p,ids,trips,lengths,4))
# G05 exact TLS labels and movement states, including wrong same-length grid.
for tag,attr,val in [('label','time','1'),('state','state','rG'),('program','programID','bad')]:
 r=E.Element('tlsStates')
 for t in range(4):E.SubElement(r,'tlsState',time=str(t),id='urban_tls',programID='technical_placeholder',state='Gr')
 r[0].set(attr,val);p=xml('tls_'+tag+'.xml',r);reject('G05 '+tag,lambda p=p:m.read_tls(p,4))
# G06/G09 E1 expected30s with actual5s tail; contributions separate from entries.
def e1():
 r=E.Element('detector')
 for a,b,ne,nc,v in [(0,30,4,2,10),(30,35,2,1,40)]:E.SubElement(r,'interval',id='det',begin=str(a),end=str(b),nVehEntered=str(ne),nVehContrib=str(nc),speed=str(v),occupancy='5')
 return r
p=xml('e1_valid_tail.xml',e1());es=m.read_e1(p,'det',35,expected_period_s=30)
a=m.aggregate_e1(es,'e1_nVehEntered_rate');b=m.aggregate_e1(es,'e1_nVehContrib_rate');check('G09 literal tail and counters',a['covered_seconds']==35 and a['rate_vehph']==6*3600/35 and b['rate_vehph']==3*3600/35 and b['speed']['value']==20)
reject('G06 wrong registered period',lambda:m.read_e1(p,'det',35,expected_period_s=15))
for tag,attr,v in [('positive_bad_speed','speed','-1'),('negative_contrib','nVehContrib','-1'),('missing_speed','speed',None),('bad_tail','end','34')]:
 r=e1();el=r[1]
 if v is None:el.attrib.pop(attr)
 else:el.set(attr,v)
 q=xml('e1_'+tag+'.xml',r);reject('G06 '+tag,lambda q=q:m.read_e1(q,'det',35,expected_period_s=30))
r=e1()
for el in r:el.set('nVehContrib','0');el.set('speed','-1')
p=xml('e1_empty_contrib.xml',r);z=m.aggregate_e1(m.read_e1(p,'det',35,expected_period_s=30),'e1_nVehContrib_rate');check('G06 no contributors',z['speed']['value'] is None and z['speed']['value_state']=='no_contributors')
# G07 exact independent regional assignment of internal samples.
r=m.regional_stops({'R_flow.0':[m.Sample(0,':urban_diverge_1_0',0,0),m.Sample(1,':ramp_mid_0_0',0,.1),m.Sample(2,':freeway_merge_0_0',0,0)],'M_flow.0':[m.Sample(1,':freeway_merge_1_0',0,0)]},3)
check('G07 final attribution',r['ramp']['R']==[1,1,1] and r['merge_M']['M']==[0,1,0] and sum(sum(v) for reg in r.values() for v in reg.values())==4)
# G08 boundaries and valid last confirmed time; missing identity remains error.
check('G08 2699 lower',m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=True)['lower']==1699)
reject('G08 missing continuity',lambda:m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=False))
check('G08 half open',m.membership((299,300),300,360)=='possible_only' and m.membership((359,360),300,360)=='possible_only')
# Independent exhaustive subset oracle, unlike sorted production implementation.
def oracle(ds,os):
 choices=[]
 for bits in itertools.product([0,1],repeat=len(os)):
  selected=ds+[x for x,b in zip(os,bits) if b]
  if selected:choices.append((sum(x['lower'] for x in selected)/len(selected),sum(math.inf if x['upper'] is None else x['upper'] for x in selected)/len(selected)))
 return (min(x[0] for x in choices),max(x[1] for x in choices)) if choices else (None,None)
mk=lambda l,u:{'lower':l,'upper':u,'bound_state':'unbounded' if u is None else 'bounded'}
for i,(ds,opts) in enumerate([([],[]),([mk(10,12)],[mk(0,100),mk(30,40)]),([],[mk(1,2),mk(3,None)]),([mk(4,None)],[mk(0,1)]),([mk(1,1),mk(9,15)],[mk(3,7),mk(11,30),mk(1,100)])]):
 lo,hi=oracle(ds,opts);got=m.conservative_mean_bounds(ds,opts);check('G09 exhaustive cohort'+str(i),got['lower']==lo and ((hi is None and got['upper'] is None) or (hi==math.inf and got['upper'] is None) or got['upper']==hi))
# G10 fixed denominator and absent pair, independent keys.
check('G10 outer not zero',m.paired_rows({'a':0},{'b':2})==[{'key':'a','left':0,'right':None,'pair_state':'not_paired'},{'key':'b','left':None,'right':2,'pair_state':'not_paired'}])
rr=[{**x,'value_state':'missing_observation' if x['applicable']=='true' else 'not_applicable','result':'not_evaluated' if x['applicable']=='true' else 'not_applicable'} for x in keys]
check('G10 all rows retained',m.validate_rule_results(rr,keys)['required']==148)
reject('G10 missing key',lambda:m.validate_rule_results(rr[:-1],keys));bad=copy.deepcopy(rr);bad[0]['required_for_resolution']='false';reject('G10 shrunken required',lambda:m.validate_rule_results(bad,keys))
reject('G11 unknown metric',lambda:m.aggregate_e1(es,'requested_flow'))
# Registered states should be accepted consistently; record current violation separately.
for state,val in [('observed_zero',0),('not_paired',None)]:
 try:m.value(val,state)
 except Exception as exc:findings.append({'id':'G11_value_state_'+state,'severity':'Major','observed':str(exc),'expected':'registered value_state supported without converting missing tozero'})
# G12 pure recovery states, no real process calls.
s=o.new_budget(card);ev={'event':'reserve','run_id':'S6_V1_ML_S17','attempt_id':'auditA','role':'validation','parameter_hash':'a'*64};s=o.budget_event(s,card,ev);check('G12 reserved charged',o.budget_usage(s)['sumo']==1);s=o.budget_event(s,card,{'event':'mark_unknown','attempt_id':'auditA'});reject('G12 unknown duplicate reserve',lambda:o.budget_event(s,card,{**ev,'attempt_id':'auditB'}));reject('G12 unproved release',lambda:o.budget_event(s,card,{'event':'release','attempt_id':'auditA'}));p=o.save_budget_revision(s,D);reject('G12 overwrite ledger',lambda:o.save_budget_revision(s,D))
# Real archive compatibility and independent raw trip IDs/endpoints.
archive=net.parent;rawtrips={n.get('id'):n.attrib for n in E.parse(archive/'outputs/tripinfo.xml').getroot().findall('tripinfo')};check('archive direct identity count',len(rawtrips)==1608 and sum(x.startswith('M_flow.') for x in rawtrips)==1083)
measured=m.analyze_observations(archive/'outputs',{'M':1083,'R':300,'U':150,'X':75},lengths,'V0')
check('archive total samples',sum(len(x) for x in measured['trajectories'].values())==260011)
for t in [1500,2700]:
 entered=sum(0<=float(x['depart'])<t for x in rawtrips.values());arrived=sum(0<=float(x['arrival'])<t for x in rawtrips.values());g=measured['endpoints'][str(t)];check('archive endpoint'+str(t),(g['entered'],g['arrived'],g['in_network'],g['outside'])==(entered,arrived,entered-arrived,1608-entered))
common=m.domain_cohort(measured['trajectories'],measured['tripinfo'],'main_down',100,700)
old=read(ROOT/'results/tables/stage6_obstacle_20260913_v1/b01_seen_common_domain_vehicles.csv');old=[x for x in old if x['run_id']=='ML17'];ds=[];opts=[]
for x in old:
 lo=float(x['start_lower_s']);hi=float(x['start_upper_s']);v=mk(float(x['travel_lower_s']),float(x['travel_upper_s']))
 if lo>=300 and hi<1500:ds.append(v)
 elif hi>=300 and lo<1500:opts.append(v)
lo,hi=oracle(ds,opts);check('archive independent cohort bounds',math.isclose(lo,common['bounds']['lower']) and math.isclose(hi,common['bounds']['upper']))
# Demonstrate whether top-level binding distinguishes same-count wrong-seed archives.
source={p.name:o.bind(p) for p in [archive/'outputs'/n for n in ['tripinfo.xml','fcd.xml','tls_states.xml']+[f'{pre}_l{i}.xml' for pre in ['merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1'] for i in [0,1]]]+[net]}
try:
 wrong=m.analyze_to_new_directory(source,'S6_V0_ML_S23',D/'wrong_seed_audit_probe')
 findings.append({'id':'G01_wrong_seed_binding','severity':'Major','observed':'ML17 raw archive accepted as S6_V0_ML_S23 with qualified manifest','expected':'binding to registered physical-run identity, not just arbitrary file hashes'})
except o.EvidenceError:checks.append({'name':'G01 wrong seed rejected','passed':True})
with (D/'initial_independent_receipt.json').open('x') as f:json.dump({'checks':checks,'findings':findings,'production_hashes':src_hash,'oracle':'exhaustive optional subsets plus literal raw XML identities and registered key arithmetic; production imported as SUT only','SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},f,indent=2)
print(json.dumps({'checks':len(checks),'failed_checks':[x for x in checks if not x['passed']],'findings':findings}))
