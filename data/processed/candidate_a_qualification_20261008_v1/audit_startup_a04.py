"""Read-only zero-step A04 failure audit; no SUMO/TraCI import or launch."""
import ast,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
RAW=ROOT/'data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A04'
ART=ROOT/'artifacts/candidate_a_qualification_20261008_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
g=read(RAW/'guardian_receipt.json');w=read(RAW/'outputs/worker_receipt.json');f=read(RAW/'outputs/failure_snapshot.json');offline=read(ART/'engineering/PHASE_A_A04_OFFLINE_RECEIPT.json')
verified={}
for name,h in g['files_sha256'].items():
 p=RAW/'outputs'/name;assert sha(p)==h,name;verified[str(p.relative_to(ROOT))]=h
assert {str(p.relative_to(RAW/'outputs')) for p in (RAW/'outputs').rglob('*') if p.is_file()}==set(g['files_sha256'])
ledger=[json.loads(x) for x in (ART/'engineering/EXECUTION_LEDGER.jsonl').read_text().splitlines() if x.strip()]
entry=[x for x in ledger if x['run_id']==w['run_id']];assert len(entry)==1 and entry[0]==g
card=read(RAW/'outputs/snapshots/card.json');assert sha(RAW/'outputs/snapshots/card.json')==w['card_sha256']==g['card_sha256']
for name,h in card['sources_sha256'].items():assert sha(RAW/'outputs/snapshots'/name)==h==offline['tested_sources_sha256'][name]
card_checks=[]
for record in offline['cards']:
 p=ROOT/record['card_path'];c=read(p);assert sha(p)==record['card_sha256']
 assert c['qMain']==3600 and c['qRamp']==900 and c['seed']==17 and c['step_s']==1 and c['horizon_s']==4200
 assert c['activation_s']==1200 and c['service_windows']==[[b,b+300] for b in range(1200,3000,300)] and c['tracking_tolerance']==.1
 assert c['fixed_command_veh_h']==record['rate'] and c['sources_sha256']==card['sources_sha256']
 for name,h in c['prepared_input_sha256'].items():assert sha(ROOT/name)==h
 for name,h in c['protected_baseline_sha256'].items():assert sha(ROOT/name)==h
 card_checks.append(dict(rate=record['rate'],card_sha256=sha(p)))
counts={}
for name in ['phase_steps.csv','cycles.csv','crossings.csv','feedback_updates.csv','detector_vehicle_events.csv']:
 with (RAW/'outputs'/name).open() as stream:
  r=csv.DictReader(stream);assert r.fieldnames;counts[name]=sum(1 for _ in r)
assert all(n==0 for n in counts.values())
assert g['worker_started'] and w['sumo_started'] and g['worker_exit_code']==1
assert w['status']==f['status']=='ABORTED_TECHNICAL' and "'PosixPath' object is not callable" in w['error']==f['error']
for d in [w,f]:
 assert d['last_completed_step_s']==d['last_accounted_s']==0 and d['accounting_complete']
 assert d['accounting_status']=='RECONCILED_COMPLETED_PREFIX' and d['unaccounted_completed_interval_s'] is None
 assert d['accounting']['C']==d['accounting']['C_applied']==d['accounting']['E']==d['accounting']['N']==0
assert w['cycle_count']==w['prefix_total_crossings']==0 and w['prefix_crossings_by_segment']=={'PRECONTROL':0,'EXTERNAL_HOLD':0}
# Independently exercise only the preserved pure accounting status helper.
source=RAW/'outputs/snapshots/scripts/candidate_a_qualification_20261008_v1/worker.py'
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='accounting_coverage')
ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
assert ns['accounting_coverage'](5,4)['accounting_status']=='UNRECONCILED_UNSUPPORTED'
assert ns['accounting_coverage'](5,4)['qualification_accounting_supported'] is False
assert ns['accounting_coverage'](5,4)['unaccounted_completed_interval_s']==[4,5]
assert ns['accounting_coverage'](0,0)['accounting_complete'] is True
result=dict(classification='INDEPENDENT_STARTUP_FAILURE_AUDIT_NOT_TRAFFIC_RESULT',run_id=w['run_id'],base_commit=card['base_commit'],disposition='FAILURE_PRESERVATION_AND_ZERO_STEP_ACCOUNTING_VERIFIED',actual_worker_attempts=1,actual_SUMO_starts=1,completed_simulation_steps=0,completed_cycles=0,csv_rows=counts,C=0,C_applied=0,E=0,N=0,qualification_accounting_note='Flag true describes an empty reconciled prefix only; not overall qualification.',safety_qualification='NOT_TESTED',phase_qualification='NOT_TESTED',service_qualification='NOT_TESTED',range_qualification='NOT_TESTED',effective_qualification_runs=0,service_windows_observed=0,relative_tracking_error=None,error=w['error'],failure_original_preserved=True,manifest_files_verified=len(verified),offline_A04_card_checks=card_checks,post_advance_coverage_helper_known_cases='PASS',limitations=['No runtime safety/phase/rate evidence exists at zero steps.','A04 source only; pending A05 callback repair is not tested by this audit.','No FCD traffic file was produced; no fabricated zero-flow service window.'],bindings={**verified,str((RAW/'guardian_receipt.json').relative_to(ROOT)):sha(RAW/'guardian_receipt.json'),str((ART/'engineering/PHASE_A_A04_OFFLINE_RECEIPT.json').relative_to(ROOT)):sha(ART/'engineering/PHASE_A_A04_OFFLINE_RECEIPT.json'),'analysis_script_sha256':sha(Path(__file__))})
p=OUT/'A04_STARTUP_FAILURE_DATA_AUDIT.json';data=json.dumps(result,indent=2)+'\n'
if p.exists():assert p.read_text()==data,'audit exists with different content; preserve before revision'
else:
 with p.open('x') as stream:stream.write(data)
print(json.dumps({k:v for k,v in result.items() if k not in ['bindings','offline_A04_card_checks']},indent=2))
