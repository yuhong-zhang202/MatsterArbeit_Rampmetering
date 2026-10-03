import importlib.util,unittest
from pathlib import Path
p=Path(__file__).parents[1]/'scripts/stage6/standard_metering_analysis_20261003/guard.py';s=importlib.util.spec_from_file_location('guard',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class TestGuard(unittest.TestCase):
 def fixture(self):
  rows=[]
  for t in range(600,4200):
   n=t>=603;before=min((t-600)/4,1);after=min((t-599)/4,1);dropped=max(0,(t-599)/4-1)
   rows.append(dict(time_begin_s=t,command_rate_veh_h=900,credit_before=before,credit_after=after,dropped_credit_total=dropped,guard_vehicle_states_json='[]',front_queued_vehicle_id='',queue_vehicle_count=0,guard_failed_follower_ids_json='[]',guard_reason='NO_FRONT' if n else 'NOT_DUE_OR_MIN_RED',guard_allowed=False,nominal_slot_scheduled=n,slot_scheduled=False,guard_rejected_slot=n,credit_deferred=n,observed_state='r',crossing_bracket_ids_json='[]'))
  return rows
 def test_no_front_retains_one_credit_no_burst(self):
  z=a.audit(self.fixture(),204.49);self.assertEqual(z['counts']['actual_slots'],0);self.assertEqual(z['dropped_credit'],899)
 def test_tampered_allow_fails(self):
  rows=self.fixture();rows[3]['guard_allowed']=True
  with self.assertRaisesRegex(ValueError,'reason'):a.audit(rows,204.49)
if __name__=='__main__':unittest.main()
