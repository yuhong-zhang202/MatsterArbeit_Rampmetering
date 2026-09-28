#!/usr/bin/env python3
"""Single-start read-only TraCI observer; launched only by bound supervisor."""
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).absolute().parent
sys.path.insert(0,str(BASE))
import runtime_executor as supervisor
REGION=('urban_in_0',':urban_tls_0_0','shared_approach_0',':urban_diverge_0_0',':urban_diverge_1_0','urban_out_0','ramp_storage_0',':ramp_mid_0_0','ramp_accel_0')
TARGETS=('U_flow.34','U_flow.35','U_flow.36','R_flow.68','R_flow.69','R_flow.70','R_flow.71','R_flow.72')
LOOKAHEAD=600.0

def emit(out,row):
 out.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n');out.flush()

def observe_vehicle(c,vid):
 v=c.vehicle
 leader=v.getLeader(vid,LOOKAHEAD)
 gap=v.getMinGap(vid)
 return {'id':vid,'type':v.getTypeID(vid),'route':v.getRoute(vid),'route_index':v.getRouteIndex(vid),
 'lane':v.getLaneID(vid),'pos':v.getLanePosition(vid),'xy':v.getPosition(vid),'angle':v.getAngle(vid),
 'speed':v.getSpeed(vid),'acceleration':v.getAcceleration(vid),'length':v.getLength(vid),'minGap':gap,
 'leader_raw':leader,'leader_bumper_gap':leader[1]+gap if leader and leader[0] else None,
 'leader_speed':v.getSpeed(leader[0]) if leader and leader[0] else None,
 'next_tls':v.getNextTLS(vid),'next_links':v.getNextLinks(vid),'junction_foes':v.getJunctionFoes(vid,LOOKAHEAD)}

def snapshot(c,label,before,after):
 ids=c.vehicle.getIDList();chosen=[]
 for vid in sorted(ids):
  if vid in TARGETS or c.vehicle.getLaneID(vid) in REGION:chosen.append(observe_vehicle(c,vid))
 return {'kind':'target_snapshot','fcd_label_candidate':label,'step_before_s':before,'step_after_s':after,
 'vehicles':chosen,'missing_targets':[v for v in TARGETS if v not in ids],
 'lane_links':{lane:c.lane.getLinks(lane,True) for lane in REGION},
 'tls':{tls:{'program':c.trafficlight.getProgram(tls),'phase':c.trafficlight.getPhase(tls),'state':c.trafficlight.getRedYellowGreenState(tls)} for tls in ('urban_tls','ramp_mid')}}

