"""Read/reconcile-only isolated diagnostic seam. No launch, advance or setters.

A future authorized bridge must separately supply complete native observations.
Post-step stops detect anomalies after a step, not prevent that step's danger.
"""
from dataclasses import asdict
import math
from src.candidate_a_qualification_20261008.actor import CycleLedger, PhaseEnvelope as ProtectedPhaseEnvelope, motion_phase, crossing_records
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
PROFILE = 'NATIVE_PHASE_CURRENT_FOLLOWING_WAIT_DIAGNOSTIC_NOT_QUALIFIED'
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import classify_receiver, current_following
from src.candidate_a_issue12_packet_policy_20261012.policy import Ledger, PROGRAM, PERIOD, MAX_GREEN, YELLOW, yellow_scope
from src.candidate_a_issue12_packet_policy_20261012.body import BodyTracker


class PhaseEnvelope(ProtectedPhaseEnvelope):
    def phases(self, period_s):
        phases = super().phases(period_s)
        return phases[:2] + ((phases[2][0], phases[2][1], 0),)



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
    def __init__(self, observe, command=300):
        self.observe = observe  # Future bridge binds exact protected worker.observe.
        self.envelope = PhaseEnvelope()  # Pre-control holding program only.
        self.ledger = Ledger(command)
        self.command = command
        self.first_controlled_red_begin = None
        self.last_yellow_scope = None
        self.last_end = None
        self.last_completed = None
        self.pending = None
        self.previous_motion = None
        self.crossed = set()
        self.paused = False
        self.checkpoint_pending = False
        self.checkpoint_verified = False
        self.receipts = []
        self.body = BodyTracker()

    def _terminal_call(self, method, *args):
        require(not self.paused, 'TERMINAL_PAUSE_NO_RETRY')
        try:
            return method(*args)
        except Exception as exc:
            self.paused = True
            self.terminal_reason = type(exc).__name__ + ':' + str(exc)
            if self.receipts:
                self.receipts[-1]['terminal_reason'] = self.terminal_reason
                if self.receipts[-1]['status'] != 'STOP_OBSERVED_AFTER_STEP':
                    self.receipts[-1]['status'] = 'STOP_UNKNOWN_NO_CONTINUATION'
            raise

    def prepare_step(self, conn, time_s):
        return self._terminal_call(self._prepare_step, conn, time_s)

    def reconcile_step(self, conn, warning_observation):
        return self._terminal_call(self._reconcile_step, conn, warning_observation)

    def _prepare_step(self, conn, time_s):
        require(type(time_s) is int and 0 <= time_s < 1272, 'TIME_OUTSIDE_PROPOSED_CAP')
        require(not self.paused and self.pending is None, 'PAUSED_OR_UNRECONCILED_STEP')
        require(not self.checkpoint_pending, 'MANDATORY_CHECKPOINT_NOT_RELEASED')
        require(self.first_controlled_red_begin is None or self.checkpoint_verified, 'FIRST_RED_CHECKPOINT_MISSING')
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
            expected_position=conn.vehicle.getLanePosition(v.vehicle_id)-(113.08 if v.population=='ingress' else 0)
            require(abs(v.position_m-expected_position)<=1e-8 and
                    abs(v.length_m-conn.vehicle.getLength(v.vehicle_id))<=1e-8, 'UNBOUND_YELLOW_POSITION_OR_BODY')
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
            new, cycle = self.ledger.begin_step(time_s, self.command)
            require(program == PROGRAM, 'PROGRAM_IDENTITY')
            idx, motion = motion_phase(phase, state, nxt, time_s,
                                      (('G',MAX_GREEN,1),('y',YELLOW,2),('r',2,0)))
            if new:
                require(idx == 0 and motion == 'G' and receiver['available'], 'GREEN_START_NOT_PREPARED_OR_RECEIVER_DENIED')
                require((time_s == 1200 and phase == 0 and state == 'G' and nxt == time_s+MAX_GREEN) or
                        (time_s in range(1200+PERIOD,1272,PERIOD) and phase == 2 and state == 'r' and nxt == time_s),
                        'NATIVE_CYCLE_START_BOUNDARY_MISMATCH')
                self.ledger.mark_cycle_start(True)
            if motion == 'y' and cycle['green_end_s'] is None:
                self.ledger.close_green(time_s, 'MAX_GREEN_DEADLINE')
            require(motion == self.ledger.motion_at(time_s), 'PHASE_SCHEDULE_MISMATCH')
            if motion == 'y' and self.previous_motion != 'y':
                self.last_yellow_scope = yellow_scope(vehicles, time_s)
                require(self.last_yellow_scope['status']=='PASS', 'UNKNOWN_LOCAL_YELLOW_SCOPE')
        elif time_s >= 600:
            require(program == 'CA_C8', 'HOLD_PROGRAM_IDENTITY')
            idx, motion = motion_phase(phase, state, nxt, time_s, self.envelope.phases(8))
            require(motion == ('y' if time_s < 603 else 'r'), 'HOLD_PHASE_MISMATCH')
        else:
            require(program == 'A_OPEN' and type(phase) is int and phase == 0 and state == 'G', 'OPEN_PHASE_MISMATCH')
            motion = 'G'
        native_decision = classify_receiver(conn, receiver, time_s) if motion == 'G' else None
        require(receiver['available'] or motion != 'G' or native_decision['decision'] == 'WAIT_NATIVE_FOLLOWING', 'CURRENT_GAP_BOUND_DENIED')
        entry_before = {vid: current_following(conn, vid, time_s, allow_clear=True) for vid in sorted(ids[STORAGE])} if motion in ('G','y') else {}
        entering_red = motion == 'r' and (self.previous_motion != 'r' or state == 'y')
        shadow = red_transition_witness(vehicles) if entering_red else None
        self.pending = {'time_s': time_s, 'world': world, 'loaded': loaded, 'pending_ids': pending_ids,
                        'storage': set(ids[STORAGE]), 'internal': set(internal), 'cycle_id': cycle['cycle_id'] if cycle else -1,
                        'program': program, 'phase_before': phase, 'state_before': state, 'next_switch_before_s': nxt, 'motion_phase': idx if time_s >= 600 else 0,
                        'motion': motion, 'entering_red': entering_red, 'shadow_envelope': shadow,
                        'vehicle_states': [asdict(v) for v in vehicles], 'receiver': receiver,
                        'yellow_scope':self.last_yellow_scope,
                        'rate_chain':dict(input_origin='FIXED_POLICY_DIAGNOSTIC',r_ALINEA=None,
                            r_final_veh_h=self.command if cycle else None,
                            r_policy_pending_veh_h=self.ledger.step_mapped if cycle else None,
                            r_policy_applied_veh_h=cycle['applied_command_veh_h'] if cycle else None,
                            requested_quota=cycle['requested_quota'] if cycle else None,
                            period_s=PERIOD if cycle else None,
                            cycle_application_delay_s=cycle['application_delay_s'] if cycle else None),
                        'terminal_before':{vid:dict(vehicle_id=vid, time_s=time_s,
                            speed_m_s=w['speed_m_s'], lane_id=w['lane_id'],
                            position_m=conn.vehicle.getLanePosition(vid),
                            length_m=conn.vehicle.getLength(vid),type_id=conn.vehicle.getTypeID(vid),
                            route=list(conn.vehicle.getRoute(vid)),terminal_edge=ROUTES[w['role']][-1],
                            normal_decel_m_s2=conn.vehicle.getDecel(vid),
                            terminal_lane_binding_scope='any actual network lane on bound terminal route edge; legal final lane changes allowed',
                            acceleration_m_s2=(self.receipts[-1]['braking_observation']['actual_acceleration_m_s2'].get(vid)
                                if self.receipts and 'braking_observation' in self.receipts[-1]
                                else conn.vehicle.getAcceleration(vid)),
                            acceleration_scope='same-before-time last-post reading or initial getter')
                            for vid,w in world.items()},
                        'native_receiver_decision': native_decision, 'entry_following_before': entry_before}
        return {'status': 'OBSERVATIONS_BOUND_NOT_PROSPECTIVE_SAFETY', 'profile': PROFILE,
                'motion': motion, 'shadow_envelope': shadow, 'step_advance_performed': False}

    def _reconcile_step(self, conn, warning_observation):
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
        row['post_world'] = world
        row['phase_observation'] = {'phase_before': p['phase_before'], 'state_before': p['state_before'],
            'next_switch_before_s': p['next_switch_before_s'], 'phase_after': conn.trafficlight.getPhase(TLS),
            'state_after': conn.trafficlight.getRedYellowGreenState(TLS), 'next_switch_after_s': conn.trafficlight.getNextSwitch(TLS)}
        arrived = set(conn.simulation.getArrivedIDList())
        departed = set(conn.simulation.getDepartedIDList())
        row['identity_change'] = {'arrived_ids': sorted(arrived), 'departed_ids': sorted(departed),
            'before_only_ids': sorted(before-after), 'after_only_ids': sorted(after-before)}
        require(before-after == arrived and after-before <= departed, 'UNRECONCILED_WORLD_ID_CHANGE_OR_ARRIVAL_COVERAGE')
        row['terminal_arrival_pending'] = [dict(p['terminal_before'][vid],
            time_begin_s=p['time_s'],time_end_s=p['time_s']+1,arrived_id_bound=True,
            status='PENDING_FINAL_TRIPINFO_LAST_MOVEMENT_AUDIT_NOT_ONLINE_COVERED')
            for vid in sorted(before-after)]
        row['yellow_scope'] = p['yellow_scope']
        row['rate_chain'] = p['rate_chain']
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
            if p['motion'] == 'G':
                row['post_native_receiver_decision'] = classify_receiver(conn, post_receiver, self.last_completed)
                if row['post_native_receiver_decision']['decision'] not in ('READY','WAIT_NATIVE_FOLLOWING'):
                    errors.append('POST_CURRENT_GAP_BOUND_DENIED')
            if set(post_internal) != set(conn.lane.getLastStepVehicleIDs(INTERNAL)): errors.append('POST_INTERNAL_COVERAGE_MISMATCH')
            row['post_receiver'] = post_receiver
        except Exception as exc:
            row['post_observation_error'] = {'type':type(exc).__name__, 'reason':str(exc)}
            errors.append('POST_OBSERVATION_UNKNOWN:'+type(exc).__name__+':'+str(exc))
        row['actual_entry_following'] = []
        for record in recs:
            vid = record['vehicle_id']
            bound = {'vehicle_id':vid, 'time_begin_s':p['time_s'], 'time_end_s':self.last_completed,
                'before':p['entry_following_before'].get(vid), 'after':None, 'motion':p['motion']}
            row['actual_entry_following'].append(bound)
            try:
                require(bound['before'] is not None and bound['before']['vehicle_id']==vid, 'UNKNOWN_ENTRY_BEFORE_BINDING')
                allowed = {'CURRENT_GAP_OBSERVED_WITHIN_BOUND','CLEAR_WITHIN_OBSERVED_LOOKAHEAD'}
                before_status = bound['before'].get('status')
                if before_status not in allowed:
                    reason = 'ACTUAL_ENTRY_BEFORE_CURRENT_GAP_BOUND_DENIED' if before_status == 'STOP_CURRENT_GAP_BOUND_DENIED' else 'ACTUAL_ENTRY_BEFORE_FOLLOWING_UNKNOWN'
                    errors.append(reason+':'+vid)
                bound['after'] = current_following(conn, vid, self.last_completed, allow_clear=True)
                after_status = bound['after'].get('status')
                if after_status not in allowed:
                    reason = 'ACTUAL_ENTRY_AFTER_CURRENT_GAP_BOUND_DENIED' if after_status == 'STOP_CURRENT_GAP_BOUND_DENIED' else 'ACTUAL_ENTRY_AFTER_FOLLOWING_UNKNOWN'
                    errors.append(reason+':'+vid)
            except Exception as exc:
                bound['error'] = type(exc).__name__+':'+str(exc)
                errors.append('ACTUAL_ENTRY_FOLLOWING_UNKNOWN:'+vid+':'+str(exc))
        counters = {'colliding_vehicles': conn.simulation.getCollidingVehiclesNumber(),
            'starting_teleports': conn.simulation.getStartingTeleportNumber(), 'ending_teleports': conn.simulation.getEndingTeleportNumber()}
        row['native_event_counters'] = counters
        if any(counters.values()): errors.append('COLLISION_OR_TELEPORT')
        if p['motion'] == 'r' and recs: errors.append('RED_CROSSING')
        braking = {'speed_difference_ids': sorted(before & after), 'after_acceleration_ids': sorted(after),
            'excluded_before_only_ids': sorted(before-after), 'arrived_ids': sorted(arrived),
            'speed_difference_m_s2': {}, 'actual_acceleration_m_s2': {},
            'coverage': 'BEFORE_INTERSECTION_AFTER_DIFFERENCE_AND_AFTER_POPULATION_GETTER_NOT_GLOBAL'}
        row['braking_observation'] = braking
        for vid in sorted(before & after):
            difference = world[vid]['speed_m_s']-p['world'][vid]['speed_m_s']
            braking['speed_difference_m_s2'][vid] = difference
            if difference < -4.5-1e-6: errors.append('ORDINARY_BRAKING_EXCEEDED:'+vid)
        for vid in sorted(after):
            a = conn.vehicle.getAcceleration(vid)
            braking['actual_acceleration_m_s2'][vid] = a if math.isfinite(a) else None
            if not math.isfinite(a) or a < -4.5-1e-6: errors.append('UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+vid)
        if any(s in native_warning_text.lower() for s in ('emergency braking','emergency stop','collision','teleport')): errors.append('NATIVE_WARNING')
        try:row['body_observation']=self.body.observe(conn,self.last_completed,world,recs,p['motion'])
        except Exception as exc:
            row['body_observation_error']={'type':type(exc).__name__,'reason':str(exc)}
            errors.append('BODY_COVERAGE_UNKNOWN:'+type(exc).__name__+':'+str(exc))
        if errors:
            self.paused = True
            row.update(status='STOP_OBSERVED_AFTER_STEP', reasons=errors)
            raise DiagnosticStop(';'.join(errors))
        if p['time_s'] >= 1200 and p['motion'] == 'r' and self.first_controlled_red_begin is None:
            self.first_controlled_red_begin = p['time_s']
            self.checkpoint_pending = True
            row['status'] = 'MANDATORY_FIRST_RED_CHECKPOINT_PENDING'
        if self.last_end >= 1272:
            require(self.checkpoint_verified, 'FIRST_RED_CHECKPOINT_MISSING')
            require(len(self.ledger.rows) == (1272-1200)//PERIOD and all(c['completed'] for c in self.ledger.rows), 'PACKET_CYCLES_INCOMPLETE')
            self.paused = True
            row['status'] = 'PACKET_CYCLES_COMPLETED_MANDATORY_STOP_NOT_QUALIFIED'
        return row
