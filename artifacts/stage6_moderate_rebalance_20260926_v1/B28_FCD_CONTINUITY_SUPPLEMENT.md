# B28/A per-vehicle FCD continuity supplement

**Date:** 2026-09-26  
**Reviewer:** independent `data_analyst`, read-only raw inspection after final Stage 6 scientific red-team.  
**Disposition:** `PASS_FCD_PER_VEHICLE_CONTINUITY` (High confidence); no change to B28 scientific outcome or Stage 6 `PARTIAL`.

The original B28 analyzer checked all 2700 global FCD seconds, duplicate `(vehicle ID, second)` records and ID presence, but did not explicitly prove that an individual vehicle had no missing interior second. This supplementary audit checked the immutable default V2 A and B28 raw FCD/tripinfo against their completed execution receipts. FCD/tripinfo sizes and SHA-256 match both receipts. For each ID in M1396/R240/U150/X75, the reviewer compared the sorted FCD second list to every integer second from its first through last observation, rejected duplicate/noninteger/unknown/missing IDs, and checked first FCD second against realized tripinfo `depart` and last against `arrival−1`.

| Arm | FCD vehicle rows | Observed IDs | Interior gaps | Duplicate ID/second | Endpoint exceptions |
|---|---:|---:|---:|---:|---:|
| Default V2 A | 138,732 | 1,861 | 0 | 0 | 0 |
| B_REBALANCED28 | 143,493 | 1,861 | 0 | 0 | 0 |

Every first FCD second equals realized departure; every last equals arrival minus one. Class-specific FCD vehicle-seconds equal `sum(arrival−depart)` in each arm: A M102,695/R21,195/U9,737/X5,105; B28 M103,702/R24,949/U9,737/X5,105. The two files each cover 2700 timesteps. No missing sample was imputed, no output or analysis file was overwritten, and no SUMO run occurred. This closes a measurement-completeness gap; it does not resolve early nonlocal default-model M divergence or prove physical spillback.
