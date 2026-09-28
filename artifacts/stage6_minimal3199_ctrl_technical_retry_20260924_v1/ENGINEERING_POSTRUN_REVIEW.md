# Engineering post-run review — `MINIMAL3199_CTRL_S17_TECH_RETRY1`

**Disposition:** `TECHNICAL_FAILURE_PRE_SUMO`  
**Authorization:** consumed; no retry allowed.  
**SUMO starts:** 0.

The exact-card R02 launch invocation created the one-use reservation and started the Guardian handshake. Guardian rejected the START request with `INVALID_START_REQUEST`; the run ID is present in the exact `_run_binding` dispatch but absent from `SUPPORTED_RUN_BINDINGS` used by `guardian_main()`. No `SPAWNED` event was received, `simulator_pid` is null, and all SUMO traffic-output roles are absent. The reservation remains `GUARDIAN_HANDOFF_PENDING`, `retry_allowed=false`; no repair or retry was attempted.

The process-table query was denied by the operating system, so this review cannot independently verify Guardian process termination. The Guardian validation response and null simulator PID establish that no SUMO child was spawned.

## Resource and output inventory

- Recorded wall-clock before failure: 0.022354 s (below the 90 s trigger).
- Output inventory: 6,742 bytes total (below 60,000,000 bytes).
- `scenario_control.sumocfg`: 2,802 bytes, SHA-256 `1906f98e1e108a9019919d29fa4c9c6086659fdbedd231d16531ec275505650c`.
- `scenario_control.add.xml`: 3,940 bytes, SHA-256 `6b93195465eb66462394905fcf6bd450c8e3b863517bef436f5177f0a54c9470`.
- `guardian_stderr.log`: 0 bytes.
- Required traffic output roles present: 0/18. `output_manifest` and `execution_receipt` are absent.

The two staged files match the prelaunch expected hashes; no staged inputs were overwritten. The one-start reservation is consumed. No SUMO retry, other demand, treatment, seed23, B/C, or scientific-input modification occurred.
