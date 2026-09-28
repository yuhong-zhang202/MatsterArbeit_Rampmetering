# RI3350 Control finalization proposal — Revision 1

Status: **ENGINEERING PROPOSAL / NOT A LAUNCH AUTHORIZATION**

Scope: `RI3350_CTRL_S17_attempt1` only. This note records the user-accepted
resource-monitoring semantics and Guardian behavior for eventual exact-card
binding. It does not authorize a process start and does not amend
`docs/EXPERIMENT_PROTOCOL.md`.

The user's acceptance covers the 180 s / 300,000,000-byte monitored triggers,
100 ms polling with accepted overshoot, and the requirement not to leave the
child orphaned after launcher failure while Guardian remains operational. It
does not waive the separate conditional execution gates or authorize a launch;
the current card remains `DRAFT_NOT_AUTHORIZED`.

## Exact one-run resource contract

- Maximum wall-clock monitoring trigger: **180 seconds** from Guardian child
  start. At or after the threshold, Guardian requests termination.
- Output-tree monitoring trigger: **300,000,000 bytes** (decimal MB), including
  generated configs/logs and simulator artifacts present under the exclusive
  output directory.
- Poll interval: **100 ms**. The trigger is polling-based and can overshoot
  between observations. It is not a strict filesystem quota or a promise that
  output can never exceed 300,000,000 bytes.
- On either trigger: send SIGTERM to the simulator process group; wait up to
  5 seconds; send SIGKILL to that group if it remains.
- These numeric values are approved for this exact run only. They must not be
  generalized to another run or treated as thesis-wide resource policy.

## Guardian lifecycle bound into the runner

The future exact card must contain
`runtime_binding.guardian_runner_sha256` equal to the exact `runner.py`
SHA-256. The Guardian is launched as a separate process and must return READY
before START can be sent. The Guardian itself spawns the one simulator process
in a new process group and owns its process handle. A one-use reservation is
persisted and its containing directory fsynced before materialization/Guardian
startup; Guardian startup failure consumes the attempt but cannot spawn the
simulator.

The launcher-to-Guardian control pipe is the liveness signal. If the launcher
exits, crashes, or is terminated, EOF causes Guardian to terminate the child
group, wait for the child, write `output_manifest.json` and
`execution_receipt.json` if needed, and durably record cleanup/finalization in
the reservation. On normal completion, Guardian stays armed until it verifies
the manifest/receipt digests, fsyncs the reservation file before atomic
replacement, fsyncs the containing reservation directory after replacement,
and only then acknowledges DISARMED.
No technical retry or progression to another point is possible.

This covers launcher failure while Guardian remains operational. Guardian's
own crash or kill, operating-system failure, machine shutdown, or power loss is
not covered; these conditions may prevent cleanup. A strict disk quota would
require a separate, independently tested bounded filesystem; no disk image or
mount is part of this proposal.

## Verification evidence and limits

The R02 suite runs offline with fake Python children only. It covers normal
handoff, startup failure/no-spawn, wall-clock and output triggers, launcher
pipe closure, abrupt launcher-process exit and Guardian self-finalization, and
card/runner hash validation. A fixture verifies atomic-replace then
parent-directory-fsync ordering, and normal handoff records the durability
marker before DISARMED. It does not start SUMO, netconvert, TraCI, or a
SUMO-backed controller, and it does not validate simulator compatibility or
output semantics.

## Remaining authorization gates

The existing card remains `DRAFT_NOT_AUTHORIZED`. Before any execution, the
user-approved exact card must bind the above one-run values, exact runner hash,
all existing immutable input and environment hashes, output location, one
start/retry-zero constraints, and exact card SHA-256. Passing preflight alone
is not execution authorization. The next safe action is an offline exact-card
preflight after that card is explicitly approved; no launch is authorized by
this proposal.
