"""Explicit finite-diagnostic loop seam, with no native launcher or run card.

This unexecuted version is for offline review. A future native use needs a new
source binding, independent reader, reviews and explicit execution authority.
It cannot qualify formal or general service under demand/receiving constraints.
"""
import json
from pathlib import Path

from src.candidate_a_native_yellow_minqual_20261015.bridge import _diagnostic_loop as historical_loop
from src.candidate_a_native_yellow_minqual_20261015.bridge import encoded
from src.candidate_a_service_scope_20261015.adapter import StepAdapter
from src.candidate_a_service_scope_20261015.policy import DiagnosticTargetNotMet, require_purpose


def _diagnostic_loop(conn, worker, capture, output, resources, process, start_time,
                     adapter, producer, *, purpose):
    require_purpose(purpose)
    if not isinstance(adapter, StepAdapter) or adapter.purpose != purpose:
        raise ValueError('EXPLICIT_DIAGNOSTIC_ADAPTER_REQUIRED')
    output = Path(output)
    # Create this dedicated receipt before any inherited setters or advances.
    # Existing output cannot be silently overwritten.
    with (output/'service_scope_receipt.json').open('x') as receipt, \
            (output/'service_scope_events.jsonl').open('x') as events:
        error = None
        try:
            return historical_loop(conn, worker, capture, output, resources,
                                   process, start_time, adapter, producer)
        except Exception as exc:
            error = exc
            raise
        finally:
            # The historical loop can stop before its next event flush. This
            # independent complete stream preserves the final assessment too.
            for event in adapter.ledger.events:
                events.write(json.dumps(event, default=encoded, allow_nan=False)+'\n')
            assessed = (adapter.ledger.cycle or {}).get('service_diagnostic')
            json.dump(dict(
                purpose=purpose, implementation_status='OFFLINE_REVIEW_NO_NATIVE_RELEASE',
                status=('DIAGNOSTIC_TARGET_NOT_MET_CAUSE_UNESTABLISHED'
                        if isinstance(error, DiagnosticTargetNotMet) else
                        'HARD_OR_UNKNOWN_GATE_STOP' if error is not None else
                        'FINITE_LOOP_COMPLETED_NOT_GENERAL_QUALIFICATION'),
                error=None if error is None else type(error).__name__+':'+str(error),
                accounting=adapter.ledger.accounting(), service_diagnostic=assessed,
                partial_cycle=bool(adapter.ledger.cycle and not adapter.ledger.cycle['completed']),
                general_service_qualified=False, actuator_fault_established=False,
                new_packet_after_under_target=False, automatic_retry=False,
                formal_use_authorized=False), receipt, default=encoded, allow_nan=False, indent=2)
            receipt.write('\n')
