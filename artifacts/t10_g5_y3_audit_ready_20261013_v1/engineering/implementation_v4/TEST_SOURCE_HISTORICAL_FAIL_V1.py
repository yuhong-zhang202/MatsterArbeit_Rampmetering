"""Synthetic offline audit fixtures; no native processes or observed safety claim."""
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
import copy,json,tempfile,shutil,hashlib,unittest
from scripts.t10_g5_y3_audit_20261013_v1 import core,evidence,actual
from src.candidate_a_t10_g5_y3_audit_ready_20261013 import profile,bridge,telemetry


def fixture(g=4,stop=1210,entries_at=(1200,1203)):
    states='G'*g+'y'*3+'r'*(10-g-3);events=[dict(event='REQUESTED',request_id='fixed',global_request_s=1200,rate_veh_h=750,origin='FIXED',r_ALINEA=None,mapped_period_s=10,mapped_rate_veh_h=720.),dict(event='ACK_OBSERVED',request_id='fixed',application_global_s=1200,first_green_ACK_s=1201,application_delay_s=0)]
    posts=[];tls=[];acks=[];pre=[];entries=[];N=0
    for t in range(1200,stop):
        state=states[t-1200];ph={'G':0,'y':1,'r':2}[state];ge=1200+g
        switch=1205 if state=='G' else ge+3 if state=='y' else ge+5 if t==ge+3 else 1210
        prior=states[t-1201] if t>1200 and t in (ge,ge+3) else state
        bs=t if prior!=state else switch
        ids=[]
        if t in entries_at:
            x=dict(vehicle_id=f'R_flow.{N}',time_begin_s=t,time_end_s=t+1,motion=state);entries.append(x);ids=[dict(vehicle_id=x['vehicle_id'])];N+=1
        n=t-1199;E=2 if t+1==1210 else 0
        accounting=dict(C=float(Fraction(750*n,3600)),C_mapped_pending=n/5,C_applied=n/5,E=E,N=N,policy_quantization=float(Fraction(n,120)),application_latency=0.,C_applied_minus_E=n/5-E,E_minus_N=E-N)
        rc=dict(pending_request_id='fixed',input_origin='FIXED',r_final_veh_h=750,r_policy_pending_veh_h=720.,applied_request_id='fixed',period_s=10,requested_quota=2,r_policy_applied_veh_h=720.,cycle_application_delay_s=None if t==1200 else 0)
        po=dict(phase_before={'G':0,'y':1,'r':2}[prior],state_before=prior,next_switch_before_s=bs,phase_after=ph,state_after=state,next_switch_after_s=switch)
        posts.append(dict(time_begin_s=t,time_end_s=t+1,accounting_complete=True,motion=state,rate_chain=rc,actual_crossings=ids,accounting=accounting,phase_observation=po))
        tls.append(dict(time=str(t),id='ramp_mid',programID='T10_G5Y3_NATIVE',phase=str(ph),state=state))
        acks.extend([dict(requested_target_s=t+1,ACK_received=True,actual_time_verified=False,actual_readback_s=None),dict(requested_target_s=t+1,ACK_received=True,actual_time_verified=True,actual_readback_s=t+1)])
        pre.append(dict(bound_snapshot=dict(phase_before=po['phase_before'],state_before=prior,next_switch_before_s=bs,program='T10_G5Y3_NATIVE')))
    calls=[];dur=[];ge=1200+g
    if g<5 and stop>=ge:
        calls.append(dict(requests=[dict(method='setPhase',value=1,time_s=ge,call_completed=True)],actual_readback=dict(time_s=ge,phase=1,state='y',nextSwitch_s=ge+3)))
    at=ge+4
    if stop>=at:
        rb=dict(time_s=at,program='T10_G5Y3_NATIVE',phase=2,state='r',nextSwitch_s=1210)
        q=dict(method='setPhaseDuration',value=1210-at,time_s=at,call_completed=True,actual_readback=rb)
        dur=[dict(time_s=at,method='setPhaseDuration',value=1210-at,call_completed=False,status='ATTEMPTED',cycle_end_s=1210),dict(q,status='READBACK_VERIFIED',cycle_end_s=1210)]
        calls.append(dict(requests=[q],actual_readback=dict(state='r',nextSwitch_s=1210)))
    return dict(classification='SYNTHETIC_NOT_OBSERVED',posts=posts,events=events,entries=entries,tls=tls,acks=acks,pre=pre,calls=calls,durations=dur)

