# Targeted validation engineering contract — immutable revision01

Status: engineering package only; final exact-card scientific static review is required. No SUMO has been started by this package. `EXPERIMENT_PROTOCOL.md` is empty, so these are technical/exploratory runs, never formal thesis runs. Prior RV4 five starts remain exhausted and separate.

## Fixed design and program selection

All five planned starts share the exact newly compiled network. Only ramp_mid changed from a priority node to a traffic-light node; the unique controlled link is ramp_storage_0 → ramp_accel_0 via :ramp_mid_0_0, linkIndex=0. Urban TLS and all lane shapes/lengths/permissions, merge requests and connections are unchanged. Runtime selection uses native WAUT `startProg` at time zero, no switches. No TraCI, controller, speed/stop/lane command, GUI, or additional build is permitted by the runtime card.

- A_OPEN: one 60 s G phase repeated (continuous G).
- B_MODERATE: 22 G / 3 y / 35 r, offset0.
- C_STRONG: 12 G / 3 y / 45 r, offset0.

These are **timing allocation tiers**, not calibrated discharge rates. Yellow is SUMO's normal braking/pass behavior, not zero discharge. Selected program remains unchanged through2700. WAUT selection is documented officially and accepted by local1.26 XSD; actual selected program and phase are still a smoke gate.

M/R/U/X counts1333/300/150/75; demand0–1500; step1; duration0–2700; seed17. The nominal M3200 label represents number-flow1333/1500s=3199.2veh/h. Routes, vehicle class, default Krauss/lane-change parameters, source insertion and Mpos100 are byte-equivalent to old R720 demand. All detector settings remain unchanged, including native E2 thresholds. `changeRight=authority` on merge_section_1 also affects already merged passenger R; preserved, not newly introduced.

## Finite run sequence and executable releases

1. TV_SMOKE_B_LC_ON_S17_attempt1: full-length B native lanechange output ON, technical.
2. TV_SMOKE_B_LC_OFF_S17_attempt1: identical B native output OFF, technical, after first full14 gates.
3. TV_A_S17_attempt1: only after both fixtures full14 gates plus logger neutrality PASS.
4. TV_B_S17_attempt1: only after A full14 gates.
5. TV_C_S17_attempt1: only after B full14 gates.

The smoke pair is not two independent scientific replications. Runtime executable allows only these IDs, no automatic retry. Any technical failure blocks this card; continuing pure technical troubleshooting requires preserved evidence, a new immutable package/attempt identity and parent/scientific review under the standing user task. No silent budget reset or behavior change. Structural/physical failure stops the task.

Runtime approval must cite the attached user task and exact card hash; it must not falsely assert that the user personally approved a later-generated hash. The approval contains a bound final reviewer receipt with status PASS_STATIC_FINAL, stage exact_runtime_package and matching card SHA. A design-only/old/nonpass receipt fails closed. Approval template is not approval. No sidecar is supplied as approved in Phase1.

## Output and technical gates

ON runs: 18 XML roles (old17 plus lanechanges.xml). OFF fixture: explicitly17, lanechanges.xml must be absent. Both log files and execution receipts/manifests retained. Native `SaveTLSStates` omits source to log **both urban_tls and ramp_mid** into tls_states.xml:2700 records each,5400 total. TLS state at integer t must match selected program and offset; phases follow registered60s cycle. Detector files each90 continuous30s bins. FCD/queue/summary have2700 labels0..2699. Legal empty detector flow or lanechange event set must not be rejected.

The 14 hard technical check IDs are in gate_contract.json. All must PASS, physical_status=suitable, progression_allowed=true. Gate must bind exact card/attempt/receipt/output manifest and analysis implementation; wrapper rechecks each raw-file hash. Never collapse unknown/missing records to zeros. Collision/teleport makes comparison unsuitable even if complete. During execution the primary observes logs; upon explicit collision/teleport it writes the supported physical_stop_request.json with event/source/time/excerpt and wrapper terminates group, retains partial_evidence_physical and consumes the start. If first discovered after completion, classify complete_evidence_but_comparison_unsuitable_physical_event and block progression. No unverified log pattern is used as automatic scientific detection. Emergency braking is counted separately, not automatically structural failure. Invalid lane/connection, detector/TLS load errors, incomplete identity accounting and missing roles are hard technical failures.

Logger neutrality compares the17 non-LC XML semantic digests in document event order. XML comments (including generated dates/config paths), formatting whitespace and `summary/step@duration` **computational wallclock** are excluded. No traffic duration, tripinfo time, position, speed, IDs, TLS state, interval or detector value is excluded. Each role must match exactly; comparison is rerun in preflight for every primary run. Mismatches block primary science. Native LC does not add temporal substeps; lane changes are discrete simulation events, not continuous-time empirical trajectories.

