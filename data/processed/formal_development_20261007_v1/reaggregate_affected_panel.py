"""Minimum raw reaggregation of one historical mean-speed panel only."""
import csv,gzip,hashlib,json,sys,xml.etree.ElementTree as E
from pathlib import Path
from collections import defaultdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
run='M3600_R750_S17';raw=ROOT/'data/raw/stage6_boundary_search_20261002_v1'/run/'outputs';old=ROOT/'data/processed/stage6_boundary_search_20261002_v1'/run;out=HERE/'PANEL_R750_S17_RAW_REAGG';out.mkdir()
lanes={'main_up_0','main_up_1',':freeway_merge_0_0',':freeway_merge_0_1','merge_section_1','merge_section_2',':merge_end_0_0',':merge_end_0_1','main_down_0','main_down_1'}
bins=defaultdict(lambda:[0,0.]);labels=0
for _,e in E.iterparse(gzip.open(raw/'fcd.xml.gz','rb'),events=('end',)):
 if e.tag!='timestep':continue
 t=float(e.get('time'));assert t==labels;labels+=1
 for v in e:
  if not v.get('id','').startswith('M_') or v.get('lane') not in lanes:continue
  x=float(v.get('x'));speed=float(v.get('speed'));assert speed>=0
  if not 0<=x<=2200:continue
  cell=min(int(x//100),21);b=int(t//30);z=bins[(b,cell)];z[0]+=1;z[1]+=speed
 e.clear()
assert labels==4200
rows=[]
for b in range(140):
 for cell in range(22):
  n,total=bins[(b,cell)];rows.append(dict(begin=b*30,cell=cell,lane_track='pooled',samples=n,speed_mps=total/n if n else ''))
with (old/'mainline_cells.csv').open() as f:historical={(int(float(r['begin'])),int(r['cell'])):r for r in csv.DictReader(f) if r['lane_track']=='pooled'}
assert len(historical)==len(rows)==3080
max_residual=0.
for r in rows:
 h=historical[(r['begin'],r['cell'])];assert int(h['samples'])==r['samples']
 if r['samples']:d=abs(float(h['speed_mps'])-r['speed_mps']);assert d<1e-12;max_residual=max(max_residual,d)
 else:assert h['speed_mps']==''
with (out/'mainline_cells.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'status':'PASS_RAW_REAGGREGATED_PANEL','run_id':run,'scope':'Only pooled M mean-speed samples in fixed30s/100m x-coordinate cells, used by checkpoint heatmap. Not a revalidation of all historical derived metrics or state classifier.','FCD_timesteps':labels,'cells_compared':3080,'historical_sample_counts_all_equal':True,'speed_max_residual_m_s':max_residual,'historical_script_sha256':json.loads((old/'summary.json').read_text())['source_hashes'][str(ROOT/'scripts/stage6/boundary_search_20261002/analyze.py')],'current_historical_script_sha256':sha(ROOT/'scripts/stage6/boundary_search_20261002/analyze.py'),'sources':{str(p):sha(p) for p in [raw/'fcd.xml.gz',old/'mainline_cells.csv',Path(__file__)]},'output_sha256':sha(out/'mainline_cells.csv')}
with (out/'PANEL_REAGGREGATION.json').open('x') as f:json.dump(report,f,indent=2)
with (out/'analysis_source_snapshot.py').open('x') as f:f.write(Path(__file__).read_text())
print(json.dumps(report))
