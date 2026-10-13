"""Boundary-applied two-car native policy; requests are not measured service."""
from fractions import Fraction
from dataclasses import dataclass, asdict
import math
from src.candidate_a_issue12_packet_policy_20261012.policy import period_for, quantize, require

MIN_RED = 2
PERIODS = (8, 10)
CATALOGUE_STATUS = "DIAGNOSTIC_T8_T10_ONLY_NOT_FULL_300_900"


# The original generic Command remains the request/Feedback interface.
from src.candidate_a_unified_alinea_20261013.policy import Command


def parameters(period):
    require(type(period) is int and period in PERIODS, 'UNREVIEWED_PACKET_PERIOD')
    green, yellow, program = (4, 2, 'I12_PACKET8') if period == 8 else (5, 3, 'T10_G5Y3_NATIVE')
    return dict(period_s=period, max_green_s=green, yellow_s=yellow, minimum_red_s=2,
                program=program, phases=(('G',green,1),('y',yellow,2),('r',2,0)))


def select_packet(C, N, requested_rate):
    require(type(N) is int and N >= 0, 'UNKNOWN_ACTUAL_CUMULATIVE_N')
    require(type(requested_rate) in (int,float) and math.isfinite(requested_rate) and
            720 <= requested_rate <= 900, 'UNSUPPORTED_RATE_T8_T10')
    error = Fraction(C)-N
    candidates = {p: error+Fraction(str(requested_rate))*p/3600-2 for p in PERIODS}
    chosen = min(PERIODS, key=lambda p:(abs(candidates[p]), -p))
    return chosen, dict(actual_C_fraction=str(Fraction(C)),actual_N=N,
        actual_error_fraction=str(error),forecast_request_veh_h=requested_rate,
        forecast_assumption='CURRENT_REQUEST_HELD_NOT_OBSERVED_FUTURE',
        candidate_errors_fraction={str(p):str(v) for p,v in candidates.items()},
        chosen_period_s=chosen,catalogue_status=CATALOGUE_STATUS)


