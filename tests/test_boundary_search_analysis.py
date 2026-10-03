import importlib.util
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).parents[1]/'scripts/stage6/boundary_search_20261002/analyze.py'
spec=importlib.util.spec_from_file_location('boundary_analysis',P);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.cfg={**a.DEFAULTS,'horizon':3,'bin_seconds':3,'evaluation_start':0,'evaluation_end':3}
    def tearDown(self):self.tmp.cleanup()
    def fcd(self,steps):
        p=self.root/'fcd.xml';p.write_text('<fcd-export>'+''.join(f'<timestep time="{t}">{s}</timestep>' for t,s in steps)+'</fcd-export>');return p
    def v(self,id='M_flow.0',speed=10,lane='main_up_0',x=350):return f'<vehicle id="{id}" speed="{speed}" lane="{lane}" x="{x}"/>'
    def test_missing_second(self):
        with self.assertRaisesRegex(ValueError,'timestep'):a.fcd_scan(self.fcd([(0,''),(2,'')]),self.cfg)
    def test_duplicate_vehicle(self):
        with self.assertRaisesRegex(ValueError,'duplicate vehicle'):a.fcd_scan(self.fcd([(0,self.v()*2),(1,''),(2,'')]),self.cfg)
    def test_vehicle_gap(self):
        with self.assertRaisesRegex(ValueError,'interior FCD gap'):a.fcd_scan(self.fcd([(0,self.v()),(1,''),(2,self.v())]),self.cfg)
    def test_incomplete_tail(self):
        with self.assertRaisesRegex(ValueError,'incomplete FCD'):a.fcd_scan(self.fcd([(0,''),(1,'')]),self.cfg)
    def test_denominators(self):
        z=a.fcd_scan(self.fcd([(0,self.v(speed=10)+self.v('M_flow.1',20)),(1,self.v(speed=30)),(2,'')]),self.cfg)
        r=next(r for r in z['cells'] if r['cell']==3)
        self.assertEqual(r['speed_mps'],20);self.assertEqual(r['slow_fraction'],1/3)
        self.assertEqual(r['mean_M_count'],1);self.assertEqual(r['density_veh_per_km_lane'],5)
    def test_normalized_reference_and_simultaneous_group(self):
        d={'M_flow.0':{'speedFactor':.5},'M_flow.1':{'speedFactor':1}}
        rows=[(0,self.v(speed=10)+self.v('M_flow.1',20)),(1,self.v(speed=10)),(2,'')]
        z=a.fcd_scan(self.fcd(rows),self.cfg,d,{'main_up_0':40})
        r=next(r for r in z['cells'] if r['cell']==3 and r['lane_track']=='pooled')
        self.assertEqual(r['model_reference_ratio'],.5);self.assertEqual(r['slow_fraction_0p6'],1)
        self.assertEqual(r['simultaneous_ge2_slow_seconds_0p6'],1)
    def test_total_density_includes_r_but_speed_is_m_only(self):
        rows=[(0,self.v(speed=10)+self.v('R_flow.0',20)),(1,''),(2,'')]
        z=a.fcd_scan(self.fcd(rows),self.cfg)
        r=next(r for r in z['cells'] if r['cell']==3 and r['lane_track']=='pooled')
        self.assertEqual(r['speed_mps'],10)
        self.assertEqual(r['total_MR_density_veh_per_km_lane'],2*r['density_veh_per_km_lane'])
    def test_missing_speedfactor_rejected(self):
        p=self.root/'demand.xml';p.write_text('<routes><vehicle id="M_flow.0" depart="0"/></routes>')
        with self.assertRaises(KeyError):a.demand_rows(p)
    def test_internal_mainline_lane(self):
        z=a.fcd_scan(self.fcd([(0,self.v(speed=0,lane=':freeway_merge_0_0',x=1399)),(1,''),(2,'')]),self.cfg)
        r=next(r for r in z['cells'] if r['cell']==13 and r['lane_track']=='0')
        self.assertEqual(r['samples'],1);self.assertEqual(r['speed_mps'],0)
    def test_unexpected_lane_gate(self):
        z=a.fcd_scan(self.fcd([(0,self.v(lane='merge_section_0',x=1450)),(1,''),(2,'')]),self.cfg)
        self.assertEqual(a.measurement_gate({'status':'FREE_FLOW_CANDIDATE'},z['invalid_m'])['status'],'MEASUREMENT_INCOMPLETE')
    def test_departure_boundary(self):
        cfg={**a.DEFAULTS,'horizon':60}
        d={'M_flow.0':dict(class_='M',scheduled=29)};d['M_flow.0']['class']='M'
        trips={'M_flow.0':dict(depart=30,arrival=-1,departDelay=1,duration=30,timeLoss=0,waitingTime=0)}
        f={'ids':{'M_flow.0':dict(first=30,last=59,n=30)},'events':{}}
        rows,_,cumulative,_=a.lifecycle(d,trips,f,cfg)
        self.assertEqual(next(r for r in cumulative if r['time']==30 and r['vehicle_class']=='M')['source_backlog'],1)
        events=a.event_bins(rows,cfg)
        self.assertEqual(next(r for r in events if r['begin']==30 and r['vehicle_class']=='M')['depart_count'],1)
    def test_half_open(self):
        self.assertTrue(a.in_window(1200,1200,3000));self.assertFalse(a.in_window(3000,1200,3000))
    def test_edge_and_change_separate(self):
        z=a.fcd_scan(self.fcd([(0,self.v('R_flow.0',20,'merge_section_0')),(1,self.v('R_flow.0',20,'merge_section_1')),(2,'')]),self.cfg)
        self.assertEqual(z['events']['R_flow.0']['merge_edge'],0);self.assertEqual(z['events']['R_flow.0']['mainline_observed'],1)
        p=self.root/'lc.xml';p.write_text('<lanechanges><change id="R_flow.0" time="0.8" from="merge_section_0" to="merge_section_1" pos="40"/></lanechanges>')
        self.assertEqual(a.lanechanges(p)['R_flow.0'][0]['time'],0.8)
    def test_lifecycle_censoring(self):
        d={'M_flow.0':{'class':'M','scheduled':0},'R_flow.0':{'class':'R','scheduled':1}}
        trips={'M_flow.0':dict(depart=1,arrival=-1,departDelay=1,duration=2,timeLoss=0,waitingTime=0)}
        f={'ids':{'M_flow.0':dict(first=1,last=2,n=2)},'events':{}}
        rows,classes,times,_=a.lifecycle(d,trips,f,self.cfg)
        self.assertEqual(rows[0]['scheduled_system_time_observed_s'],3)
        self.assertEqual(rows[1]['status'],'undeparted');self.assertEqual(rows[1]['external_wait_observed_s'],2)
        self.assertEqual(next(x for x in times if x['time']==3 and x['vehicle_class']=='R')['source_backlog'],1)
    def test_disabled_classifier(self):self.assertEqual(a.classify([],self.cfg)['status'],'NOT_CLASSIFIED')

