"""Independent arithmetic and real public phase-subset regressions, no SUMO."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.unified_alinea_audit_20261013_v1.core import *

def toy(schedule,stop,end,entry_times=()):
    requests=[];events=[];rows=[];entries=[];applied={};cycles=[];s=[Fraction(0)]*3;E=N=0
    for t,rate in schedule:
        T,r=mapping(rate);q=dict(event='REQUESTED',request_id=str(t),global_request_s=t,rate_veh_h=rate,origin='SCHEDULED',r_ALINEA=None,mapped_period_s=T,mapped_rate_veh_h=float(r));requests.append(q);events.append(q)
    for t in range(1200,stop):
        q=[x for x in requests if x['global_request_s']<=t][-1];T,r=mapping(q['rate_veh_h']);new=not cycles or cycles[-1]['end']==t
        if new:
            cycles.append(dict(begin=t,end=t+T,q=q));rid=q['request_id']
            if rid not in applied:
                applied[rid]=t;events.append(dict(event='ACK_OBSERVED',request_id=rid,application_global_s=t,first_green_ACK_s=t+1,application_delay_s=t-q['global_request_s']))
        cycle=cycles[-1];a=cycle['q'];at,ar=mapping(a['rate_veh_h']);motion='G' if t-cycle['begin']<4 else 'y' if t-cycle['begin']<4+min(5,at-6) else 'r'
        ids=[]
        if t in entry_times:
            vid=f'R_flow.{N}';entries.append(dict(vehicle_id=vid,time_begin_s=t,time_end_s=t+1,motion=motion));ids=[dict(vehicle_id=vid)];N+=1
        s[0]+=Fraction(q['rate_veh_h'],3600);s[1]+=r/3600;s[2]+=ar/3600
        if t+1==cycle['end']:E+=2
        account=dict(C=float(s[0]),C_mapped_pending=float(s[1]),C_applied=float(s[2]),E=E,N=N,policy_quantization=float(s[0]-s[1]),application_latency=float(s[1]-s[2]),C_applied_minus_E=float(s[2]-E),E_minus_N=E-N)
        rc=dict(pending_request_id=q['request_id'],input_origin='SCHEDULED',r_final_veh_h=q['rate_veh_h'],r_policy_pending_veh_h=float(r),applied_request_id=a['request_id'],period_s=at,requested_quota=2,r_policy_applied_veh_h=float(ar),cycle_application_delay_s=None if new else applied[a['request_id']]-a['global_request_s'])
        rows.append(dict(time_begin_s=t,time_end_s=t+1,accounting_complete=True,motion=motion,rate_chain=rc,actual_crossings=ids,accounting=account))
    # Command requests are interleaved with applications in real time.
    events.sort(key=lambda e:(e.get('global_request_s',e.get('application_global_s')),e['event']=='ACK_OBSERVED'))
    return rows,events,entries

class AuditTests(unittest.TestCase):
    def test_zero_partial_unobserved_and_unbound_entries(self):
        rows,events,entries=toy([(1200,300)],1201,1272)
        out=audit_accounting(rows,events,entries,1272)
        self.assertEqual((out['accounting']['N'],out['accounting']['E']),(0,0));self.assertFalse(out['cycles'][0]['completed']);self.assertAlmostEqual(out['accounting']['C'],1/12)
        self.assertTrue(all(v is None for v in audit_accounting([],events,[],1272)['accounting'].values()))
        for extra in ({'vehicle_id':'R_flow.0','time_begin_s':1201,'time_end_s':1202,'motion':'G'},{'vehicle_id':'R_flow.0','motion':'G'}):
            with self.assertRaises(ValueError):audit_accounting(rows,events,[extra],1272)
    def test_midcycle_and_quantization(self):
        rows,events,entries=toy([(1200,300),(1201,750),(1226,900),(1237,300)],1266,1266,(1200,1224,1234,1242))
        q=audit_accounting(rows,events,entries,1266)
        self.assertEqual([x['application_delay_s'] for x in q['applications']],[0,23,8,5]);self.assertAlmostEqual(q['accounting']['C'],251/24);self.assertEqual(q['accounting']['C_mapped_pending'],10.25);self.assertEqual(q['accounting']['C_applied'],8);self.assertEqual((q['accounting']['E'],q['accounting']['N']),(8,4))
        r,e,n=toy([(1200,750)],1270,1270);a=audit_accounting(r,e,n,1270);self.assertEqual(a['accounting']['C_applied'],14);self.assertAlmostEqual(a['accounting']['policy_quantization'],7/12)
        with self.assertRaises(ValueError):audit_accounting(rows,events,entries+[dict(entries[0])],1266)
    def test_real900_public_phases_and_reordering(self):
        f=json.loads((ROOT/'data/processed/issue12_phase_sequence_fix_20261013_v1/PUBLIC_PHASE_FIXTURE_V1.json').read_text());cycles=[]
        for b in range(1200,1272,8):cycles.append(dict(begin_s=b,end_s=b+8,period_s=8,N_G=2,completed=True,phase_exposure_s={'G':4,'y':2,'r':2}))
        args=(f['tls_rows'],f['post_rows'],f['ack_rows'],cycles,f['phase_requests'],f['duration_requests'])
        self.assertEqual(len(audit_phases(*args)['cycles']),9)
        bad=copy.deepcopy(f);bad['tls_rows'][0],bad['tls_rows'][4]=bad['tls_rows'][4],bad['tls_rows'][0]
        with self.assertRaises(ValueError):audit_phases(bad['tls_rows'],*args[1:])
    def test_feedback_global_ongoing_clipped_and_application(self):
        raw={d:[['A',5,1199,-1,'technical_passenger']] for d in DETECTORS};ev=[dict(event='E1_ACTIVATION_SEED',global_s=1200,logical_s=600,raw_events=raw,ongoing_events=raw)];cmd=[]
        for t in range(1201,1261):
            x=[['A',5,1199,-1 if t<1203 else 1203,'technical_passenger']] if t<=1203 else [['B',5,1240,-1 if t<1246 else 1246,'technical_passenger']] if 1240<=t<=1246 else []
            v={d:x for d in DETECTORS};ev.append(dict(event='E1_POST_ACK_EVENTS',global_s=t,logical_s=t-600,raw_events=v,normalized_events=v))
            if t in (1230,1260):
                o=10 if t==1230 else 20;previous=900;unclipped=previous+70*(11-o);clipped=max(300,min(900,unclipped));rid=f'feedback:{t}'
                ev.append(dict(event='PROJECT_FEEDBACK_DECISION',global_s=t,logical_s=t-600,global_window_begin_s=t-30,global_window_end_s=t,update_time_s=t-600,interval_begin_s=t-630,interval_end_s=t-600,detector_ids=list(DETECTORS),contributors=[1,1],request_id=rid,occ_l0_pct=o,occ_l1_pct=o,occ_mean_pct=o,rate_previous_veh_h=previous,rate_raw_veh_h=unclipped,rate_clipped_veh_h=clipped));cmd.append(dict(event='REQUESTED',request_id=rid,origin='PROJECT_FEEDBACK',global_request_s=t,rate_veh_h=clipped))
        out=audit_feedback(ev,cmd,{'applications':[{'request_id':'feedback:1230'}]},1260);self.assertTrue(out['feedback_command_applied']);self.assertFalse(out['different_period_observed']) # pending 300 is not applied
        bad=copy.deepcopy(ev);bad[1]['raw_events']={d:[] for d in DETECTORS}
        with self.assertRaises(ValueError):audit_feedback(bad,cmd,{'applications':[]},1260)

if __name__=='__main__':unittest.main()
