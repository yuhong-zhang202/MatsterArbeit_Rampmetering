import csv,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
b=Path('data/processed/stage6_obstacle_20260913_v1')
rows=[]
for s in csv.DictReader((b/'source_file_inventory.csv').open()):
 if s['source_suffix']!='network.net.xml':continue
 p=Path(s['path']); assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
 root=ET.parse(p).getroot()
 for tag,selector in [('edge',lambda e:e.get('id') in ['main_up','ramp_accel','main_down']),('connection',lambda e:e.get('from') in ['main_up','ramp_accel'] and e.get('to')=='main_down')]:
  for e in root.findall(tag):
   if selector(e):
    rows.append({'run_id':s['run_id'],'path':s['path'],'sha256':s['sha256'],'element':tag,'attributes':str(dict(e.attrib)),'lanes':str([dict(x.attrib) for x in e.findall('lane')]),'scope':'static compiled configuration; no observed causal attribution'})
with (b/'static_context_links.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
idx=list(csv.DictReader((b/'diagnostic_evidence_index.csv').open()))
p=b/'static_context_links.csv';idx.append(dict(evidence_id='A-STATIC',path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),locator='run_id,element,attributes,lanes; original XML paths and hashes in each row',scope='static compiled configuration only; no lane-change/gap-acceptance event logs'))
with (b/'diagnostic_evidence_index_revision_02.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=idx[0]);w.writeheader();w.writerows(idx)
d=list(csv.DictReader((b/'obstacle_diagnosis.csv').open()))
for x in d:
 if x['hypothesis_id']=='H3':
  x['evidence_ids']+='|A-STATIC'
  x['observed_result']='R first-downstream counts and upstream expansion are observed; original compiled network has main_up priority3, ramp_accel priority2, mainline connection state M and ramp connection state m.'
with (b/'obstacle_diagnosis_revision_02.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=d[0]);w.writeheader();w.writerows(d)
print({'static_rows':len(rows),'evidence_ids':len(idx),'hypotheses':len(d)})
