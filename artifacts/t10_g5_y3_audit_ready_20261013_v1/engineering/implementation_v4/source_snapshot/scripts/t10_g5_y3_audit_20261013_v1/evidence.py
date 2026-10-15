"""Independent body/log/serialized identity checks; no new safety thresholds."""
import hashlib
from scripts.t10_g5_y3_audit_20261013_v1.core import need,near,number
INTERNAL=':ramp_mid_0_0'
STORAGE='ramp_storage_0'
STREAMS={'sumo_stdout.log','sumo_stderr.log','sumo_error.log','sumo.log'}
ROUTES={'M':['main_up','merge_section','main_down'],'R':['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'],'U':['urban_in','shared_approach','urban_out'],'X':['cross_in','cross_out']}

def serialized_population(snapshot,t):
    world=snapshot['world'];meta=snapshot['terminal_before']
    need(set(world)==set(meta),'SERIALIZED_IDENTITY_POPULATION')
    for vid,w in world.items():
        v=meta[vid];role=vid.split('_',1)[0]
        need(role in ROUTES and w['role']==role and v['vehicle_id']==vid and v['time_s']==t,'SERIALIZED_ID_ROLE_TIME')
        need(v['type_id']=='technical_passenger' and v['route']==ROUTES[role] and v['terminal_edge']==ROUTES[role][-1],'SERIALIZED_TYPE_ROUTE')
        need(number(w['speed_m_s']) and 0<=w['speed_m_s']<=55.55555555555556 and near(v['speed_m_s'],w['speed_m_s']) and v['lane_id']==w['lane_id'] and near(v['normal_decel_m_s2'],4.5) and near(v['length_m'],5) and number(v['position_m']) and number(v['acceleration_m_s2']),'SERIALIZED_DYNAMICS')
    return {'scope':'SERIALIZED_FIELDS_ONLY_RUNTIME_EFFECTIVE_GETTERS_NOT_RECONSTRUCTED'}

def body_frame(i,row,before,frame,state,metadata,active,binding,cleared):
    ids=sorted(v for v,x in frame.items() if v.startswith('R_flow.') and x['lane']==INTERNAL and v in before and before[v]['lane_id']==STORAGE)
    entries=[]
    for vid in ids:
        need(vid not in binding,'INDEPENDENT_DUPLICATE_ENTRY')
        x={'vehicle_id':vid,'time_begin_s':i,'time_end_s':i+1,'motion':state};entries.append(x);binding[vid]=x;active.add(vid)
    need(ids==sorted(q['vehicle_id'] for q in row.get('actual_crossings',[])),'INDEPENDENT_FCD_CROSSINGS')
    obs=row.get('body_observation');need(isinstance(obs,dict),'MISSING_BODY_OBSERVATION')
    need(obs['ACK_s']==i+1 and obs['signal']==state,'BODY_ACK_SIGNAL')
    internal={v for v,x in frame.items() if x['lane']==INTERNAL};need(active<=internal,'BODY_MISSING_BEFORE_CLEAR')
    rows={q['vehicle_id']:q for q in obs['rows']};need(len(rows)==len(obs['rows']) and set(rows)==active,'BODY_ACTIVE_IDS');spanning=set()
    for vid in internal:
        length=metadata[vid]['length_m']
        if float(frame[vid]['pos'])-length<=0:spanning.add(vid)
    need(set(obs['spanning_ids'])==spanning,'ALL_SPANNING_POPULATION')
    for vid,q in rows.items():
        x=binding[vid];length=metadata[vid]['length_m']
        need(q['entry_time_begin_s']==x['time_begin_s'] and q['entry_time_end_s']==x['time_end_s'] and q['entry_signal']==x['motion'] and q['observed_ACK_s']==i+1 and q['observed_signal']==state,'BODY_ENTRY_TIME_ID_SIGNAL')
        need(abs(q['head_position_m']-float(frame[vid]['pos']))<.51e-8 and q['length_m']==length==5 and abs(q['speed_m_s']-float(frame[vid]['speed']))<.51e-8 and near(q['rear_position_m'],q['head_position_m']-length),'BODY_DYNAMICS')
        if vid in spanning:need(q['status']=='REAR_SPANS_LINE','BODY_SPAN_STATUS')
        else:
            need(q['status']=='REAR_CLEAR_OBSERVED' and q['first_actual_rear_clear_ACK_s']==i+1 and vid not in cleared,'BODY_CLEAR_STATUS');cleared[vid]=i+1;active.remove(vid)
    return entries,len(rows)

