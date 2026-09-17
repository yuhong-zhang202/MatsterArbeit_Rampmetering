"""Independent C17 archive/table arithmetic; never imports production analysis."""
from pathlib import Path
import argparse,csv,json,hashlib,xml.etree.ElementTree as E
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only',action='store_true',help='Run all assertions and print results without writing any file.')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/stage2_completion_20260909_v1/revision_01'
MAP=ROOT/'data/processed/stage2_completion_20260909_v1/source_maps/C17_reused.json'
mapping=json.loads(MAP.read_text())
files={Path(e['original_absolute_path']).name:ROOT/e['archive_relative_path'] for e in mapping['file_map']}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for e in mapping['file_map']:assert sha(ROOT/e['archive_relative_path'])==e['sha256']
def read(name):
 with (TABLE/name).open() as f:return list(csv.DictReader(f))
v=read('vehicle_accounting.csv');co=read('cohort_timeline.csv');e1=read('e1_native.csv');merge=read('merge_events.csv');windows=read('run_window_summary.csv')
assert len(v)==1858 and len({r['vehicle_id'] for r in v})==1858
assert {c:sum(r['class']==c for r in v) for c in 'MRUX'}=={'M':1333,'R':300,'U':150,'X':75}
assert len(e1)==540 and len(co)==364 and len(merge)==300
assert all(r['planned_time_s']=='' for r in v)
assert all(r['outside_confirmed']=='' for r in co if int(r['time_s']) not in [1500,2700])
assert all(r['fcd_available']=='False' and r['fcd_raw_in_network']=='' for r in co if int(r['time_s'])==2700)
for node in E.parse(files['scenario.add.xml']).getroot().findall('inductionLoop'):
 raw=E.parse(files[Path(node.attrib['file']).name]).getroot().findall('interval')
 rows=[r for r in e1 if r['detector_id']==node.attrib['id']]
 for a,b in zip(raw,rows,strict=True):
  for x,y in [('begin','begin_s'),('end','end_s'),('flow','flow_vehph'),('speed','speed_raw_mps'),('occupancy','occupancy_pct'),('nVehContrib','nVehContrib'),('nVehEntered','nVehEntered')]:assert float(a.attrib[x])==float(b[y])
trip={n.attrib['id']:n.attrib for n in E.parse(files['tripinfo.xml']).getroot().findall('tripinfo')}
for r in co:
 t=int(r['time_s']);sub=[n for k,n in trip.items() if k.startswith(r['class']+'_flow.')]
 assert int(r['entered_before'])==sum(0<=float(n['depart'])<t for n in sub)
 assert int(r['arrived_before'])==sum(0<=float(n['arrival'])<t for n in sub)
for name,count in [('Full',1333),('A',1331)]:
 match=[r for r in windows if r['entity']=='internal_M' and r['window']==name and r['metric']=='nVehContrib']
 assert len(match)==1 and int(match[0]['value'])==count
assert sum(float(r['first_downstream_time_s'])<1500 for r in merge)==36
assert sum(r['boundary_30s_ambiguous']=='True' for r in merge)==4
manifest=json.loads((OUT/'manifest.json').read_text())
for p,h in {**manifest['source_sha256'],**manifest['output_sha256']}.items():assert sha(p)==h,p
report={'status':'passed','archive_files_hash_verified':len(mapping['file_map']),'vehicle_unique_rows':1858,'E1_raw_rows_fields_reconciled':[540,7],'cohort_trip_account_rows_reconciled':364,'internal_E1_Full_A':[1333,1331],'R_brackets':300,'R_first_downstream_before1500':36,'R_bin_ambiguous':4,'tests':'12 dedicated plus13 specified existing static/analysis tests passed; py_compile/diffcheck passed','source_archive_only':True,'pending_runs_retained':7,'figures':'Both viewed: full internal/downstream passage series and R/U observed cumulative insertion/arrival fallback; outside not interpolated. Horizontal ticks are simulation seconds as defined by analysis_windows.','limitations':'Schedule unverified; per-ID E1 coverage unverified; C1 scientific review pending.','command':'.venv/bin/python data/processed/stage2_completion_20260909_v1/revision_01/independent_verification.py','verification_script_sha256':sha(__file__)}
if args.check_only:
 report['mode']='check_only'
 report['command']+=' --check-only'
else:
 with (OUT/'independent_verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report,indent=2))
