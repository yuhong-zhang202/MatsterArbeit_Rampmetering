#!/usr/bin/env python3
"""Fail-closed targeted validation launcher. Two technical fixtures then A/B/C; no automatic retries."""
import argparse,fcntl,hashlib,json,os,signal,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
BASE=ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering'
BINARY=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')
BINARY_SHA='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179'
NETWORK_SHA='887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca'
SUMO_HOME='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
ORDER=['TV_SMOKE_B_LC_ON_S17_attempt1','TV_SMOKE_B_LC_OFF_S17_attempt1','TV_A_S17_attempt1','TV_B_S17_attempt1','TV_C_S17_attempt1']
LIMITS={'SUMO_starts':5,'retry':0,'seed23_starts':0,'netconvert':0,'TraCI':0,'GUI':0,'per_attempt_monitored_s':180,'total_monitored_s':900,'per_attempt_observed_bytes':1500000000,'total_observed_bytes':7500000000}
REQUIRED=['source_binding_exact','execution_complete_2700','output_role_set_exact','xml_roots_and_timegrids','planned_identity_coverage','departed_route_and_fcd_consistency','population_conservation','actual_lane_and_connection_consistency','detector_output_contract','tls_state_contract','output_manifest_complete','m_insertion_contract','native_lanechange_contract','meter_state_and_crossing_contract']
def require(value,message):
 if not value:raise ValueError(message)
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def binding(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)}
def no_symlink(p):
 p=Path(p);require(p.is_absolute(),'absolute path required')
 for x in (p,*p.parents):require(not x.is_symlink(),'symlink rejected '+str(x))
def verify(row):
 p=Path(row['path']);no_symlink(p);require(p.is_file() and p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],'binding mismatch '+str(p))
