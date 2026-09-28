"""No sockets/SUMO: exact accepted-connection ownership negative cases."""
import io,json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).absolute().parents[1];sys.path.insert(0,str(B))
from connection_ownership import verify_established_connection,parse_lsof
class Tests(unittest.TestCase):
 def run_case(self,text,peer=('127.0.0.1',8819),dead=False):
  t=[0.0];sock=SimpleNamespace(getsockname=lambda:('127.0.0.1',50950),getpeername=lambda:peer);p=SimpleNamespace(pid=123,poll=lambda:1 if dead else None)
  def sleep(n):t[0]+=n
  return verify_established_connection(p,sock,io.StringIO(),runner=lambda *a,**k:SimpleNamespace(returncode=0,stdout=text,stderr=''),clock=lambda:t[0],sleep=sleep)
 def test_matching_established(self):
  r=self.run_case('p123\nf4\ntIPv4\nn127.0.0.1:8819->127.0.0.1:50950\nTST=ESTABLISHED\n');self.assertEqual(len(r['matching_descriptors']),1)
 def test_wrong_pid(self):
  with self.assertRaises(RuntimeError):self.run_case('p999\nf4\nn127.0.0.1:8819->127.0.0.1:50950\nTST=ESTABLISHED\n')
 def test_same_pid_wrong_client_tuple(self):
  with self.assertRaises(RuntimeError):self.run_case('p123\nf4\nn127.0.0.1:8819->127.0.0.1:50951\nTST=ESTABLISHED\n')
 def test_listening_not_accepted(self):
  with self.assertRaises(RuntimeError):self.run_case('p123\nf4\nn*:8819\nTST=LISTEN\n')
 def test_unexpected_peer(self):
  with self.assertRaises(RuntimeError):self.run_case('',peer=('127.0.0.1',8820))
 def test_dead_child(self):
  with self.assertRaises(RuntimeError):self.run_case('',dead=True)
 def test_duplicate_matching_descriptors_rejected(self):
  row='n127.0.0.1:8819->127.0.0.1:50950\nTST=ESTABLISHED\n'
  with self.assertRaises(RuntimeError):self.run_case('p123\nf4\n'+row+'f5\n'+row)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 with (B/'connection_ownership_test_receipt.json').open('x') as f:json.dump({'status':'PASS' if r.wasSuccessful() else 'FAIL','tests':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'SUMO_starts':0,'TraCI_connections':0,'live_network_connections':0},f,indent=2)
 sys.exit(not r.wasSuccessful())
