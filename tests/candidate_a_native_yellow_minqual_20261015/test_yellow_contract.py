"""Bounded synthetic gate/helper checks, never future vehicle safety evidence."""
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace as NS
from unittest.mock import patch
import copy,json,tempfile,time,unittest
from src.candidate_a_native_yellow_minqual_20261015 import bridge
from src.candidate_a_native_yellow_minqual_20261015.yellow_contract import annotate_yellow_scope,require_contract,POLICY
from src.candidate_a_native_yellow_minqual_20261015.adapter import StepAdapter,inventory,STORAGE,INGRESS,INTERNAL
from src.candidate_a_cumulative_full_catalogue_20261014.policy import yellow_scope,Ledger
from src.candidate_a_qualification_20261008.safety import Vehicle
from tests.candidate_a_dynamic_minqual_20261015.test_minqual import Frame

def subject():
 return Vehicle('R_flow.5','storage',204.3438399856509,4.973246721802868,5.,2.5,2.6,4.5,1.,1.,'technical_passenger')

class YellowTests(unittest.TestCase):
 def test_bound_legacy_failure_strict_default_typed_mode_and_missing_fields(self):
  v=subject();raw=yellow_scope([v],1236,2);saved=copy.deepcopy(raw)
  strict=annotate_yellow_scope(raw,[v],1236,2);allowed=annotate_yellow_scope(raw,[v],1236,2,True)
  self.assertEqual(raw,saved);self.assertEqual(raw['status'],'UNKNOWN');self.assertIs(allowed['rows'],raw['rows'])
  self.assertFalse(strict['diagnostic_yellow_contract']['allow_prepared_step']);d=allowed['diagnostic_yellow_contract']
  self.assertTrue(d['allow_prepared_step']);self.assertFalse(d['witness_established']);self.assertEqual(d['interpretation'],'DIAGNOSTIC_WITNESS_NOT_ESTABLISHED');self.assertIsNone(d['safety_certified'])
  for mode in (1,1.0,None,'true'):
   with self.subTest(mode=mode),self.assertRaises(ValueError):annotate_yellow_scope(raw,[v],1236,2,mode)
   with self.subTest(contract_mode=mode),self.assertRaises(ValueError):require_contract({'policy':POLICY,'enabled':mode})
   with self.subTest(adapter_mode=mode),self.assertRaises(ValueError):StepAdapter(lambda c:None,yellow_diagnostic_mode=mode)
  for fault in ('missing_status','wrong_ID','stale_time','row_bool_int','false_clear_PASS'):
   bad=copy.deepcopy(raw)
   if fault=='missing_status':bad.pop('status')
   elif fault=='wrong_ID':bad['covered_ids']=['R_flow.foreign']
   elif fault=='stale_time':bad['time_s']=1235
   elif fault=='row_bool_int':bad['rows'][0]['stop_possible']=0
   else:bad['rows'][0]['clear_possible']=True;bad['status']='PASS'
   with self.subTest(fault=fault),self.assertRaises((ValueError,KeyError)):annotate_yellow_scope(bad,[v],1236,2,True)
  with self.assertRaises(ValueError):annotate_yellow_scope(raw,[replace(v,speed_m_s=float('nan'))],1236,2,True)

 def make_frame_adapter(self,t,quota=False,enabled=True):
  w=Frame();w.time=t;v=subject();oldpos=w.vehicle.getLanePosition;oldspeed=w.vehicle.getSpeed
  w.vehicle.getLanePosition=lambda x:v.position_m if x==v.vehicle_id else oldpos(x)
  w.vehicle.getSpeed=lambda x:v.speed_m_s if x==v.vehicle_id else oldspeed(x)
  w.vehicle.getAcceleration=lambda x:0.
  w.phase=0;w.state='G';w.switch=1204;w.program='I12_PACKET8'
  w.trafficlight.getProgram=lambda tls:w.program;w.trafficlight.getPhase=lambda tls:w.phase
  w.trafficlight.getRedYellowGreenState=lambda tls:w.state;w.trafficlight.getNextSwitch=lambda tls:w.switch
  def setphase(tls,p):
   self.assertEqual(p,1);w.phase=1;w.state='y';w.switch=w.time+2
  w.trafficlight.setPhase=setphase
  def observe(c):return [v],{STORAGE:(v.vehicle_id,),INGRESS:(),INTERNAL:('R_flow.4',)}, {'R_flow.4':{}},dict(available=True)
  a=StepAdapter(observe,900,1296,yellow_diagnostic_mode=enabled)
  # Synthetic already-observed packet entries exercise the real helper seam;
  # these IDs/positions are not a microscopic simulation or service sample.
  for s in range(1200,t):
   a.ledger.begin_step(s)
   if s==1200:a.ledger.mark_cycle_start(True)
   a.ledger.end_step(s+1,['SYNTHETIC.entry0','SYNTHETIC.entry1'] if quota and s==1200 else [],'G')
  a.ledger.begin_step(t);a.last_end=t;a.last_completed=t;a.previous_motion='G'
  a.receipts=[{'time_end_s':t,'post_world':inventory(w)[0],'status':'RECONCILED_DIAGNOSTIC_ONLY'}]
  return w,a

 def test_real_quota_and_deadline_prepare_definitive_journals_and_strict_stop(self):
  worker=bridge.protected_worker()
  for quota,t in ((True,1201),(False,1204)):
   with self.subTest(quota=quota),tempfile.TemporaryDirectory() as tmp:
    out=Path(tmp);w,a=self.make_frame_adapter(t,quota)
    if quota:bridge.policy_after_ack(w,a,worker,out)
    a.prepare_step(w,t);bridge.write_first_yellow_screen(a,t,out)
    rows=[json.loads(x) for x in (out/'yellow_scope.jsonl').read_text().splitlines()]
    self.assertEqual(len(rows),1);self.assertEqual(rows[0]['status'],'UNKNOWN');self.assertFalse(rows[0]['observed_first_Y'])
    self.assertTrue(rows[0]['diagnostic_yellow_contract']['enabled']);self.assertEqual(a.pending['motion'],'y')
    self.assertEqual(a.ledger.cycle['green_end_reason'],'ACTUAL_QUOTA_ACK' if quota else 'MAX_GREEN_DEADLINE')
    if quota:
     attempts=[json.loads(x) for x in (out/'yellow_scope_attempts.jsonl').read_text().splitlines()]
     self.assertEqual(len(attempts),1);self.assertEqual(attempts[0]['status'],'UNKNOWN');self.assertEqual(w.phase,1)
  for quota,t in ((True,1201),(False,1204)):
   with self.subTest(strict_quota=quota),tempfile.TemporaryDirectory() as tmp:
    w,a=self.make_frame_adapter(t,quota,enabled=False)
    with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):
     if quota:bridge.policy_after_ack(w,a,worker,Path(tmp))
     else:a.prepare_step(w,t)
    self.assertEqual(w.phase,0)

 def test_other_stop_keeps_original_exception_and_durable_events(self):
  v=subject();scope=annotate_yellow_scope(yellow_scope([v],1236,2),[v],1236,2,True)
  original=ValueError('COLLISION_OR_TELEPORT');conn=NS(simulation=NS(),clock=0,stats={},trafficlight=NS());conn.simulation.getTime=lambda:conn.clock;targets=[]
  def step(t):targets.append(t);conn.clock=t
  conn.simulationStep=step
  a=NS(end_s=2,ledger=Ledger(900,1208),pending=None,receipts=[],last_completed=None,last_end=None,last_yellow_scope=None)
  def prepare(c,t):a.pending={'motion':'G'};a.ledger.begin_step(1200);a.ledger.mark_cycle_start(True);return {'classification':'SYNTHETIC_LOGGING_CLOCK_OFFSET'}
  def reconcile(c,warning):
   a.ledger.end_step(1201,[],'G');a.last_end=1;a.pending=None
   a.receipts.append({'time_begin_s':0,'time_end_s':1,'yellow_scope':scope});raise original
  a.prepare_step=prepare;a.reconcile_step=reconcile
  capture=NS(snapshot=lambda *args:{'streams':{'sumo_stderr.log':{'text':''}}},adapter_warning=lambda x:{})
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)
   with patch.object(bridge,'FrameCache',side_effect=lambda x:x),patch.object(bridge,'identity_snapshot',return_value={'synthetic':True}):
    with self.assertRaises(ValueError) as caught:bridge._diagnostic_loop(conn,NS(request_phase=lambda *a:None),capture,out,dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=None),NS(poll=lambda:None),time.monotonic(),a,NS(events=[],mode='dynamic_commands'))
   self.assertIs(caught.exception,original);self.assertEqual(targets,[1]);self.assertEqual([json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()],a.ledger.events)
   q=json.loads((out/'post_steps.jsonl').read_text())['retained_receipts'][0]['yellow_scope'];self.assertEqual(q['status'],'UNKNOWN');self.assertEqual(q['diagnostic_yellow_contract']['interpretation'],'DIAGNOSTIC_WITNESS_NOT_ESTABLISHED')

if __name__=='__main__':unittest.main()
