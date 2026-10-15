"""Final bounded pending-field fix: read five saved bundles, two corruptions."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/thesis_actuator_readiness_20261015_v1/final_pending_fix_v1'
BASE=ROOT/'artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles'
s=importlib.util.spec_from_file_location('pending_reader',ROOT/'scripts/natural_service_audit_20261015_v1/actual.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class PendingFieldTests(unittest.TestCase):
    def test_saved_cases_and_two_pending_corruptions(self):
        results={}
        for name in ('empty_none_641','supply_none_641','late_none_641','blocked_none_641','blocked_none_640'):
            with self.subTest(case=name):results[name]=m.audit(m.read_bundle(BASE/name))
        base=m.read_bundle(BASE/'blocked_none_641');rejected={}
        for key,value in [('pending_request_id','NONEXISTENT'),('r_policy_pending_veh_h',900)]:
            d=deepcopy(base);next(r for r in d['files']['post_steps.jsonl'] if r.get('time_begin_s')==630)['rate_chain'][key]=value
            with self.subTest(field=key),self.assertRaisesRegex(ValueError,'pending request not latest'):m.audit(d)
            rejected[key]='REJECTED'
        result=dict(status='PASS_OFFLINE_PENDING_FIELD_BINDING_ONLY',cases=results,rejections=rejected,native_started=False)
        # Keep previous receipts immutable when this read-only regression is rerun.
        if not (OUT/'RESULT_V1.json').exists():
            with (OUT/'RESULT_V1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')

if __name__=='__main__':unittest.main(verbosity=2)
