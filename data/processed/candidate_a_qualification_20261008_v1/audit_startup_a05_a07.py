"""Bounded A05 startup-failure preservation and A07 interface delta audit."""
import csv,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
ART=ROOT/'artifacts/candidate_a_qualification_20261008_v1';RAW=ROOT/'data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A05'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
g=read(RAW/'guardian_receipt.json');w=read(RAW/'outputs/worker_receipt.json');f=read(RAW/'outputs/failure_snapshot.json')
for name,h in g['files_sha256'].items():assert sha(RAW/'outputs'/name)==h,name
assert set(g['files_sha256'])=={str(p.relative_to(RAW/'outputs')) for p in (RAW/'outputs').rglob('*') if p.is_file()}
ledger=[json.loads(x) for x in (ART/'engineering/EXECUTION_LEDGER.jsonl').read_text().splitlines() if x.strip()]
assert len([x for x in ledger if x['run_id']==w['run_id']])==1 and next(x for x in ledger if x['run_id']==w['run_id'])==g
assert {x['run_id'] for x in ledger}=={'CA_FIXED_R300_S17_A04','CA_FIXED_R300_S17_A05'}
assert all(x['worker_started'] for x in ledger)
counts={}
for name in ['phase_steps.csv','cycles.csv','crossings.csv','feedback_updates.csv','detector_vehicle_events.csv']:
 with (RAW/'outputs'/name).open() as stream:counts[name]=sum(1 for _ in csv.DictReader(stream))
assert all(x==0 for x in counts.values())
assert g['worker_exit_code']==1 and w['sumo_started'] and w['status']==f['status']=='ABORTED_TECHNICAL'
for d in [w,f]:
 assert d['last_completed_step_s']==d['last_accounted_s']==0 and d['accounting_complete']
 assert all(d['accounting'][k]==0 for k in ['C','C_applied','E','N'])
assert w['cycle_count']==0
stderr=(RAW/'outputs/sumo_stderr.log').read_text();assert "no declaration found for element 'routes'" in stderr and 'SUMO_HOME is not set properly' in stderr
warnings=[x for x in stderr.splitlines() if 'only loops backs to itself' in x];assert len(warnings)==17
trace=[json.loads(x) for x in (RAW/'outputs/startup_trace.jsonl').read_text().splitlines() if x.strip()];assert trace and trace[-1]['outcome']=='CONNECTED' and all(x['outcome']=='FAILED' for x in trace[:-1])
reject=[json.loads(x) for x in (ART/'PRELAUNCH_REJECTIONS.jsonl').read_text().splitlines() if x.strip()];assert len(reject)==1 and reject[0]['worker_starts']==reject[0]['sumo_starts']==0
repair=read(ART/'engineering/R300_A07_REPAIR_OFFLINE_RECEIPT.json');cards=read(ART/'engineering/PHASE_A_A07_FINAL_CARDS.json')['cards'];oldcard=read(RAW/'outputs/snapshots/card.json')
for p,h in repair['tested_sources_sha256'].items():assert sha(ROOT/p)==h
for r in cards:
 c=read(ROOT/r['card_path']);assert sha(ROOT/r['card_path'])==r['card_sha256']
 assert c['sources_sha256']==repair['tested_sources_sha256'] and c['protected_baseline_sha256']==oldcard['protected_baseline_sha256']
 assert c['seed']==17 and c['qMain']==3600 and c['qRamp']==900 and c['step_s']==1 and c['activation_s']==1200
 assert c['tracking_tolerance']==.1 and c['service_windows']==[[b,b+300] for b in range(1200,3000,300)] and c['feedback']==oldcard['feedback']
 for p,h in c['prepared_input_sha256'].items():assert sha(ROOT/p)==h
 config=ET.parse(Path(c['package'])/'scenario.sumocfg');assert config.find('./report/xml-validation').get('value')=='always'
 assert Path(c['package'],'demand.rou.xml').read_bytes()==Path(oldcard['package'],'demand.rou.xml').read_bytes()
for p,h in oldcard['protected_baseline_sha256'].items():assert sha(ROOT/p)==h
home=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo');schemas={name:sha(home/'data/xsd'/name) for name in ['routes_file.xsd','additional_file.xsd','sumoConfiguration.xsd']}
j=dict(classification='INDEPENDENT_STARTUP_FAILURE_AND_INTERFACE_DELTA_NOT_TRAFFIC_RESULT',run_id=w['run_id'],disposition='FAILURE_PRESERVED_A07_INTERFACE_DELTA_REVIEWED',actual_attempts_total=2,actual_SUMO_starts_total=2,effective_runs_total=0,prelaunch_metadata_rejection_starts=0,completed_steps_this_run=0,cycles_this_run=0,csv_rows=counts,C=0,C_applied=0,E=0,N=0,service_windows=0,tracking_error=None,safety_phase_service_range='NOT_TESTED',accounting_note='Empty completed prefix is reconciled; qualification_accounting_supported true is not overall qualification.',failure_error=w['error'],native_failure="Error: no declaration found for element 'routes'; missing local SUMO_HOME schema lookup",native_self_loop_warnings_count=17,native_self_loop_warnings_interpretation='Program initialization warnings only; not collisions, unsafe traffic transitions, or measured service failure.',startup_trace_callback='A05 callable records212 failed attempts then213 CONNECTED; SUMO schema loading later closes connection before any step. Former PosixPath-callable error absent',A07_delta='Production Popen receives explicit env through a tested launch wrapper; child SUMO_HOME restored to protected runner installed share/sumo path; local schema existence and hashes logged, xml-validation always unchanged; no installation/phase/mapping/safety/timing changes.',A07_sources=repair['tested_sources_sha256'],A07_cards=cards,installed_schema_sha256=schemas,A07_actual_runtime_verification='NOT_RUN_BY_THIS_AUDIT',bindings={str((RAW/'guardian_receipt.json').relative_to(ROOT)):sha(RAW/'guardian_receipt.json'),str((RAW/'outputs/failure_snapshot.json').relative_to(ROOT)):sha(RAW/'outputs/failure_snapshot.json'),str((RAW/'outputs/worker_receipt.json').relative_to(ROOT)):sha(RAW/'outputs/worker_receipt.json'),str((ART/'PRELAUNCH_REJECTIONS.jsonl').relative_to(ROOT)):sha(ART/'PRELAUNCH_REJECTIONS.jsonl'),str((ART/'engineering/R300_A07_REPAIR_OFFLINE_RECEIPT.json').relative_to(ROOT)):sha(ART/'engineering/R300_A07_REPAIR_OFFLINE_RECEIPT.json'),'manifest_files_verified':len(g['files_sha256']),'script_sha256':sha(Path(__file__))})
p=OUT/'A05_FAILURE_A07_DELTA_DATA_AUDIT.json';data=json.dumps(j,indent=2)+'\n'
if p.exists():assert p.read_text()==data,'Preserve prior audit; changed inputs require a new audit version'
else:
 with p.open('x') as stream:stream.write(data)
print(p,sha(p));print('43 raw files bound; 2 physical starts /0steps/0effective; A07 delta source/card validation complete')
