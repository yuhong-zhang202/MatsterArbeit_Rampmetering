# PAIR3199 matched-input repair — offline report

**Disposition:** `PAIR3199_MATCHED_INPUTS_REPAIRED_PRELAUNCH_NOT_AUTHORIZED` (input construction only; no launch authorization).

## Root causes established from existing evidence

1. **U/X omission:** treatment source XML lists `M_flow`, then delayed `R_flow`, then `U_flow` and `X_flow`. Because the flows are not globally ordered by departure time, SUMO 1.26.0 logged `Route file should be sorted by departure time, ignoring 'U_flow'!` and the same warning for `X_flow`. The prior treatment raw contains M/R but no U/X identities; the existing control source, ordered M/U/X, realized its planned U/X. This is a direct source-order defect, not a geometry or classifier issue.
2. **M speedFactor mismatch:** the shared `<vType id="technical_passenger" vClass="passenger"/>` does not specify a fixed per-vehicle `speedFactor`. Existing `vehroute.xml` therefore records distinct realized factors for the same M IDs: only 2/1,333 exact matches between arms. Among the 480 M vehicles with desired departure before R activation at 540 s, only 1 has an identical exact factor. That rules out the narrow explanation that only R vehicles entering after 540 consume draws and then shift later M factors; the divergence is already present in the constructed input realization. The SUMO tripinfo documentation says an individual speed factor may be drawn from a speed distribution. Same seed initializes a random stream; it does not bind random draws to vehicle identity across different route populations. The added R flow is the only intended demand-input difference and is consistent with perturbing the common random realization during flow/vehicle construction, but the precise internal draw point cannot be isolated from recorded logs without a new instrumented simulation. No such simulation was run.

   **Version-matched source check:** in SUMO tag `v1_26_0`, `MSBaseVehicle.cpp` initializes the chosen factor from `pars->speedFactor` when that value is explicit and otherwise uses the supplied `speedFactor` argument. This confirms why writing per-vehicle `speedFactor` makes the property deterministic at construction. The observed 2/1,333 mismatch is direct evidence of the unmatched realization; the available source line does not establish which RNG instance or exact draw was shifted by the new R flow. Thus “R changed the precise RNG draw order” remains a plausible mechanism, not a source-proven fact.

## Repaired binding

The immutable existing control `vehroute.xml` supplies each common M/U/X identity's realized high-precision speedFactor. Each M/U/X vehicle is materialized explicitly in both route files with its original identity, SUMO 1.26 integer-millisecond desired departure schedule, route, type, and class-specific departure position/lane/speed attributes. All pair records are globally sorted by `(depart_ms, id)`. Treatment adds exactly the planned R192 identities scheduled at 5,000 ms offsets from 540,000 through 1,495,000 ms; R factors are materialized from the existing treatment `vehroute.xml` solely to make the added records explicit. No prior treatment outcome is analyzed here.

The pair invariant checker fails closed on count/ID differences, departure mismatch, route/type mismatch, missing or invalid speedFactor, any exact speedFactor mismatch, departures outside the integer schedule, extra non-R treatment identities, missing R identities, or route-file ordering. The inputs preserve qMain=3199.2, R=192 at [540,1500), geometry, routes, vehicle type, seed and other approved pair conditions. The control is not reclassified as a clean baseline. No exact run card, runtime config, launch command, or authorization is created by this package.

## Static verification

| Invariant | Result |
|---|---:|
| Control M/U/X counts | 1,333 / 150 / 75 |
| Treatment M/U/X/R counts | 1,333 / 150 / 75 / 192 |
| Common identity matches | 1,558 / 1,558 |
| Desired depart schedule matches | 1,558 / 1,558 |
| Route and type matches | 1,558 / 1,558 |
| Exact high-precision speedFactor matches | 1,558 / 1,558 |
| Complete common-vehicle record matches | 1,558 / 1,558 |
| Treatment-only identities | exactly R_flow.0–R_flow.191 |
| Checker mutation tests | 4/4 PASS |
| SUMO / TraCI / netconvert starts | 0 / 0 / 0 |

These are input-construction checks. They cannot establish future insertion success, realized trajectories, or treatment outcomes. Any future use requires separate card preparation and fresh prelaunch review/authorization. The prior single-start treatment authorization is consumed and remains consumed.

## Provenance

See `COMMON_DEMAND_MANIFEST.json`, `INVARIANT_CHECK_REPORT.json`, and `PROVENANCE_RECEIPT.json`. Source raw files remain immutable. This repair does not alter the adopted exploratory witness contract or formal experiment protocol.

The directly verified tagged source is [MSBaseVehicle.cpp at v1_26_0](https://github.com/eclipse-sumo/sumo/blob/v1_26_0/src/microsim/MSBaseVehicle.cpp); the local SUMO tripinfo documentation is `literature/core_reading/sumo_docs/TripInfo.html`. The online [SUMO speed-distribution manual](https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#speed-distributions) explains the per-vehicle sampled attribute, but is not treated here as tag-pinned source evidence.
