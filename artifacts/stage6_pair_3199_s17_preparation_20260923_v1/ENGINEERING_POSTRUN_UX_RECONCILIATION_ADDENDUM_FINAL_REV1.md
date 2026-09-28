# Engineering addendum — U/X realization finding

**Disposition:** Execution and raw-output integrity remain **PASS**. The prior
required U/X data-reconciliation issue is **closed as a confirmed
simulation-input realization failure**. Overall pair disposition remains the
data review's `NOT_EVALUABLE`; this addendum does not classify a witness or a
scientific outcome.

## Evidence binding

The independent data/lifecycle report
`data/processed/stage6_pair_3199_s17_treatment_postrun_20260923_v1/analysis_rev6/DATA_LIFECYCLE_REVIEW.md`
has SHA-256
`54e7830620f9d945749b5c8bb215182b05f2e34575b93484be6d38dfc6032509`; its
receipt `DATA_REVIEW_RECEIPT.json` has SHA-256
`7074ebce98e42b1bc730f832b73032945188dad6f568f64b5ff2e7ac20b68338`. The
receipt binds treatment raw-manifest SHA-256
`92dbe5627f8afbfe26f50bc8d62207ca9a9ed579c6f707481079d8ad795228dd`, exact
FINAL card SHA-256
`08160a2ad225ee9fcc2abcc11d509a88ecf554252f1fb17e35dc69b9404351d4`, and the
adopted witness-contract hash.

The earlier engineering report SHA-256
`81483835553e7cc7e50849f353cae18364d9e2bba132a378ae554673794a61da` verified
one authorized R02 start, normal exit at t=2700, rc=0, 19.92132 s, payload
21,066,503 bytes under the 120 s / 90,000,000-byte stop triggers, retry
disabled, and complete hash/size reconciliation of 18/18 required roles and
25/25 manifest-inventoried files. Those execution and raw-file integrity
findings are unchanged.

## Closed U/X issue

The data review joined the planned identities against route, tripinfo and FCD
records. Planned M/R/U/X were 1,333/192/150/75; observed identity counts were
1,333/192/0/0. All 150 scheduled U IDs and 75 scheduled X IDs (225 total) are
absent from all three lifecycle/trajectory sources. The treatment SUMO log,
SHA-256
`4be0e443c50ca88ac78e924ac7f4ae2067bd2b7cd5e78b650ead89a2ad563e2a`, contains
the `U_flow` and `X_flow` departure-sort warnings and reports `Inserted: 1525`.
The data receipt classifies this as
`FLOW_IGNORED_WARNING_CONFIRMED_BY_ID_SET_DIFFERENCE`; insertion counts for
these absent U/X identities remain **unknown**. This is confirmed lack of
planned U/X realization in the recorded run, not evidence that raw files were
corrupted or that SUMO failed to execute.

The control realized the planned U/X identities. Therefore treatment and
control do not differ only in R; the run cannot be treated as a valid matched
R-only contrast. This supports the data review's `NOT_EVALUABLE` disposition.
It does not make any claim about the presence or absence of a ramp-induced
traffic event. The scientific post-run reviewer retains sole responsibility
for the final bounded scientific disposition.

No raw, input, classifier, threshold, geometry, vehicle-behavior, witness
contract, or formal-protocol file was changed. No simulator, TraCI, or
netconvert process was invoked for this addendum; it only rechecked the hashes
of the cited review/receipt and bound execution records.
