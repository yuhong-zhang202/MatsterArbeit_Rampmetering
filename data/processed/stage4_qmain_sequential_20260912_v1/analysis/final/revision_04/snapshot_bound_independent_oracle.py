#!/usr/bin/env python3
"""Independent Stage 4 final oracle; intentionally imports no production analysis."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]; B=ROOT/'data/processed/stage4_qmain_sequential_20260912_v1'; OUT=Path(__file__).resolve().parent
SNAP=B/'final_evidence_ledger_snapshot.json'; EXPECTED='f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def payload_hash(v):
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def main():
 raw=SNAP.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;s=json.loads(raw);ledger=s['execution_ledger'];assert canonical(ledger)==s['canonical_execution_ledger_sha256'];ext=s['bound_external_evidence']
 contract_path=B/'measurement_contract.json';assert sha(contract_path)==ext['measurement_contract_sha256'];contract=json.loads(contract_path.read_text())
 rr=ROOT/ext['candidate_manifest_receipt_registry']['path'];assert sha(rr)==ext['candidate_manifest_receipt_registry']['sha256']; reg=json.loads(rr.read_text()); candidates=[]; receipt_checks=[]
 for idx in reg['receipts']:
  mp=ROOT/idx['manifest_path'];rp=ROOT/idx['receipt_path'];m=json.loads(mp.read_text());r=json.loads(rp.read_text())
  checks={'manifest_file':sha(mp)==idx['manifest_file_sha256'],'receipt_file':sha(rp)==idx['receipt_file_sha256'],'manifest_payload':payload_hash(m)==idx['manifest_payload_sha256'],'receipt_manifest_link':r['manifest_file_sha256']==idx['manifest_file_sha256'] and r['manifest_payload_sha256']==idx['manifest_payload_sha256'],'identity':m['run_id']==idx['run_id']==r['run_id'],'qualified':m['technical_qualified'] is True and r['technical_qualified'] is True}
  receipt_checks.append({'run_id':m['run_id'],'checks':checks,'passed':all(checks.values())});candidates.append(m)
 assert len(candidates)==4 and all(x['passed'] for x in receipt_checks)
 refs={}
 for m in candidates:
  for side in ('lower','upper'):
   b=m['ejmi_reference_registration'][side];p=ROOT/b['manifest_path'];v=json.loads(p.read_text());assert payload_hash(v)==b['manifest_payload_sha256'];refs[v['run_id']]=v
 by={m['run_id']:m for m in candidates}|refs; ordered_ids=('C17','C23','QM3500S17','QM3500S23','QM3650S17','QM3650S23','MH17','MH23'); assert set(by)==set(ordered_ids)
 points=[]
 for q,ids in [(3500,('QM3500S17','QM3500S23')),(3650,('QM3650S17','QM3650S23'))]:
  rows=[by[x] for x in ids];points.append({'q_main':q,'run_ids':list(ids),'r_states':[x['r_passage']['status'] for x in rows],'ejmi_states':[x['ejmi']['status'] for x in rows],'r_consistent':len({x['r_passage']['status'] for x in rows})==1,'ejmi_consistent':len({x['ejmi']['status'] for x in rows})==1})
 supports=(points[0]['r_states']==['clear_passage']*2 and points[1]['r_states']==['clear_exclusion']*2 and all(p['ejmi_states']==['not_identified']*2 for p in points))
 action='supports_B_pattern_within_registered_points' if supports else 'unresolved'
 envelope=[]
 margins=contract['ejmi']['margins']
 for m in candidates:
  lo=by[m['ejmi_reference_registration']['lower']['run_id']];hi=by[m['ejmi_reference_registration']['upper']['run_id']]
  for w in ('A','B'):
   c=m['e1']['aggregates'][w]; lv=lo['e1']['aggregates'][w];uv=hi['e1']['aggregates'][w];req_v=min(lv['speed_mps'],uv['speed_mps'])-margins[w]['delta_v_mps'];req_o=max(lv['occupancy_percent'],uv['occupancy_percent'])+margins[w]['delta_occ_percentage_points'];vp=c['speed_mps']<req_v;op=c['occupancy_percent']>req_o
   envelope.append({'run_id':m['run_id'],'seed':m['seed'],'q_main':m['q_main'],'window':w,'candidate_speed_mps':c['speed_mps'],'required_speed_below_mps':req_v,'speed_delta_candidate_minus_threshold_mps':c['speed_mps']-req_v,'speed_condition_passed':vp,'candidate_occupancy_percent':c['occupancy_percent'],'required_occupancy_above_percent':req_o,'occupancy_delta_candidate_minus_threshold_pp':c['occupancy_percent']-req_o,'occupancy_condition_passed':op,'aggregate_ejmi_passed':vp and op,'registered_aggregate_ejmi_passed':m['ejmi']['aggregate_checks'][w],'persistence_passed':m['ejmi']['persistence']['passed'],'ejmi_status':m['ejmi']['status']})
 assert all(x['aggregate_ejmi_passed']==x['registered_aggregate_ejmi_passed'] for x in envelope)
 r_evidence=[{'run_id':m['run_id'],'seed':m['seed'],'q_main':m['q_main'],'coverage_complete':m['r_passage']['coverage_complete'],'A_arrivals':m['r_passage']['a_arrival_count'],'A_bracketed':m['r_passage']['a_bracketed_event_count'],'A_unbracketed':m['r_passage']['a_unbracketed_event_count'],'all_observed_R_passage_events':m['r_passage']['denominator_all_observed_r_passage_events'],'status':m['r_passage']['status']} for m in candidates]
 terminal=sum(bool(x['terminal']) for x in ledger['logical_runs']); used=[by[x] for x in ordered_ids]; endpoints=sum(len(x['endpoints']) for x in used)
 denominators={'registered_logical_runs':len(ledger['logical_runs']),'registered_terminal_runs':terminal,'used_valid_run_manifests':len(used),'class_endpoint_units_expected':64,'class_endpoint_units_observed':endpoints,'adjacent_matched_seed_comparisons_expected':6,'used_qmain_points':[3200,3500,3650,3800]}
 out={'schema_version':1,'batch_id':s['batch_id'],'method':'independent standard-library snapshot/manifest oracle; no production aggregation, EJMI, status, or decision import','normative_evidence_ledger_snapshot':{'path':SNAP.relative_to(ROOT).as_posix(),'sha256':EXPECTED,'canonical_execution_ledger_sha256':s['canonical_execution_ledger_sha256']},'current_mutable_execution_ledger_used':False,'receipt_checks':receipt_checks,'point_states':points,'ejmi_envelope_checks':envelope,'r_passage_evidence':r_evidence,'denominators':denominators,'independent_action':action,'supports_B_conditions_passed':supports,'interpretation_boundary':'Exploratory registered discrete points and two seeds only; not causal, capacity, Breakdown, mainline-absence, controller, sweet-spot, or thesis evidence.'}
 p=OUT/'snapshot_bound_independent_oracle.json';assert not p.exists();p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
