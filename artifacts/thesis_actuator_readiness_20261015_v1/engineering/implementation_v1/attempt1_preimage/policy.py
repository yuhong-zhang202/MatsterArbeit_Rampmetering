"""Natural-service packet translation; correct nominal quantization, not lost flow."""
from fractions import Fraction
from dataclasses import dataclass, asdict
import math
from src.candidate_a_issue12_packet_policy_20261012.policy import period_for, quantize, require

MIN_RED = 2
PERIODS = tuple(range(8, 25))
CATALOGUE_STATUS = "FULL_300_900_CONFIGURED_ACTUAL_SERVICE_UNQUALIFIED"


# The original generic Command remains the request/Feedback interface.
from src.candidate_a_unified_alinea_20261013.policy import Command


def parameters(period):
    require(type(period) is int and period in PERIODS, 'UNREVIEWED_PACKET_PERIOD')
    green, yellow, program = (5, 3, 'T10_G5Y3_NATIVE') if period == 10 else (4, min(5, period-6), f'I12_PACKET{period}')
    red = period-green-yellow
    return dict(period_s=period, max_green_s=green, yellow_s=yellow, minimum_red_s=2,
                program=program, phases=(('G',green,1),('y',yellow,2),('r',red,0)))


def select_packet(C, E, requested_rate):
    require(type(E) is int and E >= 0, 'UNKNOWN_SCHEDULED_NOMINAL_E')
    require(type(requested_rate) in (int,float) and math.isfinite(requested_rate) and
            300 <= requested_rate <= 900, 'UNSUPPORTED_RATE_FULL_300_900')
    error = Fraction(C)-E
    candidates = {p: error+Fraction(str(requested_rate))*p/3600-2 for p in PERIODS}
    chosen = min(PERIODS, key=lambda p:(abs(candidates[p]), -p))
    return chosen, dict(actual_C_fraction=str(Fraction(C)),scheduled_nominal_E=E,
        scheduled_error_fraction=str(error),forecast_request_veh_h=requested_rate,
        forecast_assumption='CURRENT_REQUEST_HELD_NOT_OBSERVED_FUTURE',
        candidate_errors_fraction={str(p):str(v) for p,v in candidates.items()},
        chosen_period_s=chosen,catalogue_status=CATALOGUE_STATUS)


