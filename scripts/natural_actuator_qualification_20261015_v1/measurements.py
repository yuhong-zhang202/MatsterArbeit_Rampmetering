"""Read-only lifecycle and city measurements; no service acceptance threshold."""
from collections import Counter,defaultdict
import xml.etree.ElementTree as ET
from fractions import Fraction
from scripts.natural_service_audit_20261015_v1.actual import need,near


def cohort(demand_path,trips,observed,last,summary_steps,endpoint):
    elements=ET.parse(demand_path).getroot().findall('vehicle')
    demand={v.get('id'):v for v in elements}
    need(len(demand)==len(elements)==4050,'PLANNED_COHORT_NOT_4050_OR_DUPLICATE')
    need(Counter(v.split('_',1)[0] for v in demand)==dict(M=3000,R=600,U=300,X=150),'COHORT_CLASSES')
    trip={x['id']:x for x in trips};need(len(trip)==len(trips) and set(trip)<=set(demand),'DUPLICATE_OR_UNPLANNED_TRIP')
    need(set(observed)<=set(demand),'UNPLANNED_FCD_ID')
    rows=[];missing=[]
    for vid,v in demand.items():
        p=float(v.get('depart'));t=trip.get(vid);f=observed.get(vid)
        if p>=last:
            need(not f and (not t or float(t['depart'])<0),'FUTURE_REQUEST_INSERTED')
            rows.append(dict(id=vid,vehicle_class=vid.split('_',1)[0],scheduled=p,status='FUTURE_SCHEDULED',source_wait_s=0.,in_network_s=0.,system_s=0.));continue
        if t is None:
            missing.append(vid);rows.append(dict(id=vid,vehicle_class=vid.split('_',1)[0],scheduled=p,status='UNKNOWN_MISSING_DUE_TRIP',source_wait_s=None,in_network_s=None,system_s=None));continue
        d=float(t['depart']);a=float(t['arrival']);inserted=d>=0;arrived=a>=0
        need(not arrived or inserted,'ARRIVAL_WITHOUT_INSERTION')
        if inserted:
            need(p<=d<last and f is not None and 0<=f['first']-d<=1,'INSERTION_FCD_BOUNDARY')
            need(near(float(t['departDelay']),d-p),'INSERTION_DELAY')
            need((arrived and 0<=a-f['last']<=1) or (not arrived and f['last']==last-1),'ARRIVAL_OR_CENSOR_FCD_BOUNDARY')
        else:need(f is None,'UNINSERTED_HAS_FCD')
        stop=min(a,last) if arrived else last
        source=(min(d,last) if inserted else last)-p
        inside=stop-min(d,last) if inserted else 0.
        need(min(source,inside)>=0 and near(source+inside,stop-p),'NEGATIVE_OR_UNRECONCILED_COST')
        if inserted and not arrived:need(vid in endpoint,'UNFINISHED_ENDPOINT_ID_MISSING')
        rows.append(dict(id=vid,vehicle_class=vid.split('_',1)[0],scheduled=p,depart=d if inserted else None,arrival=a if arrived else None,
                         status='ARRIVED' if arrived else 'IN_NETWORK_UNFINISHED' if inserted else 'DUE_UNINSERTED',source_wait_s=source,in_network_s=inside,system_s=source+inside))
    need(len(summary_steps)==last,'SUMMARY_PREFIX_COVERAGE')
    need(all(float(x['time'])==i for i,x in enumerate(summary_steps)),'SUMMARY_TIME_GAP')
    inserted={v for v,x in trip.items() if float(x['depart'])>=0};arrived={v for v,x in trip.items() if float(x['arrival'])>=0}
    if last:
        s=summary_steps[-1]
        need(int(s['inserted'])==len(inserted) and int(s['arrived'])==len(arrived) and int(s['running'])==len(inserted-arrived),'SUMMARY_COUNTS')
        need(set(endpoint)==inserted-arrived,'ENDPOINT_POPULATION')
    sums={key:sum(r[key] for r in rows if r[key] is not None) for key in ('source_wait_s','in_network_s','system_s')}
    integral={}
    if not missing:
        exposure=sum(max(0,last-float(v.get('depart'))) for v in elements)
        integral=dict(system_s=exposure-sum(int(x['arrived']) for x in summary_steps),source_wait_s=exposure-sum(int(x['inserted']) for x in summary_steps),in_network_s=sum(int(x['running']) for x in summary_steps))
        need(all(near(sums[k],v) for k,v in integral.items()),'COHORT_TIME_INTEGRAL')
    classes={c:dict(counts=dict(Counter(r['status'] for r in rows if r['vehicle_class']==c)),**{k:sum(r[k] for r in rows if r['vehicle_class']==c and r[k] is not None) for k in sums}) for c in 'MRUX'}
    return dict(status='UNKNOWN_MISSING_DUE_TRIP' if missing else 'PASS_REQUESTED_COHORT_ACCOUNTING',rows=rows,classes=classes,totals=sums,integral=integral,missing_due_ids=missing,future_exposure='ZERO_NOT_NEGATIVE',cost_scope='RESTRICTED_AT_LAST_ACK_NOT_COMPLETE_JOURNEY_UNLESS_ALL_ARRIVED')


