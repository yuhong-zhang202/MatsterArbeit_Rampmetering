"""Read guardian receipt/logs and record technical completion, never launch."""
from pathlib import Path
import csv,hashlib,json,re,sys
root=Path.cwd();b=root/'artifacts/formal_development_20261007_v1';run=sys.argv[1];release=b/'RELEASE_FIX02_SEEDS23_42_A03.json'
assert run in json.loads(release.read_text())['cards']
p=b/'receipts'/f'{run}.json';r=json.loads(p.read_text());card=b/'inputs'/run/'card.json';c=json.loads(card.read_text());o=Path(c['output']);sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();errors=[]
for name,v in r['output_manifest'].items():
 if (o/name).stat().st_size!=v['bytes'] or sha(o/name)!=v['sha256']:errors.append(name)
log=(o/'sumo.log').read_text() if (o/'sumo.log').exists() else '';stderr=(o/'worker_stderr.log').read_text()
end=re.search(r'Simulation ended at time: ([0-9.]+)',log)
counts={k:int(re.search(r'\b'+k+r': (\d+)',log).group(1)) if re.search(r'\b'+k+r': (\d+)',log) else None for k in ('Inserted','Running','Waiting')}
svc={}
if (o/'service_windows.csv').exists():
 with (o/'service_windows.csv').open() as f:rows=list(csv.DictReader(f));svc=rows[-1] if rows else {}
x={'run_id':run,'status':r['status'],'command':'.venv/bin/python -B scripts/formal_development_20261007_v1/runner.py launch --card '+str(card.relative_to(root))+' --release '+str(release.relative_to(root)),'permission_path':'require_escalated local TraCI approved','card_sha256':sha(card),'receipt_sha256':sha(p),'wall_s':r['wall_s'],'output_bytes':r['output_bytes'],'new_raw_bytes':r['new_raw_bytes'],'manifest_files_verified':len(r['output_manifest']),'manifest_errors':errors,'return_code':r['return_code'],'sumo_log_end_s':float(end.group(1).rstrip('.')) if end else None,'sumo_log_counts':counts,'logged_service_summary':svc,'entrant_coverage':json.loads((o/'fix02_entrant_coverage.json').read_text()) if (o/'fix02_entrant_coverage.json').exists() else None,'sumo_error_bytes':(o/'sumo_error.log').stat().st_size if (o/'sumo_error.log').exists() else None,'sumo_stderr_bytes':(o/'sumo_stderr.log').stat().st_size if (o/'sumo_stderr.log').exists() else None,'retained_warning':'TraCI API UserWarning retained' if 'UserWarning' in stderr else None,'next_gate':'Independent persisted integrity/data/safety/rule gate before next authorized run. No final data/rate qualification inferred here.'}
with (b/'engineering'/f'{run}_TECHNICAL_COMPLETION.json').open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(json.dumps({k:x[k] for k in ('run_id','status','wall_s','output_bytes','manifest_files_verified','manifest_errors','sumo_log_end_s','sumo_log_counts','logged_service_summary')}))
assert not errors and r['status']=='COMPLETED' and x['sumo_log_end_s']==4200
