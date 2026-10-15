"""Dormant, source-scale stopping observation; not a numerical-cause proof.

Only an exact future authority may enable the runtime seam. Pure offline
classification does not authorize motion. Legacy peaks/reasons are retained.
"""
import math
import re
import hashlib
import json
from pathlib import Path
from src.candidate_a_unified_alinea_20261013.numeric_stop import read_vehicle_state
from src.candidate_a_natural_service_20261015.current_gap_scope import current_following

CONTRACT = 'FIRST_YELLOW_SOURCE_SCALE_OBSERVATION_V1'
SOURCE = 'fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
EPS_M = .001
TOL = 1e-6
STORAGE = 'ramp_storage_0'
INGRESS = ':urban_diverge_1_0'
LENGTH = 204.49
RECEIVER_LANES = (':ramp_mid_0_0', 'ramp_accel_0', ':freeway_merge_2_0',
                  'merge_section_0', 'merge_section_1', 'merge_section_2')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_authority(authority):
    need(isinstance(authority, dict) and authority.get('enabled') is True and
         authority.get('contract') == CONTRACT and authority.get('source_commit') == SOURCE and
         authority.get('status') == 'EXACT_ACCEPTANCE_CONTRACT_AUTHORITY_VERIFIED' and
         authority.get('configured_model') == 'Krauss' and
         authority.get('configured_Euler_dt_s') == 1 and
         authority.get('no_model_or_JM_override') is True and
         isinstance(authority.get('run_id'), str) and bool(authority['run_id']) and
         all(isinstance(authority.get(k), str) and re.fullmatch('[a-f0-9]{64}', authority[k])
             for k in ('approval_sha256', 'execution_card_sha256')),
         'ACCEPTANCE_CONTRACT_NOT_AUTHORIZED')
    return dict(authority)


def runtime_authority(card, card_path, release, root):
    """An exact direct approval, never a proposal or the old numeric license."""
    proposal = card['spec'].get('safety_acceptance_contract')
    if proposal is None:
        return None
    need(proposal['policy'] == CONTRACT and proposal['status'] == 'PROPOSED_DEFAULT_INACTIVE' and
         proposal['configured_model'] == 'Krauss' and proposal['configured_Euler_dt_s'] == 1 and
         proposal['source_commit'] == SOURCE and proposal['no_model_or_JM_override'] is True,
         'ACCEPTANCE_PROPOSAL_DRIFT')
    bound = release['direct_execution_authority']
    path = Path(root)/bound['path']
    approval_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    need(approval_hash == bound['sha256'], 'ACCEPTANCE_APPROVAL_HASH_DRIFT')
    approval = json.loads(path.read_text())
    card_hash = hashlib.sha256(Path(card_path).read_bytes()).hexdigest()
    need(approval['status'] == 'DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION' and
         approval['run_id'] == card['spec']['run_id'] and approval['card_sha256'] == card_hash and
         approval.get('acceptance_contract_approved') == CONTRACT and
         approval.get('accuracy_criteria_approved') == card['spec']['accuracy_acceptance_contract']['policy'] and
         approval.get('acceptance_standard_sha256') == proposal['standard_sha256'] and
         approval.get('additional_exact_single_start_approved') is True,
         'ACCEPTANCE_EXACT_CONTRACT_AND_START_NOT_APPROVED')
    return validate_authority(dict(enabled=True,contract=CONTRACT,source_commit=SOURCE,
        status='EXACT_ACCEPTANCE_CONTRACT_AUTHORITY_VERIFIED',configured_model='Krauss',
        configured_Euler_dt_s=1,no_model_or_JM_override=True,run_id=card['spec']['run_id'],
        approval_sha256=approval_hash,execution_card_sha256=card_hash))


