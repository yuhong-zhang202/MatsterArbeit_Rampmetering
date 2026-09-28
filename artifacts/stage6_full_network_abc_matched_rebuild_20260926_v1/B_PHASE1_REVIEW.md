# Default-model B Phase 1 scientific eligibility, 2026-09-26

**Independent disposition: `PASS_RELEASE_B_POST_R_ANALYSIS`**, High confidence in pairability and actual treatment exposure; no B freeway/ramp/urban outcome yet. C remains held.

Engineering review independently checked exact-card, one-use reservation, receipt, 22/22 raw hashes, 18 XML, 2700 FCD/summary/queue steps and full detector/TLS coverage. SUMO ended at 2700 s, exit 0, no resource stop, warning/error, collision, teleport, discard, final waiting or unfinished vehicle. All planned M1396/R240/U150/X75 were inserted and arrived. The B signal actually followed `B_MODERATE` for all 2700 s (990 green, 135 yellow, 1575 red seconds); A was green throughout. The urban signal states were identical.

The raw-bound data report `data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/b_phase1/B_PHASE1_REVIEW.json` confirms A/B input demand XML is identical, and all 38,810 `[0,540)` M/U/X identity-second FCD trajectories and pre-540 M502/U54/X27 departures match exactly. All 240 R in both arms enter the merge-section edge and arrive. First entry is t592 in A and t613 in B; unique entries by 1440/1500 are A211/226 and B159/170, both 240 overall. This establishes actual moderate-metering exposure without treating requested flow as realized admission.

The scientific reviewer independently judged the A/B pair eligible for post-R fixed-window M protection, ramp queue and urban cost analysis. It did not classify B or release C. The default-model A's numerical effect attribution remains unidentified; B's earliest differences and RNG/source alternatives must be examined before a scientific conclusion.
