import sys,json,hashlib,csv,copy,ast
from pathlib import Path
import xml.etree.ElementTree as E
from unittest.mock import patch
ROOT=Path.cwd();sys.path.insert(0,str(ROOT))
D=ROOT/'data/processed/stage6_obstacle_20260913_v1/c04_data_review_revision_01';B=D.parent;P=B/'c04_launch_preparation_revision_01'
from src.scenarios import stage6_h2_execution as x, stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m,stage6_h2_pipeline as p
checks=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail});assert ok,name

def js(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bind(path):return {'path':str(path),'sha256':sha(path)}
def save(path,data):
 with path.open('x') as f:json.dump(data,f,indent=2,sort_keys=True,allow_nan=False)
def reject(name,fn):
 try:fn()
 except (o.EvidenceError,FileExistsError,KeyError,ValueError):ck(name,True);return
 ck(name,False)
# Independent byte inventories and XML checks, no production parser as oracle.
manifest=js(P/'package_manifest.json')
for i,b in enumerate(manifest['files']):ck('package_file_'+str(i),sha(b['path'])==b['sha256'])
card=js(P/'proposed_launch_card.json');ck('launch_false',card['launch_eligible'] is False and card['status']=='Proposed' and card['user_approval'] is None)
ck('real_journal_empty',not list((P/'budget_journal').iterdir()))
ck('five_distinct',len(card['attempts'])==len({r['attempt_id'] for r in card['attempts']})==5)
for r in card['attempts']:
 mat=js(r['materialization']['path']);ck(r['attempt_id']+'_manifest',sha(r['materialization']['path'])==r['materialization']['sha256'])
 for k in ('card','source_manifest','implementation','measurement_implementation','execution_implementation','binary','network'):ck(r['attempt_id']+'_'+k,sha(mat[k]['path'])==mat[k]['sha256'])
 for name,b in mat['files'].items():ck(r['attempt_id']+'_'+name,sha(b['path'])==b['sha256'])
 config=E.parse(mat['files']['scenario.sumocfg']['path']).getroot();flow=E.parse(mat['files']['demand.rou.xml']['path']).getroot().findall('flow')
 condition='ML' if '_ML_' in r['run_id'] else 'C';counts={'M':1083 if condition=='ML' else 1333,'R':300,'U':150,'X':75}
 ck(r['attempt_id']+'_counts',all(int(f.get('number'))==counts[f.get('id')[0]] for f in flow))
 ck(r['attempt_id']+'_p100',next(f for f in flow if f.get('id')[0]=='M').get('departPos')=='100')
 ck(r['attempt_id']+'_seed',config.find('.//seed').get('value')==r['run_id'][-2:])
 ck(r['attempt_id']+'_argv',r['argv']==[mat['binary']['path'],'-c',mat['files']['scenario.sumocfg']['path']])
keys=list(csv.DictReader((B/'b02_registered_rule_keys_revision_02.csv').open()));sens=list(csv.DictReader((B/'b02_registered_sensitivity_keys_revision_02.csv').open()))
ck('fixed_main_keys',(len(keys),sum(r['applicable']=='true' for r in keys),sum(r['required_for_resolution']=='true' for r in keys),sum(r['applicable']=='false' for r in keys))==(352,150,148,202))
ck('fixed_sensitive_keys',len(sens)==14 and len({tuple(sorted(r.items())) for r in sens})==14)
ck('method_count45',sum(sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse((ROOT/'tests'/name).read_text()))) for name in ('test_stage6_h2_c04.py','test_stage6_h2_measurement.py','test_stage6_h2_offline.py'))==45)
class Clock:
 def __init__(self):self.t=0
 def __call__(self):return self.t
 def sleep(self,s):self.t+=s
class Proc:
 pid=123456789
 def __init__(self,mode):self.mode=mode;self.dead=False;self.killed=False
 def poll(self):return -9 if self.killed else (-15 if self.dead else (None if self.mode in ('timeout','crash') else (2 if self.mode=='nonzero' else 0)))
 def terminate(self):self.dead=True
 def kill(self):self.killed=True
 def wait(self,timeout):return self.poll()
