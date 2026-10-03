# Batch03 engineering report

2026-10-02. One exploratory M3600/R900/seed17 start via exact release_batch03.json. No retry or additional run. All XML complete, raw hashes match, all4050 requested vehicles departed/arrived,4200 continuous FCD seconds with no vehicle interior gaps/duplicates, no M auxiliary use;600R lane changes. Zero errors/collisions/teleports/discards; signal continuously G. Technical completion does not determine traffic-state or causal conclusions.

```json
{
  "run_id": "M3600_R900_S17",
  "status": "COMPLETED",
  "wall_seconds": 6.711600749986246,
  "bytes": 15181261,
  "raw_hash_pass": true,
  "fcd_4200_contiguous": true,
  "fcd_interior_gaps": 0,
  "fcd_duplicates": 0,
  "fcd_ids": 4050,
  "tripinfo_ids": 4050,
  "all_cohort_departed_arrived": true,
  "M_aux_ids": [],
  "R_lanechanges": 600,
  "R_unique_lanechanges": 600,
  "R_max_lc_pos_m": 294.48,
  "max_departDelay": {
    "M": 58.0,
    "R": 0.0,
    "U": 0.0,
    "X": 0.0
  },
  "summary_last": {
    "time": "4199.00",
    "loaded": "4050",
    "inserted": "4050",
    "running": "0",
    "waiting": "0",
    "ended": "4050",
    "arrived": "4050",
    "collisions": "0",
    "teleports": "0",
    "halting": "0",
    "stopped": "0",
    "meanWaitingTime": "4.88",
    "meanTravelTime": "132.50",
    "meanSpeed": "-1.00",
    "meanSpeedRelative": "-1.00",
    "discarded": "0",
    "duration": "0"
  },
  "all_ramp_G": true,
  "error_bytes": 0
}
```
