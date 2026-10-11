"""Default offline prepare/check. Native execution needs canonical future release."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.candidate_a_native_smoke_20261011.bridge_card import prepare,validate

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group()
    g.add_argument('--prepare',action='store_true');g.add_argument('--check-card');g.add_argument('--execute')
    p.add_argument('--release');a=p.parse_args()
    if a.execute:
        if not a.release:p.error('--execute requires --release; this round has no runtime approval')
        from src.candidate_a_native_smoke_20261011.bridge import execute
        sys.exit(execute(a.execute,a.release))
    elif a.check_card:print(json.dumps({'status':'OFFLINE_CARD_CHECK', 'spec':validate(a.check_card)['spec']},indent=2))
    else:print(prepare())
