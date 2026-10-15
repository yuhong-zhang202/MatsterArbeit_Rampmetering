"""One bounded count-actuated policy. Planned quota is never measured discharge."""
from fractions import Fraction
import math

PERIODS = tuple(range(8,25))
PERIOD = 8
YELLOW = 2
MIN_RED = 2
MAX_GREEN = PERIOD - YELLOW - MIN_RED
PROGRAM = 'I12_PACKET8'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def quantize(rate):
    require(type(rate) in (int, float) and math.isfinite(rate) and 300 <= rate <= 900,
            'INVALID_FINAL_COMMAND')
    return 7200 / period_for(rate)


def period_for(rate):
    require(type(rate) in (int,float) and math.isfinite(rate) and 300<=rate<=900, "INVALID_FINAL_COMMAND")
    return min(PERIODS, key=lambda t:(abs(7200/t-rate),-t))


class Ledger:
    def __init__(self, command):
        require(period_for(command)==PERIOD, "THIS_DIAGNOSTIC_ONLY_SUPPORTS_PREPARED_PERIOD8")
        self.command = command
        self.next_time_s = 1200
        self.C = self.C_mapped = self.C_applied = Fraction(0)
        self.E = self.N = self.observed_steps = 0
        self.rows = []
        self.cycle = None
        self.crossed_ids = set()
        self.pending_rate = None
        self.pending_requested_s = None

    def begin_step(self, t, final_command):
        require(t == self.next_time_s, 'NONSEQUENTIAL_POLICY_TIME')
        require(period_for(final_command)==PERIOD, "UNPREPARED_PERIOD_CHANGE")
        mapped = quantize(final_command)
        if mapped != self.pending_rate:
            self.pending_rate = mapped
            self.pending_requested_s = t
        new = self.cycle is None or t == self.cycle['end_s']
        if new:
            require(t in range(1200,1272,PERIOD), 'UNDECLARED_CYCLE_START')
            applied = self.pending_rate
            self.cycle = dict(cycle_id=len(self.rows), begin_s=t, end_s=t+PERIOD,
                period_s=PERIOD, requested_quota=2,
                quota_status='REQUESTED_NOT_EMPIRICALLY_QUALIFIED',
                applied_command_veh_h=applied, command_requested_s=self.pending_requested_s,
                command_applied_s=t, application_delay_s=t-self.pending_requested_s,
                green_end_s=None, green_end_reason=None, executed=None,
                completed=False, N_G=0, N_y=0, N_r=0, crossing_ids=[],
                phase_exposure_s={'G':0,'y':0,'r':0})
            self.rows.append(self.cycle)
        self.step_command = Fraction(str(final_command))
        self.step_mapped = mapped
        return new, self.cycle

    def mark_cycle_start(self, executed, denial_reason=''):
        require(self.cycle is not None and self.cycle['executed'] is None, 'DUPLICATE_CYCLE_START')
        self.cycle['executed'] = bool(executed)
        self.cycle['denial_reason'] = denial_reason

    def close_green(self, time_s, reason):
        c = self.cycle
        require(c is not None and c['green_end_s'] is None, 'DUPLICATE_GREEN_CLOSE')
        require(type(time_s) is int and c['begin_s'] < time_s <= c['begin_s']+MAX_GREEN,
                'GREEN_CLOSE_OUTSIDE_BUDGET')
        require(reason in ('ACTUAL_QUOTA_ACK','MAX_GREEN_DEADLINE'), 'UNKNOWN_GREEN_CLOSE_REASON')
        if reason == 'ACTUAL_QUOTA_ACK':
            require(c['N_G'] >= c['requested_quota'], 'QUOTA_NOT_OBSERVED')
        c['green_end_s'] = time_s
        c['green_end_reason'] = reason

    def motion_at(self, t):
        c = self.cycle
        require(c is not None and c['begin_s'] <= t < c['end_s'], 'OUTSIDE_CYCLE')
        end = c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+MAX_GREEN
        return 'G' if t < end else 'y' if t < end+YELLOW else 'r'

    def end_step(self, end, crossing_ids, motion):
        require(end == self.next_time_s+1 and motion == self.motion_at(end-1), 'POLICY_MOTION_MISMATCH')
        ids = tuple(crossing_ids)
        require(len(set(ids)) == len(ids) and not self.crossed_ids.intersection(ids), 'DUPLICATE_ACTUAL_ENTRY')
        self.crossed_ids.update(ids)
        self.C += self.step_command/3600
        self.C_mapped += Fraction(str(self.step_mapped))/3600
        self.C_applied += Fraction(str(self.cycle['applied_command_veh_h']))/3600
        self.N += len(ids)
        self.cycle['N_'+motion] += len(ids)
        self.cycle['crossing_ids'].extend(ids)
        self.cycle['phase_exposure_s'][motion] += 1
        self.observed_steps += 1
        if end == self.cycle['end_s']:
            require(self.cycle['phase_exposure_s']['y'] == YELLOW and
                    self.cycle['phase_exposure_s']['r'] >= MIN_RED, 'INCOMPLETE_CLEARANCE_PHASES')
            self.E += self.cycle['requested_quota']
            self.cycle['completed'] = True
        self.next_time_s = end

    def accounting(self):
        keys = ('C','C_mapped_pending','C_applied','E','N','policy_quantization',
                'application_latency','C_applied_minus_E','E_minus_N')
        if self.observed_steps == 0:
            return dict.fromkeys(keys)
        return dict(C=float(self.C), C_mapped_pending=float(self.C_mapped),
            C_applied=float(self.C_applied), E=self.E, N=self.N,
            policy_quantization=float(self.C-self.C_mapped),
            application_latency=float(self.C_mapped-self.C_applied),
            C_applied_minus_E=float(self.C_applied-self.E), E_minus_N=self.E-self.N)


