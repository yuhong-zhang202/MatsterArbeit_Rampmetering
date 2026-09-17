"""Recheck revision_02 independently, archive-only; --check-only writes nothing."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as E
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-only',action='store_true');args=p.parse_args()
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/stage2_completion_20260909_v1/revision_02'
ledger=json.loads((OUT/'ledger_snapshot.json').read_text());audit=json.loads((OUT/'run_audit.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(name):
 with (TABLE/name).open() as f:return list(csv.DictReader(f))
v=rows('vehicle_accounting.csv');co=rows('cohort_timeline.csv');e1=rows('e1_native.csv');merge=rows('merge_events.csv');windows=rows('run_window_summary.csv')
assert len(audit['runs'])==8 and sum(r['status']=='pending' for r in audit['runs'])==6
assert json.loads((OUT/'comparison.json').read_text())['contrasts']==[]
results={};archive_count=0
for rid in ['C17','C23']:
 run=next(r for r in ledger['runs'] if r['run_id']==rid);attempt=next(a for a in run['attempts'] if a['attempt_id']==run['selected_attempt_id'])
 mapping=json.loads((ROOT/attempt['source_manifest']).read_text());assert mapping['logical_run_id']==rid
 files={Path(e['original_absolute_path']).name:ROOT/e['archive_relative_path'] for e in mapping['file_map']}
 for e in mapping['file_map']:assert sha(ROOT/e['archive_relative_path'])==e['sha256']
 archive_count+=len(mapping['file_map'])
 summary=json.loads(files['summary.json'].read_text());cmd=summary['sumo_command'];assert int(cmd[cmd.index('--seed')+1])==run['seed']
 rv=[r for r in v if r['run_id']==rid];rc=[r for r in co if r['run_id']==rid];re=[r for r in e1 if r['run_id']==rid];rm=[r for r in merge if r['run_id']==rid]
 assert len(rv)==1858 and len({r['vehicle_id'] for r in rv})==1858 and len(re)==540 and len(rc)==364 and len(rm)==300
 assert {c:sum(r['class']==c for r in rv) for c in 'MRUX'}=={'M':1333,'R':300,'U':150,'X':75}
 assert all(r['schedule_time_status']=='unverified' and r['planned_time_s']=='' for r in rv)
 for node in E.parse(files['scenario.add.xml']).getroot().findall('inductionLoop'):
  raw=E.parse(files[Path(node.attrib['file']).name]).getroot().findall('interval');block=[r for r in re if r['detector_id']==node.attrib['id']];assert len(block)==90
  for a,b in zip(raw,block,strict=True):
   for x,y in [('begin','begin_s'),('end','end_s'),('flow','flow_vehph'),('speed','speed_raw_mps'),('occupancy','occupancy_pct'),('nVehContrib','nVehContrib'),('nVehEntered','nVehEntered')]:assert float(a.attrib[x])==float(b[y])
 trip={n.attrib['id']:n.attrib for n in E.parse(files['tripinfo.xml']).getroot().findall('tripinfo')}
 for r in rc:
  t=int(r['time_s']);sub=[n for k,n in trip.items() if k.startswith(r['class']+'_flow.')]
  assert int(r['entered_before'])==sum(0<=float(n['depart'])<t for n in sub)
  assert int(r['arrived_before'])==sum(0<=float(n['arrival'])<t for n in sub)
  if t not in [1500,2700]:assert r['outside_confirmed']==''
  if t==2700:assert r['fcd_available']=='False' and r['fcd_raw_in_network']=='' and int(r['outside_confirmed'])==0 and int(r['in_network_before'])==0
 # Independent complete endpoint-pair check, not production crossing logic.
 events={r['vehicle_id']:r for r in rm};matched=set()
 for _,step in E.iterparse(files['fcd.xml'],events=('end',)):
  if step.tag!='timestep':continue
  t=float(step.attrib['time'])
  for n in step:
   e=events.get(n.get('id'))
   if e:
    for field,lane in [('previous_time_s','previous_lane'),('first_downstream_time_s','first_downstream_lane')]:
     if t==float(e[field]):assert n.get('lane')==e[lane];matched.add((n.get('id'),field))
  step.clear()
 assert len(matched)==600
 at1500={r['class']:int(r['outside_confirmed']) for r in rc if int(r['time_s'])==1500}
 r_a=sum(float(r['first_downstream_time_s'])<1500 for r in rm)
 a=next(r for r in audit['runs'] if r['run_id']==rid);assert a['core_evidence_status']=='passed_for_descriptive_contract'
 internal={r['window']:float(r['value']) for r in windows if r['run_id']==rid and r['family']=='E1_group' and r['metric']=='nVehContrib'}
 assert internal['Full']==1333
 results[rid]={'archive_files':len(mapping['file_map']),'unique_vehicles':len(rv),'E1_rows':len(re),'cohort_rows':len(rc),'merge_raw_endpoint_records':len(matched),'R_before1500':r_a,'merge_bin_ambiguous':sum(r['boundary_30s_ambiguous']=='True' for r in rm),'outside_at1500':at1500,'internal_contributions':internal,'qualification':a['qualification'],'last_arrival_s':a['last_arrival_s']}
manifest=json.loads((OUT/'manifest.json').read_text())
for path,h in {**manifest['source_sha256'],**manifest['output_sha256']}.items():assert sha(path)==h,path
report={'status':'passed','runs':results,'archive_files_verified':archive_count,'coverage_rows':8,'pending_runs':6,'comparisons':0,'tests':'25 pure-offline tests plus compile/diffcheck passed','mode':'check_only' if args.check_only else 'create_report','command':'.venv/bin/python data/processed/stage2_completion_20260909_v1/revision_02/independent_verification.py --check-only','script_sha256':sha(__file__),'limitations':'Schedule and per-ID E1 completeness remain unverified; no significance or breakdown claim.'}
if not args.check_only:
 with (OUT/'independent_verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report,indent=2))
