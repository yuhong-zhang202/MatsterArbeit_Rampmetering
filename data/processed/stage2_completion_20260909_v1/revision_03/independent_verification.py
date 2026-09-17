"""Independent full-batch archive verification. --check-only never writes."""
import argparse,csv,json,hashlib,math,xml.etree.ElementTree as E
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-only',action='store_true');args=p.parse_args()
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/stage2_completion_20260909_v1/revision_03'
ledger=json.loads((OUT/'ledger_snapshot.json').read_text());audit=json.loads((OUT/'run_audit.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(name):
 with (TABLE/name).open() as f:return list(csv.DictReader(f))
v=rows('vehicle_accounting.csv');co=rows('cohort_timeline.csv');e1=rows('e1_native.csv');merge=rows('merge_events.csv');windows=rows('run_window_summary.csv')
assert len(audit['runs'])==8 and all(r['status']=='analyzed' for r in audit['runs'])
assert ledger['budget']['actual_new_starts']==7 and ledger['budget']['retries_used']==0
results={};archive_count=0;total_pairs=0;total_vehicles=0
for run in ledger['runs']:
 rid=run['run_id'];attempt=next(a for a in run['attempts'] if a['attempt_id']==run['selected_attempt_id'])
 mapping=json.loads((ROOT/attempt['source_manifest']).read_text());assert mapping['logical_run_id']==rid
 files={Path(e['original_absolute_path']).name:ROOT/e['archive_relative_path'] for e in mapping['file_map']}
 for e in mapping['file_map']:assert sha(ROOT/e['archive_relative_path'])==e['sha256']
 archive_count+=len(mapping['file_map'])
 summary=json.loads(files['summary.json'].read_text());cmd=summary['sumo_command'];assert int(cmd[cmd.index('--seed')+1])==run['seed'] and float(cmd[cmd.index('--end')+1])==2700
 assert summary['simulation']['requested_demand_vehph']=={'M':run['q_main'],'R':run['q_ramp'],'U':360,'X':180}
 assert summary['time_windows']['measurement']=={'begin_s':0,'duration_s':1500,'end_s':1500}
 assert summary['time_windows']['clearance']=={'begin_s':1500,'duration_s':1200,'end_s':2700}
 plan={n.attrib['id'].split('_')[0]:int(n.attrib['number']) for n in E.parse(files['demand.rou.xml']).getroot().findall('flow')}
 rv=[r for r in v if r['run_id']==rid];rc=[r for r in co if r['run_id']==rid];re=[r for r in e1 if r['run_id']==rid];rm=[r for r in merge if r['run_id']==rid]
 assert len(rv)==sum(plan.values()) and len({r['vehicle_id'] for r in rv})==len(rv) and len(re)==540 and len(rc)==364 and len(rm)==plan['R']
 total_vehicles+=len(rv)
 assert {c:sum(r['class']==c for r in rv) for c in 'MRUX'}==plan
 assert all(r['schedule_time_status']=='unverified' and r['planned_time_s']=='' for r in rv)
 for node in E.parse(files['scenario.add.xml']).getroot().findall('inductionLoop'):
  raw=E.parse(files[Path(node.attrib['file']).name]).getroot().findall('interval');block=[r for r in re if r['detector_id']==node.attrib['id']];assert len(block)==90
  for a,b in zip(raw,block,strict=True):
   for x,y in [('begin','begin_s'),('end','end_s'),('flow','flow_vehph'),('speed','speed_raw_mps'),('occupancy','occupancy_pct'),('nVehContrib','nVehContrib'),('nVehEntered','nVehEntered')]:assert float(a.attrib[x])==float(b[y])
  for win,(lo,hi) in {'Full':(0,2700),'A':(0,1500),'B':(300,1500),'Post':(1500,2700)}.items():
   selected=[a.attrib for a in raw if lo<=float(a.get('begin')) and float(a.get('end'))<=hi]
   valid=[a for a in selected if int(a['nVehContrib'])>0 and float(a['speed'])>=0];weight=sum(int(a['nVehContrib']) for a in valid)
   speed=sum(float(a['speed'])*int(a['nVehContrib']) for a in valid)/weight if weight else None
   published=next(r for r in windows if r['run_id']==rid and r['entity']==node.attrib['id'] and r['window']==win and r['metric']=='speed_mps')
   if speed is None:assert published['value']==''
   else:assert abs(float(published['value'])-speed)<1e-10
 trip={n.attrib['id']:n.attrib for n in E.parse(files['tripinfo.xml']).getroot().findall('tripinfo')}
 for r in rc:
  t=int(r['time_s']);sub=[n for k,n in trip.items() if k.startswith(r['class']+'_flow.')]
  assert int(r['entered_before'])==sum(0<=float(n['depart'])<t for n in sub)
  assert int(r['arrived_before'])==sum(0<=float(n['arrival'])<t for n in sub)
  if t not in [1500,2700]:assert r['outside_confirmed']==''
  if t==2700:assert r['fcd_available']=='False' and r['fcd_raw_in_network']=='' and int(r['outside_confirmed'])==0 and int(r['in_network_before'])==0
  if t in [1500,2700]:assert int(r['planned_before'])==int(r['outside_confirmed'])+int(r['in_network_before'])+int(r['arrived_before'])
 events={r['vehicle_id']:r for r in rm};matched=set();frames=0
 for _,step in E.iterparse(files['fcd.xml'],events=('end',)):
  if step.tag!='timestep':continue
  t=float(step.attrib['time']);frames+=1
  if t%30==0:
   for c in 'MRUX':
    published=next(r for r in rc if float(r['time_s'])==t and r['class']==c)
    group=[n for n in step if n.get('id').startswith(c+'_flow.')]
    assert int(published['fcd_raw_in_network'])==len(group)
    assert int(published['fcd_raw_stopped'])==sum(float(n.get('speed'))<=.1 for n in group)
  for n in step:
   event=events.get(n.get('id'))
   if event:
    for field,lane in [('previous_time_s','previous_lane'),('first_downstream_time_s','first_downstream_lane')]:
     if t==float(event[field]):assert n.get('lane')==event[lane];matched.add((n.get('id'),field))
  step.clear()
 assert frames==2700 and len(matched)==2*plan['R'];total_pairs+=len(matched)
 a=next(r for r in audit['runs'] if r['run_id']==rid);assert a['core_evidence_status']=='passed_for_descriptive_contract' and a['clearance_status']=='complete'
 assert a['qualification']=={'plan_count_status':'verified_declared_flow_number','schedule_time_status':'unverified','departure_coverage_status':'verified','arrival_coverage_status':'verified'}
 def metric(win,key):return float(next(r['value'] for r in windows if r['run_id']==rid and r['family']=='E1_group' and r['window']==win and r['metric']==key))
 boundary={r['class']:r for r in rc if int(r['time_s'])==1500}
 response={'M_request_vehph':run['q_main'],'R_request_vehph':run['q_ramp'],'internal_M_A_flow_vehph':metric('A','flow_vehph'),'internal_M_A_speed_mps':metric('A','speed_mps'),'internal_M_B_flow_vehph':metric('B','flow_vehph'),'internal_M_B_speed_mps':metric('B','speed_mps'),'internal_M_Full_contributions':metric('Full','nVehContrib'),'R_first_downstream_before1500':sum(float(r['first_downstream_time_s'])<1500 for r in rm),'R_outside1500':int(boundary['R']['outside_confirmed']),'U_outside1500':int(boundary['U']['outside_confirmed']),'R_in_network1500':int(boundary['R']['in_network_before']),'U_in_network1500':int(boundary['U']['in_network_before']),'R_arrived1500':int(boundary['R']['arrived_before']),'U_arrived1500':int(boundary['U']['arrived_before']),'last_departure_s':a['last_actual_departure_s'],'last_arrival_s':a['last_arrival_s']}
 for c in 'MRUX':response[c+'_post_departures']=sum(float(n['depart'])>=1500 for k,n in trip.items() if k.startswith(c+'_flow.'))
 assert response['internal_M_Full_contributions']==plan['M']
 results[rid]={'plan':plan,'response':response,'raw_E1_rows':len(re),'merge_brackets':len(rm),'merge_bin_ambiguous':sum(r['boundary_30s_ambiguous']=='True' for r in rm),'invalid_E1_speed_with_contributions':a['invalid_E1_speed_with_contributions'],'no_contribution_speed_intervals':sum(r['missing_reason']=='no_vehicle_contributions' for r in re),'unknown_schedule':True,'censoring':False}
# Every published contrast is checked from independently selected source table values.
lookup={(r['run_id'],r['family'],r['entity'],r['window'],r['metric']):r for r in windows}
contrasts=json.loads((OUT/'comparison.json').read_text())['contrasts']
for c in contrasts:
 treat,base=c['contrast'].split('-');key=(c['family'],c['entity'],c['window'],c['metric'])
 a=lookup[(treat,*key)]['value'];b=lookup[(base,*key)]['value']
 if a=='' or b=='':assert c['difference'] is None
 else:assert abs(float(a)-float(b)-c['difference'])<1e-10
core_contrasts={}
for prefix in ['ML','MH','RL']:
 core_contrasts[prefix]={}
 for key in results['C17']['response']:
  if key.endswith('request_vehph'):continue
  differences=[results[prefix+str(seed)]['response'][key]-results['C'+str(seed)]['response'][key] for seed in [17,23]]
  directions=[0 if d==0 else 1 if d>0 else -1 for d in differences]
  core_contrasts[prefix][key]={'seed17_difference':differences[0],'seed23_difference':differences[1],'direction_matches':directions[0]==directions[1]}
manifest=json.loads((OUT/'manifest.json').read_text())
for path,h in {**manifest['source_sha256'],**manifest['output_sha256']}.items():assert sha(path)==h,path
assert archive_count==232
report={'status':'passed','runs':results,'core_same_seed_contrasts':core_contrasts,'archive_files_verified':archive_count,'unique_vehicle_rows':total_vehicles,'E1_raw_rows':len(e1),'cohort_rows':len(co),'merge_raw_endpoint_records':total_pairs,'published_contrasts_verified':len(contrasts),'coverage_rows':8,'pending_runs':0,'starts':7,'retries':0,'mode':'check_only' if args.check_only else 'create_report','command':'.venv/bin/python data/processed/stage2_completion_20260909_v1/revision_03/independent_verification.py --check-only','script_sha256':sha(__file__),'limitations':'Two seeds only; schedule and E1 per-ID completeness unverified. Raw passage speed is not capacity/Breakdown. No mechanistic causal inference.'}
if not args.check_only:
 with (OUT/'independent_verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'status':'passed','archive_files':archive_count,'vehicles':total_vehicles,'E1_rows':len(e1),'merge_endpoints':total_pairs,'contrasts':len(contrasts),'mode':report['mode']}))
