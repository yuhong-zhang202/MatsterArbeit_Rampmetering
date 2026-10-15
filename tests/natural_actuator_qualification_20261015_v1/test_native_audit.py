"""Tiny native evidence joins and preserved saved arithmetic; no simulator."""
from copy import deepcopy
from fractions import Fraction
import gzip,json,tempfile,unittest
from pathlib import Path
from scripts.natural_actuator_qualification_20261015_v1 import actual,measurements,phases,streaming,provenance,yellow
from scripts.natural_service_audit_20261015_v1.actual import read_bundle,audit as math_audit
from scripts.cumulative_full_catalogue_audit_20261014_v1.evidence import body_frame
from scripts.unified_alinea_audit_20261013_v1.signal_binding_v2 import validate as signal_validate

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles'

class NativeAuditTests(unittest.TestCase):
    def test_five_saved_math_and_window_support(self):
        for name in ('empty_none_641','supply_none_641','late_none_641','blocked_none_641','blocked_none_640'):
            d=read_bundle(BASE/name);r=dict(d['receipt'],control_accounting=d['receipt']['accounting'])
            with self.subTest(name=name):self.assertEqual(math_audit(actual.accounting_view(r,d['files']))['C'],'10' if name.endswith('640') else '41/4')
        rows=[]
        for t in range(1500):
            C=Fraction(max(0,t+1-600),4)
            rows.append(dict(time_begin_s=t,accounting_complete=True,accounting=dict(C=float(C),C_exact_fraction=str(C),N=0,E_scheduled_nominal=0,E_executed_nominal=0,C_selected_exact_fraction=str(C),C_applied_exact_fraction=str(C))))
        w=measurements.windows(rows,1500);self.assertEqual(w[0]['C_exact_fraction'],'75');self.assertEqual(w[0]['N'],0)
        self.assertTrue(all(q['status']=='NOT_TESTED_WINDOW_NOT_REACHED' for q in w[1:]));self.assertEqual(measurements.windows(rows[:1350],1350)[0]['status'],'UNKNOWN_INCOMPLETE_WINDOW')

    def test_requested_cohort_future_and_missing_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'routes.xml';items=['<routes>']
            for c,n in dict(M=3000,R=600,U=300,X=150).items():
                for i in range(n):items.append(f'<vehicle id="{c}_flow.{i}" depart="{0 if c=="M" and i==0 else 10000}"/>')
            items.append('</routes>');p.write_text(''.join(items))
            trips=[dict(id='M_flow.0',depart='0',arrival='1',departDelay='0')];fcd={'M_flow.0':dict(first=0,last=0)}
            summary=[dict(time='0',inserted='1',arrived='0',running='1'),dict(time='1',inserted='1',arrived='1',running='0')]
            r=measurements.cohort(p,trips,fcd,2,summary,{})
            self.assertEqual(r['totals'],dict(source_wait_s=0.,in_network_s=1.,system_s=1.));self.assertEqual(sum(x['status']=='FUTURE_SCHEDULED' for x in r['rows']),4049)
            missing=measurements.cohort(p,[],{},2,[dict(time=str(t),inserted='0',arrived='0',running='0') for t in range(2)],{})
            self.assertEqual(missing['status'],'UNKNOWN_MISSING_DUE_TRIP');self.assertIsNone(missing['rows'][0]['system_s'])
            with self.assertRaises(ValueError):measurements.cohort(p,trips+trips,fcd,2,summary,{})

    def test_fcd_entry_body_and_bad_joins(self):
        vid='R_flow.0';active=set();binding={};cleared={}
        row=dict(actual_crossings=[dict(vehicle_id=vid)],body_observation=dict(ACK_s=1,signal='G',spanning_ids=[vid],rows=[dict(vehicle_id=vid,entry_time_begin_s=0,entry_time_end_s=1,entry_signal='G',observed_ACK_s=1,observed_signal='G',head_position_m=.5,length_m=5,speed_m_s=2,rear_position_m=-4.5,status='REAR_SPANS_LINE')]))
        before={vid:dict(lane_id='ramp_storage_0')};frame={vid:dict(lane=':ramp_mid_0_0',pos='.50000000',speed='2.00000000')};meta={vid:dict(length_m=5)}
        entries,n=body_frame(0,row,before,frame,'G',meta,active,binding,cleared);self.assertEqual(len(entries),1);self.assertEqual(n,1)
        bad=deepcopy(row);bad['actual_crossings']=[]
        with self.assertRaises(ValueError):body_frame(0,bad,before,frame,'G',meta,set(),{},{} )
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fcd.xml.gz'
            with gzip.open(p,'wt') as f:f.write('<fcd-export><timestep time="0"><vehicle id="x"/><vehicle id="x"/></timestep></fcd-export>')
            with self.assertRaises(ValueError):list(streaming.fcd_frames(p))
        b=dict(ACK_s=1,actual_phase=0,actual_state='G',actual_program='P',expected_phase=0,expected_state='G',expected_program='P',actual_controlled_links=[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]],status='BOUND_BEFORE_LEDGER')
        signal_validate(dict(post_signal_application_binding=b),dict(phase=0,state='G',program='P',ACK_s=1))
        b['actual_program']='WRONG'
        with self.assertRaises(ValueError):signal_validate(dict(post_signal_application_binding=b),dict(phase=0,state='G',program='P',ACK_s=1))

    def test_terminal_red_no_future_setter_and_earlier_missing_rejected(self):
        def example(last):
            c=dict(begin_s=600,end_s=608,period_s=8,signal_program='I12_PACKET8',executed=True,green_end_s=604,completed=last==608,N_G=0,green_end_reason='MAX_GREEN_DEADLINE')
            pre=[{} for _ in range(last)];post=[dict(time_begin_s=t,time_end_s=t+1,motion='G') for t in range(last)];tls={}
            for t in range(600,last):
                state='G' if t<604 else 'y' if t<606 else 'r';switch=604 if state=='G' else 606 if state=='y' else 608
                pre[t]=dict(bound_snapshot=dict(program='I12_PACKET8',motion=state));post[t]=dict(time_begin_s=t,time_end_s=t+1,motion=state,phase_observation=dict(next_switch_after_s=switch))
                tls[t]=dict(programID='I12_PACKET8',state=state,phase=str({'G':0,'y':1,'r':2}[state]))
            return pre,post,[c],tls
        self.assertEqual(phases.audit(*example(607),[],607)['status'],'PASS_CONTINUOUS_NATIVE_PHASES')
        with self.assertRaisesRegex(ValueError,'EARLIER_RED_SETTER'):phases.audit(*example(608),[],608)
        durations=[dict(time_s=607,status='ATTEMPTED',value=1,cycle_end_s=608),dict(time_s=607,status='READBACK_VERIFIED',value=1,cycle_end_s=608,call_completed=True,actual_readback=dict(time_s=607,program='I12_PACKET8',phase=2,state='r',nextSwitch_s=608))]
        phases.audit(*example(608),durations,608)

    def test_stream_two_saved_frames_and_missing_ACK(self):
        source=read_bundle(BASE/'empty_none_641')
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)
            def write(name,rows):
                (raw/name).write_text(''.join(json.dumps(r)+'\n' for r in rows))
            write('pre_steps.jsonl',source['files']['pre_steps.jsonl'][:2])
            write('post_steps.jsonl',source['files']['post_steps.jsonl'][:2])
            write('step_ack.jsonl',source['files']['step_ack.jsonl'][:4])
            write('identity_journal.jsonl',source['files']['identity_journal.jsonl'][:4])
            (raw/'tls_states.xml').write_text('<tlsStates>'+''.join(f'<tlsState time="{t}" id="{name}" state="G" phase="0" programID="A_OPEN"/>' for t in range(2) for name in ('ramp_mid','urban_tls'))+'</tlsStates>')
            with gzip.open(raw/'fcd.xml.gz','wt') as f:
                f.write('<fcd-export>'+''.join(f'<timestep time="{t}"><vehicle id="M_flow.0" lane="main_up_0" speed="5.00000000" pos="0"/></timestep>' for t in range(2))+'</fcd-export>')
            network=raw/'network.xml';network.write_text('<net><edge id="main_down"><lane id="main_down_0"/></edge></net>')
            receipt=dict(last_completed_s=2,body_censored_ids=[])
            result=streaming.scan(raw,receipt,network,[])
            self.assertEqual(len(result['post']),2);self.assertEqual(result['observed']['M_flow.0'],dict(first=0,last=1))
            self.assertEqual(result['populations']['after_vehicle_steps'],2)
            write('step_ack.jsonl',source['files']['step_ack.jsonl'][:3])
            with self.assertRaisesRegex(ValueError,'TWO_STAGE_ACK'):streaming.scan(raw,receipt,network,[])

    def test_nonempty_E1_XML_and_last_arrival(self):
        from scripts.natural_actuator_qualification_20261015_v1.streaming import audit_terminal
        from scripts.natural_service_audit_20261015_v1.actual import feedback_check
        detectors=('p1_main_down_20_l0','p1_main_down_20_l1')
        seed=dict(event='E1_ACTIVATION_SEED',global_s=600,logical_s=600,window_begin_global_s=600,
                  ongoing_events={d:[[f'unit.{i}',5,599,-1,'technical_passenger']] for i,d in enumerate(detectors)})
        events=[seed]
        for t in range(601,632):
            raw={d:[] for d in detectors}
            for i,d in enumerate(detectors):
                if t==603+3*i:raw[d]=[[f'unit.{i}',5,599,t,'technical_passenger']]
            events.append(dict(event='E1_POST_ACK_EVENTS',global_s=t,logical_s=t,raw_events=raw))
        events.append(dict(event='PROJECT_FEEDBACK_DECISION',global_s=630,logical_s=630,update_time_s=630,
            global_window_begin_s=600,global_window_end_s=630,interval_begin_s=600,interval_end_s=630,
            request_id='feedback:630',occ_l0_pct=10.,occ_l1_pct=20.,rate_previous_veh_h=900,rate_raw_veh_h=620.,rate_clipped_veh_h=620.))
        rebuilt=feedback_check(events,631,[dict(request_id='feedback:630',global_request_s=630,rate_veh_h=620)])
        self.assertEqual(rebuilt[0]['rate_veh_h'],620.)
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp);event=dict(event='PROJECT_FEEDBACK_DECISION',global_window_begin_s=600,global_window_end_s=630,occ_l0_pct=10.,occ_l1_pct=20.)
            for i in range(2):(raw/f'p1_main_down_20_l{i}.xml').write_text(f'<detector><interval id="p1_main_down_20_l{i}" begin="600" end="630" occupancy="{10+10*i}.00000000"/></detector>')
            self.assertEqual(measurements.feedback_xml(raw,[event],631)['lane_windows_checked'],2)
            event['occ_l1_pct']=21.
            with self.assertRaisesRegex(ValueError,'OCCUPANCY'):measurements.feedback_xml(raw,[event],631)
        before=dict(vehicle_id='M_flow.0',time_begin_s=1,time_end_s=2,time_s=1,arrived_id_bound=True,type_id='technical_passenger',route=['main_up','merge_section','main_down'],terminal_edge='main_down',speed_m_s=5.,acceleration_m_s2=0.,normal_decel_m_s2=4.5)
        trip=dict(id='M_flow.0',vType='technical_passenger',arrivalLane='main_down_0',arrivalSpeed='5.00000000',arrival='1.00000000')
        self.assertEqual(audit_terminal(before,[trip],{'main_down':['main_down_0']})['status'],'PASS')
        self.assertEqual(audit_terminal(before,[],{'main_down':['main_down_0']})['status'],'UNKNOWN')

    def test_named_lane_queue_rear_and_export(self):
        lengths={'ramp_storage_0':204.49,':urban_diverge_1_0':113.08,'shared_approach_0':238.8}
        frame={'R_flow.0':dict(lane='ramp_storage_0',pos='200',speed='0.0')}
        q=measurements.queue_extent(frame,{'R_flow.0':dict(length_m=5)},lengths,600)
        self.assertAlmostEqual(q['ramp_slow_R_rear_extent_m'],9.49);self.assertEqual(q['shared_slow_R_rear_extent_m'],0)
        self.assertEqual(measurements.queue_extent(frame,{},lengths,600)['status'],'UNKNOWN_MISSING_QUEUE_LENGTH')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'queues.xml';p.write_text('<queue-export><data timestep="0"><lanes><lane id="ramp_storage_0" queueing_length="0"/></lanes></data></queue-export>')
            self.assertEqual(measurements.queue_xml(p,1)['status'],'PASS_NATIVE_QUEUE_EXPORT_COVERAGE')
            with self.assertRaises(ValueError):measurements.queue_xml(p,2)

    def test_owned_EOF_not_worker_exit_alone(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp);names=('sumo_stdout.log','sumo_stderr.log','sumo_error.log','sumo.log');empty=hashlib.sha256(b'').hexdigest()
            for name in names:(raw/name).write_bytes(b'')
            logs=[dict(stage='AFTER_NATIVE_CLOSE_PROCESS_EOF',streams={n:dict(byte_start=0,byte_end=0,prefix_sha256=empty,fragment_sha256=empty) for n in names})]
            r=dict(run_id='UNIT',final_logs=dict(coverage='FINAL_FILES_AT_OWNED_PROCESS_EOF',process_returncode=0,all_streams_bound=True))
            worker=dict(pid=101,pgid=101,sid=101,status='OBSERVED')
            g=dict(card_sha256='card',release_sha256='release',run_id='UNIT',group_cleanup=dict(ownership_verified=True,no_live_owned_members=True),worker=worker,worker_returncode=0,stop_reason='WORKER_EXITED',native_identity_verified=True,monitored_elapsed_through_cleanup_s=1.,outer_wall_limit_s=900)
            identity=dict(schema='NATURAL_OWNED_PROCESS_IDENTITY_V1',run_id='UNIT',card_sha256='card',release_sha256='release',ownership_verified=True,child_returncode_before=None,child_returncode_after=None,worker=worker,native=dict(pid=102,pgid=101,sid=101,status='OBSERVED'))
            self.assertEqual(provenance.eof(raw,r,logs,g,identity,'card','release')['status'],'PASS_NATIVE_EOF_AND_OWNERSHIP')
            g['native_identity_verified']=False
            with self.assertRaises(ValueError):provenance.eof(raw,r,logs,g,identity,'card','release')

    def test_empty_yellow_real600_clock_and_absent_native_not_pass(self):
        d=read_bundle(BASE/'empty_none_641');post=next(r for r in d['files']['post_steps.jsonl'] if r.get('time_begin_s')==604)
        q=deepcopy(post['yellow_scope']);q['source_post_frame_time_s']=q['time_s']
        yellow.yellow_record(q,d['receipt']['cycles'],{}, {},641,dict(policy=yellow.POLICY,enabled=True))
        with tempfile.TemporaryDirectory() as tmp:
            r=actual.audit(Path(tmp)/'absent_manifest.json',Path(tmp)/'absent_card.json',root=tmp)
            self.assertEqual(r['status'],'UNKNOWN_NATIVE_PROVENANCE');self.assertFalse(r['qualified'])

if __name__=='__main__':unittest.main(verbosity=2)
