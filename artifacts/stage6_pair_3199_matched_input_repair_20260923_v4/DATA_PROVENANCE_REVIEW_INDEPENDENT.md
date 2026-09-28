# Independent data/provenance review — PAIR3199 matched-input repair v4

**Disposition: PASS for offline input construction and provenance.** SUMO, TraCI and netconvert starts: 0. This is not a new run authorization and does not reinterpret the previous treatment's `NOT_EVALUABLE` result.

## Context and scope

Project state records the single `PAIR_3199_R720_DELAYED_S17` start as consumed. The adopted Stage 6 witness contract requires matched common identities/attributes and later review of pre-R trajectories; `docs/EXPERIMENT_PROTOCOL.md` remains unfrozen. This independent review inspected v4 generated route files, source/provenance bindings, strict checker, tests, and previous package supersession status. Raw outputs were read-only.

## Independent data and provenance recomputation

Both XMLs were independently parsed. I resolved each vehicle's route and vType definitions, recomputed integer-millisecond departure schedules, compared full common vehicle records and recalculated every receipt and manifest SHA-256.

| Invariant | Independent result |
|---|---:|
| Control identities | M=1,333; U=150; X=75; R=0 (1,558 total) |
| Treatment identities | M=1,333; U=150; X=75; R=192 (1,750 total) |
| Common M/U/X IDs and full records | 1,558 / 1,558 exact |
| Integer-ms desired departures | M 1,333/1,333; U 150/150; X 75/75; R 192/192 |
| Treatment-only identities | Exactly `R_flow.0`–`R_flow.191` |
| Route definitions and vType definitions | 4/4 routes and 1/1 vType exactly equal |
| Control `vehroute.xml` speedFactor matches | M 1,333/1,333; U 150/150; X 75/75 |
| Package file receipt hashes | 5/5 match |
| Checker/test receipt hashes | 2/2 match |
| Manifest source hashes | 5/5 match |

Integer schedule offsets are M=1,125 ms, U=10,000 ms, X=20,000 ms and R=5,000 ms. First/last desired departures are M 0.000/1498.500 s, U 0.000/1490.000 s, X 0.000/1480.000 s and R 540.000/1495.000 s. No common record differs; there are no control-only identities, and all treatment-only records are R.

Verified hashes:

- `control/demand.rou.xml`: `b98bbedfb4dc4310526184e4d326bd9a9e03e072683aa67f8116bd56c5f9bd81`
- `treatment/demand.rou.xml`: `b8aae801122e918731fb8e4d326bd9a9e03e072683aa67f8116bd56f6bea96ea`
- Checker `scripts/stage6/pair3199_common_demand.py`: `ea63d2ad5add0158ded96b4eb4623cc25a597e473f2cbf0566602a7dff8c75ad`
- Tests `tests/test_pair3199_common_demand.py`: `1971364964e4265a6e5554e8bdaf0711ed82ee5f17527f12f9d477992b0c5b58`
- Immutable control vehroute source: `c64bdadbfdd98923417356033c36832d1e19292a3b08ecf000e27e568bfe8306`
- Original control/treatment demand sources: `6bbdc1d9148b05286c25b94f23c37174951c9f3e4a544ef8b9a322fbc42ab631` / `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`
- Network reference: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`

## Fail-closed checker verification

The targeted tests independently ran **9/9 PASS**. In addition to the valid pair, missing-U, speedFactor, route-edge and vType mutations, tests reject the v4 bypass cases: treatment-only top-level `<flow>`, nested common-vehicle `<param>`, and an unlisted vehicle attribute.

Static inspection confirms that the parser rejects DTD/entities; unsupported top-level elements; nested child elements; comments or processing instructions; mixed text; unsupported root/node attributes; duplicate route, vType or vehicle identities; unresolved route/type references; invalid schedules; and nonpositive/missing speedFactors. The exact vehicle attribute allowlist rejects unknown per-vehicle behavior fields. The checker compares route/vType definition maps as well as all permitted common vehicle attributes, enforces the fixed counts/identity sets and schedule, and rejects every treatment-only identity except the prescribed R set. Running the checker against v4 files independently returned `PASS`: 1,558 common full records, 4/4 route definitions and 1/1 vType definitions equal.

## Precision and supersession

The common M/U/X factors come from immutable control `vehroute.xml`, not two-decimal `tripinfo.xml`. For example, `M_flow.1` is `1.1361` in vehroute and in both v4 inputs, while tripinfo reports `1.14`. Thus the earlier tripinfo-rounding trap is avoided. V4's receipt and repair report explicitly supersede v3; v3 and its prior independent review remain preserved for audit. V3's report identifies the checker gap that v4 addresses. V1's retained notice records its precision issue; the current chain is v4 superseding v3, which superseded earlier revisions.

## Limitations and boundary

This PASS establishes input-level matching of identity, desired departure, route, type, speedFactor and explicit departure-placement attributes, with a strict XML allowlist. It cannot establish future insertion success or identical dynamic trajectories: adding R may still change traffic interactions or simulation-time random decisions. Serialized vehroute factors are the most precise per-vehicle values recorded in the inspected source; this review makes no claim about unrecorded floating-point bits. A future run requires a new exact card bound to these inputs, fresh prelaunch review and separate user authorization. Post-run lifecycle and pre-R trajectory checks remain required under the adopted witness contract. The previous one-start authorization remains consumed; v4 includes no card or authorization.

**Data/provenance review: PASS** for this offline v4 input repair, limited to static matching/provenance as stated.
