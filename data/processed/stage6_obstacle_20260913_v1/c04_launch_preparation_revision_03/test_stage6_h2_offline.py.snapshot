"""Offline-only Stage 6 fixture tests. No simulator executable may be called."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from src.scenarios import stage6_h2_offline as o


class OfflineControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=o.BATCH, prefix="c02_fixture_")
        self.directory = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.block = patch("subprocess.Popen", side_effect=AssertionError("process launch forbidden in offline test"))
        self.block.start()
        self.addCleanup(self.block.stop)
        self.card = o.load_card()
        self.network = o.ROOT / "artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused/network.net.xml"

    def test_card_config_and_fixed_denominators(self):
        main, sensitivity = o.read_rule_keys(self.card)
        self.assertEqual((len(main), len(sensitivity)), (352, 14))
        self.assertEqual(sum(r['required_for_resolution'] == 'true' for r in main), 148)
        self.assertEqual(len(o.verify_candidate()['files']), 7)
        p = self.directory / 'card.json'
        p.write_text(json.dumps({**self.card, 'seed_set': [17, 24]}))
        with self.assertRaises(o.EvidenceError):
            o.load_card(p)
        with self.assertRaises(o.EvidenceError):
            o.registered_run(self.card, 'S6_V1_C_S24')

    def test_candidate_manifest_cannot_be_rebound(self):
        p = self.directory / 'candidate'
        p.mkdir()
        for source in o.CANDIDATE.iterdir():
            (p / source.name).write_bytes(source.read_bytes())
        entry = o.read_json(p / 'entry_contract.json')
        entry['M_departPos_m'] = 200
        (p / 'entry_contract.json').write_bytes(o.encode(entry))
        manifest = o.read_json(p / 'source_manifest.json')
        manifest['files']['entry_contract.json'] = o.sha256(p / 'entry_contract.json')
        (p / 'source_manifest.json').write_bytes(o.encode(manifest))
        with self.assertRaises(o.EvidenceError):
            o.verify_candidate(p)

    def test_deterministic_materialization_and_no_overwrite(self):
        dest = self.directory / 'attempt'
        run = 'S6_V1_ML_S17'
        manifest = o.prepare(o.CARD, self.network, o.sha256(self.network), run, run + '_attempt1', dest, self.directory)
        self.assertFalse(manifest['launch_eligible'])
        self.assertEqual(o.verify_materialization(dest / 'materialization_manifest.json', self.directory)['status'], 'offline_materialization_verified')
        flow = {x.get('id'): x.attrib for x in ET.parse(dest / 'demand.rou.xml').getroot().findall('flow')}
        self.assertEqual([flow[g + '_flow']['number'] for g in 'MRUX'], ['1083','300','150','75'])
        self.assertEqual(flow['M_flow']['departPos'], '100')
        self.assertEqual(flow['U_flow']['departPos'], 'last')
        config = ET.parse(dest / 'scenario.sumocfg').getroot()
        self.assertEqual(config.find('processing/extrapolate-departpos').get('value'), 'false')
        self.assertEqual(config.find('time/end').get('value'), '2700')
        original = (dest / 'materialization_manifest.json').read_bytes()
        with self.assertRaises(o.EvidenceError):
            o.prepare(o.CARD, self.network, o.sha256(self.network), run, run + '_attempt1', dest, self.directory)
        self.assertEqual((dest / 'materialization_manifest.json').read_bytes(), original)
        (dest / 'demand.rou.xml').write_text('drift')
        with self.assertRaises(o.EvidenceError):
            o.verify_materialization(dest / 'materialization_manifest.json', self.directory)

    def test_bad_network_symlink_and_reused_run_rejected_before_write(self):
        with self.assertRaises(o.EvidenceError):
            o.verify_network(self.network, '0' * 64)
        link = self.directory / 'link'
        link.symlink_to(o.CANDIDATE, target_is_directory=True)
        with self.assertRaises(o.EvidenceError):
            o.checked_path(link / 'entry_contract.json', self.directory)
        with self.assertRaises(o.EvidenceError):
            o.prepare(o.CARD, self.network, o.sha256(self.network), 'S6_V0_ML_S17', 'S6_V0_ML_S17_attempt1', self.directory/'bad', self.directory)
        self.assertFalse((self.directory/'bad').exists())

    def reserve(self, state, aid, run='S6_V1_ML_S17', role='validation', **extra):
        return o.budget_event(state, self.card, {'event':'reserve','attempt_id':aid,'run_id':run,'role':role,'parameter_hash':'a'*64,**extra})

    def test_reserved_unknown_block_relaunch_and_cancel_denominator(self):
        s = self.reserve(o.new_budget(self.card), 'a')
        self.assertEqual(o.budget_usage(s)['sumo'], 1)
        s = o.budget_event(s,self.card,{'event':'mark_unknown','attempt_id':'a'})
        with self.assertRaises(o.EvidenceError): self.reserve(s,'b')
        with self.assertRaises(o.EvidenceError): o.budget_event(s,self.card,{'event':'release','attempt_id':'a'})
        proof=self.directory/'no_start.json';proof.write_bytes(o.encode({'attempt_id':'a','simulator_start_observed':False,'process_absent':True}))
        s = o.budget_event(s,self.card,{'event':'release','attempt_id':'a','verified_no_start':True,'evidence_binding':o.bind(proof)})
        self.assertEqual(o.budget_usage(s)['sumo'], 0)
        s = o.budget_event(s,self.card,{'event':'cancel','run_id':'S6_V1_ML_S17'})
        self.assertEqual(len(self.card['logical_runs']),8)
        with self.assertRaises(o.EvidenceError): self.reserve(s,'b')

    def test_one_retry_shared_across_smoke_and_validation(self):
        s = self.reserve(o.new_budget(self.card), 'smoke', role='smoke')
        s = o.budget_event(s,self.card,{'event':'mark_running','attempt_id':'smoke'})
        s = o.budget_event(s,self.card,{'event':'technical_fail','attempt_id':'smoke','wallclock_s':1,'archive_bytes':10})
        with self.assertRaises(o.EvidenceError): self.reserve(s,'r',role='retry',parent_attempt_id='smoke',parameter_hash='b'*64)
        s = self.reserve(s,'r',role='retry',parent_attempt_id='smoke')
        s = o.budget_event(s,self.card,{'event':'mark_running','attempt_id':'r'})
        s = o.budget_event(s,self.card,{'event':'technical_fail','attempt_id':'r','wallclock_s':1,'archive_bytes':10})
        with self.assertRaises(o.EvidenceError): self.reserve(s,'r2',role='retry',parent_attempt_id='r')
        self.assertEqual(o.budget_usage(s)['retry'],1)

    def test_budget_revision_is_exclusive_and_no_json_nonfinite(self):
        s = o.new_budget(self.card)
        p = o.save_budget_revision(s,self.directory)
        with self.assertRaises(FileExistsError):o.save_budget_revision(s,self.directory)
        self.assertEqual(o.read_json(p),s)
        with self.assertRaises(ValueError):o.encode({'x':float('inf')})
        p = self.directory/'bad.json';p.write_text('{"x":1,"x":2}')
        with self.assertRaises(o.EvidenceError):o.read_json(p)

    def test_budget_overrun_is_retained_and_stops_new_reservation(self):
        s=self.reserve(o.new_budget(self.card),'a')
        s=o.budget_event(s,self.card,{'event':'mark_running','attempt_id':'a'})
        s=o.budget_event(s,self.card,{'event':'technical_fail','attempt_id':'a','wallclock_s':121,'archive_bytes':2_000_000_001})
        self.assertEqual(o.budget_usage(s)['wallclock_s'],121)
        self.assertEqual(len(s['stop_violations']),2)
        self.assertEqual(o.watchdog_action(121,0,self.card)['action'],'stop_and_record_technical_failure')
        with self.assertRaises(o.EvidenceError):self.reserve(s,'retry',role='retry',parent_attempt_id='a')

    def test_offline_cli_has_no_launch_or_build(self):
        self.assertEqual(o.main(['validate-offline']),0)
        with self.assertRaises(SystemExit):o.main(['run'])


if __name__ == '__main__': unittest.main()