## Measurement boundary contract

All FCD timestamps have1s resolution. Stop tag speed<0.1m/s, no persistence filter. R route coordinate starts at the shared_approach downstream endpoint. Internal :urban_diverge_1_0 is113.08m, ramp_storage_0 is204.49m; their sum to meter stopline is317.57m. This is a geometric reference, not calibrated storage capacity. The81.98m :ramp_mid_0_0 internal lane is **downstream** of the stopline.

Meter anchor: stopped R front bumper at most10m upstream of stopline. No anchor means no meter-connected queue; distant stopped R is separately unanchored/junction_blocking_candidate. Add adjacent stopped vehicles only with actual bumper gap≤10m, retaining intervening U. Record IDs, class, lane, front/back position, length, gap, and anchor distance. This10m threshold is descriptive, borrowed from existing E2 jamThreshold, not capacity/significance calibration. Do not delete a moving U and join R across it. Negative bumper gap triggers investigation.

Vehicle length: all input flow types resolve to the sole technical_passenger vClass=passenger with no length overrides. Official SUMO v1_26_0 source is archived with URL+SHA in references: SUMOVTypeParameter.cpp takes VClassDefaultValues length, which invokes getDefaultVehicleLength; SUMOVehicleClass.cpp passenger follows default5m. Official Vehicle_Type_Parameter_Defaults documentation agrees. This is the **SUMO software default**, not empirically calibrated or a runtime TraCI measurement. The downloaded version-tag source is not claimed as the installed binary's reproducible build source. Gate must verify no vType/per-vehicle override and every observed type matches before using5m; otherwise stop measurement rather than guess.

Record first nonempty queue, every frame count/length change, contiguous episodes and observed duration; single-frame presence is not sustained. `storage_cross_observed` requires a stopped R directly observed on shared_approach in the meter-connected component. `shared_obstruction_potential` describes that same component's spatial/duration footprint: these are not independent sequential events. A large internal gap can only support junction_blocking_candidate. U_blocking_candidate requires stopped U on shared lane linked through the actual front-vehicle chain to an R ahead, retaining all intervening identities and TLS states. U_additional_impact additionally requires aligned A/B/C whole planned U-cohort waiting/time comparisons and linked events; single stop or mean change is insufficient.

A stopline crossing is bracketed between consecutive FCD positions before/on and after stopline; internal lane coordinate must be retained. Exact boundary equality adds ambiguity. Missing internal samples may permit topology-inferred crossing bracket, never fabricated exact position. Event timestamps use adjacent1s bounds; overlapping bounds mean temporal_order_unidentified. Undeparted and unfinished are distinct and kept. Missing tripinfo identity is an evidence error because write-undeparted is enabled, not evidence of external backlog. E2 metrics remain separate under native thresholds.

`measurement_helpers.py` supplies deterministic primitives and boundary fixtures. Full streaming analysis, episode tables, U counterfactuals and O1/O2 adjudication require the separate data/scientific implementation and are not claimed complete by these unit fixtures.

## Resource and retry governance

Each start:180s and1.5GB observed output stop-lines; whole initial card5 starts/900s/7.5GB. Polling50ms with possible overshoot; no hard filesystem quota claimed. Baseline RV4 successful R720 took1.122s and25.04MB, but metering can extend residence. Conservative sizing:1858×2700=5,016,600 possible vehicle-frames ×200bytes≈1.003GB, plus remaining XML/log/event overhead;1.5GB is an operational ceiling, not proof of worst-case guarantee.180s gives substantial headroom relative to old run and prior successful11.653s compiler startup. Unknown anomalous output growth terminates at the monitor. Reservations consume attempts before child spawn; crashes/orphans/nonzero/timeouts preserve traces and cannot auto-resume/retry. No source science change is justified by hitting a resource bound.

A single follow-up family is registered but **not executable under this card**. If all O1+O2 gates pass under scientific review, exactly A/B/Cseed23 may receive a new reviewed card. Otherwise diagnose, choose at most one demand OR timing family with concrete values and parent/scientific review before new starts. Never both, no second family, no third seed, no search. Technical troubleshooting attempts remain identified separately and cannot increase scientific replication counts.

## Sources

- https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#defining_program_switch_times_and_procedure (WAUT startProg).
- https://sumo.dlr.de/docs/Simulation/Output/Traffic_Lights.html (source omitted logs all TLS).
- https://sumo.dlr.de/docs/Simulation/Output/Lanechange.html (native events).
- https://sumo.dlr.de/docs/Simulation/Output/FCDOutput.html (front bumper, position and step timing).
- https://sumo.dlr.de/docs/Vehicle_Type_Parameter_Defaults.html (passenger5m).
- Installed1.26 additional_file.xsd and types/sumoConfigurationType.xsd, bound in manifest.
