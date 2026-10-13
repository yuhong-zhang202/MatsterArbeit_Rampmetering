"""Bounded approved exception tests; offline bindings are synthetic, not native proof."""
from copy import deepcopy
from pathlib import Path
import importlib.util, tempfile, unittest
from src.candidate_a_unified_alinea_20261013 import numeric_stop as n, profile
from src.candidate_a_unified_alinea_20261013.adapter import StepAdapter
from src.candidate_a_unified_alinea_20261013.policy import Command
sp=importlib.util.spec_from_file_location('unified_fixture',Path(__file__).with_name('test_unified.py'))
f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)


def authority():
    return dict(enabled=True,run_id='UA_FIXED750_S17_02',mode='fixed750',approval_sha256='a'*64,
        execution_card_sha256='b'*64,source_commit='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3',
        actual_branch_identified=False,configured_model='Krauss',configured_Euler_dt_s=1,
        no_model_or_JM_override=True)


def evidence():
    # Speed/position/alpha taken from the retained 750/01 event. Extra bindings
    # below are deliberately constructed offline and are NOT claimed observed.
    a=authority();v=4.69222772465427;pos=203.97137014006898;post=.19122772465426985
    before=dict(vehicle_id='R_flow.13',time_s=1264,lane_id=n.STORAGE,type_id='technical_passenger',
        route=list(n.ROUTE),speed_mode=31,lane_change_mode=1621,speed_m_s=v,
        position_m=pos,length_m=5.,dynamics=dict(n.DYNAMICS))
    after={**deepcopy(before),'time_s':1265,'speed_m_s':post,'position_m':204.16259786}
    return dict(run_id=a['run_id'],mode=a['mode'],execution_card_sha256=a['execution_card_sha256'],
        vehicle_id='R_flow.13',time_begin_s=1264,time_end_s=1265,dt_s=1,before=before,after=after,
        motion='y',first_yellow_begin_s=1264,post_signal_binding_status='BOUND_BEFORE_LEDGER',
        actual_phase=1,actual_state='y',actual_program='I12_PACKET10',expected_program='I12_PACKET10',
        controlled_links=[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]],
        full_before_after_world_binding=True,entered_link=False,body_coverage_complete=True,
        before_current_gap_status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',
        after_current_gap_status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',
        native_event_counters=dict(colliding_vehicles=0,starting_teleports=0,ending_teleports=0),
        native_warning_observed=False,recorded_delta_v_m_s2=-4.501,
        actual_native_acceleration_m_s2=-4.501)


