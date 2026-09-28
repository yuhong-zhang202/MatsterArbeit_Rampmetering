#!/usr/bin/env python3
"""New isolated technical attempt; never edit attempt01 or start a simulator."""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
B=Path(__file__).absolute().parent;OLD=B.parent/'engineering'
def put(p,s):
 p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('x') as f:f.write(s)
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for p in (OLD/'inputs').iterdir():
 s=p.read_text().replace(str(OLD),str(B)).replace('/O2_C_S17_450_attempt1/outputs/','/O2_C_S17_450_attempt2/outputs/')
 put(B/'inputs'/p.name,s)
for name in ['executor_tail.txt','static_validate.py','DIAGNOSTIC_CONTRACT.md','diagnostic_gate_contract.json']:
 s=(OLD/name).read_text().replace('O2_C_S17_450_attempt1','O2_C_S17_450_attempt2')
 if name=='DIAGNOSTIC_CONTRACT.md':
  s=s.replace('revision01','revision02').replace('8 seconds','60 seconds')
  s=s.replace('No second run, retry, build, GUI, geometry/demand/model/program change, parameter search or statistical/formal conclusion is authorized.','The user subsequently authorized evidence-based technical troubleshooting until this same diagnostic completes. Attempt01 remains consumed and preserved. This card releases only one new attempt02 after exact review; no automatic retry, build, GUI, geometry/demand/model/program change, parameter search or statistical/formal conclusion.')
  s=s.replace('The user condition is recorded verbatim in authorization_provenance.json.','The original user condition and subsequent technical-troubleshooting authorization are recorded in authorization_provenance.json.')
  s += '\n## Revision02 technical change and preserved failure\n\nAttempt01 started SUMO once but never obtained a TraCI session or stepped traffic. Its101 exact lsof queries returned no listener before the8s gate; observer then terminated SUMO. A Python TCP control with the same lsof query/sanitized environment passed PID detection and loopback, so the syntax/general local visibility hypothesis is disfavored. System logs show OS validation-category warnings for that exact SUMO PID, not proof of a causal security block. The deeper startup cause remains Unknown. This attempt tests the explicit hypothesis that8s was insufficient for startup: wait up to60s within the unchanged180s per-attempt total watchdog. At2s with no listener, capture ps and one1-second startup sample (5s diagnostic subprocess timeout); preserve diagnostic failures too. No traffic step has occurred during these OS observations. Never disable code signing, policy, sandboxing, or loopback ownership checks.\n\nThe exact original SUMO binary and traffic inputs remain unchanged. Previous diagnostic consumption1 start/8.43560208400595s/13288bytes is reconciled; attempt02 adds at most1 start/180s/200MB observed output. This card cumulative stop-lines are188.43560208400595s and200013288bytes. Further attempts require a distinct evidence-based card and exact review under the continuing user instruction, never automatic repeats.\n'
 put(B/name,s)
s=(OLD/'runtime_executor.py').read_text().replace('O2_C_S17_450_attempt1','O2_C_S17_450_attempt2')
s=s.replace("'total_monitored_s':180", "'total_monitored_s':188.43560208400595").replace("'total_observed_bytes':200000000", "'total_observed_bytes':200013288")
s=s.replace("if run.parent.exists():require(not list(run.parent.iterdir()),'unregistered prior attempt')", "if run.parent.exists():require({p.name for p in run.parent.iterdir()}=={'O2_C_S17_450_attempt1'},'prior inventory mismatch')\n prior=run.parent/'O2_C_S17_450_attempt1'\n require(digest(prior/'execution_receipt.json')=='ceb91d360a1dea201b5d5151abe0cb0880c57b20768066d8a6923307e1e37114' and size(prior)==13288,'prior evidence changed')")
s=s.replace("binding(a.approval),timeout=180,cap=200000000)", "binding(a.approval),prior_time=8.43560208400595,prior_bytes=13288,timeout=180,cap=200000000)")
put(B/'runtime_executor.py',s)
s=(OLD/'observer.py').read_text();a=s.index('   # Prove the loopback listener');z=s.index('   c=traci.connect',a)
s=s[:a]+"   from startup_probe import wait_for_owned_listener\n   wait_for_owned_listener(p,out,run)\n"+s[z:]
put(B/'observer.py',s)
put(B/'tests/test_offline.py',(OLD/'tests/test_offline.py').read_text())
put(B/'references/source_bindings.json',(OLD/'references/source_bindings.json').read_text())
oldraw=B.parents[2]/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt1'
prior={'previous_card':bind(OLD/'O2_DIAGNOSTIC_CARD.json'),'previous_receipt':bind(oldraw/'execution_receipt.json'),'previous_output_manifest':bind(oldraw/'output_manifest.json'),'previous_raw_files':[bind(p) for p in sorted(oldraw.rglob('*')) if p.is_file()],'consumed_starts':1,'wallclock_s':8.43560208400595,'bytes':13288,'traffic_steps':0,'successful_TraCI_sessions':0,'status':'technical_startup_failure_preserved'}
put(B/'prior_attempt_accounting.json',json.dumps(prior,indent=2,sort_keys=True)+'\n')
