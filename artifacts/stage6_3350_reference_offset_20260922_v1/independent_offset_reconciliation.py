#!/usr/bin/env python3
"""Independent raw XML check for one lane1, lane0-fallback and pooled-unknown event."""
import csv, hashlib, json, math, statistics
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/stage6_3350_reference_offset_20260922_v1'
NET=ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml'
FCD=ROOT/'data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/outputs/fcd.xml'
VEH=ROOT/'data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/outputs/vehroute.xml'
SUM=ROOT/'data/processed/stage6_mainline_reference_library_20260922_v2/reference_summary.csv'
WL={'main_up_0':0,'main_up_1':1,':freeway_merge_0_0':0,':freeway_merge_0_1':1,'merge_section_1':0,'merge_section_2':1,':merge_end_0_0':0,':merge_end_0_1':1,'main_down_0':0,'main_down_1':1}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def avg(v): return statistics.fmean(v) if v else None
net=ET.parse(NET).getroot(); limits={x.attrib['id']:float(x.attrib['speed']) for x in net.iter('lane') if x.attrib.get('id') in WL}; km={(c,l):0.0 for c in range(22) for l in (0,1)}
for x in net.iter('lane'):
 if x.attrib.get('id') not in WL: continue
 p=[]
 for q in x.attrib.get('shape','').split():
  try:p.append(float(q.split(',')[0]))
  except:pass
 if len(p)<2:continue
 lo,hi=min(p),max(p); l=WL[x.attrib['id']]
 for c in range(22):km[(c,l)]+=max(0,min(hi,(c+1)*100)-max(lo,c*100))/1000
route={}
for v in ET.parse(VEH).getroot().findall('vehicle'):
 vid=v.attrib['id']; e=v.find('route').attrib.get('edges','').split() if v.find('route') is not None else []
 cohort='M' if vid.startswith('M_flow.') and e==['main_up','merge_section','main_down'] else ('R' if vid.startswith('R_flow.') and 'merge_section' in e and 'main_down' in e else None)
 try:sf=float(v.attrib['speedFactor'])
 except:sf=math.nan
 route[vid]=(cohort,sf)
obs=[]
for ts in ET.parse(FCD).getroot().findall('timestep'):
 b=int(round(float(ts.attrib['time'])))//30
 for v in ts.findall('vehicle'):
  vid=v.attrib.get('id'); lane=v.attrib.get('lane')
  if vid not in route or route[vid][0] not in {'M','R'} or lane not in WL:continue
  try:x=float(v.attrib['x']);s=float(v.attrib['speed']);sf=route[vid][1]
  except:continue
  if not(0<=x<2200 and math.isfinite(sf) and sf>0):continue
  obs.append((b,int(x//100),WL[lane],vid,route[vid][0],s,s/(limits[lane]*sf)))
refs={}
for r in csv.DictReader(open(SUM)):
 if r['n_blocks']!='0' and r['status']=='LIMITED_REFERENCE_SUPPORT':refs[(r['run'],int(r['cell']),r['lane'],r['metric'])]=float(r['median'])
e=next(r for r in csv.DictReader(open(ROOT/'data/processed/stage6_mainline_reference_library_20260922_v2/disturbance_catalog.csv')) if r['run']=='M3350'); c=int(e['cell']); a=int(e['first_low_bin']); z=int(e['low_bin_end_exclusive']); eid=e['source_event_id']; results=[]
for scope in ('lane0','lane1','pooled'):
 vals=[]
 for b in range(a,z):
  l=None if scope=='pooled' else int(scope[-1]); m=[o for o in obs if o[0]==b and o[1]==c and o[4]=='M' and (l is None or o[2]==l)]; mr=[o for o in obs if o[0]==b and o[1]==c and o[4] in {'M','R'} and (l is None or o[2]==l)]
  vals.append({'speed':avg([o[5] for o in m]),'ratio':avg([o[6] for o in m]),'density':len(m)/(30*km[(c,l)]) if l is not None and m else None,'mr_density':len(mr)/(30*km[(c,l)]) if l is not None and mr else None})
 if scope=='pooled':results.append({'scope':scope,'unknown':True});continue
 l=int(scope[-1]); donor='M3350' if ('M3350',c,scope,'m_ratio') in refs else 'A0'; ref=[refs.get((donor,c,scope,x)) for x in ('m_speed_mps','m_ratio','m_density_veh_per_lane_km','mr_density_veh_per_lane_km')]; means=[avg([v[x] for v in vals]) for x in ('speed','ratio','density','mr_density')]; off=[means[i]-ref[i] for i in range(4)]
 results.append({'scope':scope,'unknown':False,'support':donor,'offsets':off})
reported=[r for r in csv.DictReader(open(OUT/'candidate_c_offset_summary.csv')) if r['source_event_id']==eid]; checks=[]
for x in results:
 r=next(q for q in reported if q['scope']==x['scope'])
 if x['unknown']:checks.append(r['reference_support']=='NO_CELL_LANE_REFERENCE' and r['mean_speed_offset_mps']=='')
 else:checks += [abs(float(r[k])-v)<1e-8 for k,v in zip(('mean_speed_offset_mps','mean_ratio_offset','mean_m_density_offset','mean_mr_density_offset'),x['offsets'])]
out={'status':'PASS' if all(checks) else 'FAIL','source_event_id':eid,'cell':c,'start_s':a*30,'end_s':z*30,'results':results,'checks_pass':sum(checks),'checks_total':len(checks),'source_hashes':{'fcd':sha(FCD),'vehroute':sha(VEH),'network':sha(NET),'reference_summary':sha(SUM),'reported_summary':sha(OUT/'candidate_c_offset_summary.csv')}}
(OUT/'offset_independent_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
