"""Independent proposed900s scope; historical remainder is never available here."""
import json
import math
import os
from pathlib import Path
from src.candidate_a_native_yellow_minqual_20261015 import budget as previous
from src.candidate_a_natural_service_20261015.profile import RAW, TASK, RUN, HISTORICAL_RUN, sha, require

APPROVAL=Path('artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json')
SCOPE='NATURAL_QUALIFICATION_20261015_V1'
TOTAL=900


def preview(root):
    """Disclosure only: a proposal does not have a numeric available balance."""
    return dict(scope_id=SCOPE,status='PROPOSED_NOT_APPROVED',proposed_total_monitored_s=TOTAL,
        available_monitored_s=None,prior_stage=previous.accounting(Path(root)),old_remainder_pooled=False)


def accounting(root):
    root=Path(root)
    require((root/APPROVAL).is_file(),'NEW_NUMERIC_BUDGET_NOT_APPROVED')
    approval=json.loads((root/APPROVAL).read_text())
    require(approval['status']=='DIRECT_USER_APPROVED_INDEPENDENT_NUMERIC_BUDGET' and approval['scope_id']==SCOPE and approval['total_monitored_s']==TOTAL,'NEW_NUMERIC_BUDGET_NOT_APPROVED')
    authority=approval['direct_user_authority']
    require(sha(root/authority['path'])==authority['sha256'],'NEW_BUDGET_AUTHORITY_DRIFT')
    old=previous.accounting(root)
    wall=0.;unknown=[];known={}
    names=set()
    for base in (root/RAW,root/TASK/'runs'):
        for parent in base.iterdir() if base.exists() else ():
            require(parent.is_dir() and parent.name in (HISTORICAL_RUN,RUN),'UNPREPARED_NATURAL_IDENTITY')
            names.add(parent.name)
    # The live, exact outer-owned worker uses its already-reserved envelope.
    # Every other process sees even a pre-raw early failure as fully reserved.
    active=None
    from src.candidate_a_natural_service_20261015 import guardian
    if os.environ.get(guardian.CONTEXT_ENV):
        context=json.loads(Path(os.environ[guardian.CONTEXT_ENV]).read_text())
        guardian.require_worker_context(context['card_path'],context['release_path'],root)
        active=RUN;names.discard(RUN)
    require(len(names)<=2,'NATURAL_START_CAP_EXCEEDED')
    for name in sorted(names):
        parent=root/RAW/name
        settlement=root/TASK/'settlements'/parent.name/'SETTLEMENT.json'
        if not settlement.is_file():
            wall+=TOTAL;unknown.append(parent.name);continue
        s=json.loads(settlement.read_text())
        require(s['run_id']==parent.name and s['status']=='SETTLED_AFTER_THREE_ROLE_REVIEW' and set(s['reviews'])=={'engineering','data','science'},'NATURAL_SETTLEMENT_UNREVIEWED')
        for item in s['reviews'].values():require(sha(root/item['path'])==item['sha256'],'NATURAL_SETTLEMENT_REVIEW_DRIFT')
        for key in ('guardian_receipt','raw_manifest'):
            require(sha(root/s[key]['path'])==s[key]['sha256'],'NATURAL_SETTLEMENT_RECORD_DRIFT')
        r=json.loads((root/s['guardian_receipt']['path']).read_text())
        require(r['run_id']==parent.name and r['group_cleanup']['no_live_owned_members'] is True and r['native_identity_verified'] is True,'NATURAL_SETTLEMENT_NO_OWNED_EOF')
        elapsed=r['monitored_elapsed_through_cleanup_s']
        require(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0,'UNKNOWN_MONITORED_COST')
        m=json.loads((root/s['raw_manifest']['path']).read_text())
        actual={str(p.relative_to(root)) for p in parent.rglob('*') if p.is_file()}
        require(actual==set(m['files']),'NATURAL_SETTLEMENT_RAW_CLOSURE')
        require(all(sha(root/p)==v['sha256'] and (root/p).stat().st_size==v['bytes'] for p,v in m['files'].items()),'NATURAL_SETTLEMENT_RAW_DRIFT')
        require(sum(v['bytes'] for v in m['files'].values())==m['bytes'],'NATURAL_SETTLEMENT_BYTE_DRIFT')
        wall+=elapsed;known[parent.name]=elapsed
    require(wall<TOTAL,'NATURAL_TOTAL_BUDGET_EXHAUSTED_OR_RESERVED')
    return dict(scope_id=SCOPE,charged_monitored_s=wall,remaining_s=TOTAL-wall,
        approved_total_monitored_s=TOTAL,prior_stage=old,old_remainder_pooled=False,
        unknown_reserved=unknown,known_settled=known,budget_approval_sha256=sha(root/APPROVAL),start_count=len(names),active_outer_reservation=active)


def effective_limits(resources,bound):
    require(bound['start_count']<2 and not bound['unknown_reserved'],'NATURAL_START_CAP_OR_UNKNOWN_RESERVATION')
    outer=min(resources['wall_limit_s'],bound['remaining_s'])
    require(outer>30,'INSUFFICIENT_CLEANUP_RESERVE')
    return {**resources,'wall_limit_s':outer-30,'outer_wall_limit_s':outer,'cleanup_reserve_s':30}
