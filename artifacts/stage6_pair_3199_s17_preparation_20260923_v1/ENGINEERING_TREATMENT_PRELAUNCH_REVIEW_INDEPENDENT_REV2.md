# Independent engineering prelaunch review — PAIR3199 delayed-R treatment REV2

**Disposition: PASS.** Blocker / Major / required Minor: **0 / 0 / 0**. Confidence: **High** for the exact-card, runner, runtime, path and fail-closed bindings. This review does not authorize a launch.

## Exact artifacts reviewed

- Treatment card REV2: `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV2.json`, SHA-256 `6e810adfe70c03ff321ba47a4fff6593323e5b4a78884ce8e6971ffd86bb8d25`.
- Runtime sidecar REV2: `runtime_bindings/PAIR_3199_R720_DELAYED_S17_PRELAUNCH_REV2.json`, SHA-256 `5c72fa902c828b2d85efc4f5adf4ff1d534526d2ccebdf352fb5c2d703cefb6f`.
- R02 runner: `artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py`, SHA-256 `482056a14df16af779ef8c8ad8182c313775a3392caa24e1e5224e9f0c1c8a37`.
- Adopted scoped witness contract: `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- Control final card SHA-256 `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`; control execution receipt SHA-256 `a6a1a67282ff9e19f0205ce4b681cef34315bc04ad65f9588d7b269fadcfd336`; output manifest SHA-256 `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`; control lifecycle review SHA-256 `6c8c2a381a5a2fc1102953ed58a5a1cd022a0c22789b0bbbd486d86a7b0ac799`.

## Findings

1. **Exact run binding and inputs: PASS.** The REV2 card is bound to the treatment run ID, exact versioned card path, package, dedicated output path and run-specific reservation path. Card, sidecar, runner and witness-contract hashes match the stated digests. All five input files exist and match the card's SHA-256 values. The embedded runtime object exactly matches the bound sidecar. Demand, input hashes/manifest, matched-control binding, output path, resource proposal and witness-contract binding are unchanged from REV1.
2. **Runtime and SUMO_HOME: PASS.** Read-only preflight verifies SUMO 1.26.0 binary path/hash, canonical SUMO_HOME, local additional schema path/hash, Python 3.13.0 executable/hash and bound package versions. No simulator process was started.
3. **Treatment/control isolation: PASS.** The treatment output directory and its one-use reservation are absent. The treatment's allowlist entry points only to REV2 and its REV2 sidecar. Control card and raw receipt/manifest bindings remain separate; the control raw records its original execution identity and output manifest. The card retains the historical control `NOT_EVALUABLE` state, screen/warning information, and `use_as_clean_normal_baseline=false`.
4. **Unauthorized launch refusal: PASS.** REV2 remains `PRELAUNCH_READY_AWAITING_AUTHORIZATION`, `execution_authorized=false`, `approval_required=true`, and `run_command=null`; its resource proposal is `PROPOSED_NOT_AUTHORIZED`. Runner source maps the treatment run ID to the exact REV2 card and runtime sidecar and admits it only for preflight. Ordinary launch verification uses `allow_prelaunch=false` and refuses this card with `CARD_NOT_EXACTLY_AUTHORIZED` before a reservation or process. `max_starts=1` and retries `0` are future bounds, not current authorization.
5. **Seven-marker chronology: PASS.** REV2 binds ordered, distinct markers for R demand activation, first scheduled R departure, first actual R departure, first R arrival near the merge, first meaningful merge exposure, first M deterioration, and State1 onset. The runner enforces exact list equality. The additional scheduled/actual departure and arrival/exposure distinctions improve traceability without changing scientific inputs or limits.
6. **Scoped gate and resources: PASS.** REV2 uses the adopted witness contract for this Stage 6 matched pair only; the old `LOW_R_BACKGROUND_ACCEPTABLE` gate is not a treatment release prerequisite. Proposed triggers remain 120 s and 90,000,000 decimal bytes, treatment-scoped, with 100 ms polling and possible overshoot. They are not authorized and do not inherit the control resource authorization.

## Verification

- Hashes, input provenance, REV1/REV2 invariant fields, card/sidecar equality, absent output/reservation, resource fields and seven chronology markers: PASS.
- R02 mock-only offline suite, run from `artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/` with `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python test_runner.py`: **19 tests passed**.
- Runner `py_compile`: PASS.
- Exact read-only preflight with approved card SHA `6e810adfe70c03ff321ba47a4fff6593323e5b4a78884ce8e6971ffd86bb8d25`: `PREFLIGHT_PASS_NO_PROCESS_STARTED`; `launch_authorized=false`.
- SUMO starts: 0; TraCI starts: 0; netconvert starts: 0; treatment output/reservation created: no.

## Boundary

Engineering prelaunch requirements for REV2 are satisfied. Resource authorization and treatment execution authorization remain absent. Runtime completion, treatment raw integrity, actual R merge exposure and any witness outcome remain unknown. REV1 and its engineering review remain preserved. No runner, card, sidecar, input, control raw, protocol, project state or worklog was changed in this review.
