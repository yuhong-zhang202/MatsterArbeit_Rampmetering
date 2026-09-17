"""Stage 2 archive-only boundary tests. No simulator is imported or launched."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/analysis'))
from analyze_stage2_exploration import (ArchiveResolver, classify, endpoint_counts, before,
    read_trips, read_fcd, comparisons, category, digest, e1_row, check_intervals, summarize_e1,
    crossing_event, reserve_directories)


class ExplorationAnalysisTests(unittest.TestCase):
    def test_archive_only_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);archive=root/'archive/attempt';archive.mkdir(parents=True)
            (archive/'data').write_text('retained')
            mapping={'archive_status':'complete','archive_runtime_relative_path':'archive/attempt','source_runtime_path':'/private/tmp/prohibited','file_map':[{'original_absolute_path':'/private/tmp/prohibited/data','archive_relative_path':'archive/attempt/data','sha256':digest(archive/'data')}]}
            m=root/'map.json';m.write_text(json.dumps(mapping))
            original_open=Path.open
            def guarded(path,*args,**kwargs):
                if str(path).startswith('/private/tmp/prohibited'):raise AssertionError('Original read attempted')
                return original_open(path,*args,**kwargs)
            with patch.object(Path,'open',guarded):
                r=ArchiveResolver(m,root)
                self.assertEqual(r.resolve('/private/tmp/prohibited/data').read_text(),'retained')
                with self.assertRaises(ValueError):r.resolve('/private/tmp/prohibited/missing')
            (archive/'data').write_text('changed')
            with self.assertRaises(ValueError):r.verify()
            with self.assertRaises(ValueError):ArchiveResolver(m,root)

    def test_archive_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'outside').write_text('x')
            m=root/'map.json';m.write_text(json.dumps({'archive_status':'complete','archive_runtime_relative_path':'archive/attempt','source_runtime_path':'/old','file_map':[{'original_absolute_path':'/old/a','archive_relative_path':'outside','sha256':digest(root/'outside')}]}))
            with self.assertRaises(ValueError):ArchiveResolver(m,root)

    def test_four_vehicle_states(self):
        self.assertEqual(classify(None),'record_missing_unknown')
        self.assertEqual(classify(None,True),'not_entered_confirmed')
        self.assertEqual(classify({'depart':10,'arrival':-1}),'entered_unfinished')
        self.assertEqual(classify({'depart':10,'arrival':20}),'arrived')

    def test_endpoint_does_not_require_precise_schedule(self):
        self.assertEqual(endpoint_counts(10,8,6,True),{'outside_confirmed':2,'in_network':2,'unaccounted_count':0})
        self.assertEqual(endpoint_counts(10,8,6,False),{'outside_confirmed':None,'in_network':None,'unaccounted_count':2})
        self.assertEqual(endpoint_counts(0,0,0,True)['outside_confirmed'],0)
        with self.assertRaises(ValueError):endpoint_counts(5,6,5,True)

    def test_exact_time_boundaries(self):
        for t in (0,1500,2700):
            self.assertFalse(before(t,t));self.assertTrue(before(t,t+1))
        self.assertFalse(before(-1,2700));self.assertFalse(before(None,2700))

    def test_unknown_id(self):
        with self.assertRaises(ValueError):category('arbitrary')

    def test_duplicate_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'trip.xml';p.write_text('<tripinfos>'+('<tripinfo id="M_flow.0" depart="0" arrival="1" departDelay="0" duration="1"/>'*2)+'</tripinfos>')
            with self.assertRaises(ValueError):read_trips(p)

    def test_missing_fcd_and_merge_bracket(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'fcd.xml';p.write_text('<fcd-export><timestep time="29"><vehicle id="R_flow.0" lane=":freeway_merge_0_0" speed="4"/></timestep><timestep time="30"><vehicle id="R_flow.0" lane="main_down_0" speed="5"/></timestep><timestep time="32"><vehicle id="R_flow.0" lane="main_down_1" speed="6"/></timestep></fcd-export>')
            frames,ids,events,_=read_fcd(p,{'R_flow.0'})
            self.assertNotIn(31,frames);self.assertEqual(len(events),1)
            self.assertTrue(events['R_flow.0']['boundary_30s_ambiguous'])
            self.assertNotIn(2700,frames)
        self.assertEqual(crossing_event('R',None,(1,'main_down_0'))['status'],'unresolved')
        self.assertEqual(crossing_event('R',(1,'ramp_accel_0'),(3,'main_down_0'))['reason'],'non_unit_sample_gap')

    def test_duplicate_fcd(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'f.xml';p.write_text('<fcd-export><timestep time="0"><vehicle id="R_flow.0" lane="ramp_accel_0" speed="1"/><vehicle id="R_flow.0" lane="ramp_accel_0" speed="1"/></timestep></fcd-export>')
            with self.assertRaises(ValueError):read_fcd(p,set())

    def test_e1_sentinel_weighting_and_coverage(self):
        def row(t,s,n):return e1_row({'id':'e','begin':str(t),'end':str(t+30),'speed':str(s),'flow':str(n*120),'occupancy':'1','nVehContrib':str(n),'nVehEntered':str(n)},'e','lane')
        a,b=row(0,10,1),row(30,20,3)
        self.assertEqual(summarize_e1([a,b],0,60)['speed_mps'],17.5)
        self.assertIsNone(summarize_e1([row(0,-1,0)],0,30)['speed_mps'])
        with self.assertRaises(ValueError):check_intervals([a,a],end=60)
        with self.assertRaises(ValueError):check_intervals([a],end=60)

    def test_output_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):reserve_directories([Path(directory)])
        # After the C17 fixture artifact is built, its repeat verification must
        # exercise every assertion with all write-capable opens forbidden.
        root=Path(__file__).resolve().parents[1]
        script=None
        # Historical reports retain historical code hashes. Exercise a built
        # verification fixture only when it describes the current code version.
        for revision in ('revision_04','revision_03','revision_02','revision_01'):
            folder=root/'data/processed/stage2_completion_20260909_v1'/revision
            candidate=folder/'independent_verification.py'
            if candidate.exists() and (folder/'manifest.json').exists():
                expected=json.loads((folder/'manifest.json').read_text())['source_sha256'].get(str(root/'src/analysis/analyze_stage2_exploration.py'))
                if expected==digest(root/'src/analysis/analyze_stage2_exploration.py'):
                    script=candidate;break
        if script is not None:
            import contextlib, io, runpy
            original_open=Path.open
            def readonly(path, mode='r', *args, **kwargs):
                if any(flag in mode for flag in 'wax+'):raise AssertionError('check-only attempted to write')
                return original_open(path,mode,*args,**kwargs)
            with patch.object(sys,'argv',[str(script),'--check-only']),patch.object(Path,'open',readonly),contextlib.redirect_stdout(io.StringIO()) as result:
                runpy.run_path(str(script),run_name='__main__')
            self.assertEqual(json.loads(result.getvalue())['mode'],'check_only')

    def test_no_comparison_until_matching_seed_available(self):
        def row(run,value):return {'run_id':run,'family':'cohort','entity':'R','window':'A','metric':'actual_departures','value':value,'unit':'veh','denominator':None}
        self.assertEqual(comparisons([row('C17',10),row('ML23',20)])['contrasts'],[])
        self.assertEqual(comparisons([row('C17',10),row('ML17',20)])['contrasts'][0]['difference'],10)


if __name__=='__main__':unittest.main()
