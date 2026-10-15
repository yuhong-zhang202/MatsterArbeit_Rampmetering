"""Minimal STOP-wrapper and gap classification schema tests; no runtime import."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.unified_alinea_audit_20261013_v1.actual import flatten,following,STREAMS
class ReaderTests(unittest.TestCase):
    def test_retained_prefix_and_bound_known_refusal(self):
        q=[{'time_begin_s':0},{'time_s':1,'retained_receipts':[{'time_begin_s':1,'accounting_complete':False}]}]
        self.assertEqual(len(flatten(q)),2)
        with self.assertRaises(ValueError):flatten(q+[q[-1]])
        world={'R_flow.1':{'speed_m_s':7.,'lane_id':'ramp_storage_0'},'R_flow.0':{'speed_m_s':8.,'lane_id':':ramp_mid_0_0'}}
        x={'vehicle_id':'R_flow.1','time_s':1206,'speed_mode':31,'lane_change_mode':1621,'actual_speed_m_s':7.,'lane_id':'ramp_storage_0','route':['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'],'lookahead_m':478.67,'future_safety_proven':False,'margin_m':1.1,'status':'STOP_CURRENT_GAP_BOUND_DENIED','fresh_getLeader_result':['R_flow.0',9.63],'leader_id':'R_flow.0','getSecureGap_args':{'vehID':'R_flow.1','speed':7.,'leaderSpeed':8.,'leaderMaxDecel':9.,'leaderID':'R_flow.0'},'actual_secure_gap_m':9.62,'gap_excluding_minGap_m':9.63,'min_gap_m':2.5,'leader_speed_m_s':8.,'leader_lane_id':':ramp_mid_0_0','physical_bumper_gap_m':12.13,'required_with_margin_m':10.72}
        alarms=[];following(x,'R_flow.1',1206,world,{},alarms);self.assertEqual(len(alarms),1);self.assertFalse(alarms[0]['native_unsafe_proven'])
        x['time_s']=1205
        with self.assertRaises(ValueError):following(x,'R_flow.1',1206,world,{},alarms)
        self.assertEqual(len(STREAMS),4)
if __name__=='__main__':unittest.main()
