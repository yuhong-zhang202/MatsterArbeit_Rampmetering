"""Two review defects only: synthetic reader integrity, no native evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/thesis_actuator_readiness_20261015_v1/pr13_reader_p2_fix_v1'
OLD=ROOT/'data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1'

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
reader=load(ROOT/'scripts/pr13_service_scope_audit_20261015/audit.py','reader')
scope=load(ROOT/'tests/candidate_a_service_scope_20261015/test_scope.py','scope')


def overquota():
    # Arithmetic ledger generation plus explicit synthetic ACK rebinding of
    # saved one-car template, not native movement or a three-car adapter test.
    d=json.loads((OLD/'one_exact.json').read_text())
    q=scope.Ledger(750,1210,purpose=scope.PURPOSE)
    scope.ScopeTests().finish_packet(q,3)
    ev=q.assess_completed_packet()
    try:q.require_diagnostic_target()
    except ValueError as exc:error=type(exc).__name__+':'+str(exc)
    ev['service_context']=deepcopy(d['receipt']['service_diagnostic']['service_context'])
    for ack in d['acks']:
        # Three distinct same-interval synthetic crossings and observed IDs.
        if ack['time_begin_s']==1200:
            first=ack['actual_crossings'][0]
            ack['actual_crossings']=[dict(first,vehicle_id=f'synthetic.quota.{i}') for i in range(3)]
        ack['post_world'].update({f'synthetic.quota.{i}':dict(role='R',speed_m_s=0,lane_id=':ramp_mid_0_0') for i in range(3)})
        a=ack['accounting'];a['N']=3
        a['nominal_minus_actual']=a['E']-3;a['requested_minus_actual']=float(scope.Fraction(a['C_exact_fraction'])-3)
    d['acks'][-1]['status']='STOP_OBSERVED_AFTER_STEP'
    d['events']=[e for e in d['events'] if e['event']!='FINITE_PACKET_DIAGNOSTIC_ASSESSED']+[ev]
    d['receipt'].update(status='HARD_OR_UNKNOWN_GATE_STOP',error=error,service_diagnostic=ev)
    d['receipt']['accounting'].update(q.accounting())
    d['receipt']['accounting']['diagnostic_target_status']=ev['status']
    d['provenance']='PURE_LEDGER_OVERQUOTA_EXCEPTION_PLUS_EXPLICIT_SYNTHETIC_ACK_REBINDING_NOT_NATIVE_OR_ADAPTER_MOVEMENT'
    return d


def later_hard():
    original=scope.fixture.World
    def world(*args,**kwargs):
        w=original(*args,**kwargs)
        w.vehicle.getAcceleration=lambda vid:-5. if w.time==1212 and vid.startswith('M') else 0.
        return w
    with patch.object(scope.fixture,'World',side_effect=world):
        w,a,error,r,events=scope.ScopeTests().run_fixture('two',1212)
    assert error is not None
    keys=('time_begin_s','time_end_s','observed_time_s','accounting_complete','accounting','actual_crossings','post_world','status')
    return dict(receipt=r,events=events,acks=[{k:v for k,v in ack.items() if k in keys} for ack in a.receipts if ack.get('time_begin_s',-1)>=1200],world_time=w.time,setters=w.requests,provenance='EXISTING_TWO_FIXTURE_REAL_NEW_FINITE_LOOP_FINAL1212_FAKE_M_ACCELERATION_MINUS5_AFTER_PRIOR_GOOD_PACKET')


class ReaderReviewTests(unittest.TestCase):
    def test_two_p2_regressions_and_unchanged_saved_cases(self):
        old=load(OUT/'READER_6DC_PREIMAGE.py','oldreader')
        results={}
        for label,d in [(name,json.loads((OUT/(name+'.json')).read_text()) if (OUT/(name+'.json')).exists() else make()) for name,make in [('overquota',overquota),('later_hard',later_hard)]]:
            with self.subTest(label=label):
                with self.assertRaises(ValueError):old.audit(d)
                results[label]=reader.audit(d)
                self.assertEqual(results[label]['diagnostic_outcome'],'HARD_OR_UNKNOWN_GATE_STOP')
                if not (OUT/(label+'.json')).exists():reader.dump(OUT/(label+'.json'),d)
        for label in ('empty','one_exact','partial','safety_priority'):
            results[label]=reader.audit(json.loads((OLD/(label+'.json')).read_text()))
        checks={}
        for label,mutate in [
            ('false_quota_pass',lambda d:d['events'][-1].update(status='FINITE_DIAGNOSTIC_TARGET_OBSERVED_NOT_GENERAL_QUALIFICATION')),
            ('quota_without_hard',lambda d:d['receipt'].update(status='FINITE_LOOP_COMPLETED_NOT_GENERAL_QUALIFICATION',error=None)),
            ('misbound_quota',lambda d:d['events'][-1].update(end_s=1209)),
            ('malformed_quota',lambda d:d['acks'][-1].update(time_end_s=1211)),
        ]:
            d=overquota();mutate(d)
            with self.subTest(reject=label),self.assertRaises(ValueError):reader.audit(d)
            checks[label]='REJECTED'
        d=json.loads((OUT/'later_hard.json').read_text())
        # Current partial cannot gain a neutral completed assessment to mask
        # an actual safety stop; terminal binding/completeness must reject it.
        ev=deepcopy(next(e for e in d['events'] if e['event']=='FINITE_PACKET_DIAGNOSTIC_ASSESSED'));ev.update(cycle_id=1,status=scope.UNDER_TARGET,end_s=1212)
        d['events'].append(ev);d['receipt']['service_diagnostic']=ev
        with self.assertRaises(ValueError):reader.audit(d)
        checks['current_neutral_masks_safety']='REJECTED'
        reader.dump(OUT/'RESULT_V1.json',dict(status='PASS_SYNTHETIC_READER_INTEGRITY_ONLY',cases=results,rejections=checks,old_reader_regression_failures=2,native_started=False))

if __name__=='__main__':unittest.main(verbosity=2)
