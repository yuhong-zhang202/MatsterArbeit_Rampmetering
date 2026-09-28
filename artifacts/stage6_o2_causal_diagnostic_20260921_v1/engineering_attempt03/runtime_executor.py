#!/usr/bin/env python3
"""One isolated O2 C/seed17 technical diagnostic. Defaults to zero-process dry-run."""
import argparse,fcntl,hashlib,json,os,signal,socket,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
BASE=Path(__file__).absolute().parent
SUMO_HOME='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
LIMITS={'SUMO_starts':1,'TraCI_connections':1,'netconvert':0,'GUI':0,'retry':0,'per_attempt_monitored_s':180,'total_monitored_s':208.54239662599866,'per_attempt_observed_bytes':200000000,'total_observed_bytes':200118166}
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
def _run(attempt,card_sha,approval_binding,prior_time=0,prior_bytes=0,factory=subprocess.Popen,clock=time.monotonic,sleep=time.sleep,size_fn=size,stop=terminate,timeout=180,cap=1500000000,synthetic=False):
 run=Path(attempt['run_root']);no_symlink(run);run.parent.mkdir(parents=True,exist_ok=True);os.mkdir(run);fsync_dir(run.parent)
 durable(run/'reservation.json',{'executor_pid':os.getpid(),'attempt_id':attempt['attempt_id'],'consumed_SUMO_starts':1,'card_sha256':card_sha,'approval_binding':approval_binding,'synthetic_test_only':synthetic,'automatic_retry':False,'argv':attempt['argv'],'created_unix':time.time(),'orphan_claim_rule':'terminal_unknown_consumed_no_relaunch'})
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
     require(physical.get('event_type') in ['collision','teleport'] and physical.get('observed_excerpt') and physical.get('observer') in ['primary','readonly_traci'] and physical.get('source_path') and isinstance(physical.get('observed_unix'),(int,float)),'invalid physical stop evidence')
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

def validate_approval(card,card_path,approval_path):
 no_symlink(approval_path)
 approval=json.loads(approval_path.read_text());sha=digest(card_path)
 require(approval.get('status')=='conditionally_authorized_released_after_exact_review','approval is not released')
 require(approval.get('card_sha256')==sha and approval.get('max_SUMO_starts')==1 and approval.get('scope')=='single_C_seed17_end450_readonly_diagnostic','approval scope/card mismatch')
 require(approval.get('user_authorization_binding')==card['user_authorization_binding'],'authorization provenance mismatch')
 verify(approval['user_authorization_binding']);verify(approval['review_receipt'])
 review=json.loads(Path(approval['review_receipt']['path']).read_text())
 require(review.get('status')=='PASS_STATIC_FINAL' and review.get('stage')=='exact_o2_diagnostic_package' and review.get('card_sha256')==sha,'review is not exact final PASS')
 return approval

def load_checked(card_path):
 no_symlink(card_path);card=json.loads(card_path.read_text())
 require(card_path==BASE/'O2_DIAGNOSTIC_CARD.json' and card['kind']=='O2_SINGLE_START_DIAGNOSTIC' and card['approved'] is False,'wrong immutable card')
 require(card['limits']==LIMITS,'budget mismatch')
 for row in card['bindings']:verify(row)
 require(card['executor']==binding(__file__),'wrong executor')
 require(card['attempt']['argv']==[card['python']['path'],'-B',str(BASE/'observer.py'),'--card',str(card_path)],'observer argv mismatch')
 require(card['sumo_argv']==[card['sumo_binary']['path'],'-c',str(BASE/'inputs/scenario.sumocfg'),'--remote-port','8819','--num-clients','1'],'SUMO argv mismatch')
 require(card['sumo_binary']['sha256']=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179','unexpected binary')
 require(card['network']['sha256']=='887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca','unexpected network')
 for key in ('static_receipt','test_receipt'):
  verify(card[key]);require(json.loads(Path(card[key]['path']).read_text())['status']=='PASS','offline validation not PASS')
 require(json.loads(Path(card['test_receipt']['path']).read_text())['executor_sha256']==digest(__file__),'test/executor mismatch')
 return card

def preflight(card_path,approval_path):
 card=load_checked(card_path);approval=validate_approval(card,card_path,approval_path)
 require(os.environ.get('SUMO_HOME')==SUMO_HOME,'SUMO_HOME mismatch')
 require(not any(k.startswith(('DYLD_','LD_','PYTHON')) for k in os.environ),'unsafe injected environment')
 run=Path(card['attempt']['run_root']);no_symlink(run);require(not run.exists(),'attempt consumed')
 require(run==ROOT/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt3','unexpected raw root')
 if run.parent.exists():require({p.name for p in run.parent.iterdir()}=={'O2_C_S17_450_attempt1','O2_C_S17_450_attempt2'},'prior inventory mismatch')
 prior=card['prior_diagnostic_attempts']
 require(sum(size(Path(a['run_root'])) for a in prior['attempts'])==118166,'prior total changed')
 for a in prior['attempts']:
  verify(a['receipt']);require(size(Path(a['run_root']))==a['bytes'],'prior attempt bytes changed')
 # Checking port is not a SUMO start. No observer may attach to another server.
 with socket.socket() as probe:probe.bind(('127.0.0.1',8819))
 return card,approval

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--card',type=Path,required=True);ap.add_argument('--approval',type=Path);ap.add_argument('--execute',action='store_true');a=ap.parse_args()
 card=load_checked(a.card.absolute())
 if not a.execute:print(json.dumps({'status':'STATIC_DRY_RUN_NO_PROCESS','card_sha256':digest(a.card),'SUMO_starts':0,'TraCI_connections':0}));return 0
 require(a.approval==Path(card['approval_path']),'exact approval path required')
 with (BASE/'execution.lock').open('a') as lock:
  fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  card,approval=preflight(a.card.absolute(),a.approval.absolute())
  def interrupted(signum,frame):raise KeyboardInterrupt('signal '+str(signum))
  signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGHUP,interrupted)
  result=_run(card['attempt'],digest(a.card),binding(a.approval),prior_time=28.542396625998663,prior_bytes=118166,timeout=180,cap=200000000)
  print(json.dumps(result,sort_keys=True));return 0 if result['status']=='process_completed_pending_gate' else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as exc:print('FAIL_CLOSED: '+repr(exc),file=sys.stderr);sys.exit(2)
