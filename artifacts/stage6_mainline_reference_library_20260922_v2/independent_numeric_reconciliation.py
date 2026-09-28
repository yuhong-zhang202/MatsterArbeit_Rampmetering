#!/usr/bin/env python3
"""Second implementation for a small accepted/rejected raw-FCD slice audit."""
from __future__ import annotations
import csv, json, math, statistics
import hashlib
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/stage6_mainline_reference_library_20260922_v2'
NET=ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml'
WL={'main_up_0':0,'main_up_1':1,':freeway_merge_0_0':0,':freeway_merge_0_1':1,'merge_section_1':0,'merge_section_2':1,':merge_end_0_0':0,':merge_end_0_1':1,'main_down_0':0,'main_down_1':1}
RUNS={
 'A0':('A','data/raw/stage6_targeted_validation_20260920_v1/TV_A_S17_attempt1','results/tables/stage6_protectable_state_application_20260921_v1/candidate_events.csv'),
 'M3350':('LOC','data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1','data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/classifier_output/tables/candidate_events.csv')}
def lane_km():
 out={(c,l):0.0 for c in range(22) for l in (0,1)}; root=ET.parse(NET).getroot()
 for lane in root.iter('lane'):
  if lane.attrib.get('id') not in WL: continue
  pts=[]
  for p in lane.attrib.get('shape','').split():
   try: pts.append(float(p.split(',')[0]))
   except Exception: pass
  if len(pts)<2: continue
  lo,hi=min(pts),max(pts); role=WL[lane.attrib['id']]
  for c in range(22): out[(c,role)]+=max(0,min(hi,(c+1)*100)-max(lo,c*100))/1000
 return out
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def routes(root):
 out={}
 for v in ET.parse(root/'outputs/vehroute.xml').getroot().findall('vehicle'):
  vid=v.attrib['id']; e=v.find('route').attrib.get('edges','').split() if v.find('route') is not None else []
  cohort='M' if vid.startswith('M_flow.') and e==['main_up','merge_section','main_down'] else ('R' if vid.startswith('R_flow.') and 'merge_section' in e and 'main_down' in e else None)
  try: sf=float(v.attrib['speedFactor'])
  except Exception: sf=math.nan
  out[vid]=(cohort,sf)
 return out
