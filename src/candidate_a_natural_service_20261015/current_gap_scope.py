"""Approved passive reference observation; never prospective green admission.

The original fresh query and every legacy result remain unchanged. Only a
fully bound ordinary observation may continue below that reference. This is
neither a safe-motion certificate nor a claim about unavailable service.
"""
from src.candidate_a_dynamic_minqual_20261015 import receiver_wait as legacy

CONTRACT = 'ORDINARY_NATIVE_REFERENCE_OBSERVATION_V1'
BELOW = 'BELOW_NATIVE_REFERENCE_OBSERVED'
CLEAR = 'CLEAR_WITHIN_OBSERVED_LOOKAHEAD'
WITHIN = 'CURRENT_GAP_OBSERVED_WITHIN_BOUND'
ROLES = ('ONGOING_PRE_RECEIVER', 'POST_RECEIVER', 'ENTRY_BEFORE', 'ENTRY_AFTER')
ACCEPTED = (BELOW, CLEAR, WITHIN)


def _annotate(conn, query, role):
    legacy.require(role in ROLES, 'UNKNOWN_PASSIVE_QUERY_ROLE')
    status = query['status']
    legacy.require(status in (CLEAR, WITHIN, 'STOP_CURRENT_GAP_BOUND_DENIED'),
                   'UNKNOWN_PASSIVE_QUERY_STATUS')
    classification = status
    if status == 'STOP_CURRENT_GAP_BOUND_DENIED':
        # Bind the actual route-distance coordinates as well as the native
        # leader ID/query. Parallel merge lanes share the same path station.
        geo = query['path_geometry_m']
        chain = ('ramp_storage_0', ':ramp_mid_0_0', 'ramp_accel_0', ':freeway_merge_2_0', 'merge_section_0')
        offsets = {}; station = 0
        for lane in chain:
            offsets[lane] = station
            station += geo[lane]
        for lane in ('merge_section_1', 'merge_section_2'):
            offsets[lane] = offsets['merge_section_0']
        leader = query['leader_id']; lane = query['leader_lane_id']
        pos = legacy.number(conn.vehicle.getLanePosition(leader), 'LEADER_POSITION')
        length = legacy.number(conn.vehicle.getLength(leader), 'LEADER_LENGTH', minimum=1e-12)
        legacy.require(pos <= geo[lane], 'LEADER_POSITION_OUTSIDE_LANE')
        gap = (offsets[lane] + pos - length - offsets[query['lane_id']] -
               query['lane_position_m'] - query['min_gap_m'])
        legacy.require(gap >= -1e-9 and abs(gap-query['gap_excluding_minGap_m']) <= 1e-8,
                       'PASSIVE_PATH_DISTANCE_BINDING_MISMATCH')
        query['passive_leader_geometry'] = dict(lane_id=lane, position_m=pos,
            length_m=length, reconstructed_gap_excluding_minGap_m=gap,
            status='BOUND_CURRENT_ROUTE_DISTANCE_NOT_FUTURE_SAFETY')
        classification = BELOW
    query['ordinary_current_gap_observation'] = dict(contract=CONTRACT, role=role,
        time_s=query['time_s'], classification=classification,
        observational_only=True, native_safety_proven=False)
    legacy.require(conn.simulation.getTime() == query['time_s'], 'PASSIVE_QUERY_TIME_DRIFT')
    return query


def current_following(conn, vid, time_s, expected_leader=None, allow_clear=False, *, role):
    query = legacy.current_following(conn, vid, time_s, expected_leader, allow_clear)
    return _annotate(conn, query, role)


def classification(query):
    observation = query.get('ordinary_current_gap_observation', {})
    legacy.require(observation.get('contract') == CONTRACT and
                   observation.get('role') in ROLES and
                   observation.get('time_s') == query.get('time_s') and
                   observation.get('observational_only') is True and
                   observation.get('native_safety_proven') is False,
                   'UNKNOWN_PASSIVE_QUERY_CONTRACT')
    return observation.get('classification')


def classify_receiver(conn, receiver, time_s, *, role):
    result = legacy.classify_receiver(conn, receiver, time_s)
    result['current_gap_responsibility_contract'] = CONTRACT
    result['legacy_decision'] = result['decision']
    if 'current_following' in result:
        query = _annotate(conn, result['current_following'], role)
        if classification(query) == BELOW:
            result['decision'] = BELOW
    return result
