# Independent data/provenance review — PAIR3199 matched-input repair v2

**Disposition: FAIL pending checker hardening.** The generated XML inputs and package provenance independently satisfy the stated matching invariants, but the supplied checker is not fail-closed against route/type definition changes under unchanged identifiers. This review does not authorize a run, certify future insertion/trajectory matching, or reinterpret the previous treatment. No SUMO, TraCI, or netconvert process was started.

## Context and scope

The current project state records the earlier `PAIR_3199_R720_DELAYED_S17` output as `NOT_EVALUABLE`, with the single authorized start consumed. The adopted Stage 6 witness contract requires identity/attribute matching and pre-R trajectory scrutiny; `docs/EXPERIMENT_PROTOCOL.md` remains unfrozen. This review is limited to static input data, source hashes, the invariant checker and its tests. The old control and treatment raw outputs were read only.

## Independent checks

I independently parsed both generated route XML files, resolved route IDs to edge sequences, reconstructed integer-millisecond schedules from the original flow definitions, recomputed identity and attribute comparisons, and recalculated all listed SHA-256 values.

| Check | Independent result |
|---|---:|
| Control entries | M=1,333; U=150; X=75; R=0 (1,558 total) |
| Treatment entries | M=1,333; U=150; X=75; R=192 (1,750 total) |
| Common M/U/X identities | 1,558 / 1,558 |
| Full parsed common record equality, including route edge sequence | 1,558 / 1,558 |
| Integer-ms desired departure matches | M 1,333/1,333; U 150/150; X 75/75; R 192/192 |
| Treatment-only identities | Exactly `R_flow.0`–`R_flow.191` |
| Source control `vehroute.xml` speedFactor lexical matches | M 1,333/1,333; U 150/150; X 75/75 |
| Package file hashes | 5/5 match receipt |
| Checker/test hashes | 2/2 match receipt |
| Manifest input-source hashes | 5/5 match source files |

Independent schedule offsets are M=1,125 ms, U=10,000 ms, X=20,000 ms, R=5,000 ms. First/last desired departures are M 0.000/1498.500 s, U 0.000/1490.000 s, X 0.000/1480.000 s, and R 540.000/1495.000 s. The treatment contains no control-only IDs and its only additional vehicle records are the planned R identities.

The paired route files have byte SHA-256 values:

- `control/demand.rou.xml`: `b98bbedfb4dc4310526184e4d326bd9a9e03e072683aa67f8116bd56c5f9bd81`
- `treatment/demand.rou.xml`: `b8aae801122e918731fb8e4d326bd9a9e03e072683aa67f8116bd56f6bea96ea`

The immutable control `vehroute.xml` hash is `c64bdadbfdd98923417356033c36832d1e19292a3b08ecf000e27e568bfe8306`; the original control/treatment source demand hashes are `6bbdc1d9148b05286c25b94f23c37174951c9f3e4a544ef8b9a322fbc42ab631` and `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`. The network reference hash is `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`.

## Precision and supersession

The materializer takes M/U/X `speedFactor` lexical values from the existing control `vehroute.xml`, not `tripinfo.xml`. Independent examples confirm the precision distinction: `M_flow.1` is `1.1361` in `vehroute.xml` and `1.14` in `tripinfo.xml`; the generated common inputs retain `1.1361` in both arms. I found no common-vehicle speedFactor mismatch in v2. The existing v1 `SUPERSESSION_NOTICE.md` explicitly marks v1 superseded because it sourced two-decimal tripinfo factors; that notice says v1 is retained for audit and is not to be used for any future run preparation. V2 therefore excludes the identified tripinfo rounding trap and clearly supersedes v1 for the matched inputs.

The checker unit suite was independently run: 4 tests passed, including injected missing-U and speedFactor-mismatch cases. Static inspection confirms it checks fixed class counts/ID sets, integer schedules, route/type identifiers, explicit positive speedFactors, shared vehicle-attribute equality, and treatment-only R IDs. The receipt hashes bind the exact checker and tests reviewed here.

**Required checker issue:** `parse_materialized()` resolves only whether a referenced route/type ID exists. `check_pair()` compares the route/type ID strings on each common vehicle, but does not compare the referenced route edge lists or the referenced vType definitions between arms. I independently resolved current route references and confirmed their edge lists match, and both current files use the same `technical_passenger` definition; nevertheless, changing a treatment route's edge list or a vType parameter under the existing ID would escape the checker. Add fail-closed equality checks for route and vType definitions plus mutation tests, then rerun the invariant check and this independent review. Current XML content itself has no such mismatch.

## Limitations and boundary

The existing `vehroute.xml` serialized speedFactor values (four decimal places) are the highest-precision recorded per-vehicle values used here; they are not a claim to recover hidden floating-point bits beyond the raw output representation. The test establishes deterministic **input** equality for the specified shared attributes and copied departure-placement fields. It does not establish equal future random lane-change or trajectory realizations: inserting R can still alter simulation-time random draws and traffic interactions. Future use must hash-bind these exact v2 inputs in a newly reviewed card and preflight, and post-run analysis must still check realized lifecycle and pre-R trajectories against the adopted witness contract. No launch authorization is present; the prior one-start authorization remains consumed.

**Data/provenance review: FAIL pending the checker issue above.** The current paired inputs match exactly and source provenance hashes verify; the gate remains closed until the checker also rejects semantic route/type drift.
