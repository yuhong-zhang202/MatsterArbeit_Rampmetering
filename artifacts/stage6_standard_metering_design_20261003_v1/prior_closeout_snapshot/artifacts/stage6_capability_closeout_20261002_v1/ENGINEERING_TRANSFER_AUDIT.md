# Stage 6 city-side capability transfer: engineering input audit

Date: 2026-10-02. Status: **PASS_FOR_QUALIFIED_CAPABILITY_TRANSFER (technical scope only)**. This is an input and measurement-invariance audit, not acceptance of Stage 6, a control effect, or a formal protocol. No simulation or converter was started. The machine-readable source paths, SHA-256 values, normalized definitions and check results are in [`ENGINEERING_TRANSFER_AUDIT.json`](ENGINEERING_TRANSFER_AUDIT.json).

## Context and audited scope

- `docs/PROJECT_STATE.md` currently records Stage 6 `PARTIAL — PAUSED_BY_USER`. `docs/DECISIONS.md` D-011 concerns historical exploratory A/B/C evaluation. `docs/EXPERIMENT_PROTOCOL.md` is empty/unfrozen. Robert's 2026-09-30 original reply requests geometry, insertion and connection checks before uncontrolled localization; it does not approve a new control result.
- Old **default-model V2** inputs: `artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2/{A,B}/`, with `A_OPEN` versus `B_MODERATE` (22G+3y+35r). The A/B demand XML is byte-identical, SHA-256 `12e2e4e003089dad489a2ea1323cd44ef54dea39f994f1bb5fe61e45c7f03be0`.
- New representative input: `artifacts/stage6_boundary_search_20261002_v1/inputs/M3600_R900_S17/`, `A_OPEN`. The same input structure, network, routes, detector definitions, processing settings and ramp program were checked for `M3600_R900_S23` and `S42`; only the S17 demand cohort was used for detailed counts. This audit does not pool the old and new outcome series.

## Mechanism-relevant invariants

All three S17 configs reference `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml`, SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. Its compiled connections send U and R along `urban_in → shared_approach`, then U to `urban_out` and R to `ramp_storage → ramp_accel → merge_section_0`; M enters `merge_section_1/_2`. `urban_tls` has the same 45G/3y/9G/3y phases because it is part of that exact network. `ramp_mid` has both compiled programs; selection changes as intended: old A=`A_OPEN`, old B=`B_MODERATE`, new S17/S23/S42=`A_OPEN`.

The four explicit route edge lists and `technical_passenger` (`vClass=passenger`, no explicit model/sigma override) are identical. All arms request `departLane=best`, `departSpeed=max`; M uses `departPos=100`, R/U/X `last`. SUMO config processing fields (`time-to-teleport=-1`, `collision.action=warn`, `collision.check-junctions=true`, `extrapolate-departpos=false`), one-second step and output role set are identical. Old and new cards bind the same SUMO binary SHA-256 `3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179`; old B and new S17 logs both say SUMO 1.26.0, return code 0.

The 11 detector definitions match after removing output file destinations. The city-side `shared_boundary_e2` still covers `shared_approach_0` from 0 to 238.8 m in 30-second periods, with `timeThreshold=1`, `speedThreshold=1.3888888888888888 m/s` and `jamThreshold=10`. The `ramp_storage_e2` and lane-specific E1 locations/periods likewise match. Both configs retain FCD, lane changes, tripinfo, vehroute, queue, TLS and detector output roles. New FCD uses `.gz`, a storage-format difference. E2 jam-positive bins and U-specific FCD slow time remain observations with their stated lane/window definitions; an E2 jam flag alone cannot prove a continuous queue across connectors or city-wide spillback.

## Expected and material differences

| Input | Old V2 A/B22 | New M3600_R900_S17 | Transfer implication |
| --- | --- | --- | --- |
| Requested cohorts | M1396, R240, U150, X75 | M3000, R600, U300, X150 | Larger and longer new loading; U/X rates stay 360/180 veh/h. |
| Requested times | M/U/X near `[0,1500)`, R `[540,1500)` | M/U/X `[0,3000)`, R `[600,3000)` | Different warm-up and exposure length. |
| SUMO end | 2700 s | 4200 s | Compare observations only within each declared window. |
| Ramp program | A open; B 22G+3y+35r | Open | Old B22 queue cost is a metering-capability observation, not a new-open-run prediction. |
| Explicit speedFactor | One prospective old vector shared exactly across A/B (1861/1861 matching vehicle IDs) | New SHA-256(seed/class/index) to per-vehicle Python `Random.gauss(1,0.1)`, rejection `[0.2,2]`, 10 decimals; CPython 3.13.0 | Same declared marginal family, different realization. Of 1861 common IDs between old A and new S17, 0 speedFactor strings match. |

The old vector's design used `random.Random(170026)` in sorted ID order, not the new per-ID digest rule. Neither vector recreates SUMO's historic random stream. The new run also has a higher M requested rate (3600 versus about 3350 veh/h); preserved routes, default type and network do not imply identical traffic trajectories or identical queue duration.

## Transfer judgment and limits

The independent old [B22 scientific outcome review](../stage6_full_network_abc_matched_rebuild_20260926_v1/B_SCIENTIFIC_OUTCOME_REVIEW.md) reports B minus matched A R network residence `+153.821 s`, U `+26.473 s`, zero external departure-delay difference, shared E2 jam-positive `22/90` bins versus A zero, and U-specific shared-approach slow exposure `987` vehicle-seconds versus A zero. With the audited geometry, city TLS, routes, behavior type, departure rules and measurement definitions unchanged, this remains evidence that **this model can produce R/U internal cost and shared-road U obstruction when its ramp admission is constrained**. The audit finds no mechanism-relevant configuration change that discards that limited capability evidence.

It does **not** establish that new M3600_R900 **open-ramp** runs show the same U obstruction, reproduce the old B22 effect size, yield a successful M protection trade-off, or meet current-version Q3/Q4 and formal-use acceptance. Those require their own matched outcome/trajectory assessment and scientific review. The old A/B22 single-seed effects and early distant M divergence retain their original limitations. Original nonpairable RI3350 and separate sigma0 sensitivity are outside this transfer comparison.

## Verification and files

- Read-only checks parsed the three S17 scenario configs, additional files, demand XML, compiled network and old/new run cards/logs; then checked the corresponding S23/S42 input structure. `sha256sum` independently confirmed network and S17 file hashes. All 12 machine-readable equality checks in the JSON are true.
- Created only `ENGINEERING_TRANSFER_AUDIT.md` and `ENGINEERING_TRANSFER_AUDIT.json` in this versioned directory. No existing input, raw output, decision, protocol or project document was changed by this subtask. No SUMO, netconvert or TraCI command was run.
