"""Bounded current-state observation policy. No setters or safety certificate."""
import math
from src.candidate_a_native_budget_cycles_20261012.adapter import identity, ROUTES, STORAGE, INTERNAL

LOOKAHEAD_M = 478.67
MARGIN_M = 1.1
PATH_LANES = (INTERNAL, 'ramp_accel_0', ':freeway_merge_2_0', 'merge_section_0', 'merge_section_1', 'merge_section_2')
POLICY = 'ACTUAL_SPEED_FOLLOWING_OBSERVATION_WITH_RETAINED_1_1_M_MARGIN_V1'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def number(value, name, minimum=0):
    require(type(value) in (int,float) and math.isfinite(value) and value>=minimum, 'UNKNOWN_'+name)
    return value


def current_following(conn, vid, time_s, expected_leader=None, allow_clear=False):
    """Read one exact vehicle/leader frame. Empty leader means bounded clear only."""
    require(conn.simulation.getTime()==time_s, 'FOLLOWING_TIME_MISMATCH')
    require(vid in conn.vehicle.getIDList() and identity(conn,vid)=='R', 'UNKNOWN_FOLLOWING_VEHICLE')
    lane=conn.vehicle.getLaneID(vid)
    require(lane in (STORAGE,)+PATH_LANES, 'FOLLOWING_OFF_BOUND_PATH')
    route=tuple(conn.vehicle.getRoute(vid));require(route==ROUTES['R'], 'FOLLOWING_ROUTE_DRIFT')
    geometry={l:number(conn.lane.getLength(l),'PATH_LENGTH',minimum=1e-12) for l in (STORAGE,)+PATH_LANES}
    position=number(conn.vehicle.getLanePosition(vid),'LANE_POSITION')
    require(position<=geometry[lane], 'FOLLOWING_POSITION_OUTSIDE_LANE')
    length=number(conn.vehicle.getLength(vid),'VEHICLE_LENGTH',minimum=1e-12)
    speed=number(conn.vehicle.getSpeed(vid),'ACTUAL_SPEED')
    min_gap=number(conn.vehicle.getMinGap(vid),'MIN_GAP')
    query={'vehicle_id':vid,'lane_id':lane,'time_s':time_s,'route':list(route),'lookahead_m':LOOKAHEAD_M,
        'receiver_path_lanes':list(PATH_LANES),'path_geometry_m':geometry,'actual_speed_m_s':speed,
        'lane_position_m':position,'vehicle_length_m':length,'min_gap_m':min_gap,'speed_mode':conn.vehicle.getSpeedMode(vid),'lane_change_mode':conn.vehicle.getLaneChangeMode(vid),
        'policy':POLICY,'margin_m':MARGIN_M,'future_safety_proven':False}
    raw=conn.vehicle.getLeader(vid,LOOKAHEAD_M)  # This getter is deliberately not cached.
    query['fresh_getLeader_result']=raw
    empty=raw is None or (isinstance(raw,(tuple,list)) and len(raw)==2 and raw[0]=='' and type(raw[1]) in (int,float) and raw[1]==-1)
    if empty:
        require(allow_clear and expected_leader is None, 'UNKNOWN_MISSING_BOUND_LEADER')
        query.update(status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD', actual_secure_gap_m=None, gap_excluding_minGap_m=None,
                     claim_scope='fresh valid native empty result within fixed lookahead and bound route/path, not globally clear')
        return query
    require(isinstance(raw,(tuple,list)) and len(raw)==2 and isinstance(raw[0],str) and raw[0] and raw[0]!=vid, 'UNKNOWN_LEADER_SCHEMA')
    leader,gap=raw;gap=number(gap,'LEADER_GAP')
    require(leader in conn.vehicle.getIDList(), 'UNKNOWN_LEADER_ID')
    identity(conn,leader)
    leader_lane=conn.vehicle.getLaneID(leader)
    require(leader_lane in (STORAGE,)+PATH_LANES,'UNKNOWN_LEADER_LANE')
    if expected_leader is not None:
        require(leader==expected_leader['vehicle_id'] and abs(gap-expected_leader['gap_excluding_minGap_m'])<=1e-8, 'LEADER_FRAME_BINDING_MISMATCH')
    leader_speed=number(conn.vehicle.getSpeed(leader),'LEADER_SPEED')
    emergency=number(conn.vehicle.getEmergencyDecel(leader),'LEADER_EMERGENCY_DECEL',minimum=1e-12)
    args={'vehID':vid,'speed':speed,'leaderSpeed':leader_speed,'leaderMaxDecel':emergency,'leaderID':leader}
    secure=number(conn.vehicle.getSecureGap(**args),'CURRENT_SECURE_GAP')
    bumper_gap=gap+min_gap
    passed=bumper_gap>0 and gap+1e-9>=secure+MARGIN_M
    query.update(leader_id=leader,leader_lane_id=leader_lane,leader_speed_m_s=leader_speed,
        leader_speed_mode=conn.vehicle.getSpeedMode(leader),leader_lane_change_mode=conn.vehicle.getLaneChangeMode(leader),
        getSecureGap_args=args,actual_secure_gap_m=secure,gap_excluding_minGap_m=gap,physical_bumper_gap_m=bumper_gap,
        required_with_margin_m=secure+MARGIN_M,status='CURRENT_GAP_OBSERVED_WITHIN_BOUND' if passed else 'STOP_CURRENT_GAP_BOUND_DENIED')
    return query


def classify_receiver(conn, receiver, time_s):
    """Retain the original prospective denial; never change available to True."""
    require(type(receiver.get('available')) is bool,'UNKNOWN_RECEIVER_BOOLEAN')
    if receiver['available']:
        return {'decision':'READY','prospective_available':True,'time_s':time_s,'policy':POLICY,'future_safety_proven':False}
    vid=receiver.get('front_id');leader=receiver.get('leader')
    require(isinstance(vid,str) and vid and isinstance(leader,dict),'UNKNOWN_WAIT_FRONT_OR_LEADER')
    storage_ids=tuple(conn.lane.getLastStepVehicleIDs(STORAGE))
    require(vid in storage_ids and len(set(storage_ids))==len(storage_ids), 'UNKNOWN_WAIT_STORAGE_FRONT')
    positions={v:number(conn.vehicle.getLanePosition(v),'STORAGE_POSITION') for v in storage_ids}
    require(positions[vid]==max(positions.values()), 'WAIT_FRONT_SELECTION_MISMATCH')
    current=current_following(conn,vid,time_s,expected_leader=leader,allow_clear=False)
    decision='WAIT_NATIVE_FOLLOWING' if current['status']=='CURRENT_GAP_OBSERVED_WITHIN_BOUND' else current['status']
    return {'decision':decision,'prospective_available':False,'original_prospective_receiver':dict(receiver),
        'current_following':current,'time_s':time_s,'policy':POLICY,'future_safety_proven':False}
