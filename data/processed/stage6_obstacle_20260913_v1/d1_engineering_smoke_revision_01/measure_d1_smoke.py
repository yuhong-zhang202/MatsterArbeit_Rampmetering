"""Smoke-only technical evidence, including failed attempts; no science entry point."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
from src.analysis import stage6_h2_measurement as m
out=Path(__file__).resolve().parent
card=x.validate_launch_card(out/'approved_launch_card.json',require_approval=True)
entry=card['attempts'][0];mp=o.verify_binding(entry['materialization']);mat=o.read_json(mp);directory=mp.parent
rp=directory/'execution_receipt.json';r=o.read_json(rp)
assert r['attempt_id']=='S6_V1_ML_S17_attempt1' and r['role']=='smoke' and r['evidence_scope']=='real_executed_output'
assert r['run_id']=='S6_V1_ML_S17' and r['version']=='V1' and r['condition']=='ML' and str(r['seed'])=='17'
assert r['materialization']==entry['materialization'] and r['argv']==entry['argv'] and r['launch_card']==o.bind(out/'approved_launch_card.json')
assert r['launch_payload_sha256']==x.payload_sha(card)
source_map=o.read_json(o.verify_binding(r['executed_source_map']))
assert all(source_map[k]==r[k] for k in source_map)
for field in ('binary','network','source_manifest','files'):assert r[field]==mat[field]
for binding in r['implementation_bindings']:o.verify_binding(binding)
expected=x.expected_outputs(mat);assert set(r['output_bindings'])==set(expected)
for name,binding in r['output_bindings'].items():assert o.verify_binding(binding)==expected[name]
event=o.read_json(o.verify_binding(r['journal_event']))
assert event['metadata']['output_bindings']==r['output_bindings']
assert event['metadata']['required_xml_validation']==r['required_xml_validation']
assert x.validate_required_xml_outputs(mat)==r['required_xml_validation']
header=expected['tripinfo.xml'].read_text()[:65536]
fragments=re.findall(r'<sumoConfiguration\b[^>]*>.*?</sumoConfiguration>',header,re.S);assert len(fragments)==1
config=ET.fromstring(fragments[0])
for tag,value in (('seed','17'),('step-length','1'),('end','2700'),('net-file',mat['network']['path']),('route-files',mat['files']['demand.rou.xml']['path']),('tripinfo-output',str(expected['tripinfo.xml']))):
 elements=config.findall('.//'+tag);assert len(elements)==1 and elements[0].get('value')==value
net=ET.parse(o.verify_binding(mat['network'])).getroot()
lengths={lane.get('id'):float(lane.get('length')) for lane in net.findall('.//lane')}
demand=ET.parse(o.verify_binding(mat['files']['demand.rou.xml'])).getroot()
counts={g:int(next(f.get('number') for f in demand.findall('flow') if f.get('id')==g+'_flow')) for g in 'MRUX'}
ids=m.planned_ids(counts);trips=m.read_tripinfo(expected['tripinfo.xml'],ids)
trajectories=m.read_fcd(expected['fcd.xml'],ids,trips,lengths)
tls=m.read_tls(expected['tls_states.xml'])
per_id=[]
for vid in sorted(ids):
 t=trips[vid];samples=trajectories[vid]
 row={'vehicle_id':vid,'group':m.group(vid),'depart':t['depart'],'arrival':t['arrival'],'departDelay':t['departDelay'],'departLane':t['departLane'],'departPos':t['departPos'],'entered':t['depart']>=0,'arrived':t['arrival']>=0,'sample_count':len(samples),'last_confirmed_label':samples[-1].time if samples else None,'endpoint2700_state':'arrived_before_endpoint' if 0<=t['arrival']<2700 else 'in_network' if t['depart']>=0 else 'outside','domains':{}}
 if m.group(vid)=='M':
  if t['depart']>=0:assert t['departLane'] in ('main_up_0','main_up_1') and abs(t['departPos']-100)<=.02
  for domain,edge,a,b in (('feeder','main_up',200,1200),('common','main_down',100,700)):
   lanes={edge+'_0',edge+'_1'};start=m.crossing(samples,lanes,a);end=m.crossing(samples,lanes,b)
   status='observed_traversal' if start is not None and end is not None else 'not_observed_entry' if start is None else 'right_censored' if samples and samples[-1].time==2699 and samples[-1].lane in lanes and samples[-1].pos<b and t['arrival']<0 else 'unresolved_missing_exit'
   row['domains'][domain]={'entry_bracket':start,'exit_bracket':end,'state':status,'inside_sample_count':sum(s.lane in lanes and a<=s.pos<b for s in samples)}
 per_id.append(row)
x.exclusive_json(out/'smoke_per_id_technical_records.json',{'scope':'smoke diagnostics only; no scientific cohort or rule denominator','records':per_id})
ms=[row for row in per_id if row['group']=='M']
coverage={domain:{'M_planned':len(ms),'with_inside_samples':sum(row['domains'][domain]['inside_sample_count']>0 for row in ms),'observed_traversal':sum(row['domains'][domain]['state']=='observed_traversal' for row in ms),'states':{state:sum(row['domains'][domain]['state']==state for row in ms) for state in ('observed_traversal','not_observed_entry','right_censored','unresolved_missing_exit')}} for domain in ('feeder','common')}
links=[dict(c.attrib) for c in net.findall('connection') if c.get('tl')=='urban_tls']
diagnostics=[{'role':name,'line':i,'text':line} for name in ('sumo.log','sumo_error.log','process.stderr.log') for i,line in enumerate(expected[name].read_text().splitlines(),1) if re.search(r'\b(?:Error|Warning)\b',line)]
assert r['execution_status']=='technical_failure' and r['reason']=='diagnostic_anomaly'
report={'scope':'D1 real smoke technical evidence only; failure retained','engineering_recommendation':'FAIL_STOP','execution_status':r['execution_status'],'failure_reason':r['reason'],'exit_code':r['exit_code'],'diagnostics':diagnostics,'source_identity_check':'passed_for_smoke_role_only; not scientific qualification','runtime_header_check':'passed','required_xml_validation':r['required_xml_validation'],'M_insertion':{'planned':len(ms),'entered':sum(v['entered'] for v in ms),'departPos_min':min(v['departPos'] for v in ms if v['entered']),'departPos_max':max(v['departPos'] for v in ms if v['entered']),'misplaced_count':0,'reported_delay_max_s':max(v['departDelay'] for v in ms if v['entered']),'registered_reported_inlet_qualification':m.inlet_qualification(trips,ids),'no_additional_blocking_claim':False},'domain_coverage':coverage,'raw_time_grid':{'FCD_frames':2700,'TLS_frames':len(tls),'first_label':0,'last_label':2699,'simulation_end_from_log':'2700.00','endpoint_states':{str(t):m.endpoint(ids,trips,t) for t in (1500,2700)}},'FCD_sample_count':sum(len(s) for s in trajectories.values()),'TLS_links_from_bound_loaded_network':links,'per_id_records':o.bind(out/'smoke_per_id_technical_records.json'),'execution_receipt':o.bind(rp),'executed_source_map':r['executed_source_map'],'approved_launch_card':o.bind(out/'approved_launch_card.json'),'prelaunch_receipt':o.bind(out/'prelaunch_receipt.json'),'budget_counters':x.Journal(Path(card['budget_journal_directory'])).counters(),'final_attempt_directory_bytes':x.attempt_bytes(directory),'SUMO_starts':1,'netconvert':0,'TraCI':0,'GUI':0,'validation_starts':0,'retry_starts':0,'science_entrypoint_calls':0,'main352_rows_written':0,'sensitivity14_rows_written':0,'smoke_acceptance_gate_written':False,'next_action':'stop for engineering/data/science failure review; no retry or validation released'}
x.exclusive_json(out/'smoke_technical_receipt.json',report)
x.exclusive_json(out/'d1_manifest.json',{'smoke_technical_receipt':o.bind(out/'smoke_technical_receipt.json'),'archive_files':[o.bind(p) for p in sorted(directory.rglob('*')) if p.is_file()],'evidence_files':[o.bind(p) for p in sorted(out.iterdir()) if p.is_file()],'budget_events':[o.bind(p) for p in sorted(Path(card['budget_journal_directory']).glob('event_*.json'))],'engineering_recommendation':'FAIL_STOP','science_use_prohibited':True})
print(o.bind(out/'d1_manifest.json'));print(coverage);print(report['M_insertion']);print(report['raw_time_grid']);print(report['FCD_sample_count'],report['final_attempt_directory_bytes'])
