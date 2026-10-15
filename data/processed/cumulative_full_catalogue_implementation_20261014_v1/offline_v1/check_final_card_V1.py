"""Exact offline card readback only; no profile, worker, SUMO or runtime imports."""
import pathlib,json,hashlib,xml.etree.ElementTree as ET
ROOT=pathlib.Path.cwd();OUT=ROOT/'data/processed/cumulative_full_catalogue_implementation_20261014_v1/offline_v1'
p=ROOT/'artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/packages_v1/UA_CUMULATIVE_FULL750_S17_01/card.json';c=json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='da64599b03875f92bb99a6d45691f5d918b9cc77420c0a0b755d3ef0acc5db8c'
assert c['status']=='PREPARED_NOT_RELEASED' and c['SUMO_execution_authorized'] is False and c['numerical_exception_authority']['enabled'] is False
s=c['spec'];expected={str(t):([5,3,2] if t==10 else [4,min(5,t-6),t-4-min(5,t-6)]) for t in range(8,25)}
assert (s['run_id'],s['mode'],s['end_s'],s['activation_s'],s['step_s'],s['seed'])==('UA_CUMULATIVE_FULL750_S17_01','fixed750',1296,1200,1,17)
assert s['catalogue_periods_s']==list(range(8,25)) and s['phase_durations_s']==expected and s['scheduler']=='ACTUAL_C_MINUS_N_BOUNDARY_ONLY'
assert s['qMain']==3600 and s['qRamp']==900 and s['service_command_veh_h']==750
assert len(c['sources_sha256'])==125
for label in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
 for name,h in c[label].items():assert sha(ROOT/name)==h,(label,name)
for name,h in c['environment']['files_sha256'].items():assert sha(pathlib.Path(name))==h
assert hashlib.sha256(json.dumps(c['sources_sha256'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==c['common_runtime_source_sha256']=='c47879667efe4e92ae867353233b96ade1fb48d0cf879fdeed6b6921e86bab21'
for f in ('actual.py','core.py','evidence.py','_phase.py'):
 path='scripts/cumulative_full_catalogue_audit_20261014_v1/'+f;assert c['sources_sha256'][path]==sha(ROOT/path)
assert c['audit_contract']['reader']=='scripts/cumulative_full_catalogue_audit_20261014_v1/actual.py' and c['audit_contract']['schema']=='CUMULATIVE_FULL_C_N_V1'
assert all(v is None for v in c['observations'].values())
assert c['resources']==dict(wall_limit_s=300,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000)
assert c['proposed_new_single_run_envelope']==dict(monitored_s=300,raw_bytes=None)
cfg=ET.parse(ROOT/c['package']/'scenario.sumocfg').getroot();add=pathlib.Path(cfg.find('./input/additional-files').get('value'));add=add if add.is_absolute() else ROOT/c['package']/add
x=ET.parse(add).getroot();table=[]
for t in range(8,25):
 name='T10_G5Y3_NATIVE' if t==10 else f'I12_PACKET{t}';node=x.find("tlLogic[@id='ramp_mid'][@programID='%s']"%name);assert node is not None
 phases=[dict(q.attrib) for q in node.findall('phase')]
 assert [q['state'] for q in phases]==['G','y','r'] and [int(float(q['duration'])) for q in phases]==expected[str(t)] and [q['next'] for q in phases]==['1','2','0']
 table.append(dict(T=t,program=name,phases=phases))
result={'status':'PASS_EXACT_OFFLINE_CARD_BINDING_ONLY','card_sha256':sha(p),'source_count':125,'source_digest':c['common_runtime_source_sha256'],'17_XML_programs':table,'observations':c['observations'],'fresh_native_version':False,'native_raw_exists':(ROOT/c['output']).parent.exists(),'execution_authorized':False,'full_native_pipeline_executed':False,'reader_four_methods':'PASS0.880s_REUSED_NOT_RERUN','resources':'PROPOSED_NOT_EXECUTION_APPROVAL'}
assert not result['native_raw_exists']
with (OUT/'FINAL_CARD_READBACK_V1.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('PASS_EXACT_OFFLINE_CARD_BINDING_ONLY')
