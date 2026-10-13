"""Bounded offline evidence-interface checks; fixtures are not actual SUMO/FCD."""
from pathlib import Path
import copy,json,unittest
from scripts.cumulative_full_catalogue_audit_20261014_v1 import core,evidence
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/revision01/synthetic_fixture'
def load(name):
    p=BASE/name
    def read(n):return [json.loads(x) for x in (p/n).read_text().splitlines()]
    pre=read('pre_steps.jsonl');post=read('post_steps.jsonl');entries=[]
    # Independent state-log transitions, not the reported crossing count.
    for b,z in zip(pre,post):
        before=b['bound_snapshot']['world'];after=z['post_world'];t=z['time_begin_s']
        for vid,v in after.items():
            if vid.startswith('R_flow.') and vid in before and before[vid]['lane_id']=='ramp_storage_0' and v['lane_id']==':ramp_mid_0_0':entries.append(dict(vehicle_id=vid,time_begin_s=t,time_end_s=t+1,motion=z['motion']))
    tls=[dict(time=str(q['time_begin_s']),id='ramp_mid',programID=b['bound_snapshot']['program'],phase=str(q['phase_observation']['phase_after']),state=q['motion']) for b,q in zip(pre,post)]
    return dict(pre=pre,post=post,entries=entries,events=read('command_events.jsonl'),tls=tls,ack=[q for q in read('step_ack.jsonl') if q['requested_target_s']>1200],phase_requests=read('policy_phase_requests.jsonl'),duration_requests=read('policy_duration_requests.jsonl'),yellow=read('yellow_scope.jsonl'),feedback=read('feedback_events.jsonl') if (p/'feedback_events.jsonl').exists() else [])
def run(f,end):
    a=core.audit_accounting(f['post'],f['events'],f['entries'],end)
    ph=core.audit_phases(f['tls'],f['post'],f['ack'],a['cycles'],f['phase_requests'],f['duration_requests'],f['pre'])
    return a,ph