class Ledger:
    def __init__(self, command=900, end_s=4200, activation_s=600):
        require(activation_s == 600 and type(activation_s) is int and type(end_s) is int and activation_s < end_s <= 4200, 'INVALID_NATURAL_HORIZON')
        self.activation_s = activation_s
        self.end_s = end_s
        self.next_time_s = activation_s
        self.C = self.C_mapped = self.C_applied = self.C_selected = Fraction(0)
        self.E_executed = 0
        self.E = self.N = self.observed_steps = 0
        self.rows = []
        self.cycle = None
        self.crossed_ids = set()
        self.requests = {}
        self.events = []
        self.pending_command = Command('initial', activation_s, command, 'FIXED').validate()
        self.register(self.pending_command, activation_s)

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
            chosen, selection = select_packet(self.C, self.E, pending.rate_veh_h)
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
                green_end_s=None, green_end_reason=None, executed=None, completed=False, signal_program=None,
                service_context=[],
                N_G=0, N_y=0, N_r=0, crossing_ids=[], phase_exposure_s={'G':0,'y':0,'r':0})
            self.rows.append(self.cycle)
        self.step_command = Fraction(str(pending.rate_veh_h))
        self.step_mapped = quantize(pending.rate_veh_h)
        self.prepared_time_s = t
        self.new_cycle_prepared = new
        return new, self.cycle

    def mark_cycle_start(self, executed, denial_reason='', signal_program=None):
        require(self.cycle is not None and self.cycle['executed'] is None, 'DUPLICATE_CYCLE_START')
        require(type(executed) is bool and isinstance(signal_program,str) and signal_program, 'UNKNOWN_EXECUTION_DECISION')
        self.cycle.update(executed=executed, denial_reason=denial_reason, signal_program=signal_program)

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
        if c['executed'] is False: return 'r'
        end = c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+c['max_green_s']
        return 'G' if t < end else 'y' if t < end+c['yellow_s'] else 'r'

    def end_step(self, end, crossing_ids, motion):
        require(end == self.next_time_s+1 and motion == self.motion_at(end-1), 'POLICY_MOTION_MISMATCH')
        ids = tuple(crossing_ids)
        require(len(set(ids)) == len(ids) and not self.crossed_ids.intersection(ids), 'DUPLICATE_ACTUAL_ENTRY')
        self.crossed_ids.update(ids)
        if end == self.cycle['begin_s']+1 and self.cycle['executed'] is False:
            require(motion == 'r', 'WITHHELD_PACKET_NOT_RED')
            self.events.append(dict(event='WITHHELD_RED_ACK_OBSERVED', cycle_id=self.cycle['cycle_id'],
                request_id=self.cycle['applied_request_id'], observed_ACK_s=end, signal_program=self.cycle['signal_program']))
        if end == self.cycle['begin_s']+1 and self.cycle['executed'] is True:
            require(self.cycle['executed'] is True and motion == 'G', 'CYCLE_FIRST_ACK_NOT_GREEN')
            self.events.append(dict(event='PACKET_ACK_OBSERVED',cycle_id=self.cycle['cycle_id'],
                request_id=self.cycle['applied_request_id'],application_global_s=end-1,
                first_green_ACK_s=end,period_s=self.cycle['period_s'],
                max_green_s=self.cycle['max_green_s'],yellow_s=self.cycle['yellow_s'],
                applied_command_veh_h=self.cycle['applied_command_veh_h']))
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
        self.C_selected += Fraction(2,self.cycle['period_s'])
        if self.cycle['executed'] is True:
            self.C_applied += Fraction(2,self.cycle['period_s'])
        self.N += len(ids)
        self.cycle['N_'+motion] += len(ids)
        self.cycle['crossing_ids'].extend(ids)
        self.cycle['phase_exposure_s'][motion] += 1
        self.observed_steps += 1
        if end == self.cycle['end_s']:
            if self.cycle['executed'] is True:
                require(self.cycle['phase_exposure_s']['y'] == self.cycle['yellow_s'] and self.cycle['phase_exposure_s']['r'] >= 2, 'INCOMPLETE_CLEARANCE_PHASES')
                self.E_executed += 2
            else:
                require(self.cycle['phase_exposure_s'] == {'G':0,'y':0,'r':self.cycle['period_s']}, 'WITHHELD_PACKET_EXPOSURE_MISMATCH')
            self.E += 2
            self.cycle['completed'] = True
            actual = sum(self.cycle['N_'+m] for m in ('G','y','r'))
            self.events.append(dict(event='NOMINAL_PACKET_COMPLETED', cycle_id=self.cycle['cycle_id'],
                time_s=end, executed=self.cycle['executed'], actual_packet_N=actual,
                scheduled_quota=2, service_deviation=2-actual, cause='UNESTABLISHED',
                C_exact_fraction=str(self.C), E_scheduled=self.E, E_executed=self.E_executed, N=self.N))
        self.next_time_s = end

    def rate_chain(self):
        pending = self.pending_command; c = self.cycle
        return dict(input_origin=pending.origin, r_ALINEA=pending.r_ALINEA,
            r_final_veh_h=pending.rate_veh_h, pending_request_id=pending.request_id,
            r_policy_pending_veh_h=None,
            nearest_reference_veh_h=self.step_mapped,
            pending_packet_status='SELECTED_ONLY_AT_COMPLETE_BOUNDARY', applied_request_id=c['applied_request_id'],
            r_policy_selected_veh_h=c['applied_command_veh_h'],
            r_policy_applied_veh_h=c['applied_command_veh_h'] if c['executed'] else 0, requested_quota=2,
            period_s=c['period_s'], cycle_application_delay_s=c['application_delay_s'],
            command_requested_s=pending.global_request_s)

    def accounting(self):
        keys=('C','C_nearest_reference','C_applied','E','N','requested_minus_nominal',
              'nominal_minus_actual','requested_minus_actual')
        if not self.observed_steps: return dict.fromkeys(keys)
        return dict(C=float(self.C),C_nearest_reference=float(self.C_mapped),
            C_applied=float(self.C_applied),C_selected=float(self.C_selected),E=self.E,
            E_scheduled_nominal=self.E,E_executed_nominal=self.E_executed,N=self.N,
            C_selected_exact_fraction=str(self.C_selected), C_applied_exact_fraction=str(self.C_applied),
            scheduled_minus_executed=self.E-self.E_executed, executed_minus_actual=self.E_executed-self.N,
            requested_minus_nominal=float(self.C-self.E),nominal_minus_actual=self.E-self.N,
            requested_minus_actual=float(self.C-self.N),C_exact_fraction=str(self.C),
            E_support='COMPLETE_PACKETS_ONLY',N_support='ALL_OBSERVED_ENTRY_BEGIN_INTERVALS',
            partial_cycle=not self.cycle['completed'],
            nearest_reference_is_not_cumulative_scheduler_output=True)


from src.candidate_a_cumulative_full_catalogue_20261014.policy import yellow_scope
