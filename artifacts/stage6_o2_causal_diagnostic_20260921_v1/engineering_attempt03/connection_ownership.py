"""Verify the accepted TCP connection, not a listener that SUMO intentionally closes."""
import json,subprocess,time

def parse_lsof(text):
 records=[];pid=None;current=None
 for line in text.splitlines():
  if not line:continue
  tag,value=line[0],line[1:]
  if tag=='p':
   if current:records.append(current);current=None
   pid=value
  elif tag=='f':
   if current:records.append(current)
   current={'pid':pid,'fd':value}
  elif current is not None:
   if tag=='n':current['name']=value
   elif tag=='t':current['type']=value
   elif tag=='T' and value.startswith('ST='):current['state']=value[3:]
 if current:records.append(current)
 return records

def verify_established_connection(process,sock,out,runner=subprocess.run,clock=time.monotonic,sleep=time.sleep):
 client=sock.getsockname();server=sock.getpeername()
 if client[0]!='127.0.0.1' or server!=('127.0.0.1',8819):raise RuntimeError('unexpected observer socket endpoints')
 expected='%s:%s->%s:%s'%(server[0],server[1],client[0],client[1]);start=clock()
 argv=['/usr/sbin/lsof','-nP','-a','-p',str(process.pid),'-iTCP:8819','-sTCP:ESTABLISHED','-FpfntT']
 while True:
  if process.poll() is not None:raise RuntimeError('SUMO exited before accepted-socket ownership verification')
  r=runner(argv,capture_output=True,text=True,timeout=2);records=parse_lsof(r.stdout)
  matched=[x for x in records if x.get('pid')==str(process.pid) and x.get('name')==expected and x.get('state')=='ESTABLISHED']
  row={'kind':'connection_postconnect','argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'client_endpoint':client,'server_endpoint':server,'expected_server_socket':expected,'matching_descriptors':matched,'elapsed_s':clock()-start}
  out.write(json.dumps(row,sort_keys=True)+'\n');out.flush()
  if r.returncode==0 and len(matched)==1 and process.poll() is None:return row
  if clock()-start>=2:raise RuntimeError('accepted socket is not bound to expected SUMO child and client tuple')
  sleep(0.05)
