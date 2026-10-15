"""One frame of native world/identity/FCD in memory; small math projection only."""
from collections import Counter
import gzip,json,xml.etree.ElementTree as ET
from scripts.natural_service_audit_20261015_v1.actual import need,near
from scripts.cumulative_full_catalogue_audit_20261014_v1.evidence import body_frame,serialized_population,strict_numeric,identity_journal
from scripts.unified_alinea_audit_20261013_v1.signal_binding_v2 import validate as signal_validate
from scripts.dynamic_minimum_qualification_audit_20261015_v1.current_gap import following
from scripts.natural_actuator_qualification_20261015_v1.measurements import urban_frame,queue_extent
from data.processed.issue12_alinea_actuation_20261012_v1.audit_data_V3 import audit_terminal
from scripts.natural_actuator_qualification_20261015_v1.provenance import gap_stop


def jsonl(path,optional=False):
    if optional and not path.exists():return
    with path.open() as f:
        for line in f:
            if line.strip():yield json.loads(line)


def posts(path):
    for row in jsonl(path):
        if 'retained_receipts' in row:
            need(isinstance(row['retained_receipts'],list) and len(row['retained_receipts'])<=1,'FAILED_POST_WRAPPER')
            yield from row['retained_receipts']
        else:yield row


def fcd_frames(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rb') as f:
        for _,e in ET.iterparse(f,events=('end',)):
            if e.tag=='timestep':
                frame={v.get('id'):dict(v.attrib) for v in e};need(len(frame)==len(e),'DUPLICATE_FCD_ID')
                yield float(e.get('time')),frame
                e.clear()


def tls_rows(path,last):
    rows={}
    for _,e in ET.iterparse(path,events=('end',)):
        if e.tag!='tlsState':continue
        key=(float(e.get('time')),e.get('id'));need(key not in rows,'DUPLICATE_TLS');rows[key]=dict(e.attrib);e.clear()
    for name in ('ramp_mid','urban_tls'):need({t for t,n in rows if n==name}==set(range(last)),'TLS_COVERAGE:'+name)
    return rows


def scan(raw,receipt,network,trips):
    last=receipt['last_completed_s'];need(type(last) is int and 0<=last<=4200,'LAST_ACK')
    pi=iter(jsonl(raw/'pre_steps.jsonl'));po=iter(posts(raw/'post_steps.jsonl'));ai=iter(jsonl(raw/'step_ack.jsonl'));ji=iter(jsonl(raw/'identity_journal.jsonl'));fi=iter(fcd_frames(raw/'fcd.xml.gz'))
    tls=tls_rows(raw/'tls_states.xml',last)
    pre=next(pi,None);small_pre=[];small_post=[];acks=[];entries=[];active=set();binding={};cleared={};observed={};endpoint={};alarms=[];missing=[];advisories=[];arrivals=[];constraints=Counter();populations=Counter();urban=Counter();contexts=[];body_checked=0;queue_rows=[]
    edges={e.get('id'):[x.get('id') for x in e.findall('lane')] for e in ET.parse(network).getroot().findall('edge')}
    lane_lengths={x.get('id'):float(x.get('length')) for e in ET.parse(network).getroot().findall('edge') for x in e.findall('lane') if x.get('length') is not None}
    tripby={x['id']:x for x in trips};need(len(tripby)==len(trips),'DUPLICATE_TRIP')
    for t in range(last):
        need(pre is not None and pre['time_s']==t,'PRE_GAP');nxt=next(pi,None);r=next(po,None)
        need(r is not None and r['time_begin_s']==t and r['time_end_s']==r['observed_time_s']==t+1,'POST_TIME_GAP')
        a0,a1=next(ai,None),next(ai,None)
        need(a0 and a1 and a0['requested_target_s']==a1['requested_target_s']==t+1 and a0['ACK_received'] is True and a0['actual_time_verified'] is False and a0['actual_readback_s'] is None and a1['ACK_received'] is True and a1['actual_time_verified'] is True and a1['actual_readback_s']==t+1,'TWO_STAGE_ACK')
        acks.extend((a0,a1));f=next(fi,None);need(f is not None and f[0]==t,'FCD_TIME_GAP');frame=f[1];endpoint=frame
        for vid,v in frame.items():
            q=observed.setdefault(vid,dict(first=t,last=t));q['last']=t
        p=pre['bound_snapshot'];w=p['world'];z=r['post_world']
        populations.update(before_vehicle_steps=len(w),after_vehicle_steps=len(z),speed_difference_checks=len(set(w)&set(z)),acceleration_checks=len(z))
        serialized_population(p,t);strict_numeric(r)
        need(set(frame)==set(z),'FCD_WORLD_POPULATION')
        for vid,v in frame.items():need(v['lane']==z[vid]['lane_id'] and abs(float(v['speed'])-z[vid]['speed_m_s'])<=.51e-8,'FCD_WORLD_LANE_SPEED')
        before=next(ji,None);after=next(ji,None)
        need(before is not None and after is not None,'IDENTITY_JOURNAL_GAP')
        identity_journal(before,t,'BEFORE_MOTION',w,p)
        identity_journal(after,t+1,'AFTER_ACK',z,nxt['bound_snapshot'] if nxt else None)
        ic=r['identity_change'];need(set(w)-set(z)==set(ic['arrived_ids'])==set(ic['before_only_ids']) and set(z)-set(w)==set(ic['after_only_ids']) and set(ic['after_only_ids'])<=set(ic['departed_ids']),'WORLD_ID_CHANGE')
        pending=r['terminal_arrival_pending'];need(len(pending)==len(ic['arrived_ids']) and {q['vehicle_id'] for q in pending}==set(ic['arrived_ids']),'ARRIVAL_POPULATION')
        for q in pending:
            need(q==dict(p['terminal_before'][q['vehicle_id']],time_begin_s=t,time_end_s=t+1,arrived_id_bound=True,status='PENDING_FINAL_TRIPINFO_LAST_MOVEMENT_AUDIT_NOT_ONLINE_COVERED'),'TERMINAL_BEFORE_BINDING')
            check=audit_terminal(q,[tripby[q['vehicle_id']]] if q['vehicle_id'] in tripby else [],edges);check.setdefault('vehicle_id',q['vehicle_id']);arrivals.append(check)
            if check['status']=='FAIL':alarms.append(dict(kind='TERMINAL_MOVEMENT',detail=check))
            elif check['status']!='PASS':missing.append(dict(kind='TERMINAL_MOVEMENT',detail=check))
        need(r['accounting_complete'] is True,'ADVANCED_UNACCOUNTED_PREFIX')
        state=tls[t,'ramp_mid']['state'];need(state==r['motion'] and int(tls[t,'ramp_mid']['phase'])==r['phase_observation']['phase_after'],'NATIVE_TLS_POST_STATE')
        if t>=600:signal_validate(r,dict(phase=p['motion_phase'],state=p['motion'],program=p['program'],ACK_s=t+1))
        xs,checked=body_frame(t,r,w,frame,state,p['terminal_before'],active,binding,cleared);body_checked+=checked
        need(all(x['motion'] in ('G','y') for x in xs),'RED_NEW_FRONT_ENTRY')
        entries.extend(xs)
        bo=r['braking_observation'];need(set(bo['speed_difference_ids'])==set(bo['speed_difference_m_s2'])==set(w)&set(z) and set(bo['after_acceleration_ids'])==set(bo['actual_acceleration_m_s2'])==set(z),'BRAKING_COVERAGE')
        for vid in set(w)&set(z):
            dv=z[vid]['speed_m_s']-w[vid]['speed_m_s'];need(near(bo['speed_difference_m_s2'][vid],dv),'BRAKING_DELTA_VALUE')
            if dv< -4.5-1e-6:alarms.append(dict(kind='EXCESSIVE_SPEED_DIFFERENCE',time_s=t,id=vid,value=dv))
        for vid,v in bo['actual_acceleration_m_s2'].items():
            need(type(v) in (int,float),'ACCELERATION_UNKNOWN')
            if v< -4.5-1e-6:alarms.append(dict(kind='EXCESSIVE_ACCELERATION',time_s=t,id=vid,value=v))
        counters=r['native_event_counters'];need(set(counters)=={'colliding_vehicles','starting_teleports','ending_teleports'},'NATIVE_COUNTER_SCHEMA')
        for name,v in counters.items():
            need(type(v) is int and v>=0,'NATIVE_COUNTER_VALUE')
            if v:alarms.append(dict(kind=name,time_s=t,value=v))
        warning=r['warning_observation'];need(warning['time_begin_s']==t and warning['time_end_s']==t+1,'WARNING_INTERVAL')
        if warning['text']:alarms.append(dict(kind='NATIVE_INTERVAL_MESSAGE',time_s=t,text=warning['text']))
        if t>=600:
            need(type(p['receiver']['available']) is bool and type(r['post_receiver']['available']) is bool,'RECEIVER_UNKNOWN')
            constraints['empty_storage_seconds']+=not p['storage'];constraints['receiver_unavailable_seconds']+=not p['receiver']['available']
            for d,when,world,meta in [(p.get('native_receiver_decision'),t,w,p['terminal_before']),(r.get('post_native_receiver_decision'),t+1,z,{})]:
                if d and d['decision']!='READY':
                    if d['decision']=='STOP_CURRENT_GAP_BOUND_DENIED':
                        need(when==last and when==t+1,'NONTERMINAL_GAP_STOP');gap_stop(receipt,r)
                    else:need(d['decision']=='WAIT_NATIVE_FOLLOWING','UNEXPECTED_RECEIVER_DECISION')
                    following(d['current_following'],d['current_following']['vehicle_id'],when,world,meta,alarms,advisories)
                    constraints['WAIT_observations' if d['decision']=='WAIT_NATIVE_FOLLOWING' else 'terminal_gap_denials']+=1
            fs=r['actual_entry_following'];need(len(fs)==len(xs) and {q['vehicle_id'] for q in fs}=={x['vehicle_id'] for x in xs},'ENTRY_FOLLOWING_POPULATION')
            for q in fs:
                following(q['before'],q['vehicle_id'],t,w,p['terminal_before'],alarms,advisories);following(q['after'],q['vehicle_id'],t+1,z,{},alarms,advisories)
        if t>=600:
            q=queue_extent(frame,p['terminal_before'],lane_lengths,t);queue_rows.append(q)
            if q['missing_length_ids']:missing.append(dict(kind='MISSING_QUEUE_BODY_LENGTH',time_s=t,ids=q['missing_length_ids']))
        if 1200<=t<3000:
            counts,ctx=urban_frame(frame,tls[t,'urban_tls']['state'],t);urban.update(counts);contexts.extend(ctx)
        small_pre.append(dict(time_s=t,phase_requests=pre['phase_requests'],bound_snapshot={k:p[k] for k in ('time_s','cycle_id','program','motion','motion_phase')}))
        keys=('time_begin_s','observed_time_s','time_end_s','status','accounting_complete','accounting','actual_crossings','post_signal_application_binding','motion','rate_chain','phase_observation','reasons','terminal_reason','native_event_counters','post_native_receiver_decision','post_receiver')
        small={k:r[k] for k in keys if k in r}
        if t>=600:small['constraint_observation']=dict(empty_storage=not p['storage'],receiver_available=p['receiver']['available'],WAIT_before=(p.get('native_receiver_decision') or {}).get('decision')=='WAIT_NATIVE_FOLLOWING')
        small['post_world']={q['vehicle_id']:{} for q in r['actual_crossings']};small_post.append(small)
        pre=nxt
    need(next(po,None) is None and next(ai,None) is None and next(fi,None) is None,'EXTRA_POST_ACK_FCD')
    extra_pre=[]
    if pre is not None:
        need(pre['time_s']==last and next(pi,None) is None,'EXTRA_PRE_TIME');extra_pre=[pre]
        identity_journal(next(ji),last,'BEFORE_MOTION',pre['bound_snapshot']['world'],pre['bound_snapshot'])
    need(next(ji,None) is None,'EXTRA_IDENTITY_JOURNAL')
    need(set(x['vehicle_id'] for x in arrivals if x.get('vehicle_id'))=={q['id'] for q in trips if float(q['arrival'])>=0} and len(arrivals)==len({q['id'] for q in trips if float(q['arrival'])>=0}),'NORMAL_ARRIVAL_COVERAGE')
    need(sorted(active)==receipt['body_censored_ids'],'BODY_CENSOR_RECEIPT')
    return dict(pre=small_pre,post=small_post,acks=acks,tls=tls,observed=observed,endpoint=endpoint,entries=entries,body_rows=body_checked,alarms=alarms,missing=missing,advisories=advisories,arrivals=arrivals,constraints=dict(constraints),populations=dict(populations),urban_counts=[dict(lane=k[0],vehicle_class=k[1],metric=k[2],value=v) for k,v in urban.items()],urban_contexts=contexts,queue_rows=queue_rows,extra_pre_count=len(extra_pre),identity_scope='STREAMING_CURRENT_AND_NEXT_PRE; FINAL_AFTER_WITHOUT_NEXT_PRE_SINGLE_JOURNAL')
