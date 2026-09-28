"""Deterministic offline listener/watchdog tests. No real socket or SUMO."""
import io,json,sys,unittest,subprocess
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).absolute().parents[1];sys.path.insert(0,str(B))
from startup_probe import wait_for_owned_listener
class Clock:
 def __init__(self):self.t=0
 def __call__(self):return self.t
 def sleep(self,n):self.t+=n
class Tests(unittest.TestCase):
 def case(self,ready=0,foreign=False,dead=False,sample_timeout=False):
  clock=Clock();calls=[];out=io.StringIO();p=SimpleNamespace(pid=123,poll=lambda:1 if dead else None)
  def run(argv,**kw):
   calls.append(argv)
   if argv[0]=='/usr/sbin/lsof':return SimpleNamespace(returncode=0 if clock.t>=ready else 1,stdout=('999\n' if foreign else '123\n') if clock.t>=ready else '',stderr='')
   if sample_timeout and argv[0]=='/usr/bin/sample':raise subprocess.TimeoutExpired(argv,5)
   return SimpleNamespace(returncode=0,stdout='fake diagnostic',stderr='')
  return lambda:wait_for_owned_listener(p,out,B,runner=run,clock=clock,sleep=clock.sleep),clock,calls,out
 def test_immediate_ready(self):
  f,c,calls,out=self.case();r=f();self.assertFalse(r['diagnostic_capture_attempted']);self.assertEqual(len(calls),1)
 def test_late_ready_after_old_eight_second_limit(self):
  f,c,calls,out=self.case(ready=10);r=f();self.assertGreaterEqual(r['startup_elapsed_s'],10);self.assertEqual(sum(x[0]=='/usr/bin/sample' for x in calls),1)
 def test_foreign_listener_rejected(self):
  f,*_=self.case(foreign=True)
  with self.assertRaisesRegex(RuntimeError,'another process'):f()
 def test_dead_process_rejected(self):
  f,*_=self.case(dead=True)
  with self.assertRaisesRegex(RuntimeError,'exited'):f()
 def test_sixty_second_deadline(self):
  f,c,calls,out=self.case(ready=100)
  with self.assertRaisesRegex(RuntimeError,'60 seconds'):f()
  self.assertLess(c.t,60.1)
 def test_sample_failure_does_not_disable_pid_check(self):
  f,c,calls,out=self.case(ready=10,sample_timeout=True);f();rows=[json.loads(x) for x in out.getvalue().splitlines()];self.assertTrue(any(r.get('status')=='timeout' for r in rows))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 with (B/'startup_probe_test_receipt.json').open('x') as f:json.dump({'status':'PASS' if r.wasSuccessful() else 'FAIL','tests':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'SUMO_starts':0,'TraCI_connections':0,'live_network_connections':0},f,indent=2)
 sys.exit(not r.wasSuccessful())
