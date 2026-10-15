"""Focused synthetic boundary/logging fixtures, never native safety evidence."""
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import json,tempfile,time,unittest
from src.candidate_a_dynamic_minqual_20261015 import receiver_wait as current,bridge
from src.candidate_a_native_receiver_wait_20261012 import receiver_wait as legacy
from src.candidate_a_dynamic_minqual_20261015.adapter import StepAdapter
from src.candidate_a_cumulative_full_catalogue_20261014.policy import Ledger

class Frame:
 def __init__(self):
  self.time=1233;self.gap=2.0951522156549345;self.secure=1.022884125080513;self.calls=[]
  self.ids=('R_flow.4','R_flow.5');self.front='R_flow.5';self.lead='R_flow.4'
  self.simulation=NS(getTime=lambda:self.time,getPendingVehicles=lambda:())
  self.vehicle=NS(getIDList=lambda:self.ids,getLoadedIDList=lambda:(),getTypeID=lambda v:'technical_passenger',getRoute=lambda v:current.ROUTES['R'],getSpeedMode=lambda v:31,getLaneChangeMode=lambda v:1621,
   getLaneID=lambda v:current.STORAGE if v==self.front else current.INTERNAL,
   getLanePosition=lambda v:195.61547754834876 if v==self.front else .7206297640036894,getLength=lambda v:5.,getMinGap=lambda v:2.5,
   getSpeed=lambda v:1.022884125080513 if v==self.front else 1.765150741833242,
   getAccel=lambda v:2.6,getDecel=lambda v:4.5,getEmergencyDecel=lambda v:9.,getTau=lambda v:1.,getActionStepLength=lambda v:1.,getImperfection=lambda v:.5,getMaxSpeed=lambda v:55.55555555555556,
   getLeader=lambda v,d:(self.lead,self.gap),getSecureGap=self.query)
  self.lane=NS(getLength=lambda l:204.49 if l==current.STORAGE else 113.08 if l==':urban_diverge_1_0' else 81.98 if l==current.INTERNAL else 365.,getLastStepVehicleIDs=lambda l:(self.front,) if l==current.STORAGE else (self.lead,) if l==current.INTERNAL else ())
  self.trafficlight=NS(getControlledLinks=lambda t:((('ramp_storage_0','ramp_accel_0',current.INTERNAL),),))
 def query(self,**args):self.calls.append(args);return self.secure
 def receiver(self):return dict(available=False,front_id=self.front,reason='LEADER_SECURE_GAP',leader=dict(vehicle_id=self.lead,gap_excluding_minGap_m=self.gap))