def log_eof(logs,raw,receipt):
    need(bool(logs),'MISSING_LOG_JOURNAL');cursor=dict.fromkeys(STREAMS,0)
    for rec in logs:
        need(set(rec['streams'])==STREAMS,'FOUR_NATIVE_STREAMS')
        for name,v in rec['streams'].items():
            content=(raw/name).read_bytes();lo,hi=v['byte_start'],v['byte_end']
            need(type(lo) is int and type(hi) is int and lo==cursor[name] and 0<=lo<=hi<=len(content) and hashlib.sha256(content[:hi]).hexdigest()==v['prefix_sha256'] and hashlib.sha256(content[lo:hi]).hexdigest()==v['fragment_sha256'],'LOG_INTERVAL_HASH_OR_GAP');cursor[name]=hi
    eof=logs[-1];need(eof['stage']=='AFTER_NATIVE_CLOSE_PROCESS_EOF' and all(v['byte_end']==(raw/n).stat().st_size for n,v in eof['streams'].items()),'FINAL_NATIVE_EOF')
    need(receipt['final_logs']['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF','RECEIPT_EOF')
    return True


def strict_numeric(row):
    need('numeric_stop_classifications' in row and row['numeric_stop_classifications']==[],'UNAUTHORIZED_NUMERICAL_CLASSIFICATION_OR_MISSING_STRICT_RECORD')

def checkpoint(cp,reds):
    need(isinstance(cp,dict) and bool(reds),'MISSING_ACTUAL_FIRST_RED_CHECKPOINT')
    need(cp['time_s']==reds[0]['time_end_s'] and cp['first_controlled_red_begin_s']==reds[0]['time_begin_s'] and cp['accounting']==reds[0]['accounting'] and cp['log_scope']=='PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED','ACTUAL_FIRST_RED_CP')

def yellow_record(yy,cycles,world,meta,last):
    t=yy['time_s'];need(type(t) is int and t==yy['source_post_frame_time_s'] and 1200<t<=last,'YELLOW_SOURCE_CLOCK')
    selected=[c for c in cycles if c['begin_s']<t<=c['begin_s']+5];need(len(selected)==1,'YELLOW_CYCLE_BINDING')
    Y=selected[0]['yellow_s'];need(yy['yellow_s']==Y==3,'YELLOW_PERIOD')
    need(meta is not None,'MISSING_YELLOW_METADATA')
    need(len({q['vehicle_id'] for q in yy['rows']})==len(yy['rows']) and {q['vehicle_id'] for q in yy['rows']}==set(yy['covered_ids'])=={v for v,w in world.items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')},'YELLOW_LOCAL_COMPLETE')
    need(yy['status']=='PASS','UNKNOWN_LOCAL_YELLOW_SCOPE')
    for q in yy['rows']:
        vid=q['vehicle_id'];v=meta[vid];offset=113.08 if q['population']=='ingress' else 0
        need(q['time_s']==t and near(q['speed_m_s'],world[vid]['speed_m_s']) and q['native_future_safety_proven'] is False,'YELLOW_REAL_SPEED_ID')
        need(near(q['position_m'],v['position_m']-offset) and near(q['length_m'],v['length_m']) and near(q['normal_decel_m_s2'],v['normal_decel_m_s2']),'YELLOW_REAL_FIELDS')
        d=204.49-q['position_m'];speed=q['speed_m_s'];b=q['normal_decel_m_s2'];length=q['length_m'];dt=q['action_step_s']
        need(number(speed) and 0<=speed<=55.55555555555556 and number(d) and near(b,4.5) and near(length,5) and near(dt,1),'YELLOW_EFFECTIVE_MODEL_BOUND')
        one=d>0 and speed<=b*dt;stop=d>0 and (one or d>=speed*dt+speed*speed/(2*b));timing=None if speed==0 else dt+speed/(2*b)+length/speed;clear=speed>0 and timing<=Y and d+length<=speed*(Y-dt)
        need(q['one_step_Euler_stop_possible']==one and near(q['distance_to_meter_m'],d) and q['stop_possible']==stop and q['clear_possible']==clear,'YELLOW_INDEPENDENT_SCREEN')
        need(stop or clear,'UNKNOWN_LOCAL_YELLOW_SCOPE')
    return True


EXPECTED_DYNAMICS={'accel_m_s2':2.6,'normal_decel_m_s2':4.5,'emergency_decel_m_s2':9.,'tau_s':1.,'action_step_s':1.,'sigma':.5,'max_speed_m_s':55.55555555555556}
def identity_journal(record,t,stage,world,source_snapshot=None):
    need(type(record.get('time_s')) is int and record['time_s']==t and record.get('stage')==stage and record.get('setter_calls')==0,'IDENTITY_JOURNAL_CLOCK_OR_STAGE')
    pools=[]
    for key in ('active_ids','loaded_ids','pending_ids'):
        x=record.get(key);need(isinstance(x,list) and len(x)==len(set(x)) and all(isinstance(v,str) for v in x),'IDENTITY_JOURNAL_ID_LIST');pools.append(set(x))
    need(pools[0]==set(world) and set(record.get('vehicle_states',{}))==set.union(*pools),'IDENTITY_JOURNAL_POPULATION')
    if source_snapshot is not None:
        need(type(source_snapshot.get('time_s')) is int and source_snapshot['time_s']==t and set(source_snapshot.get('world',{}))==set(world),'INDEPENDENT_IDENTITY_POOL_SOURCE_TIME')
        for journal_key,source_key in [('loaded_ids','loaded'),('pending_ids','pending_ids')]:
            pool=source_snapshot.get(source_key)
            need(isinstance(pool,(list,tuple)) and len(pool)==len(set(pool)) and all(isinstance(v,str) for v in pool),'INDEPENDENT_IDENTITY_POOL_SOURCE_MISSING_OR_DUPLICATE')
            need(set(record[journal_key])==set(pool),'INDEPENDENT_IDENTITY_POOL_MISMATCH')
    for vid,v in record['vehicle_states'].items():
        role=vid.split('_',1)[0];need(role in ROUTES and v.get('vehicle_id')==vid and type(v.get('time_s')) is int and v['time_s']==t and v.get('type_id')=='technical_passenger' and v.get('route')==ROUTES[role],'IDENTITY_JOURNAL_ID_TYPE_ROUTE')
        need(type(v.get('speed_mode')) is int and v['speed_mode']==31 and type(v.get('lane_change_mode')) is int and v['lane_change_mode']==1621,'IDENTITY_JOURNAL_MODES')
        need(all(near(v.get(k),x) for k,x in EXPECTED_DYNAMICS.items()),'IDENTITY_JOURNAL_DYNAMICS')
    return {'pool_scope':'INDEPENDENT_SAME_TIME_PRE_POOL_CHECK' if source_snapshot is not None else 'SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK'}


def identity_prefix(journal,pre,post,last):
    need(type(last) is int and last>=0 and len(post)==last and last<=len(pre)<=last+1,'IDENTITY_PREFIX_FRAME_COVERAGE')
    need(len(journal)==2*last+(len(pre)-last),'IDENTITY_JOURNAL_ACK_COVERAGE')
    after_sources=[]
    for i in range(last):
        identity_journal(journal[2*i],i,'BEFORE_MOTION',pre[i]['bound_snapshot']['world'],pre[i]['bound_snapshot'])
        independent_after=pre[i+1]['bound_snapshot'] if i+1<len(pre) else None
        identity_journal(journal[2*i+1],i+1,'AFTER_ACK',post[i]['post_world'],independent_after)
        after_sources.append('NEXT_SAME_TIME_PRE_INDEPENDENT_POOL_CHECK' if independent_after is not None else 'SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK')
    if len(pre)>last:
        need(pre[last]['time_s']==last,'EXTRA_PRE_SOURCE_TIME')
        identity_journal(journal[-1],last,'BEFORE_MOTION',pre[last]['bound_snapshot']['world'],pre[last]['bound_snapshot'])
    return {'complete_motion_intervals':last,'prepared_not_observed_last_PRE':len(pre)>last,'after_pool_sources':after_sources,'terminal_AFTER_pools_independently_verified':bool(after_sources and after_sources[-1]=='NEXT_SAME_TIME_PRE_INDEPENDENT_POOL_CHECK')}

def yellow_coverage(records,phase,cycles,post,pre,last,runtime_stop):
    need(phase.get('status')=='PASS_CONTINUOUS_PHASES','UNKNOWN_PHASE_FOR_YELLOW_COVERAGE')
    expected={}
    for c in phase['cycles']:
        seq=c['observed_motion_sequence']
        if 'y' in seq:
            t=c['begin_s']+seq.index('y');need(c['green_end_s']==t and t not in expected,'YELLOW_OBSERVED_PHASE_BOUNDARY');expected[t]=c
    times=[q.get('time_s') for q in records]
    need(all(type(t) is int for t in times) and len(times)==len(set(times)),'DUPLICATE_OR_INVALID_YELLOW_RECORD')
    need(set(expected)<=set(times),'MISSING_OBSERVED_YELLOW_SCREEN')
    extras=set(times)-set(expected);need(len(extras)<=1,'EXTRA_UNBOUND_YELLOW_SCREEN')
    for q in records:
        t=q['time_s'];need(q.get('screen_stage')=='PREPARED_BEFORE_FIRST_Y_MOTION' and q.get('source_program')=='T10_G5Y3_NATIVE' and q.get('source_motion')=='y','YELLOW_SCREEN_SOURCE_PHASE')
        need(t<len(pre) and pre[t]['bound_snapshot']['time_s']==t and pre[t]['bound_snapshot']['motion']=='y' and pre[t]['bound_snapshot']['program']=='T10_G5Y3_NATIVE','YELLOW_PREPARATION_PHASE_JOIN')
        if t in extras:
            need(runtime_stop is True and t==last and len(pre)==last+1,'EXTRA_YELLOW_NOT_BOUND_TO_ABORTED_PREPARED_PREFIX')
        yellow_record(q,cycles,post[t-1]['post_world'],pre[t]['bound_snapshot']['terminal_before'],last)
    return {'observed_first_Y_count':len(expected),'validated_records':len(records),'prepared_not_observed_times':sorted(extras),'future_native_safety_proven':False}
