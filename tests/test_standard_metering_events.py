import importlib.util,unittest
from pathlib import Path
p=Path(__file__).parents[1]/'scripts/stage6/standard_metering_analysis_20261003/events.py';s=importlib.util.spec_from_file_location('events',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class TestEvents(unittest.TestCase):
 def rows(self,seq):return [dict(step_end_s=t,detector_id='d',events=ev) for t,ev in seq]
 def test_early_and_cross_window_no_duplicate(self):
  rows=self.rows([(601,[('v',5,599,-1,'car')]),(602,[('v',5,599,-1,'car')]),(603,[('v',5,599,602.5,'car')]),(604,[])])
  rr=a.reconstruct(rows,['d'],600,604,2)
  self.assertEqual([r['occupancy_pct'] for r in rr],[100,25])
 def test_sum_overlap_not_time_union(self):
  rr=a.reconstruct(self.rows([(601,[('a',5,600,601,'car'),('b',5,600.5,601,'car')])]),['d'],600,601,1)
  self.assertEqual(rr[0]['occupancy_pct'],150)
 def test_empty_is_valid_missing_not_zero(self):
  self.assertEqual(a.reconstruct(self.rows([(601,[])]),['d'],600,601,1)[0]['occupancy_pct'],0)
  with self.assertRaises(ValueError):a.reconstruct([],['d'],600,601,1)
 def test_disappeared_ongoing(self):
  with self.assertRaisesRegex(ValueError,'disappeared'):a.reconstruct(self.rows([(601,[('a',5,600,-1,'car')]),(602,[])]),['d'],600,602,2)
 def test_duplicate_and_conflict(self):
  ev=('a',5,600,601,'car')
  with self.assertRaisesRegex(ValueError,'duplicate event'):a.reconstruct(self.rows([(601,[ev,ev])]),['d'],600,601,1)
  with self.assertRaisesRegex(ValueError,'completed event'):a.reconstruct(self.rows([(601,[ev]),(602,[('a',5,600,601.5,'car')])]),['d'],600,602,2)
if __name__=='__main__':unittest.main()
