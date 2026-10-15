"""Post-run derived observations; never changes the frozen audit verdict."""
import sys,json,time,importlib.util,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT));OUT=Path(__file__).parent
from scripts.natural_actuator_qualification_20261015_v1 import actual,measurements
from scripts.natural_service_audit_20261015_v1.actual import audit as arithmetic
spec=importlib.util.spec_from_file_location('observation_only',OUT/'observational_scan.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
card=json.loads((ROOT/'artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1/QUAL_NATURAL_ALINEA_R900_S17_01/card.json').read_text())
raw=ROOT/'data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_01/outputs';receipt=json.loads((raw/'bridge_receipt.json').read_text());last=receipt['last_completed_s'];package=Path(card['package']);network=Path(__import__('xml.etree.ElementTree',fromlist=['']).parse(package/'scenario.sumocfg').getroot().find('input/net-file').get('value'))
r={'classification':'DERIVED_OBSERVED_PREFIX_ONLY_ORIGINAL_AUDIT_UNKNOWN_RETAINED','qualified':False,'scope':'No change to runtime, safety predicates or frozen native audit','domains':{}}
def run(name,fn):
 try:r['domains'][name]=fn()
 except Exception as e:r['domains'][name]={'status':'UNKNOWN','reason':type(e).__name__+':'+str(e)}
t=time.monotonic();trips=actual.records(raw/'tripinfo.xml','tripinfo');scan=obs.scan(raw,receipt,network,trips)
r['scan_elapsed_s']=time.monotonic()-t
files={name:actual.lines(raw/name,True) for name in ('command_events.jsonl','feedback_events.jsonl','admission.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl')}
files.update({'pre_steps.jsonl':scan['pre'],'post_steps.jsonl':scan['post'],'step_ack.jsonl':scan['acks']})
run('pure_arithmetic',lambda:arithmetic(actual.accounting_view(receipt,files)))
run('feedback_XML',lambda:measurements.feedback_xml(raw,files['feedback_events.jsonl'],last))
run('phase_yellow',lambda:actual.phase_and_yellow(raw,receipt,scan,card))
run('setters',lambda:actual.setter_journal(raw,last,receipt))
run('cohort',lambda:measurements.cohort(package/'demand.rou.xml',trips,scan['observed'],last,actual.records(raw/'sumo_summary.xml','step'),scan['endpoint']))
run('queue_XML',lambda:measurements.queue_xml(raw/'queues.xml',last))
r.update(last_ACK=last,independent_entries=scan['entries'],body_censored_ids=receipt['body_censored_ids'],body_rows_checked=scan['body_rows'],populations_checked=scan['populations'],arrivals=scan['arrivals'],alarms=scan['alarms'],missing=scan['missing'],advisories=scan['advisories'],constraints=scan['constraints'],six_windows=measurements.windows(scan['post'],last),queue_rows=scan['queue_rows'],per_step=scan['post'][600:],current_gap_terminal=list(obs.posts(raw/'post_steps.jsonl'))[-1]['post_native_receiver_decision'],guardian=json.loads((raw.parent/'guardian_receipt.json').read_text()),native_final_logs=receipt['final_logs'])
# Full native source is untouched; this observation preserves STOP as an alarm.
(OUT/'DERIVED_OBSERVED_PREFIX_V1.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
print(json.dumps({'scan_elapsed_s':r['scan_elapsed_s'],'domains':{k:(v.get('status') if isinstance(v,dict) else type(v).__name__) for k,v in r['domains'].items()},'entries':scan['entries'],'alarms':scan['alarms'],'constraints':scan['constraints']}))
