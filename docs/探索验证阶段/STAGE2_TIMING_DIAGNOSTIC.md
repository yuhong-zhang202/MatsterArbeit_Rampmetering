# Stage 2 timing diagnostic — exploratory

Date: 2026-09-09. Status: descriptive audit only; no timing parameter selected.

## Evidence and provenance

The data analyst independently checked raw tripinfo, FCD and E1 XML in the five retained runtime directories below. Raw files were not modified. All runs used seed 17; no independent stochastic replication is represented here.

| Runtime under `/private/tmp/` | Warm-up / measurement / maximum clearance (s) | Requested main / ramp (veh/h) | Ramp actual measurement departures (veh/h) | Ramp / urban departures during clearance | Last arrival (s) |
| --- | --- | --- | --- | --- | --- |
| `minimal_uncontrolled_17p2c9eo` | 600 / 600 / 900 | 1080 / 360 | 360 | 0 / 0 | 1271 |
| `minimal_uncontrolled_vbpsz_99` | 600 / 600 / 900 | 2600 / 600 | 360 | 40 / 24 | 1670 |
| `minimal_uncontrolled_zk23w8q3` | 600 / 600 / 900 | 3200 / 720 | 156 | 94 / 47 | 1883 |
| `minimal_uncontrolled_d73b4m7x` | 300 / 600 / 600 | 3200 / 720 | 462 | 43 / 22 | 1385 |
| `minimal_uncontrolled_eozyn46f` | 600 / 900 / 1200 | 3200 / 720 | 120 | 150 / 75 | 2401 |

All scheduled vehicles eventually entered and arrived. This is not evidence of demand realization during measurement: vehicles waiting outside the network can enter during clearance. Clearance stops new scheduled demand, not necessarily actual insertion.

## Same-trajectory observation windows

The following comparisons reaggregate only `minimal_uncontrolled_eozyn46f/outputs/`. They do not rerun SUMO or change traffic. Overlapping windows are not independent replicates.

| Window (s) | Ramp scheduled / actual departures | Urban scheduled / actual departures | End-of-window waiting to insert, ramp / urban | Outside-network waiting within window, ramp / urban (vehicle-seconds) |
| --- | --- | --- | --- | --- |
| 300–900 | 120 / 77 | 60 / 38 | 43 / 22 | 5205 / 2690 |
| 300–1200 | 180 / 85 | 90 / 42 | 95 / 48 | 26281 / 13313 |
| 300–1500 | 240 / 90 | 120 / 45 | 150 / 75 | 63271 / 31953 |
| 600–1500 | 180 / 30 | 90 / 15 | 150 / 75 | 63271 / 31953 |

Scheduled departure times were reconstructed as `depart - departDelay`; waiting is the overlap of each vehicle's scheduled-to-actual departure interval with the observation window. These are descriptive diagnostics, not approved formal evaluation metrics.

Across these windows, downstream E1 vehicle-weighted mean speeds were 29.81–29.85 m/s and flows 3260–3288 veh/h. Similar window averages do not establish a stable time series or a stable system. Local stopped ramp-vehicle counts also obscured growing upstream and outside-network accumulation.

The first stopped ramp/urban vehicles on the shared approach were observed at 412/414 seconds. A 600-second cut excludes this initial event; neither 300 nor 600 seconds has been validated as an appropriate warm-up. Earlier stops on `urban_in` at 45/58 seconds may include normal fixed-signal stopping and cannot be attributed to ramp spillback from these timestamps alone.

Demand scheduling ended at 1500 seconds; the last vehicle entered at 2245 seconds and arrived at 2401 seconds. The observed 901-second clearing tail is not a recommended clearance duration.

## Corrected analysis artifacts

The engineering repair adds `--reanalyze-summary` without rerunning SUMO or replacing original files. Each new report retains the original summary path and SHA-256, explicitly supersedes the old insertion-gate interpretation, uses consistent vehicle weighting for detector speeds, and reports queue differences without claiming stability.

Final corrected `reanalysis.json` files, in the same order as the five-run table above, are located under `/private/tmp/`:

- `minimal_uncontrolled_reanalysis_vatmiakw/`
- `minimal_uncontrolled_reanalysis_s98w3xiu/`
- `minimal_uncontrolled_reanalysis_r7zm521n/`
- `minimal_uncontrolled_reanalysis_fdr6tupv/`
- `minimal_uncontrolled_reanalysis_pb0uw7j8/`

