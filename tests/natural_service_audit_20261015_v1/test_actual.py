"""Read saved affected bundles only; no fake loop, native, or expanded matrix."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles'
OUT=ROOT/'data/processed/thesis_actuator_readiness_20261015_v1/natural_reader_v1'
s=importlib.util.spec_from_file_location('natural_reader',ROOT/'scripts/natural_service_audit_20261015_v1/actual.py');reader=importlib.util.module_from_spec(s);s.loader.exec_module(reader)

class ReaderTests(unittest.TestCase):
    def test_saved_ordinary_cases_and_minimal_rejections(self):
        results={}
        for name in ('empty_none_641','supply_none_641','late_none_641','blocked_none_641','blocked_none_640'):
            with self.subTest(case=name):results[name]=reader.audit(reader.read_bundle(BASE/name))
        self.assertEqual(results['empty_none_641']['N'],0)
        self.assertTrue(all(n<2 for n in results['supply_none_641']['complete_packet_actual_N']))
        self.assertEqual(results['empty_none_641']['periods'],results['supply_none_641']['periods'])
        self.assertEqual(results['blocked_none_641']['held_packets'],[1])
        self.assertTrue(results['blocked_none_641']['partial']);self.assertFalse(results['blocked_none_640']['partial'])
        base=reader.read_bundle(BASE/'blocked_none_641');checks={}
        def rejection(name,mutate):
            d=deepcopy(base);mutate(d)
            with self.subTest(rejection=name),self.assertRaises((ValueError,KeyError,TypeError,IndexError)):reader.audit(d)
            checks[name]='REJECTED'
        rejection('missing_ACK',lambda d:d['files']['step_ack.jsonl'].pop(1215))
        rejection('false_held_applied_request',lambda d:d['receipt']['cycles'][1].update(applied_request_id='real_alinea:600'))
        rejection('false_executed_held_cycle',lambda d:d['receipt']['cycles'][1].update(executed=True))
        rejection('physical_debt_selection',lambda d:next(e for e in d['files']['command_events.jsonl'] if e['event']=='BOUNDARY_PACKET_SELECTED_NOT_APPLIED' and e['time_s']==616).update(scheduled_error_fraction='3'))
        rejection('held_selected_as_actual_program',lambda d:next(r for r in d['files']['post_steps.jsonl'] if r.get('time_begin_s')==608)['post_signal_application_binding'].update(actual_program='SELECTED_BUT_NOT_EXECUTED'))
        rejection('missing_held_duration_readback',lambda d:d['files'].update({'policy_duration_requests.jsonl':[e for e in d['files']['policy_duration_requests.jsonl'] if e['time_s']!=608]}))
        rejection('terminal_setter',lambda d:d['files']['policy_phase_requests.jsonl'].append({'time_s':641,'requests':[]}))
        rejection('missing_E1_sample',lambda d:d['files'].update({'feedback_events.jsonl':[e for e in d['files']['feedback_events.jsonl'] if not(e['event']=='E1_POST_ACK_EVENTS' and e['global_s']==610)]}))
        rejection('missing_command_record',lambda d:d['receipt']['command_records'].pop('feedback:630'))
        rejection('unreported_safety_stop',lambda d:d['files']['post_steps.jsonl'][-1].update(status='STOP_OBSERVED_AFTER_STEP',reasons=['SYNTHETIC_HARD_FAULT']))
        # Explicit synthetic current-terminal stop annotation tests retention,
        # not a new observed runtime safety-fault case.
        hard=deepcopy(base);hard['receipt']['error']='DiagnosticStop:SYNTHETIC_HARD_FAULT'
        hard['files']['post_steps.jsonl'][-1].update(status='STOP_OBSERVED_AFTER_STEP',reasons=['SYNTHETIC_HARD_FAULT'])
        results['synthetic_terminal_hard_annotation']=reader.audit(hard)
        self.assertEqual(results['synthetic_terminal_hard_annotation']['observed_stop'],'HARD_OR_UNKNOWN_STOP_RETAINED')
        with (OUT/'OFFLINE_RESULT_V2.json').open('x') as f:json.dump(dict(status='PASS_OFFLINE_SAVED_BUNDLE_INTEGRITY_ONLY',cases=results,rejections=checks,native_started=False),f,indent=2);f.write('\n')

if __name__=='__main__':unittest.main(verbosity=2)
