from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,subprocess,copy
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering');B=ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering';OLD=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering';SOURCE=OLD/'runtime_validation_revision04/inputs/RV4_R720_S17_attempt1';NET=B/'build_attempts/TV_BUILD01/network.net.xml';HOME=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo')
def bind(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,obj):
 with p.open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
def xml(p,r):E.indent(r);p.write_bytes(E.tostring(r,encoding='utf-8',xml_declaration=True))
old=E.parse(OLD/'build_attempts/BUILD02/network.net.xml').getroot();new=E.parse(NET).getroot();checks=[]
def check(label,ok):checks.append(dict(check=label,status='PASS' if ok else 'FAIL'));assert ok,label
for tag in ['edge','junction','connection']:
 key=lambda x:tuple(x.get(k,'') for k in (['from','to','fromLane','toLane'] if tag=='connection' else ['id']))
 aa={key(x):x for x in old.findall(tag)};bb={key(x):x for x in new.findall(tag)};check(tag+'_same_IDs',aa.keys()==bb.keys())
 for k,a in aa.items():
  b=copy.deepcopy(bb[k])
  if tag=='junction' and k==('ramp_mid',):check('only_ramp_mid_type',b.get('type')=='traffic_light');b.set('type','priority')
  if tag=='connection' and k==('ramp_storage','ramp_accel','0','0'):
   check('ramp_meter_exact_control',b.get('tl')=='ramp_mid' and b.get('linkIndex')=='0' and b.get('state')=='O');b.attrib.pop('tl');b.attrib.pop('linkIndex');b.set('state','M')
  check(tag+str(k)+'_unchanged_except_registered',E.tostring(a).strip()==E.tostring(b).strip())
check('urban_TLS_unchanged',E.tostring(old.find("tlLogic[@id='urban_tls']")).strip()==E.tostring(new.find("tlLogic[@id='urban_tls']")).strip())
programs={'A_OPEN':[(60,'G')],'B_MODERATE':[(22,'G'),(3,'y'),(35,'r')],'C_STRONG':[(12,'G'),(3,'y'),(45,'r')]}
check('ramp_program_set',set(x.get('programID') for x in new.findall("tlLogic[@id='ramp_mid']"))==set(programs))
for name,phases in programs.items():
 tl=new.find(f"tlLogic[@id='ramp_mid'][@programID='{name}']");check(name,tl.get('offset')=='0' and [(int(p.get('duration')),p.get('state')) for p in tl]==phases)
