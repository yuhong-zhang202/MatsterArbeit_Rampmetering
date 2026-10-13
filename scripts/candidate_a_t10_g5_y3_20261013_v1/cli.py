"""Prepare/check only today; future execution needs separate exact canonical gate."""
from pathlib import Path
import sys,argparse,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.candidate_a_t10_g5_y3_20261013.profile import prepare,validate
if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--check-card');g.add_argument('--execute');p.add_argument('--release');a=p.parse_args()
 if a.execute:
  if not a.release:p.error('--execute requires future exact canonical release')
  from src.candidate_a_t10_g5_y3_20261013.bridge import execute
  sys.exit(execute(a.execute,a.release))
 elif a.check_card:print(json.dumps(validate(a.check_card)['spec'],indent=2))
 else:print(prepare())
