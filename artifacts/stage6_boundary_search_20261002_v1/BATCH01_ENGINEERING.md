# Batch 01 engineering execution and integrity report

2026-10-02. Exploratory runs only. Four starts, zero retries.

Execution used the exact cards and release_batch01.json. For each run: `.venv/bin/python scripts/stage6/boundary_search_20261002/runner.py launch --card artifacts/stage6_boundary_search_20261002_v1/inputs/RUN_ID/card.json --approved-card-sha256 HASH --release artifacts/stage6_boundary_search_20261002_v1/release_batch01.json`. Subsequent three calls used the identical imported `launch` function sequentially.

All outputs are complete XML (including gzip FCD), receipt hashes match, all requested vehicles departed and arrived, full 4200-second FCD and ramp TLS histories exist with no per-vehicle interior FCD gaps or duplicate IDs per label. No collisions, teleports, discarded vehicles or error-log messages. The ramp remained G throughout. Input cards, plan and runner were unchanged during execution.

First launch took 31.53 s, with delayed first output; later launches took 3.08–3.91 s. No process restarted. Shell `ps` was unavailable under sandbox, but the original tool session returned normal completion; no limitation affected simulation outputs.

These are technical integrity results, not traffic-state conclusions. Data analyst must apply the reviewed state classifier and examine insertion chronology. No further demand cell released by this report.

```json
[
  {
    "run": "M2400_R0_S17",
    "seconds_wall": 31.528,
    "disk_bytes": 7367900,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 2450,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 2000,
      "R": 0,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "all_departed_arrived": true,
    "max_depart_delay_M_s": 0.5,
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0
  },
  {
    "run": "M3000_R0_S17",
    "seconds_wall": 3.083,
    "disk_bytes": 8275982,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 2950,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 2500,
      "R": 0,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "all_departed_arrived": true,
    "max_depart_delay_M_s": 0.8,
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0
  },
  {
    "run": "M3600_R0_S17",
    "seconds_wall": 3.325,
    "disk_bytes": 9174563,
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
    "all_departed_arrived": true,
    "max_depart_delay_M_s": 0.0,
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0
  },
  {
    "run": "M4200_R0_S17",
    "seconds_wall": 3.909,
    "disk_bytes": 10147264,
    "hashes_ok": true,
    "fcd_labels": 4200,
    "consecutive_labels": true,
    "unique_ids": 3950,
    "interior_gaps": 0,
    "duplicate_ids_per_label": 0,
    "class_counts": {
      "M": 3500,
      "R": 0,
      "U": 300,
      "X": 150
    },
    "trip_ids_equal_fcd": true,
    "all_departed_arrived": true,
    "max_depart_delay_M_s": 0.86,
    "collision_teleport_discard_max": {
      "collisions": 0.0,
      "teleports": 0.0,
      "discarded": 0.0
    },
    "ramp_tls_4200_G": true,
    "error_bytes": 0
  }
]
```
