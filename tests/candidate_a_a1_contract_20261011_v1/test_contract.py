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
    def test_native_int_domain_maximum_and_adjacent_boundary(self):
        max_steps=32766;decel=4.5
        speed=max_steps*decel
        self.assertTrue(math.isfinite(brake_gap_euler(speed,decel)))
        speed_below=math.nextafter((max_steps+1)*decel,-math.inf)
        self.assertEqual(int(speed_below/decel),max_steps)
        self.assertTrue(math.isfinite(brake_gap_euler(speed_below,decel)))
        self.assertTrue(math.isfinite(brake_gap_euler((max_steps+.999)*decel,decel)))
        for speed_outside in ((max_steps+1)*decel,1e11):
            with self.assertRaises(ValueError):
                brake_gap_euler(speed_outside,decel)

    def test_finite_native_int_domain_unbound_is_unknown(self):
        s=fixture();s['vehicles'][0]['speed_m_s']=1e11
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

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

    def test_finite_extreme_brake_values_cannot_emit_nan(self):
        for speed,decel,step in [(1e200,4.5,1.0),(4.5,5e-324,1.0),
                                 (4.5,5e-324,5e-324)]:
            with self.subTest(speed=speed,decel=decel,step=step):
                with self.assertRaises(ValueError):brake_gap_euler(speed,decel,step)

    def test_finite_extreme_stop_speed_inputs_fail_as_valueerror(self):
        for gap,decel,step,headway in [(1e308,4.5,1,1),(1,5e-324,1,1),
                                      (1,5e-324,5e-324,1),(1,4.5,1,1e308),
                                      (1,4.5,1,5e-324)]:
            with self.subTest(gap=gap,decel=decel,step=step,headway=headway):
                with self.assertRaises(ValueError):maximum_safe_stop_speed_euler(gap,decel,step,headway)

    def test_reachability_and_response_underflow_not_silent_zero(self):
        with self.assertRaises(ValueError):one_step_excluded(1,1e308,1e308,1)
        with self.assertRaises(ValueError):one_step_excluded(1,0,5e-324,5e-324)
        with self.assertRaises(ValueError):brake_gap_euler(5e-324,4.5,1,5e-324)



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
        s=fixture();s['observed_red_crossing_ids']=['synthetic_front']
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')
        s=fixture();s['vehicles'][0].update(speed_m_s=9,seen_m=4)
        self.assertEqual(diagnostic_decision(s)['decision'],'INELIGIBLE')

    def test_red_crossing_missing_and_malformed_evidence_is_unknown(self):
        cases=[None,'unknown',True,False,{}, {'synthetic_front':True},
               ['synthetic_front','synthetic_front'],[''],[' '],[None],[True],
               [1],[{}],[['synthetic_front']],('synthetic_front',)]
        for value in cases:
            s=fixture();s['observed_red_crossing_ids']=value
            with self.subTest(value=value):
                result=diagnostic_decision(s)
                self.assertEqual(result['decision'],'UNKNOWN')
                self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])
        s=fixture();del s['observed_red_crossing_ids']
        result=diagnostic_decision(s)
        self.assertEqual(result['decision'],'UNKNOWN')
        self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])

    def test_red_crossing_foreign_ids_and_invalid_inventory_are_unknown(self):
        cases=[(['foreign'],['synthetic_front']),
               (['synthetic_front','foreign'],['synthetic_front'])]
        for inventory in [None,True,'synthetic_front',{},[{}],[''],[' '],
                          ['synthetic_front','synthetic_front'],['foreign'],[]]:
            cases.append((['synthetic_front'],inventory))
        for red_ids,inventory in cases:
            s=fixture();s['observed_red_crossing_ids']=red_ids
            s['affected_inventory_ids']=inventory
            with self.subTest(red_ids=red_ids,inventory=inventory):
                result=diagnostic_decision(s)
                self.assertEqual(result['decision'],'UNKNOWN')
                self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])

    def test_red_crossing_valid_ids_do_not_claim_observation_in_inconsistent_state(self):
        changes=[('source_commit','other'),('measurement_time_s',1205),
                 ('time_s',1205),('next_switch_s',1207),('step_s',.5),
                 ('phase_before',2),('motion_state','G'),('program','other'),
                 ('controlled_link',['foreign']),('vehicles',[{}]),
                 ('receiver',None)]
        for key,value in changes:
            s=fixture();s['observed_red_crossing_ids']=['synthetic_front'];s[key]=value
            with self.subTest(key=key):
                result=diagnostic_decision(s)
                self.assertEqual(result['decision'],'UNKNOWN')
                self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])

    def test_red_crossing_valid_empty_and_bound_positive_remain_distinct(self):
        s=fixture();result=diagnostic_decision(s)
        self.assertEqual(result['decision'],'UNKNOWN')
        self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])
        s['observed_red_crossing_ids']=['synthetic_front']
        result=diagnostic_decision(s)
        self.assertEqual(result['decision'],'INELIGIBLE')
        self.assertIn('OBSERVED_RED_ANOMALY',result['reasons'])
        self.assertNotEqual(result['decision'],'ELIGIBLE')

    def test_red_crossing_nonempty_vehicle_contract_mismatch_is_unknown(self):
        # 16 combinations: four fields x all four existing vehicle roles.
        for role in ['front','follower','ingress','receiver']:
            for key,value in [('speed_mode',0),('lane_change_mode',0),
                              ('action_step_s',2),('tau_s',.5)]:
                s=fixture();s['vehicles'][0]['role']=role;s['vehicles'][0][key]=value
                s['observed_red_crossing_ids']=['synthetic_front']
                with self.subTest(role=role,key=key):
                    result=diagnostic_decision(s)
                    self.assertEqual(result['decision'],'UNKNOWN')
                    self.assertIn('RED_CROSSING_EVIDENCE_UNBOUND_TO_STATE',result['reasons'])
                    self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])

    def test_red_crossing_empty_preserves_vehicle_contract_policy_denials(self):
        # Matched 16 negative controls: change only the crossing list to empty.
        for role in ['front','follower','ingress','receiver']:
            for key,value in [('speed_mode',0),('lane_change_mode',0),
                              ('action_step_s',2),('tau_s',.5)]:
                s=fixture();s['vehicles'][0]['role']=role;s['vehicles'][0][key]=value
                with self.subTest(role=role,key=key):
                    result=diagnostic_decision(s)
                    self.assertEqual(result['decision'],'INELIGIBLE')
                    self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])
                    self.assertNotIn('RED_CROSSING_EVIDENCE_UNBOUND_TO_STATE',result['reasons'])

    def test_red_crossing_matched_pinned_and_other_policy_denial_controls(self):
        # 12 controls: four roles x empty, valid positive, positive+receiver denial.
        for role in ['front','follower','ingress','receiver']:
            for condition in ['empty','positive','positive_receiver_blocked']:
                s=fixture();s['vehicles'][0]['role']=role
                if condition!='empty':s['observed_red_crossing_ids']=['synthetic_front']
                if condition=='positive_receiver_blocked':s['receiver']['rear_clearance_m']=7
                with self.subTest(role=role,condition=condition):
                    result=diagnostic_decision(s)
                    self.assertEqual(result['decision'],'UNKNOWN' if condition=='empty' else 'INELIGIBLE')
                    self.assertEqual('OBSERVED_RED_ANOMALY' in result['reasons'],condition!='empty')
                    self.assertNotIn('RED_CROSSING_EVIDENCE_UNBOUND_TO_STATE',result['reasons'])
                    if condition=='positive_receiver_blocked':
                        self.assertIn('RECEIVER_BLOCKED',result['reasons'])

    def test_red_crossing_multiple_mismatches_and_preexisting_denials(self):
        # 12 combinations: four roles x all mismatch+receiver denial,
        # noncrossing-mode mismatch+committed front, noncrossing dynamics mismatch.
        for role in ['front','follower','ingress','receiver']:
            for condition in ['all_mismatches_receiver_blocked',
                              'other_vehicle_modes_committed_front','other_vehicle_dynamics']:
                s=fixture();s['observed_red_crossing_ids']=['synthetic_front']
                if condition=='all_mismatches_receiver_blocked':
                    s['vehicles'][0].update(role=role,speed_mode=0,lane_change_mode=0,
                                            action_step_s=2,tau_s=.5)
                    s['receiver']['rear_clearance_m']=7
                else:
                    v=copy.deepcopy(s['vehicles'][0]);v.update(vehicle_id='additional',role=role)
                    if condition=='other_vehicle_modes_committed_front':
                        v.update(speed_mode=0,lane_change_mode=0)
                        s['vehicles'][0].update(speed_m_s=9,seen_m=4)
                    else:v.update(action_step_s=2,tau_s=.5)
                    s['vehicles'].append(v);s['affected_inventory_ids'].append('additional')
                with self.subTest(role=role,condition=condition):
                    result=diagnostic_decision(s)
                    self.assertEqual(result['decision'],'UNKNOWN')
                    self.assertIn('RED_CROSSING_EVIDENCE_UNBOUND_TO_STATE',result['reasons'])
                    self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])
                    if condition=='all_mismatches_receiver_blocked':
                        self.assertIn('RECEIVER_BLOCKED',result['reasons'])
                    elif condition=='other_vehicle_modes_committed_front':
                        self.assertIn('COMMITTED_APPROACH_NOT_ADMITTED',result['reasons'])

    def test_phase_type_rejects_invalid_values_with_empty_or_bound_red(self):
        # 22 cases: ten malformed/wrong phase values plus missing x two red lists.
        for phase in [True,False,1.0,0.0,None,'1',{},[],0,2]:
            for red in [[],['synthetic_front']]:
                s=fixture();s['phase_before']=phase;s['observed_red_crossing_ids']=red
                with self.subTest(phase=phase,phase_type=type(phase).__name__,red=red):
                    result=diagnostic_decision(s)
                    self.assertEqual(result['decision'],'UNKNOWN')
                    self.assertIn('PHASE_MISMATCH',result['reasons'])
                    self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])
        for red in [[],['synthetic_front']]:
            s=fixture();del s['phase_before'];s['observed_red_crossing_ids']=red
            result=diagnostic_decision(s)
            self.assertEqual(result['decision'],'UNKNOWN')
            self.assertIn('PHASE_MISMATCH',result['reasons'])
            self.assertNotIn('OBSERVED_RED_ANOMALY',result['reasons'])

    def test_integer_phase_one_preserves_matched_red_controls(self):
        # Two controls: JSON integer1, with empty or valid known positive IDs.
        for red in [[],['synthetic_front']]:
            s=fixture();s['phase_before']=1;s['observed_red_crossing_ids']=red
            result=diagnostic_decision(s)
            self.assertEqual(result['decision'],'INELIGIBLE' if red else 'UNKNOWN')
            self.assertEqual('OBSERVED_RED_ANOMALY' in result['reasons'],bool(red))
            self.assertNotIn('PHASE_MISMATCH',result['reasons'])
            self.assertNotEqual(result['decision'],'ELIGIBLE')

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
        relative='artifacts/candidate_a_a1_contract_20261011_v1/review_fix_20261011/v6/INPUT_BINDINGS_V6.json'
        binds=json.loads((ROOT/relative).read_text())
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp);(dest/relative).parent.mkdir(parents=True)
            (dest/relative).write_text(json.dumps(binds))
            first=next(iter(binds['files']))
            (dest/first).parent.mkdir(parents=True,exist_ok=True)
            (dest/first).write_text('tampered input')
            with self.assertRaisesRegex(ValueError,'hash drift'):audit(dest)


    def test_finite_subnormal_decel_and_huge_speed_return_unknown(self):
        cases=[dict(decel_m_s2=5e-324,emergency_decel_m_s2=5e-324,yellow_min_decel_m_s2=5e-324),
               dict(speed_m_s=1e200),dict(speed_m_s=1e308)]
        for change in cases:
            s=fixture();s['vehicles'][0].update(change)
            with self.subTest(change=change):
                self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')

    def test_overflowing_finite_receiver_inputs_return_unknown(self):
        s=fixture();s['receiver'].update(rear_clearance_m=1e308,vehicle_length_m=1e308,min_gap_m=1e308)
        self.assertEqual(diagnostic_decision(s)['decision'],'UNKNOWN')



if __name__=='__main__':unittest.main()
