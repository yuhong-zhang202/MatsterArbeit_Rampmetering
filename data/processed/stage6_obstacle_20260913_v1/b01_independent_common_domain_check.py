"""Independent direct XML boundary checks for B seen-archive proposal evidence."""
from pathlib import Path
import csv,hashlib,json,xml.etree.ElementTree as ET,math
B=Path(__file__).resolve().parent;R=B.parents[2];T=R/'results/tables'/B.name
with (T/'b01_seen_common_domain_vehicles.csv').open() as f:data=list(csv.DictReader(f))
with (T/'b01_seen_common_domain_summary.csv').open() as f:sums=list(csv.DictReader(f))
with (B/'source_file_inventory.csv').open() as f:inventory=list(csv.DictReader(f))
count=0
for source in inventory:
 if source['source_suffix']!='outputs/fcd.xml':continue
 p=Path(source['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'];rid=source['run_id']
 expected={r['id']:r for r in data if r['run_id']==rid};track={};samples={w:[0,0,0] for w in ['A','B','Post','Full']};win={'A':(0,1500),'B':(300,1500),'Post':(1500,2700),'Full':(0,2700)}
 for _,node in ET.iterparse(p,events=('end',)):
  if node.tag!='timestep':continue
  now=float(node.attrib['time'])
  for car in node:
   i=car.attrib['id']
   if i not in expected:continue
   if car.attrib['lane'] not in {'main_down_0','main_down_1'}:continue
   position=float(car.attrib['pos']);v=float(car.attrib['speed'])
   x=track.setdefault(i,{'below100':None,'above100':None,'below700':None,'above700':None})
   for point in [100,700]:
    if position<point:x['below'+str(point)]=now
    elif x['above'+str(point)] is None:x['above'+str(point)]=now
   if 100<=position<700:
    for w,(lo,hi) in win.items():
     if lo<=now<hi:samples[w][0]+=1;samples[w][1]+=v;samples[w][2]+=int(v<=.1)
  node.clear()
 assert set(track)==set(expected)
 for i,e in expected.items():
  x=track[i]
  for c,k in [('start_lower_s','below100'),('start_upper_s','above100'),('end_lower_s','below700'),('end_upper_s','above700')]:assert float(e[c])==x[k],(rid,i,c)
  assert float(e['travel_lower_s'])==x['below700']-x['above100'];assert float(e['travel_upper_s'])==x['above700']-x['below100'];count+=1
 for s in [s for s in sums if s['run_id']==rid]:
  w=s['window'];lo,hi=win[w];eligible=[x for x in track.values() if lo<=x['below100'] and x['above100']<hi];n=len(eligible);assert int(s['eligible_completed_M'])==n
  if n:
   assert math.isclose(float(s['mean_travel_lower_s']),sum(x['below700']-x['above100'] for x in eligible)/n,abs_tol=1e-10)
   assert math.isclose(float(s['mean_travel_upper_s']),sum(x['above700']-x['below100'] for x in eligible)/n,abs_tol=1e-10)
  a,b,c=samples[w];assert a==int(s['domain_vehicle_samples']) and c==int(s['stopped_vehicle_seconds'])
  if a:assert math.isclose(b/a,float(s['mean_speed_mps']),abs_tol=1e-9)
assert count==16622 and len(sums)==48
with (B/'b01_independent_verification.json').open('x') as f:json.dump({'status':'passed','source_runs':12,'vehicle_boundary_records':count,'window_summary_records':len(sums),'method':'separate XML scan; last-below/first-above boundaries; no production module import','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0,'limit':'descriptive seen-archive evidence; no rule validation or scientific approval'},f,indent=2)
print('verified',count,len(sums))
