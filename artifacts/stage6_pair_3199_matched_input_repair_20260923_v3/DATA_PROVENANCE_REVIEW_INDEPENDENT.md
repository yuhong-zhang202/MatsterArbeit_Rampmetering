# Independent data/provenance review — PAIR3199 matched-input repair v3

**Disposition: PASS for offline input construction and provenance.** No SUMO, TraCI, or netconvert process was started. This does not authorize a new run and does not reinterpret the previous treatment as a witness or negative result.

## Context and review scope

Project state records the single `PAIR_3199_R720_DELAYED_S17` start as consumed and the treatment disposition as `NOT_EVALUABLE`; the adopted witness contract requires same-identity attributes and review of pre-R trajectories. The formal experiment protocol remains unfrozen. This review independently inspected v3 XML, manifest, provenance receipt, checker, tests, existing source files and prior v1/v2 status. Raw outputs were read-only.

## Independent recomputation

I independently parsed both generated XML files, resolved every vehicle's route and vType definitions, reconstructed desired departures in integer milliseconds, compared complete common vehicle records and recomputed source and package SHA-256 values.

| Invariant | Independent result |
|---|---:|
| Control identities | M=1,333; U=150; X=75; R=0 (1,558 total) |
| Treatment identities | M=1,333; U=150; X=75; R=192 (1,750 total) |
| Common M/U/X identities and complete records | 1,558 / 1,558 exact |
| Depart schedules | M 1,333/1,333; U 150/150; X 75/75; R 192/192 |
| Treatment-only identities | Exactly `R_flow.0`–`R_flow.191` |
| Route definitions, including edge lists and attributes | 4/4 identical |
| vType definitions, including attributes | 1/1 identical |
| Control `vehroute.xml` speedFactor exact lexical matches | M 1,333/1,333; U 150/150; X 75/75 |
| Package hashes in receipt | 5/5 match |
| Checker/test hashes in receipt | 2/2 match |
| Manifest source hashes | 5/5 match |

Integer schedule offsets are M=1,125 ms, U=10,000 ms, X=20,000 ms and R=5,000 ms. The respective first/last desired departures are M 0.000/1498.500 s, U 0.000/1490.000 s, X 0.000/1480.000 s and R 540.000/1495.000 s. There are no control-only identities. Both files retain the same route and vType definitions; the only additional vehicle records in treatment are the 192 R records.

Key verified hashes:

- Control demand: `b98bbedfb4dc4310526184e4d326bd9a9e03e072683aa67f8116bd56c5f9bd81`
- Treatment demand: `b8aae801122e918731fb8e4d326bd9a9e03e072683aa67f8116bd56f6bea96ea`
- Checker `scripts/stage6/pair3199_common_demand.py`: `e18ac586926ef255c7c5d78f267b37244766d09d9729a4a3e9836f45e287169e`
- Tests `tests/test_pair3199_common_demand.py`: `6e12232410d8bdfbbb7e3f329938a8fd96ecc7aff748db04777adcb4a47e7983`
- Existing control vehroute source: `c64bdadbfdd98923417356033c36832d1e19292a3b08ecf000e27e568bfe8306`
- Existing control/treatment flow sources: `6bbdc1d9148b05286c25b94f23c37174951c9f3e4a544ef8b9a322fbc42ab631` / `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`
- Network reference: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`

## Precision trap, checker and supersession

V3 preserves common M/U/X per-vehicle factors from immutable control `vehroute.xml`, not two-decimal `tripinfo.xml`. For example, `M_flow.1` is `1.1361` in vehroute, `1.14` in tripinfo and `1.1361` in both generated route files. The known serialization-precision trap is therefore excluded for the common factors.

I independently ran the targeted unit suite: **6/6 passed**. This includes fail-closed mutations for missing U identity, changed common speedFactor, missing explicit speedFactor, changed route edge definition under an unchanged route ID, and changed vType attribute under an unchanged vType ID. Static code inspection confirms comparison of full route and vType attribute maps as well as common vehicle identity/attributes, integer schedule, counts and exact treatment-only R identities. Running the checker on the v3 XML independently returned PASS with 1,558 exact common records, route definitions 4/4 and vType definitions 1/1 equal.

The v3 provenance receipt explicitly supersedes v2. The v2 package and this review's earlier FAIL finding are preserved for audit; v2 had the route/vType-definition checker gap addressed by v3. The v1 supersession notice identifies its two-decimal tripinfo speedFactor source as unsuitable. V3's report also marks v2 superseded and directs any future preparation to use the v3 inputs.

## Limitations and boundary

These findings establish **input-level** binding for identities, desired departures, route definitions, vType definitions, speedFactors and explicit departure placement. They do not ensure future insertion/arrival success or identical stochastic lane-change and traffic trajectories: adding R may still perturb simulation-time random decisions and traffic interactions. The serialized vehroute factors are the highest-precision recorded values used here; this review makes no claim about unrecorded floating-point bits. A future run would need a newly reviewed exact card with these input hashes and post-run lifecycle/pre-R trajectory checks under the adopted witness contract. No new card or run authorization is included in v3; the previous one-start authorization remains consumed.

**Data/provenance review: PASS** for the stated v3 offline matched-input repair, subject to the input-versus-future-trajectory boundary above.