lanes={x.get('id'):dict(x.attrib) for x in new.iter('lane')};storage=float(lanes[':urban_diverge_1_0']['length'])+float(lanes['ramp_storage_0']['length']);check('storage_317_57',abs(storage-317.57)<1e-9)
check('aux_usable',280<=float(lanes['merge_section_0']['length'])<=300);check('downstream_gt400',float(lanes['main_down_0']['length'])>400)
check('aux_no_outgoing',not any(x.get('from')=='merge_section' and x.get('fromLane')=='0' for x in new.findall('connection')))
check('all_three_merge_foes_zero',all(x.get('foes')=='000' for x in new.find("junction[@id='freeway_merge']").findall('request')))
argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(HOME/'data/xsd/net_file.xsd'),str(NET)];r=subprocess.run(argv,capture_output=True,text=True);check('compiled_XSD',r.returncode==0)
save(B/'compiled_audit.json',{'status':'PASS_STATIC_ONLY','network':bind(NET),'previous_network':bind(OLD/'build_attempts/BUILD02/network.net.xml'),'checks':checks,'schema':dict(argv=argv,stdout=r.stdout,stderr=r.stderr),'storage_reference_m':storage,'storage_not_calibrated_capacity':True,'lanes':lanes,'runtime_UNTESTED':['WAUT selected program','meter movements and yellow handling','detector operation','LC instrumentation neutrality','spillback and U chain']})
attempts=[];schemas=[]
for id,program,lc,purpose in [('TV_SMOKE_B_LC_ON_S17_attempt1','B_MODERATE',True,'technical_logger_on'),('TV_SMOKE_B_LC_OFF_S17_attempt1','B_MODERATE',False,'technical_logger_off'),('TV_A_S17_attempt1','A_OPEN',True,'primary'),('TV_B_S17_attempt1','B_MODERATE',True,'primary'),('TV_C_S17_attempt1','C_STRONG',True,'primary')]:
 inp=B/'inputs'/id;inp.mkdir(parents=True);run=ROOT/'data/raw/stage6_targeted_validation_20260920_v1'/id;out=run/'outputs'
 (inp/'demand.rou.xml').write_bytes((SOURCE/'demand.rou.xml').read_bytes())
 roles=json.loads((SOURCE/'output_roles.json').read_text());roles.pop('zero_expected_R');roles['required_role_count']=18 if lc else 17;roles['full_time_contract']='FCD/summary/queue labels0..2699. TLS two IDs each labels0..2699 (5400 total). Detectors90 consecutive30s bins.'
 for row in roles['required_xml_roles']:row['path']=str(out/row['role'])
 if lc:roles['required_xml_roles'].append({'kind':'native_lanechange','role':'lanechanges.xml','root':'lanechanges','path':str(out/'lanechanges.xml'),'empty_events_permitted':True})
 roles['lanechange_logging_enabled']=lc;save(inp/'output_roles.json',roles)
 identity=json.loads((SOURCE/'expected_identity_manifest.json').read_text());identity['attempt_id']=id;identity['arm']=program;save(inp/'expected_identity_manifest.json',identity)
 add=E.parse(SOURCE/'scenario.add.xml').getroot()
 for x in add:
  for field in ['file','dest']:
   if field in x.attrib:x.set(field,str(out/Path(x.get(field)).name))
  if x.tag=='timedEvent':x.attrib.pop('source')
 E.SubElement(add,'WAUT',id='targeted_program_selector',refTime='0',startProg=program)
 E.SubElement(add,'wautJunction',wautID='targeted_program_selector',junctionID='ramp_mid')
 xml(inp/'scenario.add.xml',add)
 cfg=E.parse(SOURCE/'scenario.sumocfg').getroot()
 cfg.find('input/net-file').set('value',str(NET));cfg.find('input/route-files').set('value',str(inp/'demand.rou.xml'));cfg.find('input/additional-files').set('value',str(inp/'scenario.add.xml'))
 for x in list(cfg.find('output'))+list(cfg.find('report')):
  if '/' in x.get('value'):x.set('value',str(out/Path(x.get('value')).name))
 if lc:E.SubElement(cfg.find('output'),'lanechange-output',value=str(out/'lanechanges.xml'))
 xml(inp/'scenario.sumocfg',cfg)
 for file,schema in [('scenario.sumocfg','sumoConfiguration.xsd'),('scenario.add.xml','additional_file.xsd'),('demand.rou.xml','routes_file.xsd')]:
  argv=['/usr/bin/xmllint','--nonet','--noout','--schema',str(HOME/'data/xsd'/schema),str(inp/file)];rr=subprocess.run(argv,capture_output=True,text=True);assert rr.returncode==0,rr.stderr;schemas.append(dict(argv=argv,returncode=rr.returncode,stderr=rr.stderr))
 attempts.append(dict(attempt_id=id,program=program,seed=17,purpose=purpose,lanechange_logging=lc,run_root=str(run),output_root=str(out),argv=[str(HOME.parent.parent/'bin/sumo'),'-c',str(inp/'scenario.sumocfg')],inputs=[bind(p) for p in sorted(inp.iterdir())]))
save(B/'input_manifest.json',{'attempts':attempts,'common_network':bind(NET),'source_input_bindings':[bind(p) for p in sorted(SOURCE.iterdir()) if p.is_file()],'allowed_differences':['output paths/identity labels','WAUT startProg A/B/C only traffic intervention selector','technical LC off fixture omits native logger only'],'schema_checks':schemas,'programs':programs,'planned_population':{'M':1333,'R':300,'U':150,'X':75},'demand_window':[0,1500],'simulation_window':[0,2700],'step_s':1})
print('PASS',len(checks),'compiled checks,',len(schemas),'runtime XSD checks;',len(attempts),'unlaunched inputs')