class ClassifierTest(unittest.TestCase):
    def cfg(self):return {**a.DEFAULTS,'classifier':{'version':'exploratory_normalized_v1','review_reference':'synthetic-test'}}
    def cells(self):
        return [dict(cell=c,begin=t,lane_track='pooled',population_valid=True,model_reference_ratio=1.,density_veh_per_km_lane=10.,**{'slow_fraction_'+str(x).replace('.','p'):0. for x in [.6,.7,.8]},**{'simultaneous_ge2_slow_seconds_'+str(x).replace('.','p'):0 for x in [.6,.7,.8]}) for c in range(22) for t in range(0,4200,30)]
    def low(self,rows,cs,start,end,ratio=.65,density=10):
        for r in rows:
            if r['cell'] in cs and start<=r['begin']<end:
                r['model_reference_ratio']=ratio;r['density_veh_per_km_lane']=density
                for x in [.6,.7,.8]:
                    r['slow_fraction_'+str(x).replace('.','p')]=1 if ratio<=x else 0
                    r['simultaneous_ge2_slow_seconds_'+str(x).replace('.','p')]=30 if ratio<=x else 0
    def test_free(self):self.assertEqual(a.classify(self.cells(),self.cfg())['status'],'FREE_FLOW_CANDIDATE')
    def test_same_pair_and_union(self):
        r=self.cells();self.low(r,[13,14,15],1500,1590)
        z=a.classify(r,self.cfg());self.assertEqual(z['status'],'SUSTAINED_CONGESTION_CANDIDATE')
        self.assertEqual(z['windows']['evaluation']['P']['supported_time_union_seconds'],90)
    def test_changing_pairs_not_persistent(self):
        r=self.cells();self.low(r,[12,13],1500,1530);self.low(r,[13,14],1530,1560);self.low(r,[14,15],1560,1590)
        z=a.classify(r,self.cfg());self.assertFalse(z['windows']['evaluation']['P']['episodes'])
    def test_density_support_and_bad_baseline(self):
        r=self.cells();self.low(r,[13],1500,1590,density=13)
        self.assertTrue(a.classify(r,self.cfg())['windows']['evaluation']['P']['episodes'])
        self.low(r,[13],300,330,ratio=.8,density=10)
        self.assertFalse(a.classify(r,self.cfg())['windows']['evaluation']['P']['episodes'])
    def test_state_does_not_require_onset(self):
        r=self.cells();self.low(r,[13,14],1200,1500)
        for row in r:
            if row['cell'] in [13,14] and 1110<=row['begin']<1200:row['model_reference_ratio']=.8
        z=a.classify(r,self.cfg());self.assertEqual(z['status'],'SUSTAINED_CONGESTION_CANDIDATE')
        self.assertEqual(z['windows']['evaluation']['P']['episodes'][0]['onset'],'ONSET_UNRESOLVED')
    def test_crossing_window_retains_episode_and_global_onset(self):
        r=self.cells();self.low(r,[13,14],1140,1230)
        z=a.classify(r,self.cfg());eps=z['windows']['evaluation']['P']['episodes']
        self.assertEqual(eps[0]['begin'],1140);self.assertEqual(eps[0]['report_begin'],1200)
        self.assertEqual(eps[0]['onset'],'ONSET_SUPPORTED')
        self.assertEqual(z['windows']['evaluation']['P']['supported_time_union_seconds'],30)
    def test_missing_population_not_free(self):
        r=self.cells();next(x for x in r if x['cell']==13 and x['begin']==1500)['population_valid']=False
        self.assertEqual(a.classify(r,self.cfg())['status'],'MEASUREMENT_INCOMPLETE')

if __name__=='__main__':unittest.main()
