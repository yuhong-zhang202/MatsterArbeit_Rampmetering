"""Approved NEW-stage envelope. Unsettled reservations charge their full ceilings."""
from pathlib import Path
import json, math
from src.candidate_a_issue12_packet_policy_20261012.budget import sha, require, effective_limits
TOTAL_WALL=1200
TOTAL_BYTES=1200000000
SINGLE_WALL=300
SINGLE_BYTES=300000000
RAW=Path('data/raw/unified_alinea_actuator_20261013_v1')
SETTLEMENTS=Path('artifacts/unified_alinea_actuator_20261013_v1/engineering/settlements')


def accounting(root):
    root=Path(root);known={};unknown=[];wall=0.;size=0
    for parent in (root/RAW).iterdir() if (root/RAW).exists() else ():
        require(parent.is_dir(), 'UNKNOWN_NEW_RAW_ALLOCATION')
        settlement=root/SETTLEMENTS/parent.name/'SETTLEMENT.json'
        if not settlement.exists():
            unknown.append(parent.name);wall+=300;size+=300000000;continue
        s=json.loads(settlement.read_text())
        require(s['run_id']==parent.name and s['status']=='SETTLED_AFTER_THREE_ROLE_REVIEW', 'INVALID_SETTLEMENT')
        require(set(s['reviews'])=={'engineering','data','science'}, 'UNREVIEWED_SETTLEMENT')
        for item in s['reviews'].values():require(sha(root/item['path'])==item['sha256'], 'SETTLEMENT_REVIEW_DRIFT')
        for key in ('receipt','raw_manifest'):
            require(sha(root/s[key]['path'])==s[key]['sha256'], 'SETTLEMENT_RECORD_DRIFT')
        b=json.loads((root/s['receipt']['path']).read_text());m=json.loads((root/s['raw_manifest']['path']).read_text())
        require(b['run_id']==parent.name and b['final_logs']['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF', 'UNSETTLED_OWNED_PROCESS')
        elapsed=b['monitored_elapsed_through_cleanup_s']
        require(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0, 'UNKNOWN_MONITORED_COST')
        actual={str(p.relative_to(root)) for p in parent.rglob('*') if p.is_file()}
        require(actual==set(m['files']) and all(sha(root/p)==h for p,h in m['files'].items()), 'SETTLEMENT_RAW_DRIFT')
        amount=sum((root/p).stat().st_size for p in actual)
        require(amount==m['bytes'], 'SETTLEMENT_BYTES_UNKNOWN')
        wall+=elapsed;size+=amount;known[parent.name]={'monitored_s':elapsed,'raw_bytes':amount}
    require(wall<TOTAL_WALL and size<TOTAL_BYTES,'TOTAL_BUDGET_EXHAUSTED')
    return dict(known_settled=known,unknown_reserved=unknown,charged_monitored_s=wall,
        charged_raw_bytes=size,remaining_s=TOTAL_WALL-wall,remaining_bytes=TOTAL_BYTES-size,
        selected_total_limits={'wall_s':TOTAL_WALL,'bytes':TOTAL_BYTES},fixed_start_count_limit=None,
        scope='ONLY_NEW_UNIFIED_STAGE_RAW; OLD_ISSUE12_EXCLUDED')
