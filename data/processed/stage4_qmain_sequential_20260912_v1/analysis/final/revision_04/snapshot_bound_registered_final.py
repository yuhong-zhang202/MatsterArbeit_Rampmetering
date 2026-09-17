#!/usr/bin/env python3
"""Generate registered Stage 4 final outputs from the immutable ledger snapshot."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from src.analysis import analyze_stage4_qmain as stage4

ROOT=Path(__file__).resolve().parents[6]
BATCH=ROOT/'data/processed/stage4_qmain_sequential_20260912_v1'
SNAPSHOT=BATCH/'final_evidence_ledger_snapshot.json'
EXPECTED='f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516'
OUT=Path(__file__).resolve().parent

def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v:object)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(name:str,v:object)->None:
 p=OUT/name
 if p.exists(): raise FileExistsError(p)
 p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')

def main()->None:
 raw=SNAPSHOT.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED
 snapshot=json.loads(raw); ledger=snapshot['execution_ledger']
 assert canonical(ledger)==snapshot['canonical_execution_ledger_sha256']
 ext=snapshot['bound_external_evidence']
 contract=BATCH/'measurement_contract.json'; registry=BATCH/'source_registry.json'
 runtime=ROOT/ext['runtime_source_registry']['path']; receipt_registry=ROOT/ext['candidate_manifest_receipt_registry']['path']
 assert digest(contract)==ext['measurement_contract_sha256']
 assert digest(registry)==ext['approved_source_registry_sha256']
 assert digest(runtime)==ext['runtime_source_registry']['sha256']
 assert digest(receipt_registry)==ext['candidate_manifest_receipt_registry']['sha256']
 # Independently hash every archived byte through the snapshot-bound runtime registry.
 approved=json.loads(registry.read_text()); runtime_value=json.loads(runtime.read_text()); archive_checks=[]
 for run_id in stage4.TIER1_IDS+stage4.UPPER_IDS:
  row=next(x for x in runtime_value['runs'] if x['run_id']==run_id)
  sm=ROOT/row['source_map_path']; assert digest(sm)==row['source_map_sha256']; smv=json.loads(sm.read_text())
  assert smv['archive_file_count']==29 and len(smv['file_map'])==29
  for item in smv['file_map']:
   p=ROOT/item['archive_relative_path']; ok=digest(p)==item['sha256'] and p.stat().st_size==item['size_bytes']
   archive_checks.append({'run_id':run_id,'path':item['archive_relative_path'],'sha256':item['sha256'],'passed':ok})
 assert len(archive_checks)==116 and all(x['passed'] for x in archive_checks)
 # Consume candidate manifests via the embedded ledger and its receipt binding.
 receipt_value=json.loads(receipt_registry.read_text())
 candidate_paths=[ROOT/x['manifest_path'] for x in receipt_value['receipts']]
 validated_ledger,candidates=stage4.validate_candidate_manifest_receipt_registry(receipt_registry,ledger,contract,registry,candidate_paths)
 stage4.validate_candidate_decision_inputs(validated_ledger,candidates); stage4.validate_final_candidate_set(validated_ledger,candidates)
 decision=stage4.decide_final(candidates)
 # Full ordered C/3500/3650/MH matrix for terminal denominators.
 contract_value=json.loads(contract.read_text()); refs={}
 for run_id in stage4.TIER1_IDS+stage4.UPPER_IDS:
  for side in ('lower','upper'):
   x=contract_value['ejmi_reference_map'][run_id][side]; refs[x['run_id']]=json.loads((ROOT/x['manifest_path']).read_text())
 by_id={x['run_id']:x for x in list(refs.values())+candidates}
 ordered=[by_id[x] for x in ('C17','C23','QM3500S17','QM3500S23','QM3650S17','QM3650S23','MH17','MH23')]
 stage4.validate_tier2_branch_gate(validated_ledger,approved)
 branch_path=BATCH/'analysis/tier1/revision_05/decision/branch_decision.json'; branch=json.loads(branch_path.read_text())
 summary=stage4.build_logical_statuses(validated_ledger,ordered,branch)
 provenance={'normative_evidence_ledger_snapshot':{'path':SNAPSHOT.relative_to(ROOT).as_posix(),'sha256':EXPECTED,'canonical_execution_ledger_sha256':snapshot['canonical_execution_ledger_sha256']},'current_mutable_execution_ledger_used':False}
 decision['evidence_provenance']=provenance; summary['evidence_provenance']=provenance
 verification={'schema_version':1,'batch_id':snapshot['batch_id'],'status':'passed','normative_evidence_ledger_snapshot':provenance['normative_evidence_ledger_snapshot'],'current_mutable_execution_ledger_used':False,'execution_counters':{k:ledger[k] for k in ('actual_sumo_starts','actual_netconvert_operations','actual_traci_connections','actual_gui_starts')},'attempts_verified':f"{len(ledger['attempts'])}/4",'runtime_rows_verified':f"{len(runtime_value['runs'])}/4",'receipts_verified':f"{len(receipt_value['receipts'])}/4",'archive_files_verified':f"{sum(x['passed'] for x in archive_checks)}/116",'external_bindings_verified':True,'registered_action':decision['action'],'registered_terminal':summary['all_registered_terminal'],'historical_unpreserved_ledger_sha256':snapshot['historical_unpreserved_ledger_binding']['sha256'],'historical_exact_snapshot_available':snapshot['historical_unpreserved_ledger_binding']['exact_immutable_ledger_snapshot_available']}
 write('registered_final_decision.json',decision);write('logical_status_summary.json',summary);write('snapshot_consumption_verification.json',verification);write('archive_hash_checks.json',{'checks':archive_checks,'passed':True})
if __name__=='__main__':main()
