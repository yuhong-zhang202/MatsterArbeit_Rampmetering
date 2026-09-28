# Independent engineering feasibility review

**Scope:** Read-only static review of the proposed U=X=0 paired mechanism test.  
**Disposition:** `FEASIBLE_CONDITIONAL_ON_NEW_BINDING`, High confidence for static feasibility; runtime behavior unknown.  
**SUMO / TraCI / netconvert starts:** 0 / 0 / 0.

The existing accepted network SHA-256 is `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. A new paired demand can retain that network, `urban_tls`, A_OPEN, 1 s step, 2700 s horizon and current detectors. For qMain3199.2, derive both arms from the previously reviewed v5 materialized vehicle records. Keep the M1333 records identical, remove U/X records from both arms, record R=0 explicitly for control, and add only `R_flow.0`–`.191` at 5 s spacing from 540 to 1495 to treatment. Retain route and vType definitions and sort vehicles globally by `(depart_ms,id)`; do not rely on unvalidated zero-count flows.

The existing v5 invariant checker and R04 adapter bind U150/X75, old IDs and hashes. They cannot be reused unchanged. A future fail-closed U=X0 checker/adapter and offline tests must preserve the locked classifier and measurement formulas, enforce 100% M per-identity planned-attribute equality, and show treatment-only R192. Same seed and materialized speedFactor fix planned attributes but do not statically establish runtime RNG consumption or trajectory equality. Future raw must establish actual insertion, pre-treatment M matching, R merge exposure and output coverage. Existing U/X-positive R0 raw is not a control for this module.

This engineering review provides no card, input construction, runtime approval or simulation result. The reviewer rechecked network and v5 demand hashes against existing receipts; no files were edited during the review.