def advance(c,out,stop_path):
 supervisor.require(c.simulation.getTime()==0 and c.simulation.getDeltaT()==1,'initial clock/step mismatch')
 for label in range(450):
  before=c.simulation.getTime();c.simulationStep();after=c.simulation.getTime()
  supervisor.require(before==label and after==label+1,'clock is not registered 1-second stepping')
  events={'collisions':c.simulation.getCollidingVehiclesIDList(),'teleport_start':c.simulation.getStartingTeleportIDList(),
   'teleport_end':c.simulation.getEndingTeleportIDList(),'emergency_stopping':c.simulation.getEmergencyStoppingVehiclesIDList()}
  emit(out,{'kind':'step','fcd_label_candidate':label,'step_before_s':before,'step_after_s':after,'events':events,
   'departed':c.simulation.getDepartedIDList(),'arrived':c.simulation.getArrivedIDList()})
  if events['collisions'] or events['teleport_start'] or events['teleport_end']:
   supervisor.durable(stop_path,{'event_type':'collision' if events['collisions'] else 'teleport','observer':'readonly_traci',
    'source_path':str(out.name),'observed_unix':time.time(),'simulation_after_s':after,'fcd_label_candidate':label,'events':events,
    'observed_excerpt':json.dumps(events)})
   raise RuntimeError('physical_event_stop')
  # Two early samples verify FCD/TraCI frame alignment before interpretation.
  if label in (0,1,2) or 385<=label<=430:emit(out,snapshot(c,label,before,after))
 return {'steps':450,'initial_s':0,'final_s':c.simulation.getTime(),'target_frames':46,'alignment_frames':3}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--card',type=Path,required=True);a=ap.parse_args()
 card=supervisor.load_checked(a.card);run=Path(card['attempt']['run_root'])
 reservation=json.loads((run/'reservation.json').read_text())
 supervisor.require(reservation['card_sha256']==supervisor.digest(a.card) and reservation.get('executor_pid')==os.getppid(),'not launched by bound live supervisor')
 supervisor.validate_approval(card,a.card,Path(card['approval_path']))
 sys.path.insert(0,card['SUMO_HOME']+'/tools');import traci
 supervisor.require(Path(traci.__file__).resolve()==Path(card['SUMO_HOME']+'/tools/traci/__init__.py').resolve(),'wrong TraCI module')
 p=None;c=None;status='observer_failure';error=None;counts={};rc=None
 try:
  with (run/'sumo_stdout.log').open('xb',buffering=0) as so,(run/'sumo_stderr.log').open('xb',buffering=0) as se,(run/'observer.jsonl').open('x',buffering=1) as out:
   # Inherit supervisor process group. Exactly one Popen, no traci.start auto-retry.
   p=subprocess.Popen(card['sumo_argv'],cwd=card['cwd'],env=os.environ.copy(),stdout=so,stderr=se)
   supervisor.durable(run/'sumo_started.json',{'pid':p.pid,'pgid':os.getpgid(p.pid),'argv':card['sumo_argv'],'time_unix':time.time()})
   # Prove the loopback listener belongs to our sole child, not an unrelated server.
   deadline=time.monotonic()+8
   while True:
    supervisor.require(p.poll() is None,'SUMO exited before socket became ready')
    seen=subprocess.run(['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t'],capture_output=True,text=True,timeout=2)
    emit(out,{'kind':'listener_preconnect','returncode':seen.returncode,'stdout':seen.stdout,'stderr':seen.stderr})
    owners=set(seen.stdout.split())
    if owners:
     supervisor.require(owners=={str(p.pid)},'TraCI listener owned by another process');break
    supervisor.require(time.monotonic()<deadline,'no owned TraCI listener in 8 seconds');time.sleep(0.05)
   c=traci.connect(port=8819,host='127.0.0.1',numRetries=100,waitBetweenRetries=0.05,proc=p)
   seen=subprocess.run(['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t'],capture_output=True,text=True,timeout=2)
   emit(out,{'kind':'listener_postconnect','returncode':seen.returncode,'stdout':seen.stdout,'stderr':seen.stderr})
   supervisor.require(set(seen.stdout.split())=={str(p.pid)} and p.poll() is None,'server ownership changed before observation')
   version=c.getVersion();supervisor.require('1.26.0' in version[1],'runtime SUMO version mismatch')
   emit(out,{'kind':'initial','version':version,'time':c.simulation.getTime(),'dt':c.simulation.getDeltaT()})
   counts=advance(c,out,run/'physical_stop_request.json')
   c.close(wait=False);c=None;rc=p.wait(timeout=10)
   supervisor.require(rc==0,'SUMO nonzero');status='observer_completed_pending_independent_gate'
 except BaseException as exc:
  error=repr(exc)
  if p and p.poll() is None:
   p.terminate()
   try:p.wait(timeout=1)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=1)
  if p:rc=p.poll()
 finally:
  supervisor.durable(run/'observer_receipt.json',{'status':status,'error':error,'SUMO_returncode':rc,'counts':counts,
   'card_sha256':supervisor.digest(a.card),'behavior_setters':0,'no_retry':True,'SUMO_starts':1 if p else 0,
   'alignment_status':'UNVERIFIED_PENDING_PREFIX_AND_POSITION_GATE','scientific_acceptance':False})
 return 0 if status=='observer_completed_pending_independent_gate' else 2
if __name__=='__main__':sys.exit(main())
