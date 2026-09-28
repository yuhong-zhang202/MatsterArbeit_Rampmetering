# MINIMAL3350_CTRL_S17 Engineering Prelaunch Review

**Disposition:** `PASS_PRELAUNCH` — engineering scope only.

- Exact card SHA-256: `6095e498eb560d2ed8dc16548e19902313d7a89be92057db0d2fae689497c2ac`
- R02 runner SHA-256: `5cfbd1542016205203ed046756ef00800d1d5fe0070aa20878ebdd0d6a67384a`
- The control condition is fixed at qMain=3350.4, seed17, R=0, U=0, X=0, with 1,396 explicitly materialized M vehicles. SUMO 1.26.0 integer time semantics give a 1,074 ms offset and last desired departure 1,498,230 ms.
- Runtime, SUMO_HOME, additional schema and runner hashes are bound. The Guardian request uses `r02-start-v2`; exact request validation passed offline.
- Output path is absent. Resource trigger is 90 s / 60,000,000 bytes, 100 ms polling with slight overshoot accepted.
- R02 launch gate requires exact-card engineering, data/provenance and scientific receipts with zero blocker/major/required-minor findings. `make_plan` reports `launchable_now=false` while receipts are absent.
- Focused regression suite: 4 tests PASS. No Guardian, SUMO, TraCI or netconvert process started.

**Reviewer limitation for independent adjudication:** the per-vehicle speedFactor values are sourced from the prior full-network qMain=3350.4 seed17 `vehroute.xml`, where U/X were nonzero. The source raw hash and generated common M list are bound in `COMMON_M_DEMAND_MANIFEST.json`; whether this sampled list is acceptable for the minimal module remains for data/scientific review.
