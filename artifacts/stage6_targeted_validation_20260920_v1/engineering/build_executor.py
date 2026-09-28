"""Single isolated network build. Default dry-run; no SUMO/TraCI/GUI launch capability."""
import os,sys,json,hashlib,time,subprocess,signal,argparse
from pathlib import Path
BASE=Path(__file__).resolve().parent
HOME='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
BINARY='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def write(p,obj):
 with Path(p).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(Path(p).parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
def verify(b):
 p=Path(b['path']);assert p.is_file() and not p.is_symlink() and p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],str(p)
def size(p):return sum(x.stat().st_size for x in p.rglob('*') if x.is_file())
def stop(p):
 for sig in [signal.SIGTERM,signal.SIGKILL]:
  try:os.killpg(p.pid,sig)
  except ProcessLookupError:pass
  try:p.wait(timeout=1);return
  except subprocess.TimeoutExpired:pass
 raise RuntimeError('process termination unknown')
def execute(card,cardsha):
 run=Path(card['run_root']);assert not run.exists();run.parent.mkdir(parents=True,exist_ok=True);run.mkdir()
 write(run/'reservation.json',dict(card_sha256=cardsha,netconvert_starts=1,automatic_retry=False,argv=card['argv'],time=time.time()))
 start=time.monotonic();p=None;status='start_failure';rc=None
 try:
  with (run/'stdout.log').open('xb',buffering=0) as out,(run/'stderr.log').open('xb',buffering=0) as err:
   p=subprocess.Popen(card['argv'],cwd=card['cwd'],env={'SUMO_HOME':HOME,'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','HOME':os.environ.get('HOME','')},stdout=out,stderr=err,start_new_session=True)
   write(run/'started.json',dict(pid=p.pid,unix=time.time()))
   while True:
    rc=p.poll()
    if size(run)>card['observed_byte_stop']:status='output_stop';stop(p);break
    if time.monotonic()-start>card['timeout_s']:status='timeout';stop(p);break
    if rc is not None:status='completed' if rc==0 else 'nonzero';break
    time.sleep(.05)
 except BaseException as e:
  status='exception';write(run/'exception.json',{'error':repr(e)})
  if p:stop(p)
 absent=True
 if p:
  rc=p.poll()
  try:os.killpg(p.pid,0);absent=False;stop(p)
  except ProcessLookupError:pass
 write(run/'build_receipt.json',dict(status=status,returncode=rc,wallclock_s=time.monotonic()-start,card_sha256=cardsha,process_group_absent=absent,netconvert_starts=1,SUMO_starts=0,TraCI=0,GUI=0,files_before_receipt=[bind(x) for x in sorted(run.rglob('*')) if x.is_file()],observed_bytes_before_receipt=size(run),monitoring='50ms polling stop-line, not hard disk quota; overshoot possible',automatic_retry=False))
 return 0 if status=='completed' and absent else 2
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--card',type=Path,required=True);a.add_argument('--execute',action='store_true');args=a.parse_args();c=json.loads(args.card.read_text())
 assert c['kind']=='TARGETED_COMMON_NETWORK_BUILD' and c['argv']==[BINARY,'-c',str(BASE/'network_inputs/candidate.netccfg')]
 assert c['run_root']==str(BASE/'build_attempts/TV_BUILD01') and c['timeout_s']==30 and c['observed_byte_stop']==100000000
 for b in c['bindings']:verify(b)
 assert os.environ.get('SUMO_HOME')==HOME and not any(k.startswith(('DYLD_','LD_')) for k in os.environ)
 assert not Path(c['run_root']).exists()
 if not args.execute:print('PASS_DRY_RUN_NO_PROCESS');sys.exit(0)
 sys.exit(execute(c,sha(args.card)))
