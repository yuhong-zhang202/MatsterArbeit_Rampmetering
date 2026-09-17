"""Independent schema/arithmetic checks for the non-executable B registration draft."""
import csv,json,hashlib,itertools
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
k=read(B/'b02_registered_rule_keys_revision_02.csv');s=read(B/'b02_registered_sensitivity_keys_revision_02.csv');c=json.loads((B/'validation_card_draft_revision_02.json').read_text())
assert len(k)==352 and len({tuple(r[x] for x in ['rule_id','version','condition','seed','window']) for r in k})==352
assert sum(r['applicable']=='true' for r in k)==150
assert sum(r['required_for_resolution']=='true' for r in k)==148
assert sum(r['applicable']=='false' for r in k)==202
assert sum(r['rule_id'].startswith('T_') and r['required_for_resolution']=='true' for r in k)==128
assert all(r['applicable']=='false' for r in k if r['version']=='V0' and r['rule_id'] in ['M_PRIMARY','M_SUPPORT','R_SUPPORT','Q4_COEXIST'])
assert len(s)==14 and len({(r['sensitivity_id'],r['seed']) for r in s})==14
assert all(r['required_for_resolution']=='true' and r['version']=='V1' for r in s)
assert c['launch_eligible'] is False and c['formal_protocol_frozen'] is False
assert c['position_contract']['extrapolate_departpos'] is False
assert c['rule_denominators']=={'total':352,'applicable':150,'required':148,'not_applicable':202,'required_sensitivity_keys':14}
assert c['scientific_rules']['M_PRIMARY']['TT_ratio_threshold']==1.10
assert c['scientific_rules']['S_M_INFLOW']['max_reported_departDelay_s']==1.01
assert c['position_contract']['M_departPos_m']==100
assert len(c['logical_runs'])==8 and len({r['run_id'] for r in c['logical_runs']})==8
assert c['time_contract']['windows']['B']==[300,1500] and len(c['time_contract']['primary_bins'])==20
assert all(r['status']=='pending_C' for r in c['engineering_dependencies'])
for link in c['artifact_bindings']:
 assert hashlib.sha256((ROOT/link['path']).read_bytes()).hexdigest()==link['sha256']
# Cancelled cells remain members of required set; no denominator decrement.
required={tuple(r[x] for x in ['rule_id','version','condition','seed','window']) for r in k if r['required_for_resolution']=='true'}
assert len(required)==148
# Literal arithmetic fixtures for lower/upper interval contrast and missing state.
assert not (22>1.10*20) and 22.01>1.10*20
assert not (100>1.10*float('inf'))
assert sum([1083,300,150,75])==1608 and sum([1333,300,150,75])==1858
receipt={'status':'passed_non_executable_schema_and_arithmetic','rule_keys':352,'applicable':150,'required':148,'not_applicable':202,'required_sensitivity_keys':14,'launch_eligible':False,'source_binding_count':len(c['artifact_bindings']),'verification_scope':'independent schema, literal arithmetic, fixed-key uniqueness and artifact hashes; no future analyzer or scientific effect validated','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0}
with (B/'b04_registration_verification_revision_02.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt))
