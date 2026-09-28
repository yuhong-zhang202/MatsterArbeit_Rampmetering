import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

import analyze_sigma0 as s
from review_sigma0_r0 import lifecycle


class Sigma0GateTests(unittest.TestCase):
    def test_negative_control_all_fixed_seconds_and_upstream_counts(self):
        r0={('M_flow.1',594):('main_down_0',1715.55,11,26.69),
            ('M_flow.2',599):('main_up_0',800.0,800,28.0),
            ('M_flow.3',599):('main_up_0',1200.0,1200,27.0)}
        a={('M_flow.1',594):('main_down_0',1715.37,11,26.51),
           ('M_flow.2',599):('main_up_0',800.1,800.1,27.9),
           ('M_flow.3',599):('main_up_0',1200.0,1200,27.0)}
        r={594:[('R_flow.0',1481.58,'merge_section_1')]}
        rows=s.negative_control(r0,a,r)
        self.assertEqual(len(rows),14)
        self.assertEqual(rows[2]['different_M_ahead_of_all_R'],1)
        self.assertEqual(rows[7]['different_M_x_below_1000m'],1)
        self.assertEqual(rows[7]['different_M_x_below_1400m'],1)
        self.assertEqual(rows[7]['different_ids'],['M_flow.2'])

    def test_pre_fcd_fails_on_missing_second(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fcd.xml'
            p.write_text('<fcd-export><timestep time="0"><vehicle id="M_flow.0" lane="main_up_0" x="100" y="0" pos="100" speed="20"/></timestep><timestep time="2"/></fcd-export>')
            with patch.object(s,'HORIZON',3):
                with self.assertRaisesRegex(s.GateFailure,'missing/repeated'):
                    s.pre_and_r_fcd(p,False)

    def test_r_exposure_counts_first_any_merge_section_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fcd.xml'
            p.write_text('<fcd-export>'
                         '<timestep time="0"><vehicle id="R_flow.0" lane=":freeway_merge_2_0" x="1399"/></timestep>'
                         '<timestep time="1"><vehicle id="R_flow.0" lane="merge_section_0" x="1420"/><vehicle id="R_flow.1" lane="merge_section_2" x="1422"/></timestep>'
                         '<timestep time="2"><vehicle id="R_flow.0" lane="merge_section_1" x="1440"/></timestep>'
                         '</fcd-export>')
            with patch.object(s,'HORIZON',3):
                pre,r=s.pre_and_r_fcd(p,True)
            self.assertEqual(pre,{})
            self.assertEqual(r,{'R_flow.0':1,'R_flow.1':1})

    def test_fcd_vehicle_uses_its_parent_timestep(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fcd.xml'
            p.write_text('<fcd-export><timestep time="0"/><timestep time="1"/>'
                         '<timestep time="2"><vehicle id="R_flow.0" lane="urban_in_0" x="1001" speed="12" pos="1"/></timestep>'
                         '<timestep time="3"><vehicle id="R_flow.0" lane=":freeway_merge_2_0" x="1399" speed="24" pos="1"/></timestep>'
                         '<timestep time="4"><vehicle id="R_flow.0" lane="merge_section_0" x="1420" speed="25" pos="20"/></timestep>'
                         '</fcd-export>')
            with patch.object(s,'HORIZON',5):
                m,r=s.load_full_m(p)
                _,through=s.pre_and_r_fcd(p,True)
            self.assertEqual(m,{})
            self.assertNotIn(1,r)
            self.assertEqual([x[0] for x in r[2]],['R_flow.0'])
            self.assertEqual(through,{'R_flow.0':4})

    def test_manifest_hash_mismatch_is_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'R0').mkdir();(p/'R0'/'demand.rou.xml').write_text('mutated')
            (p/'INPUT_MANIFEST.json').write_text('{"files":{"R0/demand.rou.xml":"bad"}}')
            with self.assertRaisesRegex(s.GateFailure,'hash mismatch'):
                s.verify_manifest(p)

    def test_card_raw_root_uses_arm_not_run_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pkg=root/'inputs';arm='R0_SIGMA0';(pkg/arm).mkdir(parents=True)
            data={}
            for key,name in (('demand','demand.rou.xml'),('additional','scenario.add.xml'),('sumocfg','scenario.sumocfg')):
                f=pkg/arm/name;f.write_text(name);data[key]=s.digest(f)
            card={'arm':arm,'package_manifest_sha256':'a'*64,'package_dir':str(pkg),
                  'raw_root':str(root/'raw'),'run_id':'a_distinct_run_id',
                  'input_sha256':data,'network_sha256':'b'*64,'sumo_sha256':'c'*64}
            cp=root/'card.json';cp.write_text(json.dumps(card))
            raw=root/'raw'/arm/'outputs'
            _,sha=s.verify_card(cp,pkg,arm,'a'*64,raw)
            self.assertEqual(sha,s.digest(cp))
            with self.assertRaisesRegex(s.GateFailure,'raw binding mismatch'):
                s.verify_card(cp,pkg,arm,'a'*64,root/'raw'/'a_distinct_run_id'/'outputs')

    def test_demand_requires_requested_semantics_and_unique_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'demand.xml'
            p.write_text('<routes><vType id="technical_passenger"/><route id="M_route" edges="main_up merge_section main_down"/><vehicle id="M_flow.0" type="technical_passenger" route="M_route" depart="0" departPos="100" departLane="best" departSpeed="max" speedFactor="1"/><vehicle id="M_flow.0" type="technical_passenger" route="M_route" depart="1" departPos="100" departLane="best" departSpeed="max" speedFactor="1"/></routes>')
            with self.assertRaisesRegex(s.GateFailure,'Missing/duplicate'):
                s.demand(p)

    def test_r0_lifecycle_boundary_and_delay(self):
        requested={'M_flow.1':{'depart':'539.148'},'U_flow.1':{'depart':'100'}}
        trips={'M_flow.1':{'depart':'540','departDelay':'0.852'},
               'U_flow.1':{'depart':'100','departDelay':'0'}}
        veh={'M_flow.1':{'depart':'540','arrival':'600'},
             'U_flow.1':{'depart':'100','arrival':'120'}}
        by_class={r['class']:r for r in lifecycle(requested,trips,veh)}
        self.assertEqual(by_class['M']['desired_depart_before_540'],1)
        self.assertEqual(by_class['M']['actual_depart_before_540'],0)
        self.assertEqual(by_class['M']['departDelay_mean_s'],0.852)
        self.assertEqual(by_class['U']['arrived'],1)
        self.assertEqual(by_class['R']['planned'],0)


if __name__=='__main__':unittest.main()