class MinimumQualificationTests(unittest.TestCase):
 def test_recorded_margin_only_frame_preserves_legacy_and_logs_advisory(self):
  w=Frame();r=w.receiver();old=legacy.classify_receiver(w,r,w.time);new=current.classify_receiver(w,r,w.time)
  self.assertEqual(old['decision'],'STOP_CURRENT_GAP_BOUND_DENIED');self.assertEqual(new['decision'],'WAIT_NATIVE_FOLLOWING');self.assertFalse(r['available'])
  q=new['current_following'];self.assertTrue(q['hard_screen_pass']);self.assertFalse(q['legacy_margin_pass']);self.assertEqual(q['legacy_contract_status'],'STOP_CURRENT_GAP_BOUND_DENIED');self.assertEqual(q['margin_classification'],'EXTRA_MARGIN_ADVISORY')
  self.assertEqual(q['required_with_margin_m'],w.secure+1.1);self.assertEqual(q['required_hard_floor_m'],w.secure);self.assertEqual(q['hard_margin_m'],0.);self.assertEqual(q['getSecureGap_args']['leaderMaxDecel'],9.);self.assertFalse(q['future_safety_proven'])
  # Replay only: exact query value is supplied from immutable historical input.
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'advisory.jsonl';bridge.append_new(p,q);self.assertEqual(json.loads(p.read_text()),q)
 def test_below_floor_and_unknown_binding_never_become_wait(self):
  w=Frame();w.gap=w.secure-.01;self.assertEqual(current.classify_receiver(w,w.receiver(),w.time)['decision'],'STOP_CURRENT_GAP_BOUND_DENIED')
  for fault in ('wrong_leader','missing_leader','wrong_time','bad_mode','nan_gap','nan_secure'):
   with self.subTest(fault=fault):
    w=Frame();r=w.receiver()
    if fault=='wrong_leader':r['leader']['vehicle_id']='R_flow.unknown'
    elif fault=='missing_leader':r['leader']=None
    elif fault=='wrong_time':w.simulation.getTime=lambda:1232
    elif fault=='bad_mode':w.vehicle.getSpeedMode=lambda v:0
    elif fault=='nan_gap':w.gap=float('nan')
    else:w.secure=float('nan')
    with self.assertRaises(ValueError):current.classify_receiver(w,r,1233)
 def test_advisory_cannot_bypass_new_green_or_strict_numeric_authority(self):
  w=Frame();w.time=1232;self.assertEqual(current.classify_receiver(w,w.receiver(),w.time)['decision'],'WAIT_NATIVE_FOLLOWING')
  with self.assertRaisesRegex(ValueError,'receiver denies green'):bridge.admission(w,w.time,lambda c:([],{}, {},w.receiver()),'I12_PACKET8')
  with self.assertRaisesRegex(ValueError,'NEW_SCOPE_NUMERICAL_EXCEPTION_NOT_ENABLED'):StepAdapter(lambda c:None,300,1296,{'enabled':True})
 def test_coexisting_stop_flushes_observed_ACK_and_advisory_without_more_steps(self):
  w=Frame();advisory=current.classify_receiver(w,w.receiver(),w.time);original=ValueError('COLLISION_OR_TELEPORT')
  conn=NS(simulation=NS(),clock=0,stats={},trafficlight=NS());conn.simulation.getTime=lambda:conn.clock;targets=[]
  def advance(t):targets.append(t);conn.clock=t
  conn.simulationStep=advance
  adapter=NS(end_s=2,ledger=Ledger(900,1208),pending=None,receipts=[],last_completed=None,last_end=None,last_yellow_scope=None)
  def prepare(c,t):
   adapter.pending={'motion':'G'};adapter.ledger.begin_step(1200);adapter.ledger.mark_cycle_start(True);return {'classification':'SYNTHETIC_LOGGING_CLOCK_OFFSET'}
  def reconcile(c,warning):
   adapter.ledger.end_step(1201,[],'G');adapter.last_end=1;adapter.pending=None
   adapter.receipts.append(dict(time_begin_s=0,time_end_s=1,post_native_receiver_decision=advisory));raise original
  adapter.prepare_step=prepare;adapter.reconcile_step=reconcile
  capture=NS(snapshot=lambda *a:{'streams':{'sumo_stderr.log':{'text':''}}},adapter_warning=lambda x:{})
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)
   with patch.object(bridge,'FrameCache',side_effect=lambda x:x),patch.object(bridge,'identity_snapshot',return_value={'synthetic':True}):
    with self.assertRaises(ValueError) as caught:bridge._diagnostic_loop(conn,NS(request_phase=lambda *a:None),capture,out,dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=None),NS(poll=lambda:None),time.monotonic(),adapter,NS(events=[],mode='dynamic_commands'))
   self.assertIs(caught.exception,original);self.assertEqual(targets,[1]);events=[json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()]
   self.assertEqual(events,adapter.ledger.events);self.assertEqual([x['event'] for x in events].count('ACK_OBSERVED'),1)
   retained=json.loads((out/'post_steps.jsonl').read_text())['retained_receipts'][0]['post_native_receiver_decision']['current_following']
   self.assertEqual(retained['margin_classification'],'EXTRA_MARGIN_ADVISORY');self.assertFalse(retained['legacy_margin_pass'])

if __name__=='__main__':unittest.main()
