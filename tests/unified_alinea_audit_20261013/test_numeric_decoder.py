import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.unified_alinea_audit_20261013_v1.numeric_event_audit import validate_formula
class NumericDataTests(unittest.TestCase):
    def test_known_values_with_synthetic_binding_and_unknown_rejection(self):
        f=json.loads((ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/numerical_exception_v1/OFFLINE_REAL_VALUE_FIXTURE_V1.json').read_text());e=f['evidence'];a=f['authority'];r=validate_formula(e,a);self.assertEqual(r['actual_delta_v_m_s2'],-4.501);self.assertTrue(r['legacy_strict_FAIL']);self.assertFalse(r['private_branch_observed'])
        for mutation in ('phase','coverage','alpha','other_alarm','stronger'):
            q=copy.deepcopy(e)
            if mutation=='phase':q['actual_phase']=True
            elif mutation=='coverage':q['body_coverage_complete']=False
            elif mutation=='alpha':q['actual_native_acceleration_m_s2']=-4.5
            elif mutation=='other_alarm':q['native_event_counters']['colliding_vehicles']=1
            else:q['after']['speed_m_s']-=.001;q['after']['position_m']-=.001;q['recorded_delta_v_m_s2']=-4.502;q['actual_native_acceleration_m_s2']=-4.502
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):validate_formula(q,a)
if __name__=='__main__':unittest.main()
