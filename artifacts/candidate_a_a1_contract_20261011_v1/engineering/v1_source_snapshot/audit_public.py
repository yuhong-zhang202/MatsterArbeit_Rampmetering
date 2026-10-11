"""Read-only public evidence audit. No raw, network, SUMO or TraCI dependencies."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from contract import SOURCE_COMMIT, old_guard, local_plan_stop, maximum_safe_stop_speed_euler

ROOT=Path(__file__).resolve().parents[2]
ENGINEERING=Path('artifacts/candidate_a_a1_contract_20261011_v1/engineering')
SNAPSHOT=Path('artifacts/candidate_a_qualification_20261008_v1/pr_review/CA_FIXED_R300_S17_A07/outputs/failure_snapshot.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(condition,message):
    if not condition:
        raise ValueError(message)


def audit(root=ROOT):
    bindings=json.loads((root/ENGINEERING/'INPUT_BINDINGS.json').read_text())
    for path,expected in bindings['files'].items():
        checked(not path.startswith('data/raw/'),'raw dependency prohibited')
        checked(sha(root/path)==expected,'input/source hash drift: '+path)
    source=json.loads((root/ENGINEERING/'SOURCE_RECEIPT.json').read_text())
    excerpts=json.loads((root/ENGINEERING/'SOURCE_EXCERPTS.json').read_text())
    checked(source['resolved_commit']==SOURCE_COMMIT==excerpts['commit'],'pinned source mismatch')
    checked(sha(root/source['excerpt_file'])==source['excerpt_file_sha256'],'excerpt hash drift')
    for ex in excerpts['excerpts']:
        checked(hashlib.sha256(ex['text'].encode()).hexdigest()==ex['sha256'],'source excerpt drift')
        checked(len(ex['text'].splitlines())==ex['line_end']-ex['line_start']+1,'physical-line count')
        checked('/'+SOURCE_COMMIT+'/' in ex['url'],'nonpermanent source anchor')
    snapshot=json.loads((root/SNAPSHOT).read_text());state=snapshot['snapshot']
    checked(snapshot['decision_time_s']==snapshot['last_completed_step_s']==snapshot['last_accounted_s']==1206,'prefix timing')
    checked(state['phase_before']==1 and state['state_before']=='y' and state['predicted_motion']=='r' and state['next_switch']==1206,'pending event')
    checked(not state.get('step_advanced',False) and state['phase_api_requests']==[],'refused interval unexecuted')
    states=state['vehicle_states'];witnesses={w['vehicle_id']:w for w in state['red_transition']['witnesses']}
    checked(len(states)==len(witnesses)==42 and len({s['vehicle_id'] for s in states})==42,'42 unique witnesses')
    rows=[]
    for v in states:
        gap=204.49-v['position_m'];old=old_guard(v['speed_m_s'],gap,v['normal_decel_m_s2'])
        w=witnesses[v['vehicle_id']]
        checked(abs(old['required_m']-w['required_normal_red_m'])<1e-12 and abs(old['margin_m']-w['margin_m'])<1e-12 and old['safe']==w['safe'],'old guard mismatch')
        # These are CONDITIONAL source-input projections, not reconstructed
        # full native DriveProcessItems or a future movement calculation.
        proj=local_plan_stop(v['speed_m_s'],gap,0.0,v['normal_decel_m_s2'],9.0,3.0,1.0)
        proj['scalar_euler_stop_speed_before_caps_m_s']=maximum_safe_stop_speed_euler(proj['native_stop_dist_m'],proj['stop_decel_m_s2'])
        rows.append({'vehicle_id':v['vehicle_id'],'population':v['population'],
                     'front_distance_projected_to_controlled_link_m':gap,
                     'speed_m_s':v['speed_m_s'],'old_guard':old,
                     'conditional_native_local_arithmetic':proj,
                     'projection_assumptions':['native seen equals this route-projected gap','lane stopOffset=0',
                       'passenger; decel4.5/emergency9/yellow-min3; jmStoplineGap1; Euler1s',
                       'no rail/reversal/GLOSA/driver/newStopDist/device overrides'],
                     'actual_native_branch':'UNKNOWN','red_outcome':'UNOBSERVED',
                     'missing':['per-vehicle native seen/DriveProcessItem and action status',
                       'runtime effective offsets/devices/JM params/influencer trace',
                       'receiver/leader complete dynamic state and reservations',
                       'finalized speed interval for followers and RNG effects']})
    checked(sum(r['population']=='storage' for r in rows)==27 and sum(r['population']=='ingress' for r in rows)==15,'population')
    unsafe=[r['vehicle_id'] for r in rows if not r['old_guard']['safe']]
    checked(unsafe==['R_flow.1'],'sole old refusal')
    checked(all(r['conditional_native_local_arithmetic']['can_brake_before_stopline'] for r in rows),'conditional brake predicate')
    topology=json.loads((root/ENGINEERING/'STATIC_TOPOLOGY.json').read_text())
    checked(len(topology['controlled_connections'])==1 and 'foes="0"' in topology['ramp_junction'],'static link')
    gate=json.loads((root/'data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_GATE_V3.json').read_text())
    # Preserve authoritative missing-window semantics through upstream audit.
    sys.path.insert(0,str(root/'scripts/candidate_a_safety_contract_20261011_v1'))
    import audit_a07
    upstream=audit_a07.audit()
    checked(upstream['status']=='PASS','upstream committed audit failed')
    return {'status':'PASS','classification':'UNRESOLVED_NEEDS_EVIDENCE',
            'scope':'OFFLINE_PUBLIC_EVIDENCE_AND_CONDITIONAL_SOURCE_SUBPREDICATES',
            'source_commit':SOURCE_COMMIT,'input_files_checked':len(bindings['files']),
            'source_excerpt_count':len(excerpts['excerpts']),'witness_count':42,
            'old_guard_unsafe_ids':unsafe,'conditional_plan_can_brake_count':42,
            'actual_native_branches_determined':0,'refused_red_motion_steps_executed':0,
            'sumo_traci_starts':0,'public_evidence_only':True,
            'independent_raw_phase_reconstruction':False,'full_a1_eligibility_proven':False,
            'a07_a1_decision':'UNKNOWN','runtime_eligible_path_implemented':False,
            'a1_a2_qualified':False,'current_contract_STOP3':'PRESERVED',
            'rate_900':'NOT_TESTED','further_execution':'HOLD',
            'upstream_public_audit':upstream,'a07_witness_mapping':rows}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2,allow_nan=False))