class Ledger:
    def __init__(self, command=750, end_s=1296):
        require(type(end_s) is int and 1200 < end_s, 'INVALID_APPROVED_HORIZON')
        self.end_s = end_s
        self.next_time_s = 1200
        self.C = self.C_mapped = self.C_applied = Fraction(0)
        self.E = self.N = self.observed_steps = 0
        self.rows = []
        self.cycle = None
        self.crossed_ids = set()
        self.requests = {}
        self.events = []
        self.pending_command = Command('initial', 1200, command, 'FIXED').validate()
        self.register(self.pending_command, 1200)

    def register(self, command, t):
        command.validate()
        require(command.global_request_s == t and t == self.next_time_s,
                'COMMAND_REQUEST_TIME_MISMATCH')
        if command.request_id in self.requests:
            require(self.requests[command.request_id]['command'] == asdict(command), 'COMMAND_ID_REBOUND')
            return
        previous = self.requests.get(self.pending_command.request_id)
        if previous and previous['first_application_s'] is None:
            previous['status'] = 'SUPERSEDED_WITHOUT_APPLICATION'
            self.events.append({'event': 'SUPERSEDED', **previous})
        self.requests[command.request_id] = {'command': asdict(command), 'first_application_s': None, 'first_preparation_s': None,
                                            'status': 'PENDING'}
        self.pending_command = command
        self.events.append({'event': 'REQUESTED', **asdict(command),
                            'nearest_reference_period_s': period_for(command.rate_veh_h),
                            'nearest_reference_rate_veh_h': quantize(command.rate_veh_h)})

    def begin_step(self, t, command=None):
        require(t == self.next_time_s and t < self.end_s, 'NONSEQUENTIAL_POLICY_TIME')
        if command is not None:
            self.register(command, t)
        new = self.cycle is None or t == self.cycle['end_s']
        pending = self.pending_command
        if new:
            # First t0 has no previous packet. Never invent previous N=2.
            if self.cycle is not None:
                require(self.cycle['completed'] is True, 'UNKNOWN_PREVIOUS_PACKET_COMPLETENESS')
                actual = sum(self.cycle['N_'+m] for m in ('G','y','r'))
                require(actual == 2, 'SERVICE_PACKET_MISMATCH_HOLD_NO_CATCHUP')
            chosen, selection = select_packet(self.C, self.N, pending.rate_veh_h)
            self.events.append(dict(event='BOUNDARY_PACKET_SELECTED_NOT_APPLIED',time_s=t,**selection))
            record = self.requests[pending.request_id]
            if record['first_preparation_s'] is None:
                record['first_preparation_s'] = t
                record['status'] = 'PREPARED_NOT_OBSERVED'
                self.events.append({'event': 'PREPARED_NOT_OBSERVED', 'request_id': pending.request_id,
                    'application_global_s': t, 'global_request_s': pending.global_request_s,
                    'application_delay_s': t-pending.global_request_s})
            p = parameters(chosen)
            self.cycle = dict(cycle_id=len(self.rows), begin_s=t, end_s=t+p['period_s'],
                **{k:v for k,v in p.items() if k != 'phases'}, requested_quota=2,
                quota_status='REQUESTED_NOT_EMPIRICALLY_QUALIFIED',
                applied_command_veh_h=7200/p['period_s'],
                packet_selection=selection,
                applied_request_id=pending.request_id, command_requested_s=pending.global_request_s,
                command_applied_s=record['first_application_s'],
                planned_application_s=t, application_status='PREPARED_NOT_OBSERVED',
                application_delay_s=None if record['first_application_s'] is None else record['first_application_s']-pending.global_request_s,
                command_age_at_cycle_start_s=t-pending.global_request_s,
                green_end_s=None, green_end_reason=None, executed=None, completed=False,
                N_G=0, N_y=0, N_r=0, crossing_ids=[], phase_exposure_s={'G':0,'y':0,'r':0})
            self.rows.append(self.cycle)
        self.step_command = Fraction(str(pending.rate_veh_h))
        self.step_mapped = quantize(pending.rate_veh_h)
        self.prepared_time_s = t
        self.new_cycle_prepared = new
        return new, self.cycle

    def mark_cycle_start(self, executed, denial_reason=''):
        require(self.cycle is not None and self.cycle['executed'] is None, 'DUPLICATE_CYCLE_START')
        self.cycle.update(executed=bool(executed), denial_reason=denial_reason)

    def close_green(self, time_s, reason):
        c = self.cycle
        require(c is not None and c['green_end_s'] is None, 'DUPLICATE_GREEN_CLOSE')
        require(type(time_s) is int and c['begin_s'] < time_s <= c['begin_s']+c['max_green_s'],
                'GREEN_CLOSE_OUTSIDE_BUDGET')
        require(reason in ('ACTUAL_QUOTA_ACK','MAX_GREEN_DEADLINE'), 'UNKNOWN_GREEN_CLOSE_REASON')
        require(reason != 'ACTUAL_QUOTA_ACK' or c['N_G'] >= 2, 'QUOTA_NOT_OBSERVED')
        c.update(green_end_s=time_s, green_end_reason=reason)

    def motion_at(self, t):
        c = self.cycle
        require(c is not None and c['begin_s'] <= t < c['end_s'], 'OUTSIDE_CYCLE')
        end = c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+c['max_green_s']
        return 'G' if t < end else 'y' if t < end+c['yellow_s'] else 'r'

    def end_step(self, end, crossing_ids, motion):
        require(end == self.next_time_s+1 and motion == self.motion_at(end-1), 'POLICY_MOTION_MISMATCH')
        ids = tuple(crossing_ids)
        require(len(set(ids)) == len(ids) and not self.crossed_ids.intersection(ids), 'DUPLICATE_ACTUAL_ENTRY')
        self.crossed_ids.update(ids)
        if end == self.cycle['begin_s']+1:
            require(self.cycle['executed'] is True and motion == 'G', 'CYCLE_FIRST_ACK_NOT_GREEN')
            record = self.requests[self.cycle['applied_request_id']]
            if record['first_application_s'] is None:
                record.update(first_application_s=end-1, status='ACK_OBSERVED')
                self.events.append({'event':'ACK_OBSERVED','request_id':self.cycle['applied_request_id'],
                    'application_global_s':end-1,'first_green_ACK_s':end,
                    'application_delay_s':end-1-record['command']['global_request_s']})
            self.cycle.update(command_applied_s=record['first_application_s'],
                application_delay_s=record['first_application_s']-record['command']['global_request_s'],
                application_status='ACK_OBSERVED')
        self.C += self.step_command/3600
        self.C_mapped += Fraction(str(self.step_mapped))/3600
        self.C_applied += Fraction(str(self.cycle['applied_command_veh_h']))/3600
        self.N += len(ids)
        self.cycle['N_'+motion] += len(ids)
        self.cycle['crossing_ids'].extend(ids)
        self.cycle['phase_exposure_s'][motion] += 1
        self.observed_steps += 1
        if end == self.cycle['end_s']:
            require(self.cycle['phase_exposure_s']['y'] == self.cycle['yellow_s'] and
                    self.cycle['phase_exposure_s']['r'] >= 2, 'INCOMPLETE_CLEARANCE_PHASES')
            self.E += 2
            self.cycle['completed'] = True
        self.next_time_s = end

    def rate_chain(self):
        pending = self.pending_command; c = self.cycle
        return dict(input_origin=pending.origin, r_ALINEA=pending.r_ALINEA,
            r_final_veh_h=pending.rate_veh_h, pending_request_id=pending.request_id,
            r_policy_pending_veh_h=None,
            nearest_reference_veh_h=self.step_mapped,
            pending_packet_status='SELECTED_ONLY_AT_COMPLETE_BOUNDARY', applied_request_id=c['applied_request_id'],
            r_policy_applied_veh_h=c['applied_command_veh_h'], requested_quota=2,
            period_s=c['period_s'], cycle_application_delay_s=c['application_delay_s'],
            command_requested_s=pending.global_request_s)

    def accounting(self):
        keys=('C','C_nearest_reference','C_applied','E','N','requested_minus_nominal',
              'nominal_minus_actual','requested_minus_actual')
        if not self.observed_steps: return dict.fromkeys(keys)
        return dict(C=float(self.C),C_nearest_reference=float(self.C_mapped),
            C_applied=float(self.C_applied),E=self.E,N=self.N,
            requested_minus_nominal=float(self.C-self.E),nominal_minus_actual=self.E-self.N,
            requested_minus_actual=float(self.C-self.N),C_exact_fraction=str(self.C),
            E_support='COMPLETE_PACKETS_ONLY',N_support='ALL_OBSERVED_ENTRY_BEGIN_INTERVALS',
            partial_cycle=not self.cycle['completed'],
            nearest_reference_is_not_cumulative_scheduler_output=True)


