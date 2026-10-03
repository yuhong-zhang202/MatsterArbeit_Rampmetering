# S2 NOOP V2 engineering result — failed before TraCI connection

**2026-10-03 Europe/Rome; exploratory technical run, not a traffic result.** The one released start for `M3600_R900_S17_NOOP_TRACI_V2` was consumed. Status `FAILED / WORKER_FAILED`. No simulation step, trajectory, detector interval, vehicle trip or neutrality comparison was produced. Do not release ALINEA S3 from this result and do not retry V2.

## Exact released attempt

- Card: `inputs/M3600_R900_S17_NOOP_TRACI_V2/card.json`, SHA-256 `953c2d2f4b716a5ce937da7b4b1037c234486ae94d295e98f651fe68ee27d99e`; release: `RELEASE_NOOP_V2.json`, SHA-256 `6d7fbe1801675d0c2ee78ef74909e0d2fced8138b94d81f989c23f46d22bd233`. Static preflight with this release passed immediately before launch.
- Command: `.venv/bin/python scripts/stage6/standard_metering_20261003/runner.py launch --card artifacts/stage6_standard_metering_execution_20261003_v1/inputs/M3600_R900_S17_NOOP_TRACI_V2/card.json --approved-card-sha256 953c2d2f4b716a5ce937da7b4b1037c234486ae94d295e98f651fe68ee27d99e --release artifacts/stage6_standard_metering_execution_20261003_v1/RELEASE_NOOP_V2.json`, with approved elevated sandbox capability for local TraCI socket use.
- Host binding precheck: default sandbox `bind(127.0.0.1,0)` failed `PermissionError [Errno 1]`; the same pure-socket check passed with approved elevated capability. Neither precheck started SUMO or consumed a run.
- Actual start: 2026-10-02 22:58:12.292954 UTC; end 22:58:18.732437 UTC; guardian wall 6.429456 s, below 120 s. Worker PID 23466 exited 1. Receipt status `FAILED`, stop reason `WORKER_FAILED`, no automatic retry.
- Raw preserved at `data/raw/stage6_standard_metering_20261003_v1/M3600_R900_S17_NOOP_TRACI_V2/outputs/`. Receipt SHA-256 `e142b60e14e082d07f262a88652c5e68acce77056c782f5a49db0220621e3062`. Its 8 manifest files passed byte/hash readback; payload 5,104 bytes excluding the receipt. Four CSV files contain headers only. `sumo_stdout.log` and `sumo_stderr.log` are 0 bytes; no FCD or SUMO XML exists.
- Budget after attempt: baseline 18 starts + new 1 = public 19/40; control/technical 1/8. The receipt's `budget_after` snapshot was taken **before** writing its own 1,846-byte receipt, so it reports 197,940,442 shared raw bytes. Fresh post-receipt readback is **197,942,288/8,000,000,000 bytes**, including the older 197,935,338 bytes. This failed start counts against both start ceilings.

## Failure mechanism and limits of diagnosis

`worker_stderr.log` records `traci.exceptions.FatalTraCIError: Could not connect in 31 tries`; `worker_stdout.log` repeats `Connection refused` for `127.0.0.1:56311` at 0.1 s retries. The runner starts a SUMO subprocess with `--remote-port` and then attempts localhost TraCI. The available logs establish failure **before a TraCI session and before step 0**. They do not establish whether SUMO exited, started listening too late, could not bind, rejected the command/configuration, or encountered another startup error. The worker currently does not record the SUMO subprocess return code on connection failure; that omission is a diagnostic defect. Zero-byte SUMO stdout/stderr and absent XML cannot distinguish these possibilities. The standalone S17 OPEN baseline completed in 6.71 s; this does not determine its startup-to-listen time.

The worker's `finally` path closes any connection, then waits up to 3 s for its SUMO child and terminates/kills it if still running. After the failed attempt, an elevated read-only `ps -axo pid,ppid,command` check found no process matching the SUMO binary or this runner. This confirms no matching process remained at inspection time; the SUMO child's PID/exit code during the attempted connection was not captured, so the precise startup failure is still unidentified.

The one-second signal, feedback, meter service, E1 `[600,630)` readback, and OPEN–NOOP neutrality remain untested. Existing OPEN baselines cannot yet be used as matched TraCI comparators. The result is a technical failure, not evidence about ALINEA or freeway/urban response.

## Bounded next step for review

Before proposing any **new** start, revise a new runner/card revision so connection failure records SUMO child poll/return code and any stderr, and investigate whether timeout, socket binding or SUMO startup differs from the successful standalone path. Keep V1/V2 cards and failed raw immutable. Run only static or no-simulation diagnostics under the current authorization; any revised technical run needs a newly hash-bound card and independent release against the remaining public budget. Do not infer a `PASS` from the socket precheck, and do not relabel this consumed attempt as no-start.