class AuditTests(unittest.TestCase):
 def phase(self,f):
    a=core.audit_accounting(f['posts'],f['events'],f['entries'],1270)
    return a,core.audit_phases(f['tls'],f['posts'],f['acks'],a['cycles'],f['calls'],f['durations'],f['pre'])
 def test_two_closing_paths_partial_null_and_phase_negative_controls(self):
    for g,entries in [(4,(1200,1203)),(5,(1200,))]:
        f=fixture(g,entries_at=entries);a,p=self.phase(f)
        self.assertEqual(p['cycles'][0]['observed_motion_sequence'],'G'*g+'yyy'+'r'*(7-g))
        self.assertEqual((a['accounting']['E'],a['accounting']['N']),(2,len(entries)))
        first=next(x for x in f['posts'] if x['motion']=='r')
        cp=dict(time_s=first['time_end_s'],first_controlled_red_begin_s=first['time_begin_s'],accounting=first['accounting'],log_scope='PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED')
        evidence.checkpoint(cp,[first])
        for field,val in [('time_s',1207),('first_controlled_red_begin_s',1206),('log_scope','FINAL_EOF')]:
            bad=dict(cp,**{field:val})
            with self.assertRaises(ValueError):evidence.checkpoint(bad,[first])
        for kind in ('tls','ack','program','clock','transition','duration','missing'):
            bad=copy.deepcopy(f)
            if kind=='tls':bad['tls'][0]['time']='1201'
            if kind=='ack':bad['acks'][1]['actual_readback_s']=1202
            if kind=='program':bad['tls'][0]['programID']='I12_PACKET10'
            if kind=='clock':bad['posts'][0]['phase_observation']['next_switch_after_s']=1204
            if kind=='transition':bad['posts'][g]['motion']='r'
            if kind=='duration':bad['durations']=bad['durations'][:1]
            if kind=='missing':bad['pre'][0]['bound_snapshot']['phase_before']=True
            with self.subTest(g=g,kind=kind),self.assertRaises(ValueError):self.phase(bad)
    f=fixture(5,1202,());a,p=self.phase(f);self.assertEqual((a['accounting']['E'],a['accounting']['N']),(0,0));self.assertFalse(a['cycles'][0]['completed'])
    self.assertTrue(all(x is None for x in core.audit_accounting([],f['events'],[],1270)['accounting'].values()))
    f=fixture(5,entries_at=(1200,1205,1206));a,p=self.phase(f);self.assertEqual((a['accounting']['E'],a['accounting']['N']),(2,3));self.assertEqual(a['cycles'][0]['N_y'],2)
    bad=copy.deepcopy(f);bad['posts'][0]['accounting']['N']=2
    with self.assertRaises(ValueError):self.phase(bad)

 def test_body_full_population_clearance_and_missing_record_rejected(self):
    active=set();binding={};cleared={};before={v:{'lane_id':'ramp_storage_0'} for v in ('R_flow.0','R_flow.1')};meta={v:{'length_m':5} for v in before}
    def record(i,positions,state,entry=True):
        frame={v:dict(lane=':ramp_mid_0_0',pos=str(pos),speed='2')for v,pos in positions.items()};rows=[]
        for v,pos in positions.items():
            rows.append(dict(vehicle_id=v,entry_time_begin_s=1200,entry_time_end_s=1201,entry_signal='G',observed_ACK_s=i+1,observed_signal=state,head_position_m=pos,length_m=5,speed_m_s=2.,rear_position_m=pos-5,status='REAR_SPANS_LINE' if pos<=5 else 'REAR_CLEAR_OBSERVED',first_actual_rear_clear_ACK_s=None if pos<=5 else i+1))
        row=dict(actual_crossings=[dict(vehicle_id=v)for v in positions]if entry else [],body_observation=dict(ACK_s=i+1,signal=state,rows=rows,spanning_ids=[v for v,pos in positions.items()if pos<=5]))
        return row,frame
    row,frame=record(1200,{'R_flow.0':1.,'R_flow.1':2.},'G');xs,n=evidence.body_frame(1200,row,before,frame,'G',meta,active,binding,cleared);self.assertEqual(n,2)
    row,frame=record(1201,{'R_flow.0':6.,'R_flow.1':7.},'r',False);internal={v:{'lane_id':':ramp_mid_0_0'} for v in before}
    evidence.body_frame(1201,row,internal,frame,'r',meta,active,binding,cleared);self.assertFalse(active) # Red rear clearance is legal; not a new front entry.
    for fault in ('missing','population','clock'):
        a=set(before);b={v:dict(vehicle_id=v,time_begin_s=1200,time_end_s=1201,motion='G')for v in before};bad=copy.deepcopy(row)
        if fault=='missing':bad.pop('body_observation')
        if fault=='population':bad['body_observation']['rows'].pop()
        if fault=='clock':bad['body_observation']['ACK_s']=1201
        with self.subTest(fault=fault),self.assertRaises(ValueError):evidence.body_frame(1201,bad,internal,frame,'r',meta,a,b,{})

 def test_EOF_strict_NUM_serialized_population_and_terminal_UNKNOWN(self):
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);d=hashlib.sha256(b'').hexdigest()
        for n in evidence.STREAMS:(root/n).write_bytes(b'')
        q=dict(stage='AFTER_NATIVE_CLOSE_PROCESS_EOF',streams={n:dict(byte_start=0,byte_end=0,prefix_sha256=d,fragment_sha256=d)for n in evidence.STREAMS});receipt=dict(final_logs=dict(coverage='FINAL_FILES_AT_OWNED_PROCESS_EOF'))
        self.assertTrue(evidence.log_eof([q],root,receipt))
        for kind in ('missing','partial','hash'):
            bad=copy.deepcopy(q)
            if kind=='missing':bad['streams'].pop('sumo.log')
            if kind=='partial':bad['stage']='PROVISIONAL_CAPTURE'
            if kind=='hash':bad['streams']['sumo.log']['prefix_sha256']='bad'
            with self.assertRaises(ValueError):evidence.log_eof([bad],root,receipt)
    evidence.strict_numeric(dict(numeric_stop_classifications=[]))
    for q in ({},{'numeric_stop_classifications':[{'decision':'CONTINUE_RESTRICTED_NUMERICAL_EVENT'}]}):
        with self.assertRaises(ValueError):evidence.strict_numeric(q)
    meta=dict(vehicle_id='R_flow.0',time_s=1200,speed_m_s=2.,lane_id='ramp_storage_0',type_id='technical_passenger',route=evidence.ROUTES['R'],terminal_edge='main_down',normal_decel_m_s2=4.5,length_m=5.,position_m=200.,acceleration_m_s2=0.)
    snap=dict(world={'R_flow.0':dict(role='R',speed_m_s=2.,lane_id='ramp_storage_0')},terminal_before={'R_flow.0':meta});evidence.serialized_population(snap,1200)
    for key,val in [('normal_decel_m_s2',9.),('route',[]),('time_s',1201)]:
        bad=copy.deepcopy(snap);bad['terminal_before']['R_flow.0'][key]=val
        with self.assertRaises(ValueError):evidence.serialized_population(bad,1200)
    before=dict(meta,time_begin_s=1200,time_end_s=1201,arrived_id_bound=True,terminal_edge='main_down');trip=dict(id='R_flow.0',vType='technical_passenger',arrivalLane='main_down_0',arrivalSpeed='2.00000000',arrival='1200.00000000')
    self.assertEqual(actual.terminal.audit_terminal(before,[trip],{'main_down':['main_down_0']})['status'],'PASS')
    self.assertEqual(actual.terminal.audit_terminal(before,[],{'main_down':['main_down_0']})['status'],'UNKNOWN')

 def test_Y3_actual_population_binding_and_unknown_never_skipped(self):
    world={'R_flow.0':dict(speed_m_s=4.,lane_id='ramp_storage_0')}
    meta={'R_flow.0':dict(position_m=204.39,length_m=5.,normal_decel_m_s2=4.5)}
    row=dict(vehicle_id='R_flow.0',time_s=1204,population='storage',speed_m_s=4.,position_m=204.39,length_m=5.,normal_decel_m_s2=4.5,action_step_s=1.,native_future_safety_proven=False,one_step_Euler_stop_possible=True,distance_to_meter_m=.1,stop_possible=True,clear_possible=True)
    yy=dict(time_s=1204,source_post_frame_time_s=1204,yellow_s=3,status='PASS',covered_ids=['R_flow.0'],rows=[row]);cycles=[dict(begin_s=1200,yellow_s=3)]
    self.assertTrue(evidence.yellow_record(yy,cycles,world,meta,1210))
    for field,val in [('source_post_frame_time_s',1205),('yellow_s',4),('status','UNKNOWN'),('covered_ids',[]),('rows',[])]:
        with self.subTest(field=field),self.assertRaises(ValueError):evidence.yellow_record(dict(yy,**{field:val}),cycles,world,meta,1210)
    with self.assertRaises(ValueError):evidence.yellow_record(yy,cycles,world,None,1210)
    bad=copy.deepcopy(yy);bad['rows'][0].update(speed_m_s=16.,position_m=203.49,distance_to_meter_m=1.,one_step_Euler_stop_possible=False,stop_possible=False,clear_possible=False)
    with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):
        evidence.yellow_record(bad,cycles,{'R_flow.0':dict(speed_m_s=16.,lane_id='ramp_storage_0')},{'R_flow.0':dict(position_m=203.49,length_m=5.,normal_decel_m_s2=4.5)},1210)

 def test_fresh_full_identity_journal_inherited_fake_and_unknown_population(self):
    from tests.candidate_a_t10_g5_y3_20261013.test_candidate import World
    from src.candidate_a_t10_g5_y3_20261013 import profile as original
    with tempfile.TemporaryDirectory() as tmp:
        pkg=Path(tmp)/'pkg';original.stage_package(original.ROOT,pkg,Path(tmp)/'out',1210)
        w=World(pkg/'scenario.add.xml');w.time=1200
        q=telemetry.snapshot(w,1200,'BEFORE_MOTION');world={v:dict()for v in q['active_ids']}
        self.assertTrue(evidence.identity_journal(q,1200,'BEFORE_MOTION',world))
        w.simulationStep(1201);q1=telemetry.snapshot(w,1201,'AFTER_ACK');self.assertTrue(evidence.identity_journal(q1,1201,'AFTER_ACK',{v:{}for v in q1['active_ids']}))
        for fault in ('time','stage','mode','dynamic','population','missing'):
            bad=copy.deepcopy(q1);vid=next(iter(bad['vehicle_states']))
            if fault=='time':bad['time_s']=1200
            if fault=='stage':bad['stage']='BEFORE_MOTION'
            if fault=='mode':bad['vehicle_states'][vid]['speed_mode']=True
            if fault=='dynamic':bad['vehicle_states'][vid]['tau_s']=2.
            if fault=='population':bad['pending_ids'].append('R_flow.999')
            if fault=='missing':bad['vehicle_states'].pop(vid)
            with self.subTest(fault=fault),self.assertRaises(ValueError):evidence.identity_journal(bad,1201,'AFTER_ACK',{v:{}for v in q1['active_ids']})
        with self.assertRaises(ValueError):telemetry.snapshot(w,1200,'BEFORE_MOTION')

 def test_yellow_journal_complete_set_and_real_bridge_two_paths(self):
    from tests.candidate_a_t10_g5_y3_20261013.test_candidate import World
    from src.candidate_a_t10_g5_y3_20261013.adapter import StepAdapter
    from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
    from types import SimpleNamespace
    import time
    import tests.candidate_a_t10_g5_y3_20261013.test_candidate as inherited
    for early in (True,False):
        with self.subTest(early=early),tempfile.TemporaryDirectory()as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1210);out.mkdir()
            w=World(pkg/'scenario.add.xml',early)
            if not early:
                original_step=w.simulationStep
                def without_second_entry(end):
                    original_step(end)
                    if end==1205:w.enter.pop('R_flow.1',None)
                w.simulationStep=without_second_entry
            a=StepAdapter(w.observe,750,1210);cap=LogCapture(out);worker=bridge.protected_worker()
            try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=300000000),inherited.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a)
            finally:cap.close_handles()
            self.assertEqual(a.ledger.rows[0]['green_end_reason'],'ACTUAL_QUOTA_ACK'if early else'MAX_GREEN_DEADLINE')
            yy=actual.lines(out/'yellow_scope.jsonl');self.assertEqual([q['time_s']for q in yy],[1204 if early else 1205])
            f=fixture(4 if early else 5,entries_at=(1200,1203)if early else(1200,));account,phase=self.phase(f)
            post=actual.flatten(actual.lines(out/'post_steps.jsonl'));pre=actual.lines(out/'pre_steps.jsonl')
            self.assertEqual(evidence.yellow_coverage(yy,phase,account['cycles'],post,pre,1210,False)['observed_first_Y_count'],1)
            for bad in ([],yy+yy,[dict(yy[0],time_s=1203)],[dict(yy[0],time_s=1209)]):
                with self.assertRaises(ValueError):evidence.yellow_coverage(bad,phase,account['cycles'],post,pre,1210,False)
            # A successful prepare immediately before an aborted first-Y motion
            # is not an observed Y interval and must not be invented as one.
            t=yy[0]['time_s'];partial=fixture(4 if early else 5,t,entries_at=(1200,1203)if early else(1200,));pa,pp=self.phase(partial)
            q=evidence.yellow_coverage(yy,pp,pa['cycles'],post[:t],pre[:t+1],t,True)
            self.assertEqual(q['observed_first_Y_count'],0);self.assertEqual(q['prepared_not_observed_times'],[t])
            self.assertEqual(evidence.yellow_coverage([],pp,pa['cycles'],post[:t],pre[:t],t,True)['observed_first_Y_count'],0)
            with self.assertRaises(ValueError):evidence.yellow_coverage(yy,pp,pa['cycles'],post[:t],pre[:t+1],t,False)

 def test_extra_PRE_identity_prefix_valid_and_unknown_cases(self):
    x=dict(time_s=0,stage='BEFORE_MOTION',setter_calls=0,active_ids=[],loaded_ids=[],pending_ids=[],vehicle_states={})
    y=dict(x,time_s=1,stage='AFTER_ACK');z=dict(x,time_s=1)
    pre=[dict(time_s=0,bound_snapshot=dict(world={})),dict(time_s=1,bound_snapshot=dict(world={}))];post=[dict(post_world={})]
    self.assertTrue(evidence.identity_prefix([x,y,z],pre,post,1)['prepared_not_observed_last_PRE'])
    self.assertFalse(evidence.identity_prefix([x,y],pre[:1],post,1)['prepared_not_observed_last_PRE'])
    for journal,p in [([x,y],pre),([x,y,z,z],pre),([x,y,z],pre[:1]),([x,y,dict(z,time_s=0)],pre),([x,y,dict(z,active_ids=['R_flow.1'])],pre),([x,y,z],[pre[0],dict(pre[1],time_s=0)])]:
        with self.assertRaises(ValueError):evidence.identity_prefix(journal,p,post,1)
    import ast
    tree=ast.parse((profile.ROOT/'scripts/t10_g5_y3_audit_20261013_v1/actual.py').read_text())
    self.assertTrue(any(isinstance(q,ast.Call) and isinstance(q.func,ast.Name) and q.func.id=='identity_prefix' for q in ast.walk(tree)))
    self.assertTrue(any(isinstance(q,ast.Call) and isinstance(q.func,ast.Name) and q.func.id=='yellow_coverage' for q in ast.walk(tree)))

 def test_nonactive_pool_independent_binding_and_terminal_scope(self):
    def journal(t,stage):
        ids=['R_flow.0','R_flow.9','R_flow.10']
        rows={v:dict(vehicle_id=v,time_s=t,type_id='technical_passenger',route=evidence.ROUTES['R'],speed_mode=31,lane_change_mode=1621,**evidence.EXPECTED_DYNAMICS)for v in ids}
        return dict(time_s=t,stage=stage,setter_calls=0,active_ids=['R_flow.0'],loaded_ids=['R_flow.0','R_flow.9'],pending_ids=['R_flow.10'],vehicle_states=rows)
    world={'R_flow.0':{}}
    pre=[dict(time_s=t,bound_snapshot=dict(time_s=t,world=world,loaded=['R_flow.0','R_flow.9'],pending_ids=['R_flow.10']))for t in (0,1)]
    post=[dict(post_world=world)];j=[journal(0,'BEFORE_MOTION'),journal(1,'AFTER_ACK'),journal(1,'BEFORE_MOTION')]
    # Execute the historical omission counterexample against the new contract.
    bad=copy.deepcopy(j);bad[0]['loaded_ids'].remove('R_flow.9');bad[0]['vehicle_states'].pop('R_flow.9')
    with self.assertRaisesRegex(ValueError,'INDEPENDENT_IDENTITY_POOL'):evidence.identity_prefix(bad,pre,post,1)
    q=evidence.identity_prefix(j,pre,post,1);self.assertEqual(q['after_pool_sources'],['NEXT_SAME_TIME_PRE_INDEPENDENT_POOL_CHECK'])
    terminal=evidence.identity_prefix(j[:2],pre[:1],post,1);self.assertEqual(terminal['after_pool_sources'],['SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK'])
    for which,fault in [(0,'pending_omit'),(2,'loaded_omit'),(1,'wrong_pool'),(0,'duplicate'),(0,'missing_field'),(2,'source_duplicate')]:
        bad=copy.deepcopy(j);bp=copy.deepcopy(pre)
        if fault=='pending_omit':bad[which]['pending_ids']=[];bad[which]['vehicle_states'].pop('R_flow.10')
        if fault=='loaded_omit':bad[which]['loaded_ids'].remove('R_flow.9');bad[which]['vehicle_states'].pop('R_flow.9')
        if fault=='wrong_pool':bad[which]['loaded_ids']=['R_flow.0','R_flow.10'];bad[which]['pending_ids']=['R_flow.9']
        if fault=='duplicate':bad[which]['pending_ids'].append('R_flow.10')
        if fault=='missing_field':bp[0]['bound_snapshot'].pop('loaded')
        if fault=='source_duplicate':bp[1]['bound_snapshot']['pending_ids'].append('R_flow.10')
        with self.subTest(which=which,fault=fault),self.assertRaises(ValueError):evidence.identity_prefix(bad,bp,post,1)

 def test_public_fixture_real_card_gates_and_unchanged_motion_bridge(self):
    root=profile.ROOT;old=root/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json';c=json.loads(old.read_text())
    self.assertTrue(all(profile.sha(root/p)==h for p,h in c['sources_sha256'].items()))
    oldbridge=(root/'src/candidate_a_t10_g5_y3_20261013/bridge.py').read_text();newbridge=(root/'src/candidate_a_t10_g5_y3_audit_ready_20261013/bridge.py').read_text()
    expected=oldbridge.replace('from src.candidate_a_t10_g5_y3_20261013.profile import','from src.candidate_a_t10_g5_y3_audit_ready_20261013.profile import').replace('from src.candidate_a_t10_g5_y3_20261013 import budget','from src.candidate_a_t10_g5_y3_audit_ready_20261013 import budget\nfrom src.candidate_a_t10_g5_y3_audit_ready_20261013.telemetry import snapshot as identity_snapshot')
    expected=expected.replace("        append_new(output/'pre_steps.jsonl'","        append_new(output/'identity_journal.jsonl',identity_snapshot(conn,t,'BEFORE_MOTION'))\n        append_new(output/'pre_steps.jsonl'",1).replace("        after=capture.snapshot(t,t+1,'AFTER_SIMULATION_STEP_ACK')","        append_new(output/'identity_journal.jsonl',identity_snapshot(conn,t+1,'AFTER_ACK'))\n        after=capture.snapshot(t,t+1,'AFTER_SIMULATION_STEP_ACK')",1)
    expected=expected.replace("append_new(output/'yellow_scope.jsonl',scope)","append_new(output/'yellow_scope_attempts.jsonl',dict(scope,attempt_stage='QUOTA_CLOSE_SCREEN_BEFORE_SETTER',observed_first_Y=False))",1)
    newbridge=newbridge[:newbridge.index('\ndef write_first_yellow_screen(')]+newbridge[newbridge.index('\ndef _diagnostic_loop('):]
    newbridge=newbridge.replace("        try:before=adapter.prepare_step(conn,t)\n        except Exception:\n            q=adapter.last_yellow_scope\n            if isinstance(q,dict) and q.get('time_s')==t:\n                append_new(output/'yellow_scope_attempts.jsonl',dict(q,attempt_stage='PREPARE_REJECTED_BEFORE_FIRST_Y_MOTION',observed_first_Y=False))\n            raise\n        write_first_yellow_screen(adapter,t,output)","        before=adapter.prepare_step(conn,t)",1)
    self.assertEqual(newbridge,expected)
    donor=json.loads((root/profile.DONOR/'card.json').read_text());paths=set(c['sources_sha256'])|set(donor['prepared_input_sha256'])|{str(profile.NETWORK),str(profile.DONOR/'card.json'),str(old.relative_to(root))}
    for folder in ('src/candidate_a_t10_g5_y3_audit_ready_20261013','scripts/candidate_a_t10_g5_y3_audit_ready_20261013_v1','scripts/t10_g5_y3_audit_20261013_v1','tests/t10_g5_y3_audit_20261013'):
        paths|={str(p.relative_to(root))for p in (root/folder).glob('*.py')}
    paths|={str(profile.USER),'scripts/unified_alinea_audit_20261013_v1/core.py','scripts/unified_alinea_audit_20261013_v1/signal_binding_v2.py','data/processed/issue12_alinea_actuation_20261012_v1/audit_data_V3.py'}
    with tempfile.TemporaryDirectory() as tmp:
        fixture_root=(Path(tmp)/'fixture').resolve()
        for rel in paths:
            dest=fixture_root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
        p=profile.prepare(root=fixture_root);profile.validate(p,root=fixture_root,require_environment=True)
        with patch.object(bridge,'ROOT',fixture_root),patch.object(bridge,'protected_worker',side_effect=AssertionError('must not import'))as worker:
            with self.assertRaisesRegex(ValueError,'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING'):bridge.execute(p,fixture_root/profile.TASK/'releases'/profile.RUN/'EXECUTION_RELEASE.json',root=fixture_root)
            worker.assert_not_called()
        self.assertFalse((fixture_root/profile.output(profile.RUN)).parent.exists())
        foreign=(Path(tmp)/'foreign').resolve();shutil.copytree(fixture_root,foreign)
        with self.assertRaisesRegex(ValueError,'FOREIGN_RUNTIME_INPUT'):profile.validate(foreign/profile.TASK/'packages_v3'/profile.RUN/'card.json',root=foreign)

if __name__=='__main__':unittest.main()
