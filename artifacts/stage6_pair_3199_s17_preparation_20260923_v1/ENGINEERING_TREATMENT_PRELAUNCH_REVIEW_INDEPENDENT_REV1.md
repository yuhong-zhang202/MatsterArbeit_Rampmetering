# Independent engineering prelaunch review — PAIR3199 delayed-R treatment

**Disposition: PASS.** Blocker / Major / required Minor: **0 / 0 / 0**. Confidence: **High** for exact-card, runner, runtime, path and fail-closed binding. This is an engineering review only; it does not authorize a launch.

## Reviewed binding

- Exact card: `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV1.json`, SHA-256 `263c63f356b02353655a5e8e06eb7089d527e82f8137f45a8ecaf63054fd38a4`.
- Runtime sidecar: `runtime_bindings/PAIR_3199_R720_DELAYED_S17_PRELAUNCH_REV1.json`, SHA-256 `184f640de731c3da26593e2da55ab81d5bb23232cb6e7a4c9a3764568d94a41`.
- Shared R02 runner: `artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py`, SHA-256 `76175f1361bd007b5d9d7382b625fd0c3b81b2022022e4093ec5aa747685cdf3`.
- Witness contract: `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`; the user's explicit adoption in this task is scoped to this Stage 6 matched pair, not the formal protocol.
- Exact control card: `PAIR_3199_CTRL_S17_CARD_FINAL_REV1.json`, SHA-256 `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`.
- Existing control execution receipt SHA-256 `a6a1a67282ff9e19f0205ce4b681cef34315bc04ad65f9588d7b269fadcfd336`; output manifest SHA-256 `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`.
- Control data/lifecycle review SHA-256 `6c8c2a381a5a2fc1102953ed58a5a1cd022a0c22789b0bbbd486d86a7b0ac799`.

## Findings

1. **Exact binding and inputs PASS.** Card, sidecar, runner and contract hashes match the supplied expected digests. All five card-bound scientific/runtime input artifacts (demand, additional, network, output roles and SUMO configuration) exist and their SHA-256 values match the card. The runtime sidecar is byte-hash-bound and its JSON content equals the card-embedded runtime object.
2. **Runtime/SUMO_HOME PASS.** Read-only preflight verified SUMO 1.26.0 binary path/hash, canonical SUMO_HOME, local additional schema path/hash, Python 3.13.0 executable/hash and bound package versions. No SUMO process was invoked by this review or preflight.
3. **Run isolation and output exclusivity PASS.** The allowlist binds this exact treatment run ID to its exact card path, package, treatment inputs, dedicated output directory and run-specific reservation filename. Both the treatment output directory and reservation are absent. The treatment binding is separate from the existing control final-card/output/reservation binding.
4. **Fail-closed authorization boundary PASS.** The card is `PRELAUNCH_READY_AWAITING_AUTHORIZATION`, `execution_authorized=false`, `approval_required=true`, `run_command=null`; resource values are explicitly `PROPOSED_NOT_AUTHORIZED`. R02 permits this exact treatment binding for read-only preflight only. Launch validation rejects it before reservation creation; the mock regression test asserts `CARD_NOT_EXACTLY_AUTHORIZED` with no process start. `max_starts=1` and retries `0` describe a possible future separately authorized run, not current authority.
5. **Scoped treatment contract PASS.** The exact reviewed witness-contract hash is bound. The old `LOW_R_BACKGROUND_ACCEPTABLE` gate is explicitly not a treatment-release prerequisite here. The five required chronology markers are present in order: R demand activation, first R departure, first meaningful merge exposure, first M deterioration, State1 onset. Control history stays bound to its original NOT_EVALUABLE disposition, fixed-screen failures and Candidate C/low-speed warning record; the card explicitly disallows calling it a clean normal baseline.
6. **Resource proposal PASS as proposal only.** Treatment-only triggers are positive finite values: **120 seconds** and **90,000,000 decimal bytes**, with 100 ms output polling and possible overshoot. They are scoped only to `PAIR_3199_R720_DELAYED_S17`, marked `PROPOSED_NOT_AUTHORIZED`, and are not inherited from the control authorization.

## Verification performed

- SHA-256 and card/sidecar/input consistency checks: PASS.
- R02 offline mock-only suite, from `artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/`: `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python test_runner.py` — **19 tests passed**.
- Read-only exact-card preflight, from the repository root: `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py preflight --repo "$PWD" --card artifacts/stage6_pair_3199_s17_preparation_20260923_v1/PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV1.json --approved-card-sha256 263c63f356b02353655a5e8e06eb7089d527e82f8137f45a8ecaf63054fd38a4` — `PREFLIGHT_PASS_NO_PROCESS_STARTED`; `launch_authorized=false`.
- Python `py_compile` for runner: PASS.
- `pytest` invocation was unavailable because `pytest` is not installed in the project environment; the same test file was executed successfully with its built-in `unittest` entry point.
- SUMO starts: 0; TraCI starts: 0; netconvert starts: 0; treatment output/reservation created: no.

## Boundary

Engineering prelaunch requirements are satisfied. Resource limits and execution remain unauthorized. This review does not establish future runtime completion, output size, treatment lifecycle, merge exposure or witness outcome. No control raw, scientific input, runner, card, sidecar, protocol, classifier or threshold was modified.
