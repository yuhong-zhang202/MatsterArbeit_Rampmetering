# FULL_NETWORK_R0_A_PAIRABILITY_AUDIT

**Disposition:** `PAIRABLE_WITH_EXPLICIT_LIMITATION`  
**Scope:** Read-only determination whether `RI3350_CTRL_S17_technical_retry1` (qMain=3350.4, R=0, U=150, X=75, seed17) can serve as a low-pressure comparator for the proposed A arm. This does not change the historical control disposition and does not authorize execution.

## Evidence supporting conditional pairability

- The R0 and target A context use the same validated network SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`, seed 17, 1 s step, 2700 s horizon, vehicle behavior, detector definitions, and non-ramp signal program `A_OPEN`.
- The R0 raw reconciles M/U/X planned, inserted, and arrived totals of 1396/150/75, with R=0. Its `vehroute.xml` contains the realized per-ID route/type, departure attributes, and speedFactor. The new package materializes these M/U/X identities and attributes, while reconstructing desired departures with SUMO 1.26.0 integer-millisecond flow offsets. The common A/B/C demand binding has 1,861 unique records: M=1396, U=150, X=75, R=240.
- R0 pre-540 scheduled counts are M/U/X=503/54/27; actual departure and FCD-observed counts are 502/54/27. `M_flow.502` had desired departure 539148 ms but actual departure 540.00 s. It is a boundary identity and is not counted as an actual pre-540 departure.
- The source R0 flow XML is not byte-identical to the materialized A demand. This is explicitly disclosed. Exact attributes and schedules are bound per identity, but actual A insertions and trajectories over `[0,540)` cannot be demonstrated until A exists. That comparison is a fail-closed post-A eligibility gate before B/C.
- The R speedFactor vector is frozen from a reviewed qMain=3199.2, U=X=0, delayed-R900 run and shared across A/B/C. It is not claimed as the target qMain=3350.4 full-network seed17 RNG realization. The interpretation is conditional on this single chosen R realization and does not establish robustness across R realizations.
- The R0's historical `CONTROL_NOT_EVALUABLE` status and low-speed warnings remain unchanged. It is proposed only as a low-pressure relative comparator, not a clean normal/high-mobility baseline.

## Configuration and provenance checks

- Network SHA-256: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`.
- R0 source configuration and additional-file hashes: `87ba0d7d671f1f72f45d7fda3c3e857a1622263a9c2ce4d3f1ef625745f7ab7c` and `6355c6a6deaf0b7aadbdca59a8349c4e0e96e47b9ff5f89b8498b9ad02adcd59`.
- The A package binds the exact materialized demand, staged sumocfg, additional XML, runtime, runner, and output-role file in its `INPUT_MANIFEST.json` and `PREPARATION_RECEIPT.json`. All 18 output roles are unique and under the A-only output root; the A output directory is absent.
- Offline engineering preflight: `PREFLIGHT_PASS_NO_PROCESS_STARTED`; `launch_authorized=false`; `launchable_now=false`. Three regression tests passed for draft non-launchability, stale route rejection, and output path rejection.

## Reviews and final boundary

- Engineering: static binding PASS; fail-closed path checks and 3/3 offline regression tests PASS.
- Data/provenance: 1,861-record binding and source hash checks PASS; actual A-versus-R0 pre-540 comparison remains pending.
- Independent scientific reviewer: `PASS_WITH_EXPLICIT_LIMITATIONS`; confidence High for the binding and scoped comparison, Moderate for inference from one fixed R realization.
- SUMO, Guardian, TraCI, and netconvert starts: 0/0/0/0.
- Card remains `DRAFT_NOT_AUTHORIZED`. No A execution is authorized by this audit.
