# Isolated native-phase smoke proposal — review before implementation

Status: Proposed / preparation-only. No execution authorization. Baseline49d7c4a426e827342dd34be38d1f3ce2b397f8b0; old A1 remains unresolved and current-contract STOP3 stays historical. This is a diagnostic alternative profile, not a proved A1 gate or a qualified rate.

## Minimal seam

Protected worker.run is coupled to launch, a4200step loop and the custom prospective-red envelope. A new flag on that worker would change protected execution behavior. Instead introduce one isolated, connection-injected step adapter that reuses protected CycleLedger, PhaseEnvelope, motion_phase, crossing_records and red_transition_witness, and accepts the unchanged protected observe function via an explicit callback. No full runner, monkeypatch, global guard setting or native launcher is introduced. A separate CLI prints the proposed plan only and rejects launch flags. Runtime launch remains unavailable; after user approval a narrowly scoped launch bridge/package would still need to be implemented and reviewed.

The old one-reaction-step/1.1m/braking envelope is recorded as SHADOW_ADVISORY only in this new profile. All type/time/phase/state/mode/geometry/route/population/receiver checks remain mandatory. Missing identity or state never counts as a safe transition. The new profile tests native handling; it cannot establish prospective joint safety from post-step monitoring.

## Proposed single smoke

Run ID `CA_NATIVE_PHASE_R300_S17_SMOKE01` (new, never reuse A07); demand M3600/R900,U360/X180, seed17, step1s, same protected network/vehicle model. Service command300veh/h, nominal packet assumption2, cycle24s, G3/y3/r18. No timing retuning. Match old initialization: A_OPEN until600, hold introduced through native yellow then self-loop red, release at1200. Select the official static program with setProgram and green phase; subsequent yellow→red occurs through its native scheduled events, never setRedYellowGreenState or immediate forced red. Keep existing initialization requests separately visible, including old red-phase setup only at already-red cycle boundary; reviewed actual packet is advisory, actual N is measured.

First mandatory hold gate after the first **activated** yellow→red interval `(1206,1207]`: reconcile all-color crossing, phase identity, whole-world surviving-vehicle speed changes, collision/teleport/emergency log and receiver state. If any violation or unknown coverage, terminate. Even if observationally clean, stop for user/independent review before continuing. Maximum proposed second-stage continuation ends1272, at most three24s cycles including the first; each next green requires a valid receiver and native red boundary. No automatic continuation. A precontrol native yellow→red at603 also needs the same diagnostic record and post-step mandatory monitors; activated gate does not exempt initialization.

At1272 stop **before starting the next cycle** and write completed/partial accounting; never claim a300s service window or rate qualification from72s. Termination may occur earlier. Data must distinguish partial observation, observed zero and absent observation.

## Coverage and stop monitors

Use protected observe for storage/ingress/internal/receiver schema and local secure-gap checks; add a whole visible-ID inventory with actual routes/type/modes and current speed for all M/R/U/X. All vehicles that could enter the controlled storage/internal paths must be mapped, including loaded/pending IDs and the preceding shared approach; bound excluded entrants using protected geometry/step/speed premises. Unknown population/route/type/mode, coverage overlap or a nonfinite observation denies the step. A receiver denial must never start green.

Post-step: phase equals predicted native motion, count every internal entry under G/y/r, no duplicate/uncovered/red crossing; collision/teleport/native emergency-warning checks; normal-deceleration bound4.5m/s² across all surviving observed IDs (not merely the front vehicle). Missing/new/disappeared IDs require explicit departure/arrival attribution; monitor completeness is not assumed. Native emergency warnings/ordinary-deceleration violations stop the smoke. Writes are append-only to a new planned package/output directory, allocated only after explicit approval.

## Limits needing review

Three-second yellow is inherited, not certified adequate. Data review must inspect speed/gap at **yellow onset**, not only the tiny speed at its last second; stopping estimates are conditional engineering screens, not native safety proof. No new margin/speed model or relaxed criterion may be invented. Native green/yellow/red handling does not automatically certify that ordinary deceleration bound will be respected. Whole-world inventory, current route exclusions and post-speed diagnostics do not resolve all joint dynamic proof obligations.

Offline fake-connection tests can establish dispatch/accounting and mandatory stops only. No SUMO/traci imports, launches or raw allocation. No throughput/sweet-spot/freeway result claim. If reviewers cannot justify a minimal observational smoke, do not add increasingly complex proof logic; report the blocking concern.
