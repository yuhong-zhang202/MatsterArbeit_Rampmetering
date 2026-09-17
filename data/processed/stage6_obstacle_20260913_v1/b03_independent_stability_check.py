import csv,json,hashlib,math,xml.etree.ElementTree as ET
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];T=R/'results/tables'/B.name
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
bins=read(T/'b03_seen_ML_C_60s_bins.csv');vs=read(T/'b01_seen_common_domain_vehicles.csv');iv=read(B/'source_file_inventory.csv');ep=read(T/'entry_vehicle_records.csv');rp=read(T/'R_passage_events.csv');sh=read(T/'shared_label_timeline.csv')
for run in ['ML17','ML23','C17','C23']:
 moments={a:[0,0,set()] for a in range(300,1500,60)}
 src=next(x for x in iv if x['run_id']==run and x['source_suffix']=='outputs/fcd.xml');assert hashlib.sha256(Path(src['path']).read_bytes()).hexdigest()==src['sha256']
 for _,node in ET.iterparse(src['path'],events=('end',)):
  if node.tag!='timestep':continue
  time=float(node.attrib['time'])
  if 300<=time<1500:
   a=int(time//60)*60
   for v in node:
    if v.get('id').startswith('M_flow.') and v.get('lane') in {'main_down_0','main_down_1'} and 100<=float(v.get('pos'))<700:
     moments[a][0]+=1;moments[a][1]+=float(v.get('speed'));moments[a][2].add(v.get('id'))
  node.clear()
 for row in [r for r in bins if r['run_id']==run]:
  a=int(row['begin_s']);b=a+60;n,s,ids=moments[a];assert n==int(row['M_samples']) and len(ids)==int(row['M_unique_ids']);assert math.isclose(s/n,float(row['speed_mean_mps']),abs_tol=1e-10)
  cohort=[v for v in vs if v['run_id']==run and float(v['start_lower_s'])>=a and float(v['start_upper_s'])<b];assert len(cohort)==int(row['M_certain_entry_cohort'])
  for side in ['lower','upper']:assert math.isclose(sum(float(v['travel_'+side+'_s']) for v in cohort)/len(cohort),float(row['TT_mean_'+side+'_s']),abs_tol=1e-10)
  assert sum(e['run_id']==run and e['class']=='M' and a<=float(e['depart_time'])<b for e in ep)==int(row['M_actual_departures'])
  assert sum(r['run_id']==run and a<=float(r['previous_time_s']) and float(r['first_downstream_time_s'])<b for r in rp)==int(row['R_passage_lower'])
  assert sum(r['run_id']==run and a<=float(r['time_s'])<b and int(r['RU_shared']) for r in sh)==int(row['RU_shared_labels'])
with (B/'b03_independent_stability_verification.json').open('x') as f:json.dump({'status':'passed','bins_checked':80,'raw_FCD_runs':4,'M_common_TT_record_source':'b01 independently verified16,622 records','RU_R_entry_source':'A independently verified full sources','scope':'raw speed/sample/unique ID independently reconstructed; TT,entry,R,shared bins independently regrouped; no scientific threshold qualification implied','SUMO':0,'netconvert':0,'TraCI':0,'GUI':0,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},f,indent=2)
print('80 bins independently checked')
