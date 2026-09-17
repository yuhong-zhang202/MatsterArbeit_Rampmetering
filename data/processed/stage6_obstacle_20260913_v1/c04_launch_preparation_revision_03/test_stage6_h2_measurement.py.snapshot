"""Independent expected values from small synthetic XML, no simulator calls."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as E

from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=o.BATCH,prefix='c02_measure_fixture_')
        self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
        block=patch('subprocess.Popen',side_effect=AssertionError('process forbidden'));block.start();self.addCleanup(block.stop)
        self.lengths={x.get('id'):float(x.get('length')) for x in E.parse(o.ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused/network.net.xml').getroot().findall('.//lane')}
        self.n={'M':1,'R':1,'U':1,'X':0}
        self.make_fixture()

    def write(self,name,root): (self.d/name).write_bytes(E.tostring(root))

    def make_fixture(self):
        trips=E.Element('tripinfos')
        for g,l,p in [('M','main_up_0','100'),('R','ramp_storage_0','10'),('U','shared_approach_0','10')]:
            E.SubElement(trips,'tripinfo',id=f'{g}_flow.0',depart='0',arrival='-1',departPos=p,departDelay='0',departLane=l)
        self.write('tripinfo.xml',trips)
        fcd=E.Element('fcd-export');tls=E.Element('tlsStates')
        for t in range(4):
            frame=E.SubElement(fcd,'timestep',time=str(t))
            E.SubElement(frame,'vehicle',id='M_flow.0',lane='main_up_0',pos=str([100,200,400,500][t]),speed='10')
            E.SubElement(frame,'vehicle',id='R_flow.0',lane=['ramp_storage_0',':ramp_mid_0_0','ramp_accel_0',':freeway_merge_0_0'][t],pos='10',speed='0')
            E.SubElement(frame,'vehicle',id='U_flow.0',lane='shared_approach_0',pos='10',speed='0')
            E.SubElement(tls,'tlsState',time=str(t),id='urban_tls',programID='technical_placeholder',state='Gr')
        self.write('fcd.xml',fcd);self.write('tls_states.xml',tls)
        for prefix in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1'):
            for lane in (0,1):
                name=f'{prefix}_l{lane}';root=E.Element('detector')
                E.SubElement(root,'interval',id=name,begin='0',end='3',nVehEntered='2',nVehContrib='2',speed='10',occupancy='5')
                E.SubElement(root,'interval',id=name,begin='3',end='4',nVehEntered='2',nVehContrib='1',speed='20',occupancy='10')
                self.write(name+'.xml',root)

    def analyze(self):return m.analyze_observations(self.d,self.n,self.lengths,'V1',4,expected_e1_period_s=3)

    def mutate(self,name,fn):
        root=E.parse(self.d/name).getroot();fn(root);self.write(name,root)

    def test_end_to_end_internal_stopped_partition_and_real_tail(self):
        result=self.analyze()
        self.assertEqual(result['regional_stops']['ramp']['R'],[1,1,1,1])
        self.assertEqual(sum(sum(result['regional_stops'][r]['R']) for r in m.REGIONS),4)
        self.assertEqual(result['regional_stops']['shared']['U'],[1,1,1,1])
        e=result['e1']['mainline_merge_entry_e1_l0']
        self.assertEqual(e['e1_nVehEntered_rate']['rate_vehph'],3600)
        self.assertEqual(e['e1_nVehContrib_rate']['rate_vehph'],2700)
        self.assertAlmostEqual(e['e1_nVehContrib_rate']['speed']['value'],40/3)
        self.assertEqual(e['e1_nVehContrib_rate']['covered_seconds'],4)

    def test_fcd_malformed_variants_end_to_end(self):
        changes=[lambda r:r[0][0].attrib.pop('speed'),lambda r:r[0][0].set('speed','NaN'),lambda r:r[0][0].set('speed','inf'),lambda r:r[0][0].set('speed','-1'),lambda r:r[0][0].set('id','M_flow.99'),lambda r:r[0][0].set('lane','unknown'),lambda r:r[0].append(copy.deepcopy(r[0][0])),lambda r:r.remove(r[1]),lambda r:r.append(copy.deepcopy(r[-1])),lambda r:r[1].set('time','1.5'),lambda r:r[1].remove(r[1][0])]
        for change in changes:
            with self.subTest(change=change):
                self.make_fixture();self.mutate('fcd.xml',change)
                with self.assertRaises(o.EvidenceError):self.analyze()

    def test_tls_grid_identity_phase_variants(self):
        for attr,val in [('time','0.5'),('state','rG'),('id','other'),('programID','other')]:
            with self.subTest(attr=attr):
                self.make_fixture();self.mutate('tls_states.xml',lambda r:r[0].set(attr,val))
                with self.assertRaises(o.EvidenceError):self.analyze()

    def test_e1_bad_positive_speed_missing_interval_and_empty_valid(self):
        name='mainline_merge_entry_e1_l0.xml'
        for attr,val in [('speed','-1'),('speed','NaN'),('nVehEntered','-1'),('nVehContrib','-1'),('begin','1')]:
            self.make_fixture();self.mutate(name,lambda r:r[0].set(attr,val))
            with self.assertRaises(o.EvidenceError):self.analyze()
        self.make_fixture()
        def empty(root):
            for row in root:row.set('nVehContrib','0');row.set('speed','-1')
        self.mutate(name,empty)
        e=self.analyze()['e1']['mainline_merge_entry_e1_l0']['e1_nVehContrib_rate']
        self.assertEqual(e['speed'],{'value':None,'value_state':'no_contributors'})
        with self.assertRaises(o.EvidenceError):m.aggregate_e1([{}],'requested_flow')

    def test_E1_period_is_registered_and_final_short_tail_is_exact(self):
        path=self.d/'mainline_merge_entry_e1_l0.xml'
        with self.assertRaises(o.EvidenceError):m.read_e1(path,'mainline_merge_entry_e1_l0',4,expected_period_s=30)
        rows=m.read_e1(path,'mainline_merge_entry_e1_l0',4,expected_period_s=3)
        self.assertEqual([(r['begin'],r['end']) for r in rows],[(0,3),(3,4)])
        with self.assertRaises(TypeError):m.read_e1(path,'mainline_merge_entry_e1_l0',4)
        with self.assertRaises(o.EvidenceError):m.read_e1(path,'mainline_merge_entry_e1_l0',4,expected_period_s=0)

    def test_actual_candidate_position_must_not_skip_feeder(self):
        self.mutate('tripinfo.xml',lambda r:r[0].set('departPos','1300'))
        self.mutate('fcd.xml',lambda r:r[0][0].set('pos','1300'))
        with self.assertRaises(o.EvidenceError):self.analyze()

    def test_endpoint1499_1500_1501_and_no_inlet_flow_equivalence(self):
        ids={'M_flow.0','M_flow.1','M_flow.2'}
        trips={vid:{'depart':1499+i,'arrival':-1,'departDelay':0} for i,vid in enumerate(sorted(ids))}
        self.assertEqual(m.endpoint(ids,trips,1500),{'planned':3,'entered':1,'arrived':0,'in_network':1,'outside':2,'membership':'strictly_before_endpoint'})
        self.assertEqual(m.inlet_qualification(trips,ids)['scientific_result'],'not_resolved')
        self.assertEqual(m.endpoint(ids,trips,2700)['entered'],3)

    def test_2699_censor_bound_and_traceable2700(self):
        self.assertEqual(m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=True)['lower'],1699)
        p=self.d/'endpoint.json';p.write_text(json.dumps({'vehicle_id':'M_flow.0','time_s':2700,'upstream_of_terminal':True,'continuous_identity_qualified':True}))
        later={**o.bind(p),'locator':'vehicle_id=M_flow.0/time_s=2700'}
        self.assertEqual(m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=True,later_evidence=later,vehicle_id='M_flow.0')['lower'],1700)
        with self.assertRaises(o.EvidenceError):m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=False)
        with self.assertRaises(o.EvidenceError):m.travel_interval((999,1000),None,last_confirmed=2699,continuous_to_end=True,later_evidence=later,vehicle_id='M_flow.1')

    def test_raw_trajectory_to_censored_cohort(self):
        result=self.analyze()
        cohort=m.domain_cohort(result['trajectories'],result['tripinfo'],'main_up',200,1200,window=(0,4),horizon=4)
        self.assertEqual(cohort['bounds']['certain_count'],1)
        self.assertEqual(cohort['bounds']['lower'],2)
        self.assertIsNone(cohort['bounds']['upper'])
        self.assertEqual(cohort['records'][0]['last_confirmed_s'],3)

    def test_worst_case_optional_denominators_not_favorable_selection(self):
        bounded=lambda lo,hi:{'lower':lo,'upper':hi,'bound_state':'bounded'}
        result=m.conservative_mean_bounds([bounded(10,12)],[bounded(0,100),bounded(30,40)])
        self.assertEqual(result['lower'],5)
        self.assertEqual(result['lower_denominator'],2)
        self.assertEqual(result['upper'],56)
        self.assertEqual(result['upper_denominator'],2)
        self.assertEqual(result['certain_count'],1)
        self.assertEqual(m.membership((299,300),300,360),'possible_only')
        self.assertEqual(m.membership((359,360),300,360),'possible_only')
        self.assertEqual(m.conservative_mean_bounds([],[])['value_state'],'no_contributors')

    def test_unpaired_outer_union_and_rule_denominators(self):
        self.assertEqual([r['pair_state'] for r in m.paired_rows({'a':1},{'b':2})],['not_paired','not_paired'])
        card=o.load_card();keys,sens=o.read_rule_keys(card)
        def rows(items):
            return [{**r,'value_state':'missing_observation' if r.get('applicable','true')=='true' else 'not_applicable','result':'not_evaluated' if r.get('applicable','true')=='true' else 'not_applicable'} for r in items]
        main=rows(keys);sensitivity=rows(sens)
        self.assertEqual(m.validate_rule_results(main,keys)['required'],148)
        self.assertEqual(m.validate_rule_results(sensitivity,sens,True)['required'],14)
        self.assertFalse(m.validate_rule_results(main,keys)['all_required_supported'])
        with self.assertRaises(o.EvidenceError):m.validate_rule_results(main[:-1],keys)
        main[0]['required_for_resolution']='false'
        with self.assertRaises(o.EvidenceError):m.validate_rule_results(main,keys)

    def test_registered_six_value_states_and_independent_bounds(self):
        self.assertEqual(m.value(0, 'observed_zero'), {'value': 0, 'value_state': 'observed_zero'})
        self.assertEqual(m.value(0)['value_state'], 'observed_zero')
        self.assertEqual(m.value(None, 'not_paired')['value_state'], 'not_paired')
        for state in ('no_contributors', 'missing_observation', 'not_applicable'):
            self.assertIsNone(m.value(None, state)['value'])
        for val, state in ((None, 'unbounded'), (1, 'observed_zero'), (0, 'not_paired'), (None, 'observed_zero')):
            with self.subTest(value=val, state=state), self.assertRaises(o.EvidenceError):
                m.value(val, state)
        keys, _ = o.read_rule_keys(o.load_card())
        rows = [{**r, 'value_state': 'missing_observation' if r['applicable']=='true' else 'not_applicable', 'result': 'not_evaluated' if r['applicable']=='true' else 'not_applicable'} for r in keys]
        i = next(i for i, r in enumerate(rows) if r['applicable']=='true')
        rows[i].update(value_state='observed_zero', value=0, result='supported_bounded', evidence_bindings=[o.bind(o.CARD)])
        self.assertEqual(m.validate_rule_results(rows, keys)['total'], 352)
        rows[i].update(value_state='not_paired', value=None, result='not_evaluated')
        self.assertEqual(m.validate_rule_results(rows, keys)['total'], 352)
        rows[i].pop('value'); rows[i].update(value_state='observed', bound_state='unbounded', upper=None)
        self.assertEqual(m.validate_rule_results(rows, keys)['total'], 352)
        rows[i]['value_state']='unbounded'
        with self.assertRaises(o.EvidenceError): m.validate_rule_results(rows, keys)

    def test_registered_archive_roles_and_wrong_seed_are_rejected(self):
        archive=o.ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/ML17_attempt1'
        names={'tripinfo.xml','fcd.xml','tls_states.xml'} | {f'{p}_l{i}.xml' for p in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for i in (0,1)}
        bindings={name:o.bind(archive/'outputs'/name) for name in names}
        bindings['network.net.xml']=o.bind(archive/'network.net.xml')
        card=o.load_card()
        identity=m.verify_archive_identity(card,o.registered_run(card,'S6_V0_ML_S17'),bindings)
        self.assertEqual((identity['physical_run_id'],identity['condition'],identity['seed']),('ML17','ML','17'))
        for wrong in ('S6_V0_ML_S23','S6_V0_C_S17','S6_V1_ML_S17'):
            destination=self.d/wrong
            with self.subTest(run_id=wrong), self.assertRaises(o.EvidenceError):
                m.analyze_to_new_directory(bindings,wrong,destination)
            self.assertTrue((destination/'analysis_error.json').is_file())
            self.assertFalse((destination/'analysis_manifest.json').exists())
        swapped={**bindings,'fcd.xml':bindings['tripinfo.xml']}
        with self.assertRaises(o.EvidenceError): m.verify_archive_identity(card,o.registered_run(card,'S6_V0_ML_S17'),swapped)

    def test_same_block_no_stitching_and_240_subblock(self):
        speeds=[.9]*4+[None]*16;counts=[20]*20;r=[4,3,3]+[0]*17;ru=[1,1,1]+[0]*17
        self.assertEqual(m.shared_support_block(speeds,counts,r,ru,speed_bins=4),[0])
        self.assertEqual(m.shared_support_block(speeds,counts,[0]*4+[4,3,3]+[0]*13,ru),[])
        self.assertTrue(m.reference_qualification([[10.]*20 for _ in range(20)],[20]*20,500))
        self.assertFalse(m.reference_qualification([[10.]*20 for _ in range(20)],[20]*20,499))

    def test_science_pair_and_all_seven_sensitivities(self):
        def inputs(tt,speed,condition):
            return {'run_identity': {'run_id':f'S6_V1_{condition}_S17','version':'V1','condition':condition,'seed':'17','evidence_scope':'synthetic_fixture'},'source_qualification':'qualified','cohort':{'bounds':{'certain_count':500,'lower':tt,'upper':tt,'bound_state':'bounded'}},'bin_speeds':[[speed]*20 for _ in range(20)],'certain_counts':[25]*20,'r_counts':[4]*20,'ru_labels':[1]*20,'inlet':{'scientific_result':'supported_bounded'}}
        ref,challenge=inputs(10,10,'ML'),inputs(12,9,'C')
        self.assertEqual(m.evaluate_science_pair(ref,challenge,allow_fixture=True)['scientific_result'],'supported_bounded')
        cases=m.evaluate_registered_sensitivities(ref,challenge,allow_fixture=True)
        self.assertEqual(len(cases),7)
        self.assertTrue(all(r['scientific_result']=='supported_bounded' for r in cases.values()))
        ref['cohort']['bounds']['upper']=None
        self.assertEqual(m.evaluate_science_pair(ref,challenge,allow_fixture=True)['scientific_result'],'not_resolved')

    def test_science_pair_rejects_unpaired_or_unregistered_identity(self):
        def item(condition,seed='17',version='V1'):
            return {'source_qualification':'qualified','run_identity':{'run_id':f'S6_{version}_{condition}_S{seed}','condition':condition,'seed':seed,'version':version,'evidence_scope':'synthetic_fixture'}}
        # Rejected before numerical fields are read; no accidental formula pass.
        pairs=[(item('ML'),item('C','23')),(item('C'),item('ML')),(item('ML',version='V0'),item('C')),(item('ML'),item('ML'))]
        forged=item('C');forged['run_identity']['seed']='23';pairs.append((item('ML'),forged))
        missing=item('ML');missing.pop('run_identity');pairs.append((missing,item('C')))
        real=item('ML');real['run_identity']['evidence_scope']='real_output';pairs.append((real,item('C')))
        for left,right in pairs:
            with self.subTest(left=left,right=right), self.assertRaises(o.EvidenceError): m.evaluate_science_pair(left,right,allow_fixture=True)

    def test_failed_analysis_persists_error_without_success_manifest(self):
        destination=self.d/'failed_analysis'
        with self.assertRaises(o.EvidenceError):m.analyze_to_new_directory({},'S6_V1_ML_S17',destination)
        self.assertTrue((destination/'analysis_error.json').is_file())
        self.assertFalse((destination/'analysis_manifest.json').exists())

    def test_full_raw_grid_censor2699_and_disappearance_not_censor(self):
        ids={'M_flow.0'}
        trips={'M_flow.0':{'depart':999.,'arrival':-1.,'departPos':100.,'departDelay':0.,'departLane':'main_up_0'}}
        root=E.Element('fcd-export')
        for t in range(2700):
            frame=E.SubElement(root,'timestep',time=str(t))
            if t>=999:E.SubElement(frame,'vehicle',id='M_flow.0',lane='main_up_0',pos='100' if t==999 else '200',speed='0')
        self.write('long_fcd.xml',root)
        trajectories=m.read_fcd(self.d/'long_fcd.xml',ids,trips,self.lengths)
        cohort=m.domain_cohort(trajectories,trips,'main_up',200,1200)
        self.assertEqual(cohort['bounds']['lower'],1699)
        self.assertEqual(cohort['records'][0]['last_confirmed_s'],2699)
        root[-1].remove(root[-1][0]);self.write('long_fcd.xml',root)
        with self.assertRaises(o.EvidenceError):m.read_fcd(self.d/'long_fcd.xml',ids,trips,self.lengths)

    def test_R_first_downstream_bracket_can_skip_internal_lane(self):
        observations={'analysis_qualification':'qualified','inlet':{'scientific_result':'supported_bounded'},'tripinfo':{'M_flow.0':{'arrival':303},'R_flow.0':{'arrival':304}},'trajectories':{'M_flow.0':[m.Sample(300,'main_up_0',100,10),m.Sample(301,'main_up_0',200,10),m.Sample(302,'main_up_0',1200,10)],'R_flow.0':[m.Sample(301,'ramp_accel_0',94,25),m.Sample(302,'main_down_0',5,25)]},'regional_stops':{'shared':{'R':[0]*2700,'U':[0]*2700}}}
        result=m.feeder_science_inputs(observations)
        self.assertEqual(result['r_counts'][0],1)


if __name__=='__main__':unittest.main()
