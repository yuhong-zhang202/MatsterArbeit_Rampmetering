"""Isolated post-accept ownership repair. No launches."""
from pathlib import Path
import json,hashlib
B=Path(__file__).absolute().parent;OLD=B.parent/'engineering_attempt02_revision02';ROOT=B.parents[2]
def put(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(s)
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for folder in ['inputs','references','tests']:
 for p in (OLD/folder).iterdir():
  if p.is_file():
   s=p.read_text()
   if folder=='inputs':s=s.replace(str(OLD),str(B)).replace('/O2_C_S17_450_attempt2/outputs/','/O2_C_S17_450_attempt3/outputs/')
   put(B/folder/p.name,s)
for name in ['startup_probe.py','static_validate.py','diagnostic_gate_contract.json','validate_path_isolation.py']:
 s=(OLD/name).read_text().replace('O2_C_S17_450_attempt2','O2_C_S17_450_attempt3')
 if name=='validate_path_isolation.py':
  s=s.replace("==13288","==118166").replace("'prior_bytes':13288","'prior_bytes':118166")
  s=s.replace("'runtime_executor.py','observer.py','startup_probe.py'","'startup_probe.py'")
 put(B/name,s)
s=(OLD/'observer.py').read_text();a=s.index("   seen=subprocess.run(['/usr/sbin/lsof'",s.index('   c=traci.connect'));z=s.index('   version=c.getVersion()',a)
s=s[:a]+"   from connection_ownership import verify_established_connection\n   verify_established_connection(p,c._socket,out)\n"+s[z:];put(B/'observer.py',s)
s=(OLD/'runtime_executor.py').read_text().replace('O2_C_S17_450_attempt2','O2_C_S17_450_attempt3')
s=s.replace('188.43560208400595','208.54239662599866').replace('200013288','200118166')
s=s.replace("=={'O2_C_S17_450_attempt1'}","=={'O2_C_S17_450_attempt1','O2_C_S17_450_attempt2'}")
start=s.index(" prior=run.parent/'O2_C_S17_450_attempt1'");end=s.index(' # Checking port',start)
s=s[:start]+" prior=card['prior_diagnostic_attempts']\n require(sum(size(Path(a['run_root'])) for a in prior['attempts'])==118166,'prior total changed')\n for a in prior['attempts']:\n  verify(a['receipt']);require(size(Path(a['run_root']))==a['bytes'],'prior attempt bytes changed')\n"+s[end:]
s=s.replace('prior_time=8.43560208400595,prior_bytes=13288','prior_time=28.542396625998663,prior_bytes=118166')
put(B/'runtime_executor.py',s)
rows=[];attempts=[]
for i in [1,2]:
 run=ROOT/f'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt{i}'
 fs=[bind(p) for p in sorted(run.rglob('*')) if p.is_file()];receipt=run/'execution_receipt.json';rr=json.loads(receipt.read_text());rows+=fs
 attempts.append({'attempt_id':f'O2_C_S17_450_attempt{i}','run_root':str(run),'receipt':bind(receipt),'manifest':bind(run/'output_manifest.json'),'wallclock_s':rr['wallclock_s'],'bytes':sum(f['bytes'] for f in fs),'consumed_SUMO_starts':1,'traffic_steps':0,'TCP_connected':i==2,'TraCI_protocol_version_queried':False})
prior={'attempts':attempts,'consumed_SUMO_starts':2,'wallclock_s':sum(a['wallclock_s'] for a in attempts),'bytes':sum(a['bytes'] for a in attempts),'previous_raw_files':rows,'previous_card':bind(OLD/'O2_DIAGNOSTIC_CARD.json'),'other_previous_cards':[bind(B.parent/'engineering/O2_DIAGNOSTIC_CARD.json')],'non_SUMO_invocation_notes':bind(OLD/'diagnostics/attempt02_release_preflight_invocation.md'),'non_SUMO_invocation_errors':2,'non_SUMO_invocation_consumed_starts':0}
put(B/'prior_attempt_accounting.json',json.dumps(prior,indent=2,sort_keys=True)+'\n')
s=(OLD/'DIAGNOSTIC_CONTRACT.md').read_text().replace('revision02','revision03').replace('attempt02','attempt03').replace('Attempt02','Attempt03')
s=s.replace('Previous diagnostic consumption1 start/8.43560208400595s/13288bytes','Previous diagnostic consumption2 starts/28.542396625998663s/118166bytes').replace('188.43560208400595s and200013288bytes','208.54239662599866s and200118166bytes')
s=s.replace('Before connecting and again before any step, `/usr/sbin/lsof` must show port8819 belongs only to that child PID.','Before connecting, `/usr/sbin/lsof` must show LISTEN port8819 belongs only to that child PID. After connect, require an ESTABLISHED descriptor of that same PID with exact server-to-client endpoint tuple reversed from the connected Python socket. SUMO closes its listener after accepting its one client; postconnect LISTEN is not required.')
s += '\n## Attempt02 failure and attempt03 exact fix\n\nAttempt02 reached an owned listener after18.718785333s and connected TCP, then the obsolete postconnect LISTEN-only gate incorrectly failed. Official1.26 TraCIServer constructor owns a local listening socket that is destroyed after accepting the registered single client; accepted socket remains in mySockets. This lifecycle is reproduced in the Python-only control. New connection_ownership.py checks same child PID + ESTABLISHED state + exact accepted socket4-tuple matching client getsockname/getpeername; no behavior command is used. Preconnect ownership and60s readiness remain unchanged. Parent preflight relative-path and sandbox-bind invocation errors consumed zero SUMO starts and are separately retained in prior accounting.\n'
put(B/'DIAGNOSTIC_CONTRACT.md',s)
# Preserve original user quote; update technical failure/fix without changing authority.
a=json.loads((OLD/'authorization_provenance.json').read_text());a['status']='user_authorized_technical_troubleshooting_pending_exact_review_of_attempt03';a['scope']='same original C seed17 end450, one new attempt03 after review; no automatic retry or scientific changes';a['observable_failure_attempt02']='TCP connected after18.7188s; obsolete postconnect LISTEN-only test failed';a['technical_root_cause_attempt02']='Observer incorrectly required listener persistence after single accepted client; official1.26 closes local listening socket after accepting while retaining accepted socket';a['exact_fix_attempt03']='Preserve preconnect owner gate; postconnect check same child PID ESTABLISHED socket exact reversed client tuple';put(B/'authorization_provenance.json',json.dumps(a,indent=2,sort_keys=True)+'\n')
print(json.dumps({'prior_seconds':prior['wallclock_s'],'prior_bytes':prior['bytes'],'new_SUMO_starts':0}))
