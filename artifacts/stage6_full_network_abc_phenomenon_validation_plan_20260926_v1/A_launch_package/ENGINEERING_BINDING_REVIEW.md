# A-arm Engineering Binding Review

Status: `DRAFT_NOT_AUTHORIZED`. This package is a preparation artifact only. No Guardian, SUMO, TraCI, or netconvert process was started.

## Exact binding

- Run: `FULLNET3350_A_R900_S17`; condition: qMain 3350.4 veh/h, seed 17, U=150, X=75, delayed R=900 veh/h with 240 planned R identities in `[540,1500)`, A_OPEN, 2700 s horizon.
- The sumocfg route-files reference resolves exactly to the data-binding-owned `data_binding/demand_A_materialized.rou.xml`. Its SHA-256 is `69c10dafc607f616585d36b16a00a4c7d4e82eefc5c28878ea8e9dfe3c16c769`.
- The sumocfg additional-files reference resolves exactly to this package's `inputs/scenario.add.xml` (SHA-256 `eda6351f5795269b1406945963eeeabe428737a1e3e8cfaab0363ff74434f0ee`). The configured network resolves to the bound validated network (SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`).
- All 18 output-role paths are unique and lie under the A-only output root `data/raw/stage6_full_network_abc_phenomenon_validation_20260926_v1/FULLNET3350_A_R900_S17/outputs/`. No output role refers to the old `LOC_M3350_S17_attempt1` path.
- R02 runner binds only the exact A run ID, package card path, output directory, inputs, runtime, output-role file, and nested references. It rejects a changed route reference or output-role path before launch.
- Output directory is absent and its parent is creatable. Resource values are proposals only: 90 s and 75,000,000 bytes, with 100 ms polling and possible slight overshoot. They are not accepted authorization.

## Pre-activation comparison gate

Before A can support attribution, compare M/U/X under `[0,540)` against the materialized R0 binding. The gate must check IDs, desired departure, routes, vTypes, depart lane/position/speed, speedFactor, and observed trajectory. Preserve the R0 historical `CONTROL_NOT_EVALUABLE` disposition. In particular, retain `M_flow.502`: desired departure 539148 ms and R0 actual departure 540.00 s; reconcile its insertion at the activation boundary separately from trajectory comparison strictly before 540 s. Any unexplained pre-activation mismatch makes the A comparison `NOT_EVALUABLE`.

## Verification evidence

- `python3 -m py_compile artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py` — passed.
- `.venv/bin/python -m unittest discover -s artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package/tests -v` — 3 passed. Coverage: exact draft preflight remains non-launchable; changed route path fails closed; output role outside the A root fails closed.
- R02 `preflight` returned `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launch_authorized=false`, `launchable_now=false` for the exact card hash recorded in `INPUT_MANIFEST.json` / card. This validates static binding only; it is not a launch authorization or scientific review.
