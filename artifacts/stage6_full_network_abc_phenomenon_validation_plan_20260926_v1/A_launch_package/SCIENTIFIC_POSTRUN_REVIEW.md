# Independent Scientific Post-run Review — Pre-R Pairability Only

**Disposition:** `PRE_R_PAIRABILITY_FAIL`; A phenomenon status is `A_NOT_EVALUABLE`.  
**Confidence:** High.  
**Scope:** Review only the R0–A pre-activation eligibility gate. Post-540 outcomes, R merge-exposure totals, P/S/L, Candidate A/C, and the 0.85 diagnostic were not analyzed.

## Basis

- Exact FCD tuple comparison across common `(vehicle ID, integer-second t<540)` keys gives M 497/34,470 (1.44%), U 80/2,008 (3.98%), and X 468/1,394 (33.57%). First divergence: M at 12 s, U at 13 s, X at 108 s. M divergence precedes R activation.
- Actual pre-540 departures: M 502 in each arm, U 54 in R0 versus 35 in A, X 27 in each arm. Actual departure times differ for 114/502 common M identities, 6/35 common U identities, and 12/27 X identities.
- `M_flow.502` has desired departure 539.148 s and actual departure 540.00 s in both arms. Neither has an FCD record for it before 540; it remains excluded from the strict `[0,540)` actual-departure and trajectory counts.
- A discarded 57/150 planned U vehicles; 19 failures are before 540 s. SUMO logs cite inability to depart at the given speed because a slow lane was ahead. This is a concrete source/insertion mismatch; it does not by itself explain every M/X divergence.
- The data analyst's raw-hash-bound review was independently checked by the scientific reviewer against both FCD files. A execution and file integrity succeeded, but that does not restore pre-R pairability.

## Required disposition

The R0 comparator is ineligible for interpreting A because material M/U/X insertion and trajectory differences already occur before R activation. Stop the sequential gate at this point. Do not assess A's R merge exposure or post-540 M phenomenon against this R0, and do not prepare or start B/C on this comparison. Keep R0's historical `CONTROL_NOT_EVALUABLE` status unchanged.
