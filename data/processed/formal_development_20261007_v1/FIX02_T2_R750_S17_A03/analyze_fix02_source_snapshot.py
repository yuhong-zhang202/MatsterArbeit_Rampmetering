"""Version-specific independent FIX02 guard adapter; preserves previous audit code."""
import json,math,sys
from pathlib import Path
import analyze_run as D
import audit_v15_service as V
LEGACY=D.independent_guard
REVISION='FIX02_GREEN_ADVANCE_PLUS_POST_RED'

def independent_guard(row,metadata,stopline):
 states=json.loads(row['guard_vehicle_states_json']);decision=json.loads(row['guard_decision_json'])
 assert decision['guard_revision']==REVISION
 oldbad=[]
 front=max(states,key=lambda v:v['position_m'])['vehicle_id'] if states else ''
 for s in states:
  v=s['speed_m_s'];u=v+s['accel_m_s2'];need=0 if v<.1 else 1.1+u+u*u/(2*s['decel_m_s2'])
  if s['vehicle_id']!=front and stopline-s['position_m']+1e-9<need:oldbad.append(s['vehicle_id'])
 legacyrow=dict(row,guard_failed_follower_ids_json=json.dumps(oldbad))
 allowed,reason=LEGACY(legacyrow,metadata,stopline)
 predictions=decision['pre_green_post_red_prediction']; byid={s['vehicle_id']:s for s in states if s['vehicle_id']!=front}
 assert len({p['vehicle_id'] for p in predictions})==len(predictions)
 assert {p['vehicle_id'] for p in predictions if p['population']=='storage'}==set(byid)
 bad=[]
 for p in predictions:
  vid=p['vehicle_id'];assert p['population'] in {'storage','approaching'}
  if p['population']=='storage':
   s=byid[vid]
   for x,y in [('projected_position_m','position_m'),('speed_m_s','speed_m_s'),('accel_m_s2','accel_m_s2'),('normal_decel_m_s2','decel_m_s2')]:assert abs(p[x]-s[y])<1e-10
  else:assert p['projected_position_m']<=0 and vid.startswith('R_') and vid not in {s['vehicle_id'] for s in states}
  m=metadata[vid]
  assert m['type_id']=='technical_passenger' and p['speed_m_s']>=0 and p['accel_m_s2']>0 and p['normal_decel_m_s2']>0
  u=p['speed_m_s']+p['accel_m_s2'];need=1.1+2*u+u*u/(2*p['normal_decel_m_s2']);gap=stopline-p['projected_position_m'];safe=gap+1e-9>=need
  assert math.isfinite(need) and abs(p['required_m']-need)<1e-9 and abs(p['gap_m']-gap)<1e-9 and p['safe']==safe
  if not safe:bad.append(vid)
 if allowed and bad:allowed=False;reason='FOLLOWER_POST_RED_PREDICTION';expectedbad=bad
 else:expectedbad=oldbad
 assert set(json.loads(row['guard_failed_follower_ids_json']))==set(expectedbad)
 return allowed,reason

def entrant_fcd_audit(raw,card):
 rows=D.read_csv(raw/'controller_steps.csv');checked=observations=post_checked=0
 coverage=json.load((raw/'fix02_entrant_coverage.json').open());assert coverage['revision']==REVISION
 length=coverage['upstream_length_m'];assert length==113.08 and coverage['maximum_one_step_advance_m']<length
 assert coverage['tau_s']==coverage['action_step_s']==1.0
 assert abs(coverage['maximum_one_step_advance_m']-coverage['maximum_type_speed_m_s']-coverage['type_accel_m_s2'])<1e-9
 for e in D.A.records(raw/'fcd.xml.gz','timestep'):
  label=int(float(e.get('time')));postrow=rows[label]
  if label>=600 and D.truth(postrow['slot_scheduled']):
   inter=json.loads(postrow['post_green_interlock_json']);poststates=inter['input_evidence']['remaining_storage']
   actualpost={v.get('id'):dict(v.attrib) for v in e if v.get('lane')=='ramp_storage_0'}
   assert set(poststates)==set(actualpost)
   for vid,state in poststates.items():
    f=actualpost[vid];assert abs(float(f['pos'])-state['position_m'])<=.005001 and abs(float(f['speed'])-state['speed_m_s'])<=.005001
   assert inter['input_evidence']['expected_front_id']==postrow['front_queued_vehicle_id'] and inter['input_evidence']['crossing_ids']==json.loads(postrow['crossing_bracket_ids_json'])
   post_checked+=1
  t=label+1
  if t<600 or t>=4200:continue
  actual={v.get('id'):dict(v.attrib) for v in e if v.get('lane')==':urban_diverge_1_0'}
  decision=json.loads(rows[t]['guard_decision_json']);pred={p['vehicle_id']:p for p in decision['pre_green_post_red_prediction'] if p['population']=='approaching'}
  assert set(actual)==set(pred)
  for vid,p in pred.items():
   assert 0<=p['speed_m_s']<=coverage['maximum_type_speed_m_s']+1e-9 and abs(p['accel_m_s2']-coverage['type_accel_m_s2'])<1e-9
   f=actual[vid];assert abs(float(f['pos'])-length-p['projected_position_m'])<=.005001 and abs(float(f['speed'])-p['speed_m_s'])<=.005001
   observations+=1
  checked+=1
 assert checked==3600
 return dict(status='PASS',prestep_snapshots=checked,entrant_observations=observations,post_green_snapshots=post_checked,scope='Every connector entrant independently matched to FCD label t-1; rounded position/speed tolerance 0.005001. Native bounds independently recomputed. Runtime dynamic coverage remains conditional on version-bound worker and logged type contract.')

def main():
 # The original adapter resolves this global at call time, including its service audit.
 D.independent_guard=independent_guard;V.D.independent_guard=independent_guard
 cardpath=Path(sys.argv[sys.argv.index('--card')+1]);card=json.load(cardpath.open());assert card['guard_revision']==REVISION
 outname=sys.argv[sys.argv.index('--out-name')+1];raw=Path(card['output'])
 D.A.validate_current_receipt(raw,cardpath)
 entrant=entrant_fcd_audit(raw,card)
 D.main()
 out=D.HERE/outname;D.write(out/'fix02_entrant_fcd_audit.json',entrant)
 D.write(out/'fix02_adapter_provenance.json',dict(revision=REVISION,script_sha256=D.A.sha(__file__),legacy_adapter_sha256=D.A.sha(D.__file__),card_sha256=D.A.sha(cardpath),classification='DEVELOPMENT_ONLY'))
if __name__=='__main__':main()
