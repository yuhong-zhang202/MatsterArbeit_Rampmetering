"""Approved NEW-stage envelope. Unsettled reservations charge their full ceilings."""
from pathlib import Path
import json, math
from src.candidate_a_issue12_packet_policy_20261012.budget import sha, require
from src.candidate_a_dynamic_minqual_20261015.profile import RUNS
TOTAL_WALL=600
TOTAL_BYTES=None
SINGLE_WALL=300
SINGLE_BYTES=None
RAW=Path('data/raw/dynamic_minimum_qualification_20261015_v1')
SETTLEMENTS=Path('artifacts/dynamic_minimum_qualification_20261015_v1/engineering/settlements')


def accounting(root):
    root=Path(root);known={};unknown=[];wall=0.;size=0
    for parent in (root/RAW).iterdir() if (root/RAW).exists() else ():
        require(parent.is_dir() and parent.name in RUNS, 'UNKNOWN_NEW_RAW_ALLOCATION')
        settlement=root/SETTLEMENTS/parent.name/'SETTLEMENT.json'
        if not settlement.exists():
            unknown.append(parent.name);wall+=300;size+=sum(p.stat().st_size for p in parent.rglob("*") if p.is_file());continue
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
        require(actual==set(m['files']) and all(sha(root/p)==item['sha256'] and (root/p).stat().st_size==item['bytes'] for p,item in m['files'].items()), 'SETTLEMENT_RAW_DRIFT')
        amount=sum((root/p).stat().st_size for p in actual)
        require(amount==m['bytes'], 'SETTLEMENT_BYTES_UNKNOWN')
        wall+=elapsed;size+=amount;known[parent.name]={'monitored_s':elapsed,'raw_bytes':amount}
    require(not unknown,'PREVIOUS_RUN_REQUIRES_THREE_ROLE_SETTLEMENT')
    require(wall<TOTAL_WALL,'TOTAL_BUDGET_EXHAUSTED')
    return dict(known_settled=known,unknown_reserved=unknown,charged_monitored_s=wall,
        charged_raw_bytes=size,remaining_s=TOTAL_WALL-wall,remaining_bytes=None,
        selected_total_limits={'wall_s':TOTAL_WALL,'bytes':TOTAL_BYTES},fixed_start_count_limit=None,
        scope='ONLY_NEW_TWO_MINQUAL_IDENTITIES; ALL_OLD_STAGES_EXCLUDED')


def effective_limits(resources,bound):
    require(not bound['unknown_reserved'] and bound['remaining_s']>0,'UNSETTLED_OR_EXHAUSTED_NEW_ENVELOPE')
    return {**resources,'wall_limit_s':min(resources['wall_limit_s'],bound['remaining_s']),'run_limit_bytes':None}