## Queue-origin follow-up: retained trajectories only

The follow-up script `src/analysis/stage2_queue_diagnostic.py` writes an exclusively created JSON to `data/processed/stage2_queue_diagnostic_20260909/diagnostic.json`. It compares the same longest runtime with the retained low-demand runtime. It does not rerun SUMO. Source summary, FCD, tripinfo and TLS hashes were verified unchanged before and after processing. Vehicle ID sets and completed counts reconcile (1858 high, 660 low).

For the longest trajectory, the descriptive sequence is:

| Observation | Simulation time (s) |
| --- | --- |
| First stopped ramp vehicle on `ramp_accel` | 46 |
| First stopped ramp vehicle on `ramp_storage` | 192 |
| First stopped ramp / urban vehicle on `shared_approach` | 412 / 414 |
| Start of a continuous episode with stopped ramp / urban vehicles on `urban_in` | 493 / 550 |
| Start of continuous outside-network waiting, ramp / urban | 656 / 661 |

The script uses the existing technical stopped threshold of speed ≤0.1 m/s and consecutive one-second samples. An episode means at least one stopped vehicle is present, potentially different vehicles over time; it is not one vehicle's waiting time. Outside-network waiting is explicitly a before-step count (`scheduled < t <= actual departure`), not a new formal performance metric.

Low demand also has repeated stopping at `ramp_accel`: the longest continuous episode containing any stopped ramp vehicle is 168 seconds, whereas the longest same-vehicle stopped-head episode is 9 seconds. There are no stopped ramp/urban vehicles on `ramp_storage` or `shared_approach` and no ramp/urban insertion backlog in that low-demand run. Thus neither first stopping nor continuous presence of some stopped vehicle alone identifies harmful spillback.

The engineer independently verified the compiled connections: `urban_in → shared_approach` uses urban TLS link index 0, mainline connections have priority state `M`, and the ramp connection has state `m` into `main_down_0` only. Green-light counts for downstream edges indicate coincidence with the upstream signal, not direct signal control of those edges. Green-time stopping at `urban_in` alone also does not distinguish normal startup delay from downstream obstruction.

This ordering is consistent with accumulation propagating upstream from the merge end. It does not alone establish causality, a geometry fault, real-world capacity, a freeway Breakdown or a Capacity Drop. High and low runs differ in demand and demand duration and are not a matched controller comparison.

Representative FCD checks by the engineer provide additional local evidence:

- High-demand `R_flow.0` entered `ramp_accel` at 39 seconds, stopped near its downstream end (95.13–95.22 m) over samples 46–64 seconds, entered the merge internal connection at 65 seconds and `main_down` at 68 seconds. Mainline lane-0 vehicles continued to pass during its wait. Low-demand `R_flow.3` stopped at the ramp end only at samples 74–75 seconds before entering the internal connection.
- High-demand `R_flow.28` stopped near the end of `ramp_storage` at samples 192–217 seconds. At 412 seconds `R_flow.74` was stopped near the shared approach end (238.43 m); at 414 seconds `U_flow.37` was stopped behind it (230.95 m). This is local evidence of urban traffic encountering the ramp queue, not a measured counterfactual extra-delay estimate.
- At 493 and 550 seconds the urban signal state was `Gr` while urban-approach queues existed. This rules out describing all such observations as red-light stopping, but does not establish zero discharge over an entire green phase.

The compiled network also requires care in defining storage. From the downstream end of `shared_approach` to the end of `ramp_accel` before the merge internal connection, lane-path lengths sum to 494.87 m: `:urban_diverge_1_0` 113.08 m + `ramp_storage_0` 204.49 m + `:ramp_mid_0_0` 81.98 m + `ramp_accel_0` 95.32 m. This excludes the 12.60 m merge internal connection and the 238.80 m shared approach. These are compiled lane-path lengths, not effective queue storage capacity, and must not be converted automatically into an approved storage parameter. No geometry change was made.

## Compiled geometry and observation-coverage audit

