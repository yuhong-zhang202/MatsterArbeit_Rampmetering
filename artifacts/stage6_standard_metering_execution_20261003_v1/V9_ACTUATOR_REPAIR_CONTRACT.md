# V9 actuator repair: exact-card review contract

Status: prepared technical validation, no V9 SUMO start. The V8 S17 controlled run remains an exploratory actuator pilot with 10 emergency-braking and 8 red-light emergency-stop warnings. Its experiment-start accounting is unchanged.

## Scope and purpose

- Run ID: `M3600_R900_S17_ALINEA_TRACI_V9`.
- Card SHA-256: `086e5812e409125db9ebe509a51932b4c65c39a6b9d2ee27008f55034eb61507`.
- Purpose: `TECHNICAL_ACTUATOR_REPAIR_VALIDATION`. Under D-016, a launch increments physical and technical starts, not experiment starts. This classification is fixed in the card before a launch; the V8 S17 controlled experiment remains charged.
- The SUMO binary, network, demand, seed 17, vehicle types, occupancy event ledger, ALINEA target 11%, gain 70 veh/h per percentage point, rate limits 300–1200 veh/h, 30 s feedback schedule, one-second green, and at least two red seconds remain unchanged. Actual green timing and realized release rate can change because unsafe nominal slots are held red.

## Prospective one-second guard

At each interval `[t,t+1)`, feedback adds `rate/3600` credit. A nominal green is due if credit is at least one and the last actual green was at least three seconds earlier. The guard permits that green only if the true front of `ramp_storage_0` is within 1.1 m of the stopline, moves below 0.1 m/s, the receiving internal lane meets the existing front-length-plus-minGap clearance, and every other vehicle on storage has sufficient distance to the stopline.

For each follower, type-specific `a = TraCI vehicletype.getAccel` and `b = getDecel` must be finite and positive. `getTau` and `getActionStepLength` must both equal the simulation's one-second step; otherwise the run fails before using the guard. With current speed `v`, one-second step `dt=1`, and remaining stopline distance `d`, require

`d >= 1.1 m + (v+a*dt)*dt + (v+a*dt)^2/(2*b)`.

The first term is a fixed geometry margin; the next terms conservatively allow a full Euler step of acceleration followed by braking at the type's normal deceleration. This engineering bound does not replicate SUMO's full car-following or prove safety. A denied nominal slot stays red and retains no more than one credit; further accrual is recorded as dropped credit. There is no burst catch-up. A permitted slot spends one credit and commands G for one second.

## Audit layers

`controller_steps.csv` retains prior columns and adds `nominal_slot_scheduled`, `guard_allowed`, `guard_reason`, `guard_rejected_slot`, `credit_deferred`, `guard_vehicle_states_json`, and `guard_failed_follower_ids_json`. The vehicle JSON contains ID, position, speed, type, type acceleration/deceleration, stopline gap, required gap, and pass/fail for every vehicle on storage. `slot_scheduled` denotes the actual G command; `requested_state`, `observed_state`, and `crossing_bracket_ids_json` remain available. `service_windows.csv` adds `nominal_slots` and `guard_rejected_slots` and retains actual `scheduled_slots` and unique front-crossing counts. All controller rates, feedback input windows, clipping, and dropped credit must be reported, including any large service deficit.

## Existing-data evidence and limits

Read-only replay of all 781 V8 S17 nominal G instants against its FCD pre-step states found 553 without an already qualified stopped front and 228 with one. All ten braking warnings followed a green at a front gap of 15.20–33.86 m, in the unqualified group. With provisional `a=2.6 m/s²` and `b=4.5 m/s²`, the V9 Euler follower check would admit 210 of the 228 qualified V8 opportunities and reject 18. The provisional dynamics values are not a substitute for V9's actual TraCI type readings. Changed pulse timing will alter trajectories, so 210 is not a predicted V9 service count or a performance claim.

## Verification before release

- Pure/mock unit tests: 23 passed; `py_compile`: passed. No V9 SUMO/TraCI session has started.
- Static preflight: `STATIC_PREFLIGHT_PASS_NO_SIMULATION` for the exact card above.
- V9 `runner.py` SHA-256: `12a276f44b8a92e1a29c35899848c557c9e90a0580147e7e419c57a2e34baffc`; `control.py`: `a282302ecc5fefd8d1810c07d1340f9bd1dbe0e3316b718ce991e5c5bea185ab`; tests: `3deb8c2d92f9fb31659978a4685b65fa259bb8e4b25ca31e491ec00286bfd75c`.
- One S17 technical launch requires independent exact-card scientific review and release. The existing 120 s wall, 250 MB run-output, shared 8 GB raw limits and immutable output directory still apply. Its warnings, actual release counts, guard rejections, rate tracking, traffic outcomes, and 238 lane-window occupancy checks must be reviewed before any further seed.
