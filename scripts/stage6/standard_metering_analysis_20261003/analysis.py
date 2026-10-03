"""Read-only paired measurement utilities. Reuse reviewed boundary classifier unchanged."""
import argparse,csv,gzip,hashlib,importlib.util,json,math
from pathlib import Path
from collections import Counter,defaultdict
from itertools import zip_longest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('reviewed_boundary',ROOT/'scripts/stage6/boundary_search_20261002/analyze.py')
boundary=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(boundary)

def sha(p):return boundary.sha(p)
def validate_current_receipt(raw,card_path=None):
 """Current runner uses files; normalize in memory without modifying raw."""
 raw=Path(raw);receipt=json.loads((raw/'execution_receipt.json').read_text())
 if receipt.get('status')!='COMPLETED' or receipt.get('return_code')!=0:raise ValueError('execution not completed')
 manifest=receipt.get('files',receipt.get('output_manifest'))
 if not isinstance(manifest,dict) or not manifest:raise ValueError('missing receipt manifest')
 for name,meta in manifest.items():
  if Path(name).name!=name:raise ValueError('unsafe manifest path')
  path=raw/name
  if path.stat().st_size!=meta['bytes'] or sha(path)!=meta['sha256']:raise ValueError('manifest hash '+name)
 if card_path and sha(card_path)!=receipt['card_sha256']:raise ValueError('card receipt mismatch')
 return dict(receipt,output_manifest=manifest)
# Only this imported adapter instance changes; historical classifier source remains immutable.
boundary.validate_receipt=validate_current_receipt
def open_xml(p):return gzip.open(p,'rb') if str(p).endswith('.gz') else open(p,'rb')
def records(path,tag):
 with open_xml(path) as f:
  for _,e in ET.iterparse(f,events=('end',)):
   if e.tag==tag:
    yield e
    e.clear()
def canonical(e):
 return (e.tag,tuple(sorted(e.attrib.items())),tuple(sorted(canonical(x) for x in e)))
def compare_records(a,b,tag,cutoff=None,ignored_attributes=()):
 """Ignore XML headers/comments and attribute/record order within one label only."""
 def iterator(p):
  for e in records(p,tag):
   if cutoff is not None and float(e.get('time'))>=cutoff:break
   for key in ignored_attributes:e.attrib.pop(key,None)
   yield canonical(e)
 n=0;different=0;first=None
 for left,right in zip_longest(iterator(a),iterator(b)):
  n+=1
  if left!=right:
   different+=1
   if first is None:first={'record_index':n-1,'left':left,'right':right}
 return dict(records_compared=n,different_records=different,first_difference=first,equal=different==0)
def neutral_compare(left,right):
 left,right=Path(left),Path(right);result={};sources={}
 for filename,tag in [('fcd.xml.gz','timestep'),('tripinfo.xml','tripinfo'),('vehroute.xml','vehicle'),('tls_states.xml','tlsState'),('sumo_summary.xml','step'),('lanechanges.xml','change')]:
  paths=[p/filename for p in (left,right)]
  if not all(p.exists() for p in paths):raise ValueError('missing neutral output '+filename)
  result[filename]=compare_records(*paths,tag,ignored_attributes=('duration',) if filename=='sumo_summary.xml' else ())
  if filename=='sumo_summary.xml':result[filename]['excluded_computation_duration_ms']={str(p):[e.get('duration') for e in records(p,'step')] for p in paths}
  for p in paths:sources[str(p.resolve())]=sha(p)
 detectors=set(p.name for p in left.glob('p1_*.xml'))|set(p.name for p in left.glob('*_e2.xml'))
 other=set(p.name for p in right.glob('p1_*.xml'))|set(p.name for p in right.glob('*_e2.xml'))
 if detectors!=other or len(detectors)!=11:raise ValueError('detector set mismatch')
 for filename in sorted(detectors):
  paths=[p/filename for p in (left,right)];result[filename]=compare_records(*paths,'interval')
  for p in paths:sources[str(p.resolve())]=sha(p)
 return dict(equal=all(r['equal'] for r in result.values()),comparisons=result,sources=sources,script_sha256=sha(__file__),qualification='Exact stored values; a difference is retained and requires investigation, not automatic baseline replacement.')
