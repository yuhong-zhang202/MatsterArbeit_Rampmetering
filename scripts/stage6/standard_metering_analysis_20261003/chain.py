"""Prospective operational queue chain; no validated physical spillback claim."""
from collections import Counter

def snapshot(vehicles,lane_lengths,stopline,vehicle_lengths):
 lanes=['shared_approach_0',':urban_diverge_1_0','ramp_storage_0'];offset={};x=0
 for lane in lanes:offset[lane]=x;x+=lane_lengths[lane]
 if abs(x-stopline)>1e-6:raise ValueError('route distance/stopline mismatch')
 ordered=[];unknown=[]
 for v in vehicles:
  if v['lane'] not in offset:
   if v['lane'].startswith(':urban_diverge_'):unknown.append(v['id'])
   continue
  if v['id'] not in vehicle_lengths:raise ValueError('missing actual body length')
  front=offset[v['lane']]+v['pos'];rear=front-vehicle_lengths[v['id']]
  ordered.append(dict(v,front=front,rear=rear))
 ordered.sort(key=lambda v:(v['front'],v['id']),reverse=True)
 head=ordered[0] if ordered else None;chain=[];gaps=[];anomalies=[]
 if head and 0<=stopline-head['front']<=10 and head['speed']<1.389:
  chain=[head]
  for v in ordered[1:]:
   gap=chain[-1]['rear']-v['front']
   if gap<-.05:anomalies.append(dict(ahead=chain[-1]['id'],behind=v['id'],gap=gap));break
   if gap>10 or v['speed']>=1.389:break
   if v['id'][0]!='R' and not (v['id'][0]=='U' and v['lane']=='shared_approach_0'):
    unknown.append(v['id']);break
   chain.append(v);gaps.append(gap)
 if chain and chain[0]['id'][0]!='R':unknown.append(chain[0]['id']);chain=[]
 return dict(chain_ids=[v['id'] for v in chain],head_distance_m=stopline-head['front'] if head else None,tail_rear_m=chain[-1]['rear'] if chain else None,max_gap_m=max(gaps,default=None),head_speed_mps=head['speed'] if head else None,shared_reached=bool(chain and chain[-1]['rear']<lane_lengths[lanes[0]]),storage_present=bool(chain),unknown_ids=unknown,geometry_anomalies=anomalies)

def episodes(rows,flag='shared_reached',minimum_seconds=30):
 """Global episodes first. Member identity may change. All labels required."""
 result=[];start=None
 for t,r in enumerate(rows):
  if r['time']!=t:raise ValueError('chain label gap')
  valid=r[flag] and not r['geometry_anomalies']
  if valid and start is None:start=t
  if not valid and start is not None:
   if t-start>=minimum_seconds:result.append(dict(begin=start,end=t,duration_s=t-start))
   start=None
 if start is not None and len(rows)-start>=minimum_seconds:result.append(dict(begin=start,end=len(rows),duration_s=len(rows)-start))
 return result
