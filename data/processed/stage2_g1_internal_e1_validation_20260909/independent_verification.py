"""Independent raw-window calculation for the targeted E1 validation."""
import csv,json,hashlib
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables'/BATCH.name
RUN=Path('/private/tmp/minimal_uncontrolled__5s3s06d')
manifest=json.loads((BATCH/'manifest.json').read_text())
diag=json.loads((BATCH/'diagnostic.json').read_text())
windows={'full':(0,2700),'A':(0,1500),'B':(300,1500),'post':(1500,2700)}
rows=[]
for node in E.parse(RUN/'scenario.add.xml').getroot().findall('inductionLoop'):
 if not node.get('id').startswith('mainline_merge_entry'):continue
 raw=[n.attrib for n in E.parse(node.attrib['file']).getroot().findall('interval')]
 for name,(a,b) in windows.items():
  chosen=[v for v in raw if a<=float(v['begin']) and float(v['end'])<=b]
  n=sum(int(v['nVehContrib']) for v in chosen)
  valid=[v for v in chosen if int(v['nVehContrib'])>0 and float(v['speed'])>=0]
  weight=sum(int(v['nVehContrib']) for v in valid)
  speed=sum(float(v['speed'])*int(v['nVehContrib']) for v in valid)/weight if weight else None
  flow=3600*n/(b-a)
  reported=diag['window_summaries'][name]['lane_summaries'][node.attrib['lane']]
  assert reported['nVehContrib']==n
  assert abs(reported['speed_mps']-speed)<1e-12
  assert abs(reported['flow_vehph']-flow)<1e-9
  rows.append({'window':name,'detector':node.attrib['id'],'lane':node.attrib['lane'],'begin_s':a,'end_s':b,'intervals':len(chosen),'nVehContrib':n,'nVehEntered':sum(int(v['nVehEntered']) for v in chosen),'speed_mps':speed,'flow_vehph':flow,'occupancy_pct':sum(float(v['occupancy'])*(float(v['end'])-float(v['begin'])) for v in chosen)/(b-a),'no_contribution_intervals':sum(int(v['nVehContrib'])==0 for v in chosen)})
with (TABLE/'internal_e1_windows.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
for path,h in {**manifest['source_sha256'],**manifest['output_sha256']}.items():assert sha(path)==h,path
report={'status':'passed_for_declared_scope','command':'.venv/bin/python data/processed/stage2_g1_internal_e1_validation_20260909/independent_verification.py','raw_independent_lane_window_summaries':len(rows),'independent_method':'Read raw XML without production functions; recompute weighted speed and contribution-derived flow; compare with diagnostic.','dedicated_tests':'4 standard-library tests passed; no simulation','per_ID_coverage':'not_verified','source_and_initial_artifact_hashes_unchanged':True,'supplement_sha256':{str(TABLE/'internal_e1_windows.csv'):sha(TABLE/'internal_e1_windows.csv'),str(Path(__file__).resolve()):sha(__file__),str(ROOT/'tests/test_internal_e1_analysis.py'):sha(ROOT/'tests/test_internal_e1_analysis.py')}}
with (BATCH/'independent_verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report,indent=2))