def yellow_scope(vehicles, time_s, yellow_s):
    """Local stop-or-body-clear feasibility screen, not an A1 future-safety proof."""
    require(type(time_s) is int, 'UNKNOWN_yellow_s_TIME')
    # A not-yet-covered R cannot travel from outside113.08m ingress through
    #204.49m storage during5s under the unchanged checked55.56m/s speed cap.
    require(204.49+113.08 > yellow_s*55.55555555555556, 'yellow_s_APPROACH_COVERAGE_UNKNOWN')
    rows=[];seen=set()
    for v in vehicles:
        v.validate()
        require(all(type(x) in (int,float) and math.isfinite(x) for x in
            (v.position_m,v.speed_m_s,v.length_m,v.normal_decel_m_s2,v.action_step_s)), 'UNKNOWN_yellow_s_NUMERIC')
        require(v.vehicle_id not in seen, 'DUPLICATE_yellow_s_ID');seen.add(v.vehicle_id)
        require((v.population=='storage' and 0 <= v.position_m < 204.49) or
                (v.population=='ingress' and -113.08 <= v.position_m <= 0), 'UNKNOWN_yellow_s_POSITION')
        d=204.49-v.position_m;speed=v.speed_m_s;b=v.normal_decel_m_s2
        # Euler updates velocity before position; v<=b*1 permits a normal
        #one-step stop, but only for a bound front still upstream of the line.
        one_step_stop = d > 0 and speed <= b*v.action_step_s
        stop_distance = speed*v.action_step_s+speed*speed/(2*b)
        stop_possible = d > 0 and (one_step_stop or d >= stop_distance)
        timing = None if speed==0 else v.action_step_s+speed/(2*b)+v.length_m/speed
        clear_possible = speed > 0 and timing <= yellow_s and d+v.length_m <= speed*(yellow_s-v.action_step_s)
        row=dict(vehicle_id=v.vehicle_id, population=v.population,time_s=time_s,
            position_m=v.position_m, speed_m_s=speed,length_m=v.length_m,
            normal_decel_m_s2=b,action_step_s=v.action_step_s,
            distance_to_meter_m=d,one_step_Euler_stop_possible=one_step_stop,
            stop_distance_screen_m=stop_distance, stop_possible=stop_possible,
            body_clear_time_screen_s=timing, clear_possible=clear_possible,
            status='WITHIN_LOCAL_yellow_s_SCREEN' if stop_possible or clear_possible else 'UNKNOWN_LOCAL_yellow_s_SCOPE',
            native_future_safety_proven=False)
        rows.append(row)
    return {'status':'PASS' if all(x['status']=='WITHIN_LOCAL_yellow_s_SCREEN' for x in rows) else 'UNKNOWN', 'time_s':time_s,'yellow_s':yellow_s,'covered_ids':sorted(seen),'rows':rows,
            'classification':'BOUND_LOCAL_FEASIBILITY_NOT_GLOBAL_SAFETY'}
