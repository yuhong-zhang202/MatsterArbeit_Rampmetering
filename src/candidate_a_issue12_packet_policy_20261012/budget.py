"""Cumulative resource guardian; unknown reservations remain fully charged."""
from pathlib import Path
import json,hashlib,math
TOTAL_WALL=900
TOTAL_BYTES=900000000
SINGLE_WALL=300
SINGLE_BYTES=300000000
RAW=Path('data/raw/issue12_alinea_actuation_20261012_v1')
HISTORY=Path('artifacts/issue12_alinea_actuation_20261012_v1/engineering/packet_v1/HISTORY_BINDING_V1.json')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,reason):
    if not ok:raise ValueError(reason)


def accounting(root):
    """Before launch, verify settled histories; unmatched directories are unknown."""
    root=Path(root);h=json.loads((root/HISTORY).read_text());known={};wall=0.;size=0;unknown=[]
    for run,x in h['runs'].items():
        receipt=root/x['receipt_path'];manifest=root/x['raw_manifest_path']
        require(sha(receipt)==x['receipt_sha256'] and sha(manifest)==x['raw_manifest_sha256'],'TOTAL_BUDGET_HISTORY_DRIFT')
        b=json.loads(receipt.read_text());m=json.loads(manifest.read_text())
        require(b['native_started'] is True and b['final_logs']['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF','TOTAL_BUDGET_HISTORY_NOT_SETTLED')
        elapsed=b['monitored_elapsed_through_cleanup_s']
        require(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0,'TOTAL_BUDGET_HISTORY_TIME_UNKNOWN')
        require(all(sha(root/n)==v for n,v in m['files'].items()),'TOTAL_BUDGET_RAW_HISTORY_DRIFT')
        actual={str(p.relative_to(root)) for p in (root/RAW/run).rglob('*') if p.is_file()}
        require(actual==set(m['files']),'TOTAL_BUDGET_HISTORY_FILE_COVERAGE_UNKNOWN')
        amount=sum((root/n).stat().st_size for n in actual)
        require(amount==m['bytes'],'TOTAL_BUDGET_HISTORY_BYTES_UNKNOWN')
        wall+=elapsed;size+=amount;known[run]={'monitored_s':elapsed,'raw_bytes':amount}
    for parent in (root/RAW).iterdir() if (root/RAW).exists() else ():
        if parent.name not in known:
            # No inferred release for missing receipt, transport failure or orphan.
            unknown.append(parent.name);wall+=SINGLE_WALL;size+=SINGLE_BYTES
    require(wall<TOTAL_WALL and size<TOTAL_BYTES,'TOTAL_BUDGET_EXHAUSTED')
    return {'known_settled':known,'unknown_reserved':unknown,'charged_monitored_s':wall,'charged_raw_bytes':size,'remaining_s':TOTAL_WALL-wall,'remaining_bytes':TOTAL_BYTES-size,'selected_total_limits':{'wall_s':TOTAL_WALL,'bytes':TOTAL_BYTES},'fixed_start_count_limit':None}


def effective_limits(resources,bound):
    require(type(resources['wall_limit_s']) is int and resources['wall_limit_s']==SINGLE_WALL and resources['run_limit_bytes']==SINGLE_BYTES,'SINGLE_CAP_DRIFT')
    require(bound['remaining_s']>0 and bound['remaining_bytes']>0,'TOTAL_BUDGET_EXHAUSTED')
    # Original single ceilings remain; a smaller residual total also binds.
    return {**resources,'wall_limit_s':min(SINGLE_WALL,bound['remaining_s']),'run_limit_bytes':min(SINGLE_BYTES,bound['remaining_bytes'])}
