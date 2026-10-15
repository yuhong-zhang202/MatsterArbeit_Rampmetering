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
PROFILE = 'NATIVE_PHASE_PASSIVE_REFERENCE_OBSERVATION_DIAGNOSTIC_NOT_QUALIFIED'
from src.candidate_a_natural_service_20261015.current_gap_scope import (
    classify_receiver, current_following, classification, ACCEPTED, BELOW)
from src.candidate_a_natural_service_20261015.policy import Ledger, parameters, yellow_scope
from src.candidate_a_native_yellow_minqual_20261015.yellow_contract import annotate_yellow_scope
from src.candidate_a_issue12_packet_policy_20261012.body import BodyTracker
from src.candidate_a_unified_alinea_20261013 import numeric_stop


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
    def __init__(self, observe, command=900, end_s=4200, numerical_authority=None, yellow_diagnostic_mode=False):
        self.observe = observe  # Original binding unchanged.
        require(type(yellow_diagnostic_mode) is bool, 'UNKNOWN_YELLOW_MODE')
        self.yellow_diagnostic_mode = yellow_diagnostic_mode  # Default strict.
        self.envelope = PhaseEnvelope()  # Pre-control holding program only.
        self.ledger = Ledger(command, end_s)
        self.end_s = end_s
        self.selected_new_program_at = None
        require(numerical_authority is None,'NEW_SCOPE_NUMERICAL_EXCEPTION_NOT_ENABLED')
        self.numerical_authority = numerical_authority  # Default strict, never implicit approval.
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
        require(type(time_s) is int and 0 <= time_s < self.end_s, 'TIME_OUTSIDE_PROPOSED_CAP')
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
        if time_s >= 600:
            require(self.ledger.prepared_time_s == time_s, 'BRIDGE_POLICY_STEP_NOT_BOUND')
            new, cycle = self.ledger.new_cycle_prepared, self.ledger.cycle
            params = parameters(cycle['period_s'])
            require(program == cycle['signal_program'], 'PROGRAM_IDENTITY')
            require(type(cycle['executed']) is bool, 'UNBOUND_EXECUTION_DECISION')
            if cycle['executed']:
                idx, motion = motion_phase(phase, state, nxt, time_s, params['phases'])
                if new:
                    require(idx == 0 and motion == 'G' and receiver['available'], 'GREEN_START_NOT_PREPARED_OR_RECEIVER_DENIED')
                    require(self.selected_new_program_at == time_s and phase == 0 and state == 'G' and nxt == time_s+cycle['max_green_s'], 'NATIVE_CYCLE_START_BOUNDARY_MISMATCH')
            else:
                require(phase == 2 and state == 'r' and nxt == cycle['end_s'], 'WITHHELD_RED_CLOCK_MISMATCH')
                idx, motion = 2, 'r'
            if motion == 'y' and cycle['green_end_s'] is None:
                self.ledger.close_green(time_s, 'MAX_GREEN_DEADLINE')
            require(motion == self.ledger.motion_at(time_s), 'PHASE_SCHEDULE_MISMATCH')
            if motion == 'y' and self.previous_motion != 'y':
                self.last_yellow_scope = yellow_scope(vehicles, time_s, cycle['yellow_s'])
                self.last_yellow_scope = annotate_yellow_scope(self.last_yellow_scope, vehicles, time_s, cycle['yellow_s'], self.yellow_diagnostic_mode)
                require(self.last_yellow_scope['diagnostic_yellow_contract']['allow_prepared_step'] is True, 'UNKNOWN_LOCAL_YELLOW_SCOPE')
        else:
            require(program == 'A_OPEN' and type(phase) is int and phase == 0 and state == 'G', 'OPEN_PHASE_MISMATCH')
            motion = 'G'
        native_decision = classify_receiver(conn, receiver, time_s, role='ONGOING_PRE_RECEIVER') if motion == 'G' else None
        require(receiver['available'] or motion != 'G' or native_decision['decision'] in ('WAIT_NATIVE_FOLLOWING', BELOW), 'CURRENT_GAP_BOUND_DENIED')
        entry_before = {vid: current_following(conn, vid, time_s, allow_clear=True, role='ENTRY_BEFORE') for vid in sorted(ids[STORAGE])} if motion in ('G','y') else {}
        entering_red = motion == 'r' and (self.previous_motion != 'r' or state == 'y')
        shadow = red_transition_witness(vehicles) if entering_red else None
        numeric_before = ({vid:numeric_stop.read_vehicle_state(conn,vid,time_s) for vid in sorted(ids[STORAGE])}
            if self.numerical_authority is not None and cycle is not None and motion=='y' and
            cycle['green_end_s']==time_s else {})
        self.pending = {'time_s': time_s, 'world': world, 'loaded': loaded, 'pending_ids': pending_ids,
                        'storage': set(ids[STORAGE]), 'internal': set(internal), 'cycle_id': cycle['cycle_id'] if cycle else -1,
                        'program': program, 'phase_before': phase, 'state_before': state, 'next_switch_before_s': nxt, 'motion_phase': idx if time_s >= 600 else 0,
                        'motion': motion, 'entering_red': entering_red, 'shadow_envelope': shadow,
                        'vehicle_states': [asdict(v) for v in vehicles], 'receiver': receiver,
                        'yellow_scope':self.last_yellow_scope,
                        'rate_chain':self.ledger.rate_chain() if cycle else None,
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
                        'native_receiver_decision': native_decision, 'entry_following_before': entry_before,
                        'numeric_stop_before': numeric_before}
        if cycle is not None:
            cycle['service_context'].append({'time_s':time_s,'storage_ids':sorted(ids[STORAGE]),'vehicle_states':self.pending['vehicle_states'],'receiver':receiver,'native_receiver_decision':native_decision,'cause':'UNESTABLISHED'})
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
        if p['cycle_id'] >= 0:
            c=self.ledger.cycle
            green_end=c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+c['max_green_s']
            expected_switch = c['end_s'] if not c['executed'] else (c['begin_s']+c['max_green_s'] if p['motion']=='G' else
                green_end+c['yellow_s'] if p['motion']=='y' else
                c['end_s'] if c.get('red_clock_bound') else green_end+c['period_s']-c['max_green_s'])
            row['phase_clock_binding']={'cycle_id':c['cycle_id'],'program':c['signal_program'],
                'motion':p['motion'],'expected_post_nextSwitch_s':expected_switch,
                'actual_post_nextSwitch_s':row['phase_observation']['next_switch_after_s'],
                'status':'ACK_OBSERVED_NOT_FUTURE_SAFETY'}
            require(row['phase_observation']['next_switch_after_s']==expected_switch,
                'POST_PHASE_CLOCK_MISMATCH')
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
        # Retain the observed entry bracket even if signal binding fails. It
        # must not become expected-motion accounting or an applied command.
        row['actual_crossings'] = recs
        if p['cycle_id'] >= 0:
            signal = row['phase_observation']
            actual_program = conn.trafficlight.getProgram(TLS)
            actual_links = conn.trafficlight.getControlledLinks(TLS)
            signal_bound = (type(signal['phase_after']) is int and
                signal['phase_after'] == p['motion_phase'] and
                signal['state_after'] == p['motion'] and actual_program == p['program'] and
                actual_links == ((('ramp_storage_0','ramp_accel_0',INTERNAL),),) and
                conn.simulation.getTime() == self.last_completed)
            row['post_signal_application_binding'] = {
                'ACK_s': self.last_completed, 'actual_phase': signal['phase_after'],
                'actual_state': signal['state_after'], 'actual_program': actual_program,
                'actual_controlled_links': actual_links,
                'expected_phase': p['motion_phase'], 'expected_state': p['motion'],
                'expected_program': p['program'],
                'status': 'BOUND_BEFORE_LEDGER' if signal_bound else 'STOP_UNBOUND_BEFORE_LEDGER'}
            require(signal_bound, 'POST_SIGNAL_APPLICATION_BINDING_MISMATCH')
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
                row['post_native_receiver_decision'] = classify_receiver(conn, post_receiver, self.last_completed, role='POST_RECEIVER')
                if row['post_native_receiver_decision']['decision'] not in ('READY','WAIT_NATIVE_FOLLOWING', BELOW):
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
                allowed = ACCEPTED
                before_status = classification(bound['before'])
                if before_status not in allowed:
                    reason = 'ACTUAL_ENTRY_BEFORE_CURRENT_GAP_BOUND_DENIED' if before_status == 'STOP_CURRENT_GAP_BOUND_DENIED' else 'ACTUAL_ENTRY_BEFORE_FOLLOWING_UNKNOWN'
                    errors.append(reason+':'+vid)
                bound['after'] = current_following(conn, vid, self.last_completed, allow_clear=True, role='ENTRY_AFTER')
                after_status = classification(bound['after'])
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
        # BEGIN_APPROVED_NUMERICAL_EVENT_SEAM
        row['legacy_braking_reasons']=[x for x in errors if x.startswith(
            ('ORDINARY_BRAKING_EXCEEDED:','UNKNOWN_OR_EXCESSIVE_ACCELERATION:'))]
        row['numeric_stop_classifications']=[]
        if self.numerical_authority is not None:
            for vid in sorted(before & after):
                allowed_reasons={'ORDINARY_BRAKING_EXCEEDED:'+vid,
                    'UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+vid}
                if not allowed_reasons.intersection(errors):continue
                try:
                    before_state=p.get('numeric_stop_before',{}).get(vid)
                    after_state=numeric_stop.read_vehicle_state(conn,vid,self.last_completed)
                    following=current_following(conn,vid,self.last_completed,allow_clear=True,role='ENTRY_AFTER')
                    binding=row['post_signal_application_binding']
                    evidence=dict(run_id=self.numerical_authority['run_id'],mode=self.numerical_authority['mode'],
                        execution_card_sha256=self.numerical_authority['execution_card_sha256'],
                        vehicle_id=vid,time_begin_s=p['time_s'],time_end_s=self.last_completed,dt_s=1,
                        before=before_state,after=after_state,motion=p['motion'],
                        first_yellow_begin_s=self.ledger.cycle['green_end_s'],
                        post_signal_binding_status=binding['status'],actual_phase=binding['actual_phase'],
                        actual_state=binding['actual_state'],actual_program=binding['actual_program'],
                        expected_program=p['program'],controlled_links=[[list(x) for x in group] for group in binding['actual_controlled_links']],
                        full_before_after_world_binding=vid in before & after,entered_link=vid in {x['vehicle_id'] for x in recs},
                        body_coverage_complete='body_observation' in row and 'body_observation_error' not in row,
                        before_current_gap_status=p['entry_following_before'].get(vid,{}).get('status'),
                        after_current_gap_status=following['status'],native_event_counters=counters,
                        native_warning_observed=any(x in native_warning_text.lower() for x in
                            ('emergency braking','emergency stop','collision','teleport')),
                        recorded_delta_v_m_s2=braking['speed_difference_m_s2'][vid],
                        actual_native_acceleration_m_s2=braking['actual_acceleration_m_s2'][vid],
                        following_after=following)
                    decision=numeric_stop.classify(evidence,self.numerical_authority)
                except (KeyError,ValueError,TypeError,OverflowError) as exc:
                    decision={'decision':'STOP','classification':'NUMERICAL_EVENT_EVIDENCE_UNKNOWN',
                        'vehicle_id':vid,'reason':type(exc).__name__+':'+str(exc),'legacy_strict_FAIL_retained':True}
                row['numeric_stop_classifications'].append(decision)
                if decision['decision']=='CONTINUE_RESTRICTED_NUMERICAL_EVENT':
                    errors=[x for x in errors if x not in allowed_reasons]
        # END_APPROVED_NUMERICAL_EVENT_SEAM
        if errors:
            self.paused = True
            row.update(status='STOP_OBSERVED_AFTER_STEP', reasons=errors)
            raise DiagnosticStop(';'.join(errors))
        if p['time_s'] >= 600 and p['motion'] == 'r' and self.first_controlled_red_begin is None:
            self.first_controlled_red_begin = p['time_s']
            self.checkpoint_pending = True
            row['status'] = 'MANDATORY_FIRST_RED_CHECKPOINT_PENDING'
        if self.last_end >= self.end_s:
            require(self.checkpoint_verified, 'FIRST_RED_CHECKPOINT_MISSING')
            require(self.last_end == self.end_s, 'APPROVED_END_OVERRUN')
            row['terminal_cycle_complete'] = all(c['completed'] for c in self.ledger.rows)
            row['body_censored_ids'] = sorted(self.body.active) if hasattr(self.body,'active') else []
            self.paused = True
            row['status'] = 'APPROVED_TECHNICAL_END_MANDATORY_STOP_NOT_QUALIFIED'
        return row