# Synthetic XML is independently authored, mechanically impossible speed/position
# is intentional: this is a negative adapter fixture, not traffic evidence.
def emit(directory):
 mat=js(directory/'materialization_manifest.json');outs=x.expected_outputs(mat)
 for path in outs.values():path.write_text('')
 cfg=E.parse(directory/'scenario.sumocfg').getroot();cfg.tag='sumoConfiguration'
 trips=E.Element('tripinfos');frames=E.Element('fcd-export');tls=E.Element('tlsStates')
 paths={'M':[('main_up_0',100),('main_up_0',200),('main_up_0',1200),('main_down_0',100),('main_down_0',700)],'R':[('urban_in_0',0),('shared_approach_0',1),('ramp_accel_0',1),('main_down_0',1),('main_down_0',700)],'U':[('urban_in_0',0),('shared_approach_0',1),('urban_out_0',1)],'X':[('cross_in_0',0),(':urban_tls_1_0',1),('cross_out_0',1)]}
 flows=E.parse(directory/'demand.rou.xml').getroot().findall('flow')
 for f in flows:
  g=f.get('id')[0]
  for i in range(int(f.get('number'))):E.SubElement(trips,'tripinfo',id=f'{g}_flow.{i}',depart='0',arrival=str(len(paths[g])),departLane=paths[g][0][0],departPos=str(paths[g][0][1]),departDelay='0',timeLoss='0',duration=str(len(paths[g])))
 for t in range(2700):
  frame=E.SubElement(frames,'timestep',time=str(t))
  for f in flows:
   g=f.get('id')[0]
   if t<len(paths[g]):
    lane,pos=paths[g][t]
    for i in range(int(f.get('number'))):E.SubElement(frame,'vehicle',id=f'{g}_flow.{i}',lane=lane,pos=str(pos),speed='0')
  phase=0 if t%60<45 else 1 if t%60<48 else 2 if t%60<57 else 3
  E.SubElement(tls,'tlsState',time=str(t),id='urban_tls',programID='technical_placeholder',phase=str(phase),state=['Gr','yr','rG','ry'][phase])
 outs['tripinfo.xml'].write_text('<!--'+E.tostring(cfg,encoding='unicode')+'-->\n'+E.tostring(trips,encoding='unicode'))
 E.ElementTree(frames).write(outs['fcd.xml']);E.ElementTree(tls).write(outs['tls_states.xml'])
 for name,path in outs.items():
  if '_e1_' not in name and '_e2.' not in name:continue
  root=E.Element('detector')
  for t in range(0,2700,30):
   fields={'nVehEntered':'0','nVehContrib':'0','speed':'-1','occupancy':'0'} if '_e1_' in name else {'sampledSeconds':'0','nVehEntered':'0','nVehLeft':'0','nVehSeen':'0','meanSpeed':'-1','meanTimeLoss':'-1','meanOccupancy':'0','maxOccupancy':'0'}
   E.SubElement(root,'interval',id=name[:-4],begin=str(t),end=str(t+30),**fields)
  E.ElementTree(root).write(path)
class Adapter:
 evidence_scope='synthetic_fixture'
 def __init__(self,mode='success'):self.mode=mode;self.calls=0
 def start(self,argv,directory,*,launch_card_path):
  self.calls+=1
  if self.mode=='start_crash':raise OSError('independent fake startup failure')
  emit(directory)
  if self.mode=='partial':(directory/'outputs/fcd.xml').unlink()
  self.proc=Proc(self.mode);return self.proc