def pre600(left,right):return compare_records(left,right,'timestep',600)
def paired_classes(left,right):
 l={r['vehicle_class']:r for r in left};r={r['vehicle_class']:r for r in right}
 if set(l)!=set('MRUX') or set(r)!=set(l):raise ValueError('class coverage')
 out=[]
 for c,n in dict(M=3000,R=600,U=300,X=150).items():
  if l[c]['planned']!=n or r[c]['planned']!=n:raise ValueError('requested count mismatch')
  for field in ['planned','inserted','arrived','unfinished','undeparted','scheduled_system_time_observed_total_s','external_wait_observed_total_s','in_network_observed_total_s']:
   a,b=l[c][field],r[c][field];out.append(dict(vehicle_class=c,metric=field,OPEN=a,CONTROL=b,difference=b-a))
 return out

def city_evidence(fcd,tls,horizon=4200):
 """All urban/ramp lane evidence; no continuous-chain or unique causal claim."""
 states={}
 for e in records(tls,'tlsState'):
  key=(float(e.get('time')),e.get('id'))
  if key in states:raise ValueError('duplicate TLS time/id')
  states[key]=e.get('state')
 for name in ['urban_tls','ramp_mid']:
  if {t for t,i in states if i==name}!=set(range(horizon)):raise ValueError('TLS coverage '+name)
 bins=defaultdict(Counter);observations=[];counts=0
 for e in records(fcd,'timestep'):
  t=float(e.get('time'))
  if t!=counts:raise ValueError('FCD label gap')
  counts+=1;lanes=defaultdict(list);seen=set()
  for v in e:
   vid=v.get('id')
   if vid in seen:raise ValueError('duplicate FCD ID')
   seen.add(vid);lane=v.get('lane');speed=boundary.number(v.get('speed'))
   if lane.startswith(('urban_','shared_',':urban_','ramp_',':ramp_')):
    lanes[lane].append(dict(id=vid,vehicle_class=boundary.vehicle_class(vid),speed=speed,pos=boundary.number(v.get('pos'))))
  for lane,vs in lanes.items():
   vs.sort(key=lambda v:(v['pos'],v['id']))
   for index,v in enumerate(vs):
    r=bins[(int(t//30)*30,lane,v['vehicle_class'])];r['vehicle_seconds']+=1
    for label,threshold in [('slow_lt1p389',1.389),('stop_lt0p1',.1),('diagnostic_lt5',5)]:r[label+'_vehicle_seconds']+=v['speed']<threshold
    if v['vehicle_class']=='U' and lane.startswith(('shared_',':urban_')) and v['speed']<1.389:
     ahead=vs[index+1] if index+1<len(vs) else None
     observations.append(dict(time=t,lane=lane,U_id=v['id'],U_pos=v['pos'],U_speed=v['speed'],ahead_id=ahead['id'] if ahead else None,ahead_class=ahead['vehicle_class'] if ahead else None,front_position_separation_m=ahead['pos']-v['pos'] if ahead else None,ahead_speed=ahead['speed'] if ahead else None,shared_slow_R_count=sum(x['vehicle_class']=='R' and x['speed']<1.389 for x in lanes.get('shared_approach_0',[])),urban_state=states[t,'urban_tls'],urban_entry_green=states[t,'urban_tls'][0] in 'Gg',ramp_state=states[t,'ramp_mid']))
 if counts!=horizon:raise ValueError('FCD horizon')
 return dict(lane_bins=[dict(begin=k[0],lane=k[1],vehicle_class=k[2],**v) for k,v in sorted(bins.items())],all_U_slow_context=observations,timesteps=counts,scope='Nearest same-lane observed front position, not net body gap or simulator leader. Named internal/urban/ramp lanes. No continuous-chain identification.',source_hashes={str(Path(p).resolve()):sha(p) for p in [fcd,tls]})

def write_json(path,data):
 with Path(path).open('x') as f:json.dump(data,f,indent=2);f.write('\n')
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
 n=sub.add_parser('neutral');n.add_argument('--open',type=Path,required=True);n.add_argument('--control',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
 c=sub.add_parser('city');c.add_argument('--raw',type=Path,required=True);c.add_argument('--out',type=Path,required=True)
 a=p.parse_args()
 if a.mode=='neutral':write_json(a.out,neutral_compare(a.open,a.control))
 else:write_json(a.out,city_evidence(a.raw/'fcd.xml.gz',a.raw/'tls_states.xml'))
if __name__=='__main__':main()


def audit_control_logs(raw,mode,noop_probe_count=1):
 """Independent timing/unit/algebra audit; service qualification remains separate."""
 raw=Path(raw)
 with (raw/'controller_steps.csv').open() as f:steps=list(csv.DictReader(f))
 with (raw/'feedback_updates.csv').open() as f:updates=list(csv.DictReader(f))
 if len(steps)!=4200:raise ValueError('controller step coverage')
 true=lambda x:str(x).lower() in {'true','1'}
 for t,r in enumerate(steps):
  if float(r['time_begin_s'])!=t or float(r['time_end_s'])!=t+1:raise ValueError('controller label mismatch')
  if r['mode']!=mode:raise ValueError('controller mode mismatch')
  if mode=='NOOP' or t<600:
   if r['observed_state']!='G' or r['requested_state']:raise ValueError('unexpected pre-treatment actuation')
  elif r['requested_state']!=r['observed_state']:raise ValueError('applied phase mismatch')
  for key in ['crossing_bracket_ids_json','red_crossing_bracket_ids_json']:
   ids=json.loads(r[key])
   if not isinstance(ids,list) or len(ids)!=len(set(ids)):raise ValueError('invalid crossing IDs')
 expected=list(range(630,4171,30)) if mode=='ALINEA' or noop_probe_count==119 else [630]
 if noop_probe_count not in (1,119):raise ValueError('unsupported probe contract')
 if len(updates)!=len(expected):raise ValueError('feedback update count')
 previous=900.
 for t,r in zip(expected,updates):
  for field,value in [('decision_time_s',t),('application_time_s',t),('interval_begin_s',t-30),('interval_end_s',t)]:
   if float(r[field])!=value:raise ValueError('feedback interval/timing')
  if not true(r['valid']):raise ValueError('invalid feedback observation')
  if mode=='NOOP':
   if any(r[k] for k in ['rate_previous_veh_h','rate_raw_veh_h','rate_clipped_veh_h']):raise ValueError('NOOP rate decision')
   continue
  vals={k:boundary.number(r[k]) for k in ['occ_l0_pct','occ_l1_pct','occ_mean_pct','target_pct','gain_veh_h_per_pct','rate_previous_veh_h','rate_raw_veh_h','rate_clipped_veh_h']}
  if any(not 0<=vals[k]<=100 for k in ['occ_l0_pct','occ_l1_pct']):raise ValueError('occupancy range')
  if vals['target_pct']!=11 or vals['gain_veh_h_per_pct']!=70:raise ValueError('candidate parameter mismatch')
  mean=(vals['occ_l0_pct']+vals['occ_l1_pct'])/2;rate=previous+70*(11-mean);clip=max(300,min(1200,rate))
  for key,value in [('occ_mean_pct',mean),('rate_previous_veh_h',previous),('rate_raw_veh_h',rate),('rate_clipped_veh_h',clip)]:
   if abs(vals[key]-value)>1e-7:raise ValueError('feedback arithmetic '+key)
  previous=clip
 return dict(timesteps=len(steps),updates=len(updates),status='PASS_TIMING_ALGEBRA_ONLY',service_qualification='Requires prospectively qualified front-vehicle and crossing evidence; not certified by this audit.',sources={str(raw/n):sha(raw/n) for n in ['controller_steps.csv','feedback_updates.csv']})

def reconcile_feedback_xml(raw):
 """Previous complete interval, detector identity/count/value independent check."""
 raw=Path(raw)
 with (raw/'feedback_updates.csv').open() as f:updates=list(csv.DictReader(f))
 detections={}
 for lane in [0,1]:
  p=raw/f'p1_main_down_20_l{lane}.xml'
  for e in records(p,'interval'):
   key=(lane,float(e.get('begin')),float(e.get('end')))
   if key in detections:raise ValueError('duplicate detector interval')
   detections[key]=dict(e.attrib)
 checked=0
 for r in updates:
  mean=0
  for lane in [0,1]:
   e=detections[lane,float(r['interval_begin_s']),float(r['interval_end_s'])]
   if e['id']!=r[f'detector_l{lane}']:raise ValueError('feedback detector ID')
   value=boundary.number(r[f'occ_l{lane}_pct'])
   if abs(value-float(e['occupancy']))>.0050001:raise ValueError('feedback/XML occupancy mismatch')
   if int(float(r[f'n_vehicle_l{lane}']))!=int(float(e['nVehContrib'])):raise ValueError('feedback/XML count mismatch')
   mean+=value/2;checked+=1
  if abs(mean-boundary.number(r['occ_mean_pct']))>1e-8:raise ValueError('feedback mean mismatch')
 return dict(checked_lane_intervals=checked,occupancy_xml_rounding_tolerance_pct=.0050001,status='PASS')

def input_card_check(card_path):
 card_path=Path(card_path);card=json.loads(card_path.read_text());raw=Path(card['output']);package=Path(card['package'])
 boundary.validate_receipt(raw,card_path)
 for name,digest in card['input_sha256'].items():
  if sha(package/name)!=digest:raise ValueError('card input hash '+name)
 if sha(package/'demand.rou.xml')!=card['base_input_sha256']['demand.rou.xml']:raise ValueError('demand not byte-matched')
 baseline=Path(card['base_output'])/'execution_receipt.json'
 if sha(baseline)!=card['base_receipt_sha256']:raise ValueError('baseline receipt hash')
 demand=boundary.demand_rows(package/'demand.rou.xml')
 if Counter(r['class'] for r in demand.values())!=dict(M=3000,R=600,U=300,X=150):raise ValueError('4050 cohort mismatch')
 return card

def reconcile_service_fcd(raw,card):
 """FCD label t is post-step state for held [t,t+1); mapping must pass S2."""
 raw=Path(raw)
 with (raw/'controller_steps.csv').open() as f:steps=list(csv.DictReader(f))
 with (raw/'vehicle_metadata.csv').open() as f:metadata={r['vehicle_id']:r for r in csv.DictReader(f)}
 via=card['meter_controlled_link']['via'];stopline=card['meter_controlled_link']['storage_length_m'];prior={};totals=Counter();mismatches=[];seen_cross=set()
 for e in records(raw/'fcd.xml.gz','timestep'):
  t=int(float(e.get('time')));row=steps[t];now={v.get('id'):dict(v.attrib) for v in e};mode=row['mode']
  if mode=='ALINEA' and t>=600:
   before={i for i,v in prior.items() if v['lane']==via};after={i for i,v in now.items() if v['lane']==via};cross=after-before
   if set(json.loads(row['internal_before_ids_json']))!=before:mismatches.append([t,'internal_before'])
   if set(json.loads(row['crossing_bracket_ids_json']))!=cross:mismatches.append([t,'crossing'])
   if cross&seen_cross:mismatches.append([t,'duplicate crossing'])
   seen_cross|=cross
   slot=str(row['slot_scheduled']).lower()=='true';qualified=str(row['queued_unblocked_slot']).lower()=='true';front=row['front_queued_vehicle_id']
   if 'guard_vehicle_states_json' in row:
    guards=json.loads(row['guard_vehicle_states_json']);storage_ids={i for i,v in prior.items() if v['lane']=='ramp_storage_0'}
    if {v['vehicle_id'] for v in guards}!=storage_ids:mismatches.append([t,'guard FCD population'])
    for v in guards:
     old=prior.get(v['vehicle_id'])
     if old and (abs(float(old['pos'])-v['position_m'])>.005001 or abs(float(old['speed'])-v['speed_m_s'])>.005001):mismatches.append([t,'guard FCD state'])
   if qualified:
    totals['qualified']+=1
    v=prior.get(front)
    if not slot or not v or v['lane']!='ramp_storage_0':mismatches.append([t,'qualification identity'])
    else:
     storage=[i for i,x in prior.items() if x['lane']=='ramp_storage_0']
     if max(storage,key=lambda i:float(prior[i]['pos']))!=front:mismatches.append([t,'not frontmost'])
     required=float(metadata[front]['vehicle_length_m'])+float(metadata[front]['min_gap_m'])
     clearance=min((float(prior[i]['pos'])-float(metadata[i]['vehicle_length_m']) for i in before),default=1e9)
     if stopline-float(v['pos'])>1.105001 or float(v['speed'])>.105001 or clearance+.005001<required:mismatches.append([t,'qualification geometry'])
     if float(row['stopline_gap_m'])>1.1 or float(row['downstream_rear_clearance_m'])<required:mismatches.append([t,'logged qualification violation'])
     if abs(float(row['required_clearance_m'])-required)>1e-8:mismatches.append([t,'required clearance'])
    totals['qualified_front_crossings']+=front in cross
    totals['wrong_front']+=bool(cross and cross!={front})
   totals['multiple_slots']+=slot and len(cross)>1;totals['red_crossings']+=len(cross) if not slot else 0
  prior=now
 if mismatches:status='FAIL_RECONCILIATION'
 elif totals['wrong_front'] or totals['multiple_slots'] or totals['red_crossings']:status='FAIL_CROSSING_SERVICE'
 elif totals['qualified']<20:status='NOT_SUFFICIENTLY_TESTED'
 elif totals['qualified_front_crossings']/totals['qualified']<.9:status='FAIL_QUALIFIED_SERVICE'
 else:status='PASS_SAMPLED_SERVICE'
 return dict(status=status,counts=dict(totals),mismatches=mismatches,crossing_definition='First internal-lane appearance bracketing held interval, not subsecond exact crossing. FCD time alignment and traversal detectability require engineering qualification.',fcd_precision_qualification='Boundary geometry uses XML rounding tolerances; logged exact qualified set is preserved.')

def analyze_card(card_path,out):
 """Run only offline analysis after a completed, hash-bound execution."""
 card=input_card_check(card_path);raw=Path(card['output']);out=Path(out)
 logs=audit_control_logs(raw,card['mode'],119 if card.get('occupancy_sampling') else 1);feedback=reconcile_feedback_xml(raw)
 config=json.loads((ROOT/'artifacts/stage6_boundary_search_20261002_v1/analysis_config.json').read_text())
 sampling=card.get('occupancy_sampling',{}).get('source')
 step_check=(reconcile_event_feedback(raw) if sampling=='TraCI E1 getVehicleData' else reconcile_step_feedback(raw)) if sampling else None
 pre=pre600(Path(card['base_output'])/'fcd.xml.gz',raw/'fcd.xml.gz')
 summary=boundary.analyze(raw,Path(card['package'])/'demand.rou.xml',config,out,Path(card_path))
 if step_check is not None:write_json(out/'step_feedback_reconciliation.json',step_check)
 write_json(out/'control_log_audit.json',logs);write_json(out/'feedback_xml_reconciliation.json',feedback);write_json(out/'pre600_comparison.json',pre)
 if card['mode']=='NOOP':write_json(out/'neutral_comparison.json',neutral_compare(card['base_output'],raw))
 else:
  write_json(out/'sampled_service_reconciliation.json',reconcile_service_fcd(raw,card))
  with (raw/'controller_steps.csv').open() as f:has_guard='guard_vehicle_states_json' in next(csv.reader(f))
  if has_guard:write_json(out/'guard_reconciliation.json',reconcile_guard(raw,card))
  write_json(out/'city_evidence.json',city_evidence(raw/'fcd.xml.gz',raw/'tls_states.xml'))
  network=Path(ET.parse(Path(card['package'])/'scenario.sumocfg').find('.//net-file').get('value'))
  write_json(out/'operational_chain.json',chain_from_raw(raw,network))
  baseline=json.loads((ROOT/'data/processed/stage6_boundary_search_20261002_v1'/f"M3600_R900_S{card['seed']}"/'summary.json').read_text())
  boundary.csv_write(out/'paired_classes.csv',paired_classes(baseline['classes'],summary['classes']))
 write_json(out/'adapter_provenance.json',dict(script_sha256=sha(__file__),reviewed_classifier_script_sha256=sha(boundary.__file__),card_sha256=sha(card_path),scope='Offline exploratory measurement. Gate failures are retained; no automatic exclusion or run. Continuous chain needs actual vehicle lengths.'))
 return summary

def chain_from_raw(raw,network_path):
 spec=importlib.util.spec_from_file_location('operational_chain',Path(__file__).with_name('chain.py'));chain=importlib.util.module_from_spec(spec);spec.loader.exec_module(chain)
 raw=Path(raw)
 with (raw/'vehicle_metadata.csv').open() as f:rr=list(csv.DictReader(f))
 lengths={r['vehicle_id']:float(r['vehicle_length_m']) for r in rr}
 if len(lengths)!=len(rr) or any(v<=0 for v in lengths.values()):raise ValueError('vehicle length metadata')
 lanes={e.get('id'):float(e.get('length')) for e in ET.parse(network_path).iter('lane')}
 stopline=sum(lanes[k] for k in ['shared_approach_0',':urban_diverge_1_0','ramp_storage_0']);rows=[]
 for e in records(raw/'fcd.xml.gz','timestep'):
  vs=[dict(id=v.get('id'),lane=v.get('lane'),pos=float(v.get('pos')),speed=float(v.get('speed'))) for v in e]
  rows.append(dict(time=int(float(e.get('time'))),**chain.snapshot(vs,lanes,stopline,lengths)))
 if len(rows)!=4200:raise ValueError('chain horizon')
 return dict(rows=rows,shared_episodes=chain.episodes(rows),storage_episodes=chain.episodes(rows,'storage_present'),definition='Prospective operational chain: upstream head<=10m, each speed<1.389m/s, consecutive bodygap<=10m, >=30s global episode; -0.05m rounding tolerance; branch unknown retained.',sources={str(p):sha(p) for p in [raw/'fcd.xml.gz',raw/'vehicle_metadata.csv',Path(network_path),Path(chain.__file__)]})

def mean_step_window(samples,decision_time):
 """Independent complete half-open window; missing values never become zero."""
 if len(samples)!=30:raise ValueError('step occupancy window coverage')
 if [r['time_begin_s'] for r in samples]!=list(range(decision_time-30,decision_time)):raise ValueError('step occupancy missing/duplicate/boundary')
 values=[0.,0.]
 for r in samples:
  if r['time_end_s']!=r['time_begin_s']+1:raise ValueError('step occupancy interval width')
  for lane in [0,1]:
   v=boundary.number(r[f'occ_l{lane}_pct'])
   if not 0<=v<=100:raise ValueError('step occupancy range')
   values[lane]+=v/30
 return values

def reconcile_step_feedback(raw):
 raw=Path(raw)
 with (raw/'detector_step_occupancy.csv').open() as f:rows=list(csv.DictReader(f))
 with (raw/'feedback_updates.csv').open() as f:updates=list(csv.DictReader(f))
 if len(rows)!=3570 or len(updates)!=119:raise ValueError('step/update full coverage')
 for r in rows:
  r['time_begin_s']=boundary.number(r['time_begin_s']);r['time_end_s']=boundary.number(r['time_end_s'])
 if [r['time_begin_s'] for r in rows]!=list(range(600,4170)):raise ValueError('step missing/duplicate/time order')
 max_error=0.;max_legacy_xml_delta=0.
 for index,u in enumerate(updates):
  t=630+index*30
  if boundary.number(u['decision_time_s'])!=t or u['occupancy_source']!='mean_last_step_30' or int(u['sample_count'])!=30:raise ValueError('rolling source/update contract')
  block=rows[index*30:(index+1)*30];means=mean_step_window(block,t)
  for lane in [0,1]:
   if any(r[f'detector_l{lane}']!=u[f'detector_l{lane}'] for r in block):raise ValueError('step detector identity')
   error=abs(means[lane]-boundary.number(u[f'occ_l{lane}_pct']));max_error=max(max_error,error)
   if error>1e-9:raise ValueError('step mean/update mismatch')
 return dict(status='PASS_STEP_MEAN_IDENTITY',step_rows=len(rows),windows=len(updates),lane_windows=238,max_mean_error_pct=max_error,sources={str(raw/n):sha(raw/n) for n in ['detector_step_occupancy.csv','feedback_updates.csv']})

def reconcile_event_feedback(raw):
 spec=importlib.util.spec_from_file_location('detector_events',Path(__file__).with_name('events.py'));events=importlib.util.module_from_spec(spec);spec.loader.exec_module(events)
 raw=Path(raw)
 with (raw/'detector_vehicle_events.csv').open() as f:rows=list(csv.DictReader(f))
 groups=defaultdict(list)
 for r in rows:
  begin=boundary.number(r['time_begin_s']);end=boundary.number(r['time_end_s'])
  if end!=begin+1:raise ValueError('event interval width')
  groups[end,r['detector_id']].append(r)
 observations=[]
 for (end,d),rs in sorted(groups.items()):
  counts={int(r['event_count']) for r in rs}
  if len(counts)!=1:raise ValueError('event count inconsistent within group')
  n=counts.pop();ev=[]
  if n==0:
   if len(rs)!=1 or any(rs[0][k] for k in ['vehicle_id','vehicle_length_m','entry_time_s','leave_time_s','type_id']):raise ValueError('invalid empty event sentinel')
  else:
   if n<0 or len(rs)!=n:raise ValueError('event group count mismatch')
   ev=[(r['vehicle_id'],boundary.number(r['vehicle_length_m']),boundary.number(r['entry_time_s']),boundary.number(r['leave_time_s']),r['type_id']) for r in rs]
  observations.append(dict(step_end_s=end,detector_id=d,events=ev))
 with (raw/'feedback_updates.csv').open() as f:updates=list(csv.DictReader(f))
 if len(updates)!=119:raise ValueError('event feedback119 required')
 detectors=[updates[0]['detector_l0'],updates[0]['detector_l1']]
 reconstructed=events.reconstruct(observations,detectors)
 bykey={(r['detector_id'],r['end']):r for r in reconstructed};max_error=0
 for index,u in enumerate(updates):
  t=630+30*index
  if float(u['decision_time_s'])!=t or u['occupancy_source']!='vehicle_event_residence_30' or int(u['sample_count'])!=30:raise ValueError('event update source/timing')
  for lane,d in enumerate(detectors):
   if u[f'detector_l{lane}']!=d:raise ValueError('event detector changed')
   error=abs(bykey[d,t]['occupancy_pct']-float(u[f'occ_l{lane}_pct']));max_error=max(max_error,error)
   if error>1e-9:raise ValueError('event occupancy/update mismatch')
 return dict(status='PASS_EVENT_RECONSTRUCTION_IDENTITY',groups=len(groups),event_csv_rows=len(rows),lane_windows=len(reconstructed),max_error_pct=max_error,windows=reconstructed,sources={str(p):sha(p) for p in [raw/'detector_vehicle_events.csv',raw/'feedback_updates.csv',Path(events.__file__)]})

def reconcile_guard(raw,card):
 spec=importlib.util.spec_from_file_location('actuator_guard',Path(__file__).with_name('guard.py'));guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 raw=Path(raw)
 with (raw/'controller_steps.csv').open() as f:rows=list(csv.DictReader(f))
 result=guard.audit(rows,card['meter_controlled_link']['storage_length_m'])
 result['sources']={str(p):sha(p) for p in [raw/'controller_steps.csv',Path(guard.__file__)]}
 return result
