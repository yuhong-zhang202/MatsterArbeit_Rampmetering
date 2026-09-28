import unittest,json,tempfile,sys,hashlib
from pathlib import Path
from decimal import Decimal as D
import measurement_helpers as m
B=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def setUp(self):self.path,self.stop=m.r_path_map(B/'build_attempts/TV_BUILD01/network.net.xml')
 def v(self,id,cls,lane,pos,speed='0',length='5'):return dict(id=id,**{'class':cls},lane=lane,pos=pos,speed=speed,length=length)
 def test_storage_exact(self):self.assertEqual(self.stop,D('317.57'))
 def test_internal_connector_mapping(self):self.assertEqual(m.locate({'lane':':urban_diverge_1_0','pos':'50'},self.path),D(50))
 def test_meter_internal_crossing(self):
  a=dict(lane='ramp_storage_0',pos='204',time=5);b=dict(lane=':ramp_mid_0_0',pos='3',time=6)
  self.assertEqual(m.crossing_bracket(a,b,self.path,self.stop)['status'],'crossing_bracket')
 def test_exact_boundary_ambiguous(self):
  a=dict(lane='ramp_storage_0',pos='204.49',time=5);b=dict(lane=':ramp_mid_0_0',pos='3',time=6)
  self.assertTrue(m.crossing_bracket(a,b,self.path,self.stop)['boundary_equality_possible'])
 def test_missing_frame(self):self.assertEqual(m.crossing_bracket(dict(lane='ramp_storage_0',pos=200,time=5),dict(lane=':ramp_mid_0_0',pos=3,time=7),self.path,self.stop)['status'],'sampling_gap')
 def test_unknown_lane_not_zero(self):self.assertEqual(m.crossing_bracket(dict(lane='main_up_0',pos=1,time=5),dict(lane='ramp_storage_0',pos=1,time=6),self.path,self.stop)['status'],'position_unknown')
 def chain(self):
  rows=[]
  for i in range(33):
   p=self.stop-D(2)-i*10
   lane=next(k for k,v in self.path.items() if v['start']<=p<v['start']+v['length']);pos=p-self.path[lane]['start']
   rows.append(self.v('R'+str(i),'R',lane,str(pos)))
  # Reclassify the penultimate shared vehicle as U without deleting it.
  rows[-2]['class']='U';rows[-2]['id']='U0';return rows
 def test_mixed_chain_preserved(self):
  q=m.frame_queue(self.chain(),self.path,self.stop);self.assertIn('U0',q['members']);self.assertTrue(q['storage_cross_observed']);self.assertIn('U0',q['U_blocking_candidate'])
 def test_moving_intervening_U_breaks_chain(self):
  rows=self.chain();rows[-2]['speed']='1';q=m.frame_queue(rows,self.path,self.stop);self.assertNotIn(rows[-1]['id'],q['members'])
 def test_exact_anchor10(self):self.assertEqual(m.frame_queue([self.v('R','R','ramp_storage_0','194.49')],self.path,self.stop)['anchor_distance_m'],'10.00')
 def test_outside_anchor(self):self.assertTrue(m.frame_queue([self.v('R','R','ramp_storage_0','194.48')],self.path,self.stop)['junction_blocking_candidate'])
 def test_speed_boundary_excluded(self):self.assertEqual(m.frame_queue([self.v('R','R','ramp_storage_0','203','.1')],self.path,self.stop)['members'],[])
 def test_gap10_included(self):self.assertEqual(len(m.frame_queue([self.v('R1','R','ramp_storage_0','203'),self.v('R2','R','ramp_storage_0','188')],self.path,self.stop)['members']),2)
 def test_gap_above10_excluded(self):self.assertEqual(len(m.frame_queue([self.v('R1','R','ramp_storage_0','203'),self.v('R2','R','ramp_storage_0','187.99')],self.path,self.stop)['members']),1)
 def test_identity_all_states(self):self.assertEqual(m.identity_account(['a','b','c'],[dict(id='a',depart=-1,arrival=-1),dict(id='b',depart=1,arrival=-1),dict(id='c',depart=1,arrival=2)]),dict(undeparted=1,unfinished=1,arrived=1))
 def test_identity_missing_rejected(self):
  with self.assertRaises(ValueError):m.identity_account(['a'],[])
 def test_identity_duplicate_rejected(self):
  with self.assertRaises(ValueError):m.identity_account(['a'],[dict(id='a',depart=-1,arrival=-1)]*2)
 def test_temporal_overlap(self):self.assertEqual(m.interval_order((1,2),(2,3)),'temporal_order_unidentified')
 def test_neutrality_ignores_only_timing_comments(self):
  with tempfile.TemporaryDirectory(dir=B) as d:
   a=Path(d)/'a';b=Path(d)/'b';a.write_text('<summary><!--date--><step time="0" duration="1" speed="4"/></summary>');b.write_text('<summary>\n<step speed="4" duration="9" time="0"/></summary>');self.assertEqual(m.normalized_xml_digest(a),m.normalized_xml_digest(b));b.write_text('<summary><step speed="5" duration="9" time="0"/></summary>');self.assertNotEqual(m.normalized_xml_digest(a),m.normalized_xml_digest(b))
if __name__=='__main__':
 with (B/'measurement_tests.log').open('x') as f:r=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 receipt=dict(status='PASS' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),SUMO_starts=0,source_sha256=hashlib.sha256((B/'measurement_helpers.py').read_bytes()).hexdigest())
 with (B/'measurement_test_receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
 print(receipt);sys.exit(not r.wasSuccessful())
