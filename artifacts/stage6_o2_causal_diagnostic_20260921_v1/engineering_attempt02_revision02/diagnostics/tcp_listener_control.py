#!/usr/bin/env python3
"""Local Python TCP fixture and exact lsof query. Never starts SUMO."""
import json,subprocess,sys,socket,os,time
from pathlib import Path
B=Path(__file__).absolute().parent
child='''import socket,sys
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(("127.0.0.1",8819));s.listen(1)
print("ready",flush=True)
c,a=s.accept();data=c.recv(16);c.sendall(b"PONG");c.close();s.close()
'''
p=subprocess.Popen([sys.executable,'-B','-c',child],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 ready=p.stdout.readline().strip();assert ready=='ready',ready
 argv=['/usr/sbin/lsof','-nP','-iTCP:8819','-sTCP:LISTEN','-t']
 before=subprocess.run(argv,capture_output=True,text=True,timeout=2)
 with socket.create_connection(('127.0.0.1',8819),timeout=2) as c:c.sendall(b'PING');reply=c.recv(16).decode()
 stdout,stderr=p.communicate(timeout=2)
 result={'kind':'python_tcp_fixture_no_SUMO','child_pid':p.pid,'exact_lsof_argv':argv,'lsof_rc':before.returncode,'lsof_stdout':before.stdout,'lsof_stderr':before.stderr,'identified_correct_child':set(before.stdout.split())=={str(p.pid)},'loopback_reply':reply,'child_rc':p.returncode,'child_stdout':stdout,'child_stderr':stderr,'SUMO_starts':0,'TraCI_connections':0,'unix_time':time.time()}
 with (B/'tcp_listener_control_receipt.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=2)
