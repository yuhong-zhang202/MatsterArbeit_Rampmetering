"""Append proposal keys and provenance without executing the proposed experiment."""
from pathlib import Path
import csv,json,hashlib,itertools,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent;R=B.parents[2];T=R/'results/tables'/B.name
def rows(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
 with p.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=x[0]);w.writeheader();w.writerows(x)
proposal=json.loads((B/'b01_b02_data_design_proposal.json').read_text());assert proposal['launch_eligible'] is False
ss=rows(T/'b01_seen_common_domain_summary.csv');rs={r['run_id']:r for r in rows(T/'run_summary.csv')};contrasts=[]
for s in ss:
 if s['window']!='B':continue
 r=rs[s['run_id']];ref=next(x for x in ss if x['run_id']=='ML'+s['seed'] and x['window']=='B')
 contrasts.append(dict(run_id=s['run_id'],seed=s['seed'],q_main=s['q_main'],q_ramp=s['q_ramp'],B_completed_M=s['eligible_completed_M'],B_boundary_ambiguous_M=s['boundary_ambiguous_M'],B_TT_lower_s=s['mean_travel_lower_s'],B_TT_upper_s=s['mean_travel_upper_s'],B_TT_ratio_lower_vs_ML=float(s['mean_travel_lower_s'])/float(ref['mean_travel_upper_s']),B_TT_ratio_upper_vs_ML=float(s['mean_travel_upper_s'])/float(ref['mean_travel_lower_s']),B_M_speed_mps=s['mean_speed_mps'],A_R_passages=r['R_first_downstream_A'],Full_R_passages=r['R_first_downstream_Full'],selection='reference_candidate' if s['run_id'].startswith('ML') else 'challenge_candidate' if s['run_id'].startswith('C') else 'not_selected',qualification='seen_archives_only; ML is not established free-flow',value_state='observed'))
write(T/'b01_reference_challenge_candidates.csv',contrasts)
rules=['T_SOURCE','T_TIME','T_ENTRY','T_MEASURE','M_PRIMARY','M_SUPPORT','R_SUPPORT','Q4_COEXIST'];keys=[]
for rule,v,c,seed,w in itertools.product(rules,['V0','V1'],['ML','C'],[17,23],['A','B','Post','Full']):
 tech=rule.startswith('T_');applies=tech or(c=='C' and w=='B');required=tech or(applies and v=='V1')
 keys.append(dict(rule_id=rule,version=v,condition=c,seed=seed,window=w,applicable=str(applies).lower(),required_for_proposed_resolution=str(required).lower(),value_state='missing_observation' if applies else 'not_applicable',result='not_evaluated',reason='Proposed fixed denominator; cancelled/failed/unobserved cells retained; V0 science is context only' if applies else 'Registered non-primary window or reference condition; not omitted after outcomes'))
assert len(keys)==256 and len({tuple(x[k] for k in ['rule_id','version','condition','seed','window']) for x in keys})==256
write(B/'b02_proposed_expected_rule_keys.csv',keys)
matrix=[]
for v,c,s in itertools.product(['V0','V1'],['ML','C'],[17,23]):matrix.append(dict(run_id=f'S6_{v}_{c}_S{s}',version=v,condition=c,seed=s,reuse_or_new='reuse' if v=='V0' else 'new',parent_source_id=c+str(s) if v=='V0' else '',information_status='seen_reused' if v=='V0' else 'new_condition_or_seed',information_reason='same archived trajectory' if v=='V0' else 'new M insertion configuration; additional traveled upstream observation',required_for_resolution='true',status='proposed_not_run',cancel_rule='preserve registered row and denominator; no substitute seed'))
write(B/'b02_proposed_run_matrix.csv',matrix)
flows=[]
for source in rows(B/'source_file_inventory.csv'):
 if source['run_id'] not in ['C17','C23','ML17','ML23'] or source['source_suffix']!='demand.rou.xml':continue
 p=Path(source['path']);assert sha(p)==source['sha256']
 for f in ET.parse(p).getroot().findall('flow'):
  a=f.attrib;flows.append(dict(run_id=source['run_id'],class_id=a['id'],begin=a['begin'],end=a['end'],number=a['number'],departPos=a['departPos'],departLane=a['departLane'],departSpeed=a['departSpeed'],effective_scheduled_count_rate_vehph=float(a['number'])*3600/(float(a['end'])-float(a['begin'])),source_path=str(p.relative_to(R)),source_sha256=source['sha256'],qualification='exact original number-based flow; effective scheduled rate not realized entry'))
write(B/'b01_fixed_demand_source_fields.csv',flows)
assert len(flows)==16
for r in flows:
 if r['class_id']=='U_flow':assert r['number']=='150'
 if r['class_id']=='X_flow':assert r['number']=='75'
manifest=[]
for folder in [B,T]:
 for p in sorted(folder.glob('b0*')):
  if p.is_file():manifest.append(dict(path=str(p.relative_to(R)),sha256=sha(p),size_bytes=p.stat().st_size))
write(B/'b02_data_advice_manifest.csv',manifest)
with (B/'b02_data_advice_verification.json').open('x') as f:json.dump({'status':'proposal_structural_checks_passed_not_scientific_registration','unique_logical_runs':8,'expected_rule_keys':256,'required_technical_keys':128,'required_V1_scientific_keys':8,'required_total_keys':136,'applicable_V0_scientific_context_keys':8,'not_applicable_keys':112,'required_scientific_seed_denominator':2,'seen_candidate_rows':12,'original_flow_rows':16,'independent_new_numeric_receipt':'b01_independent_verification.json','cancelled_rule':'retained as unobserved/cancelled, never remove from required denominator','unknown_rules_block_B_completion':True,'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},f,indent=2)
print({'manifest_files':len(manifest),'rule_keys':len(keys),'required':sum(x['required_for_proposed_resolution']=='true' for x in keys)})
