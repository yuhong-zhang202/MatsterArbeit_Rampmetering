# S17 V9 actuator repair: engineering closeout (2026-10-03)

The single exact-released S17 V9 technical validation completed. The stopped-front/follower guard removed the V8 pilot's observed emergency warnings in this seed, but the requested feedback rate was not physically served. The guarded actuator is therefore technically safe in the observed run and still **not qualified as a rate-tracking controller**. No S23/S42 V9 simulation was started.

## Exact record and accounting

- Card: `inputs/M3600_R900_S17_ALINEA_TRACI_V9/card.json`, SHA-256 `086e5812e409125db9ebe509a51932b4c65c39a6b9d2ee27008f55034eb61507`; prospective purpose `TECHNICAL_ACTUATOR_REPAIR_VALIDATION` under D-016.
- Raw receipt: `data/raw/stage6_standard_metering_20261003_v1/M3600_R900_S17_ALINEA_TRACI_V9/outputs/execution_receipt.json`, SHA-256 `bf05acc50c7a4807d748dd68aed862645e3b220bcd87ad39e7adca0abcc753d2`.
- `COMPLETED`, return code 0, wall 23.619 s, 40,557,493 output bytes; all 32 manifest files matched recorded size and SHA-256. Shared raw after run: 302,898,421 bytes. Cumulative physical starts 26, technical starts 7, experiment starts 19 (18 preexisting uncontrolled plus the V8 S17 pilot); V9 did not erase or reclassify the pilot.
- Exact release: `RELEASE_S17_ALINEA_V9.json`. The 120 s/250 MB/8 GB guardians were not exceeded. After exit, worker PID 31405 and SUMO child PID 31406 were absent from `ps`; project launch lock was absent.

## Four-layer actuator record

For `[600,4200)`, 4,200 controller rows and 119 feedback rows were written. There were 2,442 nominal due slots; the guard rejected 1,886 (34 no front, 1,813 front/receiver not ready, 39 follower stopping distance). It commanded 556 one-second G slots; each had a qualified stopped front and a unique front crossing. Red crossing, repeated crossing, and wrong-vehicle counters were all zero. The first actual G was at t=652 s; t=603 s was only the earliest nominal due time. The service-window engineering classifier was `PASS_TECHNICAL_SERVICE`. The SUMO stderr and error logs were empty, compared with 10 emergency-braking and 8 red-light emergency-stop warnings in V8 S17. This is observed S17 behavior, not proof of general safety.

The feedback command could not track its requested rate. In four consecutive 300 s blocks, the mean command and actual crossing-equivalent rate (12 times G count) were:

| Interval (s) | Mean command (veh/h) | Actual equivalent (veh/h) |
| --- | ---: | ---: |
| 900–1200 | 1,070.67 | 576 |
| 1200–1500 | 1,164.47 | 564 |
| 1500–1800 | 1,078.28 | 552 |
| 1800–2100 | 1,136.78 | 564 |

These values come from `controller_steps.csv`; they are realized releases in four windows, not an estimate of a universal physical maximum. Rejected credit was capped at one, with excess recorded as dropped credit; the controller did not catch up through a burst. Since the chosen initial/upper feedback rates exceed observed service in these sustained windows, the current controller cannot be described as a validated standard ALINEA rate comparison.

## Status and next engineering step

The V9 technical guard, event occupancy, and trace schema can be reused. Any change to the initial or upper rate, signal service rule, or scientific interpretation requires a prospective research amendment and exact-card scientific review; the engineering evidence alone does not choose the new value. Until then, preserve the V8/V9 raw runs and hold S23/S42. No code changes or further tests are needed to identify this rate-tracking limitation.
