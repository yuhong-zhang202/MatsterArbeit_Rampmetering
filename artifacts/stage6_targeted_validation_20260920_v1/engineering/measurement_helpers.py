"""Deterministic measurement primitives. No SUMO/TraCI imports or behavior changes."""
import hashlib,json,xml.etree.ElementTree as ET
from decimal import Decimal
D=Decimal

def normalized_xml_digest(path):
 """Ignore comments/formatting and summary wallclock duration only; preserve traffic fields/order."""
 h=hashlib.sha256();root=None
 for event,el in ET.iterparse(path,events=('start','end')):
  if root is None:root=el.tag
  if event=='start':
   attrs=dict(el.attrib)
   if root=='summary' and el.tag=='step':attrs.pop('duration',None)
   h.update(json.dumps([event,el.tag,sorted(attrs.items())],separators=(',',':')).encode())
  else:
   if el.text and el.text.strip():h.update(el.text.strip().encode())
   h.update(json.dumps([event,el.tag],separators=(',',':')).encode());el.clear()
 return h.hexdigest()

def r_path_map(network):
 root=ET.parse(network).getroot();lanes={x.get('id'):D(x.get('length')) for x in root.iter('lane')}
 names=['shared_approach_0',':urban_diverge_1_0','ramp_storage_0',':ramp_mid_0_0','ramp_accel_0']
 start=-lanes[names[0]];out={}
 for name in names:out[name]={'start':start,'length':lanes[name]};start+=lanes[name]
 stop=out['ramp_storage_0']['start']+out['ramp_storage_0']['length']
 return out,stop

def locate(row,path):
 lane=row['lane'];pos=D(str(row['pos']))
 if lane not in path:return None
 domain=path[lane]
 if pos<0 or pos>domain['length']:raise ValueError('position outside compiled lane')
 return domain['start']+pos

def crossing_bracket(before,after,path,stop):
 """First directly bracketed front crossing; exact within-step time is unknown."""
 a,b=locate(before,path),locate(after,path)
 if a is None or b is None:return {'status':'position_unknown'}
 if D(str(after['time']))-D(str(before['time']))!=1:return {'status':'sampling_gap'}
 if a<=stop<b:return {'status':'crossing_bracket','lower':before['time'],'upper':after['time'],'interval':'(lower,upper]','position_at_lower':str(a),'position_at_upper':str(b),'boundary_equality_possible':a==stop}
 return {'status':'no_bracket'}

def frame_queue(rows,path,stop):
 """Includes actual intervening U. Input length is actual vehicle length; no inferred class default."""
 vehicles=[]
 for row in rows:
  p=locate(row,path)
  if p is not None and p<=stop:
   v=dict(row);v['front']=p;v['back']=p-D(str(v['length']));v['stopped']=D(str(v['speed']))<D('.1');vehicles.append(v)
 vehicles.sort(key=lambda v:(-v['front'],v['id']))
 anchor=next((v for v in vehicles if v['class']=='R' and v['stopped'] and 0<=stop-v['front']<=10),None)
 if anchor is None:return {'members':[],'storage_cross_observed':False,'shared_obstruction_potential':False,'unanchored_stopped_R':[v['id'] for v in vehicles if v['class']=='R' and v['stopped']],'junction_blocking_candidate':any(v['class']=='R' and v['stopped'] for v in vehicles)}
 members=[anchor];gaps=[]
 for v in vehicles[vehicles.index(anchor)+1:]:
  gap=members[-1]['back']-v['front']
  if gap<0:raise ValueError('overlapping bumper ordering must be investigated')
  if not v['stopped'] or gap>10:break
  gaps.append({'leader':members[-1]['id'],'follower':v['id'],'gap_m':str(gap)});members.append(v)
 crosses=any(v['class']=='R' and v['lane']=='shared_approach_0' for v in members)
 # U candidate requires an actual linked chain to an R ahead, never independent co-occurrence.
 linked=[];seen_r=False
 for v in members:
  if v['class']=='U' and v['lane']=='shared_approach_0' and seen_r:linked.append(v['id'])
  if v['class']=='R':seen_r=True
 return {'members':[v['id'] for v in members],'anchor_distance_m':str(stop-anchor['front']),'gaps':gaps,'front_m':str(anchor['front']),'tail_back_m':str(members[-1]['back']),'length_m':str(anchor['front']-members[-1]['back']),'R_count':sum(v['class']=='R' for v in members),'U_count':sum(v['class']=='U' for v in members),'storage_cross_observed':crosses,'shared_obstruction_potential':crosses,'U_blocking_candidate':linked,'junction_blocking_candidate':False}

def identity_account(planned,tripinfo):
 expected=set(planned);seen=set();counts={'undeparted':0,'arrived':0,'unfinished':0}
 for row in tripinfo:
  id=row['id']
  if id not in expected or id in seen:raise ValueError('unknown/duplicate identity')
  seen.add(id);depart=D(str(row['depart']));arrival=D(str(row['arrival']))
  if depart<0:counts['undeparted']+=1
  elif arrival<0:counts['unfinished']+=1
  elif arrival>=depart:counts['arrived']+=1
  else:raise ValueError('arrival before departure')
 if seen!=expected:raise ValueError('missing identities are evidence errors, not inferred undeparted')
 return counts

def interval_order(a,b):
 return 'before' if a[1]<b[0] else 'after' if b[1]<a[0] else 'temporal_order_unidentified'
