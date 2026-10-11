"""Independent public-evidence accounting and adversarial arithmetic probes.

No SUMO, network, ignored raw or production imports. Outputs are exclusive
versioned writes. PASS is evidence integrity, never transition qualification.
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ENG = 'artifacts/candidate_a_a1_contract_20261011_v1/engineering/'
SNAP = 'artifacts/candidate_a_qualification_20261008_v1/pr_review/CA_FIXED_R300_S17_A07/outputs/failure_snapshot.json'
GATE = 'data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_GATE_V3.json'
WINDOWS = 'results/tables/candidate_a_qualification_20261008_v1/R300_A07_SERVICE_WINDOWS_V3.csv'
THIN = 'results/tables/candidate_a_qualification_20261008_v1/R300_A07_PHASE_LEDGER_THIN_V3.csv'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def load(relative):
    check(not relative.startswith('data/raw/'), 'ignored raw forbidden')
    return json.loads((ROOT / relative).read_text())


def run():
    binding_path = ENG + 'v3/INPUT_BINDINGS_V3.json'
    inputs = load(binding_path)['files']
    check(all(not p.startswith('data/raw/') for p in inputs), 'raw dependency')
    check(all(sha(ROOT/p) == h for p,h in inputs.items()), 'input hash mismatch')
    protected = load(ENG + 'PROTECTED_BASELINE_SHA256.json')['files']
    check(len(protected) == 536, 'protected count')
    check(all(sha(ROOT/p) == h for p,h in protected.items()), 'protected drift')
    excerpts = load(ENG + 'SOURCE_EXCERPTS.json')
    receipt = load(ENG + 'SOURCE_RECEIPT.json')
    check(excerpts['commit'] == receipt['resolved_commit'], 'source commit')
    by_source = {r['path']:r for r in receipt['sources']}
    for e in excerpts['excerpts']:
        check(e['path'] in by_source, 'excerpt source not retrieved')
        check(hashlib.sha256(e['text'].encode()).hexdigest() == e['sha256'], 'excerpt bytes')
        check(len(e['text'].splitlines()) == e['line_end']-e['line_start']+1, 'physical lines')
        check('/'+excerpts['commit']+'/' in e['url'], 'fixed URL')
    snapshot = load(SNAP); state = snapshot['snapshot']
    check(snapshot['decision_time_s'] == snapshot['last_completed_step_s'] == snapshot['last_accounted_s'] == 1206, 'timing')
    check(state['state_before']=='y' and state['predicted_motion']=='r' and state['next_switch']==1206, 'pending event')
    witnesses = state['red_transition']['witnesses']
    vehicles = state['vehicle_states']
    ids = [v['vehicle_id'] for v in vehicles]
    check(len(ids) == len(set(ids)) == 42, 'vehicle duplicate/missing')
    witness_ids = [w['vehicle_id'] for w in witnesses]
    check(len(witness_ids)==len(set(witness_ids))==42 and set(ids)==set(witness_ids), 'witness coverage')
    wmap = {w['vehicle_id']:w for w in witnesses}
    topology = load(ENG+'STATIC_TOPOLOGY.json')
    net = ET.parse(ROOT/topology['input_path']).getroot()
    lane_length = float(net.find(".//lane[@id='ramp_storage_0']").get('length'))
    check(lane_length == 204.49, 'bound storage length')
    junction = net.find("junction[@id='ramp_mid']")
    check(junction.find('request').get('foes')=='0', 'static configured foes')
    mapping=[]
    for v in vehicles:
        speed=v['speed_m_s']; b=v['normal_decel_m_s2']; gap=lane_length-v['position_m']
        required=0.0 if speed==0 else 1.1+speed+speed**2/(2*b)
        margin=gap-required; safe=gap+1e-9>=required
        w=wmap[v['vehicle_id']]
        check(abs(required-w['required_normal_red_m'])<1e-12 and abs(margin-w['margin_m'])<1e-12 and safe==w['safe'], 'old guard '+v['vehicle_id'])
        # Independent finite sum of speeds AFTER each full normal Euler decrement.
        stop_b=max(min(3.0,9.0),b)
        count=int(speed/stop_b)
        brake=sum(speed-i*stop_b for i in range(1,count+1))
        offset=max(.1,min(1.0,gap-brake)) if gap>=brake else 1.0
        mapping.append(dict(vehicle_id=v['vehicle_id'],population=v['population'],speed_m_s=speed,
                            gap_projected_m=gap,old_required_m=required,old_margin_m=margin,old_safe=safe,
                            conditional_brake_gap_m=brake,conditional_can_brake=gap>=brake,
                            conditional_stop_offset_m=offset,actual_native_branch='UNKNOWN',red_outcome='UNOBSERVED'))
    check(collections.Counter(v['population'] for v in vehicles)=={'storage':27,'ingress':15}, 'population')
    check([r['vehicle_id'] for r in mapping if not r['old_safe']]==['R_flow.1'], 'sole refusal')
    check(sum(r['conditional_can_brake'] for r in mapping)==42, 'conditional booleans')
    gate=load(GATE)
    with (ROOT/WINDOWS).open(newline='') as f: windows=list(csv.DictReader(f))
    with (ROOT/THIN).open(newline='') as f: thin=list(csv.DictReader(f))
    check(len(thin)==1206 and [int(r['time_begin_s']) for r in thin]==list(range(1206)), 'contiguous derived rows')
    check(len(windows)==len(gate['service_windows'])==6, 'all windows retained')
    fields=['C_observed','C_applied_observed','E_observed','N_observed','command_latency','quantization','physical_shortfall']
    observed=[]
    for i,(row,grow) in enumerate(zip(windows,gate['service_windows'])):
        selected=[r for r in thin if int(row['begin_s'])<=int(r['time_begin_s'])<int(row['end_s'])]
        n=len(selected);observed.append(n)
        check(int(row['observed_steps'])==grow['observed_steps']==n, 'window count')
        check(row['tracking_error']=='' and grow['tracking_error'] is None, 'full-window unknown')
        if not n:
            check(all(row[k]=='' and grow[k] is None for k in fields), 'missing not zero')
        else:
            sums=[sum(float(r[k]) for r in selected) for k in ['C_delta','C_applied_delta','E_delta','N_delta']]
            expected=sums+[sums[0]-sums[1],sums[1]-sums[2],sums[2]-sums[3]]
            check(all(abs(float(row[k])-e)<1e-12 and abs(grow[k]-e)<1e-12 for k,e in zip(fields,expected)), 'partial window independent sum')
    check(observed==[6,0,0,0,0,0] and gate['cycles_completed']==0, 'no completed cycle')
    check(sum(float(r['N_delta']) for r in thin)==1, 'one observed crossing')
    # Independent test runner; monkeypatch raw reads in engineering suite is also tested.
    commands=[]
    for cmd in [[sys.executable,'-m','unittest','discover','-s','tests/candidate_a_a1_contract_20261011_v1','-v'],
                [sys.executable,'scripts/candidate_a_a1_contract_20261011_v1/audit_public.py']]:
        p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        commands.append(dict(argv=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        check(p.returncode==0, 'required offline command failed')
    audit=json.loads(commands[1]['stdout'])
    amap={r['vehicle_id']:r for r in audit['a07_witness_mapping']}
    for r in mapping:
        q=amap[r['vehicle_id']]
        check(abs(q['conditional_native_local_arithmetic']['brake_gap_m']-r['conditional_brake_gap_m'])<1e-12, 'conditional independent match')
        check(q['actual_native_branch']=='UNKNOWN' and q['red_outcome']=='UNOBSERVED', 'no future observation')
        # Independently invert the finite-sum Euler distance by bisection.
        # This is source subformula arithmetic, never a native next speed.
        target=max(0.0,r['gap_projected_m']-r['conditional_stop_offset_m']-.001)
        lo,hi=0.0,100.0
        for _ in range(80):
            speed=(lo+hi)/2; n=int(speed/4.5)
            distance=speed+sum(speed-i*4.5 for i in range(1,n+1))
            if distance>target:hi=speed
            else:lo=speed
        scalar=q['conditional_native_local_arithmetic']['scalar_euler_stop_speed_before_caps_m_s']
        check(abs(scalar-(lo+hi)/2)<1e-10,'independent scalar inverse')
        r['conditional_stop_speed_independent_inverse_m_s']=(lo+hi)/2
    check(audit['actual_native_branches_determined']==0 and not audit['full_a1_eligibility_proven'], 'bounded conclusion')
    # Challenge finite extreme arithmetic, independent of engineering test list.
    sys.path.insert(0,str(ROOT/'scripts/candidate_a_a1_contract_20261011_v1'))
    from contract import diagnostic_decision, brake_gap_euler, maximum_safe_stop_speed_euler
    spec=importlib.util.spec_from_file_location('engineering_tests',ROOT/'tests/candidate_a_a1_contract_20261011_v1/test_contract.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    boundary=[]
    for label,mutation in [('tiny_finite_deceleration',dict(decel_m_s2=5e-324,emergency_decel_m_s2=5e-324,yellow_min_decel_m_s2=5e-324)),
                           ('huge_finite_speed',dict(speed_m_s=1e200)),('largest_finite_speed',dict(speed_m_s=1e308)),
                           ('native_integer_domain_unbound',dict(speed_m_s=1e11))]:
        st=module.fixture();st['vehicles'][0].update(mutation)
        try:
            value=diagnostic_decision(st);ok=value['decision']=='UNKNOWN'
            boundary.append(dict(case=label,result=value,expected='UNKNOWN',pass_=ok))
        except Exception as exc:
            boundary.append(dict(case=label,exception=type(exc).__name__,message=str(exc),expected='UNKNOWN',pass_=False))
    for label,fn,args in [('tiny_decel_brake',brake_gap_euler,(1,5e-324)),('huge_brake',brake_gap_euler,(1e200,4.5)),
                        ('huge_stop_gap',maximum_safe_stop_speed_euler,(1e308,4.5)),
                        ('native_integer_conversion_domain',brake_gap_euler,(1e11,4.5))]:
        expected='ValueError' if label=='native_integer_conversion_domain' else 'finite_or_ValueError'
        try:
            value=fn(*args);ok=math.isfinite(value) and label!='native_integer_conversion_domain'
            boundary.append(dict(case=label,result=value if ok else str(value),expected=expected,pass_=ok))
        except ValueError:
            boundary.append(dict(case=label,exception='ValueError',expected=expected,pass_=True))
        except Exception as exc:
            boundary.append(dict(case=label,exception=type(exc).__name__,message=str(exc),expected=expected,pass_=False))
    # The V3 receipt derives a portable signed-int domain, not native bit width.
    # At 32766 steps, steps+1 is guaranteed representable (<=32767).
    # At 32767 steps, that addition is not guaranteed across implementations.
    for count in [32766,32767]:
        try:
            value=brake_gap_euler(4.5*count,4.5)
            expected_distance=4.5*count*(count-1)/2
            ok=count==32766 and math.isfinite(value) and value==expected_distance
            boundary.append(dict(case='portable_integer_boundary_'+str(count),result=value,
                                 expected='finite' if count==32766 else 'ValueError',pass_=ok))
        except ValueError:
            boundary.append(dict(case='portable_integer_boundary_'+str(count),exception='ValueError',
                                 expected='finite' if count==32766 else 'ValueError',pass_=count==32767))
    return dict(status='PASS' if all(r['pass_'] for r in boundary) else 'REQUIRES_NUMERIC_REPAIR',
                classification='EXPLORATORY_OFFLINE_EVIDENCE_INTEGRITY_NOT_SAFETY_QUALIFICATION',
                protected_checked=536,input_binding_path=binding_path,input_sha256=inputs,source_commit=excerpts['commit'],
                source_excerpts_verified=len(excerpts['excerpts']),whole_remote_sources_reverified=False,
                witness_count=42,populations={'storage':27,'ingress':15},mapping=mapping,
                conditional_can_brake=42,actual_native_branches_determined=0,
                actual_native_branches_basis='Recorded state omits DriveProcessItem/action/device/receiver joint inputs; conditional algebra cannot select complete native branch. Conservative sufficient interval proof may substitute if independently derived later.',
                service_observed_steps=observed,derived_phase_rows=1206,completed_cycles=0,
                ignored_raw_reads=0,clean_checkout_gate='PENDING_PARENT_DELIVERED_COMMIT_CHECK',
                commands=commands,independent_numeric_boundary=boundary,
                independent_script_sha256=sha(Path(__file__)),python=sys.version,
                current_STOP3='PRESERVED',A1_A2='UNVERIFIED',rate_900='NOT_TESTED',execution='HOLD')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    result=run();out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:result[k] for k in ['status','protected_checked','witness_count','service_observed_steps','actual_native_branches_determined']}))
