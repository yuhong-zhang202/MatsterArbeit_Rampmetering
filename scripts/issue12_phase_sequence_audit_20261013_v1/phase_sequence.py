"""Ordered offline audit of the frozen packet900 run; no simulator imports."""
from decimal import Decimal, InvalidOperation
import math

BEGIN = 1200
END = 1272
PERIOD = 8
PROGRAM = "I12_PACKET8"
SEQUENCE = "GGGGyyrr"
PHASE = {"G": 0, "y": 1, "r": 2}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def time_is(value, expected):
    return type(value) in (int, float) and math.isfinite(value) and value == expected


def phase_is(value, expected):
    return type(value) is int and value == expected


def readback_is(row, time_s, phase, state, switch, program=False):
    return (isinstance(row, dict) and time_is(row.get("time_s"), time_s)
            and phase_is(row.get("phase"), phase) and row.get("state") == state
            and time_is(row.get("nextSwitch_s"), switch)
            and (not program or row.get("program") == PROGRAM))


def audit_phase_sequence(tls_rows, post_rows, ack_rows, phase_requests, duration_requests):
    """Check all motion intervals, pending switches, and after-ACK setters.

    Inputs retain original order and duplicates. TLS time is motion BEGIN;
    post time is ACK end. At a due native transition, phase_before can still
    be the preceding phase. No observation at 1272 is invented for a tenth G.
    """
    require(len(tls_rows) == len(post_rows) == END - BEGIN,
            "TLS_POST_COVERAGE")
    require(len(ack_rows) == 2 * (END - BEGIN), "ACK_COVERAGE")
    require(len(phase_requests) == len(duration_requests) == 18,
            "REQUEST_TRACE_COVERAGE")
    cycles = []
    for index, (tls, post) in enumerate(zip(tls_rows, post_rows)):
        t = BEGIN + index
        offset = index % PERIOD
        cycle_begin = t - offset
        cycle_end = cycle_begin + PERIOD
        state = SEQUENCE[offset]
        phase = PHASE[state]
        try:
            tls_time = Decimal(tls.get("time", "NaN"))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("TLS_TIME_INVALID") from None
        require(tls_time.is_finite() and tls_time == t, "TLS_TIME_ORDER")
        require(tls.get("id") == "ramp_mid" and tls.get("programID") == PROGRAM,
                "TLS_IDENTITY")
        require(tls.get("state") == state and tls.get("phase") == str(phase),
                "CONTINUOUS_G_Y_R_ORDER")
        require(time_is(post.get("time_begin_s"), t)
                and time_is(post.get("time_end_s"), t + 1)
                and post.get("accounting_complete") is True,
                "POST_INTERVAL_BINDING")
        require(post.get("motion") == state, "TLS_POST_MOTION_BINDING")
        first, verified = ack_rows[2 * index:2 * index + 2]
        require(time_is(first.get("requested_target_s"), t + 1)
                and first.get("ACK_received") is True
                and first.get("actual_readback_s") is None
                and first.get("actual_time_verified") is False
                and time_is(verified.get("requested_target_s"), t + 1)
                and verified.get("ACK_received") is True
                and time_is(verified.get("actual_readback_s"), t + 1)
                and verified.get("actual_time_verified") is True,
                "ACK_CONTINUITY_BINDING")
        observation = post.get("phase_observation", {})
        after_switch = cycle_begin + (4 if offset < 4 else 6 if offset < 6 else 8)
        before_state = "r" if offset == 0 and index else "y" if offset == 6 else state
        before_switch = cycle_begin if offset == 0 and index else (
            cycle_begin + 6 if offset == 6 else after_switch)
        require(phase_is(observation.get("phase_after"), phase)
                and observation.get("state_after") == state
                and time_is(observation.get("next_switch_after_s"), after_switch)
                and phase_is(observation.get("phase_before"), PHASE[before_state])
                and observation.get("state_before") == before_state
                and time_is(observation.get("next_switch_before_s"), before_switch),
                "NATIVE_PHASE_SWITCH_CLOCK")
        if offset == 0:
            cycles.append({"begin_s": cycle_begin, "end_s": cycle_end,
                           "motion_sequence": SEQUENCE,
                           "green_begin_s": cycle_begin,
                           "yellow_begin_s": cycle_begin + 4,
                           "red_begin_s": cycle_begin + 6,
                           "first_red_ACK_s": cycle_begin + 7,
                           "phase_durations_s": {"G": 4, "y": 2, "r": 2}})
    for cycle_index, cycle in enumerate(cycles):
        begin, end = cycle["begin_s"], cycle["end_s"]
        yellow, red = phase_requests[2 * cycle_index:2 * cycle_index + 2]
        for record, t in ((yellow, begin + 4), (red, begin + 7)):
            require(time_is(record.get("time_s"), t)
                    and phase_is(record.get("cycle_id"), cycle_index)
                    and time_is(record.get("cycle_end_s"), end)
                    and phase_is(record.get("requested_quota"), 2)
                    and phase_is(record.get("actual_quota_N_G"), 2)
                    and len(record.get("requests", [])) == 1,
                    "PHASE_REQUEST_CYCLE_BINDING")
        ycall, rcall = yellow["requests"][0], red["requests"][0]
        require(ycall.get("method") == "setPhase" and phase_is(ycall.get("value"), 1)
                and time_is(ycall.get("time_s"), begin + 4)
                and ycall.get("call_completed") is True
                and readback_is(yellow.get("actual_readback"), begin + 4, 1, "y", begin + 6),
                "YELLOW_SETTER_AFTER_GREEN_ACK")
        require(rcall.get("method") == "setPhaseDuration" and phase_is(rcall.get("value"), 1)
                and time_is(rcall.get("time_s"), begin + 7)
                and rcall.get("call_completed") is True
                and readback_is(rcall.get("actual_readback"), begin + 7, 2, "r", end, True)
                and readback_is(red.get("actual_readback"), begin + 7, 2, "r", end),
                "RED_SETTER_AFTER_RED_ACK")
        attempted, verified = duration_requests[2 * cycle_index:2 * cycle_index + 2]
        for request in (attempted, verified):
            require(time_is(request.get("time_s"), begin + 7)
                    and time_is(request.get("cycle_end_s"), end)
                    and request.get("method") == "setPhaseDuration"
                    and phase_is(request.get("value"), 1), "DURATION_REQUEST_BINDING")
        require(attempted.get("status") == "ATTEMPTED"
                and attempted.get("call_completed") is False
                and verified.get("status") == "READBACK_VERIFIED"
                and verified.get("call_completed") is True
                and verified == dict(rcall, status="READBACK_VERIFIED", cycle_end_s=end),
                "DURATION_TRACE_READBACK")
    return {"status": "PASS_ORDERED_TLS_ACK_SWITCH_AUDIT",
            "observed_motion_BEGIN_s": [BEGIN, END - 1],
            "last_observed_ACK_s": END, "cycles": cycles,
            "observed_intercycle_r_to_G": len(cycles) - 1,
            "no_tenth_green_observation": True,
            "native_safety_proven": False, "rate_qualified": False}