class Tests(unittest.TestCase):
 def test_real_helper_synthetic_two_blocks_dynamic_and_Y_catalogue(self):
    f=load('fixed750_1296_True_False');a,ph=run(f,1296)
    self.assertEqual([x['period_s'] for x in a['cycles']],[10,9,10,9,10]*2)
    self.assertEqual(a['accounting']['C'],20);self.assertEqual(a['accounting']['E'],20);self.assertEqual(a['accounting']['N'],20)
    # Control-only fixtures are shifted into global array-index space for this
    # unchanged full-reader yellow seam; no warmup observations are synthesized.
    yy=evidence.yellow_coverage(f['yellow'],ph,a['cycles'],[None]*1200+f['post'],[None]*1200+f['pre'],1296,False)
    self.assertEqual(yy['observed_first_Y_count'],10)
    f=load('dynamic_commands_1218_True_False');a,ph=run(f,1218);self.assertEqual(a['cycles'][0]['period_s'],10);self.assertEqual(a['cycles'][1]['period_s'],8)
    self.assertTrue(any(x['application_delay_s']>0 for x in a['applications']))
 def test_missing_bad_boundary_application_phase_and_counts(self):
    good=load('fixed750_1296_True_False')
    for fault in ('selection','fraction','packet_ack','request_origin','missing_request_feedback','missing_pending_null','missing_chain_feedback','missing_application_delay','count','tls','time'):
        f=copy.deepcopy(good)
        if fault in ('selection','fraction'):
            e=next(x for x in f['events'] if x['event']=='BOUNDARY_PACKET_SELECTED_NOT_APPLIED');e['chosen_period_s']=9 if fault=='selection' else e['chosen_period_s'];e['actual_C_fraction']='1' if fault=='fraction' else e['actual_C_fraction']
        if fault=='packet_ack':f['events']=[e for e in f['events'] if e['event']!='PACKET_ACK_OBSERVED']
        if fault=='request_origin':f['events'][0]['origin']='SCRIPTED_DIAGNOSTIC'
        if fault=='missing_request_feedback':f['events'][0].pop('r_ALINEA')
        if fault=='missing_pending_null':f['post'][0]['rate_chain'].pop('r_policy_pending_veh_h')
        if fault=='missing_chain_feedback':f['post'][0]['rate_chain'].pop('r_ALINEA')
        if fault=='missing_application_delay':f['post'][0]['rate_chain'].pop('cycle_application_delay_s')
        if fault=='count':f['post'][0]['accounting']['N']=99
        if fault=='tls':f['tls'][20]['programID']='I12_PACKET8' # Actually T10 at1219..1229.
        if fault=='time':f['ack'][0]['requested_target_s']=1202
        with self.subTest(fault=fault),self.assertRaises(ValueError):run(f,1296)
 def test_zero_partial_null_extra_and_no_catchup(self):
    self.assertTrue(all(x is None for x in core.audit_accounting([],[],[],1296)['accounting'].values()))
    with self.assertRaises(ValueError):core.audit_accounting([], [dict(event='PACKET_ACK_OBSERVED',application_global_s=1200,first_green_ACK_s=1201)],[],1296)
    # Names are early/deadline/shortfall selectors, not count specifications.
    # Tiny count-interface fixtures below are explicitly in-memory synthetic.
    f=load('fixed750_1210_False_True');f['entries']=[]
    for q in f['post']:
        q['actual_crossings']=[];a=q['accounting'];a['N']=0;a['nominal_minus_actual']=a['E'];a['requested_minus_actual']=a['C']
    a,ph=run(f,1210);self.assertEqual(a['accounting']['N'],0);self.assertEqual(a['accounting']['E'],2)
    f=load('fixed750_1210_False_True');a,ph=run(f,1210);self.assertEqual(a['accounting']['N'],1)
    f=load('fixed750_1210_False_False');t=next(q['time_begin_s'] for q in f['post'] if q['motion']=='y');f['entries'].append(dict(vehicle_id='R_flow.synthetic_extra',time_begin_s=t,time_end_s=t+1,motion='y'))
    for q in f['post']:
        if q['time_begin_s']==t:q['actual_crossings'].append(dict(vehicle_id='R_flow.synthetic_extra'))
        if q['time_begin_s']>=t:
            a=q['accounting'];a['N']+=1;a['nominal_minus_actual']=a['E']-a['N'];a['requested_minus_actual']=a['C']-a['N']
    a,ph=run(f,1210);self.assertEqual(a['accounting']['N'],3);self.assertEqual(a['cycles'][0]['N_y'],1)
    denied=copy.deepcopy(f);denied['post'].append(load('fixed750_1296_True_False')['post'][10])
    with self.assertRaisesRegex(ValueError,'SERVICE_PACKET_MISMATCH_NO_AUTOMATIC_CATCHUP'):
        core.audit_accounting(denied['post'],denied['events'],denied['entries'],1296)
    # Exact independently indexed input consumption is mandatory even for an
    # already seen ID. An extra unobserved record must not disappear.
    bad=copy.deepcopy(f);bad['entries'].append(dict(bad['entries'][0],time_begin_s=1210,time_end_s=1211))
    with self.assertRaises(ValueError):run(bad,1210)
    self.assertEqual(core.select(core.F(0),0,300)[0],24);self.assertEqual(core.select(core.F(0),0,900)[0],8)
    for T in range(8,25):
        p=core.catalogue(T);self.assertEqual(p['max_green_s'],5 if T==10 else 4);self.assertEqual(p['yellow_s'],3 if T==10 else min(5,T-6));self.assertGreaterEqual(T-p['max_green_s']-p['yellow_s'],2)
    # Pure arithmetic only: exact tie between adjacent periods chooses longer.
    T,scores=core.select(core.F(-1,9),0,800);self.assertEqual(T,10);self.assertEqual(abs(scores[9]),abs(scores[10]))
    with self.assertRaises(ValueError):core.select(core.F(0),0,299)
    with self.assertRaises(ValueError):core.select(core.F(0),True,750)
    # Crop a valid raw-interface fixture; no last complete packet is invented.
    f=load('fixed750_1296_True_False');end=1204
    f['post']=f['post'][:4];f['entries']=[x for x in f['entries'] if x['time_begin_s']<end]
    f['events']=[e for e in f['events'] if (e.get('global_request_s',e.get('time_s',e.get('application_global_s',1200)))<end)]
    a=core.audit_accounting(f['post'],f['events'],f['entries'],1296);self.assertEqual(a['accounting']['E'],0);self.assertFalse(a['cycles'][0]['completed'])
 def test_real_feedback_raw_events_recomputed_no_nearest_label(self):
    f=load('real_alinea_1296_True_False');a,ph=run(f,1296);result=core.audit_feedback(f['feedback'],f['events'],a,1296)
    self.assertEqual(result['status'],'PASS_REAL_FEEDBACK_RECOMPUTATION');self.assertEqual([x['global_s']for x in result['decisions']],[1230,1260,1290]);self.assertTrue(result['feedback_command_applied'])
    self.assertEqual(result['different_period_observed'],len({c['period_s']for c in a['cycle_applications']})>1)
    self.assertEqual(result['period_source'],'ACTUAL_FIRST_G_ACK_CYCLE_APPLICATIONS_NOT_NEAREST_REFERENCE')
    bad=copy.deepcopy(f['feedback']);q=next(x for x in bad if x['event']=='PROJECT_FEEDBACK_DECISION');q['rate_previous_veh_h']=700
    with self.assertRaises(ValueError):core.audit_feedback(bad,f['events'],a,1296)
if __name__=='__main__':unittest.main()