def urban_frame(frame,city_state,t):
    """Existing descriptive1.389m/s exposure; no causal/continuous-chain claim."""
    by_lane=defaultdict(list);counts=Counter();contexts=[]
    for vid,v in frame.items():
        lane=v['lane'];role=vid.split('_',1)[0];speed=float(v['speed'])
        if lane in ('ramp_storage_0',':urban_diverge_1_0','shared_approach_0'):
            by_lane[lane].append((float(v['pos']),vid,role,speed));counts[(lane,role,'vehicle_seconds')]+=1
            counts[(lane,role,'slow_lt1p389_seconds')]+=speed<1.389
    for lane,items in by_lane.items():
        items.sort()
        for i,(position,vid,role,speed) in enumerate(items):
            if role=='U' and speed<1.389:
                ahead=items[i+1] if i+1<len(items) else None
                contexts.append(dict(time=t,id=vid,lane=lane,urban_green=city_state[0] in 'Gg',ahead_id=ahead[1] if ahead else None,ahead_role=ahead[2] if ahead else None))
    return counts,contexts


def windows(posts,last):
    out=[]
    for start in range(1200,3000,300):
        end=start+300;part=[r for r in posts if start<=r['time_begin_s']<end and r.get('accounting_complete') is True]
        status='NOT_TESTED_WINDOW_NOT_REACHED' if last<=start else 'PASS_COMPLETE_OBSERVATION_SUPPORT' if len(part)==300 else 'UNKNOWN_INCOMPLETE_WINDOW'
        if part:
            before=posts[start-1]['accounting'] if start>600 and start<=len(posts) else None
            a=part[-1]['accounting'];C0=Fraction(before['C_exact_fraction']) if before else Fraction(0);N0=before['N'] if before else 0
            C=Fraction(a['C_exact_fraction'])-C0;N=a['N']-N0
            measured=dict(C=float(C),C_exact_fraction=str(C),N=N,residual_C_minus_N=str(C-N))
            for field in ('E_scheduled_nominal','E_executed_nominal'):
                measured[field]=a[field]-(before[field] if before else 0)
            for field in ('C_selected_exact_fraction','C_applied_exact_fraction'):
                measured[field]=str(Fraction(a[field])-(Fraction(before[field]) if before else 0))
            measured['constraints']={name:sum(bool(r.get('constraint_observation',{}).get(name)) for r in part) for name in ('empty_storage','WAIT_before')}
            measured['constraints']['receiver_unavailable']=sum(r.get('constraint_observation',{}).get('receiver_available') is False for r in part)
        else:measured=dict(C=None,C_exact_fraction=None,N=None,residual_C_minus_N=None)
        out.append(dict(begin_s=start,end_s=end,status=status,observed_intervals=len(part),**measured))
    return out


