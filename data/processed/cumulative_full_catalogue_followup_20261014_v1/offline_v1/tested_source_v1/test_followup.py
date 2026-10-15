"""Affected follow-up interfaces only; fake movement is not native service."""
import copy,importlib.util,json,pathlib,unittest
from scripts.cumulative_full_catalogue_followup_audit_20261014_v1.scope import check_card_scope,terminal_scope,COMPLETE,PARTIAL
from scripts.cumulative_full_catalogue_audit_20261014_v1 import core
ROOT=pathlib.Path(__file__).resolve().parents[2]
def card(run,mode):
 return {'classification':'OFFLINE_CUMULATIVE_TRACKING_NOT_NATIVE_AUTHORIZED','numerical_exception_authority':{'enabled':False},'spec':{'run_id':run,'mode':mode,'end_s':1296,'activation_s':1200,'step_s':1,'seed':17,'phase_durations_s':{str(t):([5,3,2] if t==10 else [4,min(5,t-6),t-4-min(5,t-6)]) for t in range(8,25)},'catalogue_periods_s':list(range(8,25)),'scheduler':'ACTUAL_C_MINUS_N_BOUNDARY_ONLY','terminal_partial_allowed':True,'partial_final_cycle_allowed':True,'input_origin':'PROJECT_FEEDBACK' if mode=='real_alinea' else mode,'requested_schedule':{'1200':300,'1201':750,'1226':900,'1237':300} if mode=='dynamic_commands' else None,'initial_command_veh_h':300 if mode=='dynamic_commands' else 900,'request_schedule':{'1200':300,'1201':750,'1226':900,'1237':300} if mode=='dynamic_commands' else None,'Feedback':{'target_percent':11,'gain_veh_h_per_percentage_point':70,'bounds_veh_h':[300,900],'initial_veh_h':900,'sample_s':30,'global_activation_s':1200,'logical_activation_s':600,'detector_ids':['p1_main_down_20_l0','p1_main_down_20_l1'],'lanes':['main_down_0','main_down_1'],'position_m':20} if mode=='real_alinea' else None}}
class Tests(unittest.TestCase):
 def test_exact_two_card_scope_and_reject_foreign_mode_clock_NUM(self):
  for run,mode in [('UA_CUMULATIVE_FULL_DYNAMIC_S17_01','dynamic_commands'),('UA_CUMULATIVE_FULL_ALINEA_S17_01','real_alinea')]:
   c=card(run,mode);self.assertEqual(check_card_scope(c),mode)
   for fault in ('run','mode','end','NUM'):
    bad=copy.deepcopy(c)
    if fault=='run':bad['spec']['run_id']='UA_CUMULATIVE_FULL750_S17_01'
    elif fault=='mode':bad['spec']['mode']='fixed750'
    elif fault=='end':bad['spec']['end_s']=1297
    else:bad['numerical_exception_authority']['enabled']=True
    with self.subTest(fault=fault),self.assertRaises(ValueError):check_card_scope(bad)
 def test_terminal_partial_censor_null_and_early_STOP_never_success(self):
  full={'observed_end_s':1296,'planned_end_observed':True,'cycles':[{'begin_s':1286,'completed':True,'N':2,'E':2}]}
  part=copy.deepcopy(full);part['cycles'][0].update(completed=False,N=1,E=0)
  q=terminal_scope({'status':PARTIAL,'error':''},1296,1296,part,{'R_flow.9'});self.assertFalse(q['runtime_stop']);self.assertTrue(q['partial_cycle']);self.assertIsNone(q['outside_observed_window_N'])
  self.assertFalse(terminal_scope({'status':COMPLETE,'error':''},1296,1296,full,set())['runtime_stop'])
  self.assertFalse(terminal_scope({'status':PARTIAL,'error':''},1296,1296,full,{'R_flow.9'})['runtime_stop'])
  for receipt,t,a,censored in [({'status':PARTIAL,'error':''},1295,part,set()),({'status':PARTIAL,'error':'UNKNOWN'},1296,part,set()),({'status':COMPLETE,'error':''},1296,part,set()),({'status':PARTIAL,'error':''},1296,full,set())]:
   with self.assertRaises(ValueError):terminal_scope(receipt,t,1296,a,censored)
  stopped=terminal_scope({'status':'ABORTED_UNKNOWN','error':'UNKNOWN'},1290,1296,part,set());self.assertTrue(stopped['runtime_stop'])
  unobserved=core.audit_accounting([],[],[],1296);self.assertTrue(all(x is None for x in unobserved['accounting'].values()))
 def test_actual_producer_helper_dynamic_partial_and_real_feedback_fixture(self):
  # Loader is the independent old input adapter, not the production Ledger.
  spec=importlib.util.spec_from_file_location('reused_independent_loader',ROOT/'tests/cumulative_full_catalogue_audit_20261014/test_audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.BASE=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/revision01/synthetic_fixture'
  for name in ('dynamic_commands','real_alinea'):
   f=m.load(name);a,p=m.run(f,1296);self.assertEqual(a['observed_end_s'],1296)
   status=PARTIAL if not a['cycles'][-1]['completed'] else COMPLETE
   q=terminal_scope({'status':status,'error':''},1296,1296,a,set());self.assertFalse(q['runtime_stop'])
   if name.startswith('dynamic'):
    self.assertEqual([x['global_request_s'] for x in f['events'] if x['event']=='REQUESTED' and x['request_id']!='initial'],[1200,1201,1226,1237])
    self.assertAlmostEqual(a['accounting']['C'],311/24);self.assertTrue(any(x['application_delay_s']>0 for x in a['applications']))
    self.assertFalse(a['cycles'][-1]['completed']);self.assertLess(a['cycles'][-1]['phase_exposure_s']['G']+a['cycles'][-1]['phase_exposure_s']['y']+a['cycles'][-1]['phase_exposure_s']['r'],a['cycles'][-1]['period_s'])
   else:
    feedback=core.audit_feedback(f['feedback'],f['events'],a,1296);self.assertTrue(feedback['feedback_command_applied']);self.assertEqual([x['global_s'] for x in feedback['decisions']],[1230,1260,1290]);self.assertIn('feedback:1290',a['requests_without_observed_application'])
if __name__=='__main__':unittest.main()
