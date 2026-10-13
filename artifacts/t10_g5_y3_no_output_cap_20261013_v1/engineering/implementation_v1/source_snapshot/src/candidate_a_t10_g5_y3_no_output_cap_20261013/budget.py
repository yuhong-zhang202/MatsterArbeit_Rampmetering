"""New single-identity proposed envelope; no old budget carry or silent retry."""
from pathlib import Path
from src.candidate_a_t10_g5_y3_no_output_cap_20261013.profile import RAW,require
TOTAL_WALL=300;TOTAL_BYTES=None

def accounting(root):
    allocated=Path(root)/RAW
    require(not allocated.exists() or not list(allocated.iterdir()),'CANDIDATE_ALREADY_ALLOCATED_OR_UNKNOWN_RESERVATION')
    return {'charged_monitored_s':0,'charged_raw_bytes':0,'unknown_reserved':[],
        'remaining_s':TOTAL_WALL,'remaining_bytes':TOTAL_BYTES,
        'selected_total_limits':{'wall_s':TOTAL_WALL,'bytes':TOTAL_BYTES},
        'scope':'NEW_SINGLE_CARD_ENVELOPE_REQUIRES_FUTURE_EXPLICIT_RESOURCE_APPROVAL_NO_OLD_REMAINDER'}
def effective_limits(resources,bound):
    return {**resources,'wall_limit_s':min(resources['wall_limit_s'],bound['remaining_s']),
        'run_limit_bytes':None}
