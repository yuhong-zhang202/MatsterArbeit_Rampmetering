"""Exploratory S6-A01/A02 archive-only adapter. No simulator or network entry point.

Run once into exclusive new files. The fixed 12-run domain is intentional.
Historical EJMI and source contracts are read, never altered or reclassified.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/stage6_obstacle_20260913_v1'
S3=ROOT/'data/processed/stage3_baseline_diagnostic_20260912_v2'
S4=ROOT/'data/processed/stage4_qmain_sequential_20260912_v1'
WINDOWS={'A':(0,1500),'B':(300,1500),'Post':(1500,2700),'Full':(0,2700)}
CLASSES=['M','R','U','X']
RUNS=['C17','C23','ML17','ML23','MH17','MH23','RL17','RL23','QM3500S17','QM3500S23','QM3650S17','QM3650S23']
HASHES={}

def digest(path):
    path=Path(path); h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    value=h.hexdigest();HASHES[str(path.relative_to(ROOT))]=value;return value

def load(path):
    digest(path);return json.loads(Path(path).read_text())

def readcsv(path):
    digest(path)
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))

def finite(v):
    if v is None:raise ValueError('missing number')
    x=float(v)
    if not math.isfinite(x):raise ValueError('nonfinite number')
    return x

def unique(items,label):
    if len(items)!=len(set(items)):raise ValueError('duplicate '+label)

def time_grid(labels,end=2700):
    unique(labels,'time label')
    if set(labels)!=set(range(end)):raise ValueError('missing or extra label')

def state(value):return 'missing_observation' if value is None else 'observed_zero' if value==0 else 'observed'

def writejson(name,payload):
    with (BASE/name).open('x') as f:json.dump(payload,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def writecsv(name,records,at=TABLE):
    if not records:raise ValueError('empty output '+name)
    with (at/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)

def e1_values(records,duration):
    contrib=entered=0;weighted=0.
    for r in records:
        n=int(r['nVehContrib']);ne=int(r['nVehEntered']);v=finite(r['speed'])
        if n<0 or ne<0 or (n>0 and v<0):raise ValueError('invalid E1 contribution/speed')
        contrib+=n;entered+=ne
        if n:weighted+=n*v
    return contrib,entered,weighted/contrib if contrib else None,3600*contrib/duration,3600*entered/duration

def paired_outer(left,right):
    out=[]
    for key in sorted(set(left)|set(right)):
        a=left.get(key);b=right.get(key)
        eligible=a is not None and b is not None
        out.append({'key':key,'seed17':a,'seed23':b,'value_state':'observed' if eligible else 'not_paired','reason':'' if eligible else 'no comparable record for one seed; no zero imputation'})
    return out

def endpoint(planned,triprows,t):
    entered=sum(r['depart']<t for r in triprows);arrived=sum(r['arrival']<t for r in triprows)
    if not 0<=arrived<=entered<=planned:raise ValueError('endpoint conservation')
    return entered,arrived,entered-arrived,planned-entered

def safe_identity(vid,lane,seen,trips,lanes,speed):
    if vid in seen:raise ValueError('duplicate vehicle label')
    if vid not in trips:raise ValueError('unknown vehicle ID')
    if lane not in lanes:raise ValueError('unknown lane')
    v=finite(speed)
    if v<0:raise ValueError('negative speed')
    seen.add(vid);return v

def source_rows():
    l=load(S3/'execution_ledger.json');r=load(S4/'runtime_source_registry.json');snap=load(S4/'final_evidence_ledger_snapshot.json')
    if digest(S4/'runtime_source_registry.json')!=snap['bound_external_evidence']['runtime_source_registry']['sha256']:raise ValueError('snapshot registry mismatch')
    rows=[dict(x,stage='Stage2_via_Stage3') for x in l['source_runs']]+[dict(x,stage='Stage4_new') for x in r['runs']]
    unique([x['run_id'] for x in rows],'physical run')
    if {x['run_id'] for x in rows}!=set(RUNS):raise ValueError('unregistered run set')
    return sorted(rows,key=lambda r:RUNS.index(r['run_id']))

def source_files(row):
    p=ROOT/row['source_map_path']
    if digest(p)!=row['source_map_sha256']:raise ValueError('source map hash')
    sm=load(p)
    if sm['archive_status']!='complete':raise ValueError('incomplete archive')
    files={};inventory=[]
    for f in sm['file_map']:
        p=ROOT/f['archive_relative_path']
        if digest(p)!=f['sha256']:raise ValueError('raw hash mismatch')
        suffix=str(Path(f['original_absolute_path']).relative_to(sm['source_runtime_path']))
        if suffix in files:raise ValueError('duplicate suffix')
        files[suffix]=p
        inventory.append({'run_id':row['run_id'],'path':str(p),'sha256':f['sha256'],'size_bytes':p.stat().st_size,'source_suffix':suffix,'status':'hash_verified'})
    return files,inventory

def main():
    if (BASE/'analysis_started.json').exists():raise FileExistsError('batch already started; use a new reviewed revision')
    contract=load(S3/'measurement_contract.json');load(S4/'measurement_contract.json')
    lanes=contract['lanes'];stop=finite(contract['stop_definition']['speed_threshold_mps'])
    domain=[(lane,c) for lane,m in lanes.items() for c in m['observed_classes']]
    writejson('analysis_started.json',{'status':'started','code_sha256':digest(Path(__file__)),'scope':'12 fixed historical runs; exploratory only','simulation_entry_points':[]})
    writejson('offline_adapter_contract.json',{
        'status':'exploratory_archive_analysis_only','physical_run_ids':RUNS,'windows':WINDOWS,'fcd_step_s':1,
        'lane_class_domain':domain,'lane_map_source':str((S3/'measurement_contract.json').relative_to(ROOT)),
        'technical_stop_speed_mps':stop,'threshold_role':'existing technical stop only; not congestion threshold',
        'time_bin_s':30,'bin_role':'native E1-aligned descriptive display; no scientific state threshold',
        'e1_metric_ids':['q_contrib_vehph','q_entered_vehph','speed_contribution_weighted_mps','occupancy_lane_mean_percent'],
        'e1_counter_rule':'both counters preserved; historical Stage3 q uses contrib, Stage4 q uses entered; no historical reclassification',
        'value_states':['observed','observed_zero','no_contributors','missing_observation','not_applicable','not_paired'],
        'zero_rule':'dense zeros only for a validated frame and explicitly registered lane/class domain',
        'position_rule':'M signed coordinate: main_up pos minus lane length; merge internal pos; main_down pos+8.64; only declared M route',
        'outside_rule':'planned cohort minus entered only at 1500/2700, no unverified schedule-based intermediate curve',
        'TLS_rule':'same raw time label, movement 0 R/U or 1 X; no substep causal ordering',
        'R_rule':'first observed main_down and preceding observation form bracket; no exact crossing interpolation',
        'preserved_decisions':'Stage4 EJMI and all historical machine decisions unchanged',
        'independent_plan':'separate verifier directly scans raw XML without importing this adapter; full core cross-check against new rows',
        'new_simulation_counts':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0}})
    registry=[];file_inventory=[];entry=[];endpoints=[];cw=[];sections=[];e1intervals=[];exposure=[];prop=[];events=[];msumm=[];runsummary=[];compat=[];checks=[];spacetime=[];frames_total=0;samples_total=0
    timelinepath=TABLE/'lane_class_time.csv'
    with timelinepath.open('x',newline='') as tf:
        fields=['run_id','time_s','lane_id','region','class','present','stopped','speed_sum_mps','speed_n','min_pos_m','max_pos_m','mean_speed_mps','count_value_state','speed_value_state','coverage','reason']
        tw=csv.DictWriter(tf,fieldnames=fields);tw.writeheader()
        for row in source_rows():
            rid=row['run_id'];files,inventory=source_files(row);file_inventory+=inventory
            net=ET.parse(files['network.net.xml']).getroot();actual_lanes={n.get('id'):finite(n.get('length')) for n in net.iter('lane')}
            if set(actual_lanes)!=set(lanes):raise ValueError('lane domain drift')
            for lane in lanes:
                if not math.isclose(actual_lanes[lane],lanes[lane]['length_m'],abs_tol=1e-6):raise ValueError('lane length drift')
            roots=ET.parse(files['demand.rou.xml']).getroot();flows={f.get('id').split('_')[0]:f for f in roots.findall('flow')};planned={c:int(flows[c].get('number')) for c in CLASSES}
            trips={}
            for _,n in ET.iterparse(files['outputs/tripinfo.xml'],events=('end',)):
                if n.tag!='tripinfo':continue
                vid=n.get('id')
                if vid in trips:raise ValueError('duplicate tripinfo')
                trips[vid]={k:finite(n.get(k)) for k in ['depart','arrival','departPos','departDelay','duration','timeLoss','waitingTime','routeLength']}
                trips[vid].update({'class':vid.split('_')[0],'departLane':n.get('departLane')});n.clear()
            routes=[n.get('id') for _,n in ET.iterparse(files['outputs/vehroute.xml'],events=('end',)) if n.tag=='vehicle'];unique(routes,'route IDs')
            if set(routes)!=set(trips) or len(trips)!=sum(planned.values()):raise ValueError('identity/cohort mismatch')
            tls={}
            for _,n in ET.iterparse(files['outputs/tls_states.xml'],events=('end',)):
                if n.tag!='tlsState':continue
                t=finite(n.get('time'))
                if t in tls:raise ValueError('duplicate TLS')
                if n.get('id')!=contract['tls']['id'] or len(n.get('state'))!=2:raise ValueError('TLS identity/link mismatch')
                tls[t]=n.get('state');n.clear()
            time_grid(list(tls))
            first={};previous={};firstR={};frames=[];rfirst={};shared=[];mbin=defaultdict(lambda:[0,0.,0,None,None]);mwindow=defaultdict(lambda:[0,0.,0,None,None]);mids=defaultdict(set);regionR=defaultdict(set);run_samples=0;framecounts=[]
            for _,n in ET.iterparse(files['outputs/fcd.xml'],events=('end',)):
                if n.tag!='timestep':continue
                t=finite(n.get('time'));frames.append(t);seen=set();cells=defaultdict(lambda:[0,0,0.,None,None]);sharedR=sharedU=0;present=Counter();stopped=Counter()
                for v in n:
                    vid=v.get('id');lane=v.get('lane');speed=safe_identity(vid,lane,seen,trips,lanes,v.get('speed'));pos=finite(v.get('pos'));c=trips[vid]['class'];region=lanes[lane]['region']
                    if (lane,c) not in domain:raise ValueError('class outside lane domain')
                    if pos<0 or pos>actual_lanes[lane]+1e-6:raise ValueError('position outside lane')
                    cell=cells[(lane,c)];cell[0]+=1;cell[1]+=int(speed<=stop);cell[2]+=speed;cell[3]=pos if cell[3] is None else min(cell[3],pos);cell[4]=pos if cell[4] is None else max(cell[4],pos)
                    first.setdefault(vid,(t,lane,pos,speed));present[c]+=1;stopped[c]+=int(speed<=stop);run_samples+=1
                    if c=='R' and speed<=stop:rfirst.setdefault(region,t);regionR[region].add(t)
                    if region=='shared_approach' and speed<=stop:
                        sharedR+=int(c=='R');sharedU+=int(c=='U')
                    if c=='R' and lanes[lane]['first_downstream_eligible'] and vid not in firstR:
                        prior=previous.get(vid);firstR[vid]=(t,lane,prior)
                    previous[vid]=(t,lane,pos)
                    if c=='M':
                        signed=pos-actual_lanes[lane] if lane.startswith('main_up') else pos if lane.startswith(':freeway_merge_1') else pos+8.64
                        if not (lane.startswith('main_up') or lane.startswith(':freeway_merge_1') or lane.startswith('main_down')):raise ValueError('M route domain')
                        k=(int(t//30)*30,region);b=mbin[k];b[0]+=1;b[1]+=speed;b[2]+=int(speed<=stop);b[3]=signed if b[3] is None else min(b[3],signed);b[4]=signed if b[4] is None else max(b[4],signed)
                        for w,(begin,end) in WINDOWS.items():
                            if begin<=t<end:
                                a=mwindow[(w,region)];a[0]+=1;a[1]+=speed;a[2]+=int(speed<=stop);a[3]=speed if a[3] is None else min(a[3],speed);a[4]=speed if a[4] is None else max(a[4],speed);mids[(w,region)].add(vid)
                for lane,c in domain:
                    a=cells[(lane,c)];tw.writerow(dict(zip(fields,[rid,t,lane,lanes[lane]['region'],c,a[0],a[1],a[2],a[0],a[3],a[4],a[2]/a[0] if a[0] else None,state(a[0]),'observed' if a[0] else 'no_contributors','complete','validated frame; no vehicle is a measured count zero'])))
                shared.append((t,sharedR,sharedU,tls[t][0]));framecounts.append((t,dict(present),dict(stopped)));n.clear()
            time_grid(frames)
            if set(first)!=set(trips):raise ValueError('FCD/trip identity coverage')
            frames_total+=len(frames);samples_total+=run_samples
            for vid,tr in trips.items():
                t,lane,pos,speed=first[vid];c=tr['class'];distance=actual_lanes[tr['departLane']]-tr['departPos'] if c=='M' else None
                entry.append({'run_id':rid,'id':vid,'class':c,'depart_time':tr['depart'],'depart_lane':tr['departLane'],'depart_pos':tr['departPos'],'first_fcd_time':t,'first_fcd_lane':lane,'first_fcd_pos':pos,'first_fcd_speed_mps':speed,'distance_to_main_up_end_m':distance,'distance_to_main_down_start_m':distance+8.64 if distance is not None else None,'depart_delay_s':tr['departDelay'],'arrival_time':tr['arrival'],'in_network_duration_s':tr['duration'],'tripinfo_time_loss_s':tr['timeLoss'],'tripinfo_waiting_time_s':tr['waitingTime'],'route_length_m':tr['routeLength'],'coverage':'complete','value_state':'observed','M_distance_value_state':'observed' if c=='M' else 'not_applicable','reason':'M distance ends at upstream lane end; plus 8.64m ends at downstream lane start'})
            summary_steps={finite(n.get('time')):dict(n.attrib) for _,n in ET.iterparse(files['outputs/sumo_summary.xml'],events=('end',)) if n.tag=='step'}
            for endpoint_s in [1500,2700]:
                totalE=totalA=0
                for c in CLASSES:
                    E,A,N,O=endpoint(planned[c],[tr for tr in trips.values() if tr['class']==c],endpoint_s);totalE+=E;totalA+=A
                    endpoints.append({'run_id':rid,'class':c,'endpoint_s':endpoint_s,'P':planned[c],'E':E,'A':A,'N':N,'O':O,'qualification':'complete','value_state':'observed','reason':'finite planned cohort at demand end/full end; event_time < endpoint'})
                ss=summary_steps[endpoint_s-1]
                if (int(ss['loaded']),int(ss['inserted']),int(ss['arrived']))!=(sum(planned.values()),totalE,totalA):raise ValueError('summary endpoint mismatch')
            for w,(begin,end) in WINDOWS.items():
                for c in CLASSES:
                    group=[tr for tr in trips.values() if tr['class']==c];depart=sum(begin<=tr['depart']<end for tr in group);arr=sum(begin<=tr['arrival']<end for tr in group)
                    cw.append({'run_id':rid,'class':c,'window':w,'begin_s':begin,'end_s':end,'departures':depart,'arrivals':arr,'departure_rate_vehph':3600*depart/(end-begin),'arrival_rate_vehph':3600*arr/(end-begin),'planned_full_cohort':planned[c],'qualification':'complete','value_state':'observed','reason':'actual network entry/arrival; not E1 passage'})
                s=[x for x in shared if begin<=x[0]<end];co=[x for x in s if x[1]>0 and x[2]>0]
                exposure.append({'run_id':rid,'window':w,'R_shared_stopped_labels':sum(x[1]>0 for x in s),'U_shared_stopped_labels':sum(x[2]>0 for x in s),'RU_shared_labels':len(co),'R_shared_vehicle_seconds':sum(x[1] for x in s),'U_shared_vehicle_seconds':sum(x[2] for x in s),'RU_labels_green':sum(x[3] in 'Gg' for x in co),'RU_labels_red':sum(x[3]=='r' for x in co),'RU_labels_yellow':sum(x[3] in 'Yy' for x in co),'covered_seconds':end-begin,'value_state':state(len(co)),'qualification':'observed_exposure_not_causal','reason':'same raw labels; TLS upstream movement context is not immediate downstream causation'})
                for region in ['mainline_origin_observation','mainline_merge_internal','mainline_downstream']:
                    a=mwindow[(w,region)];msumm.append({'run_id':rid,'window':w,'region':region,'M_sample_count':a[0],'unique_M_ids':len(mids[(w,region)]),'speed_sum_mps':a[1],'mean_sample_speed_mps':a[1]/a[0] if a[0] else None,'min_sample_speed_mps':a[3],'max_sample_speed_mps':a[4],'M_stopped_vehicle_seconds':a[2],'value_state':'observed' if a[0] else 'no_contributors','qualification':'complete_within_observed_route','reason':'vehicle-label weighted FCD speed; not detector speed or congestion classification'})
            for region in ['ramp_accel','ramp_mid_internal','ramp_storage','ramp_diverge_internal','shared_approach']:
                prop.append({'run_id':rid,'region':region,'first_R_stopped_label':rfirst.get(region),'R_stopped_labels_full':len(regionR[region]),'value_state':state(rfirst.get(region)),'coverage_status':'complete','phenomenon_status':'observed' if region in rfirst else 'not_observed_within_scope','reason':'technical <=0.1 m/s; region labels do not prove continuous physical queue'})
            for vid,(t,lane,prior) in firstR.items():
                status='bracketed' if prior and prior[0]==t-1 else 'unresolved_previous_frame'
                events.append({'run_id':rid,'vehicle_id':vid,'previous_time_s':prior[0] if prior else None,'previous_lane':prior[1] if prior else None,'first_downstream_time_s':t,'first_downstream_lane':lane,'status':status,'A_membership':'inside' if t<1500 else 'boundary_ambiguous' if prior and prior[0]<1500<=t else 'outside','value_state':'observed','reason':'first downstream label; bracket cannot locate exact crossing'})
            # Dense 30-second spatial summaries preserve no-contributor cells.
            for b in range(0,2700,30):
                for region in ['mainline_origin_observation','mainline_merge_internal','mainline_downstream']:
                    a=mbin[(b,region)];spacetime.append({'run_id':rid,'bin_begin':b,'bin_end':b+30,'region':region,'M_samples':a[0],'mean_sample_speed_mps':a[1]/a[0] if a[0] else None,'M_stopped_vehicle_seconds':a[2],'min_signed_M_position_m':a[3],'max_signed_M_position_m':a[4],'value_state':'observed' if a[0] else 'no_contributors','reason':'full domain frame coverage; 30s bins descriptive only'})
            detector_data=defaultdict(list)
            for d in contract['e1_detectors']:
                records=[]
                for _,n in ET.iterparse(files[d['output_suffix']],events=('end',)):
                    if n.tag!='interval':continue
                    a=dict(n.attrib)
                    if a['id']!=d['detector_id']:raise ValueError('E1 detector mismatch')
                    a['begin']=finite(a['begin']);a['end']=finite(a['end']);records.append(a);n.clear()
                if [(r['begin'],r['end']) for r in records]!=[(b,b+30) for b in range(0,2700,30)]:raise ValueError('E1 interval grid')
                e1_values(records,2700)
                detector_data[d['group']]+=records
                for a in records:
                    e1intervals.append({'run_id':rid,'source_stage':row['stage'],'detector_id':d['detector_id'],'group':d['group'],'bin_begin':a['begin'],'bin_end':a['end'],'nVehContrib':int(a['nVehContrib']),'nVehEntered':int(a['nVehEntered']),'speed_mps':float(a['speed']) if int(a['nVehContrib']) else None,'occupancy_percent':float(a['occupancy']),'speed_value_state':'observed' if int(a['nVehContrib']) else 'no_contributors','value_state':'observed','reason':'raw counters kept separately; speed sentinel normalized only at zero contribution'})
            for group,records in detector_data.items():
                for w,(begin,end) in WINDOWS.items():
                    a=[r for r in records if begin<=r['begin'] and r['end']<=end];n,ne,v,qc,qe=e1_values(a,end-begin)
                    metrics=[('q_contrib_vehph',qc,'veh/h',n,end-begin),('q_entered_vehph',qe,'veh/h',ne,end-begin),('speed_contribution_weighted_mps',v,'m/s',sum(float(r['speed'])*int(r['nVehContrib']) for r in a if int(r['nVehContrib'])),n),('occupancy_lane_mean_percent',sum(float(r['occupancy'])*(r['end']-r['begin']) for r in a)/(2*(end-begin)),'percent',None,2*(end-begin))]
                    for metric,value,unit,numerator,denominator in metrics:
                        sections.append({'run_id':rid,'source_stage':row['stage'],'group':group,'window':w,'metric_id':metric,'value':value,'unit':unit,'numerator':numerator,'denominator':denominator,'nVehContrib':n,'nVehEntered':ne,'value_state':'no_contributors' if value is None else state(value),'qualification':'origin_insertion_contaminated' if group=='origin_insertion_contaminated' else 'complete_declared_section','reason':'both lane counters; distinct scope from network entry'})
            M=[tr for tr in trips.values() if tr['class']=='M'];dist=[actual_lanes[tr['departLane']]-tr['departPos'] for tr in M]
            qmain=3500 if rid.startswith('QM3500') else 3650 if rid.startswith('QM3650') else 2600 if rid.startswith('ML') else 3800 if rid.startswith('MH') else 3200
            qramp=360 if rid.startswith('RL') else 720;seed=int(rid[-2:])
            registry.append({'run_id':rid,'source_stage':row['stage'],'condition':rid[:-2],'seed':seed,'q_main_requested_vehph':qmain,'q_ramp_requested_vehph':qramp,'source_map_path':str((ROOT/row['source_map_path']).resolve()),'source_map_sha256':row['source_map_sha256'],'archive_path':str(Path(row['archive_runtime_path']).resolve()),'network_sha256':digest(files['network.net.xml']),'demand_sha256':digest(files['demand.rou.xml']),'required_horizon_s':2700,'file_count':len(files),'status':'verified_unique_archive','role':'seen_historical_diagnostic_not_prospective_validation'})
            compat.append({'run_id':rid,'historical_stage_q_counter':'nVehEntered' if row['stage']=='Stage4_new' else 'nVehContrib','new_q_metric_ids':'q_contrib_vehph|q_entered_vehph','FCD_domain':'19 lanes incl internal; explicit class memberships','time_grid':'0..2699 at 1Hz','raw_available':'FCD|6 E1|TLS|tripinfo|vehroute|summary|compiled network','not_available':'lanechange/gap acceptance logs; realistic traveled long upstream feeder; causal counterfactual','reuse_status':'raw reused under new adapter contract; old hash entry points not invoked'})
            runsummary.append({'run_id':rid,'seed':seed,'q_main':qmain,'q_ramp':qramp,'planned_total':sum(planned.values()),'M_count':len(M),'M_distance_to_main_up_end_min_m':min(dist),'M_distance_to_main_up_end_max_m':max(dist),'M_distance_mean_m':sum(dist)/len(dist),'R_first_downstream_A':sum(t<1500 for t,_,_ in firstR.values()),'R_first_downstream_Full':len(firstR),'R_late_departures':sum(tr['class']=='R' and tr['depart']>=1500 for tr in trips.values()),'U_late_departures':sum(tr['class']=='U' and tr['depart']>=1500 for tr in trips.values()),'last_departure_s':max(tr['depart'] for tr in trips.values()),'last_arrival_s':max(tr['arrival'] for tr in trips.values()),'RU_shared_labels_full':sum(r>0 and u>0 for _,r,u,_ in shared),'M_stopped_vehicle_seconds_full':sum(x[2] for (w,_),x in mwindow.items() if w=='Full'),'value_state':'observed','reason':'exploratory descriptive; no new EJMI or cause classification'})
            checks.append({'run_id':rid,'frames':len(frames),'tls_labels':len(tls),'FCD_vehicle_samples':run_samples,'trip_IDs':len(trips),'E1_intervals':540,'endpoint_units':8,'unknown_or_duplicate_records':0,'missing_critical_values':0,'R_unresolved_brackets':sum(r['status']!='bracketed' for r in events if r['run_id']==rid),'status':'passed'})
            print(rid,'complete',len(trips),'identities',run_samples,'FCD samples',flush=True)
    for name,records in [('source_registry.csv',registry),('source_file_inventory.csv',file_inventory),('schema_compatibility.csv',compat)]:writecsv(name,records,BASE)
    for name,records in [('entry_vehicle_records.csv',entry),('endpoint_accounting.csv',endpoints),('class_window_counts.csv',cw),('section_window_metrics.csv',sections),('e1_native_intervals.csv',e1intervals),('shared_exposure.csv',exposure),('R_region_propagation.csv',prop),('R_passage_events.csv',events),('M_region_window.csv',msumm),('M_space_time_30s.csv',spacetime),('run_summary.csv',runsummary)]:writecsv(name,records)
    old=readcsv(S3/'analysis_review/revision_06/same_seed_contrasts.csv');left={};right={}
    for r in old:
        k='|'.join([r['contrast_id'].split('_seed')[0],r['window'],r['entity'],r['metric'],r['unit']]);target=left if int(r['seed'])==17 else right
        if k in target:raise ValueError('duplicate seed contrast key')
        target[k]=float(r['delta'])
    paired=paired_outer(left,right);writecsv('historical_seed_outer_join.csv',paired)
    if len([r for r in paired if r['value_state']=='not_paired'])!=5:raise ValueError('unexpected historical unpaired set')
    writejson('processing_verification.json',{'status':'passed_primary_calculations_pending_independent_review','physical_runs':12,'source_hash_pairs':len(file_inventory),'FCD_frames':frames_total,'FCD_samples':samples_total,'dense_lane_class_time_rows':frames_total*len(domain),'entry_vehicle_rows':len(entry),'endpoint_rows':len(endpoints),'E1_rows':len(e1intervals),'R_event_rows':len(events),'shared_window_rows':len(exposure),'M_region_window_rows':len(msumm),'paired_key_union':len(paired),'unpaired_keys':5,'checks':checks,'simulation_counts':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'limitations':['No historical EJMI changed','No prospective validation','No structural causal conclusion','TLS label cooccurrence does not identify cause','No unverified outside-waiting curve reconstructed']})
    digest(Path(__file__));writejson('input_hashes.json',HASHES)

if __name__=='__main__':main()
