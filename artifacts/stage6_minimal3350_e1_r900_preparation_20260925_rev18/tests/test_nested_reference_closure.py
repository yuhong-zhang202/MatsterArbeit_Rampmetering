from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG/'r02_single_start'))
from e1_nested_reference_binding import build_and_validate_staged_inputs

RUN='MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY1'

class NestedReferenceClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.repo=Path(self.temp.name).resolve()
        self.package=self.repo/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev18'
        self.inputs=self.package/'inputs/treatment'
        self.inputs.mkdir(parents=True)
        (self.repo/'data/raw').mkdir(parents=True)
        self.output=self.repo/f'data/raw/stage6_minimal3350_ux0_20260925_v18/{RUN}/outputs'
        self.network=self.repo/'network.net.xml';self.network.write_text('<net/>')
        self.demand=self.inputs/'demand.rou.xml';self.demand.write_text('<routes/>')
        self.additional=self.inputs/'scenario.add.xml'
        self.roles=[]
        allout=[self.output/f'role{i}.xml' for i in range(18)]
        cfgout=allout[:6]+[self.output/'sumo.log',self.output/'sumo_error.log']
        addout=allout[6:]
        cfg=ET.Element('sumoConfiguration')
        inp=ET.SubElement(cfg,'input')
        for tag,path in [('net-file',self.network),('route-files',self.demand),('additional-files',self.additional)]:
            ET.SubElement(inp,tag,{'value':str(path.resolve())})
        op=ET.SubElement(cfg,'output')
        for tag,path in zip(('fcd-output','queue-output','summary-output','tripinfo-output','vehroute-output','lanechange-output','log','error-log'),cfgout):
            ET.SubElement(op,tag,{'value':str(path.resolve())})
        self.cfg=self.inputs/'scenario.sumocfg';self.cfg.write_bytes(ET.tostring(cfg,encoding='utf-8'))
        add=ET.Element('additional')
        for i,path in enumerate(addout):ET.SubElement(add,'inductionLoop',{'id':f'e1_{i}','lane':'lane0','pos':str(i),'period':'30','file':str(path.resolve())})
        self.additional.write_bytes(ET.tostring(add,encoding='utf-8'))
        for i,path in enumerate(allout):self.roles.append({'role':f'role{i}.xml','path':str(path.resolve()),'kind':'E1'})
        self.rolesfile=self.inputs/'output_roles.json';self.rolesfile.write_text(json.dumps({'required_role_count':18,'required_xml_roles':self.roles}))

    def tearDown(self):self.temp.cleanup()

    def run_check(self,**kw):
        args=dict(repo=self.repo,package_root=self.package,source_cfg=self.cfg,source_demand=self.demand,
                  source_additional=self.additional,network=self.network,output_directory=self.output,roles=self.roles)
        args.update(kw)
        return build_and_validate_staged_inputs(**args)

    def test_valid_closes_additional_reference_and_all_twenty_paths(self):
        cfg,add,receipt=self.run_check()
        root=ET.fromstring(cfg)
        self.assertEqual(root.find('.//additional-files').get('value'),str((self.output/'scenario_control.add.xml').resolve()))
        self.assertEqual(receipt['configured_unique_paths'],20)
        self.assertEqual(receipt['configured_role_records'],18)
        self.assertEqual(ET.fromstring(add).tag,'additional')
        self.assertFalse(self.output.exists())

    def test_validates_persisted_staged_bytes_not_only_a_recomputed_transform(self):
        cfg,add,_=self.run_check()
        cfg2,add2,receipt=self.run_check(actual_staged_cfg=cfg,actual_staged_additional=add)
        self.assertEqual(cfg2,cfg);self.assertEqual(add2,add)
        self.assertTrue(receipt['validated_actual_staged_bytes'])
        with self.assertRaisesRegex(ValueError,'PERSISTED_STAGED_SUMOCFG_NOT_DETERMINISTIC'):
            self.run_check(actual_staged_cfg=cfg.replace(b'additional-files',b'additional-filex'),actual_staged_additional=add)

    def test_reproduces_rev17_stale_additional_reference_while_new_add_targets_v18(self):
        text=self.cfg.read_text()
        current=str(self.additional.resolve())
        stale=str(self.repo/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev14/inputs/treatment/scenario.add.xml')
        self.cfg.write_text(text.replace(current,stale))
        with self.assertRaisesRegex(ValueError,'STALE_PACKAGE_REVISION|SUMOCFG_INPUT_REFERENCE_MISMATCH'):
            self.run_check()
        self.assertIn('rev14/inputs/treatment/scenario.add.xml',self.cfg.read_text())
        self.assertTrue(all('/stage6_minimal3350_ux0_20260925_v18/' in r['path'] for r in self.roles))

    def test_rejects_stale_v17_detector_target(self):
        root=ET.fromstring(self.additional.read_bytes())
        root[0].set('file',str(self.repo/'data/raw/stage6_minimal3350_ux0_20260925_v17/old.xml'))
        self.additional.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'STALE_REVISION_PATH|OUTPUT_ROLE_SET_MISMATCH|OUTSIDE_RUN_ROOT'):
            self.run_check()

    def test_rejects_extra_additional_file_reference(self):
        root=ET.fromstring(self.additional.read_bytes())
        ET.SubElement(root,'unknownDevice',{'file':str(self.output/'rogue.xml')})
        self.additional.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_ADDITIONAL_PATH_REFERENCE'):
            self.run_check()

    def test_rejects_extra_sumocfg_output_reference(self):
        root=ET.fromstring(self.cfg.read_bytes())
        ET.SubElement(root.find('output'),'extra-output',{'value':str(self.output/'rogue.xml')})
        self.cfg.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_CFG_OUTPUT_REFERENCE'):
            self.run_check()

    def test_rejects_relative_output_reference(self):
        root=ET.fromstring(self.additional.read_bytes());root[0].set('file','relative.xml')
        self.additional.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'ABSOLUTE_PATH_REQUIRED'):
            self.run_check()

    def test_rejects_output_outside_retry_root(self):
        outside=self.repo/'data/raw/outside.xml'
        self.roles[0]['path']=str(outside)
        root=ET.fromstring(self.additional.read_bytes());root[0].set('file',str(outside))
        self.additional.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'OUTPUT_ROLE_OUTSIDE_RUN_ROOT'):
            self.run_check()

    def test_rejects_uncreatable_raw_parent_without_creating_anything(self):
        raw=self.repo/'data/raw';raw.rmdir();raw.write_text('occupied by a file')
        with self.assertRaisesRegex(ValueError,'OUTPUT_PARENT_NOT_WRITABLE_DIRECTORY'):
            self.run_check()
        self.assertTrue(raw.is_file());self.assertFalse(self.output.exists())

    def test_rejects_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError,'STAGED_SUMOCFG_HASH_MISMATCH'):
            self.run_check(expected_cfg_sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'STAGED_ADDITIONAL_HASH_MISMATCH'):
            self.run_check(expected_additional_sha256='0'*64)

    def test_rejects_symlink_in_output_ancestor(self):
        real=self.repo/'data/raw/stage6_minimal3350_ux0_20260925_v18_real'
        real.mkdir()
        expected=self.repo/'data/raw/stage6_minimal3350_ux0_20260925_v18'
        expected.symlink_to(real,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'OUTPUT_DIRECTORY_NOT_EXACT_FRESH_V18_TARGET'):
            self.run_check()

    def test_rejects_path_traversal(self):
        root=ET.fromstring(self.additional.read_bytes())
        root[0].set('file',str(self.output/'..'/'escape.xml'))
        self.additional.write_bytes(ET.tostring(root,encoding='utf-8'))
        with self.assertRaisesRegex(ValueError,'PATH_TRAVERSAL|OUTPUT_ROLE_SET_MISMATCH|OUTSIDE_RUN_ROOT'):
            self.run_check()

if __name__=='__main__':unittest.main()
