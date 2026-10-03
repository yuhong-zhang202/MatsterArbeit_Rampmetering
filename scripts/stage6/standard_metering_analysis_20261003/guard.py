"""Independent V9 four-layer actuator account; no simulation imports."""
import json,math
from collections import Counter

def truth(v):
 if v in (True,'True','true','1',1):return True
 if v in (False,'False','false','0',0):return False
 raise ValueError('invalid boolean')
def audit(rows,stopline):
 credit=0.;dropped=0.;last_green=None;counts=Counter();reasons=Counter()
 rows=[r for r in rows if float(r['time_begin_s'])>=600]
 if len(rows)!=3600:raise ValueError('guard horizon')
 for t,r in enumerate(rows,600):
  if float(r['time_begin_s'])!=t:raise ValueError('guard label')
  rate=float(r['command_rate_veh_h']);before=credit;credit+=rate/3600
  nominal=credit>=1-1e-10 and (last_green is None or t-last_green>=3)
  states=json.loads(r['guard_vehicle_states_json']);front=r['front_queued_vehicle_id'];ids=[v['vehicle_id'] for v in states]
  if len(ids)!=len(set(ids)) or len(ids)!=int(r['queue_vehicle_count']):raise ValueError('guard population')
  unsafe=[]
  for v in states:
   speed=float(v['speed_m_s']);accel=float(v['accel_m_s2']);decel=float(v['decel_m_s2']);pos=float(v['position_m'])
   if not all(math.isfinite(x) for x in [speed,accel,decel,pos]) or speed<0 or min(accel,decel)<=0:raise ValueError('guard dynamics')
   gap=stopline-pos;need=1.1+(speed+accel)+(speed+accel)**2/(2*decel);safe=v['vehicle_id']==front or gap+1e-9>=need
   if abs(gap-float(v['stopline_gap_m']))>1e-8 or abs(need-float(v['required_stop_gap_m']))>1e-8 or truth(v['follower_safe'])!=safe:raise ValueError('guard formula')
   if not safe:unsafe.append(v['vehicle_id'])
  if states:
   v=max(states,key=lambda x:x['position_m'])
   if v['vehicle_id']!=front:raise ValueError('guard front ordering')
   ready=0<=stopline-v['position_m']<=1.1 and 0<=v['speed_m_s']<.1 and float(r['downstream_rear_clearance_m'])>=float(r['required_clearance_m'])
   reason='FRONT_OR_RECEIVER_NOT_READY' if not ready else 'FOLLOWER_STOP_DISTANCE' if unsafe else 'ALLOW'
  else:
   if front:raise ValueError('guard phantom front')
   reason='NO_FRONT'
  allowed=reason=='ALLOW';actual=nominal and allowed
  if set(unsafe)!=set(json.loads(r['guard_failed_follower_ids_json'])):raise ValueError('guard unsafe list')
  expected_reason=reason if nominal else 'NOT_DUE_OR_MIN_RED'
  if r['guard_reason']!=expected_reason or truth(r['guard_allowed'])!=allowed:raise ValueError('guard reason')
  for k,v in [('nominal_slot_scheduled',nominal),('slot_scheduled',actual),('guard_rejected_slot',nominal and not allowed),('credit_deferred',nominal and not allowed)]:
   if truth(r[k])!=v:raise ValueError('guard slot bookkeeping '+k)
  if actual:credit-=1;last_green=t
  if credit>1:dropped+=credit-1;credit=1
  if abs(float(r['credit_before'])-before)>1e-8 or abs(float(r['credit_after'])-credit)>1e-8 or abs(float(r['dropped_credit_total'])-dropped)>1e-8:raise ValueError('guard credit accounting')
  if r['observed_state']!=('G' if actual else 'r'):raise ValueError('guard actuation')
  counts['due_attempts']+=nominal;counts['blocked_attempts']+=nominal and not allowed;counts['actual_slots']+=actual
  counts['actual_crossings']+=len(json.loads(r['crossing_bracket_ids_json']));reasons[expected_reason]+=1
 requested=sum(float(r['command_rate_veh_h'])/3600 for r in rows)
 if abs(requested-counts['actual_slots']-dropped-credit)>1e-7:raise ValueError('credit conservation')
 return dict(requested_credit=requested,final_credit=credit,credit_conservation_error=requested-counts['actual_slots']-dropped-credit,status='PASS_GUARD_LOG_IDENTITY',counts=dict(counts),reason_seconds=dict(reasons),dropped_credit=dropped,scope='Independent logged state/formula/credit identity; FCD input-state and warning checks remain separate.')
