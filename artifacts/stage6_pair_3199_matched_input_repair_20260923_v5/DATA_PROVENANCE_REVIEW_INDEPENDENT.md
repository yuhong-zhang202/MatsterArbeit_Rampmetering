# Independent data/provenance review — PAIR3199 matched-input repair v5

**Disposition: PASS for offline input construction and provenance.** No SUMO, TraCI or netconvert process was started. This review does not authorize a new run or reinterpret the previous treatment's `NOT_EVALUABLE` result.

## Context and scope

The current project state records the single `PAIR_3199_R720_DELAYED_S17` start as consumed. The adopted Stage 6 witness contract requires identity/attribute matching and later review of realized lifecycle and pre-R trajectories; the formal experiment protocol remains unfrozen. This review independently inspected v5 inputs, hashes, schedules, strict XML checker/tests and retained superseded package history. Raw outputs were read-only.

## Independent input and provenance verification

I independently parsed each route file, resolved route and vType definitions, recomputed schedules in integer milliseconds, compared full common records, and recomputed package, code and source hashes.

| Invariant | Result |
|---|---:|
| Control M/U/X/R identities | 1,333 / 150 / 75 / 0 (1,558 total) |
| Treatment M/U/X/R identities | 1,333 / 150 / 75 / 192 (1,750 total) |
| Common M/U/X IDs and full records | 1,558 / 1,558 exact |
| Desired integer-ms schedules | M 1,333/1,333; U 150/150; X 75/75; R 192/192 |
| Route definitions and vType definitions | 4/4 routes and 1/1 vType equal |
| Control `vehroute.xml` speedFactor matches | M 1,333/1,333; U 150/150; X 75/75 |
| Control-only IDs | 0 |
| Treatment-only IDs | Exactly `R_flow.0`–`R_flow.191` |
| Receipt package hashes | 5/5 match |
| Receipt checker/test hashes | 2/2 match |
| Manifest source hashes | 5/5 match |

Integer schedule offsets are M=1,125 ms, U=10,000 ms, X=20,000 ms and R=5,000 ms. First/last desired departures are M 0.000/1498.500 s, U 0.000/1490.000 s, X 0.000/1480.000 s and R 540.000/1495.000 s. Treatment differs by exactly the R vehicle records; all common identities have the same attributes and resolved route/vType definitions.

Verified hashes:

- Control demand: `b98bbedfb4dc4310526184e4d326bd9a9e03e072683aa67f8116bd56c5f9bd81`
- Treatment demand: `b8aae801122e918731fb8e4d326bd9a9e03e072683aa67f8116bd56f6bea96ea`
- Checker `scripts/stage6/pair3199_common_demand.py`: `b7fbf945230574a459e5d28ab0512e742c58ccd079a0d84eef67f0fc4e5556d8`
- Tests `tests/test_pair3199_common_demand.py`: `df868a0ce948f77f6ee8ff2acbce98322801587d00931a8b60e2cfc0b7e22045`
- Immutable control vehroute: `c64bdadbfdd98923417356033c36832d1e19292a3b08ecf000e27e568bfe8306`
- Original control/treatment demand sources: `6bbdc1d9148b05286c25b94f23c37174951c9f3e4a544ef8b9a322fbc42ab631` / `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`
- Network reference: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`

## Strict XML validation and regression tests

The targeted suite independently ran **12/12 PASS**. Tests cover the valid pair, missing U, common speedFactor mismatch, missing explicit speedFactor, route-edge and vType-definition drift, extra treatment-only top-level `<flow>`, nested vehicle `<param>`, unknown vehicle attribute, UTF-8 DTD default attributes, a UTF-16 DTD default-attribute bypass, and UTF-8 BOM rejection.

Static inspection confirms v5 requires strict UTF-8 without BOM; runs an Expat safety parse rejecting DOCTYPE/entity declarations and references, comments and processing instructions; then applies a strict element/attribute allowlist. It rejects unknown top-level nodes, nested elements, mixed text, duplicate definitions/IDs, unresolved type/route references, unsupported attributes and invalid/missing speedFactors. The checker compares complete allowed route/vType attribute maps and common vehicle records, fixed identities/counts, integer schedules and exact treatment-only R IDs. Running it independently on v5 returned PASS (1,558 common complete records; routes 4/4 and vTypes 1/1 equal).

The speedFactor precision trap is excluded: `M_flow.1` is `1.1361` in immutable control `vehroute.xml` and both v5 inputs, whereas `tripinfo.xml` rounds it to `1.14`. V5's receipt/report explicitly supersede v4; v4 and earlier package versions remain preserved for audit. V4's retained findings on earlier fail-closed gaps are addressed by the v5 UTF-8/DTD protections and regression fixtures.

## Limitations and boundary

This review establishes static input matching and provenance for identity, desired departure, route, vType, speedFactor and permitted departure-placement attributes. It does not establish future insertion success or identical dynamic trajectories; R can still affect traffic interactions and simulation-time random decisions. The serialized `vehroute.xml` factors are the most precise recorded values used here, not a claim about unrecorded floating-point bits. Any future attempt requires a new exact card bound to these hashes, fresh prelaunch reviews and separate user authorization; post-run lifecycle and pre-R trajectory checks remain necessary. The one-start authorization is consumed; v5 contains no card or execution authorization.

**Data/provenance review: PASS** for this offline v5 input construction, limited to static input matching and provenance.