def observe_frame(conn, time_s, queries=None):
    """Fresh external state; no advance/setter or private-branch inference."""
    need(conn.simulation.getTime() == time_s, 'ACCEPTANCE_FRAME_TIME_UNKNOWN')
    world = tuple(conn.vehicle.getIDList())
    need(len(world) == len(set(world)), 'ACCEPTANCE_WORLD_IDS_UNKNOWN')
    # Full local population, including the upstream ingress, binds the nearest
    # physical follower. Other-world IDs remain visible, not projected here.
    lanes = {lane: list(conn.lane.getLastStepVehicleIDs(lane))
             for lane in (STORAGE, INGRESS)}
    states = {v: read_vehicle_state(conn, v, time_s)
              for v in sorted(set(lanes[STORAGE] + lanes[INGRESS]))}
    need(set(states) <= set(world), 'ACCEPTANCE_LOCAL_WORLD_UNKNOWN')
    for lane, ids in lanes.items():
        need(len(ids) == len(set(ids)) and
             {v for v in world if conn.vehicle.getLaneID(v) == lane} == set(ids),
             'ACCEPTANCE_LOCAL_POPULATION_UNKNOWN')
        need(all(states[v]['lane_id'] == lane for v in ids), 'ACCEPTANCE_LOCAL_LANE_UNKNOWN')
    supplied = queries or {}
    following = {v: supplied[v] if v in supplied else
                 current_following(conn, v, time_s, allow_clear=True, role='ENTRY_AFTER')
                 for v in lanes[STORAGE]}
    # Native leader geometry is recorded explicitly even when the reference
    # query passes and its passive annotation has no geometry extension.
    leaders = {}
    for vid, q in following.items():
        lead = q.get('leader_id')
        if lead:
            need(lead in world, 'ACCEPTANCE_LEADER_ID_UNKNOWN')
            leaders[vid] = read_vehicle_state(conn, lead, time_s)
    need(conn.simulation.getTime() == time_s, 'ACCEPTANCE_FRAME_TIME_DRIFT')
    return dict(time_s=time_s, world_ids=sorted(world), lane_ids=lanes,
                states=states, following=following, leaders=leaders,
                storage_length_m=conn.lane.getLength(STORAGE),
                ingress_length_m=conn.lane.getLength(INGRESS),
                coverage='FRESH_COMPLETE_STORAGE_INGRESS_AND_NATIVE_LEADER')


def receiver_domain(conn, time_s, terminal_before, receiver):
    """Finite observed population, not an external-cause or clear certificate."""
    need(conn.simulation.getTime() == time_s, 'RECEIVER_DOMAIN_TIME_UNKNOWN')
    geometry = {lane:conn.lane.getLength(lane) for lane in RECEIVER_LANES}
    need(all(finite(v) and v > 0 for v in geometry.values()), 'RECEIVER_DOMAIN_GEOMETRY_UNKNOWN')
    lanes = {lane:sorted(conn.lane.getLastStepVehicleIDs(lane)) for lane in RECEIVER_LANES}
    for lane, ids in lanes.items():
        need(len(ids) == len(set(ids)) and set(ids) ==
             {v for v,x in terminal_before.items() if x['lane_id'] == lane},
             'RECEIVER_DOMAIN_POPULATION_UNKNOWN')
    ids = {v for group in lanes.values() for v in group}
    need(conn.simulation.getTime() == time_s, 'RECEIVER_DOMAIN_TIME_DRIFT')
    return dict(time_s=time_s,scope='FRESH_COMPLETE_FIXED_RECEIVER_LANES',
        geometry_m=geometry,ids_by_lane=lanes,
        vehicles={v:terminal_before[v] for v in sorted(ids)},prospective_receiver=receiver,
        cause='UNESTABLISHED',policy_independence='NOT_ESTABLISHED',
        clear_beyond_finite_domain=False,native_safety_proven=False)


