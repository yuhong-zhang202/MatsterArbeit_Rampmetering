"""Execute exactly the user-released D1 smoke; no retry or validation loop."""
from pathlib import Path
import json
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
out=Path(__file__).resolve().parent
card=x.validate_launch_card(out/'approved_launch_card.json',require_approval=True)
assert card['attempts'][0]['attempt_id']=='S6_V1_ML_S17_attempt1'
journal=x.Journal(Path(card['budget_journal_directory']))
assert journal.counters()['sumo']==0
receipt=x.execute_attempt(out/'approved_launch_card.json','S6_V1_ML_S17_attempt1',journal,x.RealProcessAdapter(enable=True))
print(json.dumps({'execution_status':receipt['execution_status'],'reason':receipt['reason'],'exit_code':receipt['exit_code'],'budget_counters':receipt['budget_counters'],'required_xml_validation':receipt['required_xml_validation'],'receipt':o.bind(Path(receipt['materialization']['path']).parent/'execution_receipt.json')},indent=2))
