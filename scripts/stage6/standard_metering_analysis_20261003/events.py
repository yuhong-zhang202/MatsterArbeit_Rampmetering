"""Independent detector vehicle-event reconstruction. Sum clipped durations, not union."""
import math

def reconstruct(observations,detectors,start=600,end=4170,width=30):
 """observations: one row per post-step/detector, including empty events lists."""
 expected={(t,d) for t in range(start+1,end+1) for d in detectors};indexed={}
 for row in observations:
  key=(row['step_end_s'],row['detector_id'])
  if key not in expected or key in indexed:raise ValueError('event step coverage/duplicate/detector')
  indexed[key]=row['events']
 if set(indexed)!=expected:raise ValueError('missing event step; empty observation must be explicit')
 known={d:{} for d in detectors};result=[];last_close=start
 for t in range(start+1,end+1):
  for d in detectors:
   seen=set();pending={k for k,v in known[d].items() if v[3]==-1}
   for event in indexed[t,d]:
    if len(event)!=5:raise ValueError('event schema')
    vid,length,entry,leave,type_id=event
    if not vid or not type_id or not all(math.isfinite(float(x)) for x in [length,entry,leave]) or length<=0 or entry<0 or entry>t or (leave!=-1 and not entry<=leave<=t):raise ValueError('invalid event time/length')
    key=(vid,entry)
    if key in seen:raise ValueError('duplicate event within detector step')
    seen.add(key);old=known[d].get(key)
    if old:
     if old[1]!=length or old[4]!=type_id:raise ValueError('event metadata conflict')
     if old[3]!=-1 and old[3]!=leave:raise ValueError('completed event changed or reopened')
    elif last_close>start and entry<last_close:raise ValueError('late unseen event could alter closed window')
    known[d][key]=(vid,length,entry,leave,type_id)
   if pending-seen:raise ValueError('ongoing event disappeared without observed leave')
  if (t-start)%width==0:
   for d in detectors:
    pieces=[]
    for key,v in known[d].items():
     entry,leave=v[2],v[3];stop=t if leave==-1 else min(t,leave);duration=max(0,stop-max(t-width,entry))
     if duration:pieces.append(dict(vehicle_id=v[0],entry=entry,leave=leave,clipped_duration_s=duration))
    result.append(dict(detector_id=d,begin=t-width,end=t,occupancy_pct=sum(v['clipped_duration_s'] for v in pieces)/width*100,contributing_event_count=len(pieces),pieces=pieces))
   last_close=t
 return result
