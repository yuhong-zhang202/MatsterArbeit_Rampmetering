# Independent scientific post-run review — MINIMAL3199_CTRL_S17_TECH_RETRY2

**Disposition:** `LOW_R_BACKGROUND_ACCEPTABLE` — only as the R=0 control for the approved minimal U=X=0 exploratory existence-test plan.

This is not a clean high-mobility baseline, a general low-R background conclusion, or evidence of a treatment effect.

**Findings:** Blocker/Major/required Minor = 0/0/0. **Confidence: Moderate–High.**

## Basis

- Engineering integrity passed with all 18 output roles and hashes matching.
- Lifecycle is complete: M=1,333/1,333 inserted and arrived; none unfinished; R/U/X=0.
- Locked P/S/L is `NO_QUALIFYING_EVENT`; Candidate A is `NO_SPATIAL_CANDIDATE`.
- Candidate C warnings remain visible: 20 merge-core warning rows and 42 L rows. Each L row occupies one 30-second bin, below the locked two-bin sustained-event duration. Recurring patches at 720, 990, 1170, 1380, 1470 and 1500 seconds mean the run must not be called a clean normal baseline.
- The strict legacy high-mobility/reference screen remains FAIL (160/180), unchanged and not recoded.
- Downstream detectors contain entries for all 1,333 M vehicles; FCD and E1 coverage are complete. Queue export has complete timestamps but empty lane arrays, so queue absence is not established.

The reviewer judged the remaining warnings insufficient to establish sustained self-congestion under the approved minimal plan’s unchanged locked criteria. The queue-export gap leaves transient queue occupancy unverified; detector and trajectory coverage bound but do not eliminate that uncertainty. The reviewer relied on the data/lifecycle report for measurement check 4 and did not recompute it from raw vehicle records.

This classification applies only to this qMain=3199.2, seed17, R=0, U=X=0 control. It establishes neither a witness nor a treatment contrast. Stop is appropriate after this review. No threshold, classifier, witness-contract or formal-protocol change is made.

The scientific reviewer returned a read-only disposition; this file records that disposition and rationale. See the accompanying JSON for exact provenance hashes.
