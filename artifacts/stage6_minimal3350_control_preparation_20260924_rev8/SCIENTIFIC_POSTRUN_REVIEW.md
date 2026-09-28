# Independent scientific post-run review — MINIMAL3350_CTRL_S17 REV8

**Disposition:** `LOW_R_BACKGROUND_ACCEPTABLE`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Confidence:** High for lifecycle, exposure, and locked classification; Moderate for physical interpretation.

The run completed to 2700 s. All 1,396 planned M vehicles were inserted and arrived; none were unfinished, discarded, waiting, or vaporized. R/U/X were explicitly zero. FCD covers 0–2699 s; all 1,396 M vehicles passed the three named E1 stations. Merge-core coverage during [720,1440) is 677 unique M IDs and 7,096 samples.

Locked P/S/L all report `NO_QUALIFYING_EVENT`; Candidate A is absent. The 28 one-bin Candidate C warnings across 11 bins are retained, with no same-cell consecutive bins. Some flags coincide across adjacent cells, including near the merge, but they do not establish sustained self-congestion. The strict historical high-mobility screen remains FAIL and is not waived.

No clear source, downstream, TLS, geometry, lane-mapping, lifecycle, or measurement alternative invalidates this control classification. The queue export contains 2,700 timestamps but no lane records, so queue morphology cannot be assessed; this rules out claims of a clean normal baseline or queue absence. The explicit speedFactor vector came from a prior full-network seed17 run with U/X present. It is acceptable as a fixed vector for this conditional exploratory matched comparison, not as an independently sampled or representative U=X=0 realization.

A raw-FCD spot-check reproduced cell 13 [690,720) warning metrics exactly; the reviewer did not fully reimplement the classifier. Regression coverage for the analysis pipeline was not verified; this is a non-blocking observation for this run.

This disposition applies to the control only. Treatment remains a separate conditional arm requiring its own exact-card prelaunch reviews.
