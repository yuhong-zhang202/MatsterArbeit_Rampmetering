"""Additional allocation must be explicit; old expenditure is never reset."""
import json
from pathlib import Path
from src.candidate_a_native_yellow_minqual_20261015 import budget as previous
from src.candidate_a_natural_service_20261015.profile import RAW, TASK, sha, require

APPROVAL=Path('artifacts/thesis_actuator_readiness_20261015_v1/NATIVE_BUDGET_APPROVAL.json')


def accounting(root):
    root=Path(root)
    require((root/APPROVAL).is_file(),'NEW_NUMERIC_BUDGET_NOT_APPROVED')
    approval=json.loads((root/APPROVAL).read_text())
    require(approval['status']=='USER_APPROVED_ADDITIONAL_MONITORED_BUDGET','NEW_NUMERIC_BUDGET_NOT_APPROVED')
    amount=approval['additional_monitored_s']
    require(type(amount) in (int,float) and 0<amount<=1800,'INVALID_NEW_NUMERIC_BUDGET')
    authority=approval['direct_user_authority']
    require(sha(root/authority['path'])==authority['sha256'],'NEW_BUDGET_AUTHORITY_DRIFT')
    old=previous.accounting(root)
    wall=old['charged_monitored_s'];unknown=[];known={}
    parents=list((root/RAW).iterdir()) if (root/RAW).exists() else []
    require(len(parents)<=2,'NATURAL_START_CAP_EXCEEDED')
    for parent in parents:
        receipt=parent/'outputs'/'bridge_receipt.json'
        settlement=root/TASK/'settlements'/parent.name/'SETTLEMENT.json'
        if not settlement.is_file():
            wall+=900;unknown.append(parent.name);continue
        s=json.loads(settlement.read_text())
        require(s['status']=='SETTLED_AFTER_THREE_ROLE_REVIEW' and set(s['reviews'])=={'engineering','data','science'},'NATURAL_SETTLEMENT_UNREVIEWED')
        for item in s['reviews'].values():require(sha(root/item['path'])==item['sha256'],'NATURAL_SETTLEMENT_REVIEW_DRIFT')
        require(sha(receipt)==s['receipt_sha256'],'NATURAL_SETTLEMENT_RECEIPT_DRIFT')
        r=json.loads(receipt.read_text())
        require(r['final_logs']['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF','NATURAL_SETTLEMENT_NO_EOF')
        elapsed=r['monitored_elapsed_through_cleanup_s'];wall+=elapsed;known[parent.name]=elapsed
    ceiling=previous.TOTAL_WALL+amount
    require(wall<ceiling,'NATURAL_TOTAL_BUDGET_EXHAUSTED')
    return dict(charged_monitored_s=wall,remaining_s=ceiling-wall,
        approved_total_monitored_s=ceiling,prior_stage=old,unknown_reserved=unknown,
        known_settled=known,budget_approval_sha256=sha(root/APPROVAL),start_count=len(parents))


def effective_limits(resources,bound):
    require(bound['start_count']<2,'NATURAL_START_CAP_EXCEEDED')
    return {**resources,'wall_limit_s':min(resources['wall_limit_s'],bound['remaining_s'])}
