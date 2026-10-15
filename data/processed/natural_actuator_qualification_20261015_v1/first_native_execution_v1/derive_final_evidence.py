"""Minimal supplemental native measurements, retaining failed audit status."""
import sys,json,hashlib
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()))
from scripts.natural_service_audit_20261015_v1.actual import feedback_check
from scripts.natural_actuator_qualification_20261015_v1.streaming import posts,jsonl
p=Path('data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_01/outputs');out=Path(__file__).parent
r={'qualified':False,'scope':'Observed prefix only'}
try:r['independent_feedback']=feedback_check(list(jsonl(p/'feedback_events.jsonl')),650,[x for x in jsonl(p/'command_events.jsonl') if x['event']=='REQUESTED'])
except Exception as e:r['independent_feedback']={'status':'UNKNOWN','reason':str(e)}
mins={'actual_acceleration_m_s2':None,'speed_difference_m_s2':None};c=Counter();reason=[];ctrl=Counter();empty=[]
for row in posts(p/'post_steps.jsonl'):
 t=row['time_begin_s'];c.update(row['native_event_counters']);ctrl[row['motion']]+=t>=600
 for k in mins:
  for vid,v in row['braking_observation'][k].items():
   if mins[k] is None or v<mins[k]['value']:mins[k]={'value':v,'id':vid,'time_begin_s':t}
 if row.get('reasons'):reason.append({'time_s':t,'reasons':row['reasons'],'terminal_reason':row.get('terminal_reason')})
r.update(min_braking=mins,native_counter_totals=dict(c),controlled_phase_seconds=dict(ctrl),runtime_reasons=reason)
(out/'SUPPLEMENTAL_EVIDENCE_V1.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
