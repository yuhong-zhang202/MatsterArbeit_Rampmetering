import sys,json,hashlib,copy,itertools,math
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R));D=R/'data/processed/stage6_obstacle_20260913_v1/c04_data_review_revision_02';P=D.parent/'c04_launch_preparation_revision_03'
from src.analysis import stage6_h2_measurement as m
from src.scenarios import stage6_h2_offline as o
checks=[]
def ck(n,b):checks.append({'name':n,'pass':bool(b)});assert b,n
def js(p):return json.loads(Path(p).read_text())
def h(b):return hashlib.sha256(b).hexdigest()
def enc(x):return (json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
card=js(P/'proposed_launch_card.json')
for parent,retry in zip(card['attempts'],card['retry_options']):
 mat=js(parent['materialization']['path']);old=str(Path(parent['materialization']['path']).parent);new=str(Path(retry['materialization']['path']).parent)
 # Independently predict retry bytes by path-only substitution: source physics is invariant.
 expected=copy.deepcopy(mat);expected['attempt_id']=retry['attempt_id'];expected['proposed_sumo_argv_not_authorized']=[v.replace(old,new) for v in expected['proposed_sumo_argv_not_authorized']]
 for name,b in expected['files'].items():
  data=Path(mat['files'][name]['path']).read_bytes().replace(old.encode(),new.encode());b.update(path=b['path'].replace(old,new),sha256=h(data))
 ck(retry['attempt_id']+'_runtime',expected['files']==retry['expected_runtime_files'])
 ck(retry['attempt_id']+'_manifest',h(enc(expected))==retry['materialization']['sha256'])
 ck(retry['attempt_id']+'_unmaterialized',not Path(retry['materialization']['path']).exists())
# Literal interval and optional-subset oracle, upper infinity has distinct bound_state.
z=m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=True)
ck('2699_interval',z['lower']==1699 and z['upper'] is None and z['bound_state']=='unbounded')
a=[{'lower':2.,'upper':4.},{'lower':4.,'upper':6.}];b=[{'lower':0.,'upper':2.},{'lower':8.,'upper':None}]
for interval in a+b:interval['bound_state']='unbounded' if interval['upper'] is None else 'bounded'
sets=[a+[b[i] for i in range(2) if mask>>i&1] for mask in range(4)]
lo=min(sum(v['lower'] for v in s)/len(s) for s in sets);hi=max(sum(math.inf if v['upper'] is None else v['upper'] for v in s)/len(s) for s in sets)
bounds=m.conservative_mean_bounds(a,b);ck('independent_optional_lower',bounds['lower']==lo);ck('independent_optional_infinite',math.isinf(hi) and bounds['upper'] is None)
for state,val in [('observed',1),('observed_zero',0),('no_contributors',None),('missing_observation',None),('not_applicable',None),('not_paired',None)]:ck('state_'+state,m.value(val,state)['value_state']==state)
for n,rows in [('main',js(D/'independent_fake_chain/paired_negative/resolution_rule_results.json')),('sens',js(D/'independent_fake_chain/paired_negative/sensitivity_rule_results.json'))]:
 ck(n+'_no_missing_zero',all('value' not in r or r['value'] is None for r in rows if r['value_state'] in ('missing_observation','not_paired','not_applicable')))

with (D/'retry_bound_state_receipt.json').open('x') as f:json.dump({'checks':checks,'passed':len(checks)},f,indent=2)
print(len(checks))