def fsync_dir(p):
 fd=os.open(p,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def durable(p,data):
 with Path(p).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 fsync_dir(Path(p).parent)
def size(p):
 total=0
 for root,dirs,names in os.walk(p,followlinks=False):
  for name in dirs+names:
   q=Path(root)/name;require(not q.is_symlink(),'output symlink rejected')
   if q.is_file():total+=q.stat().st_size
 return total
def terminate(p):
 require(p.pid>1 and p.pid!=os.getpid(),'unsafe process group')
 for sig in [signal.SIGTERM,signal.SIGKILL]:
  try:os.killpg(p.pid,sig)
  except ProcessLookupError:pass
  try:p.wait(timeout=1);return
  except subprocess.TimeoutExpired:pass
 raise RuntimeError('termination unconfirmed')
def validate_gate(gate_path,attempt,card_sha):
 g=json.loads(Path(gate_path).read_text());require(g.get('attempt_id')==attempt['attempt_id'] and g.get('card_sha256')==card_sha,'wrong gate identity/card')
 require(g.get('technical_status')=='PASS' and g.get('physical_status')=='suitable' and g.get('progression_allowed') is True,'previous gate blocks progression')
 rows=g.get('checks',[]);require(len(rows)==len(REQUIRED) and {x['check_id'] for x in rows}==set(REQUIRED),'gate check set incomplete/duplicated')
 require(all(x.get('status')=='PASS' for x in rows),'required gate is not PASS')
 run=Path(attempt['run_root']);require(not (run/'final_output_violation.json').exists(),'final output violation blocks gate');require(g.get('execution_receipt_sha256')==digest(run/'execution_receipt.json'),'gate receipt hash mismatch')
 require(g.get('output_manifest_sha256')==digest(run/'output_manifest.json'),'gate manifest hash mismatch')
 analysis=g.get('analysis_version_binding');require(isinstance(analysis,dict),'missing gate analysis version');verify(analysis)
 for row in json.loads((run/'output_manifest.json').read_text())['files']:verify(row)
 return g

def validate_review(review_binding,card_sha):
 verify(review_binding)
 review=json.loads(Path(review_binding['path']).read_text())
 require(review.get('status')=='PASS_STATIC_FINAL' and review.get('stage')=='exact_runtime_package' and review.get('card_sha256')==card_sha,'final static review is not PASS for this exact card')
 return review

def preflight(card_path,approval_path,attempt_id,environment):
 no_symlink(card_path);no_symlink(approval_path)
 card=json.loads(Path(card_path).read_text());approval=json.loads(Path(approval_path).read_text());sha=digest(card_path)
 require(card.get('kind')=='TARGETED_FIVE_START_RUNTIME_CARD' and card.get('approved') is False,'wrong card kind/status')
 require(card.get('limits')==LIMITS,'wrong limits')
 require(approval.get('status')=='authorized-under-user-task' and approval.get('card_sha256')==sha and approval.get('card_path')==str(card_path),'authorization/card mismatch')
 require(approval.get('scope')=='two technical fixtures then seed17 A/B/C' and approval.get('max_SUMO_starts')==5 and approval.get('synthetic_test_only') is False,'scope mismatch')
 require(approval.get('user_task_binding')==card['user_task_binding'] and approval.get('review_receipt'),'authorization provenance missing')
 verify(approval['user_task_binding']);validate_review(approval['review_receipt'],sha)
 require(environment.get('SUMO_HOME')==SUMO_HOME and not any(k.startswith(('DYLD_','LD_')) for k in environment),'unsafe environment')
 require(card['binary']['path']==str(BINARY) and card['binary']['sha256']==BINARY_SHA,'wrong binary')
 require(card['network']['sha256']==NETWORK_SHA,'wrong common network')
 require(card['executor']['path']==str(Path(__file__).absolute()),'wrong executor')
 for row in card['bindings']:verify(row)
 for row in [card['binary'],card['network'],card['executor'],card['test_receipt'],card['static_receipt'],card['input_manifest'],card['user_task_binding']]:verify(row)
 require(json.loads(Path(card['static_receipt']['path']).read_text())['status']=='PASS','static check failed')
 tests=json.loads(Path(card['test_receipt']['path']).read_text());require(tests['status']=='PASS' and tests['executor_sha256']==digest(__file__) and tests['real_SUMO_starts']==0,'test binding failed')
 require([a['attempt_id'] for a in card['attempts']]==ORDER and attempt_id in ORDER,'sequence mismatch')
 require(card['attempts']==json.loads(Path(card['input_manifest']['path']).read_text())['attempts'],'input manifest mismatch')
 raw=ROOT/'data/raw/stage6_targeted_validation_20260920_v1'
 for a in card['attempts']:
  require(a['seed']==17 and a['argv']==[str(BINARY),'-c',str(BASE/'inputs'/a['attempt_id']/'scenario.sumocfg')],'unregistered argv/seed')
  require(a['run_root']==str(raw/a['attempt_id']) and a['output_root']==str(raw/a['attempt_id']/'outputs'),'wrong output root')
  for row in a['inputs']:verify(row)
  cfg=ET.parse(a['argv'][2]).getroot();require(cfg.find('input/net-file').get('value')==card['network']['path'],'different network')
  require([cfg.find('time/'+k).get('value') for k in ['begin','end','step-length']]==['0','2700','1'] and cfg.find('random_number/seed').get('value')=='17','timing mismatch')
  no_symlink(a['run_root'])
 previous=card['attempts'][:ORDER.index(attempt_id)]
 for a in previous:
  run=Path(a['run_root']);rr=json.loads((run/'execution_receipt.json').read_text());require(rr['status']=='process_completed_pending_gate','prior technical/physical failure blocks card')
  validate_gate(BASE/'gates'/(a['attempt_id']+'.json'),a,sha)
 if ORDER.index(attempt_id)>=2:
  from measurement_helpers import normalized_xml_digest
  neutral=json.loads((BASE/'gates/logger_neutrality.json').read_text())
  require(neutral.get('status')=='PASS' and neutral.get('card_sha256')==sha and neutral.get('compared_roles')==17,'logger neutrality not passed')
  verify(neutral['analysis_version_binding'])
  for a in card['attempts'][:2]:require(neutral['receipt_hashes'][a['attempt_id']]==digest(Path(a['run_root'])/'execution_receipt.json'),'neutrality source changed')
  roles=json.loads((BASE/'inputs'/ORDER[1]/'output_roles.json').read_text())['required_xml_roles']
  for role in roles:
   name=role['role'];left=Path(card['attempts'][0]['output_root'])/name;right=Path(card['attempts'][1]['output_root'])/name
   require(normalized_xml_digest(left)==normalized_xml_digest(right),'logger changed non-lanechange output '+name)
 for a in card['attempts'][ORDER.index(attempt_id):]:require(not Path(a['run_root']).exists(),'current/future attempt already consumed')
 if raw.exists():require(set(x.name for x in raw.iterdir())<=set(ORDER),'unregistered attempt in task raw root')
 previous_time=sum(json.loads((Path(a['run_root'])/'execution_receipt.json').read_text())['wallclock_s'] for a in previous)
 previous_bytes=sum(size(Path(a['run_root'])) for a in previous)
 require(previous_time<LIMITS['total_monitored_s'] and previous_bytes<LIMITS['total_observed_bytes'],'task budget exhausted')
 return card,approval,card['attempts'][ORDER.index(attempt_id)],previous_time,previous_bytes

def _run(attempt,card_sha,approval_binding,prior_time=0,prior_bytes=0,factory=subprocess.Popen,clock=time.monotonic,sleep=time.sleep,size_fn=size,stop=terminate,timeout=180,cap=1500000000,synthetic=False):
 run=Path(attempt['run_root']);no_symlink(run);run.parent.mkdir(parents=True,exist_ok=True);os.mkdir(run);fsync_dir(run.parent)
 durable(run/'reservation.json',{'attempt_id':attempt['attempt_id'],'consumed_SUMO_starts':1,'card_sha256':card_sha,'approval_binding':approval_binding,'synthetic_test_only':synthetic,'automatic_retry':False,'argv':attempt['argv'],'created_unix':time.time(),'orphan_claim_rule':'terminal_unknown_consumed_no_relaunch'})
 (run/'outputs').mkdir();start=clock();process=None;status='terminal_start_failure';error=None;peak=0;rc=None
 try:
  with (run/'stdout.log').open('xb',buffering=0) as stdout,(run/'stderr.log').open('xb',buffering=0) as stderr:
   env={'SUMO_HOME':SUMO_HOME,'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','HOME':os.environ.get('HOME','')}
   process=factory(attempt['argv'],cwd=str(ROOT),env=env,stdout=stdout,stderr=stderr,start_new_session=True)
   durable(run/'started.json',{'pid':process.pid,'wallclock_started_unix':time.time(),'synthetic_test_only':synthetic})
   while True:
    marker=run/'physical_stop_request.json'
    if marker.exists():
     physical=json.loads(marker.read_text())
     require(physical.get('event_type') in ['collision','teleport'] and physical.get('observed_excerpt') and physical.get('observer')=='primary' and physical.get('source_path') and isinstance(physical.get('observed_unix'),(int,float)),'invalid physical stop evidence')
     status='partial_evidence_physical';break
    peak=max(peak,size_fn(run));rc=process.poll();elapsed=clock()-start
    if peak>cap or peak+prior_bytes>LIMITS['total_observed_bytes']:status='terminal_output_stop_line';break
    if elapsed>=timeout or elapsed+prior_time>=LIMITS['total_monitored_s']:status='terminal_timeout';break
    if rc is not None:status='process_completed_pending_gate' if rc==0 else 'terminal_nonzero';break
    sleep(0.05)
   if status in ['terminal_timeout','terminal_output_stop_line','partial_evidence_physical']:stop(process);rc=process.poll()
   for f in [stdout,stderr]:f.flush();os.fsync(f.fileno())
 except BaseException as exc:
  status='terminal_executor_exception' if process else 'terminal_start_failure';error=repr(exc)
  if process:
   try:stop(process)
   except BaseException as ex:status='terminal_termination_unknown';error+='; '+repr(ex)
 # No child writer may survive a successful parent exit. No sampling subprocess is used.
 if process and not synthetic:
  try:os.killpg(process.pid,0);status='terminal_live_process_group';stop(process)
  except ProcessLookupError:pass
  except BaseException as exc:status='terminal_termination_unknown';error=repr(exc)
 try:peak=max(peak,size_fn(run))
 except BaseException as exc:status='terminal_inspection_failure';error=repr(exc)
 files=[binding(p) for p in sorted(run.rglob('*')) if p.is_file() and not p.is_symlink()]
 durable(run/'output_manifest.json',{'attempt_id':attempt['attempt_id'],'card_sha256':card_sha,'files':files,'synthetic_test_only':synthetic,'scope':'all files before this manifest and terminal receipt; raw outputs immutable'})
 receipt={'attempt_id':attempt['attempt_id'],'status':status,'returncode':rc,'wallclock_s':clock()-start,'observed_peak_bytes':peak,'monitored_timeout_s':timeout,'observed_stop_bytes':cap,'prior_consumed_wallclock_s':prior_time,'prior_output_bytes':prior_bytes,'consumed_SUMO_starts':1,'automatic_retry':False,'synthetic_test_only':synthetic,'card_sha256':card_sha,'error':error,'output_manifest':binding(run/'output_manifest.json'),'progression_allowed':False,'gate_required':True,'SUMO_process_only_no_scientific_acceptance':True}
 durable(run/'execution_receipt.json',receipt);final=size(run)
 if final>cap or final+prior_bytes>LIMITS['total_observed_bytes']:
  durable(run/'final_output_violation.json',{'status':'terminal_output_stop_line','exact_bytes_before_this_record':final,'automatic_retry':False});receipt['status']='terminal_output_stop_line'
 receipt['final_directory_bytes']=size(run)
 return receipt

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--card',type=Path,required=True);ap.add_argument('--approval',type=Path);ap.add_argument('--attempt',required=True);ap.add_argument('--execute',action='store_true');a=ap.parse_args()
 require(a.attempt in ORDER,'unknown attempt')
 if not a.execute:print(json.dumps({'status':'DRY_RUN_NO_PROCESS','attempt':a.attempt,'card_sha256':digest(a.card)}));return 0
 require(a.approval is not None,'approval sidecar required')
 BASE.mkdir(exist_ok=True)
 with (BASE/'execution.lock').open('a') as lock:
  fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  card,approval,attempt,prior_time,prior_bytes=preflight(a.card.absolute(),a.approval.absolute(),a.attempt,os.environ)
  def interrupted(signum,frame):raise KeyboardInterrupt('termination signal'+str(signum))
  signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGHUP,interrupted)
  r=_run(attempt,digest(a.card),binding(a.approval),prior_time,prior_bytes);print(json.dumps(r,sort_keys=True));return 0 if r['status']=='process_completed_pending_gate' else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print('FAIL_CLOSED: '+repr(e),file=sys.stderr);sys.exit(2)
