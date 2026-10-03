# Batch 02 engineering execution and integrity report

2026-10-02. Four exploratory starts, zero retries. Invoked runner.launch sequentially using release_batch02.json and its exact per-run card hashes. Equivalent CLI: `.venv/bin/python scripts/stage6/boundary_search_20261002/runner.py launch --card artifacts/stage6_boundary_search_20261002_v1/inputs/RUN_ID/card.json --approved-card-sha256 HASH --release artifacts/stage6_boundary_search_20261002_v1/release_batch02.json`.

All required XML parse, receipt hashes match, complete 4200-second FCD with no interior vehicle gaps or duplicates, all planned cohorts departed and arrived by horizon, actual ramp signal always G, no collision/teleport/discard/error warning. Every requested R has an auxiliary-to-mainline event within the auxiliary lane extent; no M observed on auxiliary. No unfinished or externally waiting vehicle at final horizon.

M3600/R1200 has two stopped strategic|urgent lane changes at the 294.51 m auxiliary endpoint (R_flow.215 t1421 and R_flow.503 t2401); output precision is 0.01 m. These are NOT strictly before lane end. Other arms have maximum positions 182.38/222.38/206.40 m. The endpoint observations are retained for mechanism review, not hidden as errors.

R1200 causes R/U external departure delay maxima274/275s in both M rows; M3600/R1200 additionally has M maximum151s while M3000/R1200 remains0.8s. Classifying insertion limitation versus propagated congestion requires chronology; these complete runs are not automatically excluded.

These results establish technical completeness only. Data analyst and scientific reviewer must distinguish urban delivery limits, sustained mainline state and merge-origin mechanism. No expansion is released.

```json
[
  {
    "run": "M3000_R600_S17",
    "seconds_wall": 3.423,
    "disk_bytes": 9421010,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3350,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 2500,
      "R": 400,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        2500,
        2500
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
      "M": 0.8,
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
    "r_lanechange_max_pos_m": 182.38,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3000_R1200_S17",
    "seconds_wall": 4.714,
    "disk_bytes": 11628591,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3750,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 2500,
      "R": 800,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "class_departed_arrived": {
      "M": [
        2500,
        2500
      ],
      "R": [
        800,
        800
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
      "M": 0.8,
      "R": 274.0,
      "U": 275.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 800,
    "r_aux_mainline_distinct": 800,
    "r_lanechange_max_pos_m": 222.38,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R600_S17",
    "seconds_wall": 3.906,
    "disk_bytes": 10367617,
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
    "r_lanechange_max_pos_m": 206.4,
    "r_lanechange_at_end": [],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  },
  {
    "run": "M3600_R1200_S17",
    "seconds_wall": 9.083,
    "disk_bytes": 17848196,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 4250,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3000,
      "R": 800,
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
        800,
        800
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
      "M": 151.0,
      "R": 274.0,
      "U": 275.0,
      "X": 0.0
    },
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0,
    "r_aux_mainline_events": 800,
    "r_aux_mainline_distinct": 800,
    "r_lanechange_max_pos_m": 294.51,
    "r_lanechange_at_end": [
      {
        "id": "R_flow.215",
        "type": "technical_passenger",
        "time": "1421.00",
        "from": "merge_section_0",
        "to": "merge_section_1",
        "dir": "1",
        "speed": "0.00",
        "pos": "294.51",
        "reason": "strategic|urgent",
        "leaderGap": "8.01",
        "leaderSecureGap": "0.00",
        "leaderSpeed": "7.24",
        "followerGap": "5.10",
        "followerSecureGap": "0.51",
        "followerSpeed": "0.51",
        "origLeaderGap": "None",
        "origLeaderSecureGap": "None",
        "origLeaderSpeed": "None"
      },
      {
        "id": "R_flow.503",
        "type": "technical_passenger",
        "time": "2401.00",
        "from": "merge_section_0",
        "to": "merge_section_1",
        "dir": "1",
        "speed": "0.00",
        "pos": "294.51",
        "reason": "strategic|urgent",
        "leaderGap": "9.24",
        "leaderSecureGap": "0.00",
        "leaderSpeed": "7.47",
        "followerGap": "4.21",
        "followerSecureGap": "0.00",
        "followerSpeed": "0.00",
        "origLeaderGap": "None",
        "origLeaderSecureGap": "None",
        "origLeaderSpeed": "None"
      }
    ],
    "m_aux_vehicle_ids": [],
    "final_running": 0,
    "final_waiting": 0
  }
]
```
