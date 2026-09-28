# FULLNET3350_A_R900_S17 Engineering Post-run Review

**Engineering disposition:** Process execution completed; raw package integrity checks passed with a material insertion warning referred to data review.  
**Run ID:** `FULLNET3350_A_R900_S17`  
**Final card SHA-256:** `09f711a540457f1fbecc1c30fe5173ca8b83b24c39ad1913a9d33e782cc03cdd`

## Execution and resource contract

- Guardian starts: 1; SUMO starts: 1; TraCI starts: 0; netconvert starts: 0.
- SUMO return code 0; reached simulation time 2700 s; wall-clock 24.467939 s.
- Output payload: 24,585,577 bytes, below the accepted 75,000,000-byte stop trigger. The 90 s trigger did not fire. 100 ms polling and slight monitoring overshoot were authorized.
- No retry or second launch occurred. No B/C, seed23, or alternate demand run occurred.

## Integrity checks

- 18/18 configured output roles and seven support files were present in the unique A output root.
- Output manifest verification passed 25/25 entries. XML outputs were well formed; manifest hashes matched the execution receipt.
- The staged sumocfg was generated with the package's bound demand, network and additional files. Staged sumocfg SHA-256: `c99c2d89dbc4eb0cd2d2508c44eeb30f71da3964b6c31bec018cef6c66b750cf`; additional XML SHA-256: `eda6351f5795269b1406945963eeeabe428737a1e3e8cfaab0363ff74434f0ee`.
- The R02 offline test suite passed 6/6; runner compilation and the final-card read-only preflight passed before the launch.

## Engineering warning handed to lifecycle review

SUMO logged 57 U-vehicle departure failures with the message that the vehicle could not depart at the given velocity because a slow lane was ahead. The run summary reports 1861 loaded and 1804 inserted. This warning is preserved for data/lifecycle review; engineering does not treat it as an acceptable or scientifically interpretable U exposure.

No scientific inputs, network geometry, vehicle behavior, signal program, classifier, thresholds, phenomenon gate, or formal protocol were changed. Engineering performed no phenomenon or causal assessment.
