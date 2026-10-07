"""Bounded failed-attempt evidence audit; no 4200s cost imputation."""
import argparse,csv,json,hashlib,sys
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
import analyze_run as D

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--card',required=True);ap.add_argument('--receipt',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 cp=Path(a.card);card=json.loads(cp.read_text());raw=Path(card['output']);receipt=json.loads(Path(a.receipt).read_text());out=Path(a.out);out.mkdir()
 sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
 assert sha(cp)==receipt['card_sha256']
 for n,v in receipt['output_manifest'].items():assert (raw/n).stat().st_size==v['bytes'] and sha(raw/n)==v['sha256'],n
 for n,h in card['input_sha256'].items():assert sha(Path(card['package'])/n)==h,n
 source={n:{'matches_run_card':sha(n)==h,'expected_sha256':h,'observed_sha256':sha(n)} for n,h in card['source_sha256'].items()}
 rows=D.read_csv(raw/'controller_steps.csv');q=D.read_csv(raw/'queue_override.csv');assert len(rows)==len(q)==654
 bytime={int(float(e.get('time'))):{v.get('id'):dict(v.attrib) for v in e} for e in D.A.records(raw/'fcd.xml.gz','timestep')};assert len(bytime)==654 and sorted(bytime)==list(range(654))
 mismatches=[];maxpos=maxspeed=0.;watched={'shared_approach_0',':urban_diverge_1_0','ramp_storage_0'}
 for t in range(600,654):
  now={i:v for i,v in bytime[t-1].items() if v['lane'] in watched};obs=json.loads(q[t]['observed_vehicle_records_json']);assert {v['id'] for v in obs}==set(now),(t,'mapped_population')
  for v in obs:
   actual=now[v['id']];assert v['lane']==actual['lane'];dp=abs(v['front_m']-float(actual['pos']));ds=abs(v['speed_m_s']-float(actual['speed']));assert dp<=.005001 and ds<=.005001;maxpos=max(maxpos,dp);maxspeed=max(maxspeed,ds)
 meta={r['vehicle_id']:r for r in D.read_csv(raw/'vehicle_metadata.csv')};last=rows[-1];inter=json.loads(last['post_green_interlock_json']);guard=json.loads(last['guard_decision_json']);pre=json.loads(last['guard_vehicle_states_json']);stop=card['meter_controlled_link']['storage_length_m'];res={}
 for fid in inter['unsafe_ids']:
  v=next(v for v in pre if v['vehicle_id']==fid);post=inter['input_evidence']['remaining_storage'][fid];b=v['decel_m_s2'];maximum=v['speed_m_s']+v['accel_m_s2'];beforegap=stop-v['position_m'];beforeneed=1.1+maximum+maximum**2/(2*b);aftergap=stop-post['position_m'];afterneed=1.1+post['speed_m_s']+post['speed_m_s']**2/(2*b)
  beforefcd=bytime[652][fid];afterfcd=bytime[653][fid]
  assert abs(float(beforefcd['pos'])-v['position_m'])<=.005001 and abs(float(afterfcd['pos'])-post['position_m'])<=.005001
  assert abs(float(beforefcd['speed'])-v['speed_m_s'])<=.005001 and abs(float(afterfcd['speed'])-post['speed_m_s'])<=.005001
  assert beforegap>=beforeneed and aftergap<afterneed
  res[fid]={'present_in_pre_guard':True,'pre_state':v,'post_state':post,'pre_FCD':beforefcd,'post_FCD':afterfcd,'pre_gap_m':beforegap,'pre_required_m':beforeneed,'pre_margin_m':beforegap-beforeneed,'post_gap_m':aftergap,'post_required_m':afterneed,'post_margin_m':aftergap-afterneed,'actual_green_step_advance_m':post['position_m']-v['position_m'],'interpretation':'Logged pre-step inequality passes but logged post-step invariant fails for an already-observed follower. This is not an unseen new storage entrant. Engineering must assess the envelope guarantee; no threshold changed.'}
 cross=json.loads(last['crossing_bracket_ids_json']);beforeinternal={i for i,v in bytime[652].items() if v['lane']==card['meter_controlled_link']['via']};afterinternal={i for i,v in bytime[653].items() if v['lane']==card['meter_controlled_link']['via']};assert set(cross)==afterinternal-beforeinternal=={last['front_queued_vehicle_id']}
 trips=[dict(v.attrib) for v in D.A.records(raw/'tripinfo.xml','tripinfo')];endpoints=bytime[653];sums=[dict(v.attrib) for v in D.A.records(raw/'sumo_summary.xml','step')];lastsum=sums[-1];unfinished=[v for v in trips if float(v['arrival'])<0 and float(v['depart'])>=0];never_departed=[v for v in trips if float(v['depart'])<0];inserted_trips=[v for v in trips if float(v['depart'])>=0];assert len(unfinished)==len(endpoints)==int(lastsum['running'])==96;assert {v['id'] for v in unfinished}==set(endpoints);assert len(inserted_trips)==int(lastsum['inserted'])==765
 base=json.loads(Path(card['legacy_card']).read_text());pre600=D.A.pre600(Path(base['output'])/'fcd.xml.gz',raw/'fcd.xml.gz');assert pre600['equal']
 endpointclasses=Counter('R' if i.startswith('R_') else 'M' if i.startswith('M_') else 'U' if i.startswith('U_') else 'X' if i.startswith('X_') else 'UNKNOWN' for i in endpoints)
 report={'run_id':card['run_id'],'classification':'FAILED_TECHNICAL_ATTEMPT_NOT_EFFECT_EVIDENCE','receipt_status':receipt['status'],'manifest_card_input_validation':'PASS','source_validation':source,'FCD_records':654,'controller_rows':654,'queue_rows':654,'pre600':pre600,'highprecision_mapped_phase':{'snapshots_checked':54,'position_max_residual_m':maxpos,'speed_max_residual_m_s':maxspeed,'status':'PASS_PARTIAL_DOMAIN_ONLY'},'failure_interval_s':[653,654],'qualified_front_crossing':cross,'unsafe_follower_evidence':res,'terminal_summary':lastsum,'tripinfo_count':len(trips),'tripinfo_unfinished_departed':len(unfinished),'tripinfo_not_departed_termination_records':never_departed,'final_FCD_count':len(endpoints),'unfinished_groups':dict(endpointclasses),'unverified':['No trajectory beyond654; no evaluation interval1200-3000; no full4200 endpoint or costs.','No completed controller/queue treatment effect, capability, throughput or sweet-spot qualification.','SUMO closed normally after deliberate interlock failure; worker failed, not a successful run.'],'cost_imputation':False,'sources':{str(raw/n):v['sha256'] for n,v in receipt['output_manifest'].items()},'analysis_sha256':sha(__file__)}
 D.write(out/'FAILED_ATTEMPT_AUDIT.json',report)
 with (out/'endpoint_vehicles.csv').open('x') as f:
  w=csv.DictWriter(f,fieldnames=['id','lane','pos','speed','x','y','angle','type']);w.writeheader();w.writerows(dict(id=i,**{k:v.get(k) for k in ['lane','pos','speed','x','y','angle','type']}) for i,v in endpoints.items())
 with (out/'analysis_source_snapshot.py').open('x') as f:f.write(Path(__file__).read_text())
 print(json.dumps({k:report[k] for k in ['classification','failure_interval_s','qualified_front_crossing','unsafe_follower_evidence','tripinfo_count','tripinfo_unfinished_departed','tripinfo_not_departed_termination_records','unfinished_groups']}))
if __name__=='__main__':main()
