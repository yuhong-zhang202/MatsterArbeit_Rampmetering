"""Focused identity/state regression after independent Major repairs; no simulation."""
import json,csv,sys,copy,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent.parent;ROOT=B.parents[2];sys.path.insert(0,str(ROOT))
from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m
checks=[]
def ok(name,c):assert c,name;checks.append(name)
def reject(name,fn):
 try:fn()
 except (o.EvidenceError,ValueError,KeyError):checks.append(name);return
 raise AssertionError(name+' silently accepted')
def rows(p):
 with p.open() as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ok('engineering receipt exact',sha(B/'c02_engineering_revision_03/engineering_receipt.json')=='a6f228d951408f3a7f15d66ec63a487b0250508018d272eb00d322a132f1a94d')
card=o.load_card();keys,sensitivity=o.read_rule_keys(card)
base=[{**r,'value_state':'missing_observation' if r.get('applicable','true')=='true' else 'not_applicable','result':'not_evaluated' if r.get('applicable','true')=='true' else 'not_applicable'} for r in keys]
for state,value in [('observed',1),('observed_zero',0),('no_contributors',None),('missing_observation',None),('not_applicable',None),('not_paired',None)]:
 ok('value state '+state,m.value(value,state)['value_state']==state)
 if state!='not_applicable':
  rs=copy.deepcopy(base);rs[0].update(value=value,value_state=state,result='not_resolved');ok('result state '+state,m.validate_rule_results(rs,keys)['required']==148)
reject('unbounded not value_state',lambda:m.value(None,'unbounded'))
reject('false measured zero',lambda:m.value(2,'observed_zero'))
reject('missing not zero',lambda:m.value(0,'missing_observation'))
rs=copy.deepcopy(base);rs[0].update(value=1,value_state='observed',bound_state='unbounded',upper=None,result='not_resolved');ok('separate unbounded upper',m.validate_rule_results(rs,keys)['required']==148)
rs[0]['upper']=2700;reject('unbounded finite upper rejected',lambda:m.validate_rule_results(rs,keys))
# Each source identity is independently selected from pinned registry by physical ID.
registry=rows(B/'source_registry.csv');sources={}
for condition in ['ML','C']:
 for seed in [17,23]:
  physical=f'{condition}{seed}';record=next(r for r in registry if r['run_id']==physical);archive=Path(record['archive_path'])
  summary=json.loads((archive/'summary.json').read_text());argv=summary['sumo_command'];ok('independent summary seed '+physical,argv[argv.index('--seed')+1]==str(seed))
  flow={e.get('id'):int(e.get('number')) for e in ET.parse(archive/'demand.rou.xml').getroot().findall('flow')};ok('independent flow count '+physical,flow['M_flow']==(1083 if condition=='ML' else 1333))
  names=['tripinfo.xml','fcd.xml','tls_states.xml']+[f'{pre}_l{i}.xml' for pre in ['merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1'] for i in [0,1]]
  bindings={n:o.bind(archive/'outputs'/n) for n in names};bindings['network.net.xml']=o.bind(archive/'network.net.xml');sources[physical]=bindings
  ident=m.verify_archive_identity(card,o.registered_run(card,f'S6_V0_{condition}_S{seed}'),bindings);ok('pinned physical identity '+physical,ident['physical_run_id']==physical and ident['tripinfo_runtime_header_verified'])
for run in ['S6_V0_ML_S23','S6_V0_C_S17','S6_V1_ML_S17']:
 reject('reject ML17 declared '+run,lambda run=run:m.verify_archive_identity(card,o.registered_run(card,run),sources['ML17']))
reject('unregistered logical run',lambda:o.registered_run(card,'S6_V0_ML_S99'))
# Valid synthetic pair identity; no imported science function is expected-value oracle.
def input_(condition,seed):return {'run_identity':{'run_id':f'S6_V1_{condition}_S{seed}','version':'V1','condition':condition,'seed':str(seed),'evidence_scope':'synthetic_fixture'},'source_qualification':'qualified','cohort':{'bounds':{'certain_count':500,'lower':20 if condition=='ML' else 25,'upper':20 if condition=='ML' else 25}},'bin_speeds':[[30 if condition=='ML' else 27]*25 for _ in range(20)],'certain_counts':[25]*20,'r_counts':[4]*20,'ru_labels':[1]*20,'inlet':{'scientific_result':'supported_bounded'}}
for seed in [17,23]:
 r,c=input_('ML',seed),input_('C',seed);v=m.evaluate_science_pair(r,c);ok('positive paired synthetic'+str(seed),v['scientific_result']=='supported_bounded' and v['evidence_scope']=='synthetic_fixture')
for label,mut in [('missing',lambda r,c:c.pop('run_identity')),('seed-label',lambda r,c:c['run_identity'].update(seed='23')),('different-valid-seed',lambda r,c:c.update(run_identity=input_('C',23)['run_identity'])),('condition',lambda r,c:c['run_identity'].update(condition='ML')),('version',lambda r,c:c['run_identity'].update(version='V0')),('real-source',lambda r,c:c['run_identity'].update(evidence_scope='executed_validation')),('unregistered-id',lambda r,c:c['run_identity'].update(run_id='S6_V1_C_S99'))]:
 r,c=input_('ML',17),input_('C',17);mut(r,c);reject('pair rejected '+label,lambda r=r,c=c:m.evaluate_science_pair(r,c))
receipt={'status':'passed','focused_checks':len(checks),'checks':checks,'closed':['D-C02-M01','D-C02-M02'],'additional_guard':'registered same-V1 same-seed ML/C synthetic pair identity; real V1 adapter remains fail-closed pending_C04_D','production_measurement_sha256':sha(ROOT/'src/analysis/stage6_h2_measurement.py'),'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0}
with (D/'repair_specific_receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
print('Focused checks passed:',len(checks))
