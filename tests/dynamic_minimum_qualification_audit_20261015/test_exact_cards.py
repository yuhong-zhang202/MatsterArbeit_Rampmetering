"""Only approved prepared-card classification compatibility; no native launch."""
import copy,json,pathlib,unittest
from scripts.dynamic_minimum_qualification_audit_20261015_v1.scope import check_card_scope
ROOT=pathlib.Path(__file__).resolve().parents[2]
class ExactCards(unittest.TestCase):
 def test_actual_prepared_cards_and_foreign_classification(self):
  base=ROOT/'artifacts/dynamic_minimum_qualification_20261015_v1/engineering/packages_v1'
  for run,mode in [('UA_NATIVEGAP_DYNAMIC_S17_01','dynamic_commands'),('UA_NATIVEGAP_ALINEA_S17_01','real_alinea')]:
   c=json.loads((base/run/'card.json').read_text());self.assertEqual(check_card_scope(c),mode)
   bad=copy.deepcopy(c);bad['classification']='UNAPPROVED'
   with self.assertRaises(ValueError):check_card_scope(bad)
if __name__=='__main__':unittest.main()