with patch('subprocess.Popen',side_effect=AssertionError('ALL OS PROCESS STARTS FORBIDDEN')):
 # No production test helpers reused.
 F=D/'independent_fake_chain';F.mkdir();fc=x.prepare_launch_card(F);cp=F/'proposed_launch_card.json';j=x.Journal(F/'budget_journal');clock=Clock()
 reject('disabled_real_adapter',lambda:x.execute_attempt(cp,fc['attempts'][0]['attempt_id'],j,x.RealProcessAdapter()))
 reject('unapproved_enabled_real_adapter',lambda:x.execute_attempt(cp,fc['attempts'][0]['attempt_id'],j,x.RealProcessAdapter(enable=True)))
 ck('no_reservation_after_rejection',j.counters()['sumo']==j.counters()['actual_starts_observed']==0)
 receipts=[];analyses=[]
 for i in range(3):
  if i==1:save(j.directory/'smoke_acceptance.json',{'accepted':True,'evidence_scope':'synthetic_fixture','launch_payload_sha256':x.payload_sha(fc),'evidence_bindings':[bind(cp)]})
  entry=fc['attempts'][i];a=Adapter();r=x.execute_attempt(cp,entry['attempt_id'],j,a,clock=clock,sleep=clock.sleep,allow_fixture=True);rp=Path(entry['materialization']['path']).parent/'execution_receipt.json';receipts.append((rp,r))
  ck('fake_completed_'+str(i),r['execution_status']=='completed' and r['evidence_scope']=='synthetic_fixture')
  reject('duplicate_'+str(i),lambda:x.execute_attempt(cp,entry['attempt_id'],j,Adapter(),clock=clock,sleep=clock.sleep,allow_fixture=True))
  reject('fake_not_real_'+str(i),lambda:x.verify_executed_source(bind(rp),r['run_id']))
  if i==0:
   reject('smoke_not_science',lambda:x.verify_executed_source(bind(rp),r['run_id'],allow_fixture=True));continue
  ident=x.verify_executed_source(bind(rp),r['run_id'],allow_fixture=True);ck('bound_validation_'+str(i),ident['run_id']==r['run_id'])
  names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{q}_l{k}.xml' for q in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for k in (0,1)}
  sources={n:r['output_bindings'][n] for n in names};sources['network.net.xml']=r['network'];out=F/('analysis_'+str(i))
  m.analyze_to_new_directory(sources,r['run_id'],out,execution_receipt=bind(rp),allow_fixture=True);analyses.append(bind(out/'analysis_manifest.json'))
  if i==1:
   unpaired=p.assemble_rule_tables(analyses,F/'unpaired',allow_fixture=True);ck('unpaired_no_pass',not unpaired['all_required_supported'])
   srows=js(F/'unpaired/sensitivity_rule_results.json');ck('seven_not_paired',sum(z['value_state']=='not_paired' for z in srows)==7)
 final=p.assemble_rule_tables(analyses,F/'paired_negative',allow_fixture=True)
 rows=js(F/'paired_negative/resolution_rule_results.json');ss=js(F/'paired_negative/sensitivity_rule_results.json')
 ck('negative_denominators',len(rows)==352 and len(ss)==14 and not final['all_required_supported'])
 ck('negative_retained',sum(r['value_state']=='observed_zero' for r in rows)>0 and sum(r['value_state']=='missing_observation' for r in rows)>0)
 ck('seven_negative_sensitivities',sum(r['result']=='not_resolved' for r in ss)==7)
 # Mutation probes alter only isolated audit fixtures and restore bytes afterward.
 rp,r=receipts[1];original=rp.read_bytes()
 for field,val in [('seed','23'),('condition','C'),('run_id','S6_V1_ML_S23'),('role','smoke'),('execution_status','technical_failure'),('execution_status','unknown'),('exit_code',1)]:
  altered=copy.deepcopy(r);altered[field]=val;rp.write_bytes(o.encode(altered));reject('receipt_mutation_'+field+'_'+str(val),lambda:x.verify_executed_source(bind(rp),r['run_id'],allow_fixture=True))
 rp.write_bytes(original)
 fcd=Path(r['output_bindings']['fcd.xml']['path']);raw=fcd.read_bytes();fcd.write_text('<fcd-export/>');reject('output_hash_mutation',lambda:x.verify_executed_source(bind(rp),r['run_id'],allow_fixture=True));fcd.write_bytes(raw)
 # Separate retained failure cases; no simulation process exists.
 for mode in ('timeout','partial','nonzero','start_crash','crash'):
  fd=D/('failure_'+mode);fd.mkdir();c=x.prepare_launch_card(fd);jp=x.Journal(fd/'budget_journal');cl=Clock();ad=Adapter(mode)
  def sleeper(s):
   if mode=='crash':raise KeyboardInterrupt()
   cl.t+=60 if mode=='timeout' else s
  rec=x.execute_attempt(fd/'proposed_launch_card.json',c['attempts'][0]['attempt_id'],jp,ad,clock=cl,sleep=sleeper,allow_fixture=True)
  ck('failure_'+mode,rec['execution_status']==('unknown' if 'crash' in mode else 'technical_failure'))
  ck('failure_charged_'+mode,jp.counters()['sumo']==1)
  reject('failure_relaunch_'+mode,lambda:x.execute_attempt(fd/'proposed_launch_card.json',c['attempts'][0]['attempt_id'],jp,Adapter(),clock=cl,sleep=sleeper,allow_fixture=True))
ck('pending_schedule_no_claim',x.verify_reported_schedule({})=={'status':'pending_exact_schedule','no_additional_blockage_claim':False})
# Independent historical count, not V1 evidence.
hist=js(P/'historical_ML17_compatibility/analysis_manifest.json');trip=E.parse(hist['source_bindings']['tripinfo.xml']['path']).getroot().findall('tripinfo');ck('old_ML17_1608',len(trip)==1608)
summary={'status':'PASS','scope':'C04 offline data preparation only','checks':len(checks),'checks_passed':sum(c['pass'] for c in checks),'simulation_invocations':dict.fromkeys(['SUMO','netconvert','TraCI','GUI'],0),'independent_fake_calls':8,'real_launch_eligible':False,'open_findings':[],'checks_detail':checks,'source_modules':{str(path):sha(path) for path in [Path(x.__file__),Path(o.__file__),Path(m.__file__),Path(p.__file__)]}}
save(D/'data_review_receipt.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k!='checks_detail'},indent=2))
