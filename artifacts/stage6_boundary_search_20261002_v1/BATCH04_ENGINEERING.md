# Batch04 engineering report

2026-10-02. One exploratory M3600/R750/seed17 start via exact release_batch04.json. No retry or additional run. All XML complete, raw hashes match, all3950 requested vehicles departed/arrived,4200 continuous FCD seconds with no vehicle interior gaps/duplicates, no M auxiliary use;500R lane changes. Zero errors/collisions/teleports/discards; signal continuously G. Technical completion does not determine traffic-state or causal conclusions.

```json
{
  "run_id": "M3600_R750_S17",
  "status": "COMPLETED",
  "wall_seconds": 4.393477749981685,
  "bytes": 10772941,
  "raw_hash_pass": true,
  "fcd_4200_contiguous": true,
  "fcd_interior_gaps": 0,
  "fcd_duplicates": 0,
  "fcd_ids": 3950,
  "tripinfo_ids": 3950,
  "all_cohort_departed_arrived": true,
  "M_aux_ids": [],
  "R_lanechanges": 500,
  "R_unique_lanechanges": 500,
  "R_max_lc_pos_m": 267.49,
  "max_departDelay": {
    "M": 0.0,
    "R": 0.8,
    "U": 0.0,
    "X": 0.0
  },
  "summary_last": {
    "time": "4199.00",
    "loaded": "3950",
    "inserted": "3950",
    "running": "0",
    "waiting": "0",
    "ended": "3950",
    "arrived": "3950",
    "collisions": "0",
    "teleports": "0",
    "halting": "0",
    "stopped": "0",
    "meanWaitingTime": "0.10",
    "meanTravelTime": "77.63",
    "meanSpeed": "-1.00",
    "meanSpeedRelative": "-1.00",
    "discarded": "0",
    "duration": "0"
  },
  "all_ramp_G": true,
  "error_bytes": 0
}
```
