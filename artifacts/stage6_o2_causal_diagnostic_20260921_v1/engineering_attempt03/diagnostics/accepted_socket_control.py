"""Python-only reproduction of SUMO accept-one-then-close-listener lifecycle."""
import json,subprocess,socket,sys,io
from pathlib import Path
B=Path(__file__).absolute().parents[1];sys.path.insert(0,str(B));from connection_ownership import verify_established_connection
child='''import socket
s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(("127.0.0.1",8819));s.listen(1);print("READY",flush=True)
c,a=s.accept();s.close();print("ACCEPTED_LISTENER_CLOSED",flush=True)
x=c.recv(16);c.sendall(b"PONG");c.close()
'''
p=subprocess.Popen([sys.executable,'-B','-c',child],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 assert p.stdout.readline().strip()=='READY'
 pre=subprocess.run(['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t'],capture_output=True,text=True,timeout=2)
 assert set(pre.stdout.split())=={str(p.pid)}
 with socket.create_connection(('127.0.0.1',8819),timeout=2) as s:
  assert p.stdout.readline().strip()=='ACCEPTED_LISTENER_CLOSED'
  old=subprocess.run(['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t'],capture_output=True,text=True,timeout=2)
  trace=io.StringIO();proof=verify_established_connection(p,s,trace)
  s.sendall(b'PING');reply=s.recv(16).decode()
 rc=p.wait(timeout=2)
 result={'status':'PASS','SUMO_starts':0,'TraCI_sessions':0,'python_tcp_child_pid':p.pid,'preconnect_exact_PID_pass':True,'old_LISTEN_check':{'rc':old.returncode,'stdout':old.stdout,'stderr':old.stderr},'new_ESTABLISHED_check':proof,'reply':reply,'child_rc':rc,'trace':trace.getvalue()}
 assert old.returncode==1 and not old.stdout and reply=='PONG' and rc==0
 with (B/'diagnostics/accepted_socket_control_receipt.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True)
 print(json.dumps(result))
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=2)
