"""Finite packet diagnostic only; no general-service controller qualification."""
from copy import deepcopy

from src.candidate_a_cumulative_full_catalogue_20261014.policy import Ledger as HistoricalLedger
from src.candidate_a_cumulative_full_catalogue_20261014.policy import require

PURPOSE = 'FINITE_PACKET_DIAGNOSTIC_ONLY'
UNDER_TARGET = 'DIAGNOSTIC_TARGET_NOT_MET_CAUSE_UNESTABLISHED'


def require_purpose(purpose):
    require(type(purpose) is str and purpose == PURPOSE,
            'UNSUPPORTED_USE_REQUIRES_GENERAL_SERVICE_CONTROLLER')


class DiagnosticTargetNotMet(ValueError):
    """An observed diagnostic target was missed; actuator fault is unproven."""
    def __init__(self, evidence):
        self.evidence = deepcopy(evidence)
        super().__init__(UNDER_TARGET)


class Ledger(HistoricalLedger):
    def __init__(self, command=750, end_s=1296, *, purpose):
        require_purpose(purpose)
        super().__init__(command, end_s)
        self.purpose = purpose

    def begin_step(self, t, command=None):
        # Check before registering a new command or selecting another packet.
        self.require_diagnostic_target()
        return super().begin_step(t, command)

    def observe_service_context(self, time_s, pending):
        require(self.cycle is not None and self.prepared_time_s == time_s,
                'SERVICE_CONTEXT_TIME_NOT_BOUND')
        require(pending['time_s'] == time_s and pending['cycle_id'] == self.cycle['cycle_id'],
                'SERVICE_CONTEXT_CYCLE_NOT_BOUND')
        # These are the original adapter's validated observations. No new
        # distance, readiness, saturation or causal threshold is introduced.
        self.cycle.setdefault('service_context', []).append(deepcopy(dict(
            time_s=time_s, motion=pending['motion'],
            storage_ids=sorted(pending['storage']),
            vehicle_states=pending['vehicle_states'],
            receiver=pending['receiver'],
            native_receiver_decision=pending['native_receiver_decision'],
            readiness_interpretation='BOUND_STATES_ONLY_NO_READY_OR_SATURATION_CLAIM')))

    def assess_completed_packet(self):
        """Call only after the original adapter's full reconciliation succeeds."""
        if not self.cycle['completed']:
            return
        if 'service_diagnostic' in self.cycle:
            return self.cycle['service_diagnostic']
        end = self.next_time_s
        actual = sum(self.cycle['N_' + phase] for phase in ('G', 'y', 'r'))
        require(type(actual) is int and actual >= 0, 'UNKNOWN_ACTUAL_PACKET_N')
        status = ('FINITE_DIAGNOSTIC_TARGET_OBSERVED_NOT_GENERAL_QUALIFICATION'
                  if actual == 2 else UNDER_TARGET if actual < 2
                  else 'SERVICE_PACKET_QUOTA_EXCEEDED')
        evidence = dict(
            event='FINITE_PACKET_DIAGNOSTIC_ASSESSED', purpose=self.purpose,
            cycle_id=self.cycle['cycle_id'], begin_s=self.cycle['begin_s'],
            end_s=end, completed=True, requested_quota=2, actual_packet_N=actual,
            status=status, actuator_fault_established=False,
            cause='UNESTABLISHED', general_service_qualified=False,
            C_exact_fraction=str(self.C), E=self.E, N=self.N,
            requested_minus_actual_exact_fraction=str(self.C-self.N),
            service_context=deepcopy(self.cycle.get('service_context', [])),
            under_target_service_recovery=('NOT_ATTEMPTED_DIAGNOSTIC_STOPS'
                                           if actual < 2 else 'NOT_APPLICABLE'),
            continuation_authorized=False)
        self.cycle['service_diagnostic'] = evidence
        self.events.append(evidence)
        return evidence

    def require_diagnostic_target(self):
        if self.cycle is None or not self.cycle['completed']:
            return
        evidence = self.cycle.get('service_diagnostic')
        require(isinstance(evidence, dict), 'UNKNOWN_COMPLETED_SERVICE_DIAGNOSTIC')
        actual = evidence['actual_packet_N']
        require(type(actual) is int and actual >= 0, 'UNKNOWN_ACTUAL_PACKET_N')
        require(actual <= 2, 'SERVICE_PACKET_QUOTA_EXCEEDED')
        if actual < 2:
            raise DiagnosticTargetNotMet(evidence)

    def accounting(self):
        result = super().accounting()
        # Preserve all historical accounting values, including the zero-step
        # null contract. Diagnostic scope is available independently as purpose.
        if self.observed_steps:
            result.update(purpose=self.purpose, general_service_qualified=False,
                          diagnostic_target_status=(self.cycle.get('service_diagnostic') or {}).get('status'),
                          debt_recovery_policy='HISTORICAL_ALGORITHM_UNCHANGED_STOP_ON_COMPLETE_UNDER_TARGET')
        return result
