"""Second review: lifecycle and preserved hard-cause evidence only."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/thesis_actuator_readiness_20261015_v1/review_round2_v1'
BASE=ROOT/'artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles'
OLD=ROOT/'data/processed/thesis_actuator_readiness_20261015_v1/pr13_reader_p2_fix_v1'

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
natural=load(ROOT/'scripts/natural_service_audit_20261015_v1/actual.py','natural')
finite=load(ROOT/'scripts/pr13_service_scope_audit_20261015/audit.py','finite')


def hard_v2():
    target=OUT/'FINITE_LATER_HARD_V2.json'
    if target.exists():return json.loads(target.read_text())
    scope=load(ROOT/'tests/candidate_a_service_scope_20261015/test_scope.py','scopev2')
    original=scope.fixture.World
    def factory(*args,**kw):
        w=original(*args,**kw);w.vehicle.getAcceleration=lambda vid:-5. if w.time==1212 and vid.startswith('M') else 0.;return w
    with patch.object(scope.fixture,'World',side_effect=factory):
        w,a,error,r,events=scope.ScopeTests().run_fixture('two',1212)
    assert error is not None
    keys=('time_begin_s','time_end_s','observed_time_s','accounting_complete','accounting','actual_crossings','post_world','status','reasons','terminal_reason')
    d=dict(receipt=r,events=events,acks=[{k:v for k,v in row.items() if k in keys} for row in a.receipts if row.get('time_begin_s',-1)>=1200],world_time=w.time,setters=w.requests,provenance='NEW_V2_EXISTING_FINITE_TWO_FIXTURE_FINAL1212_M_ACCELERATION_MINUS5_REAL_LOOP_REASONS_RETAINED_NOT_NATIVE')
    finite.dump(target,d)
    return d


class RoundTwoTests(unittest.TestCase):
    def test_lifecycle_saved_cases_and_hard_cause(self):
        results={};checks={}
        for name in ('empty_none_641','supply_none_641','late_none_641','blocked_none_641','blocked_none_640'):
            with self.subTest(case=name):results[name]=natural.audit(natural.read_bundle(BASE/name))
        base=natural.read_bundle(BASE/'blocked_none_641')
        mutations=[
            ('superseded_to_ACK',lambda d:d['receipt']['command_records']['initial'].update(status='ACK_OBSERVED')),
            ('missing_superseded',lambda d:d['files'].update({'command_events.jsonl':[e for e in d['files']['command_events.jsonl'] if e['event']!='SUPERSEDED']})),
            ('nested_command_mismatch',lambda d:d['receipt']['command_records']['feedback:630']['command'].update(rate_veh_h=300)),
            ('first_preparation_mismatch',lambda d:d['receipt']['command_records']['feedback:630'].update(first_preparation_s=630)),
            ('missing_preparation',lambda d:d['files'].update({'command_events.jsonl':[e for e in d['files']['command_events.jsonl'] if e['event']!='PREPARED_NOT_OBSERVED']})),
            ('packet_ACK_request',lambda d:next(e for e in d['files']['command_events.jsonl'] if e['event']=='PACKET_ACK_OBSERVED').update(request_id='initial')),
            ('cycle_application_delay',lambda d:d['receipt']['cycles'][0].update(application_delay_s=999)),
            ('held_history_application_time',lambda d:d['receipt']['cycles'][1].update(command_applied_s=None)),
            ('cycle_request_time',lambda d:d['receipt']['cycles'][0].update(command_requested_s=599)),
            ('superseded_nested_command',lambda d:next(e for e in d['files']['command_events.jsonl'] if e['event']=='SUPERSEDED')['command'].update(origin='PROJECT_FEEDBACK')),
        ]
        for name,mutate in mutations:
            d=deepcopy(base);mutate(d)
            with self.subTest(reject=name),self.assertRaises(ValueError):natural.audit(d)
            checks[name]='REJECTED'
        d=hard_v2();results['finite_hard_v2']=finite.audit(d)
        for name,mutate in [
            ('unrelated_hard_error',lambda x:x['receipt'].update(error='DiagnosticStop:UNRELATED_CAUSE')),
            ('missing_hard_reasons',lambda x:x['acks'][-1].pop('reasons')),
            ('corrupt_terminal_reason',lambda x:x['acks'][-1].update(terminal_reason='DiagnosticStop:WRONG')),
        ]:
            x=deepcopy(d);mutate(x)
            with self.subTest(reject=name),self.assertRaises(ValueError):finite.audit(x)
            checks[name]='REJECTED'
        results['quota_special_path']=finite.audit(json.loads((OLD/'overquota.json').read_text()))
        q=json.loads((OLD/'overquota.json').read_text());q['receipt']['error']='ValueError:UNRELATED_CAUSE'
        with self.assertRaises(ValueError):finite.audit(q)
        checks['unrelated_quota_error']='REJECTED'
        for path in [OLD/'later_hard.json',ROOT/'data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1/safety_priority.json']:
            with self.subTest(legacy=path.name),self.assertRaisesRegex(ValueError,'MISSING_HARD_CAUSE_EVIDENCE'):finite.audit(json.loads(path.read_text()))
        finite.dump(OUT/'RESULT_V2.json',dict(status='PASS_OFFLINE_REVIEW_FIX_INTEGRITY_ONLY',cases=results,rejections=checks,legacy_missing_cause='NOT_CERTIFIED_NOT_BACKFILLED',native_started=False))

if __name__=='__main__':unittest.main(verbosity=2)
