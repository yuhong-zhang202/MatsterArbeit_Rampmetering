# R0 V1 preserved technical failure

**Run:** `FULLNET3350_R0_S17_REBUILD_V1`  
**Card SHA-256:** `8ea2e804cd585e5352ed4a1de55ad229ed35701f440c8f2dfed3f23b74fcf042`  
**Disposition:** `TECHNICAL_PRETRAFFIC_FAILURE / NO_SCIENTIFIC_OUTCOME`.

SUMO PID 6102 exited 1 after 0.212646 s. The runner created and consumed its one-use reservation, recorded a 19,781-byte payload, and preserved all files in `data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1/R0/outputs/`. `stderr.log` and `sumo_error.log` show that `SUMO_HOME` was unset, so SUMO looked for `additional_file.xsd` at the wrong framework location and then failed to resolve `sumo.dlr.de`. The correct local schema is under `.../EclipseSUMO/share/sumo/data/xsd/`.

Independent `data_analyst` read-only audit verified all ten receipt-listed output hashes and sizes, unchanged bound demand/config/additional hashes, and zero traffic timesteps/vehicle/trip/queue records in six well-formed XML shells. Empty shells are **not** evidence of zero congestion or a normal baseline. Independent `scientific_reviewer` classified the attempt as a pretraffic engineering failure with no scientific outcome and allowed a versioned technical retry after an environment-only fix and fresh exact-card review. The V1 reservation remains `CONSUMED/FAILED`, `retry_allowed=false`; V1 raw, card and receipt must not be overwritten. A/B/C remain unlaunched.
