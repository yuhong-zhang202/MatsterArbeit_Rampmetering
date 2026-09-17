"""Apply only the reviewed censor-time and background-scope corrections append-only."""
import csv,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with (B/'b02_registered_background_scope_revision_02.csv').open() as f:old=list(csv.DictReader(f))
assert len(old)==16
new=[dict(x) for x in old]
for x in old:
 r=dict(x);r.update(version='V1',source_run='new/pending_C',information_status='new_condition_or_seed',role='descriptive_common_domain_and_R_background_not_feeder_science',result='pending_C');new.append(r)
bg=B/'b02_registered_background_scope_revision_03.csv'
with bg.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=new[0]);w.writeheader();w.writerows(new)
c=json.loads((B/'validation_card_draft_revision_02.json').read_text());c['schema_version']=3;c['status']='Proposed_reviewed_revision_03_pending_primary_final_review'
c['revision_provenance']={'supersedes_card':'validation_card_draft_revision_02.json','prior_card_sha256':sha(B/'validation_card_draft_revision_02.json'),'reason':'Censor lower bound uses confirmed vehicle time; add V1 common-domain background rows; rules and sensitivities unchanged.'}
c['boundary_and_censor_algorithm']['censor']='For valid right-censoring, TT lower=max(0,t_last_confirmed_below_exit-start_upper), where t_last_confirmed_below_exit is this vehicle last valid observed time confirmed upstream of the terminal virtual section. Typical final FCD label2699 does not establish2700. Upper is unbounded; serialize upper as null with bound_state=unbounded, never JSON Infinity or missing_observation.'
c['boundary_and_censor_algorithm']['later_censor_evidence']='A later bound time, including2700, is allowed only with independently traceable endpoint/trajectory evidence establishing that same vehicle remains upstream of the terminal section at that time; bind exact source/hash/locator.'
c['boundary_and_censor_algorithm']['missing_identity']='An unexplained disappearance or missing subsequent identity/trajectory coverage is blocked_by_evidence_error, not automatically right-censored. Valid end-of-record censoring requires continuous qualified identity evidence through the declared last observation.'
c['engineering_dependencies'].append({'field':'right_censor_2699_vs2700_last_confirmed_vehicle_time_and_missing_identity_fixtures','status':'pending_C'})
c['pending_C_required_censor_fixtures']=[{'case':'last_confirmed2699_start_upper1000','expected_lower_s':1699,'forbidden_lower_s':1700},{'case':'later2700_same_vehicle_upstream_status_independently_proven','expected_lower_s':1700,'required':'source/hash/locator for later status'},{'case':'unexplained_identity_disappearance_before_valid_observation_end','expected':'blocked_by_evidence_error','forbidden':'automatic_right_censor'}]
for link in c['artifact_bindings']:
 if link['path'].endswith('b02_registered_background_scope_revision_02.csv'):link.update(path=str(bg.relative_to(R)),sha256=sha(bg))
with (B/'validation_card_draft_revision_03.json').open('x') as f:json.dump(c,f,indent=2);f.write('\n')
print('revision03 card and32 background rows created')
