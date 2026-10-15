"""New explicit diagnostic seam; all historical safety checks remain active."""
from src.candidate_a_native_yellow_minqual_20261015.adapter import StepAdapter as HistoricalAdapter
from src.candidate_a_service_scope_20261015.policy import Ledger, DiagnosticTargetNotMet, require_purpose


class StepAdapter(HistoricalAdapter):
    def __init__(self, observe, command=750, end_s=1296, numerical_authority=None,
                 yellow_diagnostic_mode=False, *, purpose):
        require_purpose(purpose)
        super().__init__(observe, command, end_s, numerical_authority, yellow_diagnostic_mode)
        self.purpose = purpose
        self.ledger = Ledger(command, end_s, purpose=purpose)

    def _prepare_step(self, conn, time_s):
        result = super()._prepare_step(conn, time_s)
        if time_s >= 1200:
            self.ledger.observe_service_context(time_s, self.pending)
        return result

    def _reconcile_step(self, conn, warning_observation):
        # The historical implementation verifies actual signal/entry binding,
        # accounting, safety, warning and EOF/checkpoint gates first. An actual
        # hard-gate exception must not be replaced by a service classification.
        row = super()._reconcile_step(conn, warning_observation)
        if self.ledger.cycle is not None:
            self.ledger.assess_completed_packet()
        try:
            self.ledger.require_diagnostic_target()
        except (DiagnosticTargetNotMet, ValueError) as exc:
            self.paused = True
            row.update(status='STOP_OBSERVED_AFTER_STEP',
                       reasons=[str(exc)], service_diagnostic=self.ledger.cycle['service_diagnostic'])
            raise
        return row
