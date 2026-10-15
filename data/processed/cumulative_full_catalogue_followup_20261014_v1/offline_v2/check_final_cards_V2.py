"""Static exact two-card readback; no runtime/profile/native process imports."""
import pathlib,sys,json,hashlib,xml.etree.ElementTree as ET,ast
ROOT=pathlib.Path.cwd();sys.path.insert(0,str(ROOT));OUT=ROOT/'data/processed/cumulative_full_catalogue_followup_20261014_v1/offline_v2'
from scripts.cumulative_full_catalogue_followup_audit_20261014_v1.scope import check_card_scope
expected={'UA_CUMULATIVE_FULL_DYNAMIC_S17_01':'68e9b2c73d7164a1bd10199e77ca43bcb42332e680a240b0828091ec45a3ed34','UA_CUMULATIVE_FULL_ALINEA_S17_01':'f26cdd8e72a66d4efc782628a4107734af18c3539fc1a0073bd16f2e717786db'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={};source_maps=[]
for run,h in expected.items():
 p=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/packages_v2'/run/'card.json';c=json.loads(p.read_text());assert sha(p)==h
 mode=check_card_scope(c);assert c['status']=='PREPARED_NOT_RELEASED' and c['SUMO_execution_authorized'] is False and all(x is None for x in c['observations'].values())
 assert c['resources']==dict(wall_limit_s=300,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000)
 assert c['spec']['total_resource_envelope']==c['spec']['single_resource_envelope']==c['proposed_new_single_run_envelope']==dict(monitored_s=300,raw_bytes=None)
 assert c['spec']['combined_resource_envelope']==c['new_two_run_envelope']==dict(monitored_s=600,raw_bytes=None)
 for key in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
  for name,v in c[key].items():assert sha(ROOT/name)==v,(key,name)
 for name,v in c['environment']['files_sha256'].items():assert sha(pathlib.Path(name))==v
 assert len(c['sources_sha256'])==136 and hashlib.sha256(json.dumps(c['sources_sha256'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==c['common_runtime_source_sha256']=='5d0695195a2062f4708f455b227901b9084a76acca86dc81b34cc59e93d6d85e'
 for f in ('actual.py','scope.py'):
  name='scripts/cumulative_full_catalogue_followup_audit_20261014_v1/'+f;assert c['sources_sha256'][name]==sha(ROOT/name);ast.parse((ROOT/name).read_text())
 assert c['audit_contract']['reader']=='scripts/cumulative_full_catalogue_followup_audit_20261014_v1/actual.py' and c['audit_contract']['schema']=='CUMULATIVE_FULL_C_N_V1'
 assert c['spec']['qMain']==3600 and c['spec']['qRamp']==900 and c['spec']['initial_command_veh_h']==(300 if mode=='dynamic_commands' else 900)
 cfg=ET.parse(ROOT/c['package']/'scenario.sumocfg').getroot();a=pathlib.Path(cfg.find('./input/additional-files').get('value'));a=a if a.is_absolute() else ROOT/c['package']/a;x=ET.parse(a).getroot()
 for t in range(8,25):
  name='T10_G5Y3_NATIVE' if t==10 else f'I12_PACKET{t}';node=x.find("tlLogic[@id='ramp_mid'][@programID='%s']"%name);assert node is not None
  phases=[dict(q.attrib) for q in node.findall('phase')];assert [q['state'] for q in phases]==['G','y','r'] and [int(float(q['duration'])) for q in phases]==c['spec']['phase_durations_s'][str(t)] and [q['next'] for q in phases]==['1','2','0']
 assert not (ROOT/c['output']).parent.exists()
 source_maps.append(c['sources_sha256']);result[run]={'status':'PASS_EXACT_OFFLINE_CARD_BINDING_ONLY','card_sha256':h,'mode':mode,'source_count':136,'source_digest':c['common_runtime_source_sha256'],'reader_contract':c['audit_contract'],'resources':c['resources'],'combined_resource_envelope':c['new_two_run_envelope'],'actual_observations':c['observations'],'new_raw_exists':False,'native_pipeline_executed':False,'execution_authority_generated_by_data_agent':False}
assert source_maps[0]==source_maps[1]
with (OUT/'FINAL_CARDS_READBACK_V2.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('PASS_TWO_EXACT_OFFLINE_CARDS_SAME136_SOURCE')
