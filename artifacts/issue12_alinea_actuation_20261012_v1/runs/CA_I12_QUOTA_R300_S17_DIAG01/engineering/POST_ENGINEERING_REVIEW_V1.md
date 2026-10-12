# R300 DIAG01 engineering post-review V1

**Result: bounded technical failure, evidence preserved; not a completed cycle or qualification.**

Exactly one native child (SUMO PID78567, CLI78565, launcher78542; port59723) executed. Actual ACK and accounted prefix ended at1210 s. Whole CLI elapsed137.672064 s, bridge monitored through cleanup137.296703 s. Startup connected after24.536846 s (234 connection attempts to the same child, not234 starts). Watchdog reason/error null; EOF owned native logs bound with no observed critical message; native process exit0 and CLI exit1 represent different outcomes.

Exact failure: `ValueError:unsupported phase request`. At first actual red ACK1210, new bridge `policy_after_ack` called old protected `worker.request_phase(..., 'setPhaseDuration', remaining)`; worker.py98–105 accepts only setProgram/setPhase and raises before issuing the native duration call. This is an adapter/helper compatibility defect. No traffic-safety rejection or native SUMO failure is established by that error. Fix belongs only in the new namespace: explicit audited native setPhaseDuration request, keeping guard, thresholds, models and old worker unchanged. No fix or retry executed in this receipt.

Partial cycle1200–1210: quota2; green closed after actual N_G2 at1204; actual phase exposure G4/y5/r1; N_y0/N_r0; crossings R_flow.0 and R_flow.1. Cycle completed=false. Prefix C/appliedC=0.8333333333333334, E0 (no completed cycle), N2. Do not interpret E0 or this partial cycle as rate qualification. No first-red checkpoint file was finalized because the failing red-duration request occurred before checkpoint creation.

Final journal schema/counts, complete raw hashes and source/protection matching are in EXECUTION_RECEIPT_V1.json and RAW_FINAL_SHA256_V1.json. Terminal-arrival post-run audit remains pending independent data review. No new start beyond this one, no900, no retry, no formal experiment. The exact source is hash-bound uncommitted snapshot at baseline HEAD20e5e83, not a claim that baseline source contains this policy.
