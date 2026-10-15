"""Independent narrow offline receipt audit. No SUMO imports or launch calls.

C is reconstructed from request events on each acknowledged interval; N from
unique crossing observations, E from elapsed acknowledged nominal packets.
This validates fake evidence integrity, never physical service qualification.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
UNDER = 'DIAGNOSTIC_TARGET_NOT_MET_CAUSE_UNESTABLISHED'
PURPOSE = 'FINITE_PACKET_DIAGNOSTIC_ONLY'


def need(value, label):
    if not value:
        raise ValueError(label)


def audit(d):
    r, events, acks = d['receipt'], d['events'], d['acks']
    need(r['purpose'] == PURPOSE and r['general_service_qualified'] is False and
         r['formal_use_authorized'] is False and r['actuator_fault_established'] is False,
         'unsupported eligibility claim')
    need(isinstance(acks, list) and acks, 'missing ACK evidence')
    requests = [e for e in events if e['event'] == 'REQUESTED']
    ids = [e['request_id'] for e in requests]
    need(len(ids) == len(set(ids)), 'duplicate request')
    times = [e['global_request_s'] for e in requests]
    need(times == sorted(times) and times[0] == 1200, 'request chronology')
    packets = [e for e in events if e['event'] == 'PACKET_ACK_OBSERVED']
    need([e['cycle_id'] for e in packets] == list(range(len(packets))), 'missing or duplicate packet')
    need(packets and packets[0]['application_global_s'] == 1200, 'missing initial packet')
    C, seen = Fraction(0), set()
    for t, ack in enumerate(acks, 1200):
        need(ack['time_begin_s'] == t and ack['time_end_s'] == t+1 and
             ack['observed_time_s'] == t+1, 'missing duplicate or malformed ACK interval')
        need(ack['accounting_complete'] is True, 'incomplete accounting')
        active = [q for q in requests if q['global_request_s'] <= t]
        C += Fraction(str(active[-1]['rate_veh_h'])) / 3600
        for crossing in ack['actual_crossings']:
            vid = crossing['vehicle_id']
            need(vid not in seen, 'duplicate crossing')
            need(crossing['crossing_time_lower_s'] == t and crossing['crossing_time_upper_s'] == t+1,
                 'crossing not ACK bound')
            need(crossing['motion_signal_state'] in ('G', 'y'), 'red or unknown entry')
            need(vid in ack['post_world'], 'crossing absent from post-world')
            seen.add(vid)
        E = 2*sum(p['application_global_s']+p['period_s'] <= t+1 for p in packets)
        ac = ack['accounting']
        need(Fraction(ac['C_exact_fraction']) == C and ac['N'] == len(seen) and ac['E'] == E,
             'corrupt interval C E N')
    end = acks[-1]['time_end_s']
    need(d['world_time'] == end, 'unaccounted movement')
    need(Fraction(r['accounting']['C_exact_fraction']) == C and
         r['accounting']['N'] == len(seen) and r['accounting']['E'] == E, 'corrupt terminal accounting')
    assessed = [e for e in events if e['event'] == 'FINITE_PACKET_DIAGNOSTIC_ASSESSED']
    need(len({e['cycle_id'] for e in assessed}) == len(assessed), 'duplicate assessment')
    hard = r['status'] == 'HARD_OR_UNKNOWN_GATE_STOP'
    for ev in assessed:
        p = packets[ev['cycle_id']]
        boundary = p['application_global_s'] + p['period_s']
        relevant = [a for a in acks if p['application_global_s'] <= a['time_begin_s'] < boundary]
        n = sum(len(a['actual_crossings']) for a in relevant)
        need(ev['end_s'] == boundary <= end and len(relevant) == p['period_s'], 'partial or missing assessment')
        need(ev['actual_packet_N'] == n and ev['N'] == sum(len(a['actual_crossings']) for a in acks if a['time_end_s'] <= boundary), 'assessment N mismatch')
        need(ev['service_context'] and [f['time_s'] for f in ev['service_context']] == list(range(p['application_global_s'], boundary)), 'missing service context')
        need(ev['cause'] == 'UNESTABLISHED' and ev['actuator_fault_established'] is False and ev['general_service_qualified'] is False, 'false cause or qualification')
        at = acks[boundary-1201]['accounting']
        need(Fraction(ev['C_exact_fraction']) == Fraction(at['C_exact_fraction']) and ev['E'] == at['E'] and Fraction(ev['requested_minus_actual_exact_fraction']) == Fraction(at['C_exact_fraction'])-ev['N'], 'corrupt assessment accounting')
        need(ev['status'] == (UNDER if n < 2 else 'FINITE_DIAGNOSTIC_TARGET_OBSERVED_NOT_GENERAL_QUALIFICATION'), 'false target PASS')
        if n < 2:
            need(r['status'] == UNDER and end == boundary and len(packets) == ev['cycle_id']+1, 'continued after target failure')
            need(not any(s[0] >= boundary for s in d['setters']), 'setter after stop')
            need(not any(e.get('time_s', -1) >= boundary for e in events if e['event'] == 'BOUNDARY_PACKET_SELECTED_NOT_APPLIED'), 'selection after stop')
            need(ev['under_target_service_recovery'] == 'NOT_ATTEMPTED_DIAGNOSTIC_STOPS', 'recovery claim')
    need(r['service_diagnostic'] == (assessed[-1] if assessed and assessed[-1]['cycle_id'] == packets[-1]['cycle_id'] else None), 'terminal assessment mismatch')
    complete = packets[-1]['application_global_s']+packets[-1]['period_s'] <= end
    need(r['partial_cycle'] is (not complete), 'terminal partial flag')
    if hard:
        need(r['error'] and not assessed and r['service_diagnostic'] is None, 'hard failure downgraded')
    else:
        need(len(assessed) == E//2, 'missing complete assessment')
        need(r['status'] in (UNDER, 'FINITE_LOOP_COMPLETED_NOT_GENERAL_QUALIFICATION'), 'false result status')
        need((r['status'] == UNDER) == any(e['status'] == UNDER for e in assessed), 'false PASS or STOP')
    return dict(observation_accounting='PASS_OFFLINE_SYNTHETIC_ONLY', diagnostic_outcome=r['status'],
                C_exact_fraction=str(C), E=E, N=len(seen), requested_minus_actual_exact_fraction=str(C-len(seen)),
                accounted_end_s=end, partial=not complete, general_service_qualified=False)


def dump(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def main(out):
    out = out.resolve()
    spec = importlib.util.spec_from_file_location('scope_fixture', ROOT/'tests/candidate_a_service_scope_20261015/test_scope.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    results, bundles = {}, {}
    for label, kind, end, fault in [('empty','empty',1218,None), ('one_exact','one',1210,None),
                                     ('partial','two',1212,None), ('safety_priority','one',1218,'final_braking')]:
        w,a,error,receipt,events = m.ScopeTests().run_fixture(kind,end,fault)
        keys = ('time_begin_s','time_end_s','observed_time_s','accounting_complete','accounting','actual_crossings','post_world','status')
        bundle = dict(case=label,fixture=dict(kind=kind,end=end,fault=fault),world_time=w.time,setters=w.requests,
                      receipt=receipt,events=events,acks=[{k:v for k,v in x.items() if k in keys} for x in a.receipts if x.get('time_begin_s',-1)>=1200])
        dump(out/(label+'.json'),bundle)
        bundles[label] = bundle
        results[label] = audit(bundle)
    base=bundles['one_exact']
    mutations = {}
    def reject(label, change):
        d=deepcopy(base); change(d)
        try:
            audit(d)
        except (ValueError,KeyError,TypeError,IndexError) as exc:
            mutations[label]=str(exc)
        else:
            raise AssertionError('mutation accepted: '+label)
    reject('missing_ack',lambda d:d['acks'].pop(2))
    reject('duplicate_ack',lambda d:d['acks'].insert(1,deepcopy(d['acks'][0])))
    reject('malformed_interval',lambda d:d['acks'][0].update(time_end_s=1202))
    reject('duplicate_crossing',lambda d:d['acks'][0]['actual_crossings'].append(deepcopy(d['acks'][0]['actual_crossings'][0])))
    reject('false_pass',lambda d:d['receipt'].update(status='FINITE_LOOP_COMPLETED_NOT_GENERAL_QUALIFICATION'))
    reject('corrupt_C',lambda d:d['acks'][-1]['accounting'].update(C_exact_fraction='0'))
    reject('missing_terminal_assessment',lambda d:d['events'].pop())
    reject('post_stop_setter',lambda d:d['setters'].append([1210,'setProgram','fake']))
    reject('false_formal_eligibility',lambda d:d['receipt'].update(formal_use_authorized=True))
    # Pure ledger pending example already present in the engineering fixture;
    # independent integral uses 750 for 1s then 900 for 2s, without quota fill.
    q=m.Ledger(750,1203,purpose=PURPOSE)
    for t in range(1200,1203):
        q.begin_step(t,m.Command('pending',t,900,'SCHEDULED') if t==1201 else None)
        if t==1200:q.mark_cycle_start(True)
        q.end_step(t+1,['synthetic.one'] if t==1200 else [],'G')
    need(q.C == Fraction(750,3600)+2*Fraction(900,3600) == Fraction(17,24) and q.E==0 and q.N==1 and q.requests['pending']['first_application_s'] is None and q.assess_completed_packet() is None,'pending corruption')
    results['pending_pure_ledger']=dict(C_exact_fraction='17/24',E=0,N=1,pending_first_application_s=None,partial=True)
    dump(out/'AUDIT_RESULT_V1.json',dict(status='PASS_OFFLINE_SYNTHETIC_ONLY',cases=results,mutation_rejections=mutations,
         limitations=['No native/SUMO behavior verified','No general constrained-service continuation or causal readiness classification','Original 154 source and previous reader untouched']))
    paths=[Path(__file__),ROOT/'tests/candidate_a_service_scope_20261015/test_scope.py',*(ROOT/'src/candidate_a_service_scope_20261015').glob('*.py'),ROOT/'artifacts/pr13_underdischarge_fix_20261015_v1/engineering/ENGINEERING_BINDING_V1.json',*out.glob('*.json')]
    dump(out/'DATA_BINDING_V1.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    print(json.dumps(dict(status='PASS_OFFLINE_SYNTHETIC_ONLY',cases=len(results),mutation_rejections=len(mutations))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
