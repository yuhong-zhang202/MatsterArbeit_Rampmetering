"""C04 regression: synthetic XML and injected fake processes only."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as E
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
from src.analysis import stage6_h2_measurement as m
from src.analysis import stage6_h2_pipeline as pipeline


class FakeClock:
    def __init__(self): self.t=0
    def __call__(self): return self.t
    def sleep(self,seconds): self.t+=seconds


def synthetic_outputs(directory):
    mat=o.read_json(directory/'materialization_manifest.json')
    for path in x.expected_outputs(mat).values():path.write_text('')
    config=E.parse(directory/'scenario.sumocfg').getroot()
    config.tag='sumoConfiguration'
    routes=E.parse(directory/'demand.rou.xml').getroot()
    ids={f.get('id').split('_')[0]:int(f.get('number')) for f in routes.findall('flow')}
    paths={'M':[('main_up_0',100),('main_up_0',200),('main_up_0',1200),(':freeway_merge_1_0',4),('main_down_0',100),('main_down_0',700)],'R':[('urban_in_0',0),('shared_approach_0',0),('ramp_accel_0',0),(':freeway_merge_0_0',4),('main_down_0',0),('main_down_0',100),('main_down_0',700)],'U':[('urban_in_0',0),('shared_approach_0',0),('urban_out_0',0)],'X':[('cross_in_0',0),(':urban_tls_1_0',0),('cross_out_0',0)]}
    trips=E.Element('tripinfos');fcd=E.Element('fcd-export');tls=E.Element('tlsStates');vehroute=E.Element('routes');queues=E.Element('queue-export');summary=E.Element('summary')
    for g,count in ids.items():
        for i in range(count):
            lane,pos=paths[g][0]
            E.SubElement(trips,'tripinfo',id=f'{g}_flow.{i}',depart='0',arrival=str(len(paths[g])),departPos=str(pos),departLane=lane,departDelay='0',timeLoss='0',duration=str(len(paths[g])))
            vehicle=E.SubElement(vehroute,'vehicle',id=f'{g}_flow.{i}',type='technical_passenger',depart='0',arrival=str(len(paths[g])))
            E.SubElement(vehicle,'route',edges=o.ROUTES[g])
    for t in range(2700):
        frame=E.SubElement(fcd,'timestep',time=str(t))
        for g,count in ids.items():
            if t>=len(paths[g]):continue
            lane,pos=paths[g][t]
            for i in range(count):E.SubElement(frame,'vehicle',id=f'{g}_flow.{i}',lane=lane,pos=str(pos),speed='0')
        phase=0 if t%60<45 else 1 if t%60<48 else 2 if t%60<57 else 3
        E.SubElement(tls,'tlsState',time=str(t),id='urban_tls',programID='technical_placeholder',phase=str(phase),state=('Gr','yr','rG','ry')[phase])
        E.SubElement(E.SubElement(queues,'data',timestep=str(t)),'lanes')
        arrived=sum(n for g,n in ids.items() if len(paths[g])<=t);running=sum(ids.values())-arrived
        E.SubElement(summary,'step',time=str(t),loaded=str(sum(ids.values())),inserted=str(sum(ids.values())),running=str(running),waiting='0',ended=str(arrived),arrived=str(arrived),collisions='0',teleports='0',halting=str(running),stopped='0',discarded='0',meanWaitingTime='0',meanTravelTime='0' if arrived else '-1',meanSpeed='0' if running else '-1',meanSpeedRelative='0' if running else '-1')
    (directory/'outputs/tripinfo.xml').write_text('<!--'+E.tostring(config,encoding='unicode')+'-->\n'+E.tostring(trips,encoding='unicode'))
    E.ElementTree(fcd).write(directory/'outputs/fcd.xml');E.ElementTree(tls).write(directory/'outputs/tls_states.xml')
    for name,root in [('queues.xml',queues),('sumo_summary.xml',summary),('vehroute.xml',vehroute)]:E.ElementTree(root).write(directory/'outputs'/name)
    for name,path in x.expected_outputs(mat).items():
        if '_e1_' in name:
            root=E.Element('detector')
            for begin in range(0,2700,30):E.SubElement(root,'interval',id=name[:-4],begin=str(begin),end=str(begin+30),nVehEntered='0',nVehContrib='0',speed='-1',occupancy='0')
            E.ElementTree(root).write(path)
        elif '_e2.' in name:
            root=E.Element('detector')
            for begin in range(0,2700,30):E.SubElement(root,'interval',id=name[:-4],begin=str(begin),end=str(begin+30),sampledSeconds='0',nVehEntered='0',nVehLeft='0',nVehSeen='0',meanSpeed='-1',meanTimeLoss='-1',meanOccupancy='0',maxOccupancy='0')
            E.ElementTree(root).write(path)


class FakeProcess:
    pid=987654321
    def __init__(self,mode):self.mode=mode;self.terminated=False;self.killed=False
    def poll(self):
        if self.killed:return -9
        if self.terminated and self.mode!='kill_required':return -15
        return None if self.mode in ('timeout','kill_required','crash') else 0 if self.mode in ('success','missing','warning','empty_xml') else -11 if self.mode=='signal' else 2
    def terminate(self):self.terminated=True
    def kill(self):self.killed=True
    def wait(self,timeout):
        if self.mode=='kill_required' and not self.killed:raise TimeoutError()
        return self.poll()


class FakeAdapter:
    evidence_scope='synthetic_fixture'
    def __init__(self,mode='success'):self.mode=mode;self.started=0;self.process=None
    def start(self,argv,directory,*,launch_card_path):
        self.started+=1
        if self.mode=='start_exception':raise OSError('synthetic ambiguous startup')
        synthetic_outputs(directory)
        if self.mode=='missing':(directory/'outputs/fcd.xml').unlink()
        if self.mode=='warning':(directory/'outputs/sumo_error.log').write_text('Warning: invalid departPos fallback')
        if self.mode=='empty_xml':(directory/'outputs/queues.xml').write_text('')
        self.process=FakeProcess(self.mode)
        return self.process


class C04Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=o.BATCH,prefix='c04_fixture_')
        self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
        self.no_process=patch('subprocess.Popen',side_effect=AssertionError('real subprocess forbidden'))
        self.no_process.start();self.addCleanup(self.no_process.stop)
        self.card=x.prepare_launch_card(self.d);self.card_path=self.d/'proposed_launch_card.json'
        self.journal=x.Journal(self.d/'budget_journal');self.clock=FakeClock()
    def run_attempt(self,index=0,mode='success',**kwargs):
        adapter=FakeAdapter(mode)
        result=x.execute_attempt(self.card_path,self.card['attempts'][index]['attempt_id'],self.journal,adapter,clock=self.clock,sleep=lambda seconds:self.clock.sleep(60 if mode in ('timeout','kill_required') else seconds),allow_fixture=True,**kwargs)
        return result,adapter
    def gate(self,name):
        x.exclusive_json(self.journal.directory/(name+'.json'),{'accepted':True,'launch_payload_sha256':x.payload_sha(self.card),'evidence_bindings':[o.bind(self.card_path)],'evidence_scope':'synthetic_fixture'})
    def test_card_five_precise_materializations_zero_starts_and_disabled_live(self):
        self.assertEqual(len(x.validate_launch_card(self.card_path)['attempts']),5)
        self.assertEqual(self.journal.counters()['actual_starts_observed'],0)
        for adapter in (x.RealProcessAdapter(),x.RealProcessAdapter(enable=True)):
            with self.assertRaises(o.EvidenceError):x.execute_attempt(self.card_path,self.card['attempts'][0]['attempt_id'],self.journal,adapter)
        self.assertEqual(self.journal.counters()['sumo'],0)
    def test_fake_success_and_duplicate_refusal(self):
        receipt,adapter=self.run_attempt();self.assertEqual(receipt['execution_status'],'completed');self.assertEqual(adapter.started,1)
        self.assertEqual(self.journal.counters()['actual_starts_observed'],1)
        with self.assertRaises(o.EvidenceError):self.run_attempt()
    def test_timeout_kill_and_failed_output_are_retained(self):
        receipt,adapter=self.run_attempt(mode='kill_required')
        self.assertTrue(adapter.process.terminated and adapter.process.killed)
        self.assertEqual(receipt['reason'],'timeout');self.assertTrue(receipt['output_bindings'])
    def test_archive_overrun_is_retained_and_blocks_retry(self):
        with patch.object(x,'attempt_bytes',return_value=2000000001):receipt,_=self.run_attempt()
        self.assertEqual(receipt['reason'],'archive_size_limit')
        self.assertTrue(self.journal.load()[0]['stop_violations'])
        parent=Path(self.card['attempts'][0]['materialization']['path']).parent/'execution_receipt.json'
        with self.assertRaises(o.EvidenceError):x.materialize_retry(self.card_path,o.bind(parent),self.journal,allow_fixture=True)
    def test_nonzero_and_signal_are_not_scientific_negatives(self):
        receipt,_=self.run_attempt(mode='signal');self.assertEqual(receipt['reason'],'signal');self.assertEqual(receipt['execution_status'],'technical_failure')
    def test_missing_output_and_warning_are_technical_failures(self):
        receipt,_=self.run_attempt(mode='missing');self.assertEqual(receipt['reason'],'missing_output')
        self.assertNotIn('fcd.xml',receipt['output_bindings'])
    def test_warning_fallback_is_preserved(self):
        receipt,_=self.run_attempt(mode='warning');self.assertEqual(receipt['reason'],'diagnostic_anomaly')
    def test_start_crash_stays_charged_unknown_and_cannot_resume(self):
        receipt,_=self.run_attempt(mode='start_exception');self.assertEqual(receipt['execution_status'],'unknown')
        self.assertEqual(self.journal.counters()['reserved_or_unknown'],1)
        with self.assertRaises(o.EvidenceError):self.run_attempt()
    def test_persistent_stale_lock_and_alternate_journal_block(self):
        (self.journal.directory/'journal.lock').write_text('fake stale owner')
        with self.assertRaises(FileExistsError):self.run_attempt()
        other=self.d/'other';other.mkdir()
        with self.assertRaises(o.EvidenceError):x.execute_attempt(self.card_path,self.card['attempts'][0]['attempt_id'],x.Journal(other),FakeAdapter(),allow_fixture=True)
    def test_unique_same_parameter_retry_and_smoke_exclusion(self):
        receipt,_=self.run_attempt(mode='nonzero')
        parent=Path(self.card['attempts'][0]['materialization']['path']).parent/'execution_receipt.json'
        retry=x.materialize_retry(self.card_path,o.bind(parent),self.journal,allow_fixture=True)
        result=x.execute_attempt(self.card_path,retry['attempt_id'],self.journal,FakeAdapter(),clock=self.clock,sleep=self.clock.sleep,allow_fixture=True)
        self.assertEqual(result['execution_status'],'completed');self.assertEqual(self.journal.counters()['retry'],1)
        with self.assertRaises(o.EvidenceError):x.materialize_retry(self.card_path,o.bind(parent),self.journal,allow_fixture=True)
        with self.assertRaises(o.EvidenceError):x.verify_executed_source(o.bind(Path(retry['materialization']['path']).parent/'execution_receipt.json'),retry['run_id'],allow_fixture=True)
    def test_review_pause_and_source_identity_chain(self):
        self.run_attempt()
        with self.assertRaises(o.EvidenceError):self.run_attempt(1)
        self.gate('smoke_acceptance');receipt,_=self.run_attempt(1)
        rp=Path(self.card['attempts'][1]['materialization']['path']).parent/'execution_receipt.json'
        identity=x.verify_executed_source(o.bind(rp),receipt['run_id'],allow_fixture=True)
        self.assertEqual(identity['seed'],'17')
        with self.assertRaises(o.EvidenceError):x.verify_executed_source(o.bind(rp),receipt['run_id'])
        with self.assertRaises(o.EvidenceError):x.verify_executed_source(o.bind(rp),'S6_V1_ML_S23',allow_fixture=True)
        names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{p}_l{i}.xml' for p in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for i in (0,1)}
        sources={n:receipt['output_bindings'][n] for n in names};sources['network.net.xml']=receipt['network']
        manifest=m.analyze_to_new_directory(sources,receipt['run_id'],self.d/'analysis',execution_receipt=o.bind(rp),allow_fixture=True)
        self.assertEqual(manifest['evidence_scope'],'synthetic_fixture')
        measured=o.read_json(o.verify_binding(manifest['output']))
        self.assertEqual(measured['feeder_science_inputs']['run_identity']['run_id'],receipt['run_id'])
        self.assertEqual(measured['schedule_verification']['status'],'pending_exact_schedule')
        x.verify_scientific_identity(measured['feeder_science_inputs']['run_identity'],allow_fixture=True)
        rule_manifest=pipeline.assemble_rule_tables([o.bind(self.d/'analysis/analysis_manifest.json')],self.d/'unpaired_rules',allow_fixture=True)
        self.assertEqual(rule_manifest['counts'],{'main':352,'sensitivity':14})
        self.assertFalse(rule_manifest['all_required_supported'])
        receipt_c,_=self.run_attempt(2)
        rp_c=Path(self.card['attempts'][2]['materialization']['path']).parent/'execution_receipt.json'
        sources_c={n:receipt_c['output_bindings'][n] for n in names};sources_c['network.net.xml']=receipt_c['network']
        m.analyze_to_new_directory(sources_c,receipt_c['run_id'],self.d/'analysis_c',execution_receipt=o.bind(rp_c),allow_fixture=True)
        paired=pipeline.assemble_rule_tables([o.bind(self.d/'analysis/analysis_manifest.json'),o.bind(self.d/'analysis_c/analysis_manifest.json')],self.d/'paired_rules',allow_fixture=True)
        self.assertEqual(paired['counts'],{'main':352,'sensitivity':14})
        self.assertFalse(paired['all_required_supported'])
        self.assertEqual(o.read_json(self.d/'paired_rules/pair_results.json')['17']['scientific_result'],'not_resolved')
        with self.assertRaises(o.EvidenceError):self.run_attempt(3)
    def test_receipt_role_seed_condition_hash_and_status_tampering(self):
        self.run_attempt();self.gate('smoke_acceptance');r,_=self.run_attempt(1)
        path=Path(self.card['attempts'][1]['materialization']['path']).parent/'execution_receipt.json'
        changes=[('seed','23'),('condition','C'),('run_id','S6_V1_ML_S23'),('role','smoke'),('execution_status','unknown'),('exit_code',1)]
        for field,value in changes:
            altered=copy.deepcopy(r);altered[field]=value;path.write_bytes(o.encode(altered))
            with self.subTest(field=field),self.assertRaises(o.EvidenceError):x.verify_executed_source(o.bind(path),r['run_id'],allow_fixture=True)
        path.write_bytes(o.encode(r))
        valid=x.verify_executed_source(o.bind(path),r['run_id'],allow_fixture=True)
        self.assertEqual(valid['condition'],'ML')
        fcd=Path(r['output_bindings']['fcd.xml']['path']);fcd.write_text('<fcd-export/>')
        with self.assertRaises(o.EvidenceError):x.verify_executed_source(o.bind(path),r['run_id'],allow_fixture=True)
    def test_crash_after_start_stops_fake_process_and_keeps_unknown(self):
        adapter=FakeAdapter('crash')
        def interrupted_sleep(seconds):raise KeyboardInterrupt()
        receipt=x.execute_attempt(self.card_path,self.card['attempts'][0]['attempt_id'],self.journal,adapter,clock=self.clock,sleep=interrupted_sleep,allow_fixture=True)
        self.assertEqual(receipt['execution_status'],'unknown')
        self.assertTrue(adapter.process.terminated)
        self.assertEqual(self.journal.counters()['actual_starts_observed'],1)
    def test_journal_replay_detects_state_tamper_and_budget_reserves(self):
        aid=self.card['attempts'][0]['attempt_id']
        self.journal.append({'event':'reserve','attempt_id':aid,'run_id':'S6_V1_ML_S17','role':'smoke','parameter_hash':'fixed'})
        self.assertEqual(self.journal.counters()['sumo'],1)
        self.assertEqual(self.journal.counters()['actual_starts_observed'],0)
        self.journal.recover_unknown(aid)
        with self.assertRaises(o.EvidenceError):self.journal.append({'event':'reserve','attempt_id':'S6_V1_ML_S17_attempt2','run_id':'S6_V1_ML_S17','role':'smoke','parameter_hash':'fixed'})
        last=self.journal.directory/'event_0001.json';payload=o.read_json(last);payload['state']['attempts'][0]['state']='completed';last.write_bytes(o.encode(payload))
        with self.assertRaises(o.EvidenceError):self.journal.load()
    def test_live_approval_must_bind_payload_and_fixture_gate_cannot_pass_real(self):
        forged=copy.deepcopy(self.card);forged.update(status='User-approved',launch_eligible=True,user_approval={'approved_payload_sha256':'bad','scope':'Stage6_exact_SUMO_launch','evidence':o.bind(o.CARD)})
        self.card_path.write_bytes(o.encode(forged))
        with self.assertRaises(o.EvidenceError):x.validate_launch_card(self.card_path,require_approval=True)
        with self.assertRaises(o.EvidenceError):x.execute_attempt(self.card_path,self.card['attempts'][0]['attempt_id'],self.journal,x.RealProcessAdapter(enable=True))
    def test_exact_schedule_requires_independent_provenance(self):
        trips={'M_flow.0':{'depart':1.,'departDelay':.5}}
        self.assertFalse(x.verify_reported_schedule(trips)['no_additional_blockage_claim'])
        p=self.d/'schedule.json';x.exclusive_json(p,{'independently_verified':True,'time_unit':'seconds','planned_depart_s':{'M_flow.0':.5},'provenance_bindings':[o.bind(self.card_path)]})
        self.assertEqual(x.verify_reported_schedule(trips,o.bind(p))['status'],'reported_fields_consistent')
        trips['M_flow.0']['departDelay']=0
        self.assertEqual(x.verify_reported_schedule(trips,o.bind(p))['status'],'schedule_report_mismatch')
    def test_auxiliary_E2_empty_or_wrong_period_is_not_coverage(self):
        target=Path(self.card['attempts'][0]['materialization']['path']).parent
        synthetic_outputs(target)
        receipt={'output_bindings':{n:o.bind(p) for n,p in x.expected_outputs(o.read_json(target/'materialization_manifest.json')).items()}}
        observations={'tripinfo':{'M_flow.0':{'depart':0,'timeLoss':0,'duration':6}}}
        self.assertEqual(len(pipeline.validate_auxiliary_context(receipt,observations)),2)
        p=target/'outputs/ramp_storage_e2.xml';p.write_text('<detector/>');receipt['output_bindings'][p.name]=o.bind(p)
        with self.assertRaises(o.EvidenceError):pipeline.validate_auxiliary_context(receipt,observations)
    def test_all_required_XML_roles_reject_empty_malformed_wrong_root_and_swaps(self):
        target=Path(self.card['attempts'][0]['materialization']['path']).parent;synthetic_outputs(target)
        mat=o.read_json(target/'materialization_manifest.json');report=x.validate_required_xml_outputs(mat)
        self.assertEqual(len(report['roles']),14)
        expected=x.expected_outputs(mat)
        for name in report['roles']:
            path=expected[name];original=path.read_bytes()
            for kind,payload in [('empty',b''),('malformed',b'<broken>'),('wrong_root',b'<wrong/>')]:
                path.write_bytes(payload)
                with self.subTest(role=name,kind=kind),self.assertRaises(o.EvidenceError):x.validate_required_xml_outputs(mat)
            path.write_bytes(original)
        for left,right in [('queues.xml','sumo_summary.xml'),('tripinfo.xml','vehroute.xml'),('merge_upstream_e1_l0.xml','merge_upstream_e1_l1.xml'),('ramp_storage_e2.xml','shared_boundary_e2.xml')]:
            a,b=expected[left],expected[right];aa,bb=a.read_bytes(),b.read_bytes();a.write_bytes(bb);b.write_bytes(aa)
            with self.subTest(swap=(left,right)),self.assertRaises(o.EvidenceError):x.validate_required_xml_outputs(mat)
            a.write_bytes(aa);b.write_bytes(bb)
    def test_required_XML_time_identity_and_counter_constraints(self):
        target=Path(self.card['attempts'][0]['materialization']['path']).parent;synthetic_outputs(target);mat=o.read_json(target/'materialization_manifest.json')
        edits=[('queues.xml',lambda r:r.remove(r[-1])),('sumo_summary.xml',lambda r:r[0].set('running','nan')),('vehroute.xml',lambda r:r[0].set('id','unknown')),('vehroute.xml',lambda r:r[0][0].set('edges','main_up')),('vehroute.xml',lambda r:r[0].set('arrival','99')),('queues.xml',lambda r:r[0].set('timestep','1'))]
        for name,edit in edits:
            path=target/'outputs'/name;original=path.read_bytes();root=E.fromstring(original);edit(root);E.ElementTree(root).write(path)
            with self.subTest(name=name),self.assertRaises(o.EvidenceError):x.validate_required_xml_outputs(mat)
            path.write_bytes(original)
    def test_empty_context_XML_cannot_produce_qualified_analysis_or_T_MEASURE(self):
        self.run_attempt();self.gate('smoke_acceptance');receipt,_=self.run_attempt(1,mode='empty_xml')
        self.assertEqual(receipt['execution_status'],'technical_failure');self.assertEqual(receipt['reason'],'invalid_required_xml')
        self.assertEqual(receipt['required_xml_validation']['status'],'failed')
        rp=Path(self.card['attempts'][1]['materialization']['path']).parent/'execution_receipt.json'
        names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{p}_l{i}.xml' for p in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for i in (0,1)}
        source={n:receipt['output_bindings'][n] for n in names};source['network.net.xml']=receipt['network']
        output=self.d/'rejected_analysis'
        with self.assertRaises(o.EvidenceError):m.analyze_to_new_directory(source,receipt['run_id'],output,execution_receipt=o.bind(rp),allow_fixture=True)
        self.assertTrue((output/'analysis_error.json').exists());self.assertFalse((output/'analysis_manifest.json').exists())
        rules=pipeline.assemble_rule_tables([],self.d/'missing_rules',allow_fixture=True)
        self.assertFalse(rules['all_required_supported'])
        self.assertFalse(any(r['rule_id']=='T_MEASURE' and r['result']=='supported_bounded' for r in o.read_json(self.d/'missing_rules/resolution_rule_results.json')))


if __name__=='__main__':unittest.main()
