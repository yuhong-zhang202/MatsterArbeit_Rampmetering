# Independent scientific post-run review — RETRY3

**Disposition:** `NOT_EVALUABLE`  
**Confidence:** High  
**Findings:** Blocker 0 / Major 1 / required Minor 0

The run is technically and lifecycle interpretable. All 1,396 M and 240 R vehicles completed; pre-R M matched exactly over 34,491 vehicle-seconds; T3 confirmed at 660 s; and R900 yielded more unique merge entries than R720 at both fixed cutoffs.

The run cannot be classified as `NO_WITNESS`. In core cell 15, treatment has a four-bin P low-state episode `[1260,1380)`, but its immediately preceding reference bins average 0.840, 0.780, and 0.762, below the locked 0.85 reference criterion. The correct locked status is `ONSET_REFERENCE_UNRESOLVED`: this is not a confirmed State1-positive event and it prevents a clean negative classification. L also has unresolved primary-window episodes; S has no qualifying event. Candidate A=0. Candidate C warnings are retained as diagnostics.

Same-time/lane/cell differences are descriptive and cannot resolve the reference failure. No mainline red or ramp non-green TLS was identified, and lifecycle is complete. Queue morphology is unavailable because the queue XML contains no lane records; E1 aggregates cannot identify vehicle classes or identities. The first single-M trajectory difference at 585 s predates T3 and is not collective deterioration evidence.

The earlier data-side `NO_WITNESS` is withdrawn. The reporting regression issue is closed for this run by the retry3-specific adapter and 3 passing tests; shared analyzer/classifier, thresholds, raw data, and scientific rules were unchanged. No further run is authorized or started.