class NumericStopTests(unittest.TestCase):
    def test_real_value_formula_and_joint_negative_bindings(self):
        e=evidence();positive=n.classify(e,authority())
        self.assertEqual(positive['decision'],'CONTINUE_RESTRICTED_NUMERICAL_EVENT')
        self.assertEqual(positive['observed_native_acceleration_m_s2'],-4.501)
        self.assertFalse(positive['actual_branch_identified']);self.assertTrue(positive['legacy_strict_FAIL_retained'])
        self.assertAlmostEqual(positive['source_reference']['predicted_speed_m_s'],e['after']['speed_m_s'])
        faults=[('phase_bool',lambda x:x.update(actual_phase=True)),
            ('phase_float',lambda x:x.update(actual_phase=1.0)),
            ('ID_mode_dynamics',lambda x:(x['after'].update(vehicle_id='R_flow.14',speed_mode=0),x['before']['dynamics'].update(decel=4.6))),
            ('time',lambda x:x.update(time_end_s=1266)),('dt_bool',lambda x:x.update(dt_s=True)),
            ('dt_float',lambda x:x.update(dt_s=1.0)),('dt_units',lambda x:x.update(dt_s=1000)),
            ('model',lambda x:x['after'].update(type_id='other')),
            ('position',lambda x:x['after'].update(position_m=204.49)),
            ('gap',lambda x:x.update(after_current_gap_status='STOP_CURRENT_GAP_BOUND_DENIED')),
            ('warning',lambda x:x.update(native_warning_observed=True)),
            ('collision',lambda x:x['native_event_counters'].update(colliding_vehicles=1)),
            ('coverage',lambda x:x.update(body_coverage_complete=False)),
            ('unbound_card',lambda x:x.update(execution_card_sha256='c'*64)),
            ('wrong_program',lambda x:x.update(actual_program='I12_PACKET8')),
            ('missing',lambda x:x.pop('before')),
            ('alpha_nonfinite',lambda x:x.update(actual_native_acceleration_m_s2=float('nan'))),
            ('stronger',lambda x:(x['after'].update(speed_m_s=.19022772465426985,
                position_m=x['before']['position_m']+.19022772465426985),
                x.update(recorded_delta_v_m_s2=-4.502,actual_native_acceleration_m_s2=-4.502))),
            ('boundary_domain',lambda x:x['before'].update(speed_m_s=4.501)),
            ('not_legacy_fail',lambda x:(x['after'].update(speed_m_s=.19222772465426985,
                position_m=x['before']['position_m']+.19222772465426985),
                x.update(recorded_delta_v_m_s2=-4.5,actual_native_acceleration_m_s2=-4.5)))]
        for name,mutate in faults:
            with self.subTest(fault=name):
                q=deepcopy(e);mutate(q);self.assertEqual(n.classify(q,authority())['decision'],'STOP')
        for a in (None,{**authority(),'enabled':False},{**authority(),'configured_model':'IDM'}):
            self.assertEqual(n.classify(e,a)['decision'],'STOP')

    def adapter_case(self, tmp, enabled=True, warning=False, main_brake=False):
        pkg=Path(tmp)/'pkg';profile.stage_package(profile.ROOT,pkg,Path(tmp)/'out',1270)
        w=f.UnifiedWorld(pkg/'scenario.add.xml');w.time=1264
        w.program='I12_PACKET10';w.phase=0;w.state='G';w.switch=1264
        for i in range(13):w.enter[f'R_flow.{i}']=1257
        v='R_flow.13';p0=evidence()['before']['position_m'];v0=evidence()['before']['speed_m_s']
        original_position=w.position
        w.position=lambda vid:p0 if vid==v and w.time==1264 else (204.16259786 if vid==v else original_position(vid))
        w.vehicle.getLanePosition=w.position;w.vspeed[v]=v0
        original_acceleration=w.vehicle.getAcceleration
        w.vehicle.getAcceleration=lambda vid:-4.501 if vid==v and w.time==1265 else (-4.55 if vid=='M_flow.0' and main_brake and w.time==1265 else original_acceleration(vid))
        a=StepAdapter(w.observe,750,1270,authority() if enabled else None)
        a.ledger.begin_step(1260,Command('fixed750',1260,750,'FIXED'));a.ledger.mark_cycle_start(True)
        for t in range(1260,1264):
            if t!=1260:a.ledger.begin_step(t)
            a.ledger.end_step(t+1,[],'G')
        a.ledger.begin_step(1264);a.previous_motion='G'
        a.prepare_step(w,1264)
        w.time=1265;w.phase=1;w.state='y';w.switch=1268;w.vspeed[v]=evidence()['after']['speed_m_s']
        if main_brake:w.vspeed['M_flow.0']-=4.55
        obs=dict(time_begin_s=1264,time_end_s=1265,coverage='CALLER_DECLARED_INTERVAL',source='offline-fixture',
            byte_start=0,byte_end=0,text='emergency braking' if warning else '')
        return a,w,obs

    def test_adapter_default_strict_and_explicit_numerical_exception(self):
        for enabled in (False,True):
            with self.subTest(enabled=enabled),tempfile.TemporaryDirectory() as tmp:
                a,w,obs=self.adapter_case(tmp,enabled)
                if enabled:
                    row=a.reconcile_step(w,obs)
                    self.assertEqual(row['numeric_stop_classifications'][0]['decision'],'CONTINUE_RESTRICTED_NUMERICAL_EVENT')
                    self.assertEqual(row['braking_observation']['actual_acceleration_m_s2']['R_flow.13'],-4.501)
                    self.assertEqual(len(row['legacy_braking_reasons']),2)
                else:
                    with self.assertRaisesRegex(ValueError,'ORDINARY_BRAKING_EXCEEDED:R_flow.13'):a.reconcile_step(w,obs)
                    self.assertEqual(a.receipts[-1]['numeric_stop_classifications'],[])

    def test_coexisting_other_vehicle_or_native_alarm_still_stops(self):
        for warning,main_brake in ((True,False),(False,True)):
            with self.subTest(warning=warning,main_brake=main_brake),tempfile.TemporaryDirectory() as tmp:
                a,w,obs=self.adapter_case(tmp,True,warning,main_brake)
                reason='NATIVE_WARNING' if warning else 'ORDINARY_BRAKING_EXCEEDED:M_flow.0'
                with self.assertRaisesRegex(ValueError,reason):a.reconcile_step(w,obs)
                self.assertTrue(a.paused)
                self.assertEqual(a.receipts[-1]['braking_observation']['actual_acceleration_m_s2']['R_flow.13'],-4.501)