The subsequent read-only audit confirmed that the two long internal connections join offset source-edge shapes through elongated compiled junction polygons. The existing shared-boundary predicate is located at the downstream end of `shared_approach` (1001.60, 642.80), before the 113.08 m internal connection; it is not at the start of the named `ramp_storage` edge (1061.13, 738.87).

Raw FCD contains both internal lanes and stopped vehicles on them. However, the runner's route-edge grouping and the follow-up diagnostic's four-edge whitelist omit internal lanes from their local queue summaries. Thus the limitation is in aggregation coverage, not missing raw trajectories. Previously reported named-edge observations remain valid within their stated scope; they cannot be interpreted as a full-path queue count.

Independent data checking found 9,433 stopped-R samples on `:urban_diverge_1_0` and 10,266 on `:ramp_mid_0_0` across the entire retained longest trajectory, including clearance. With one-second sampling these are accumulated stopped-vehicle-second samples, not distinct vehicles, queue length, continuous blockage duration or net causal delay.

The reviewed static visual is `results/figures/stage2_geometry_20260909_v4.png`; `data/processed/stage2_geometry_20260909/manifest_v4.json` records source and artifact hashes. Earlier versions are retained but superseded due to highlighting/layout defects. The v4 SVG wraps the same raster image, rather than independently representing vector geometry. The image uses actual compiled lane shapes and junction polygons, equal scales within each panel, and explicitly marked endpoints; it is not a SUMO GUI screenshot. Scientific review accepted this static audit, not live GUI behavior, effective storage or detector runtime coverage.

Detector coverage also needs qualification:

- `ramp_storage_e2` requests 250 m starting at position 0 on a 204.49 m lane. Documentation and topology suggest extension into a successor, but the precise loaded lane chain has not been measured in SUMO 1.26.0. The apparent remaining 45.51 m must be labelled an inferred extension, not a runtime-verified coverage boundary.
- `shared_boundary_e2` requests 250 m on the 238.80 m shared lane, leaving 11.20 m beyond a divergence with two successors. The static configuration does not explicitly select the continuation. Neither an exact ramp-branch extension nor an exact urban-branch extension has been established.
- The four mainline E1 detectors are point observations, not continuous coverage of the merge or ramp path.

Supplementing descriptive counts by explicit internal/external lane groups while retaining the old summaries is a proposed diagnostic correction, not a change to the allowed storage area. Changing detector extent, geometry, priority or a formal queue/storage definition requires a separate explicit proposal and approval.

## Implemented observation-only repair

The user subsequently authorized direct implementation of the minimum measurement adjustment and observation of its effects. Geometry, priorities, signals, vehicle models and demand settings were retained. The narrow E2 objective is now explicit: each detector observes only its named lane, while the separate FCD accounting describes internal and external lane groups.

After network compilation the runner generates E2 endpoints from actual lane lengths, with `pos=0`: shared lane 238.80 m; named ramp-storage lane 204.49 m. Source XML uses `endPos=-0.1` only as a non-extending standalone fallback; executed runner inputs replace it with the exact compiled endpoint. SUMO 1.26.0 accepted these endpoints. A no-step TraCI load of isolated copies confirmed both loaded positions and lengths, with source hashes unchanged. The probe report is `/private/tmp/e2_coverage_probe_minimal_uncontrolled_8egb0qb1.json`. The previous 250 m detectors' complete successor chains remain unverified; this is a limitation on historical E2 interpretation, not on the new contained-lane configuration.

The FCD module `src/analysis/internal_lane_accounting.py` retains separate per-lane and mutually exclusive per-group observations, surfaces unknown lanes/IDs, duplicates and malformed observations, and reports missing declared path lanes rather than claiming complete coverage. The four-component ramp path excludes shared/urban inlet, merge internal and downstream freeway. Existing ordinary-edge fields are retained with their original scope. New sample-based counts are not a formal queue length, safe storage capacity or causal delay metric, and are not assumed equal to E2 jam/halting measures with different definitions.

One matched exploratory regression, `/private/tmp/minimal_uncontrolled_8egb0qb1`, repeated the longest retained condition (seed 17, 3200/720 veh/h main/ramp, 600/900/1200 s windows, unchanged urban/cross demand). Independent canonical-record comparison against `/private/tmp/minimal_uncontrolled_eozyn46f` found zero differences in all 2700 FCD timestep records, 1858 tripinfo records, 2700 TLS records and 90 intervals for each of four E1 files. Comments and generator/root metadata were excluded; actual record attributes, order and nested children were retained. This establishes unchanged recorded traffic for this paired case only, not general invariance or model validity. E2 outputs cover different regions and must not be compared as a traffic improvement.

