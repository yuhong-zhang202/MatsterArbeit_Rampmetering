"""Bounded pre-step OS observation, never starts SUMO or mutates vehicle state."""
import json,subprocess,time

def emit(out,row):out.write(json.dumps(row,sort_keys=True)+'\n');out.flush()
def wait_for_owned_listener(process,out,run,runner=subprocess.run,clock=time.monotonic,sleep=time.sleep):
 start=clock();diagnosed=False
 while True:
  if process.poll() is not None:raise RuntimeError('SUMO exited before socket became ready')
  seen=runner(['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t'],capture_output=True,text=True,timeout=2)
  emit(out,{'kind':'listener_preconnect','elapsed_s':clock()-start,'returncode':seen.returncode,'stdout':seen.stdout,'stderr':seen.stderr})
  owners=set(seen.stdout.split())
  if owners:
   if owners!={str(process.pid)}:raise RuntimeError('TraCI listener owned by another process')
   return {'startup_elapsed_s':clock()-start,'diagnostic_capture_attempted':diagnosed}
  if clock()-start>=60:raise RuntimeError('no owned TraCI listener in 60 seconds')
  if not diagnosed and clock()-start>=2:
   diagnosed=True
   for command,limit in [(['/bin/ps','-p',str(process.pid),'-o','pid,ppid,pgid,state,wchan,etime,%cpu,command'],2),(['/usr/bin/sample',str(process.pid),'1','1','-file',str(run/'startup.sample.txt')],5)]:
    try:
     r=runner(command,capture_output=True,text=True,timeout=limit)
     emit(out,{'kind':'startup_diagnostic','argv':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_s':clock()-start})
    except subprocess.TimeoutExpired as exc:
     emit(out,{'kind':'startup_diagnostic','argv':command,'status':'timeout','timeout_s':limit,'stdout':str(exc.stdout),'stderr':str(exc.stderr),'elapsed_s':clock()-start})
  sleep(0.05)
