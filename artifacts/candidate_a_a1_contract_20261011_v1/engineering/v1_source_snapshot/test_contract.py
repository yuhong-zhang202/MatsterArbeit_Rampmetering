"""Synthetic offline adversarial tests; none execute native SUMO movement."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/candidate_a_a1_contract_20261011_v1'))
from contract import (SOURCE_COMMIT,Decision,brake_gap_euler,local_plan_stop,
                      execute_yellow_can_brake,maximum_safe_stop_speed_euler,
                      one_step_excluded,old_guard,diagnostic_decision)
from audit_public import audit


def fixture():
    # SYNTHETIC direct-input shape; it is neither A07 native state nor proof.
    v=dict(vehicle_id='synthetic_front',role='front',type_id='technical_passenger',
           model='Krauss',speed_mode=31,lane_change_mode=1621,speed_m_s=4.5,
           seen_m=20.0,lane_offset_m=0.0,decel_m_s2=4.5,emergency_decel_m_s2=9.0,
           yellow_min_decel_m_s2=3.0,jm_stopline_gap_m=1.0,action_step_s=1.0,tau_s=1.0)
    return dict(schema='A1_LOCAL_DIAGNOSTIC_V1',source_commit=SOURCE_COMMIT,
                time_s=1206,measurement_time_s=1206,next_switch_s=1206,step_s=1,
                phase_before=1,state_before='y',motion_state='r',program='CA_C24',
                controlled_link=['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0'],
                vehicles=[v],affected_inventory_ids=['synthetic_front'],
                receiver=dict(rear_clearance_m=20,vehicle_length_m=5,min_gap_m=2.5),
                observed_red_crossing_ids=[])


class ScalarBoundaryTests(unittest.TestCase):
    def test_zero_speed_is_not_a_full_eligibility_exemption(self):
        p=local_plan_stop(0,1,0,4.5,9,3,1)
        self.assertEqual(p['brake_gap_m'],0)
        s=fixture();s['vehicles'][0]['speed_m_s']=0
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_low_positive_a07_is_old_rejection_not_native_outcome(self):
        speed=0.04573822948686786;gap=1.001999189766508
        self.assertFalse(old_guard(speed,gap,4.5)['safe'])
        p=local_plan_stop(speed,gap,0,4.5,9,3,1)
        self.assertTrue(p['can_brake_before_stopline'])
        self.assertEqual(p['brake_gap_m'],0)
        self.assertAlmostEqual(p['native_stop_dist_m'],0.001999189766508)
        self.assertAlmostEqual(maximum_safe_stop_speed_euler(p['native_stop_dist_m'],4.5),0.000999189766508)
        self.assertIsNone(p['full_branch_selected']);self.assertIsNone(p['next_speed_m_s'])

    def test_braking_formula_against_independent_finite_sum(self):
        for speed in [0,.001,4.49,4.5,4.500001,8.999999,9,13.5,22.22,55.55555555555556]:
            count=int(speed/4.5)
            expected=sum(speed-i*4.5 for i in range(1,count+1))
            self.assertAlmostEqual(brake_gap_euler(speed,4.5),expected)

    def test_plan_equality_and_execution_strict_equality_differ(self):
        p=local_plan_stop(9,4.5,0,4.5,9,3,1)
        self.assertTrue(p['can_brake_before_stopline'])
        self.assertFalse(execute_yellow_can_brake(9,4.5,4.5))
        self.assertTrue(execute_yellow_can_brake(9,math.nextafter(4.5,math.inf),4.5))
        p=local_plan_stop(9,math.nextafter(4.5,-math.inf),0,4.5,9,3,1)
        self.assertFalse(p['can_brake_before_stopline'])

    def test_native_offset_is_adjusted_not_fixed_one_metre(self):
        p=local_plan_stop(9,5,0,4.5,9,3,1)
        self.assertEqual(p['native_adjusted_stop_offset_m'],.5)
        p=local_plan_stop(9,4.5,0,4.5,9,3,1)
        self.assertEqual(p['native_adjusted_stop_offset_m'],.1)

    def test_stop_offset_can_change_branch_even_when_speed_zero(self):
        p=local_plan_stop(0,.5,1,4.5,9,3,1)
        self.assertFalse(p['can_brake_before_stopline'])

    def test_stop_speed_epsilon_boundary(self):
        self.assertEqual(maximum_safe_stop_speed_euler(.000999,4.5),0)
        self.assertEqual(maximum_safe_stop_speed_euler(.001,4.5),0)
        self.assertGreater(maximum_safe_stop_speed_euler(.001001,4.5),0)

    def test_yellow_override_and_emergency_decel_are_explicit(self):
        self.assertEqual(local_plan_stop(9,20,0,4.5,9,8,1)['stop_decel_m_s2'],8)
        self.assertEqual(local_plan_stop(9,20,0,4.5,9,12,1)['stop_decel_m_s2'],9)

    def test_reachability_equality_is_not_exclusion(self):
        bound=55.55555555555556+2.6
        self.assertFalse(one_step_excluded(bound,55.55555555555556,2.6))
        self.assertTrue(one_step_excluded(113.08,55.55555555555556,2.6))

    def test_nonfinite_negative_or_boolean_source_inputs_rejected(self):
        for speed in [math.nan,math.inf,-1,True,None,10**1000]:
            with self.subTest(speed=str(speed)[:20]):
                with self.assertRaises(ValueError):brake_gap_euler(speed,4.5)


class AdversarialContractTests(unittest.TestCase):
    def test_synthetic_best_case_remains_unknown(self):
        self.assertEqual(diagnostic_decision(fixture())['decision'],'UNKNOWN')

    def test_arbitrary_proof_flags_cannot_enable_eligible(self):
        s=fixture();s.update(proof_complete=True,safe=True,all_foes_excluded=True,randomness_bounded=True)
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_committed_vehicle_is_policy_ineligible_not_proven_collision(self):
        s=fixture();s['vehicles'][0].update(speed_m_s=9,seen_m=4.499)
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')

    def test_follower_and_ingress_cannot_be_ignored(self):
        for role in ['follower','ingress']:
            s=fixture();v=copy.deepcopy(s['vehicles'][0]);v.update(vehicle_id='additional',role=role,speed_m_s=9,seen_m=4)
            s['vehicles'].append(v);s['affected_inventory_ids'].append('additional')
            self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')

    def test_unenumerated_new_vehicle_fails_closed(self):
        s=fixture();s['affected_inventory_ids'].append('new_ingress')
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_duplicate_or_invalid_identity_fails_closed(self):
        for bad in ['duplicate','invalid']:
            s=fixture()
            if bad=='duplicate':s['vehicles'].append(copy.deepcopy(s['vehicles'][0]))
            else:s['vehicles'][0]['vehicle_id']=['not','an','id']
            self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_receiver_blocked_or_unknown(self):
        s=fixture();s['receiver']['rear_clearance_m']=7.49
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')
        s['receiver']['rear_clearance_m']=None
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_foe_and_randomness_are_unproved_even_with_local_pass(self):
        s=fixture();s['foe_states']=[];s['rng_seed']=17
        d=diagnostic_decision(s)
        self.assertEqual(d['decision'],'UNKNOWN')
        self.assertIn('RECEIVER_LEADER_FOLLOWER_FOE_AND_RANDOM_BOUNDS_UNRESOLVED',d['reasons'])

    def test_timestamp_phase_link_and_source_mismatches(self):
        mutations=[('measurement_time_s',1205),('next_switch_s',1207),('phase_before',2),
                   ('state_before','G'),('controlled_link',['wrong']),('source_commit','other'),('step_s',.5)]
        for key,value in mutations:
            s=fixture();s[key]=value
            self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_changed_modes_and_dynamics(self):
        for key,value in [('speed_mode',0),('lane_change_mode',0),('action_step_s',2),('tau_s',.5)]:
            s=fixture();s['vehicles'][0][key]=value
            self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')

    def test_new_type_missing_fields_nonfinite_fail_closed(self):
        for key,value in [('type_id','new_type'),('model','IDM'),('decel_m_s2',None),('speed_m_s',math.nan),('speed_mode',None)]:
            s=fixture();s['vehicles'][0][key]=value
            self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_observed_red_anomaly_and_yellow_commitment_not_pass(self):
        s=fixture();s['observed_red_crossing_ids']=['front']
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')
        s=fixture();s['vehicles'][0].update(speed_m_s=9,seen_m=4)
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')

    def test_missing_or_malformed_snapshot_fails_closed(self):
        for s in [None,{}, {'schema':'other'},dict(fixture(),affected_inventory_ids=[{}])]:
            self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_public_a07_42_mapping_and_missing_observations(self):
        r=audit()
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['witness_count'],42)
        self.assertEqual(r['old_guard_unsafe_ids'],['R_flow.1'])
        self.assertEqual(r['actual_native_branches_determined'],0)
        self.assertEqual(r['upstream_public_audit']['service_observed_steps'],[6,0,0,0,0,0])
        self.assertFalse(r['full_a1_eligibility_proven'])
        self.assertEqual(r['a07_a1_decision'],'UNKNOWN')

    def test_public_default_does_not_read_ignored_raw(self):
        read_text=Path.read_text;read_bytes=Path.read_bytes
        def text(p,*args,**kwargs):
            if 'data/raw/' in str(p):raise AssertionError('raw read forbidden')
            return read_text(p,*args,**kwargs)
        def data(p,*args,**kwargs):
            if 'data/raw/' in str(p):raise AssertionError('raw read forbidden')
            return read_bytes(p,*args,**kwargs)
        with patch.object(Path,'read_text',text),patch.object(Path,'read_bytes',data):
            self.assertEqual(audit()['status'],'PASS')

    def test_public_source_or_input_hash_drift_fails(self):
        relative='artifacts/candidate_a_a1_contract_20261011_v1/engineering/INPUT_BINDINGS.json'
        binds=json.loads((ROOT/relative).read_text())
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp);(dest/relative).parent.mkdir(parents=True)
            (dest/relative).write_text(json.dumps(binds))
            first=next(iter(binds['files']))
            (dest/first).parent.mkdir(parents=True,exist_ok=True)
            (dest/first).write_text('tampered input')
            with self.assertRaisesRegex(ValueError,'hash drift'):audit(dest)



if __name__=='__main__':unittest.main()
