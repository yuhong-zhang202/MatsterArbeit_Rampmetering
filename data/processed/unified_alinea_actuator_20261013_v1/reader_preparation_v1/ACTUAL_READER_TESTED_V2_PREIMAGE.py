"""Immutable actual-run orchestration; no simulation imports or launch API.

The CLI needs an engineering-frozen manifest and a new processed output directory.
Counts use independent FCD storage-to-internal movement, not reported crossings.
"""
from pathlib import Path
import argparse,collections,gzip,hashlib,importlib.util,json,math,sys,traceback,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.unified_alinea_audit_20261013_v1.core import audit_accounting,audit_phases,audit_feedback,need,near,number
from scripts.unified_alinea_audit_20261013_v1.signal_binding_v2 import validate as signal_validate
spec=importlib.util.spec_from_file_location('protected_terminal_audit',ROOT/'data/processed/issue12_alinea_actuation_20261012_v1/audit_data_V3.py')
terminal=importlib.util.module_from_spec(spec);spec.loader.exec_module(terminal)
STORAGE='ramp_storage_0';INGRESS=':urban_diverge_1_0';INTERNAL=':ramp_mid_0_0'
STREAMS={'sumo_stdout.log','sumo_stderr.log','sumo_error.log','sumo.log'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def lines(p):return [json.loads(x) for x in Path(p).open() if x.strip()]
def flatten(rows):
    out=[]
    for row in rows:
        if 'retained_receipts' in row:
            need(isinstance(row['retained_receipts'],list) and len(row['retained_receipts'])<=1,'FAILED_PREFIX_WRAPPER_SCHEMA')
            out.extend(row['retained_receipts'])
        else:out.append(row)
    need(all(r.get('time_begin_s')==i for i,r in enumerate(out)),'DUPLICATE_OR_MISSING_POST_PREFIX')
    return out

def following(q,vid,t,world,metadata,alarms):
    need(isinstance(q,dict) and q.get('vehicle_id')==vid and q.get('time_s')==t and vid in world,'CURRENT_QUERY_ID_TIME')
    need(q.get('speed_mode')==31 and q.get('lane_change_mode')==1621 and near(q.get('actual_speed_m_s'),world[vid]['speed_m_s']) and q.get('lane_id')==world[vid]['lane_id'],'CURRENT_QUERY_MODES_SPEED_LANE')
    need(q.get('route')==['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'] and q.get('lookahead_m')==478.67 and q.get('future_safety_proven') is False and q.get('margin_m')==1.1,'CURRENT_QUERY_SCOPE')
    if vid in metadata:
        v=metadata[vid];need(near(q.get('lane_position_m'),v['position_m']) and near(q.get('vehicle_length_m'),v['length_m']),'CURRENT_QUERY_POSITION_LENGTH')
    status=q.get('status');fresh=q.get('fresh_getLeader_result')
    if status=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD':
        need(fresh is None or fresh==['',-1],'CLEAR_VALID_EMPTY_RESULT');return
    need(status in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','STOP_CURRENT_GAP_BOUND_DENIED'),'UNKNOWN_CURRENT_QUERY_STATUS')
    leader=q.get('leader_id');args=q.get('getSecureGap_args',{});gap=q.get('gap_excluding_minGap_m');secure=q.get('actual_secure_gap_m');mg=q.get('min_gap_m')
    need(leader in world and isinstance(fresh,list) and fresh==[leader,gap] and all(number(x) and x>=0 for x in (gap,secure,mg)),'LEADER_FRESH_RESULT')
    need(args.get('vehID')==vid and args.get('leaderID')==leader and near(args.get('speed'),world[vid]['speed_m_s']) and near(args.get('leaderSpeed'),world[leader]['speed_m_s']) and args.get('leaderMaxDecel')==9 and near(q.get('leader_speed_m_s'),world[leader]['speed_m_s']) and q.get('leader_lane_id')==world[leader]['lane_id'],'CURRENT_SECURE_QUERY_PRIMITIVES')
    need(near(q.get('physical_bumper_gap_m'),gap+mg) and near(q.get('required_with_margin_m'),secure+1.1),'CURRENT_GAP_UNITS')
    passed=gap+mg>0 and gap+1e-9>=secure+1.1
    need((status=='CURRENT_GAP_OBSERVED_WITHIN_BOUND')==passed,'CURRENT_QUERY_CLASSIFICATION')
    if not passed:alarms.append({'kind':'CURRENT_PROJECT_GAP_CONTRACT_DENIED','time_s':t,'vehicle_id':vid,'gap_m':gap,'queried_secure_m':secure,'margin_m':1.1,'native_unsafe_proven':False})

def net_path_from_card(card):
    cfg=ET.parse(ROOT/card['package']/'scenario.sumocfg').getroot();p=Path(cfg.find('./input/net-file').get('value'));return p if p.is_absolute() else ROOT/card['package']/p

def audit(manifest_path,card_path):
    manifest_path=Path(manifest_path);card_path=Path(card_path);m=read(manifest_path);card=read(card_path);raw=ROOT/card['output'];approved_end=card['spec']['end_s'];run=card['spec']['run_id']
    need(card['classification']=='BOUNDED_UNIFIED_NATIVE_TECHNICAL_DIAGNOSTIC_NOT_FORMAL' and card['spec']['step_s']==1 and card['spec']['activation_s']==1200,'APPROVED_DIAGNOSTIC_SCOPE')
    need(raw.is_dir(),'NO_ACTUAL_RAW_RUN')
    for name,value in m['files'].items():need(sha(ROOT/name)==(value['sha256'] if isinstance(value,dict) else value),'RAW_SHA_DRIFT:'+name)
    parent=raw.parent;actual={str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()};need(actual==set(m['files']),'RAW_MANIFEST_INVENTORY')
    need(sum((ROOT/f).stat().st_size for f in actual)==m['bytes'],'RAW_BYTES')
    need(read(raw/'card.json')==card,'ACTUAL_CARD_IDENTITY')
    need(sha(net_path_from_card(card))==card['network_sha256'],'NETWORK_CARD_DRIFT')
    for name,h in card['environment']['files_sha256'].items():need(sha(Path(name))==h,'ENVIRONMENT_BOUND_BYTES_DRIFT:'+name)
    for key in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
        for name,h in card[key].items():need(sha(ROOT/name)==h,'CARD_BOUND_SOURCE_INPUT_DRIFT:'+name)
    need(card['resources']=={'wall_limit_s':300,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000} and card['spec']['total_resource_envelope']=={'monitored_s':1200,'raw_bytes':1200000000},'RESOURCE_BOUNDARY')
    receipt=read(raw/'bridge_receipt.json');need(receipt['run_id']==run and receipt['card_sha256']==sha(card_path),'EXECUTED_CARD_RECEIPT')
    last=receipt.get('last_completed_s');need(type(last) in (int,float) and last==int(last) and 0<=last<=approved_end,'LAST_ACK');last=int(last)
    pre=lines(raw/'pre_steps.jsonl');post=flatten(lines(raw/'post_steps.jsonl'));acks=lines(raw/'step_ack.jsonl');logs=lines(raw/'log_intervals.jsonl')
    need(len(post)==last and last<=len(pre)<=last+1 and len(acks)==2*last,'PREFIX_COVERAGE')
    tls=[v.attrib.copy() for v in ET.parse(raw/'tls_states.xml').getroot() if v.get('id')=='ramp_mid']
    need(len(tls)==last and all(number(float(q['time'])) and float(q['time'])==i for i,q in enumerate(tls)),'ORDERED_TLS_PREFIX')
    cfg=ET.parse(ROOT/card['package']/'scenario.sumocfg').getroot();net=Path(cfg.find('./input/net-file').get('value'));net=net if net.is_absolute() else ROOT/card['package']/net
    lanes={e.get('id'):[x.get('id') for x in e.findall('lane')] for e in ET.parse(net).getroot().findall('edge')}
    trips=[x.attrib for x in ET.parse(raw/'tripinfo.xml').getroot().findall('tripinfo')];trip_by=collections.defaultdict(list)
    for trip in trips:trip_by[trip['id']].append(trip)
    need(all(len(v)==1 for v in trip_by.values()),'DUPLICATE_TRIP_ID')
    arrivals=[];alarms=[];missing=[];wait=0;brakes=[];accelerations=[];counter_values=[];entry_following_ids={};complete=[]
    for i,r in enumerate(post):
        b=pre[i];need(b['time_s']==i and r['time_begin_s']==i and r['time_end_s']==i+1,'INTERVAL_TIME')
        a0,a1=acks[2*i:2*i+2];need(a0['requested_target_s']==i+1 and a0['ACK_received'] is True and a0['actual_time_verified'] is False and a0['actual_readback_s'] is None and a1['requested_target_s']==i+1 and a1['ACK_received'] is True and a1['actual_time_verified'] is True and a1['actual_readback_s']==i+1,'ACK_PAIR')
        w=b['bound_snapshot']['world'];z=r.get('post_world');need(isinstance(z,dict),'MISSING_ADVANCED_WORLD')
        ic=r.get('identity_change');need(isinstance(ic,dict),'MISSING_IDENTITY_CHANGE')
        need(set(w)-set(z)==set(ic['arrived_ids'])==set(ic['before_only_ids']) and set(z)-set(w)==set(ic['after_only_ids']) and set(ic['after_only_ids'])<=set(ic['departed_ids']),'WORLD_IDENTITIES')
        pending=r.get('terminal_arrival_pending');need(isinstance(pending,list) and len(pending)==len(ic['arrived_ids']) and {q['vehicle_id'] for q in pending}==set(ic['arrived_ids']),'ALL_ARRIVAL_METADATA')
        for q in pending:
            need(q==dict(b['bound_snapshot']['terminal_before'][q['vehicle_id']],time_begin_s=i,time_end_s=i+1,arrived_id_bound=True,status='PENDING_FINAL_TRIPINFO_LAST_MOVEMENT_AUDIT_NOT_ONLINE_COVERED'),'TERMINAL_BEFORE_EXACT')
            result=terminal.audit_terminal(q,trip_by[q['vehicle_id']],lanes);arrivals.append(result)
            if result['status']!='PASS':missing.append({'kind':'TERMINAL_LAST_MOVEMENT_'+result['status'],'result':result})
        if r.get('accounting_complete') is True:
            need(len(complete)==i,'ACCOUNTING_PREFIX_HOLE');complete.append(r)
            if i>=1200:
                expected={'phase':b['bound_snapshot']['motion_phase'],'state':b['bound_snapshot']['motion'],'program':b['bound_snapshot']['program'],'ACK_s':i+1};signal_validate(r,expected)
            bo=r['braking_observation'];need(set(bo['speed_difference_ids'])==set(w)&set(z) and set(bo['speed_difference_m_s2'])==set(w)&set(z) and set(bo['after_acceleration_ids'])==set(z) and set(bo['actual_acceleration_m_s2'])==set(z),'BRAKING_POPULATION')
            for vid in set(w)&set(z):
                dv=z[vid]['speed_m_s']-w[vid]['speed_m_s'];need(near(dv,bo['speed_difference_m_s2'][vid]),'BRAKING_VALUE');brakes.append(dv)
                if dv< -4.5-1e-6:alarms.append({'kind':'NORMAL_BRAKING_BOUND','vehicle_id':vid,'ACK_s':i+1,'value':dv})
            for vid,a in bo['actual_acceleration_m_s2'].items():
                need(number(a),'ACCELERATION_NUMERIC');accelerations.append(a)
                if a< -4.5-1e-6:alarms.append({'kind':'NORMAL_ACCELERATION_BOUND','vehicle_id':vid,'ACK_s':i+1,'value':a})
            for name,v in r['native_event_counters'].items():
                need(type(v) is int and v>=0,'NATIVE_EVENT_COUNT');counter_values.append(v)
                if v:alarms.append({'kind':name,'ACK_s':i+1,'value':v})
            need(int(tls[i]['phase'])==r['phase_observation']['phase_after'] and tls[i]['state']==r['motion'],'ACTUAL_TLS_STATE')
            for d,t,world,meta in [(b['bound_snapshot'].get('native_receiver_decision'),i,w,b['bound_snapshot']['terminal_before']),(r.get('post_native_receiver_decision'),i+1,z,{})]:
                if d and d['decision']!='READY':
                    following(d['current_following'],d['current_following']['vehicle_id'],t,world,meta,alarms);wait+=d['decision']=='WAIT_NATIVE_FOLLOWING'
            expected_ids={q['vehicle_id'] for q in r['actual_crossings']};ef=r['actual_entry_following'];need(len(ef)==len(expected_ids) and {q['vehicle_id'] for q in ef}==expected_ids,'ENTRY_BEFORE_AFTER_COVERAGE')
            for q in ef:
                following(q['before'],q['vehicle_id'],i,w,b['bound_snapshot']['terminal_before'],alarms);following(q['after'],q['vehicle_id'],i+1,z,{},alarms)
            entry_following_ids[i]=expected_ids
            if r.get('status') not in ('RECONCILED_DIAGNOSTIC_ONLY','MANDATORY_FIRST_RED_CHECKPOINT_PENDING','APPROVED_TECHNICAL_END_MANDATORY_STOP_NOT_QUALIFIED'):alarms.append({'kind':'RUNTIME_STOP','interval_begin_s':i,'status':r.get('status'),'reasons':r.get('reasons')})
        else:missing.append({'kind':'UNRECONCILED_ADVANCED_INTERVAL','interval_begin_s':i,'retained_fields':sorted(r),'binding':r.get('post_signal_application_binding')})
    need({q['vehicle_id'] for q in arrivals}=={v['id'] for v in trips if float(v['arrival'])>=0} and len(arrivals)==len({q['vehicle_id'] for q in arrivals}),'ALL_COMPLETED_ARRIVALS')
    entries=[];active=set();binding={};cleared={};body_rows=0;frame_count=0;shared=[]
    with gzip.open(raw/'fcd.xml.gz','rb') as stream:
        for _,elem in ET.iterparse(stream,events=('end',)):
            if elem.tag!='timestep':continue
            t=float(elem.get('time'));need(t==frame_count and frame_count<last,'FCD_ORDERED_TIME');i=frame_count;r=post[i];w=pre[i]['bound_snapshot']['world'];z=r['post_world'];frame={v.get('id'):v.attrib for v in elem}
            need(len(frame)==len(elem) and set(frame)==set(z),'FCD_POPULATION')
            for vid,v in frame.items():need(v['lane']==z[vid]['lane_id'] and abs(float(v['speed'])-z[vid]['speed_m_s'])<=.5e-8+1e-10,'FCD_SPEED_LANE')
            ids=sorted(v for v,x in frame.items() if v.startswith('R_flow.') and x['lane']==INTERNAL and v in w and w[v]['lane_id']==STORAGE)
            for vid in ids:
                need(vid not in binding,'INDEPENDENT_DUPLICATE_ENTRY');x={'vehicle_id':vid,'time_begin_s':i,'time_end_s':i+1,'motion':tls[i]['state']};entries.append(x);binding[vid]=x;active.add(vid)
                if x['motion']=='r':alarms.append({'kind':'INDEPENDENT_RED_FRONT_ENTRY','entry':x})
            need(ids==sorted(q['vehicle_id'] for q in r.get('actual_crossings',[])),'INDEPENDENT_FCD_CROSSINGS')
            obs=r.get('body_observation')
            if obs is None:missing.append({'kind':'MISSING_BODY_OBSERVATION','ACK_s':i+1})
            else:
                need(obs['ACK_s']==i+1 and obs['signal']==tls[i]['state'],'BODY_ACK_SIGNAL');internal={v for v,x in frame.items() if x['lane']==INTERNAL};need(active<=internal,'BODY_MISSING_BEFORE_CLEAR')
                rows={q['vehicle_id']:q for q in obs['rows']};need(len(rows)==len(obs['rows']) and set(rows)==active,'BODY_ACTIVE_IDS');spanning=set()
                for vid in internal:
                    length=pre[i]['bound_snapshot']['terminal_before'][vid]['length_m']
                    if float(frame[vid]['pos'])-length<=0:spanning.add(vid)
                need(set(obs['spanning_ids'])==spanning,'ALL_SPANNING_POPULATION')
                for vid,q in rows.items():
                    x=binding[vid];length=pre[i]['bound_snapshot']['terminal_before'][vid]['length_m']
                    need(q['entry_time_begin_s']==x['time_begin_s'] and q['entry_time_end_s']==x['time_end_s'] and q['entry_signal']==x['motion'] and q['observed_ACK_s']==i+1 and q['observed_signal']==tls[i]['state'],'BODY_ENTRY_TIME_ID_SIGNAL')
                    need(abs(q['head_position_m']-float(frame[vid]['pos']))<.51e-8 and q['length_m']==length==5 and abs(q['speed_m_s']-float(frame[vid]['speed']))<.51e-8 and near(q['rear_position_m'],q['head_position_m']-length),'BODY_DYNAMICS')
                    if vid in spanning:need(q['status']=='REAR_SPANS_LINE','BODY_SPAN_STATUS')
                    else:need(q['status']=='REAR_CLEAR_OBSERVED' and q['first_actual_rear_clear_ACK_s']==i+1 and vid not in cleared,'BODY_CLEAR_STATUS');cleared[vid]=i+1;active.remove(vid)
                    body_rows+=1
            if i>=1200:shared.append({'interval_begin_s':i,'rows':[{'vehicle_id':vid,'speed_m_s':float(v['speed']),'position_m':float(v['pos'])} for vid,v in frame.items() if v['lane']=='shared_approach_0' and vid.startswith(('R_flow.','U_flow.'))]})
            frame_count+=1;elem.clear()
    need(frame_count==last,'FCD_FRAME_COVERAGE');need(sorted(active)==receipt.get('body_censored_ids',[]),'BODY_CENSOR_RECEIPT')
    control=complete[1200:];control_entries=[x for x in entries if 1200<=x['time_begin_s']<len(complete)]
    commands=lines(raw/'command_events.jsonl') if (raw/'command_events.jsonl').exists() else []
    account=audit_accounting(control,commands,control_entries,approved_end)
    try:phase=audit_phases(tls[1200:len(complete)],control,acks[2400:2*len(complete)],account['cycles'],lines(raw/'policy_phase_requests.jsonl'),lines(raw/'policy_duration_requests.jsonl'),pre[1200:len(complete)])
    except Exception as exc:
        phase={'status':'UNKNOWN_PHASE_TRACE_OR_PREFIX','reason':str(exc)};missing.append(phase)
    for cycle in account['cycles']:
        rid=cycle['applied_request_id'];rec=receipt['command_records'][rid];matched=[x for x in account['applications'] if x['request_id']==rid];need(matched and rec['first_application_s']==matched[0]['application_global_s'],'APPLICATION_RECEIPT_BINDING')
    admissions=lines(raw/'body_admission.jsonl');expected=[c['begin_s'] for c in account['cycles']];need([q['ACK_s'] for q in admissions][:len(expected)]==expected and len(admissions)<=len(expected)+1,'BODY_ADMISSION_CYCLE_COVERAGE')
    for q in admissions:need(q['signal']=='r' and not q['spanning_ids'] and not q['rows'],'FRESH_NEW_G_BODY_CLEAR')
    yellow=lines(raw/'yellow_scope.jsonl')
    for yy in yellow:
        t=yy['time_s'];need(t==yy['source_post_frame_time_s'] and 1200<t<=last,'YELLOW_SOURCE_CLOCK');cycle=next(c for c in account['cycles'] if c['begin_s']<t<=c['begin_s']+4);Y=cycle['yellow_s'];need(yy['yellow_s']==Y,'YELLOW_PERIOD')
        world=post[t-1]['post_world'];meta=pre[t]['bound_snapshot']['terminal_before'] if t<len(pre) else None
        need({q['vehicle_id'] for q in yy['rows']}==set(yy['covered_ids'])=={v for v,w in world.items() if w['lane_id'] in (STORAGE,INGRESS)},'YELLOW_LOCAL_COMPLETE')
        for q in yy['rows']:
            vid=q['vehicle_id'];v=meta[vid] if meta else None;offset=113.08 if q['population']=='ingress' else 0
            need(q['time_s']==t and near(q['speed_m_s'],world[vid]['speed_m_s']) and q['native_future_safety_proven'] is False,'YELLOW_REAL_SPEED_ID')
            if v:need(near(q['position_m'],v['position_m']-offset) and near(q['length_m'],v['length_m']) and near(q['normal_decel_m_s2'],v['normal_decel_m_s2']),'YELLOW_REAL_FIELDS')
            else:missing.append({'kind':'NO_NEXT_PRE_YELLOW_METADATA','ACK_s':t})
            d=204.49-q['position_m'];speed=q['speed_m_s'];b=q['normal_decel_m_s2'];length=q['length_m'];dt=q['action_step_s'];one=d>0 and speed<=b*dt;stop=d>0 and (one or d>=speed*dt+speed*speed/(2*b));timing=None if speed==0 else dt+speed/(2*b)+length/speed;clear=speed>0 and timing<=Y and d+length<=speed*(Y-dt)
            need(q['one_step_Euler_stop_possible']==one and near(q['distance_to_meter_m'],d) and q['stop_possible']==stop and q['clear_possible']==clear,'YELLOW_INDEPENDENT_SCREEN')
            if not(stop or clear):missing.append({'kind':'UNKNOWN_LOCAL_YELLOW_SCOPE','vehicle_id':vid,'ACK_s':t})
    need(bool(logs),'MISSING_LOG_JOURNAL')
    for rec in logs:
        need(set(rec['streams'])==STREAMS,'FOUR_NATIVE_STREAMS')
        for name,v in rec['streams'].items():
            content=(raw/name).read_bytes();lo,hi=v['byte_start'],v['byte_end'];need(type(lo) is int and type(hi) is int and 0<=lo<=hi<=len(content) and hashlib.sha256(content[:hi]).hexdigest()==v['prefix_sha256'] and hashlib.sha256(content[lo:hi]).hexdigest()==v['fragment_sha256'],'LOG_INTERVAL_HASH')
    eof=logs[-1];need(eof['stage']=='AFTER_NATIVE_CLOSE_PROCESS_EOF' and all(v['byte_end']==(raw/n).stat().st_size for n,v in eof['streams'].items()),'FINAL_NATIVE_EOF')
    need(receipt['final_logs']['coverage']=='FINAL_FILES_AT_OWNED_PROCESS_EOF','RECEIPT_EOF')
    if receipt['final_logs']['status']!='BOUND_NO_OBSERVED_NATIVE_MESSAGE':alarms.append({'kind':'NATIVE_FINAL_LOG_MESSAGE','reasons':receipt['final_logs'].get('reasons')})
    elapsed=receipt['monitored_elapsed_through_cleanup_s'];need(number(elapsed) and elapsed>=0,'MONITORED_COST_MISSING')
    before=receipt['total_budget_before_run'];need(number(before['charged_monitored_s']) and type(before['charged_raw_bytes']) is int,'NEW_BUDGET_BASELINE')
    if elapsed>300 or m['bytes']>300000000 or before['charged_monitored_s']+elapsed>1200 or before['charged_raw_bytes']+m['bytes']>1200000000:alarms.append({'kind':'RESOURCE_CAP_OBSERVED_EXCEEDED','monitored_s':elapsed,'raw_bytes':m['bytes']})
    feedback_events=lines(raw/'feedback_events.jsonl') if (raw/'feedback_events.jsonl').exists() else []
    if card['spec']['mode']=='real_alinea':
        try:feedback=audit_feedback(feedback_events,commands,account,len(complete))
        except Exception as exc:
            feedback={'status':'UNKNOWN_FEEDBACK_PREFIX','reason':str(exc),'feedback_command_applied':False};missing.append(feedback)
        if not feedback['feedback_command_applied']:missing.append({'kind':'NO_NON_INITIAL_FEEDBACK_COMMAND_APPLIED'})
    else:need(not feedback_events,'UNREQUESTED_FEEDBACK_EVENTS');feedback={'status':'NOT_APPLICABLE_FIXED_OR_SCHEDULED'}
    reds=[q for q in control if q['motion']=='r'];cp=None
    if (raw/'first_red_checkpoint.json').exists():
        cp=read(raw/'first_red_checkpoint.json');need(reds and cp['time_s']==reds[0]['time_end_s'] and cp['first_controlled_red_begin_s']==reds[0]['time_begin_s'] and cp['accounting']==reds[0]['accounting'] and cp['log_scope']=='PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED','ACTUAL_FIRST_RED_CP')
    elif reds:missing.append({'kind':'FIRST_RED_CHECKPOINT_NOT_VERIFIED'})
    demand=ET.parse(ROOT/card['package']/'demand.rou.xml').getroot();planned={v.get('id'):float(v.get('depart')) for v in demand.findall('vehicle')};need(len(planned)==len(demand.findall('vehicle')),'DUPLICATE_PLANNED_ID')
    inserted={v['id'] for v in trips if float(v['depart'])>=0};due={v for v,t in planned.items() if t<last};future=set(planned)-due;unfinished={v['id'] for v in trips if float(v['depart'])>=0 and float(v['arrival'])<0};groups={}
    for role in 'MRUX':
        filt=lambda s:[v for v in s if v.startswith(role+'_flow.')]
        groups[role]={'due_before_last_ACK':len(filt(due)),'future_at_or_after_last_ACK':len(filt(future)),'inserted':len(filt(inserted)),'due_not_inserted':len(filt(due-inserted)),'unfinished_in_network':len(filt(unfinished))}
    runtime_stop=receipt['status'] not in ('PACKET_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED','APPROVED_END_PARTIAL_OR_BODY_CENSORED_NOT_QUALIFIED')
    return {'status':'UNKNOWN_INCOMPLETE_COVERAGE' if missing else 'PASS_OBSERVED_DATA_INTEGRITY_ONLY','classification':'BOUNDED_DIAGNOSTIC_NOT_FORMAL','run_id':run,'card_sha256':sha(card_path),'manifest_sha256':sha(manifest_path),'raw_files':len(m['files']),'raw_bytes':m['bytes'],'last_ACK':last,'last_accounted':len(complete),'accounting':account,'phase_audit':phase,'feedback_audit':feedback,'independent_actual_entries':entries,'entries_without_complete_accounting':[x for x in entries if x['time_begin_s']>=len(complete)],'body_censored_ids':sorted(active),'body_first_clear_ACK':cleared,'body_rows_checked':body_rows,'terminal_results':arrivals,'missing_or_unknown':missing,'observed_alarms':alarms,'runtime_stop':runtime_stop,'runtime_status':receipt['status'],'runtime_error':receipt['error'],'first_red_checkpoint':cp,'WAIT_records':wait,'min_speed_difference':min(brakes) if brakes else None,'min_native_acceleration':min(accelerations) if accelerations else None,'counter_max':max(counter_values) if counter_values else None,'log_EOF_verified':True,'demand_groups':groups,'shared_approach_diagnostic_frames':shared,'source_snapshot':'CARD_BOUND_EXACT_BYTES_NOT_BASELINE_NATIVE','native_safety_proven':False,'rate_qualified':False,'formal_effect_proven':False,'monitored_elapsed_s':elapsed,'current_source_and_environment_hashes_checked':True,'final_client_stderr_scope':'SEPARATE_FROM_FOUR_NATIVE_STREAMS_NOT_UNIVERSAL_LOG_COVERAGE'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--card',required=True);p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();need(out.is_relative_to(ROOT/'data/processed/unified_alinea_actuator_20261013_v1'),'ONLY_NEW_PROCESSED_OUTPUT')
    need(not out.exists(),'VERSIONED_OUTPUT_EXISTS');out.mkdir(parents=True)
    try:result=audit(args.manifest,args.card)
    except Exception as exc:result={'status':'UNKNOWN_AUDIT_EXCEPTION','exception_type':type(exc).__name__,'reason':str(exc),'traceback':traceback.format_exc(),'native_safety_proven':False,'rate_qualified':False}
    with (out/'ACTUAL_RESULTS_V1.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k in ('status','run_id','last_ACK','last_accounted','runtime_status','reason')},indent=2))
    return 0 if result['status']=='PASS_OBSERVED_DATA_INTEGRITY_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