def raw_rows(root):
 rt=routes(root); out=[]; limits={z.attrib['id']:float(z.attrib['speed']) for z in ET.parse(NET).getroot().iter('lane') if z.attrib.get('id') in WL}
 for ts in ET.parse(root/'outputs/fcd.xml').getroot().findall('timestep'):
  t=int(round(float(ts.attrib['time']))); b=t//30
  for v in ts.findall('vehicle'):
   vid=v.attrib.get('id'); lane=v.attrib.get('lane')
   if vid not in rt or rt[vid][0] not in {'M','R'} or lane not in WL: continue
   try: x=float(v.attrib['x']); s=float(v.attrib['speed']); sf=rt[vid][1]
   except Exception: continue
   if not (0<=x<2200 and math.isfinite(sf) and sf>0): continue
   c=int(x//100); role=WL[lane]; limit=limits[lane]
   out.append((t,b,c,role,vid,rt[vid][0],s/(limit*sf),s))
 return out
def mask_intervals(evpath,runlab):
 out=[]
 for r in csv.DictReader(open(ROOT/evpath)):
  if r.get('run')!=runlab or r.get('profile') not in {'P','S','L'}: continue
  try: c=int(r['cell']); a=int(r['first_low_bin']); z=int(r['low_bin_end_exclusive'])
  except Exception: continue
  for cc in range(max(0,c-1),min(21,c+1)+1): out.append((cc,a,z))
 return out
def eval_block(rows,lk,c,a,z,intervals):
 vals=[]
 for b in range(a,z):
  lane=[]
  for l in (0,1):
   x=[r for r in rows if r[1]==b and r[2]==c and r[3]==l and r[5]=='M']; ids={r[4] for r in x}; ratio=statistics.fmean(r[6] for r in x) if x else None
   mr=[r for r in rows if r[1]==b and r[2]==c and r[3]==l and r[5] in {'M','R'}]
   lane.append({'n':len(x),'ids':len(ids),'ratio':ratio,'density':len(x)/(30*lk[(c,l)]) if x and lk[(c,l)] else 0.0,'mr_density':len(mr)/(30*lk[(c,l)]) if mr and lk[(c,l)] else 0.0})
  pooled=[r for r in rows if r[1]==b and r[2]==c and r[5]=='M']; all_pooled=[r for r in rows if r[1]==b and r[2]==c and r[5] in {'M','R'}]; ids={r[4] for r in pooled}; pr=statistics.fmean(r[6] for r in pooled) if pooled else None
  vals.append((lane,{'n':len(pooled),'ids':len(ids),'ratio':pr,'mr_density':sum(x['mr_density'] for x in lane)}))
 reasons=[]
 for lane,_ in [x for x in vals for x in [(x[0][0],None),(x[0][1],None)]]:
  if lane['n']==0: reasons.append('EMPTY_NO_EXPOSURE')
  elif lane['ids']<2: reasons.append('LOW_POPULATION')
  elif lane['ratio'] is None or lane['ratio']<.85: reasons.append('LOW_MOBILITY')
 for _,p in vals:
  if p['n']==0: reasons.append('EMPTY_NO_EXPOSURE')
  elif p['ids']<2: reasons.append('LOW_POPULATION')
  elif p['ratio'] is None or p['ratio']<.85: reasons.append('LOW_MOBILITY')
 hits=[(cc,aa,zz) for cc,aa,zz in intervals if cc==c and not (z*30<=aa*30 or a*30>=zz*30)]
 if hits: reasons.append('DISTURBANCE_OVERLAP')
 starts=[aa*30 for cc,aa,zz in intervals if cc==c]
 if starts and z*30>min(starts): reasons.append('POST_FIRST_DISTURBANCE_ONSET')
 return {'cell':c,'block_start_s':a*30,'block_end_s':z*30,'bins':vals,'independent_reasons':sorted(set(reasons)),'independent_status':'REFERENCE_ACCEPTED' if not reasons else 'REFERENCE_REJECTED'}
ledger=list(csv.DictReader(open(OUT/'reference_candidate_ledger.csv'))); lk=lane_km(); results=[]
for run,(runlab,rootrel,evrel) in RUNS.items():
 rr=[r for r in ledger if r['run']==run and r['lane']=='pooled']; acc=next(r for r in rr if r['accepted']=='REFERENCE_ACCEPTED'); rej=next(r for r in rr if r['accepted']=='REFERENCE_REJECTED' and 'LOW_MOBILITY' in r['rejection_reason'])
 rows=raw_rows(ROOT/rootrel); intervals=mask_intervals(evrel,runlab)
 for label,r in [('accepted',acc),('rejected_low_mobility',rej)]:
  z=eval_block(rows,lk,int(r['cell']),int(r['block_start_s'])//30,int(r['block_end_s'])//30,intervals)
  z.update({'run':run,'sample':label,'ledger_status':r['accepted'],'ledger_reason':r['rejection_reason'],'matches_status':z['independent_status']==r['accepted']})
  results.append(z)
bindings={}
for run,(_,rootrel,_) in RUNS.items():
 root=ROOT/rootrel
 bindings[run]={'fcd_path':str((root/'outputs/fcd.xml').relative_to(ROOT)),'fcd_sha256':sha(root/'outputs/fcd.xml'),'vehroute_path':str((root/'outputs/vehroute.xml').relative_to(ROOT)),'vehroute_sha256':sha(root/'outputs/vehroute.xml'),'network_path':str(NET.relative_to(ROOT)),'network_sha256':sha(NET)}
out={'status':'PASS' if all(r['matches_status'] for r in results) else 'FAIL','samples':results,'source_bindings':bindings,'note':'Independent raw-FCD/vehroute/network recomputation of one accepted and one LOW_MOBILITY-rejected pooled block per run; no selector functions imported.'}
(OUT/'independent_numeric_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
