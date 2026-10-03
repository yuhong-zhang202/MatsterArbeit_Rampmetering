import importlib.util,unittest
from pathlib import Path
p=Path(__file__).parents[1]/'scripts/stage6/standard_metering_analysis_20261003/chain.py';s=importlib.util.spec_from_file_location('chain',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class TestChain(unittest.TestCase):
 def setUp(self):self.l={'shared_approach_0':20,':urban_diverge_1_0':10,'ramp_storage_0':20}
 def v(self,id,lane,pos,speed=0):return dict(id=id,lane=lane,pos=pos,speed=speed)
 def test_internal_body_continuity(self):
  vs=[self.v('R_0','ramp_storage_0',18),self.v('R_1','ramp_storage_0',4),self.v('R_2',':urban_diverge_1_0',0)]
  r=a.snapshot(vs,self.l,50,{v['id']:5 for v in vs});self.assertTrue(r['shared_reached']);self.assertEqual(r['max_gap_m'],9)
 def test_fast_intermediate_breaks(self):
  vs=[self.v('R_0','ramp_storage_0',18),self.v('R_1','ramp_storage_0',4,2),self.v('R_2',':urban_diverge_1_0',0)]
  r=a.snapshot(vs,self.l,50,{v['id']:5 for v in vs});self.assertEqual(r['chain_ids'],['R_0'])
 def test_overlap_anomaly(self):
  vs=[self.v('R_0','ramp_storage_0',18),self.v('R_1','ramp_storage_0',17)]
  self.assertTrue(a.snapshot(vs,self.l,50,{v['id']:5 for v in vs})['geometry_anomalies'])
 def test_global_cross_window_member_changes(self):
  rows=[dict(time=t,shared_reached=10<=t<45,geometry_anomalies=[],chain_ids=[str(t)]) for t in range(60)]
  self.assertEqual(a.episodes(rows),[dict(begin=10,end=45,duration_s=35)])
if __name__=='__main__':unittest.main()
