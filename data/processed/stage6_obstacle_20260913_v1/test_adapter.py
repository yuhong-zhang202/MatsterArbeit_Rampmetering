"""Offline fixtures for the fixed archive adapter; never launches simulators."""
import unittest, ast, tempfile, json
from unittest.mock import patch
from pathlib import Path
import analyze_archives as a

class Tests(unittest.TestCase):
    def test_G01_hash_identity(self):
        import hashlib
        with tempfile.TemporaryDirectory(dir=a.BASE) as d:
            root=Path(d);raw=root/'fcd.xml';raw.write_bytes(b'abc')
            sm=root/'map.json';sm.write_text(json.dumps({'archive_status':'complete','source_runtime_path':'/original','file_map':[{'archive_relative_path':'fcd.xml','original_absolute_path':'/original/fcd.xml','sha256':hashlib.sha256(b'abc').hexdigest()}]}))
            row={'run_id':'fixture','source_map_path':'map.json','source_map_sha256':hashlib.sha256(sm.read_bytes()).hexdigest()}
            with patch.object(a,'ROOT',root):
                self.assertEqual(len(a.source_files(row)[0]),1)
                raw.write_bytes(b'abd')
                with self.assertRaisesRegex(ValueError,'raw hash'):a.source_files(row)
                row['source_map_sha256']='0'*64
                with self.assertRaisesRegex(ValueError,'source map hash'):a.source_files(row)
    def test_G02_no_unregistered_execution_interface(self):
        tree=ast.parse(Path(a.__file__).read_text())
        imports={n.names[0].name for n in ast.walk(tree) if isinstance(n,ast.Import)}
        self.assertTrue(imports.isdisjoint({'subprocess','traci','sumolib','socket','requests'}))
        self.assertEqual(len(a.RUNS),len(set(a.RUNS)))
        self.assertNotIn('QM3350S17',a.RUNS)
    def test_G03_identity_and_lane(self):
        for vid,lane,seen in [('R.0','known',set()),('M.0','bad',set()),('M.0','known',{'M.0'})]:
            with self.assertRaises(ValueError):a.safe_identity(vid,lane,seen,{'M.0':{}},{'known':{}},1)
    def test_G04_missing_nonfinite_negative_speed_and_grid(self):
        for v in [None,'nan','inf',-1]:
            with self.assertRaises(ValueError):a.safe_identity('M.0','a',set(),{'M.0':{}},{'a':{}},v)
        for grid in [[0,1],[0,1,3],[0,1,1],[0,1,2,3]]:
            with self.assertRaises(ValueError):a.time_grid(grid,3)
        a.time_grid([0,1,2],3)
    def test_G05_same_length_wrong_TLS_grid(self):
        with self.assertRaises(ValueError):a.time_grid([0,1,3],3)
        a.time_grid([0,1,2],3)
    def test_G06_E1_invalid_and_zero(self):
        for n,ne,v in [(1,1,-1),(-1,1,2),(1,-1,2),(1,1,'nan'),(1,1,None)]:
            with self.assertRaises(ValueError):a.e1_values([{'nVehContrib':n,'nVehEntered':ne,'speed':v}],30)
        self.assertEqual(a.e1_values([{'nVehContrib':0,'nVehEntered':0,'speed':-1}],30),(0,0,None,0,0))
    def test_G07_internal_lane_stopping_identity(self):
        self.assertEqual(a.safe_identity('R.0',':x',set(),{'R.0':{}},{':x':{}},0),0)
        with self.assertRaises(ValueError):a.unique(['ramp','ramp'],'region memberships')
    def test_G08_endpoint_boundary(self):
        rows=[{'depart':1499,'arrival':1500},{'depart':1500,'arrival':1501},{'depart':1501,'arrival':1600}]
        self.assertEqual(a.endpoint(3,rows,1500),(1,0,1,2))
        self.assertEqual(a.endpoint(3,rows,1501),(2,1,1,1))
        self.assertEqual(a.endpoint(3,rows,2700),(3,3,0,0))
    def test_G09_actual_duration_and_weights(self):
        r=[{'nVehContrib':1,'nVehEntered':2,'speed':10},{'nVehContrib':3,'nVehEntered':3,'speed':30}]
        self.assertEqual(a.e1_values(r,60),(4,5,25,240,300))
        self.assertEqual(a.e1_values(r,120)[3],120)
    def test_G10_outer_join_keeps_unpaired(self):
        out=a.paired_outer({'x':0,'y':4},{'x':1,'z':0})
        self.assertEqual(len(out),3);self.assertEqual(sum(r['value_state']=='not_paired' for r in out),2)
        self.assertIsNone(out[1]['seed23']);self.assertEqual(out[2]['seed23'],0)
    def test_G11_counter_semantics(self):
        _,_,_,qc,qe=a.e1_values([{'nVehContrib':1,'nVehEntered':2,'speed':20}],30)
        self.assertEqual(qc,120);self.assertEqual(qe,240);self.assertNotEqual(qc,qe)
    def test_G12_exclusive_creation_and_missing_states(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipt';p.open('x').close()
            with self.assertRaises(FileExistsError):p.open('x')
        self.assertEqual(a.state(None),'missing_observation');self.assertEqual(a.state(0),'observed_zero')

if __name__=='__main__':unittest.main(verbosity=2)