def _neighbors(frame, vid):
    need(frame['coverage'] == 'FRESH_COMPLETE_STORAGE_INGRESS_AND_NATIVE_LEADER' and
         frame['storage_length_m'] == LENGTH and frame['ingress_length_m'] == 113.08,
         'NEIGHBOR_COVERAGE_UNKNOWN')
    state = frame['states'][vid]
    candidates = []
    for other, x in frame['states'].items():
        if other == vid:
            continue
        station = x['position_m'] - (113.08 if x['lane_id'] == INGRESS else 0)
        need(finite(station) and finite(x['length_m']) and x['length_m'] > 0,
             'NEIGHBOR_GEOMETRY_UNKNOWN')
        if station <= state['position_m']:
            candidates.append((station, other, x))
    witness = dict(follower_id=None, follower_bumper_gap_m=None,
                   follower_gap_excluding_minGap_m=None, leader_id=None,
                   leader_bumper_gap_m=None, leader_gap_excluding_minGap_m=None,
                   physical_overlap=False, minGap_infringement=False,
                   absence_scope='COMPLETE_STORAGE_AND_INGRESS_TO_KNOWN_BOUNDARY')
    if candidates:
        station, other, follower = max(candidates)
        gap = state['position_m'] - state['length_m'] - station
        min_gap = follower['dynamics']['min_gap']
        need(finite(min_gap) and min_gap >= 0, 'FOLLOWER_MIN_GAP_UNKNOWN')
        witness.update(follower_id=other, follower_bumper_gap_m=gap,
                       follower_gap_excluding_minGap_m=gap-min_gap)
    q = frame['following'][vid]
    need(q['time_s'] == frame['time_s'] and q['vehicle_id'] == vid,
         'CURRENT_QUERY_ID_TIME_UNKNOWN')
    if q.get('leader_id'):
        gap = q['gap_excluding_minGap_m']
        min_gap = state['dynamics']['min_gap']
        need(finite(gap) and finite(min_gap), 'LEADER_GAP_UNKNOWN')
        lead = frame['leaders'][vid]
        need(lead['vehicle_id'] == q['leader_id'] and lead['lane_id'] == q['leader_lane_id'],
             'LEADER_STATE_UNKNOWN')
        geometry = q['path_geometry_m']; offset = 0; offsets = {}
        for lane in ('ramp_storage_0', ':ramp_mid_0_0', 'ramp_accel_0', ':freeway_merge_2_0', 'merge_section_0'):
            offsets[lane] = offset
            offset += geometry[lane]
        offsets['merge_section_1'] = offsets['merge_section_2'] = offsets['merge_section_0']
        actual_gap = offsets[lead['lane_id']]+lead['position_m']-lead['length_m']-state['position_m']-min_gap
        need(finite(actual_gap) and abs(actual_gap-gap) <= 1e-8, 'LEADER_PATH_GAP_UNKNOWN')
        witness.update(leader_id=q['leader_id'], leader_bumper_gap_m=gap+min_gap,
                       leader_gap_excluding_minGap_m=gap)
    else:
        need(q['status'] == 'CLEAR_WITHIN_OBSERVED_LOOKAHEAD', 'LEADER_ABSENCE_UNKNOWN')
        need(not any(x['lane_id'] == STORAGE and x['position_m'] > state['position_m']
                     for v,x in frame['states'].items() if v != vid), 'LOCAL_LEADER_ABSENCE_MISMATCH')
    bumper = [witness[k] for k in ('leader_bumper_gap_m','follower_bumper_gap_m') if witness[k] is not None]
    net = [witness[k] for k in ('leader_gap_excluding_minGap_m','follower_gap_excluding_minGap_m') if witness[k] is not None]
    witness['physical_overlap'] = any(x < -TOL for x in bumper)
    witness['minGap_infringement'] = any(x < -TOL for x in net)
    need(not witness['physical_overlap'], 'PHYSICAL_BUMPER_OVERLAP')
    need(not witness['minGap_infringement'], 'MIN_GAP_INFRINGEMENT')
    return witness


