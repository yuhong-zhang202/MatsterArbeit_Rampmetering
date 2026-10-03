import importlib.util,tempfile,unittest
from pathlib import Path
P=Path(__file__).parents[1]/'scripts/stage6/standard_metering_analysis_20261003/analysis.py'
s=importlib.util.spec_from_file_location('meter_analysis',P);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class TestMeterAnalysis(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def xml(self,name,text):p=self.root/name;p.write_text(text);return p
 def test_comments_attribute_order_and_cutoff(self):
  left=self.xml('a.xml','<x><!--a--><timestep time="599"><vehicle id="M_0" speed="2"/></timestep><timestep time="600"/></x>')
  right=self.xml('b.xml','<x><!--b--><timestep time="599"><vehicle speed="2" id="M_0"/></timestep><timestep time="600"><vehicle id="M_0"/></timestep></x>')
  self.assertTrue(a.pre600(left,right)['equal']);self.assertFalse(a.compare_records(left,right,'timestep')['equal'])
 def test_only_summary_compute_duration_ignored(self):
  x=self.xml('a.xml','<x><step time="0" duration="1"/><tripinfo id="M_0" duration="10"/></x>')
  y=self.xml('b.xml','<x><step time="0" duration="2"/><tripinfo id="M_0" duration="11"/></x>')
  self.assertTrue(a.compare_records(x,y,'step',ignored_attributes=('duration',))['equal'])
  self.assertFalse(a.compare_records(x,y,'tripinfo')['equal'])
 def test_missing_tail_not_equal(self):
  x=self.xml('a.xml','<x><step time="0"/><step time="1"/></x>');y=self.xml('b.xml','<x><step time="0"/></x>')
  self.assertEqual(a.compare_records(x,y,'step')['different_records'],1)
 def test_censoring_keeps_uninserted(self):
  d={'M_0':{'class':'M','scheduled':0},'R_0':{'class':'R','scheduled':1}}
  tr={'M_0':dict(depart=0,arrival=-1,departDelay=0,duration=3,timeLoss=1,waitingTime=1)}
  f={'ids':{'M_0':dict(first=0,last=2,n=3)},'events':{}}
  rows,_,_,_=a.boundary.lifecycle(d,tr,f,{'horizon':3,'step':1,'bin_seconds':1})
  self.assertEqual(sum(r['scheduled_system_time_observed_s'] for r in rows),5)
  self.assertEqual(rows[1]['status'],'undeparted');self.assertEqual(rows[1]['external_wait_observed_s'],2)
 def test_city_internal_and_green_nearest(self):
  f=self.xml('f.xml','<x><timestep time="0"><vehicle id="U_0" lane=":urban_diverge_0_0" pos="2" speed="0"/><vehicle id="R_0" lane=":urban_diverge_0_0" pos="8" speed="1"/></timestep></x>')
  t=self.xml('t.xml','<x><tlsState time="0" id="urban_tls" state="Gr"/><tlsState time="0" id="ramp_mid" state="r"/></x>')
  z=a.city_evidence(f,t,1);r=z['all_U_slow_context'][0]
  self.assertTrue(r['urban_entry_green']);self.assertEqual(r['ahead_id'],'R_0');self.assertEqual(r['front_position_separation_m'],6)
  self.assertEqual(next(x for x in z['lane_bins'] if x['vehicle_class']=='U')['stop_lt0p1_vehicle_seconds'],1)
 def test_missing_tls_reject(self):
  f=self.xml('f.xml','<x><timestep time="0"/></x>');t=self.xml('t.xml','<x/>')
  with self.assertRaises(ValueError):a.city_evidence(f,t,1)
 def test_noop_log_coverage_and_no_updates(self):
  import csv
  fields=['time_begin_s','time_end_s','mode','observed_state','requested_state','crossing_bracket_ids_json','red_crossing_bracket_ids_json']
  with (self.root/'controller_steps.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for t in range(4200):w.writerow(dict(zip(fields,[t,t+1,'NOOP','G','','[]','[]'])))
  fields=['decision_time_s','application_time_s','interval_begin_s','interval_end_s','valid','rate_previous_veh_h','rate_raw_veh_h','rate_clipped_veh_h']
  with (self.root/'feedback_updates.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(dict(zip(fields,[630,630,600,630,True,'','',''])))
  self.assertEqual(a.audit_control_logs(self.root,'NOOP')['updates'],1)
  (self.root/'feedback_updates.csv').write_text('decision_time_s\n')
  with self.assertRaisesRegex(ValueError,'count'):a.audit_control_logs(self.root,'NOOP')
 def test_feedback_xml_wrong_value_rejected(self):
  import csv
  fields=['interval_begin_s','interval_end_s','detector_l0','detector_l1','occ_l0_pct','occ_l1_pct','occ_mean_pct','n_vehicle_l0','n_vehicle_l1']
  with (self.root/'feedback_updates.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(dict(zip(fields,[600,630,'d0','d1',11.004,12,11.502,2,3])))
  for lane,occ,n in [(0,11,2),(1,12,3)]:
   self.xml(f'p1_main_down_20_l{lane}.xml',f'<x><interval id="d{lane}" begin="600" end="630" occupancy="{occ}" nVehContrib="{n}"/></x>')
  self.assertEqual(a.reconcile_feedback_xml(self.root)['checked_lane_intervals'],2)
  self.xml('p1_main_down_20_l0.xml','<x><interval id="d0" begin="600" end="630" occupancy="10" nVehContrib="2"/></x>')
  with self.assertRaisesRegex(ValueError,'occupancy mismatch'):a.reconcile_feedback_xml(self.root)
 def test_current_receipt_files_hash_enforced(self):
  import json
  p=self.root/'output.txt';p.write_text('raw')
  (self.root/'execution_receipt.json').write_text(json.dumps(dict(status='COMPLETED',return_code=0,files={'output.txt':dict(bytes=p.stat().st_size,sha256=a.sha(p))})))
  self.assertIn('output_manifest',a.validate_current_receipt(self.root))
  p.write_text('bad')
  with self.assertRaisesRegex(ValueError,'hash'):a.validate_current_receipt(self.root)
 def test_rolling_half_open_and_no_zero_fill(self):
  rows=[dict(time_begin_s=t,time_end_s=t+1,occ_l0_pct=t-600,occ_l1_pct=0) for t in range(600,630)]
  self.assertAlmostEqual(a.mean_step_window(rows,630)[0],14.5)
  for bad in [rows[:-1],rows[1:]+[dict(rows[-1],time_begin_s=630,time_end_s=631)],rows[:-1]+[rows[-2]]]:
   with self.assertRaises(ValueError):a.mean_step_window(bad,630)
  rows[0]['occ_l0_pct']=''
  with self.assertRaises(ValueError):a.mean_step_window(rows,630)
 def test_all119_step_feedback_identity(self):
  import csv
  with (self.root/'detector_step_occupancy.csv').open('w') as f:
   fields=['time_begin_s','time_end_s','detector_l0','detector_l1','occ_l0_pct','occ_l1_pct'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for t in range(600,4170):w.writerow(dict(zip(fields,[t,t+1,'d0','d1',11,12])))
  with (self.root/'feedback_updates.csv').open('w') as f:
   fields=['decision_time_s','occupancy_source','sample_count','detector_l0','detector_l1','occ_l0_pct','occ_l1_pct'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for t in range(630,4171,30):w.writerow(dict(zip(fields,[t,'mean_last_step_30',30,'d0','d1',11,12])))
  self.assertEqual(a.reconcile_step_feedback(self.root)['lane_windows'],238)
  p=self.root/'detector_step_occupancy.csv';p.write_text(p.read_text().replace('600,601,','601,602,',1))
  with self.assertRaisesRegex(ValueError,'missing/duplicate'):a.reconcile_step_feedback(self.root)
if __name__=='__main__':unittest.main()