Authoritative derived files are under `data/processed/stage2_internal_accounting_20260909/`: `accounting_v2.json`, `low_accounting_v2.json`, `paired_accounting_v2.json` and `paired_semantic_comparison_v3.json`. Initial accounting outputs are superseded because per-timestep lane and group counts were initially mixed; review caught and tests now prevent that issue. The matched run's original `summary.json` was preserved: its `fcd_lane_observations` instantaneous mixed fields are superseded by `paired_accounting_v2.json`, not its raw traffic outputs or unrelated fields. `paired_output_comparison_v2.json` verifies individual structure and matched inputs only; the v3 semantic report supplies the actual cross-run equality evidence.

The full 17-test suite passed, including existing headless integrations and new coverage/internal-lane/regression checks; compilation and whitespace checks also passed. No formal demand acceptance threshold, phase duration or research metric was approved by this repair.

Final scientific review passed all five measurement checks within this repair's scope: explicit target, loaded coverage, omission/duplication checks, independent reconciliation and regression protection. This closes the measurement repair, not Stage 2, dynamic model validation or formal timing selection. The earlier 13-test reporting review described below predates this repair.

## Review and next boundary

The scientific reviewer accepted this narrow interpretation and the corrected reporting semantics, and recommended locating the source and propagation of accumulation using existing trajectories, signal records and reliable visual inspection before selecting durations. Geometry, signal timings and controllers remain unchanged. The engineer reported 13 passing regression tests, including four real headless integration tests. The first corrected report also passed independent numerical validation; final five-report consistency validation is recorded in the work log.

No Breakdown, Capacity Drop, causal urban-loss or sweet-spot claim follows from this diagnostic. The formal experiment protocol remains unfrozen. Temporary runtime paths are the current evidence location, not a permanent formal-experiment archive.

## Bounded saved-trajectory replay: 390–430 seconds

The repaired paired run now has an offline replay of all 41 original one-second frames in this interval. `src/analysis/build_stage2_replay.py` creates new outputs exclusively; `data/processed/stage2_replay_20260909/replay.json` and `manifest.json` preserve the slice, provenance, checks and visualization/template paths. The thread visualization is `stage2-queue-replay.html`. It uses compiled lane/junction geometry and original vehicle position points, including internal connections, without interpolation or an added coordinate offset. The display crops space; the payload retains all 4,541 in-network vehicle samples in the time slice. Outside-network waiting is not drawn.

The analyst reconciled every frame's lane/class and stopped counts against paired accounting v2. The reviewer independently parsed the original FCD and checked all retained vehicle IDs, lanes, coordinates and speeds, all lane shapes/lengths, 41 TLS records and the HTML payload. Source hashes before/after processing and final artifact hashes matched. Browser checks confirmed 412/413/414-second status changes, vehicle selection, slider, single-step, play/pause and stopping at 430 seconds without looping. Light-theme layout was checked at 736 and 360 pixels; the narrow root had no horizontal overflow. Dark-theme visual QA was not performed.

TLS index 0 controls the upstream urban inlet into the shared approach; index 1 controls cross traffic. At 412/414 seconds the original record is `rG`, while the observed stopped vehicles are downstream of that stop line. TLS and FCD use exact original time-label matching; within-step update ordering was not independently verified at implementation level. No phase-boundary causal claim follows. At 412 seconds R_flow.74/U_flow.37 have speeds 0.04/0.21 m/s; at 414 seconds they have 0.01/0.03 m/s, using the existing technical stopped threshold of 0.1 m/s.

Scientific review found no blocking issue for this fixed exploratory artifact. Measurement target, data coverage, omissions/duplicates and independent reconciliation passed within the declared slice; negative-input regression tests for the new generator remain unverified. This replay does not close broader dynamic model validation, select phase durations or establish causal urban loss. No SUMO execution, parameter changes or repeat of the 17-test repair suite occurred. The next bounded observation can examine existing upstream-accumulation and clearing records separately; no new simulation is implied.
