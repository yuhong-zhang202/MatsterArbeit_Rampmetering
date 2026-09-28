# RI3350 Control finalization proposal — Revision 2

Status: **CONDITIONAL USER AUTHORIZATION RECORDED / FINAL CARD NOT YET CREATED**

Scope: exactly `RI3350_CTRL_S17_attempt1`. This revision supersedes the
execution-status language in Revision 1 while preserving its engineering
evidence. It does not amend the classifier, scientific design, demand, geometry,
formal experiment protocol, or any future run's resource contract.

## User authorization and sequence

The user has conditionally authorized this one control start: after final
engineering, data, and scientific prelaunch reviews each return PASS with
Blocker/Major/required Minor = `0/0/0`, create a final exact card, run its
no-process preflight, then execute exactly once using the exact card digest.
No additional user approval is required if and only if those conditions pass.
Preflight alone is not authority to launch; authority is the user's conditional
authorization plus the three passing reviews. Any material input or code change
invalidates the corresponding reviews and requires reassessment before launch.

Hard limits are one SUMO start total and zero technical retries. Every start
attempt consumes the unique reservation. Regardless of result, perform the
specified complete post-run review and then STOP. No transition, seed23, B/C,
other demand point, retry, or other SUMO/netconvert/TraCI run is covered.

## Exact one-run resource contract

- Wall-clock monitored stop trigger: **180 seconds** from Guardian child start.
- Output-tree monitored stop trigger: **300,000,000 bytes** (decimal MB),
  including materialized files and simulator output under the exclusive run
  directory.
- Guardian poll interval: **100 ms**. User accepts minor overshoot between
  polls. This is not a strict quota and does not promise that output remains
  below the byte trigger at every instant.
- On either observed trigger, send SIGTERM to the simulator process group, wait
  up to 5 seconds, then SIGKILL the group if needed.
- These triggers apply only to this exact run and must not be generalized to
  future runs or treated as thesis-wide policy.

## Guardian and final-card bindings

The final card must bind
`runtime_binding.guardian_runner_sha256` to the reviewed exact `runner.py`
SHA-256, plus all current immutable scientific inputs, executable/runtime
identity and output-role-source hashes. It must specify the exact output
directory, `max_starts=1`, `technical_retries=0`, and
`progression_allowed=false`.

The Guardian returns READY before it can start the simulator. It owns the
simulator process group independently of the launcher. Launcher pipe EOF causes
child termination and Guardian finalization; normal DISARM follows verified
manifest/receipt handoff and a file-fsynced atomic reservation replacement
with parent-directory fsync. Mock fixtures cover abrupt launcher exit and this
ordering. Guardian/host failure and power loss are not covered. No real SUMO
compatibility or output-structure claim is made before raw exists.

## Prelaunch state

The prior `control_card_DRAFT_NOT_AUTHORIZED.json` and
`readiness_register.json` are preserved historical artifacts, not execution
inputs. Current readiness is recorded in
`readiness_register_CONDITIONAL_PRELAUNCH_REV2.json`. Until the last scientific
prelaunch review is recorded PASS with `0/0/0`, the final exact card must not be
created and no start may occur. Following a passing review, card creation and
launch are permitted by the conditional authorization described above; compute
the exact card SHA-256, run the read-only preflight, and use that exact digest
once for launch. Any result consumes the only attempt; then post-run audit and
STOP.

`docs/EXPERIMENT_PROTOCOL.md` remains unchanged and unfrozen. R03 realized
pairing, R05 real-raw application and R06 actual ramp exposure are deferred
until their relevant raw exists; they are not prelaunch blockers for this R=0
control. G6 remains `UNKNOWN`, not `PASS`, and cannot establish suitability or
release another run.