def classify(evidence):
    """Pure proposal classifier. A compatible result is never motion authority."""
    out = dict(contract=CONTRACT, classification='OUTSIDE_APPROVED_DIAGNOSTIC_SCOPE_STOP',
               decision='STOP', actual_branch_identified=False, native_safety_proven=False,
               legacy_strict_FAIL_retained=True, evidence=evidence)
    try:
        e = evidence; vid = e['vehicle_id']; before = e['before']; after = e['after']
        need(e['dt_s'] == 1 and e['first_yellow'] is True and
             e['motion'] == 'y' and e['signal_binding'] == 'BOUND_BEFORE_LEDGER' and
             e['entered_link'] is False and e['body_coverage_complete'] is True,
             'STOPPING_CONTEXT_UNKNOWN_OR_OUTSIDE_SCOPE')
        need(e['hard_reasons'] == [] and e['native_warning_text'] == '' and
             set(e['native_event_counters']) == {'colliding_vehicles','starting_teleports','ending_teleports'} and
             all(type(x) is int and x == 0 for x in e['native_event_counters'].values()),
             'COEXISTING_HARD_RISK_OR_UNKNOWN')
        x = before['states'][vid]; y = after['states'][vid]
        need(before['time_s'] + 1 == after['time_s'] and
             x['lane_id'] == y['lane_id'] == STORAGE and
             x['type_id'] == y['type_id'] == 'technical_passenger' and
             x['route'] == y['route'] and x['speed_mode'] == y['speed_mode'] == 31 and
             x['lane_change_mode'] == y['lane_change_mode'] == 1621,
             'MODEL_IDENTITY_OR_LOCATION_UNKNOWN')
        dynamics = dict(accel=2.6,decel=4.5,emergency_decel=9.,tau=1.,action_step=1.,
                        sigma=.5,max_speed=55.55555555555556,min_gap=2.5)
        need(all(set(z['dynamics']) == set(dynamics) and all(finite(z['dynamics'][k]) and
             abs(z['dynamics'][k]-v) <= 1e-8 for k,v in dynamics.items()) for z in (x,y)),
             'EFFECTIVE_DYNAMICS_UNKNOWN')
        v = x['speed_m_s']; vn = y['speed_m_s']; b = x['dynamics']['decel']
        a = e['acceleration_m_s2']; delta = e['delta_m_s2']
        need(all(finite(z) for z in (v,vn,a,delta,x['position_m'],y['position_m'])) and
             0 <= x['position_m'] < LENGTH and 0 <= y['position_m'] < LENGTH and vn >= 0 and
             abs(a-delta) <= TOL and abs(delta-(vn-v)) <= TOL,
             'ACCELERATION_OR_POSITION_UNKNOWN')
        need(TOL < -a-b <= EPS_M+TOL and b+EPS_M < v < 2*b,
             'OUTSIDE_SOURCE_SCALE_OR_ONE_STEP_DOMAIN')
        brake_gap = v-b
        offset = LENGTH-x['position_m']-brake_gap
        need(.1 <= offset <= 1., 'OUTSIDE_BOUND_STOP_OFFSET_CONTEXT')
        predicted = brake_gap-EPS_M
        need(abs(predicted-vn) <= TOL and abs(y['position_m']-x['position_m']-vn) <= TOL,
             'EXTERNAL_N0_PATTERN_NOT_COMPATIBLE')
        neighbors = {'before':_neighbors(before,vid),'after':_neighbors(after,vid)}
        out.update(classification='NUMERICAL_SCALE_COMPATIBLE',
                   decision='ONE_UNCHANGED_STEP_FOLLOWUP_REQUIRED',neighbors=neighbors,
                   arithmetic=dict(eps_distance_m=EPS_M,dt_s=1,excess_m_s2=-a-b,
                       inferred_stop_offset_m=offset,predicted_speed_m_s=predicted,
                       private_stopDist_observed=False),reason='SOURCE_SCALE_AND_EXTERNAL_CONTEXT_ONLY')
    except (KeyError,ValueError,TypeError,OverflowError) as exc:
        out['reason'] = type(exc).__name__+':'+str(exc)
    return out


def followup(frame, vehicle_ids, braking, hard_reasons, warning_text):
    """One observed step closes an episode; it cannot renew an exception."""
    out = dict(contract=CONTRACT,classification='FOLLOWUP_UNKNOWN_OR_HARD_STOP',decision='STOP')
    try:
        need(not hard_reasons and warning_text == '', 'FOLLOWUP_HARD_RISK_OR_EXCESS')
        for vid in vehicle_ids:
            need(vid in frame['states'], 'FOLLOWUP_VEHICLE_NOT_OBSERVED')
            _neighbors(frame,vid)
            need(vid in braking['actual_acceleration_m_s2'] and
                 finite(braking['actual_acceleration_m_s2'][vid]) and
                 braking['actual_acceleration_m_s2'][vid] >= -4.5-TOL,
                 'FOLLOWUP_ACCELERATION_UNKNOWN_OR_EXCESS')
        out.update(classification='FOLLOWUP_CLOSED_OBSERVED',decision='CLOSED',
                   vehicle_ids=list(vehicle_ids),frame=frame,native_safety_proven=False)
    except (KeyError,ValueError,TypeError,OverflowError) as exc:
        out['reason'] = type(exc).__name__+':'+str(exc)
    return out
