# E1 R900 post-failure engineering disposition

- Run: `MINIMAL3350_E1_R900_DELAYED_S17`
- Result: `ENGINEERING_FAILURE_PRE_TRAFFIC_RAW_NOT_EVALUABLE`
- Authorization: consumed; retry prohibited.
- Starts: Guardian 1, SUMO 1. This review started no process.
- Runtime: 23.522957 s; return code 1.
- Output payload: 26,800 bytes, below the 100,000,000 byte stop limit.
- The raw directory inventory totals 33,348 bytes including manifest and execution receipt.

## Exact root cause

The executed staged config `data/raw/stage6_minimal3350_ux0_20260925_v17/MINIMAL3350_E1_R900_DELAYED_S17/outputs/scenario_control.sumocfg` (SHA-256 `f2883c2ad355a8a604fd20610380d0f648e175afcf8228b5f3b407bd149b851f`) names its `additional-files` as:

`/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev14/inputs/treatment/scenario.add.xml`

That is REV14's source XML (SHA-256 `5e2d659b3c615b97c68381f72ebab2ae0606a3835ba2b9875c21df72323e6d62`), not the staged REV17 `data/raw/stage6_minimal3350_ux0_20260925_v17/MINIMAL3350_E1_R900_DELAYED_S17/outputs/scenario_control.add.xml` (SHA-256 `28a7bd6afbe5c0a151ce96dabfabf7aeaf5885ba38b6add36da7e1faa258369c`). The old REV14 additional XML points detector outputs at `data/raw/stage6_minimal3350_ux0_20260925_v16/...`. SUMO's log confirms it loaded the REV14 additional file and failed creating `shared_boundary_e2.xml` in v16, then quit during additional-file loading.

The staged REV17 additional XML itself points at v17 correctly, but SUMO never used it. The config also points to the REV14 demand path; its file hash is byte-identical to the REV17 bound demand hash, though this remains a stale path reference.

## Why preflight missed it

The runner verifies the exact staged config/additional hashes and that the START command points at the staged config. It does not check that the config's `additional-files` XML attribute resolves to the staged additional file. E1's generic replacement only substitutes the path string for `files["additional"]`; the config contained a different REV14 path, so the replacement was a no-op. The staged bytes still matched their bound hash, making the check internally consistent but semantically incomplete. The 12 passing prelaunch tests covered command/output path, reservation, hashes, and stale R720 binding, but not this nested config-to-additional edge.

## Evidence and preservation

See `ENGINEERING_FAILURE_DISPOSITION.json` for exact hashes, source references, start receipts, all 13 output inventory entries, and test/preflight evidence. No `data/raw/` file was modified during this diagnosis. No tests, SUMO, Guardian, TraCI, or netconvert were run for this disposition.

This attempt is consumed. No repair-and-rerun or scientific interpretation is authorized by this task.
