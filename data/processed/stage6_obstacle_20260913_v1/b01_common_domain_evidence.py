"""Seen-archive descriptive evidence for proposed B common-domain choices. No simulator."""
from pathlib import Path
import csv,json,hashlib,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent;R=B.parents[2];T=R/'results/tables'/B.name
W={'A':(0,1500),'B':(300,1500),'Post':(1500,2700),'Full':(0,2700)}
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rs):
 with p.open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
files=read(B/'source_file_inventory.csv');registry=read(B/'source_registry.csv');allrows=[];summ=[];hashes={}
for run in registry:
 rid=run['run_id'];p=Path(next(x['path'] for x in files if x['run_id']==rid and x['source_suffix']=='outputs/fcd.xml'));hashes[str(p.relative_to(R))]=sha(p)
 previous={};events={};sample={w:[0,0,0] for w in W}
 for _,step in ET.iterparse(p,events=('end',)):
  if step.tag!='timestep':continue
  t=float(step.get('time'))
  for v in step:
   vid=v.get('id')
   if not vid.startswith('M_flow.'):continue
   lane=v.get('lane');pos=float(v.get('pos'));speed=float(v.get('speed'))
   if lane in ['main_down_0','main_down_1']:
    for w,(a,b) in W.items():
     if a<=t<b and 100<=pos<700:
      sample[w][0]+=1;sample[w][1]+=speed;sample[w][2]+=int(speed<=.1)
    prev=previous.get(vid)
    for x in [100,700]:
     if pos>=x and (vid,x) not in events:
      if prev is None or prev[1] not in ['main_down_0','main_down_1'] or prev[2]>=x:raise ValueError((rid,vid,x,'unbracketed'))
      events[vid,x]=(prev[0],t)
   previous[vid]=(t,lane,pos)
  step.clear()
 local=[]
 for vid in sorted(previous):
  a=events[vid,100];b=events[vid,700]
  local.append(dict(run_id=rid,id=vid,start_lower_s=a[0],start_upper_s=a[1],end_lower_s=b[0],end_upper_s=b[1],travel_lower_s=b[0]-a[1],travel_upper_s=b[1]-a[0],distance_m=600,value_state='observed',qualification='seen_archive_proposed_domain_not_confirmatory'))
 allrows+=local
 for w,(a,b) in W.items():
  eligible=[x for x in local if a<=x['start_lower_s'] and x['start_upper_s']<b]
  ambiguous=[x for x in local if not(a<=x['start_lower_s'] and x['start_upper_s']<b) and x['start_upper_s']>=a and x['start_lower_s']<b]
  n=len(eligible);count,ss,stop=sample[w]
  summ.append(dict(run_id=rid,seed=run['seed'],q_main=run['q_main_requested_vehph'],q_ramp=run['q_ramp_requested_vehph'],window=w,eligible_completed_M=n,boundary_ambiguous_M=len(ambiguous),mean_travel_lower_s=sum(x['travel_lower_s'] for x in eligible)/n if n else None,mean_travel_upper_s=sum(x['travel_upper_s'] for x in eligible)/n if n else None,domain_vehicle_samples=count,mean_speed_mps=ss/count if count else None,mean_accumulation_veh=count/(b-a),stopped_vehicle_seconds=stop,value_state='observed' if n else 'no_contributors',qualification='seen_archive_descriptive_not_qualified_freeflow_reference',reason='M-only main_down positions100..700; crossing-time bounds; bracket-boundary cases counted separately'))
write(T/'b01_seen_common_domain_vehicles.csv',allrows);write(T/'b01_seen_common_domain_summary.csv',summ)
with (B/'b01_seen_common_domain_receipt.json').open('x') as f:json.dump(dict(status='computed_pending_independent_check',runs=len(registry),vehicle_rows=len(allrows),summary_rows=len(summ),code_sha256=sha(Path(__file__)),source_hashes=hashes,SUMO=0,netconvert=0,TraCI=0,GUI=0),f,indent=2)
print({'runs':len(registry),'vehicles':len(allrows),'rows':len(summ)})
