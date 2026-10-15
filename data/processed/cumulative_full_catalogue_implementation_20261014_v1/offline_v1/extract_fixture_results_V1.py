"""Independent frozen synthetic-file extraction. Never imports production Ledger."""
import importlib.util,json,pathlib,hashlib
from fractions import Fraction
ROOT=pathlib.Path.cwd();OUT=ROOT/'data/processed/cumulative_full_catalogue_implementation_20261014_v1/offline_v1'
spec=importlib.util.spec_from_file_location('independent_fixture_reader',ROOT/'tests/cumulative_full_catalogue_audit_20261014/test_audit.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
results={}
for name,end in [('fixed750_1296_True_False',1296),('fixed750_1210_False_False',1210),('fixed750_1210_False_True',1210),('dynamic_commands_1218_True_False',1218),('real_alinea_1296_True_False',1296)]:
 f=mod.load(name);a,p=mod.run(f,end);result={'accounting':a,'phase_audit':p,'independent_state_transition_entry_count':len(f['entries']),'scope':'SYNTHETIC_REAL_HELPER_NO_NATIVE_FCD_PHYSICS_OR_EOF_INTEGRATION'}
 if f['feedback']:result['feedback']=mod.core.audit_feedback(f['feedback'],f['events'],a,end)
 results[name]=result
# Independent exact arithmetic only, not exported fake traffic or production.
reqs={1200:300,1201:750,1226:900,1237:300};r=300;C=Fraction(0);N=0;end=1200;packets=[]
for t in range(1200,1266):
 if t in reqs:r=reqs[t]
 if t==end:
  scores={T:C-N+Fraction(r*T,3600)-2 for T in range(8,25)};T=min(scores,key=lambda p:(abs(scores[p]),-p));end=t+T;packets.append({'begin_s':t,'planned_end_s':end,'period_s':T,'request':r,'C_fraction':str(C),'N_assumed':N})
 C+=Fraction(r,3600)
 if t+1==end:N+=2
results['original_four_command_arithmetic_only']={'requests':reqs,'observed_traffic':None,'C1266_fraction':str(C),'N_assumed_complete_quota':N,'selections':packets,'note':'Nominal two-car completion assumed; no vehicle or setter simulation. Last packet may be partial.'}
with (OUT/'INDEPENDENT_FIXTURE_RESULTS_V1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
inputs={}
for name,_ in [('fixed750_1296_True_False',1296),('fixed750_1210_False_False',1210),('fixed750_1210_False_True',1210),('dynamic_commands_1218_True_False',1218),('real_alinea_1296_True_False',1296)]:
 for n in ('pre_steps.jsonl','post_steps.jsonl','command_events.jsonl','step_ack.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl','yellow_scope.jsonl','feedback_events.jsonl'):
  p=mod.BASE/name/n
  if p.is_file():inputs[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
with (OUT/'USED_FIXTURE_INPUT_BINDINGS_V1.json').open('x') as f:json.dump({'files':inputs,'scope':'USED_SYNTHETIC_SEAMS_ONLY_NO_NATIVE_RAW'},f,indent=2);f.write('\n')
print('FIXTURE_EXTRACTION_PASS',len(inputs),'original_requested_C',C)
