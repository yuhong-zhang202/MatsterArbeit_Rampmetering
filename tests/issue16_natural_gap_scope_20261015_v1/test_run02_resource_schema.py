"""Only the two fixed resource identities; no prepare/native/budget write."""
import json,unittest
from pathlib import Path
from copy import deepcopy
from scripts.natural_actuator_qualification_20261015_v1 import provenance
from src.candidate_a_natural_service_20261015 import profile
ROOT=Path(__file__).resolve().parents[2]
class ResourceSchemaTests(unittest.TestCase):
 def test_exact_two_identities_and_rejections(self):
  old=json.loads((ROOT/'artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1/QUAL_NATURAL_ALINEA_R900_S17_01/card.json').read_text());self.assertEqual(provenance.resource_card(old,ROOT)['outer_wall_limit_s'],900)
  spent=83.63743604102638
  scope=dict(scope_id='NATURAL_QUALIFICATION_20261015_V1',approved_total_monitored_s=900,charged_before_preparation_s=spent,remaining_before_preparation_s=900-spent,start_count_before_preparation=1,unknown_reserved_before_preparation=[],budget_approval_sha256=provenance.sha(ROOT/'artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json'),old_scope_available_not_pooled=True,current_identity_ordinal=2,max_new_identities=2,further_identity_prepared=False)
  c=dict(spec=profile.spec(ROOT),resources=profile.resources(),guardian=profile.guardian_spec(),resources_scope=scope,resources_status='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL',qualification_proposal=profile.qualification_proposal())
  b=dict(known_settled={'QUAL_NATURAL_ALINEA_R900_S17_01':spent},charged_monitored_s=spent,remaining_s=900-spent,start_count=1)
  self.assertEqual(provenance.resource_card(c,ROOT,b)['inner_wall_limit_s'],786);provenance.guardian_receipt_limits(c['guardian'],c['guardian'])
  cases=[]
  for path,value in [(('spec','run_id'),'UNKNOWN'),(('resources','wall_limit_s'),815),(('guardian','inner_wall_limit_s'),870),(('guardian','receipt'),old['guardian']['receipt']),(('resources_scope','charged_before_preparation_s'),0),(('qualification_proposal','alinea_numeric_tracking_accuracy'),'PASS')]:
   bad=deepcopy(c);bad[path[0]][path[1]]=value;cases.append(bad)
  for bad in cases:
   with self.assertRaises(ValueError):provenance.resource_card(bad,ROOT,b)
  bad=deepcopy(b);bad['start_count']=0
  with self.assertRaises(ValueError):provenance.resource_card(c,ROOT,bad)
  with self.assertRaises(ValueError):provenance.guardian_receipt_limits(old['guardian'],c['guardian'])
if __name__=='__main__':unittest.main(verbosity=2)
