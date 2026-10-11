"""Issue4 regression and failed-state tests; no SUMO/TraCI launch."""
from dataclasses import replace
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts/candidate_a_qualification_20261008_v1'))
from src.candidate_a_qualification_20261008.actor import CycleLedger,PhaseEnvelope,motion_phase,crossing_records
from src.candidate_a_qualification_20261008.safety import Vehicle,red_transition_witness,normal_red_envelope_m,assert_ingress_and_crossing_coverage
import runner
from worker import accounting_coverage,request_phase,startup_trace_callback,connect_traci

class MappingTests(unittest.TestCase):
    def drive(self,rate,end=3000,deny=False):
        q=CycleLedger(1200)
        rows=[]
        for t in range(1200,end):
            start,c=q.begin_step(t,rate)
            if start:q.mark_cycle_start(not deny,'TEST_DENIAL' if deny else '')
            s=q.envelope.state_at(t-c['begin_s'],c['period_s'],c['executed'])
            e=q.end_step(t+1,[],s)
            rows.append((t,rate/3600,e))
        return q,rows
    def test_fixed_rates_phase_complete_and_finite_window_bound(self):
        for rate in (300,450,600,750,900):
            q,rows=self.drive(rate)
            for begin in range(1200,2701,17):
                r=[x for x in rows if begin<=x[0]<begin+300]
                self.assertLess(abs(sum(x[1] for x in r)-sum(x[2] for x in r)),4.5)
            for c in q.rows:
                self.assertGreaterEqual(c['period_s'],8)
                self.assertEqual(sum(x[1] for x in q.envelope.phases(c['period_s'])),c['period_s'])
                self.assertTrue(set(q.envelope.state_at(i,c['period_s']) for i in range(c['period_s']))=={'G','y','r'})
    def test_750_fractional_cycle_mean_uses_elapsed_time(self):
        q,_=self.drive(750,end=1248)
        self.assertEqual([c['period_s'] for c in q.rows],[9,10,9,10,10])
        self.assertEqual(q.E,10);self.assertEqual(q.C,10)
    def test_denied_cycle_does_not_erase_E(self):
        q,_=self.drive(900,deny=True,end=1500)
        self.assertEqual(q.E,74);self.assertEqual(q.N,0)
        self.assertEqual(q.C,75)
        self.assertTrue(all(c['denial_reason']=='TEST_DENIAL' for c in q.rows))
    def test_midcycle_command_update_does_not_restart_green(self):
        q=CycleLedger(1200)
        for t in range(1200,1225):
            rate=300 if t==1200 else 900
            start,c=q.begin_step(t,rate)
            if start:q.mark_cycle_start(True)
            if t==1201:self.assertEqual(c['applied_command_veh_h'],300);self.assertFalse(start)
            q.end_step(t+1,[],q.envelope.state_at(t-c['begin_s'],c['period_s']))
        self.assertEqual(q.rows[1]['begin_s'],1224)
        self.assertEqual(q.rows[1]['applied_command_veh_h'],900)
        self.assertEqual(q.rows[1]['application_delay_s'],23)
        self.assertAlmostEqual(q.accounting()['mapping_command_latency'],23*600/3600)
    def test_variable_command_exact_partition(self):
        q=CycleLedger(1200)
        for t in range(1200,1800):
            rate=(300,900,750)[((t-1200)//30)%3]
            start,c=q.begin_step(t,rate)
            if start:q.mark_cycle_start(True)
            q.end_step(t+1,[],q.envelope.state_at(t-c['begin_s'],c['period_s']))
        a=q.accounting()
        self.assertAlmostEqual(a['C']-a['N'],a['mapping_command_latency']+a['mapping_quantization']+a['physical_shortfall'])
    def test_before_motion_abort_has_no_unexecuted_command_accrual(self):
        q=CycleLedger(1200);q.begin_step(1200,900);q.mark_cycle_start(False,'UNSAFE')
        self.assertEqual(q.C,0);self.assertEqual(q.E,0);self.assertEqual(q.N,0)
    def test_post_motion_failure_ledger_retains_real_elapsed_second(self):
        q=CycleLedger(1200);q.begin_step(1200,900);q.mark_cycle_start(True)
        q.end_step(1201,['R_1'],'G')
        self.assertEqual(q.C,Fraction(1,4));self.assertEqual(q.N,1)
        self.assertFalse(q.cycle['completed']);self.assertEqual(q.next_time_s,1201)
    def test_invalid_time_and_unsafe_envelope_rejected(self):
        with self.assertRaises(ValueError):PhaseEnvelope(green_s=4)
        with self.assertRaises(ValueError):CycleLedger(600).begin_step(601,900)

class AccountingFailureTests(unittest.TestCase):
    def test_inherited_connection_uses_callable_trace_without_socket(self):
        import tempfile
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'trace.jsonl';trace=startup_trace_callback(path)
            self.assertTrue(callable(trace))
            traci=Mock();process=Mock();process.poll.return_value=None
            result=connect_traci(traci,8813,process,trace,enforce_alarm=False)
            self.assertIs(result,traci.connect.return_value)
            event=json.loads(path.read_text())
            self.assertEqual(event['outcome'],'CONNECTED')
            trace(dict(outcome='FIXTURE_SECOND_ENTRY'))
            self.assertEqual(len(path.read_text().splitlines()),2)
            with self.assertRaises(FileExistsError):startup_trace_callback(path)

    def test_phase_requests_log_attempt_success_and_failure(self):
        from unittest.mock import Mock
        tls=Mock();requests=[]
        request_phase(tls,requests,0,'setProgram','A_OPEN')
        request_phase(tls,requests,0,'setPhase',0)
        self.assertEqual([(r['method'],r['value'],r['call_completed']) for r in requests],[('setProgram','A_OPEN',True),('setPhase',0,True)])
        tls.setPhase.side_effect=RuntimeError('API failure')
        with self.assertRaises(RuntimeError):request_phase(tls,requests,600,'setPhase',1)
        self.assertEqual(requests[-1],dict(time_s=600,method='setPhase',value=1,call_completed=False))
    def test_feedback_inside_cycle_produces_no_phase_api_requests(self):
        from unittest.mock import Mock
        tls=Mock();q=CycleLedger(1200)
        for t in range(1200,1203):
            requests=[];start,c=q.begin_step(t,300 if t==1200 else 900)
            if start:
                q.mark_cycle_start(True)
                for method,value in [('setProgram','CA_C24'),('setPhase',2),('setPhase',0)]:request_phase(tls,requests,t,method,value)
            else:self.assertEqual(requests,[])
            q.end_step(t+1,[],q.envelope.state_at(t-c['begin_s'],c['period_s']))
        self.assertEqual(tls.setProgram.call_count,1);self.assertEqual(tls.setPhase.call_count,2)

    def test_poststep_observation_or_commit_failure_is_unsupported(self):
        for failed_stage in ('TLS_STATE_PENDING','INTERNAL_IDS_PENDING','CROSSING_RECONCILIATION_PENDING','LEDGER_COMMIT_PENDING'):
            with self.subTest(failed_stage=failed_stage):
                q=CycleLedger(1200);q.begin_step(1200,900);q.mark_cycle_start(True)
                a=accounting_coverage(1201,1200)
                self.assertFalse(a['accounting_complete'])
                self.assertFalse(a['qualification_accounting_supported'])
                self.assertEqual(a['accounting_status'],'UNRECONCILED_UNSUPPORTED')
                self.assertEqual(a['unaccounted_completed_interval_s'],[1200,1201])
                self.assertEqual(q.N,0)  # No unknown actual crossing invented.
    def test_precontrol_poststep_failure_and_pre_step_stop_are_distinct(self):
        self.assertFalse(accounting_coverage(11,10)['accounting_complete'])
        self.assertTrue(accounting_coverage(1200,1200)['accounting_complete'])
    def test_successfully_committed_poststep_failure_preserves_coverage(self):
        q=CycleLedger(1200);q.begin_step(1200,900);q.mark_cycle_start(True)
        q.end_step(1201,['R_1'],'G')
        a=accounting_coverage(1201,q.next_time_s)
        self.assertTrue(a['accounting_complete']);self.assertEqual(q.N,1)

class NativeAndCrossingTests(unittest.TestCase):
    def test_getter_old_phase_at_switch_is_predicted_before_motion(self):
        phases=PhaseEnvelope().phases(8)
        self.assertEqual(motion_phase(0,'G',1203,1203,phases),(1,'y'))
        self.assertEqual(motion_phase(1,'y',1206,1206,phases),(2,'r'))
        self.assertEqual(motion_phase(1,'y',1206,1205,phases),(1,'y'))
        self.assertEqual(motion_phase(2,'r',1208,1208,phases),(2,'r'))
    def test_missing_or_overdue_actual_phase_fails_closed(self):
        for args in ((0,'r',1203,1200),(-1,'G',1203,1200),(0,'G',1199,1200),(0,'G',math.nan,1200)):
            with self.assertRaises(ValueError):motion_phase(*args,PhaseEnvelope().phases(8))
    def test_yellow_red_and_multiple_crossings_all_counted(self):
        for s in ('G','y','r'):
            rows=crossing_records({'R_1','R_2'},{'R_old'},{'R_old','R_1','R_2'},1300,4,s)
            self.assertEqual(len(rows),2)
            self.assertTrue(all(r['crossing_time_lower_s']==1300 and r['crossing_time_upper_s']==1301 and r['motion_signal_state']==s for r in rows))
        with self.assertRaises(ValueError):crossing_records(set(),set(),{'R_unknown'},1300,4,'G')
    def test_unique_ids_and_actual_more_than_nominal_not_clamped(self):
        q=CycleLedger(1200);q.begin_step(1200,900);q.mark_cycle_start(True)
        q.end_step(1201,['R_1','R_2','R_3'],'G');self.assertEqual(q.N,3)
        q.begin_step(1201,900)
        with self.assertRaises(ValueError):q.end_step(1202,['R_1'],'G')

class SafetyTests(unittest.TestCase):
    def state(self,pos=150,speed=5,pop='storage'):
        return Vehicle('R_1',pop,pos,speed,5,2.5,2.6,4.5,1,1,'technical_passenger')
    def test_low_positive_speed_near_line_is_not_stopped_shortcut(self):
        self.assertFalse(red_transition_witness([self.state(204.4899,.099)])['safe'])
        self.assertTrue(red_transition_witness([self.state(204.4899,0)])['safe'])
    def test_follower_ingress_identity_and_exact_red_boundary(self):
        v=self.state();req=normal_red_envelope_m(v)
        self.assertTrue(red_transition_witness([replace(v,position_m=204.49-req)])['safe'])
        self.assertFalse(red_transition_witness([replace(v,position_m=204.49-req+1e-6)])['safe'])
        self.assertTrue(red_transition_witness([self.state(-1,20,'ingress')])['safe'])
        with self.assertRaises(ValueError):red_transition_witness([v,v])
    def test_unknown_dynamics_and_unseen_population_fail_closed(self):
        for v in (replace(self.state(),tau_s=.9),replace(self.state(),speed_m_s=math.nan),replace(self.state(),type_id='unknown'),self.state(1,10,'ingress')):
            with self.assertRaises(ValueError):red_transition_witness([v])
    def test_no_internal_skip_or_unseen_ingress_proof(self):
        self.assertTrue(assert_ingress_and_crossing_coverage(55.5555555556,2.6)['new_crossing_cannot_skip_internal_lane_in_one_step'])
        with self.assertRaises(ValueError):assert_ingress_and_crossing_coverage(80,3)

class ReleaseTests(unittest.TestCase):
    def test_source_import_and_missing_release_cannot_spawn(self):
        self.assertTrue(callable(runner.prepare))
        with patch.object(runner.subprocess,'Popen') as p:
            with self.assertRaises(FileNotFoundError):runner.launch('/missing/card.json','/missing/release.json')
            p.assert_not_called()
    def test_preload_and_n_assumption_explicit_contract(self):
        j=json.loads((runner.CONFIG/'PHASE_RATE_CONTRACT.json').read_text())
        self.assertEqual(j['nominal_n_status'],'UNQUALIFIED_DISCHARGE_ASSUMPTION')
        self.assertEqual(j['tracking_tolerance'],.1)
        self.assertIn('no preload',j['PhaseC'])

if __name__=='__main__':unittest.main()