def yellow_scope(vehicles, time_s):
    """Local stop-or-body-clear feasibility screen, not an A1 future-safety proof."""
    require(type(time_s) is int, 'UNKNOWN_YELLOW_TIME')
    # A not-yet-covered R cannot travel from outside113.08m ingress through
    #204.49m storage during5s under the unchanged checked55.56m/s speed cap.
    require(204.49+113.08 > YELLOW*55.55555555555556, 'YELLOW_APPROACH_COVERAGE_UNKNOWN')
    rows=[];seen=set()
    for v in vehicles:
        v.validate()
        require(all(type(x) in (int,float) and math.isfinite(x) for x in
            (v.position_m,v.speed_m_s,v.length_m,v.normal_decel_m_s2,v.action_step_s)), 'UNKNOWN_YELLOW_NUMERIC')
        require(v.vehicle_id not in seen, 'DUPLICATE_YELLOW_ID');seen.add(v.vehicle_id)
        require((v.population=='storage' and 0 <= v.position_m < 204.49) or
                (v.population=='ingress' and -113.08 <= v.position_m <= 0), 'UNKNOWN_YELLOW_POSITION')
        d=204.49-v.position_m;speed=v.speed_m_s;b=v.normal_decel_m_s2
        # Euler updates velocity before position; v<=b*1 permits a normal
        #one-step stop, but only for a bound front still upstream of the line.
        one_step_stop = d > 0 and speed <= b*v.action_step_s
        stop_distance = speed*v.action_step_s+speed*speed/(2*b)
        stop_possible = d > 0 and (one_step_stop or d >= stop_distance)
        timing = None if speed==0 else v.action_step_s+speed/(2*b)+v.length_m/speed
        clear_possible = speed > 0 and timing <= YELLOW and d+v.length_m <= speed*(YELLOW-v.action_step_s)
        row=dict(vehicle_id=v.vehicle_id, population=v.population,time_s=time_s,
            position_m=v.position_m, speed_m_s=speed,length_m=v.length_m,
            normal_decel_m_s2=b,action_step_s=v.action_step_s,
            distance_to_meter_m=d,one_step_Euler_stop_possible=one_step_stop,
            stop_distance_screen_m=stop_distance, stop_possible=stop_possible,
            body_clear_time_screen_s=timing, clear_possible=clear_possible,
            status='WITHIN_LOCAL_YELLOW_SCREEN' if stop_possible or clear_possible else 'UNKNOWN_LOCAL_YELLOW_SCOPE',
            native_future_safety_proven=False)
        rows.append(row)
    return {'status':'PASS' if all(x['status']=='WITHIN_LOCAL_YELLOW_SCREEN' for x in rows) else 'UNKNOWN', 'time_s':time_s,'yellow_s':YELLOW,'covered_ids':sorted(seen),'rows':rows,
            'classification':'BOUND_LOCAL_FEASIBILITY_NOT_GLOBAL_SAFETY'}
