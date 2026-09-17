"""Seen ML/C stability facts; no thresholds selected, no simulator imports."""
import csv,json,math,statistics as st,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];T=ROOT/'results/tables'/B.name
RUNS=['ML17','ML23','C17','C23'];START=list(range(300,1500,60))
def rows(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rs):
 with p.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
def mean(xs):return sum(xs)/len(xs) if xs else None
def trend(xs):return sum((i-9.5)*(x-mean(xs)) for i,x in enumerate(xs))/sum((i-9.5)**2 for i in range(20))
inputs=[T/'b01_seen_common_domain_vehicles.csv',T/'entry_vehicle_records.csv',T/'R_passage_events.csv',T/'shared_label_timeline.csv',B/'source_file_inventory.csv']
vs,entries,rpasses,shared,inv=[rows(p) for p in inputs];bins=[];summary=[];joint=[];inflows=[];proof=[]
for run in RUNS:
 vv=[v for v in vs if v['run_id']==run];ee=[e for e in entries if e['run_id']==run and e['class']=='M'];rr=[r for r in rpasses if r['run_id']==run];ss=[r for r in shared if r['run_id']==run];samples={a:[] for a in START};ids={a:set() for a in START};first_merge={};prev={};f1200={}
 source=next(x for x in inv if x['run_id']==run and x['source_suffix']=='outputs/fcd.xml');p=Path(source['path']);assert sha(p)==source['sha256'];proof.append({'path':str(p),'sha256':sha(p)})
 for _,node in ET.iterparse(p,events=('end',)):
  if node.tag!='timestep':continue
  time=float(node.get('time'))
  for v in node:
   i=v.get('id')
   if not i.startswith('M_flow.'):continue
   lane=v.get('lane');pos=float(v.get('pos'));old=prev.get(i)
   if lane in ['main_up_0','main_up_1'] and pos>=1200 and old and old[1] in ['main_up_0','main_up_1'] and old[2]<1200:f1200.setdefault(i,(old[0],time))
   if lane in ['main_down_0','main_down_1']:
    first_merge.setdefault(i,time)
    if 300<=time<1500 and 100<=pos<700:
     a=300+int((time-300)//60)*60;samples[a].append(float(v.get('speed')));ids[a].add(i)
   prev[i]=(time,lane,pos)
  node.clear()
 for a in START:
  b=a+60;certain=[v for v in vv if a<=float(v['start_lower_s']) and float(v['start_upper_s'])<b];amb=[v for v in vv if float(v['start_upper_s'])>=a and float(v['start_lower_s'])<b and v not in certain];rlo=sum(a<=float(r['previous_time_s']) and float(r['first_downstream_time_s'])<b for r in rr);rhi=sum(float(r['first_downstream_time_s'])>=a and float(r['previous_time_s'])<b for r in rr);s=[r for r in ss if a<=float(r['time_s'])<b];qs=samples[a];tt=[(float(v['travel_lower_s'])+float(v['travel_upper_s']))/2 for v in certain]
  bins.append(dict(run_id=run,begin_s=a,end_s=b,M_samples=len(qs),M_unique_ids=len(ids[a]),M_certain_entry_cohort=len(certain),M_boundary_ambiguous=len(amb),TT_mean_lower_s=mean([float(v['travel_lower_s']) for v in certain]),TT_mean_upper_s=mean([float(v['travel_upper_s']) for v in certain]),TT_midpoint_descriptive_mean_s=mean(tt),TT_midpoint_descriptive_sd_s=st.stdev(tt) if len(tt)>1 else None,speed_mean_mps=mean(qs),speed_sample_sd_mps=st.stdev(qs) if len(qs)>1 else None,M_actual_departures=sum(a<=float(e['depart_time'])<b for e in ee),M_first_merge_labels=sum(a<=x<b for x in first_merge.values()),M_common_entry_lower=len(certain),M_common_entry_upper=len(certain)+len(amb),R_passage_lower=rlo,R_passage_upper=rhi,RU_shared_labels=sum(int(r['RU_shared']) for r in s),RU_shared_green_labels=sum(int(r['RU_shared']) for r in s if r['TLS_movement0'] in ['G','g']),value_state='observed',role='seen_exploratory_rule_formulation_only'))
 bb=[r for r in bins if r['run_id']==run];speeds=[r['speed_mean_mps'] for r in bb];tt=[r['TT_midpoint_descriptive_mean_s'] for r in bb];early=sum(sum(samples[a]) for a in START[:10])/sum(len(samples[a]) for a in START[:10]);late=sum(sum(samples[a]) for a in START[10:])/sum(len(samples[a]) for a in START[10:]);dd=[float(e['depart_delay_s']) for e in ee]
 summary.append(dict(run_id=run,bins=20,min_bin_certain_M=min(r['M_certain_entry_cohort'] for r in bb),speed_first_half_mps=early,speed_second_half_mps=late,speed_half_change_pct=100*(late/early-1),speed_bin_cv_pct=100*st.stdev(speeds)/mean(speeds),speed_max_adjacent_change_pct=max(100*abs(speeds[i]/speeds[i-1]-1) for i in range(1,20)),speed_max_deviation_from_binmean_pct=max(100*abs(x/mean(speeds)-1) for x in speeds),speed_linear_slope_mps_per_60s=trend(speeds),TT_binmean_cv_pct=100*st.stdev(tt)/mean(tt),TT_linear_slope_s_per_60s=trend(tt),M_planned=len(ee),M_entered_before1500=sum(float(e['depart_time'])<1500 for e in ee),M_depart_delay_mean_s=mean(dd),M_depart_delay_max_s=max(dd),M_common_first_bracket_lower=min(float(v['start_lower_s']) for v in vv),M_common_last_bracket_upper=max(float(v['start_upper_s']) for v in vv),M_main_up1200_bracketed=len(f1200),M_first_merge_total=len(first_merge),qualification='seen lower-load comparator not scientifically validated stable baseline'))
 for w,a,b in [('A',0,1500),('B',300,1500),('Full',0,2700)]:
  n=sum(a<=float(e['depart_time'])<b for e in ee);nm=sum(a<=x<b for x in first_merge.values());nc=sum(a<=float(v['start_lower_s']) and float(v['start_upper_s'])<b for v in vv)
  inflows.append(dict(run_id=run,window=w,planned_full_M=len(ee),nominal_requested_q_main=2600 if run.startswith('ML') else 3200,effective_scheduled_q_main=len(ee)*3600/1500,M_entered=n,actual_entry_q_vehph=n*3600/(b-a),M_first_merge_labels=nm,M_merge_label_rate_vehph=nm*3600/(b-a),M_common_certain_crossings=nc,M_common_certain_rate_vehph=nc*3600/(b-a),M_feeder1200_crossings=sum(a<=x[0] and x[1]<b for x in f1200.values()),feeder_qualification='V0 missing long traversal is structural observation-domain absence, not missing XML',role='distinct counts and windows; no enforced equality of counters'))
 for i in range(18):
  bs=bb[i:i+3];joint.append(dict(run_id=run,begin_s=bs[0]['begin_s'],end_s=bs[-1]['end_s'],R_lower_total=sum(x['R_passage_lower'] for x in bs),R_upper_total=sum(x['R_passage_upper'] for x in bs),bins_R_lower_nonzero=sum(x['R_passage_lower']>0 for x in bs),bins_RU_shared_nonzero=sum(x['RU_shared_labels']>0 for x in bs),RU_shared_labels=sum(x['RU_shared_labels'] for x in bs),all3_R_and_shared=all(x['R_passage_lower']>0 and x['RU_shared_labels']>0 for x in bs),R10_and_all3_R_and_shared=sum(x['R_passage_lower'] for x in bs)>=10 and all(x['R_passage_lower']>0 and x['RU_shared_labels']>0 for x in bs),qualification='event-context opportunity only; no M impairment gate applied'))
write(T/'b03_seen_ML_C_60s_bins.csv',bins);write(T/'b03_seen_ML_C_stability_summary.csv',summary);write(T/'b03_seen_ML_C_inflow_scopes.csv',inflows);write(T/'b03_seen_ML_C_joint_triplets.csv',joint)
receipt={'status':'computed_and_identity_totals_checked','source_runs':4,'bins':80,'triplets':72,'inflow_rows':12,'sources':proof+[{'path':str(p),'sha256':sha(p)} for p in inputs],'script_sha256':sha(Path(__file__)),'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0}
assert len(bins)==80 and len(joint)==72
with (B/'b03_stability_receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(summary,indent=2));print('triplet_counts',[(r,sum(x['R10_and_all3_R_and_shared'] for x in joint if x['run_id']==r)) for r in RUNS])
