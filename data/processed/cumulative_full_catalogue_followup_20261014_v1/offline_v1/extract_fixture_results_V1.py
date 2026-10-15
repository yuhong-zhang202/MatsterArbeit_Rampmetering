"""Frozen fake-helper inputs only; independent reused parser/math, no Ledger."""
import json,pathlib,sys,importlib.util,hashlib
ROOT=pathlib.Path.cwd();sys.path.insert(0,str(ROOT));OUT=ROOT/'data/processed/cumulative_full_catalogue_followup_20261014_v1/offline_v1'
spec=importlib.util.spec_from_file_location('independent_loader',ROOT/'tests/cumulative_full_catalogue_audit_20261014/test_audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.BASE=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/revision01/synthetic_fixture'
from scripts.cumulative_full_catalogue_followup_audit_20261014_v1.scope import terminal_scope,PARTIAL,COMPLETE
result={};inputs={}
for name in ('dynamic_commands','real_alinea'):
 f=m.load(name);a,ph=m.run(f,1296)
 status=PARTIAL if not a['cycles'][-1]['completed'] else COMPLETE
 result[name]={'accounting':a,'phase_audit':ph,'terminal':terminal_scope({'status':status,'error':''},1296,1296,a,set()),'entries_independent_state_transitions':len(f['entries']),'scope':'SYNTHETIC_NATIVE_HELPER_INTERFACE_NOT_NATIVE_VEHICLE_PHYSICS_OR_FULL_AUDIT'}
 if name=='real_alinea':result[name]['feedback']=m.core.audit_feedback(f['feedback'],f['events'],a,1296)
 for n in ('pre_steps.jsonl','post_steps.jsonl','command_events.jsonl','step_ack.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl','feedback_events.jsonl'):
  p=m.BASE/name/n
  if p.exists():inputs[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
with (OUT/'INDEPENDENT_FIXTURE_RESULTS_V1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
with (OUT/'USED_FIXTURE_INPUT_BINDINGS_V1.json').open('x') as f:json.dump({'files':inputs,'scope':'FROZEN_SYNTHETIC_USED_FIELDS_ONLY'},f,indent=2);f.write('\n')
for name,v in result.items():print(name,v['accounting']['accounting'],'apps',v['accounting']['applications'],'lastcycle',v['accounting']['cycles'][-1], 'requests_unapplied',v['accounting']['requests_without_observed_application'])
