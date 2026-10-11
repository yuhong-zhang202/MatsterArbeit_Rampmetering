"""Read/reconcile-only isolated diagnostic seam. No launch, advance or setters.

A future authorized bridge must separately supply complete native observations.
Post-step stops detect anomalies after a step, not prevent that step's danger.
"""
from dataclasses import asdict
import math
from src.candidate_a_qualification_20261008.actor import CycleLedger, PhaseEnvelope, motion_phase, crossing_records
from src.candidate_a_qualification_20261008.safety import red_transition_witness, assert_ingress_and_crossing_coverage

TLS = 'ramp_mid'
STORAGE = 'ramp_storage_0'
INGRESS = ':urban_diverge_1_0'
INTERNAL = ':ramp_mid_0_0'
ROUTES = {
    'M': ('main_up', 'merge_section', 'main_down'),
    'R': ('urban_in', 'shared_approach', 'ramp_storage', 'ramp_accel', 'merge_section', 'main_down'),
    'U': ('urban_in', 'shared_approach', 'urban_out'),
    'X': ('cross_in', 'cross_out'),
}
PROFILE = 'NATIVE_PHASE_DIAGNOSTIC_SHADOW_ENVELOPE_PREPARATION_ONLY'


class DiagnosticStop(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise DiagnosticStop(reason)


def identity(conn, vid):
    require(isinstance(vid, str) and vid and vid.split('_', 1)[0] in ROUTES, 'UNKNOWN_POPULATION')
    role = vid.split('_', 1)[0]
    require(conn.vehicle.getTypeID(vid) == 'technical_passenger', 'UNKNOWN_TYPE')
    require(tuple(conn.vehicle.getRoute(vid)) == ROUTES[role], 'UNKNOWN_ROUTE')
    require(conn.vehicle.getSpeedMode(vid) == 31 and conn.vehicle.getLaneChangeMode(vid) == 1621, 'UNKNOWN_MODES')
    for getter, value in [('getAccel',2.6),('getDecel',4.5),('getEmergencyDecel',9.0),('getTau',1.0),('getActionStepLength',1.0),('getImperfection',.5),('getMaxSpeed',55.55555555555556)]:
        observed = getattr(conn.vehicle,getter)(vid)
        require(math.isfinite(observed) and abs(observed-value) <= 1e-8, 'UNKNOWN_EFFECTIVE_DYNAMICS')
    return role


def inventory(conn):
    ids = tuple(conn.vehicle.getIDList())
    require(len(set(ids)) == len(ids), 'DUPLICATE_WORLD_ID')
    current = {}
    for vid in ids:
        role = identity(conn, vid)
        speed = conn.vehicle.getSpeed(vid)
        require(math.isfinite(speed) and 0 <= speed <= 55.55555555555556, 'UNKNOWN_WORLD_SPEED')
        lane_id = conn.vehicle.getLaneID(vid)
        require(isinstance(lane_id,str) and lane_id, 'UNKNOWN_CURRENT_LANE')
        current[vid] = {'role': role, 'speed_m_s': speed, 'lane_id': lane_id}
    loaded = tuple(conn.vehicle.getLoadedIDList())
    pending = tuple(conn.simulation.getPendingVehicles())
    require(len(set(loaded)) == len(loaded) and len(set(pending)) == len(pending), 'DUPLICATE_LOADED_PENDING')
    for vid in set(loaded) | set(pending):
        identity(conn, vid)
    return current, loaded, pending


class StepAdapter:
    """Preparation seam only: callers observe/advance externally; we never do."""
    def __init__(self, observe):
        self.observe = observe  # Future bridge binds exact protected worker.observe.
        self.envelope = PhaseEnvelope()
        self.ledger = CycleLedger(1200, self.envelope)
        self.last_end = None
        self.last_completed = None
        self.pending = None
        self.previous_motion = None
        self.crossed = set()
        self.paused = False
        self.receipts = []

    def prepare_step(self, conn, time_s):
        require(type(time_s) is int and 0 <= time_s < 1272, 'TIME_OUTSIDE_PROPOSED_CAP')
        require(not self.paused and self.pending is None, 'PAUSED_OR_UNRECONCILED_STEP')
        require(self.last_end is None or time_s == self.last_end, 'NONSEQUENTIAL_STEP')
        require(conn.simulation.getTime() == time_s, 'SOURCE_TIME_MISMATCH')
        require(conn.trafficlight.getControlledLinks(TLS) == ((('ramp_storage_0', 'ramp_accel_0', INTERNAL),),), 'LINK_IDENTITY')
        for lane, length in [(STORAGE, 204.49), (INGRESS, 113.08), (INTERNAL, 81.98)]:
            require(abs(conn.lane.getLength(lane) - length) <= 1e-8, 'GEOMETRY_DRIFT')
        assert_ingress_and_crossing_coverage(55.55555555555556, 2.6)
        world, loaded, pending_ids = inventory(conn)
        vehicles, ids, internal, receiver = self.observe(conn)
        require(type(receiver.get('available')) is bool, 'UNKNOWN_RECEIVER')
        for v in vehicles:
            v.validate()
            require(v.vehicle_id in world and world[v.vehicle_id]['role'] == 'R', 'UNBOUND_LOCAL_ID')
            require(abs(v.speed_m_s - world[v.vehicle_id]['speed_m_s']) <= 1e-8, 'INCONSISTENT_LOCAL_SPEED')
        local = {v.vehicle_id for v in vehicles}
        require(len(local) == len(vehicles) and set(ids[STORAGE]) | set(ids[INGRESS]) == local, 'LOCAL_COVERAGE_MISMATCH')
        require(set(ids[STORAGE]) == set(conn.lane.getLastStepVehicleIDs(STORAGE)) and set(ids[INGRESS]) == set(conn.lane.getLastStepVehicleIDs(INGRESS)), 'STALE_LANE_INVENTORY')
        require(set(internal) == set(conn.lane.getLastStepVehicleIDs(INTERNAL)), 'STALE_INTERNAL_INVENTORY')
        require(set(internal) <= world.keys() and all(world[v]['role'] == 'R' for v in internal), 'UNKNOWN_INTERNAL_ID')
        for lane, expected_ids in [(STORAGE,set(ids[STORAGE])),(INGRESS,set(ids[INGRESS])),(INTERNAL,set(internal))]:
            require({v for v,w in world.items() if w['lane_id']==lane} == expected_ids, 'WORLD_LOCAL_LANE_COVERAGE_MISMATCH')
        program = conn.trafficlight.getProgram(TLS)
        phase = conn.trafficlight.getPhase(TLS)
        state = conn.trafficlight.getRedYellowGreenState(TLS)
        nxt = conn.trafficlight.getNextSwitch(TLS)
        cycle = None
        if time_s >= 1200:
            new, cycle = self.ledger.begin_step(time_s, 300)
            # This adapter emits no green setter; a future bridge must prepare
            # the declared official program before this observation boundary.
            require(program == 'CA_C24', 'PROGRAM_IDENTITY')
            if new:
                require(phase == 0 and state == 'G' and receiver['available'], 'GREEN_START_NOT_PREPARED_OR_RECEIVER_DENIED')
                self.ledger.mark_cycle_start(True)
            idx, motion = motion_phase(phase, state, nxt, time_s, self.envelope.phases(24))
            require(motion == self.envelope.state_at(time_s-cycle['begin_s'], 24, True), 'PHASE_SCHEDULE_MISMATCH')
        elif time_s >= 600:
            require(program == 'CA_C8', 'HOLD_PROGRAM_IDENTITY')
            idx, motion = motion_phase(phase, state, nxt, time_s, self.envelope.phases(8))
            require(motion == ('y' if time_s < 603 else 'r'), 'HOLD_PHASE_MISMATCH')
        else:
            require(program == 'A_OPEN' and type(phase) is int and phase == 0 and state == 'G', 'OPEN_PHASE_MISMATCH')
            motion = 'G'
        require(receiver['available'] or motion != 'G', 'GREEN_RECEIVER_DENIED')
        entering_red = motion == 'r' and (self.previous_motion != 'r' or state == 'y')
        shadow = red_transition_witness(vehicles) if entering_red else None
        self.pending = {'time_s': time_s, 'world': world, 'loaded': loaded, 'pending_ids': pending_ids,
                        'storage': set(ids[STORAGE]), 'internal': set(internal), 'cycle_id': cycle['cycle_id'] if cycle else -1,
                        'program': program, 'motion_phase': idx if time_s >= 600 else 0,
                        'motion': motion, 'entering_red': entering_red, 'shadow_envelope': shadow,
                        'vehicle_states': [asdict(v) for v in vehicles], 'receiver': receiver}
        return {'status': 'OBSERVATIONS_BOUND_NOT_PROSPECTIVE_SAFETY', 'profile': PROFILE,
                'motion': motion, 'shadow_envelope': shadow, 'step_advance_performed': False}

    def reconcile_step(self, conn, warning_observation):
        require(self.pending is not None, 'NO_PRESTEP_OBSERVATION')
        p = self.pending
        row = {'time_begin_s': p['time_s'], 'observed_time_s': conn.simulation.getTime(),
               'status': 'UNRECONCILED_ADVANCED_PREFIX', 'accounting_complete': False,
               'shadow_envelope': p['shadow_envelope']}
        self.receipts.append(row)
        require(conn.simulation.getTime() == p['time_s'] + 1, 'POST_TIME_MISMATCH')
        self.last_completed = p['time_s']+1
        row['time_end_s'] = self.last_completed
        # Schema checks do not verify actual logger completeness. The missing
        # authorized bridge must supply/prove native interval provenance.
        require(isinstance(warning_observation, dict), 'MISSING_NATIVE_WARNING_OBSERVATION')
        require(warning_observation.get('time_begin_s') == p['time_s'] and warning_observation.get('time_end_s') == self.last_completed, 'WARNING_TIME_MISMATCH')
        require(warning_observation.get('coverage') == 'CALLER_DECLARED_INTERVAL' and isinstance(warning_observation.get('source'), str) and warning_observation['source'], 'WARNING_SOURCE_MISSING')
        require(type(warning_observation.get('byte_start')) is int and type(warning_observation.get('byte_end')) is int and 0 <= warning_observation['byte_start'] <= warning_observation['byte_end'], 'WARNING_OFFSET_MISSING')
        require(isinstance(warning_observation.get('text'), str), 'WARNING_TEXT_MISSING')
        native_warning_text = warning_observation['text']
        row['warning_observation'] = warning_observation
        world, _, _ = inventory(conn)
        before, after = set(p['world']), set(world)
        arrived = set(conn.simulation.getArrivedIDList())
        departed = set(conn.simulation.getDepartedIDList())
        require(before-after <= arrived and after-before <= departed, 'UNRECONCILED_WORLD_ID_CHANGE')
        recs = crossing_records(p['storage'], p['internal'], set(conn.lane.getLastStepVehicleIDs(INTERNAL)),
                                p['time_s'], p['cycle_id'], p['motion'])
        require(not self.crossed.intersection(r['vehicle_id'] for r in recs), 'DUPLICATE_CROSSING')
        self.crossed.update(r['vehicle_id'] for r in recs)
        if p['cycle_id'] >= 0:
            self.ledger.end_step(p['time_s']+1, [r['vehicle_id'] for r in recs], p['motion'])
        self.last_end = p['time_s']+1
        self.previous_motion = p['motion']
        self.pending = None
        row.update(time_end_s=self.last_end, motion=p['motion'], actual_crossings=recs,
                   accounting=self.ledger.accounting(), accounting_complete=True,
                   status='RECONCILED_DIAGNOSTIC_ONLY')
        errors = []
        if conn.trafficlight.getRedYellowGreenState(TLS) != p['motion'] or conn.trafficlight.getPhase(TLS) != p['motion_phase']: errors.append('PHASE_MISMATCH')
        if conn.trafficlight.getProgram(TLS) != p['program']: errors.append('PROGRAM_MISMATCH')
        if conn.trafficlight.getControlledLinks(TLS) != ((('ramp_storage_0','ramp_accel_0',INTERNAL),),): errors.append('POST_LINK_MISMATCH')
        try:
            _, _, post_internal, post_receiver = self.observe(conn)
            if type(post_receiver.get('available')) is not bool: errors.append('UNKNOWN_POST_RECEIVER')
            if post_receiver.get('available') is False and p['motion'] == 'G': errors.append('POST_GREEN_RECEIVER_DENIED')
            if set(post_internal) != set(conn.lane.getLastStepVehicleIDs(INTERNAL)): errors.append('POST_INTERNAL_COVERAGE_MISMATCH')
            row['post_receiver'] = post_receiver
        except Exception as exc:
            errors.append('POST_OBSERVATION_UNKNOWN:'+type(exc).__name__)
        if conn.simulation.getCollidingVehiclesNumber() or conn.simulation.getStartingTeleportNumber() or conn.simulation.getEndingTeleportNumber(): errors.append('COLLISION_OR_TELEPORT')
        if p['motion'] == 'r' and recs: errors.append('RED_CROSSING')
        for vid in before & after:
            if world[vid]['speed_m_s']-p['world'][vid]['speed_m_s'] < -4.5-1e-6: errors.append('ORDINARY_BRAKING_EXCEEDED:'+vid)
        for vid in after:
            a = conn.vehicle.getAcceleration(vid)
            if not math.isfinite(a) or a < -4.5-1e-6: errors.append('UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+vid)
        if any(s in native_warning_text.lower() for s in ('emergency braking','emergency stop','collision','teleport')): errors.append('NATIVE_WARNING')
        if errors:
            self.paused = True
            row.update(status='STOP_OBSERVED_AFTER_STEP', reasons=errors)
            raise DiagnosticStop(';'.join(errors))
        if p['time_s'] == 1206 or self.last_end >= 1272:
            self.paused = True
            row['status'] = 'MANDATORY_REVIEW_PAUSE_NO_AUTOMATIC_CONTINUATION'
        return row
