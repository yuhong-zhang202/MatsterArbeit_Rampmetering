"""Seal a completed independent FIX02 audit, retaining capacity failures."""
import argparse,csv,hashlib,json,shutil
from pathlib import Path
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--audit',required=True);ap.add_argument('--card',required=True);a=ap.parse_args();out=B/a.audit;cardpath=Path(a.card);card=json.load(cardpath.open());raw=Path(card['output'])
 def read(n):return json.load((out/(n+'.json')).open())
 summary=read('summary');classes=summary['classes'];expected={'M':3000,'R':500 if card['ramp_veh_h']==750 else 600,'U':300,'X':150}
 assert {r['vehicle_class']:r['planned'] for r in classes}==expected
 assert summary['timesteps']==4200 and summary['summary_reconciliation']['lifecycle_reconciled'] and not summary['warnings'] and not summary['invalid_M_observations']
 assert all(v==0 for v in summary['summary_reconciliation']['anomaly_maxima'].values())
 act=read('actuator_identity');service=read('v15_service_fcd_audit');entrant=read('fix02_entrant_fcd_audit');queue=read('queue_identity');spatial=read('queue_spatial_audit');windows=read('final_command_windows');integral=read('integral_cost_audit');chain=read('operational_chain');pre=read('pre600_comparison');feedback=read('feedback_xml_audit');events=read('event_feedback_audit')
 assert pre['equal'] and feedback['status']=='PASS' and events['status']=='PASS_EVENT_RECONSTRUCTION_IDENTITY'
 assert act['status']==entrant['status']==queue['status']==spatial['status']==integral['status']=='PASS'
 assert service['status']=='PASS_V15_FCD_SERVICE' and not service['mismatches']
 assert entrant['prestep_snapshots']==spatial['prestep_snapshots_checked']==3600 and entrant['post_green_snapshots']==act['counts']['greens']
 assert len(windows)==6
 eligible=[w for w in windows if w['eligible_continuous_supply']]
 capacity='NOT_QUALIFIED' if any(w['engineering_status']=='FAIL' for w in eligible) else 'PASS' if eligible else 'NOT_TESTED'
 for name in ['analyze_fix02.py','analyze_run.py','audit_v15_service.py','write_fix02_gate.py']:
  target=out/(name.removesuffix('.py')+'_source_snapshot.py');assert not target.exists();shutil.copyfile(B/name,target)
 receipt=json.load((raw/'execution_receipt.json').open())
 report=dict(reviewer_role='data_analyst',reviewer_task='/root/development_data_fix02',run_id=card['run_id'],classification='DEVELOPMENT_ONLY_FIX02',data_layer='PASS',safety_and_rule_replay='PASS_OBSERVED_RUN',rate_capability=capacity,traffic_effect='DESCRIPTIVE_ONLY_NOT_ACCEPTANCE',cohort=classes,total_system_time_s=sum(r['scheduled_system_time_observed_total_s'] for r in classes),total_source_wait_s=sum(r['external_wait_observed_total_s'] for r in classes),endpoint_vehicles=len(read('endpoint_vehicles')),pre600=pre,feedback_xml=feedback,entrant_and_post_sensors=entrant,actuator=act,actual_service=service,capacity_windows=windows,queue=queue,queue_spatial=spatial,integral=integral,strict_continuous_30s_shared_episodes=len(chain['shared_episodes']),warnings=summary['warnings'],runtime_wall_s=receipt['wall_s'],raw_payload_bytes=receipt['output_bytes'],card_sha256=sha(cardpath),raw_receipt_sha256=sha(raw/'execution_receipt.json'),gate_script_sha256=sha(Path(__file__)),output_sha256={p.name:sha(p) for p in out.iterdir() if p.is_file()},limits=['SecureGap and actual vehicle dynamics remain conditional on version-bound native TraCI logs; sensors matched to rounded FCD.', 'Rate refusals are not uniquely causal allocations of missed crossings. Every fixed window is retained.', 'No formal inference, sweet-spot threshold or new simulation authorized. Scientific review required before subsequent release.'])
 target=out/'FIX02_DATA_GATE.json'
 with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({k:report[k] for k in ['run_id','data_layer','safety_and_rule_replay','rate_capability','total_system_time_s','total_source_wait_s','endpoint_vehicles']}))
if __name__=='__main__':main()
