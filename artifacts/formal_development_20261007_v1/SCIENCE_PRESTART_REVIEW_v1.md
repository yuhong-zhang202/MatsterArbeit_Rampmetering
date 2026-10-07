# Pre-start scientific review — v1

Date: 2026-10-07. Reviewer: project scientific_reviewer, read-only. Status: HOLD — technical interface defect; no simulation launched.

The temporary geometry-based risk proxy, threshold/hysteresis, independent nominal ALINEA state, fixed horizon and scoped resource envelope passed the bounded design review. The proxy permits gaps and a single slow R trigger; it does not identify a continuous physical queue or uniquely identify a queue origin. Shared-only low R is outside triggering but remains measured. No guaranteed improvement or clearance is required.

The exact initial OPEN card SHA-256 was `bd409dc251e6f722266a33c218ce395ba77852eaaa9cbe11ca5a66cbded6feda`; parameter contract SHA-256 was `31f439c1a83f724259d7a74a382b3d03b6cb82378ec145b85431739655ca07f3`.

Final code/card review found a definite blocker: `v15_worker.py` reads `card["startup_deadline_s"]`, but the prepared card lacks that key. The error would occur after spawning SUMO and before connection. Compile, six offline tests and generic preflight did not cover this interface. A read-only AST check found this was the only missing direct card key.

Required minimum repair: bind the existing60s startup deadline consistently, add a no-SUMO card-interface regression/preflight check, preserve the initial source/card provenance, and bind a new revision before release. User-authorized ordinary technical repair applies; no new scientific parameter approval is needed. The blocked preparation is not a physical startup attempt.

The reviewed design also applies to the same-parameter S17 R900 T2 and R750 T1/T2, but their actual starts remain gated by OPEN equivalence and independent data checks. Runtime space/time/measurement qualifications are not yet established. Stage6 remains closed and formal protocol empty.
