#!/usr/bin/env python3
"""Read-only compiled-network audit; writes only separate review artifacts."""
from pathlib import Path
import hashlib,json,os,subprocess,xml.etree.ElementTree as ET
ROOT=Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering');B=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering';O=B/'build_attempts/BUILD02';D=B/'build02_compiled_review_revision01'
D.mkdir(exist_ok=False)
def bind(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(n,v):
 with (D/n).open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
checks=[]
def check(name,ok,evidence,scope='compiled'):
 checks.append({'check':name,'status':'PASS' if ok else 'FAIL','evidence':evidence,'scope':scope})
def na(name,why):checks.append({'check':name,'status':'NOT_EVALUABLE','evidence':why,'scope':'runtime'})
initial={p.name:bind(p) for p in O.iterdir() if p.is_file()};r=json.loads((O/'build_receipt.json').read_text());started=json.loads((O/'started.json').read_text());pid=started['pid']
proc={}
for label,call in [('pid',lambda:os.kill(pid,0)),('process_group',lambda:os.killpg(pid,0))]:
 try:call();proc[label]='exists'
 except ProcessLookupError:proc[label]='absent'
 except PermissionError:proc[label]='permission_denied_unknown'
check('process_and_group_absent',all(v=='absent' for v in proc.values()),proc,'execution')
p=subprocess.run(['/usr/sbin/lsof','-nP','+D',str(O)],capture_output=True,timeout=10)
(D/'lsof.stdout').write_bytes(p.stdout);(D/'lsof.stderr').write_bytes(p.stderr)
check('no_open_attempt_handles_reported',p.returncode==1 and not p.stdout and not p.stderr,{'argv':['/usr/sbin/lsof','-nP','+D',str(O)],'returncode':p.returncode,'stdout_bytes':len(p.stdout),'stderr_bytes':len(p.stderr)},'execution')
sample={'status':'NOT_STARTED_PARENT_OBSERVED_PID_ALREADY_ABSENT','parent_evidence':'Primary first inspected after executor tool yielded; os.kill and os.getpgid for24060 both raised ProcessLookupError. No sample command was started.','timing_deviation':'The first observation time relative to t+2 was not recorded; cannot claim an exact2s skip. No post-hoc sample was attempted.','matching_files':[str(p) for p in O.rglob('*') if 'sample' in p.name.lower()],'consequence':'No live stack evidence; this limits diagnosis, not XML existence. Independent reviewer must assess this procedural deviation.'}
check('no_sample_file_or_partial',not sample['matching_files'],sample,'execution')
check('wrapper_success',r['returncode']==0 and r['status']=='completed_pending_compiled_review',{'returncode':r['returncode'],'status':r['status']},'execution')
for name,row in r['outputs'].items():check('receipt_hash_'+name,bind(O/name)['sha256']==row['sha256'] and (O/name).stat().st_size==row['bytes'],row,'integrity')
exact=sum(x['bytes'] for x in initial.values());pre=exact-(O/'build_receipt.json').stat().st_size
check('directory_byte_reconciliation',exact==21096 and pre==r['observed_peak_bytes']==17609,{'before_receipt':pre,'receipt_bytes':(O/'build_receipt.json').stat().st_size,'final_directory_bytes':exact,'expected_printed_final':21096},'execution')
check('observed_resource_lines',exact<=100000000 and r['wallclock_s']<30,{'bytes':exact,'wallclock_s':r['wallclock_s']},'execution')
card=json.loads((B/'build_recovery_diagnosis_revision01/BUILD02_request_card_revision02.json').read_text())
for row in card['inputs']:check('source_identity_'+Path(row['path']).name,bind(Path(row['path']))==row,row,'integrity')
for row in json.loads((B/'BUILD01_execution_delivery_manifest.json').read_text())['files']:check('BUILD01_preserved_'+Path(row['path']).name,bind(Path(row['path']))==row,row,'integrity')
n=ET.parse(O/'network.net.xml').getroot();oldpath=ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused/network.net.xml';old=ET.parse(oldpath).getroot();check('baseline_bound',bind(oldpath)['sha256']=='a83bb0c3a03b7e74cf8c2360336eb0dfbb330073cf8b8f6aea9940ff7cf3d8ea',bind(oldpath),'integrity')
check('network_xml_exists_nonempty_root',n.tag=='net' and (O/'network.net.xml').stat().st_size>0,bind(O/'network.net.xml'))
E={e.get('id'):e for e in n.findall('edge')};L={l.get('id'):l for l in n.findall('edge/lane')};J={j.get('id'):j for j in n.findall('junction')};OL={l.get('id'):l for l in old.findall('edge/lane')};OJ={j.get('id'):j for j in old.findall('junction')};C=[c.attrib for c in n.findall('connection')];external=[c for c in C if not c['from'].startswith(':')]
length=lambda lane:float(L[lane].get('length'))
check('expected_external_edges_lanes',len([x for x in E if not x.startswith(':')])==10 and len([x for x in L if not x.startswith(':')])==14,{'external_edges':len([x for x in E if not x.startswith(':')]),'external_lanes':len([x for x in L if not x.startswith(':')]),'internal_lanes':len([x for x in L if x.startswith(':')])})
expected={(c.get('from'),c.get('to'),c.get('fromLane'),c.get('toLane')) for c in ET.parse(B/'network_inputs/candidate.con.xml').getroot()};actual={(c['from'],c['to'],c['fromLane'],c['toLane']) for c in external}
check('exact10_requested_movements',actual==expected and len(external)==10,{'expected':sorted(expected),'actual':sorted(actual)})
for c in external:
 via=c['via'];check('via_'+via,via in L and any(x['from']==via.rsplit('_',1)[0] and x['fromLane']==via.rsplit('_',1)[1] and x['to']==c['to'] and x['toLane']==c['toLane'] for x in C),c)
merge=[c for c in external if c['to']=='merge_section'];req=[q.attrib for q in J['freeway_merge'].findall('request')]
check('three_merge_requests_nonconflicting',len(merge)==3 and len(req)==3 and all(q['foes']=='000' and q['response']=='000' for q in req) and all(c['state']=='M' for c in merge),{'connections':merge,'requests':req})
check('aux0_no_outgoing',not any(c['from']=='merge_section' and c['fromLane']=='0' for c in external),[c for c in external if c['from']=='merge_section'])
check('two_through_continuations', {(c['fromLane'],c['toLane']) for c in external if c['from']=='merge_section'}=={('1','0'),('2','1')},[c for c in external if c['from']=='merge_section'])
check('aux_usable_280_300',280<=length('merge_section_0')<=300,{'compiled_m':length('merge_section_0'),'nominal_planning_span_m':300})
check('downstream_gt400',all(length(f'main_down_{i}')>400 for i in (0,1)),{'compiled_lane_lengths_m':[length(f'main_down_{i}') for i in (0,1)]})
check('passenger_right_entry_excluded',L['merge_section_1'].get('changeRight')=='authority',L['merge_section_1'].attrib)
check('aux_left_not_prohibited',L['merge_section_0'].get('changeLeft') is None,L['merge_section_0'].attrib)
check('no_unregulated_junctions_or_pass_override',not any(j.get('type') in ['unregulated','right_before_left'] for j in J.values()) and not any(c.get('pass')=='true' for c in C),{'junction_types':sorted(set(j.get('type') for j in J.values()))})
def points(l):return [tuple(map(float,p.split(','))) for p in l.get('shape').split()]
check('aux_geometrically_right',max(y for x,y in points(L['merge_section_0']))<min(y for x,y in points(L['merge_section_1']))<min(y for x,y in points(L['merge_section_2'])),{k:L[k].get('shape') for k in ['merge_section_0','merge_section_1','merge_section_2']})
check('r_approach_stays_below_M_centres',max(y for key in ['ramp_accel_0',':freeway_merge_2_0'] for x,y in points(L[key])) < min(y for key in ['main_up_0',':freeway_merge_0_0'] for x,y in points(L[key])),{'R_max_y':max(y for k in ['ramp_accel_0',':freeway_merge_2_0'] for x,y in points(L[k])),'M_right_y':895.2})
for i in (0,1):
 keys=[f'main_up_{i}',f':freeway_merge_0_{i}',f'merge_section_{i+1}',f':merge_end_0_{i}',f'main_down_{i}'];ys={y for k in keys for x,y in points(L[k])};check('straight_M_alignment_'+str(i),len(ys)==1,{'lanes':keys,'ys':sorted(ys)})
urban=['urban_in_0','shared_approach_0','urban_out_0','cross_in_0','cross_out_0',':urban_tls_0_0',':urban_tls_1_0',':urban_diverge_0_0',':urban_diverge_1_0']
def normalized(l):d=dict(l.attrib);d.setdefault('width','3.20');return d
for lane in urban:check('urban_lane_invariant_'+lane,normalized(L[lane])==normalized(OL[lane]),{'candidate':L[lane].attrib,'baseline':OL[lane].attrib,'normalization':'Missing width interpreted3.2 per bound local sumolib parser; shape/length/speed exact'})
def canon(e):return {'tag':e.tag,'attrs':e.attrib,'children':[canon(x) for x in e]}
for j in ['urban_in','urban_out','cross_in','cross_out','urban_tls','urban_diverge']:check('urban_junction_invariant_'+j,canon(J[j])==canon(OJ[j]),canon(J[j]))
uc=[c for c in C if c['from'] in ['urban_in','shared_approach','cross_in',':urban_tls_0',':urban_tls_1',':urban_diverge_0',':urban_diverge_1']];oc=[c.attrib for c in old.findall('connection') if c.get('from') in ['urban_in','shared_approach','cross_in',':urban_tls_0',':urban_tls_1',':urban_diverge_0',':urban_diverge_1']]
check('urban_connections_invariant',uc==oc,{'candidate':uc,'baseline':oc})
check('TLS_exact_invariant',[canon(t) for t in n.findall('tlLogic')]==[canon(t) for t in old.findall('tlLogic')],[canon(t) for t in n.findall('tlLogic')])
check('ramp_storage_and_mid_invariant',normalized(L['ramp_storage_0'])==normalized(OL['ramp_storage_0']) and normalized(L[':ramp_mid_0_0'])==normalized(OL[':ramp_mid_0_0']),{'storage_m':length('ramp_storage_0'),'ramp_mid_internal_m':length(':ramp_mid_0_0'),'changed_neighborhood':'ramp_accel and freeway merge; storage and ramp_mid geometries unchanged'})
# Offline numeric detector/domain fit is distinct from actually loading detectors in SUMO.
detectors=[]
for attempt in sorted((B/'attempts').iterdir()):
 a=ET.parse(attempt/'scenario.add.xml.template').getroot();ds=[x for x in a if x.tag in ['inductionLoop','laneAreaDetector']];check('detector_counts_'+attempt.name,len([x for x in ds if x.tag=='inductionLoop'])==9 and len([x for x in ds if x.tag=='laneAreaDetector'])==2,{'E1':9,'E2':2})
 for x in ds:
  lane=x.get('lane');start=float(x.get('pos'));end=x.get('endPos');resolved=length(lane) if end=='PENDING_COMPILED_RAMP_STORAGE_LENGTH' else float(end) if end else start
  ok=lane in L and 0<=start<=resolved<=length(lane) and x.get('friendlyPos')=='false';check('detector_fit_'+attempt.name+'_'+x.get('id'),ok,{'lane':lane,'pos':start,'resolved_endPos':resolved,'lane_length':length(lane),'materialized':False})
  if attempt.name=='P1B_SMOKE_R720_S17_attempt1':detectors.append({'id':x.get('id'),'lane':lane,'pos':start,'resolved_endPos':resolved,'actual_loaded_coverage':'NOT_EVALUABLE_NO_SUMO'})
for lane,positions in [('main_up_0',[100,200,1200,1300]),('main_up_1',[100,200,1200,1300]),('merge_section_0',[0,20,294.51]),('main_down_0',[20,200,400]),('main_down_1',[20,200,400])]:check('domain_position_fit_'+lane,all(0<=p<=length(lane) for p in positions),{'positions':positions,'length':length(lane)})
primary=[{'lane':'main_up_0','from':1200,'to':length('main_up_0')},{'lane':':freeway_merge_0_0','from':0,'to':length(':freeway_merge_0_0')},{'lane':'merge_section_1','from':0,'to':length('merge_section_1')},{'lane':':merge_end_0_0','from':0,'to':length(':merge_end_0_0')},{'lane':'main_down_0','from':0,'to':200}]
paths={'M_local_primary_lane_longitudinal_sum_m':sum(x['to']-x['from'] for x in primary),'M_primary_components':primary,'M_total_route_longitudinal_sum_m':sum(length(k) for k in ['main_up_0',':freeway_merge_0_0','merge_section_1',':merge_end_0_0','main_down_0']),'R_only_from_shared_exit_to_aux_terminal_m':sum(length(k) for k in [':urban_diverge_1_0','ramp_storage_0',':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0']),'R_components':{k:length(k) for k in [':urban_diverge_1_0','ramp_storage_0',':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0']},'shared_RU_m':length('shared_approach_0'),'downstream_background_m':200,'downstream_tail_m':length('main_down_0')-400,'interpretation':'Longitudinal geometry sums, not storage vehicle capacity or realized route length; R must perform a safe left lane change within merge_section. Primary same across both M lanes.'}
for a in (B/'attempts').iterdir():
 routes={x.get('id'):x.get('edges').split() for x in ET.parse(a/'demand.rou.xml').getroot().findall('route')}
 for rid,edges in routes.items():check('route_edge_connectivity_'+a.name+'_'+rid,all(any(c['from']==u and c['to']==v for c in external) for u,v in zip(edges,edges[1:])),{'route':edges,'R_lane_change_required':rid=='route_R'})
na('loaded_E1_E2_coverage_and17_role_output','No SUMO invoked; pending final additional materialization and separate technical smoke')
na('M_actual_p100_and_no_aux0_usage','Only route input and permissions verified; trajectory requires separately approved SUMO')
na('R_actual_safe_lane_change_and_passage','Lane connectivity permits intended mechanism; actual safe merge/queue behavior not observed')
na('specific_obstacle_and_two_sided_behavior','No traffic run; unresolved')
# local offline XSD check, not a simulator process
xsd=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo/data/xsd/net_file.xsd');q=subprocess.run(['/usr/bin/xmllint','--nonet','--noout','--schema',str(xsd),str(O/'network.net.xml')],capture_output=True,timeout=15);(D/'network_schema.stdout').write_bytes(q.stdout);(D/'network_schema.stderr').write_bytes(q.stderr);check('local_net_XSD',q.returncode==0,{'returncode':q.returncode,'stderr':q.stderr.decode(),'schema':bind(xsd)})
width_source=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo/tools/sumolib/net/__init__.py')
annotations={'explicit_width_serialization':'Candidate emits width3.20 on every lane; baseline omitted it. Physical urban shape/length/speed and normalized width unchanged; local sumolib parser defaults missing width3.2 at line820.','width_source':bind(width_source),'generated_auxiliary_attribute':{'lane':'merge_section_0','acceleration':'1','source_plain_attribute_present':False,'scope':'Compiler-generated lane metadata, preserved; not a new manually tuned CF/LC setting. Runtime consequences not evaluated.'},'timestamp_metadata':'netconvert XML comment timezone suffix+01:00 conflicts with local+02:00 receipt context; use wrapper UTC epoch for execution timing. Does not change geometry.'}
save('compiled_checks.json',checks);save('compiled_lane_map.json',[dict(l.attrib,edge=eid,internal=eid.startswith(':')) for eid,e in E.items() for l in e.findall('lane')]);save('compiled_connections.json',C);save('detector_domain_resolution.json',{'detectors':detectors,'paths':paths});save('compiled_annotations.json',annotations)
final={p.name:bind(p) for p in O.iterdir() if p.is_file()};check('no_attempt_file_changed_during_audit',initial==final,{'file_count':len(final)},'integrity');save('final_integrity_check.json',checks[-1])
summary={'status':'PASS_STATIC_COMPILED_ONLY' if not any(c['status']=='FAIL' for c in checks) else 'FAIL_STATIC_COMPILED','counts':{s:sum(c['status']==s for c in checks) for s in ['PASS','FAIL','NOT_EVALUABLE']},'process':proc,'sample':sample,'exact_final_attempt_bytes':sum(x['bytes'] for x in final.values()),'attempt_files':list(final.values()),'wrapper_receipt_immutable':bind(O/'build_receipt.json'),'network':bind(O/'network.net.xml'),'compiled_geometry':{'aux_m':length('merge_section_0'),'main_down_m':length('main_down_0'),'main_up_m':length('main_up_0')},'paths':paths,'annotations':annotations,'no_build_or_simulation_calls_by_this_audit':True,'SUMO_launch_released':False,'independent_acceptance_pending':True,'confidence':'High for static XML and file accounting; Unknown for traffic behavior'}
save('engineering_closeout.json',summary);print(json.dumps({'status':summary['status'],'counts':summary['counts'],'bytes':summary['exact_final_attempt_bytes'],'paths':paths},indent=2))
