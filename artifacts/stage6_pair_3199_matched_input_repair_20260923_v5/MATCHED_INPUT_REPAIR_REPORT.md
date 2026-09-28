# PAIR3199 matched-input repair — checker revision 5

**Disposition:** `PAIR3199_MATCHED_INPUTS_REPAIRED_PRELAUNCH_NOT_AUTHORIZED`. v5 is an offline input package only; no run card or launch authorization exists.

## XML hardening

v4 remains unchanged and is superseded by v5 after independent review showed that an encoding-dependent byte scan could miss a UTF-16 DTD supplying default vehicle attributes. v5 now:

- accepts only strict UTF-8 without a BOM and rejects NUL bytes or non-UTF-8 XML declarations;
- performs an Expat safety pass with callbacks that reject DOCTYPE declarations, entity declarations/references, comments and processing instructions before building the ElementTree;
- rejects unknown top-level nodes, all nested elements, mixed text, duplicate definitions, missing or unknown attributes, and DTD/entity declarations;
- retains full cross-arm route/vType comparison and the vehicle/count/schedule/R-only invariants.

## Rebuilt pair and verification

The materializer rebuilt v5 from the immutable original control/treatment demand sources and existing raw `vehroute.xml` attributes. It first confirms the source route and vType maps match. The generated control contains M/U/X = 1,333/150/75; treatment contains M/U/X/R = 1,333/150/75/192. The pair checker passes with 1,558/1,558 matching shared identities, full vehicle records, integer-ms departure schedules, route/type and exact speedFactors; route definitions match 4/4 and vType definitions 1/1. Treatment-only vehicle identities are exactly R_flow.0–R_flow.191.

The 12-test suite passes, including regression cases for treatment-only `<flow>`, nested vehicle `<param>`, UTF-16 DTD default-attribute bypass, UTF-8 DTD default attributes, UTF-8 BOM, and an unlisted vehicle attribute, as well as route/vType mutation cases. `checker_fail_closed: true` is the enforced policy; `mismatch_detected: false` is the result for the valid v5 pair.

Earlier findings remain unchanged: treatment route ordering caused SUMO to ignore U/X; M speedFactors were not materialized in the old input and only 2/1,333 exact values matched (including 1/480 before R activation). The exact internal RNG draw/order point is still unverified. No SUMO, TraCI or netconvert was run; no raw output or scientific input was changed. Prior treatment authorization remains consumed. v5 does not authorize another attempt.

## Provenance

See `COMMON_DEMAND_MANIFEST.json`, `INVARIANT_CHECK_REPORT.json`, and `PROVENANCE_RECEIPT.json`. Receipt bindings include generated v5 inputs, checker source and tests; v5 supersedes v4.
