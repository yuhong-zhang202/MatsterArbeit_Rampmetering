"""Two bounded offline configuration checks; no native execution."""
from pathlib import Path
import hashlib,json,tempfile,unittest
import xml.etree.ElementTree as ET
from src.candidate_a_native_wait_budget_series_20261012 import profile,bridge
ROOT=profile.ROOT
DONOR=ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2'

def physical_xml(path):
    root=ET.parse(path).getroot()
    for node in root.iter():
        if node.tag in ('net-file','route-files','additional-files'):
            node.set('value','PATH_METADATA:'+node.tag)
        if node.tag in ('output','report'):
            for child in node:
                if child.get('value','').startswith('/'):
                    child.set('value','PATH_METADATA:'+child.tag)
        for attr in ('file','dest'):
            if attr in node.attrib:node.set(attr,'PATH_METADATA:'+attr)
    def bound(n):
        return [n.tag,sorted(n.attrib.items()),(n.text or '').strip(),[bound(c) for c in n]]
    return bound(root)

class ConfigurationChecks(unittest.TestCase):
    def test_exact_common_core_cards_and_physical_inputs(self):
        frozen=json.loads((ROOT/'artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/INPUT_BINDINGS_V2.json').read_text())['files']
        for name,h in frozen.items():self.assertEqual(profile.sha(ROOT/name),h,name)
        old=(ROOT/'src/candidate_a_native_receiver_wait_20261012/bridge.py').read_text()
        new=(ROOT/'src/candidate_a_native_wait_budget_series_20261012/bridge.py').read_text()
        self.assertEqual(new.replace('src.candidate_a_native_wait_budget_series_20261012.profile','src.candidate_a_native_receiver_wait_20261012.profile'),old)
        donor=json.loads((DONOR/'card.json').read_text())
        for run,budget in profile.RUNS.items():
            card=profile.prepare(run);c=profile.validate(card,require_environment=True)
            self.assertEqual(c['resources'],{**donor['resources'],'wall_limit_s':budget})
            self.assertEqual({k:v for k,v in c['spec'].items() if k!='run_id'},{k:v for k,v in donor['spec'].items() if k!='run_id'})
            package=card.parent
            self.assertEqual(profile.sha(package/'demand.rou.xml'),profile.sha(DONOR/'demand.rou.xml'))
            self.assertEqual(physical_xml(package/'scenario.sumocfg'),physical_xml(DONOR/'scenario.sumocfg'))
            self.assertEqual(physical_xml(package/'scenario.add.xml'),physical_xml(DONOR/'scenario.add.xml'))
            self.assertFalse((ROOT/profile.output(run)).parent.exists())

    def test_invalid_identity_and_unreleased_execution_reject_without_allocation(self):
        for bad in (None,True,360,'360','CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W300_01'):
            with self.assertRaises(ValueError):profile.resources(bad)
        for run in profile.RUNS:
            card=profile.prepare(run)
            expected=ROOT/profile.TASK/'engineering/releases'/run/'EXECUTION_RELEASE.json'
            self.assertFalse(expected.exists())
            self.assertFalse((ROOT/profile.TASK/'authorization'/run/'AUTHORIZATION_NATIVE_EXECUTION.json').exists())
            with self.assertRaisesRegex(ValueError,'exact technical series authorization missing'):
                bridge.execute(card,expected)
            self.assertFalse((ROOT/profile.output(run)).parent.exists())

if __name__=='__main__':unittest.main(verbosity=2)
