# Guardian ownership clarification — read-only proposal

No source edit, worker/child test or native process was started. This adds a concrete ownership constraint to PIPELINE_DESIGN_V1, rather than assuming an unverified shared process group.

## Actual current launch path

The natural bridge calls `protected_worker().launch_sumo_process` and receives its Popen object. The protected worker's implementation is exactly `subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env)` in `scripts/candidate_a_qualification_20261008_v1/worker.py:86`. It supplies neither start_new_session nor process_group. The installed Python3.13 `subprocess.py:819` defaults start_new_session=False, and process_group=None is converted internally to -1. Thus the Python launch configuration inherits the worker's group/session; it does not request a separate SUMO session.

If a thin guardian creates the sole Python execute worker with start_new_session=True, that worker initially leads a dedicated new session/group, and the current SUMO launch inherits it. This is a source-level startup relationship, not an observed native PID/PGID result. SUMO has not been launched during this task, and source/binary/compiler equivalence remains unverified. The guardian must verify actual identities at future launch rather than generalize this source argument into a cleanup guarantee.

The current bridge does not immediately persist native PID/PGID/SID. startup_context binds command/environment but is written before Popen, and final receipts may never appear if the worker dies. The existing child ResourceWatchdog knows the direct Popen object, but the outer guardian currently lacks that early native identity and cannot safely reconstruct it after reparenting merely from a process name.

## Minimum spawn-only hook to review before implementation

Keep policy/adapter/producer byte-identical. A small bridge hook immediately after Popen returns and before TraCI connection, control setters or simulation advances should:

1. obtain direct native PID from the owned Popen object, worker PID/parent PID and os.getpgid/os.getsid for both live worker and native; surround reads with Popen.poll checks so an already-exited child is not treated as a live identity;
2. persist an exclusive early owned_process_identity record tied to run ID and exact card/release, with each observation's time/support/status and the expected guardian/worker group; unreadable fields remain UNKNOWN;
3. require actual native PGID/SID to equal the dedicated worker PGID/SID before connection/control. An exited child, unknown observation or unexpected separate group/session stops the task and enters the existing direct-owned-Popen terminate/kill/wait cleanup, with failure evidence retained;
4. let the outer guardian read/validate this identity against its own direct worker Popen PID and dedicated group/session before relying on group cleanup. Do not discover arbitrary same-name processes, trust a stale PID-only file, or signal an unrelated group.

The direct worker lifecycle should also record process birth/identity support if the implementation intends to act on a retained PID after reparenting; an exited/reused PID must not be mistaken for the prior child. Where ownership cannot still be established, report cleanup UNKNOWN instead of attempting a broad kill. The chosen restricted contract is that the exact worker/native remain in their initially verified owned group; deliberate future detachment or changed spawn flags is outside it and must fail verification, not silently extend cleanup scope.

This is spawn metadata and resource supervision, not a new signal policy, control command or algorithm. However, it **does change bridge source bytes**, so the preparation cannot truthfully claim all four behavioral-module files are exactly616. Root/science should approve this minimal exception and bind a new exact bridge source, preserving the old616 file/report. A monkey-patch or hidden import override would obscure the actual launch closure and is not recommended merely to keep a file hash unchanged.

## Successful, hanging and early-exit chains

- **Normal completion:** child watchdog remains active during normal connection close and native wait. Worker writes normal native EOF/log state and full cost through cleanup. Outer guardian observes worker exit, verifies no bound owned native/group members remain, and records its own elapsed/cleanup status. A zero worker exit alone is insufficient proof of no surviving child or native data integrity.
- **Blocked connection/loop/cleanup:** keep the existing child watchdog; the thin parent independently owns the whole worker lifecycle/deadline and cleanup reserve. On timeout, signal only the verified dedicated group, allow bounded terminate grace, then kill/reap verified remaining owned members. Record both trigger and actual cost including cleanup/overshoot. If the worker cannot finalize, preserve partial files and outer receipt, mark missing native EOF UNKNOWN and reserve full/actual resource cost. No retry is released automatically.
- **Worker exits before normal native cleanup:** the parent checks its verified group/native identity even when the worker itself has already exited. A live native in the previously verified group must be cleaned up; it is not ignored because Popen.poll(worker) returned an exit code. If native identity changed, became unobservable or group relation cannot be re-established, retain UNKNOWN and stop qualification/resource settlement. Do not silently declare cleanup complete.
- **Worker fails between Popen and identity persistence:** the outer dedicated group still provides the configured inherited-startup boundary, but the missing native identity is explicitly incomplete coverage. Clean the owned group when its ownership remains supported; never fabricate a native PID/PGID or a normal EOF. This case requires one bounded fake-child fault check before claiming the guardian path ready.

No general daemon management, external process scanning/cleanup framework or detached-child support is proposed. If the exact SUMO binary were observed to create a distinct session, group-only supervision would be insufficient; stop and review a direct-child identity/cleanup change before any control, rather than extending permissions ad hoc.

## Small future offline check only after scope GO

Use short ordinary Python worker/child processes, never SUMO or TraCI, to verify the selected group/session contract and one composite normal/timeout/worker-early-exit sequence, including no surviving verified child and truthful missing-identity/EOF status. Reuse the existing child watchdog where applicable. This is a resource ownership check, not a traffic fault matrix. No such subprocess check has been run yet.
