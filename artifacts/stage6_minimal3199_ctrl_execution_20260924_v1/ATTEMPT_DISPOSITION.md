# MINIMAL3199_CTRL_S17 — one-use attempt disposition

**Final outcome:** `NOT_EVALUABLE`  
**Authorization:** consumed by one launch attempt; no retry.  
**SUMO starts:** 0. **TraCI starts:** 0. **netconvert starts:** 0.

The authorized one-time control launch failed before Guardian/SUMO spawn because R02 raised `KeyError:'additional_schema'` while building its Guardian START spec. The reservation is irreversible and records `FAILED`, `simulator_pid=null`, `retry_allowed=false`. The partial output and reservation have been retained. No data/lifecycle outputs exist, so engineering integrity could only audit the pre-spawn failure and data reconciliation is impossible. Independent scientific review confirms that neither an acceptable low-R background nor self-congestion can be inferred.

The accepted resource contract was 90 s wall-clock / 60,000,000 bytes with 100 ms polling. No resource stop trigger fired. No treatment, other qMain/qRamp, seed23, B/C or other demand ran. The FINAL card itself remains in the execution package as provenance; it must not be reused to launch.

Review details: `ENGINEERING_POSTATTEMPT.md`, `DATA_RECONCILIATION.md`, and `SCIENTIFIC_REVIEW.md`.
