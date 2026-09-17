"""Dedicated pure analysis tests; no simulator imports or launches."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/analysis'))
from validate_internal_e1 import combined_summary
from build_stage2_g1_diagnostic import e1_row, check_intervals

def row(lane,speed,count,begin=0):
    return e1_row({'id':lane,'begin':str(begin),'end':str(begin+30),'speed':str(speed),'flow':str(count*120),'occupancy':'5','nVehContrib':str(count),'nVehEntered':str(count)},lane,lane)

class InternalE1AnalysisTests(unittest.TestCase):
    def test_parallel_flow_sum_and_weighted_speed(self):
        s=combined_summary([row('a',10,1),row('b',20,3)],0,30)
        self.assertEqual(s['total_flow_vehph'],480)
        self.assertEqual(s['speed_mps'],17.5)
        self.assertEqual(s['nVehContrib'],4)
    def test_empty_speed_stays_missing(self):
        s=combined_summary([row('a',-1,0),row('b',-1,0)],0,30)
        self.assertIsNone(s['speed_mps']);self.assertEqual(s['total_flow_vehph'],0)
    def test_boundaries(self):
        s=combined_summary([row('a',10,1),row('a',20,2,30)],30,60)
        self.assertEqual(s['nVehContrib'],2)
    def test_duplicate_intervals_rejected(self):
        with self.assertRaises(ValueError):check_intervals([row('a',10,1),row('a',10,1)],end=60)

if __name__=='__main__':unittest.main()
