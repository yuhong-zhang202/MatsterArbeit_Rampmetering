"""Synthetic offline audit fixtures; no native processes or observed safety claim."""
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
import copy,json,tempfile,shutil,hashlib,unittest
from scripts.t10_g5_y3_audit_20261013_v1 import core,evidence,actual
from src.candidate_a_t10_g5_y3_audit_ready_20261013 import profile,bridge


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

 def test_public_fixture_real_card_gates_and_unchanged_motion_bridge(self):
    root=profile.ROOT;old=root/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json';c=json.loads(old.read_text())
    self.assertTrue(all(profile.sha(root/p)==h for p,h in c['sources_sha256'].items()))
    oldbridge=(root/'src/candidate_a_t10_g5_y3_20261013/bridge.py').read_text();newbridge=(root/'src/candidate_a_t10_g5_y3_audit_ready_20261013/bridge.py').read_text()
    self.assertEqual(newbridge,oldbridge.replace('from src.candidate_a_t10_g5_y3_20261013.profile import','from src.candidate_a_t10_g5_y3_audit_ready_20261013.profile import').replace('from src.candidate_a_t10_g5_y3_20261013 import budget','from src.candidate_a_t10_g5_y3_audit_ready_20261013 import budget'))
    donor=json.loads((root/profile.DONOR/'card.json').read_text());paths=set(c['sources_sha256'])|set(donor['prepared_input_sha256'])|{str(profile.NETWORK),str(profile.DONOR/'card.json'),str(old.relative_to(root))}
    for folder in ('src/candidate_a_t10_g5_y3_audit_ready_20261013','scripts/candidate_a_t10_g5_y3_audit_ready_20261013_v1','scripts/t10_g5_y3_audit_20261013_v1','tests/t10_g5_y3_audit_20261013'):
        paths|={str(p.relative_to(root))for p in (root/folder).glob('*.py')}
    paths|={str(profile.USER),'scripts/unified_alinea_audit_20261013_v1/core.py','scripts/unified_alinea_audit_20261013_v1/signal_binding_v2.py','data/processed/issue12_alinea_actuation_20261012_v1/audit_data_V3.py'}
    with tempfile.TemporaryDirectory() as tmp:
        fixture_root=Path(tmp).resolve()
        for rel in paths:
            dest=fixture_root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
        p=profile.prepare(root=fixture_root);profile.validate(p,root=fixture_root,require_environment=True)
        with patch.object(bridge,'ROOT',fixture_root),patch.object(bridge,'protected_worker',side_effect=AssertionError('must not import'))as worker:
            with self.assertRaisesRegex(ValueError,'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING'):bridge.execute(p,fixture_root/profile.TASK/'releases'/profile.RUN/'EXECUTION_RELEASE.json',root=fixture_root)
            worker.assert_not_called()
        self.assertFalse((fixture_root/profile.output(profile.RUN)).parent.exists())
        foreign=fixture_root/'foreign';foreign.mkdir()
        with self.assertRaises(ValueError):profile.validate(p,root=foreign)

if __name__=='__main__':unittest.main()
