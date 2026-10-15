"""Boundary-applied two-car native policy; requests are not measured service."""
from fractions import Fraction
from dataclasses import dataclass, asdict
import math
from src.candidate_a_issue12_packet_policy_20261012.policy import period_for, quantize, require

MAX_GREEN = 5
MIN_RED = 2
PERIODS = (10,)


def parameters(period):
    require(type(period) is int and period in PERIODS, 'INVALID_PERIOD')
    return {'period_s':10,'yellow_s':3,'minimum_red_s':2,
            'program':'T10_G5Y3_NATIVE','phases':(('G',5,1),('y',3,2),('r',2,0))}


@dataclass(frozen=True)
class Command:
    request_id: str
    global_request_s: int
    rate_veh_h: float
    origin: str
    r_ALINEA: float | None = None

    def validate(self):
        require(isinstance(self.request_id, str) and self.request_id and
                type(self.global_request_s) is int and self.global_request_s >= 1200 and
                self.origin=='FIXED' and type(self.rate_veh_h) in (int,float) and self.rate_veh_h==750, 'INVALID_COMMAND_BINDING')
        period_for(self.rate_veh_h)
        require(self.r_ALINEA is None or (type(self.r_ALINEA) in (int, float) and
                math.isfinite(self.r_ALINEA) and self.r_ALINEA == self.rate_veh_h),
                'FEEDBACK_REQUEST_STATE_MISMATCH')
        return self


class Ledger:
    def __init__(self, command=750, end_s=1270):
        require(type(end_s) is int and 1200 < end_s <= 1272, 'INVALID_APPROVED_HORIZON')
        require(type(command) in (int,float) and command==750,'FIXED750_ONLY')
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
                            'mapped_period_s': period_for(command.rate_veh_h),
                            'mapped_rate_veh_h': quantize(command.rate_veh_h)})

    def begin_step(self, t, command=None):
        require(t == self.next_time_s and t < self.end_s, 'NONSEQUENTIAL_POLICY_TIME')
        if command is not None:
            self.register(command, t)
        new = self.cycle is None or t == self.cycle['end_s']
        pending = self.pending_command
        if new:
            record = self.requests[pending.request_id]
            if record['first_preparation_s'] is None:
                record['first_preparation_s'] = t
                record['status'] = 'PREPARED_NOT_OBSERVED'
                self.events.append({'event': 'PREPARED_NOT_OBSERVED', 'request_id': pending.request_id,
                    'application_global_s': t, 'global_request_s': pending.global_request_s,
                    'application_delay_s': t-pending.global_request_s})
            p = parameters(period_for(pending.rate_veh_h))
            self.cycle = dict(cycle_id=len(self.rows), begin_s=t, end_s=t+p['period_s'],
                **{k:v for k,v in p.items() if k != 'phases'}, requested_quota=2,
                quota_status='REQUESTED_NOT_EMPIRICALLY_QUALIFIED',
                applied_command_veh_h=quantize(pending.rate_veh_h),
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
        require(type(time_s) is int and c['begin_s'] < time_s <= c['begin_s']+MAX_GREEN,
                'GREEN_CLOSE_OUTSIDE_BUDGET')
        require(reason in ('ACTUAL_QUOTA_ACK','MAX_GREEN_DEADLINE'), 'UNKNOWN_GREEN_CLOSE_REASON')
        require(reason != 'ACTUAL_QUOTA_ACK' or c['N_G'] >= 2, 'QUOTA_NOT_OBSERVED')
        c.update(green_end_s=time_s, green_end_reason=reason)

    def motion_at(self, t):
        c = self.cycle
        require(c is not None and c['begin_s'] <= t < c['end_s'], 'OUTSIDE_CYCLE')
        end = c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+MAX_GREEN
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
            r_policy_pending_veh_h=self.step_mapped, applied_request_id=c['applied_request_id'],
            r_policy_applied_veh_h=c['applied_command_veh_h'], requested_quota=2,
            period_s=c['period_s'], cycle_application_delay_s=c['application_delay_s'],
            command_requested_s=pending.global_request_s)

    def accounting(self):
        keys=('C','C_mapped_pending','C_applied','E','N','policy_quantization',
              'application_latency','C_applied_minus_E','E_minus_N')
        if not self.observed_steps: return dict.fromkeys(keys)
        return dict(C=float(self.C), C_mapped_pending=float(self.C_mapped),
            C_applied=float(self.C_applied), E=self.E, N=self.N,
            policy_quantization=float(self.C-self.C_mapped),
            application_latency=float(self.C_mapped-self.C_applied),
            C_applied_minus_E=float(self.C_applied-self.E), E_minus_N=self.E-self.N)


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
