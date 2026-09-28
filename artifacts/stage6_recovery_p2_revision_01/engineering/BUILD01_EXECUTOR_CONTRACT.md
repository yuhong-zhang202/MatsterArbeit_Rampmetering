# BUILD01 executor contract — Proposed; no launch approval

This supplement implements only the proposed P2 netconvert BUILD01. It does not authorize a build, SUMO run, TraCI connection, GUI, retry, scientific inference, or formal experiment. `docs/EXPERIMENT_PROTOCOL.md` remains empty. Context reviewed: AGENTS, PROJECT_STATE (P2 authorized), DECISIONS, EXPERIMENT_PROTOCOL and recent WORKLOG. Current obstacle remains unresolved. Original build/launch drafts, earlier input revisions and raw evidence are preserved.

## Authorization and binding

`build01_executor.py` defaults to a no-process dry-run. Its production `--execute` path requires a separate JSON approval sidecar with the exact final card path/SHA, `status=user-approved`, the actual user approval quote/time, `scope=SG6-BUILD BUILD01 only`, and exactly one netconvert start. A file cannot independently prove that a human authorized it: the coordinating agent must create the sidecar only from an actual subsequent user approval. No active approval sidecar is delivered here. Synthetic fixture sidecars reference non-build cards and are left NOT_APPROVED.

The card remains `approved=false`, `authorized_starts=0`. The sidecar is separate to avoid changing the hash the user approved. The executor validates the fixed binary path/SHA, exact command, five network inputs, bound manifest and schemas, executor/test receipt and budget audit. It checks caller SUMO_HOME, rejects dynamic-loader overrides, passes a clean process-local environment, and verifies configured sources/output. Any changed source, script, test receipt or final card requires a new review/hash; no automatic approval transfer.

## Exclusive reservation and process lifetime

The production target is exactly `engineering/build_attempts/BUILD01`. It must not exist. An atomic mkdir exclusively consumes the one attempt; the parent directory and exclusive reservation are fsynced before Popen. Reservation and later started/terminal records are write-once. Any existing directory, including an empty claim left by a crash before reservation write, is consumed and cannot be retried. No code removes the claim.

The process uses an argv array, no shell, a new session/process group, and separate unbuffered stdout/stderr files. Stderr is retained verbatim; nonempty stderr is recorded for the mandatory engineering review. Nonzero exit, timeout, output overrun, start failure or executor exception consumes the attempt. Partial network/log files remain. A caught exception terminates the child group where possible. SIGTERM is followed by up to one second for exit, then SIGKILL and up to one second for confirmation. Failure to confirm termination is a terminal unknown state requiring manual inspection.

SIGKILL/power loss of the wrapper cannot execute Python cleanup. An existing claim without a terminal receipt must be treated as `terminal_unknown_consumed`. Do not relaunch. Inspect any started process manually before further work; a pid alone must never justify killing a potentially reused unrelated process. Persistent claim prevents budget reuse but is not an operating-system guarantee that a surviving child is killed after supervisor failure.

## Resource semantics requiring explicit user review

The registered numbers remain one netconvert attempt, zero retries, **30 s timeout trigger**, and **100,000,000-byte observed directory stop line**. Directory polling interval is 0.05 s; the fake-process tests verify timeout/overrun handling, not a maximum real process scheduling latency.

These are monitored thresholds, **not an absolute disk quota or an exact real-time deadline**. No finite maximum byte overshoot can be guaranteed from the available evidence: writing rate and scheduler delays are unbounded by this wrapper. Timeout detection may lag the trigger and termination may require up to two additional seconds of bounded waits; operating-system scheduling can delay them further. All observed excess is preserved and counted as failure. The terminal receipt itself and any final overrun record also use bytes; a final check records an envelope violation if metadata crosses the stop line. The contract deliberately does not claim a 100 MB hard storage envelope.

The approval sidecar must explicitly name `monitoring_semantics=polling_50ms_possible_overshoot_preserved`. If an absolute 100 MB limit is required, this version is **blocked**; do not reinterpret the proposed stop line as user approval of hard-limit relaxation. A separate filesystem quota or fully restricted output architecture would need implementation and review. Per-file RLIMIT_FSIZE alone cannot prove an aggregate directory bound.

## Result interpretation and recovery

Exit 0 plus a nonempty XML `<net>` only yields `completed_pending_compiled_review`. It does not accept geometry, lane connections/permissions, routing, requests, urban/TLS semantics, detector domains, path length, storage, or scientific suitability. Complete the P1/P2 compiled-network checks independently before any runtime materialization. No manual patch of compiled XML is allowed.

`build_receipt.json` is the primary terminal record; `final_envelope_violation.json`, if present, overrides any earlier apparent completed state. Missing terminal receipt is terminal unknown/consumed. Filesystem failure while writing a receipt cannot free the claim. Preserve all evidence and stop; another build would require a new explicit plan/card, never automatic retry under BUILD01.

## Offline verification

`test_build01_executor.py` writes a new isolated synthetic test tree and refuses to reuse it. Nineteen tests cover authorization/hash/scope, command/binary/environment/budget mismatch, pending cumulative audit, claim-before-process, duplicates/orphan claim, nonzero/start/monitor failure, timeout, observed byte overrun, symlinks, missing network and stderr preservation. Two subprocesses invoke only the project Python runtime as a fake process, including a real process-group timeout/termination test. Real SUMO/netconvert/TraCI/GUI counts remain zero. Python tests do not establish netconvert behavior or hard crash cleanup.

Historical project counts in the bound reconciliation are conservative lower bounds with explicit exclusions, never a complete lifetime total. They do not transfer unused historical run budgets to BUILD01.
