"""Tiny public data fixtures; no SUMO/bridge/fake-world loop."""
import unittest,copy
from audit_data_V2 import audit_rate_steps,audit_terminal

def row(t,ids=(),motion='G',n=None,e=0):
    steps=t-1199;C=steps/12
    return dict(time_begin_s=t,time_end_s=t+1,accounting_complete=True,motion=motion,
      phase_observation=dict(state_after=motion,phase_after={'G':0,'y':1,'r':2}[motion]),
      rate_chain=dict(input_origin='FIXED_POLICY_DIAGNOSTIC',r_ALINEA=None,r_final_veh_h=300,r_policy_pending_veh_h=300,r_policy_applied_veh_h=300,requested_quota=2,period_s=24),
      actual_crossings=[dict(vehicle_id=i) for i in ids],accounting=dict(C=C,C_mapped_pending=C,C_applied=C,E=e,N=len(ids) if n is None else n,policy_quantization=0,application_latency=0,C_applied_minus_E=C-e,E_minus_N=e-(len(ids) if n is None else n)))
def entry(t,vid,motion='G'):return dict(time_begin_s=t,time_end_s=t+1,vehicle_id=vid,motion=motion)

class Tests(unittest.TestCase):
 def test_empty_zero_partial_and_multiple_yellow_entries(self):
    self.assertTrue(all(v is None for v in audit_rate_steps([],[])['accounting'].values()))
    zero=audit_rate_steps([row(1200)],[]);self.assertEqual(zero['accounting']['N'],0);self.assertFalse(zero['complete_observation'])
    entries=[entry(1200,'R_flow.0'),entry(1200,'R_flow.1'),entry(1201,'R_flow.2','y')]
    rows=[row(1200,['R_flow.0','R_flow.1'],n=2)]
    for t in range(1201,1224):rows.append(row(t,['R_flow.2'] if t==1201 else [],'y' if t<1206 else 'r',n=3,e=2 if t==1223 else 0))
    a=audit_rate_steps(rows,entries);self.assertEqual(a['status'],'PASS_ACCOUNTING_ONLY');self.assertEqual((a['accounting']['E'],a['accounting']['N']),(2,3))
    bad=copy.deepcopy(rows);bad[0]['phase_observation']['phase_after']=True;self.assertEqual(audit_rate_steps(bad,entries)['status'],'UNKNOWN')
    self.assertEqual(audit_rate_steps(rows,entries+[entries[0]])['status'],'UNKNOWN')
    self.assertEqual(audit_rate_steps(rows,entries[:-1])['status'],'UNKNOWN')
 def test_terminal_pass_fail_unknown_rounding_and_legal_lane_change(self):
    b=dict(vehicle_id='M_flow.0',time_s=1200,time_begin_s=1200,time_end_s=1201,arrived_id_bound=True,type_id='technical_passenger',route=['main_down'],terminal_edge='main_down',speed_m_s=10.,acceleration_m_s2=0.,normal_decel_m_s2=4.5)
    tr=dict(id='M_flow.0',arrival='1200.00000000',arrivalSpeed='5.50000000',arrivalLane='main_down_1',vType='technical_passenger',vaporized='')
    lanes={'main_down':['main_down_0','main_down_1']}
    self.assertEqual(audit_terminal(b,[tr],lanes)['status'],'PASS')
    self.assertEqual(audit_terminal(b,[dict(tr,arrivalSpeed='5.40000000')],lanes)['status'],'FAIL')
    self.assertEqual(audit_terminal(b,[dict(tr,arrivalSpeed='5.49999900')],lanes)['status'],'UNKNOWN')
    self.assertEqual(audit_terminal(b,[dict(tr,arrival='1200.50000000')],lanes)['status'],'UNKNOWN')
    self.assertEqual(audit_terminal(b,[],lanes)['status'],'UNKNOWN');self.assertEqual(audit_terminal(b,[tr,tr],lanes)['status'],'UNKNOWN')
    self.assertEqual(audit_terminal(b,[dict(tr,arrivalLane='ramp_accel_0')],lanes)['status'],'UNKNOWN')
    self.assertEqual(audit_terminal(b,[dict(tr,vaporized='true')],lanes)['status'],'UNKNOWN')
if __name__=='__main__':unittest.main(verbosity=2)
