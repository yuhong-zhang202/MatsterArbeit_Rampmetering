"""Prepare/check three Issue12 cards by default; execute only exact released identity."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.candidate_a_issue12_signal_policy_20261012.profile import RUNS,ACTIVE_RUNS,prepare,validate
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--check-card');g.add_argument('--execute');p.add_argument('--release');p.add_argument('--run',choices=tuple(RUNS));a=p.parse_args()
    if a.execute:
        if not a.release:p.error('--execute requires canonical per-run release')
        from src.candidate_a_issue12_signal_policy_20261012.bridge import execute
        sys.exit(execute(a.execute,a.release))
    elif a.check_card:print(json.dumps({'status':'OFFLINE_THREE_CYCLE_CARD_CHECK','spec':validate(a.check_card)['spec']},indent=2))
    else:
        for run in ((a.run,) if a.run else tuple(ACTIVE_RUNS)):print(prepare(run))
