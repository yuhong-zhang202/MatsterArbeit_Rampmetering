# Batch05 engineering report and paused technical handoff

2026-10-02. Eight exploratory starts in S23 R0/600/750/900 then S42 same order via exact release_batch05.json; zero retries. All eight completed. User requested pause after this minimal released node; no subsequent preparation, simulation or controller implementation performed.

All XML complete; raw receipt hashes match;4200 consecutive FCD seconds per run, zero per-vehicle interior gaps or duplicates, full requested cohorts departed and arrived by4200. No M auxiliary usage; all R lane changes occurred within auxiliary extent. Actual ramp continuously G. Zero collisions, teleports, discarded vehicles or errors. Run-state interpretation is delegated to data/scientific review.

Total at stop: 18 consumed reservations / starts, 18 completed receipts, zero failed/retried starts; raw disk bytes including receipts=197935338; summed simulation payload bytes=197865671. Global launch lock absent=True. No unused prepared card remains in the18-run series.

## Technical resume checklist (future user-authorized work only)

1. Read current PROJECT_STATE, WORKLOG, PLAN, batch reviews, all engineering reports, and final scientific handoff. Preserve old RI3350 results and new sustained-loading series separately.
2. Existing runner: scripts/stage6/boundary_search_20261002/runner.py; tested with `.venv/bin/python -m unittest discover -s tests -p test_boundary_search_runner.py`. Commands: `prepare --run-id NEW_ID --q-main Q --q-ramp Q --seed N --plan PATH`; `preflight --card PATH --approved-card-sha256 HASH`; `launch --card PATH --approved-card-sha256 HASH --release RELEASE_JSON`. Consumed cards cannot rerun. Existing source hash must remain unchanged for old cards.
3. Inputs/cards: artifacts/stage6_boundary_search_20261002_v1/inputs/RUN_ID; immutable raw: data/raw/stage6_boundary_search_20261002_v1/RUN_ID/outputs. Each execution_receipt.json binds commands, runtime, statuses and all output hashes. Reconcile analyzer outputs independently before advancing.
4. Runtime: CPython3.13.0 .venv/bin/python; SUMO1.26.0 /Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo; TraCI1.26.0, sumoITScontrol0.1.0. Binary, Python build, source, network and reference hashes are in every card. Network path remains artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml.
5. Resource ceiling:40 total starts (32 uncontrolled +8 conditional control/technical by PLAN),120s wall/run,250MB on-disk/run,8GB total raw. Counts already consumed must carry into any controller runner; do not reset budgets by creating a new code path. Any failure is retained; no automatic retry.
6. ALINEA remains unimplemented and unreleased. Stock sumoITScontrol assumes the first TLS program has G/r and uses green-share percent; current network first program is single-G, so direct stock call is invalid. Proposed new adapter computes veh/h rate from downstream E1 lane-mean occupancy with explicit gain units and exact completed-period timing. Target, gain, bounds, start600s, cycle/pulse details require prospective amendment and review supported by current occupancy evidence.
7. A one-car-per-green actuator needs technical validation of startup loss,1s discretization, one-versus-multiple crossings, minimum green/red and yellow policy. Preserve fractional timing error and phase continuity at updates; prevent empty-demand credits creating platoons. Archive requested rate, unclipped/clipped rate, actual signal, per-vehicle ramp_mid crossings, ramp admission and downstream occupancy. Matching baseline/control requires byte-identical demand XML and unchanged noncontroller settings; conditional comparison is not yet authorized for execution after this pause.

```json
[
  {
    "run": "M3600_R0_S23",
    "seconds_wall": 3.786,
    "disk_bytes": 9157942,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3450,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 0,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        0,
        0
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 0,
    "r_aux_mainline_distinct": 0,
    "r_lanechange_max_pos_m": null,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R600_S23",
    "seconds_wall": 3.869,
    "disk_bytes": 10354696,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3850,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 400,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        400,
        400
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0.0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 400,
    "r_aux_mainline_distinct": 400,
    "r_lanechange_max_pos_m": 226.01,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R750_S23",
    "seconds_wall": 7.307,
    "disk_bytes": 10745331,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3950,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 500,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        500,
        500
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0.8,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 500,
    "r_aux_mainline_distinct": 500,
    "r_lanechange_max_pos_m": 258.01,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R900_S23",
    "seconds_wall": 5.371,
    "disk_bytes": 12944131,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 4050,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 600,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        600,
        600
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0.0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 600,
    "r_aux_mainline_distinct": 600,
    "r_lanechange_max_pos_m": 294.47,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R0_S42",
    "seconds_wall": 3.5,
    "disk_bytes": 9144265,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3450,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 0,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        0,
        0
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 0,
    "r_aux_mainline_distinct": 0,
    "r_lanechange_max_pos_m": null,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R600_S42",
    "seconds_wall": 5.037,
    "disk_bytes": 10318899,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3850,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 400,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        400,
        400
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0.0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 400,
    "r_aux_mainline_distinct": 400,
    "r_lanechange_max_pos_m": 224.78,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R750_S42",
    "seconds_wall": 5.944,
    "disk_bytes": 10705297,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3950,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 500,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        500,
        500
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 0.0,
      "R": 0.8,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 500,
    "r_aux_mainline_distinct": 500,
    "r_lanechange_max_pos_m": 251.05,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R900_S42",
    "seconds_wall": 7.164,
    "disk_bytes": 14309785,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 4050,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 600,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        3000,
        3000
      ],
      "R": [
        600,
        600
      ],
      "U": [
        300,
        300
      ],
      "X": [
        150,
        150
      ]
    },
    "max_depart_delay_s": {
      "M": 65.0,
      "R": 0.0,
      "U": 0.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 600,
    "r_aux_mainline_distinct": 600,
    "r_lanechange_max_pos_m": 293.46,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  }
]
```
