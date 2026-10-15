"""Independent bounded E1 union for the only complete600..630 window."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
p=Path('data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_01/outputs');out=Path(__file__).parent
events=[json.loads(l) for l in (p/'feedback_events.jsonl').read_text().splitlines()];decision=next(e for e in events if e['event']=='PROJECT_FEEDBACK_DECISION');windows={}
for d in decision['detector_ids']:
 known={}
 for e in events:
  if e['event']=='E1_POST_ACK_EVENTS' and e['global_s']<=630:
   for a in e['raw_events'][d]:
    key=(a[0],a[2]);old=known.get(key)
    if old is None or a[3]>=0:known[key]=a
 active=[a for a in known.values() if a[2]<630 and (a[3]<0 or a[3]>600)]
 occupied=sum(max(0,min(630,a[3] if a[3]>=0 else 630)-max(600,a[2])) for a in active)
 occ=100*occupied/30
 xml=next(x for x in ET.parse(p/(d+'.xml')).getroot().findall('interval') if float(x.get('begin'))==600 and float(x.get('end'))==630)
 reported=decision['occ_l0_pct' if d.endswith('l0') else 'occ_l1_pct'];assert abs(occ-reported)<1e-9 and abs(occ-float(xml.get('occupancy')))<=.51e-8
 windows[d]=dict(contributors=len(active),occupied_s=occupied,occupancy_pct=occ,XML_occupancy_pct=float(xml.get('occupancy')))
mean=sum(x['occupancy_pct'] for x in windows.values())/2;rate=900+70*(11-mean);assert abs(rate-decision['rate_clipped_veh_h'])<1e-9
r=dict(classification='INDEPENDENT_NATIVE_E1_COMPLETE_WINDOW_ONLY',window=[600,630],lane_measurements=windows,mean_occupancy_pct=mean,previous_rate_veh_h=900,computed_rate_veh_h=rate,reported_rate_veh_h=decision['rate_clipped_veh_h'],applied_s=632,delay_s=2,terminal_650_event_not_emitted_due_STOP=True,note='Frozen synthetic feedback_check expects global601..650; native journal has postACK events601..649; terminal650 feedback processing stopped after safety denial. Its UNKNOWN is retained, not repaired.')
(out/'FEEDBACK_WINDOW_V1.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
