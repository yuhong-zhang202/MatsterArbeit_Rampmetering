#!/usr/bin/env python3
"""One-time non-simulation package builder. Refuses overwriting existing products."""
import json,hashlib,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering');BASE=Path(__file__).absolute().parent
OLD=ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering';SRC=OLD/'inputs/TV_C_S17_attempt1'
RUN=ROOT/'data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt1';OUT=RUN/'outputs'
HOME='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
def write(p,s):
 with p.open('x') as f:f.write(s)
def dump(p,v):write(p,json.dumps(v,indent=2,sort_keys=True)+'\n')
def binding(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
write(BASE/'inputs/demand.rou.xml',(SRC/'demand.rou.xml').read_text())
add=ET.parse(SRC/'scenario.add.xml')
for e in add.iter():
 for k in ('file','dest'):
  if k in e.attrib:e.set(k,str(OUT/Path(e.get(k)).name))
ET.indent(add,space='  ');write(BASE/'inputs/scenario.add.xml',ET.tostring(add.getroot(),encoding='unicode',xml_declaration=True)+'\n')
cfg=ET.parse(SRC/'scenario.sumocfg')
cfg.find('input/route-files').set('value',str(BASE/'inputs/demand.rou.xml'));cfg.find('input/additional-files').set('value',str(BASE/'inputs/scenario.add.xml'))
cfg.find('time/end').set('value','450')
for sec in ('output','report'):
 for e in cfg.find(sec):
  if '/data/raw/' in e.get('value',''):e.set('value',str(OUT/Path(e.get('value')).name))
ET.SubElement(cfg.find('output'),'fcd-output.max-leader-distance',{'value':'600'})
ET.indent(cfg,space='  ');write(BASE/'inputs/scenario.sumocfg',ET.tostring(cfg.getroot(),encoding='unicode',xml_declaration=True)+'\n')
roles=json.loads((SRC/'output_roles.json').read_text());roles['status']='PROPOSED_DIAGNOSTIC_STATIC_ONLY';roles['full_time_contract']='FCD/summary/queue labels0..449; TLS two IDs each0..449; detectors15 continuous30s bins; 18 XML roles plus observer JSONL. Full original planned demand is preserved through1500 but cutoff450 censors future demand.'
for r in roles['required_xml_roles']:r['path']=str(OUT/r['role'])
dump(BASE/'inputs/output_roles.json',roles)
write(BASE/'inputs/original_expected_identity_manifest.json',(SRC/'expected_identity_manifest.json').read_text())
# Preserve prior audited low-level watchdog code, adapting only this isolated wrapper's scope.
old=(OLD/'runtime_executor.py').read_text()
prefix=old[old.index('def require'):old.index('def validate_gate')]
run=old[old.index('def _run'):old.index('\ndef main():')]
run=run.replace("'executor_pid':os.getpid(),",'')
run=run.replace("'attempt_id':attempt['attempt_id'],'consumed_SUMO_starts'","'executor_pid':os.getpid(),'attempt_id':attempt['attempt_id'],'consumed_SUMO_starts'")
run=run.replace("physical.get('observer')=='primary'","physical.get('observer') in ['primary','readonly_traci']")
header='''#!/usr/bin/env python3
"""One isolated O2 C/seed17 technical diagnostic. Defaults to zero-process dry-run."""
import argparse,fcntl,hashlib,json,os,signal,socket,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
BASE=Path(__file__).absolute().parent
SUMO_HOME='/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'
LIMITS={'SUMO_starts':1,'TraCI_connections':1,'netconvert':0,'GUI':0,'retry':0,'per_attempt_monitored_s':180,'total_monitored_s':180,'per_attempt_observed_bytes':200000000,'total_observed_bytes':200000000}
'''
write(BASE/'runtime_executor.py',header+prefix+run+'\n'+(BASE/'executor_tail.txt').read_text())
refs=[SRC/'scenario.sumocfg',SRC/'scenario.add.xml',SRC/'demand.rou.xml',SRC/'expected_identity_manifest.json',OLD/'RUNTIME_CARD.json',OLD/'runtime_executor.py',OLD/'RUNTIME_CONTRACT.md',ROOT/'data/raw/stage6_targeted_validation_20260920_v1/TV_C_S17_attempt1/execution_receipt.json',ROOT/'data/raw/stage6_targeted_validation_20260920_v1/TV_C_S17_attempt1/output_manifest.json']
refs += [ROOT/'data/raw/stage6_targeted_validation_20260920_v1/TV_C_S17_attempt1/outputs'/name for name in ['fcd.xml','tls_states.xml','queues.xml','sumo_summary.xml','lanechanges.xml']]
refs += [Path(HOME)/'tools/traci'/s for s in ['__init__.py','main.py','connection.py','domain.py','constants.py','_vehicle.py','_vehicletype.py','_simulation.py','_trafficlight.py','_lane.py']]
dump(BASE/'references/source_bindings.json',{'context':'O2 unresolved; original 5 starts exhausted; D001-D004 provisional; protocol empty. Parent authorized package only, run conditional on exact final review. No formal claims.','sources':[binding(p) for p in refs],'default_length_not_assumed':'Observer reads actual vehicle length and minGap.','source_scope':'Installed Python API and installed local XSD; official version-tag C++ source is documentation, not proof of binary reproducible build.'})
print('inputs and isolated executor prepared; zero simulation processes')
