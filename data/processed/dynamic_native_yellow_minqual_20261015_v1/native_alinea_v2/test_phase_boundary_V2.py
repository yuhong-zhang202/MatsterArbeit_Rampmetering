"""One affected boundary method; real phase subset plus labelled mutations."""
from pathlib import Path
import unittest,json,copy,importlib.util,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=module(ROOT/'scripts/cumulative_full_catalogue_audit_20261014_v1/_phase.py','scripts.cumulative_full_catalogue_audit_20261014_v1.old_boundary')
new=module(HERE/'phase_boundary_V2.py','phase_boundary_V2')
class Tests(unittest.TestCase):
 def test_terminal_unexecuted_duration_and_all_observed_trace_still_required(self):
  f=json.loads((HERE/'ACTUAL_PHASE_SUBSET_V1.json').read_text());args=lambda q:[q[k] for k in ('tls','posts','acks','cycles','phase_requests','durations','pre_rows')]
  with self.assertRaisesRegex(ValueError,'RED_DURATION_TRACE_COVERAGE'):old.audit_phases(*args(f))
  self.assertEqual(new.audit_phases(*args(f))['status'],'PASS_CONTINUOUS_PHASES')
  bad=copy.deepcopy(f);bad['posts'][-1]['phase_observation']['next_switch_after_s']=1298
  with self.assertRaises(ValueError):new.audit_phases(*args(bad))
  bad=copy.deepcopy(f);bad['cycles'][-1]['completed']=True
  with self.assertRaises(ValueError):new.audit_phases(*args(bad))
  bad=copy.deepcopy(f);bad['phase_requests'].append({'requests':[{'method':'setPhaseDuration','time_s':1296,'value':1,'call_completed':True}]})
  with self.assertRaisesRegex(ValueError,'RED_DURATION_TRACE_COVERAGE'):new.audit_phases(*args(bad))
  bad=copy.deepcopy(f);bad['durations'].append({'time_s':1296,'status':'ATTEMPTED','call_completed':False})
  with self.assertRaisesRegex(ValueError,'RED_DURATION_TRACE_COVERAGE'):new.audit_phases(*args(bad))
  # A real observed earlier first-red interval is not a terminal exemption.
  bad=copy.deepcopy(f);bad['durations']=[d for d in bad['durations'] if d['time_s']!=1288]
  with self.assertRaisesRegex(ValueError,'RED_DURATION_TRACE_COVERAGE'):new.audit_phases(*args(bad))
if __name__=='__main__':unittest.main()
