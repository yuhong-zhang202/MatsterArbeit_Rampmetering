"""Audit exactly one independently released remaining-seed receipt, no simulation."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('run_id');a=ap.parse_args();rid=a.run_id
 release=json.load((ROOT/'artifacts/formal_development_20261007_v1/RELEASE_FIX02_SEEDS23_42_A03.json').open());p=ROOT/'artifacts/formal_development_20261007_v1/inputs'/rid/'card.json'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==release['cards'][rid]
 card=json.load(p.open());out=f"FIX02_{card['treatment']}_R{card['ramp_veh_h']}_S{card['seed']}_A03";base=ROOT/f"artifacts/stage6_boundary_search_20261002_v1/inputs/M3600_R{card['ramp_veh_h']}_S{card['seed']}/card.json"
 subprocess.run([sys.executable,str(B/'analyze_fix02.py'),'--card',str(p),'--baseline-card',str(base),'--out-name',out,'--queue-parameters',str(ROOT/'artifacts/formal_development_20261007_v1/PINNED_PARAMETER_CONTRACT.json')],check=True)
 subprocess.run([sys.executable,str(B/'write_fix02_gate.py'),'--audit',out,'--card',str(p)],check=True)
if __name__=='__main__':main()
