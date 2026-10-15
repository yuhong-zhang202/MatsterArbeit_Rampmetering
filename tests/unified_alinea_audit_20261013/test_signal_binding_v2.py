import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.unified_alinea_audit_20261013_v1.signal_binding_v2 import validate,LINKS
class SignalBindingTests(unittest.TestCase):
    def test_same_clock_unbound_signal_does_not_support_application(self):
        expected={'phase':0,'state':'G','program':'I12_PACKET24','ACK_s':1201}
        row={'post_signal_application_binding':{'status':'BOUND_BEFORE_LEDGER','actual_phase':0,'actual_state':'G','actual_program':'I12_PACKET24','actual_controlled_links':LINKS,'ACK_s':1201,'expected_phase':0,'expected_state':'G','expected_program':'I12_PACKET24'}}
        self.assertEqual(validate(row,expected)['status'],'PASS_ACTUAL_SIGNAL_BINDING_ONLY')
        for field,value in [('actual_phase',2),('actual_state','r'),('actual_program','wrong'),('actual_controlled_links',[]),('ACK_s',1202)]:
            with self.subTest(field=field):
                bad=copy.deepcopy(row);bad['post_signal_application_binding'][field]=value
                with self.assertRaises(ValueError):validate(bad,expected)
if __name__=='__main__':unittest.main()