def feedback_xml(raw,events,last):
    detectors=('p1_main_down_20_l0','p1_main_down_20_l1')
    decisions=[e for e in events if e['event']=='PROJECT_FEEDBACK_DECISION']
    matched=0
    for i,name in enumerate(detectors):
        intervals=ET.parse(raw/(name+'.xml')).getroot().findall('interval');by={}
        for e in intervals:
            a=e.attrib;key=(float(a['begin']),float(a['end']))
            need(a['id']==name and key not in by,'E1_XML_DUPLICATE_OR_ID');by[key]=a
        for e in decisions:
            key=(e['global_window_begin_s'],e['global_window_end_s']);need(key in by,'E1_XML_DECISION_WINDOW_MISSING')
            # XML is output-rounded to8 decimals; this is representation
            # tolerance, not a new service/safety acceptance threshold.
            value=float(by[key]['occupancy']);need(abs(value-e['occ_l0_pct' if i==0 else 'occ_l1_pct'])<=.51e-8,'E1_XML_OCCUPANCY');matched+=1
    return dict(status='PASS_EVENT_XML_FEEDBACK_WINDOWS' if decisions else 'NOT_TESTED_NO_FULL_FEEDBACK_DECISION',lane_windows_checked=matched,terminal_measurement_not_new_command=True)


def queue_extent(frame,metadata,lane_lengths,t):
    names=('ramp_storage_0',':urban_diverge_1_0','shared_approach_0');offset={};total=0.
    for lane in names:offset[lane]=total;total+=lane_lengths[lane]
    rows=[];missing=[];ambiguous=[]
    for vid,v in frame.items():
        if not vid.startswith('R_flow.') or v['lane'] not in names:continue
        speed=float(v['speed'])
        if abs(speed-1.389)<=.51e-8:ambiguous.append(vid)
        if speed>=1.389:continue
        meta=metadata.get(vid)
        if not meta or 'length_m' not in meta:missing.append(vid);continue
        lane=v['lane'];position=float(v['pos']);length=meta['length_m']
        need(type(length) in (int,float) and length>0 and 0<=position<=lane_lengths[lane],'QUEUE_BODY_OR_POSITION')
        rows.append(dict(id=vid,lane=lane,front_position_m=position,length_m=length,speed_m_s=speed,rear_upstream_meter_m=offset[lane]+lane_lengths[lane]-position+length))
    return dict(time_begin_s=t,observed_ACK_s=t+1,status='UNKNOWN_MISSING_QUEUE_LENGTH' if missing else 'PASS_NAMED_LANE_REAR_OBSERVATION',
        ramp_slow_R_rear_extent_m=max((r['rear_upstream_meter_m'] for r in rows if r['lane']!=names[-1]),default=0),
        shared_slow_R_rear_extent_m=max((r['rear_upstream_meter_m'] for r in rows if r['lane']==names[-1]),default=0),
        slow_R_rows=rows,missing_length_ids=missing,speed_boundary_ambiguous_ids=ambiguous,
        scope='Maximum observed slow R rear; gaps permitted; not contiguous queue or causal spillback')


def queue_xml(path,last):
    rows=[];seen=set()
    for _,e in ET.iterparse(path,events=('end',)):
        label=e.get('timestep',e.get('time'))
        if label is None or e.find('lanes') is None:continue
        t=float(label);need(t not in seen and t==len(seen),'QUEUE_XML_TIME_GAP_OR_DUPLICATE');seen.add(t)
        lanes=[]
        for lane in e.findall('./lanes/lane'):
            if lane.get('id') not in ('ramp_storage_0',':urban_diverge_1_0','shared_approach_0'):continue
            a=dict(lane.attrib)
            for k,v in a.items():
                if k!='id':need(float(v)>=0,'NEGATIVE_QUEUE_EXPORT')
            lanes.append(a)
        rows.append(dict(time_begin_s=t,lanes=lanes));e.clear()
    need(seen==set(range(last)),'QUEUE_XML_PREFIX_COVERAGE')
    return dict(status='PASS_NATIVE_QUEUE_EXPORT_COVERAGE',rows=rows,definition='Native SUMO queue export; not equated to project1.389m/s R rear extent')
