# Independent engineering prelaunch review — repaired PAIR3199 treatment

**Disposition: PASS for preparation and read-only preflight only.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0.  
**Execution authorization:** None. `SUMO starts = 0`; TraCI/netconvert starts = 0/0.

## Context preflight and current boundary

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/WORKLOG.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`. Current phase is offline v5 common-input repair followed by a separately prepared treatment proposal. Stage 6 is partial; O2 is unresolved; formal protocol is unchanged and unfrozen. D-005 scopes the exploratory contract to this pair. D-006's one-start treatment authorization is consumed. The previous treatment remains `NOT_EVALUABLE` and is not reused or reinterpreted.

Also inspected the v5 repair receipt, invariant report and independent engineering/data/scientific reviews; the new preparation package's exact draft card, runtime binding, R02 runner/test code, read-only preflight, engineering/provenance receipts, treatment inputs and post-run gate plan; plus the old treatment status in project records. Review was read-only except for these two independent review artifacts.

## Exact binding and provenance

- New card SHA-256: `593cabd4c82a8b7b735e6ebc000d836bebab80a9c8962e20f2865a5bbf4dbed0`; status `DRAFT_NOT_AUTHORIZED`, `execution_authorized=false`, `approval_required=true`, `run_command=null`, max starts 1, retries 0, progression disabled.
- Runtime sidecar SHA-256: `d1d86b35ffa0a55ccb4ed5ed0f4e654fc6a1ecfc0c722cdbd802ed0cf465932f`; it binds SUMO 1.26.0 binary/version/SUMO_HOME/schema and the exact Python executable/package versions. Runner SHA-256: `86faab71ea187be4f46fb89d2436fbfb679324297166c63ee376805c362fbdcf`.
- Card, sidecar and runner agree on `PAIR_3199_R720_DELAYED_S17`. The shared R02 runner has an additive exact-card binding for this new package and distinct output/consumption paths; the prior `SUPPORTED_RUN_BINDINGS` entry and old treatment path remain separate. The runner resolves the repaired card path explicitly, then checks run ID and card/package/output/consumption/kind binding. Existing fail-closed checks remain for approved card hash, input/runtime/runner hashes, SUMO_HOME, output exclusivity, and authorization state.
- Treatment demand SHA-256 `b8aae801122e918731fb8e05a9aa8ca94873f02282d7f1afee57777f6bea96ea` matches v5. V5 invariant report SHA-256 `509f1a46873b6922ce22e18f4100fa2dcb84a632d80ee9a014750efc6c857d54`; v5 provenance receipt SHA-256 `3a2531c3bbf3d9d69ac6c94f0f2663b67b47ffde7ce36c7ea0e1a943b74e32c9`. V5 independently reports 1,558/1,558 common M/U/X records and exactly 192 treatment-only identities `R_flow.0–191`.
- Network hash and remaining card input hashes are consistent with the package provenance receipt. The new output directory is absent. Its run-specific consumption directory exists but contains no reservation file. No old output path or old raw result is overwritten.
- Witness contract hash is `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`; contract scope and hash are fixed in the card.

## Runtime tests and preflight

I ran the R02 suite in both interpreters to assess the reported discrepancy:

- `python3 artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/test_runner.py` — **22 tests, one error**. The exact-card preflight test fails closed with `PYTHON_EXECUTABLE_PATH_MISMATCH` because system `python3` is not the executable recorded in the runtime binding.
- `.venv/bin/python artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/test_runner.py` — **22/22 PASS** under the bound interpreter.

This is correct fail-closed behavior, not a runner defect: the card intentionally binds `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/.venv/bin/python`, and the test suite passes when invoked with it. Future preflight must continue to use that exact interpreter and recheck its hash.

The retained R02 receipt reports `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launch_authorized=false`, simulator process false and zero SUMO/TraCI/netconvert starts. I did not invoke the runner's preflight or launch endpoint again; no reservation or output was created.

## Resource proposal and prospective post-run gate

The card proposes a treatment-specific 90 s wall-clock stop trigger and 75,000,000 decimal-byte output stop trigger, polled every 100 ms with slight stop overshoot possible. The status is `PROPOSED_NOT_AUTHORIZED`. This provides about 3.6x headroom over the completed control's 24.881003 s / 20,821,740 bytes; the prior non-comparable treatment's 19.921320 s / 21,066,503 bytes is secondary context. The proposal is concrete and correctly does not inherit the old authorization.

The post-run plan preregisters a first gate comparing M/U/X trajectories before meaningful R exposure, with common time/location/cell/lane, identities, sample/coverage and trajectory attributes considered. Any material unexplained pre-R divergence or identity/coverage failure yields pair `NOT_EVALUABLE`; post-R witness analysis is permitted only after that gate passes. No numeric equivalence threshold or scientific input is added. This is technically implementable as an analysis gate; actual trajectories and future insertion remain unverified until a separately authorized run and review.

## Limits and final finding

Static review establishes binding integrity and the reviewed v5 planned-input invariant only; it does not establish future runtime availability, vehicle insertion/lifecycle, or trajectory equivalence. No SUMO, TraCI, or netconvert process was launched. The exact card remains explicitly unauthorized, and the proposed resource limits remain unapproved. Fresh data/provenance and scientific prelaunch reviews and separate user authorization are still required before any start.
