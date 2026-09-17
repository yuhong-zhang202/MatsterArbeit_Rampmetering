"""Re-run only Stage3 archive analysis and compare new products with old ones."""
from pathlib import Path
import subprocess, hashlib, json
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
S3=ROOT/'data/processed/stage3_baseline_diagnostic_20260912_v2'
TABLE=ROOT/'results/tables/astra_stage3_stage5_reaudit_20260913_v1'
LEDGER=ROOT/'data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/audit_only_execution_ledger_revision_02.json'
CODE=ROOT/'src/analysis/analyze_stage3_baseline.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(CODE)=='6558f971bc713397e26a41fd4b2b4a71255a38ff7b6122d77df6056b88b6b8f6'
assert sha(LEDGER)=='22bc5506f0b9df2976b2dc7100fde7ab9729e469836cf7d8d8a0bd5ef2316b38'
runs=json.loads(LEDGER.read_text())['source_runs'];results=[]
(OUT/'repaired_runs').mkdir(exist_ok=False)
(TABLE/'repaired_runs').mkdir(parents=True,exist_ok=False)
for row in runs:
    rid=row['run_id'];dest=OUT/'repaired_runs'/rid;tab=TABLE/'repaired_runs'/rid
    args=['python3','-B',str(CODE),'analyze-run','--ledger',str(LEDGER),'--contract',str(S3/'measurement_contract.json'),'--run-id',rid,'--output-dir',str(dest),'--table-dir',str(tab)]
    done=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
    if done.returncode:
        with (OUT/f'repair_failure_{rid}.json').open('x') as f:json.dump({'command':args,'exit':done.returncode,'stdout':done.stdout,'stderr':done.stderr},f,indent=2)
        raise RuntimeError(f'{rid} failed; retained failure JSON')
    old=json.loads((S3/'runs'/rid/'revision_02/manifest.json').read_text());new=json.loads((dest/'manifest.json').read_text())
    outputs=[]
    for path,expected in old['outputs'].items():
        oldpath=ROOT/path
        newpath=(tab if path.startswith('results/tables/') else dest)/oldpath.name
        actual=sha(newpath)
        assert sha(oldpath)==expected
        outputs.append({'basename':oldpath.name,'old_path':path,'new_path':str(newpath.relative_to(ROOT)),'old_sha256':expected,'new_sha256':actual,'byte_identical':actual==expected})
    assert all(r['byte_identical'] for r in outputs)
    normalized_old={k:v for k,v in old.items() if k!='outputs'};normalized_new={k:v for k,v in new.items() if k!='outputs'}
    assert normalized_old==normalized_new
    results.append({'run_id':rid,'exit_code':done.returncode,'products':outputs,'manifest_metadata_identical_except_output_paths':True,'old_manifest_sha256':sha(S3/'runs'/rid/'revision_02/manifest.json'),'new_manifest_sha256':sha(dest/'manifest.json')})
    print(rid,'12/12 products byte-identical',flush=True)
receipt={'status':'passed','new_sumo_starts':0,'new_netconvert_starts':0,'code_sha256':sha(CODE),'audit_ledger_sha256':sha(LEDGER),'contract_sha256':sha(S3/'measurement_contract.json'),'runs':results,'counts':{'runs':len(results),'byte_identical_products':sum(len(r['products']) for r in results)},'manifest_difference':'Only output paths differ; all other manifest metadata equals historical revision_02. No historical file was rewritten.'}
with (OUT/'repaired_invariance.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
