"""Build the explicitly instructed B revision02 denominator; no scientific evaluation."""
import csv,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parent
RULES=['T_SOURCE','T_TIME','T_ENTRY','T_MEASURE','M_PRIMARY','M_SUPPORT','R_SUPPORT','Q4_COEXIST','S_REF_QUAL','S_M_INFLOW','S_RU_EXPOSURE']
rs=[]
for rule,v,c,s,w in itertools.product(RULES,['V0','V1'],['ML','C'],[17,23],['A','B','Post','Full']):
 if rule.startswith('T_'):app=req=True;scope='version-appropriate source and observation qualification'
 elif rule in ['M_PRIMARY','M_SUPPORT','R_SUPPORT','Q4_COEXIST']:app=req=(v=='V1' and c=='C' and w=='B');scope='V1 feeder science; V0 lacks feeder and is not applicable'
 elif rule=='S_REF_QUAL':app=req=(v=='V1' and c=='ML' and w=='B');scope='V1 feeder lower-load reference qualification'
 elif rule=='S_M_INFLOW':app=req=(w=='B');scope='limited network inlet qualification; not equality of common-section flow and demand'
 elif rule=='S_RU_EXPOSURE':app=(c=='C' and w=='B');req=app and v=='V1';scope='V1 required, V0 context; shared R/U context in registered support block'
 rs.append(dict(rule_id=rule,version=v,condition=c,seed=s,window=w,applicable=str(app).lower(),required_for_resolution=str(req).lower(),value_state='missing_observation' if app else 'not_applicable',result='not_evaluated',scope=scope,cancellation_rule='retain fixed key and required denominator; no substitute seed'))
assert len(rs)==352 and sum(r['applicable']=='true' for r in rs)==150 and sum(r['required_for_resolution']=='true' for r in rs)==148
with (B/'b02_registered_rule_keys_revision_02.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
background=[dict(version='V0',condition=c,seed=s,window=w,domain='main_down[100,700)',source_run=c+str(s),information_status='seen_reused',role='descriptive_common_domain_and_R_background_not_feeder_science',result='not_evaluated') for c,s,w in itertools.product(['ML','C'],[17,23],['A','B','Post','Full'])]
with (B/'b02_registered_background_scope_revision_02.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=background[0]);w.writeheader();w.writerows(background)
print('352 total,150 applicable,148 required,202 N/A')
