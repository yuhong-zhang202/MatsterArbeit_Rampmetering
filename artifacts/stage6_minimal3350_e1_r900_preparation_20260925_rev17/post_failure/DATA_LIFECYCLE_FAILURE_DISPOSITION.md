# Data/lifecycle failure disposition — MINIMAL3350_E1_R900_DELAYED_S17

**Disposition: `NOT_EVALUABLE`.** This is a read-only disposition of the failed attempt; no classifier or witness analysis was run.

- Guardian starts: **1**; SUMO starts: **1**; return code: **1**; runtime: **23.522957 s**. Authorization was consumed; retry is prohibited.
- SUMO aborted during additional-file loading before traffic simulation because the stale additional-file path targeted an absent v16 output directory. This is an engineering failure, not a scientific negative result.
- The immutable manifest records 13 output payload/support entries; 6 required traffic/lifecycle roles are present only as empty XML skeletons (`fcd.xml`, `lanechanges.xml`, `queues.xml`, `sumo_summary.xml`, `tripinfo.xml`, `vehroute.xml`); 12 required detector/TLS roles are missing. The present XML files parse with zero data records.
- Therefore planned/inserted/actual departure/arrival/unfinished/insertion-delay counts, detector coverage, and locked P/S/L or Candidate A/C cannot be evaluated. No zero counts are inferred from empty artifacts. No `NO_WITNESS` inference is made.
- Current raw inventory hashes and sizes match the immutable output manifest. This review changed no raw files and started no processes.

Machine-readable evidence and hashes: `DATA_LIFECYCLE_FAILURE_DISPOSITION.json`.
