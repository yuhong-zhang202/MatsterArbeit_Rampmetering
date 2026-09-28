# A V2 phase-1 pairability and exposure gate

**Independent disposition:** `PASS_PHASE1_PAIRABILITY_AND_EXPOSURE / RELEASE_PHASE2_FIXED_WINDOW_ANALYSIS` (scientific reviewer, High confidence). This releases only the predetermined post-540 outcome analysis; it does not establish A, State1, or B/C eligibility.

Engineering postrun review passed: A completed at 2700 s, exit 0, 25,431,727 bytes, 22/22 output hashes, 18/18 XML files, complete 2700-step FCD/summary/queue and detector intervals, correct OPEN TLS, no errors/warnings or resource stop. The data analyst's reproducible phase-1 package is in `data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/a_prergate/`.

Independent scientific reparse restricted to `<540 s` confirmed exact R0/A FCD equality for M 33,991, U 3,053 and X 1,766 vehicle-second records, with zero one-arm-only or mismatched tuples. Actual pre-R departures match by identity/time: M502, U54, X27. `M_flow.502` was planned at 539.148 s and actually inserted at 540 s in both arms, outside strict `[0,540)`. Both arms have complete M/U/X lifecycle; A has R240/240 inserted and arrived, zero unfinished/never inserted/errors. R first departs at 540 s, first route-consistent through-lane entry is 592 s, and unique through entries are 211/225/240 by inclusive 1440/1500/2700 s. Auxiliary 1 Hz FCD sees only 207/240 R overall, so this detector view is incomplete; route-consistent through reconstruction is retained.

Phase 2 must show all fixed cells/windows and reconcile decisive M measures to raw per-vehicle records; assess internal-lane/detector coverage and source/downstream explanations. No post-540 M outcome was examined during this phase-1 gate.
