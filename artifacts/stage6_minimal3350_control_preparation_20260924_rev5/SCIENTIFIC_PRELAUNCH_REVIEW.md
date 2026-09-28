# Independent scientific prelaunch review — MINIMAL3350 control REV5

**Disposition:** `PASS_PRELAUNCH`  
**Blocker / Major / required Minor:** 0 / 0 / 0  
**Confidence:** High for card/design alignment; Moderate for interpretation beyond this single fixed seed/vector.

Scope is `MINIMAL3350_CTRL_S17`: qMain=3350.4 veh/h, seed17, U=X=0, R=0. The reviewer did not inspect or infer any 3350 treatment outcome. The qMain3199.2 pair remains the already reviewed `NO_WITNESS`; this review does not reuse historical 3350 suitability assessments.

## Scientific and input assessment

The common M manifest has 1,396 unique identities, an integer SUMO schedule of `i × 1,074 ms`, last departure at 1,498,230 ms, and explicit route/type/behavior attributes. R, U and X are explicitly zero. The card binds the approved locked classifier and exploratory method without changing geometry, vehicle behavior, thresholds, witness rules or formal protocol.

The per-vehicle speedFactor vector comes from the prior qMain=3350.4 seed17 full-network `vehroute.xml` where U/X were present. The reviewer accepts it as a reproducible fixed vector for this conditional matched exploratory contrast if treatment reuses the same manifest. It does not establish a representative or independently sampled U=X=0 seed17 RNG realization.

## Output paths, resources and execution boundary

All eight `sumocfg` targets, twelve additional-file targets and eighteen output-role paths resolve under the same unique output directory bound by the card and runner. The twenty unique configured targets are absent. The request remains persisted and unsent. Resource contract: 90 s wall-clock, 60,000,000 bytes, 100 ms polling, slight overshoot accepted.

This PASS does not classify the future control outcome or release treatment. Engineering and data/provenance prelaunch reviews also pass; runtime coverage and lifecycle remain to be verified after the single authorized control run.

**Final review:** `PASS_PRELAUNCH`, 0/0/0. Full evidence bindings are in `SCIENTIFIC_PRELAUNCH_REVIEW.json`. No process was started by this reviewer.
