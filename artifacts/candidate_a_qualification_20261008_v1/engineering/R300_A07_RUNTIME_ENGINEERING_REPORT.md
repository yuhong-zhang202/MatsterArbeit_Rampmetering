# R300 A07 runtime engineering diagnostic

Disposition: **STOP_EXPANSION_PENDING_INDEPENDENT_DATA_AND_SCIENCE**. This is an aborted technical qualification attempt, not a qualified rate, traffic-effect result or formal experiment. No retry or source change is proposed here.

## Execution and preserved evidence

Exact command: `.venv/bin/python scripts/candidate_a_qualification_20261008_v1/runner.py --launch config/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07/card.json --release artifacts/candidate_a_qualification_20261008_v1/RELEASE_FIXED_R300_A07.json`. Executed once through `require_escalated` for the authorized local TraCI socket. The release binds A05 failure and A07 repair evidence. Guardian exit1, no budget trigger,32.412148542 s and10,797,838 payload bytes. TraCI connected on attempt221 after23.197924250 s. The restored installed-schema environment enabled motion.

Raw directory: `data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07/outputs/`. Raw receipts, startup context, native logs, XML/FCD, five CSVs, source/input/card snapshots and failure snapshot are preserved. The guardian manifest verifies all45 files; all67 protected baseline hashes still match. Execution ledger now has A04/A05/A07:3 actual SUMO starts,0 effective qualifications. Earlier failed raw is untouched.

## Actual phase and service observations

Completed/accounted prefix is exactly1206 one-second steps; there is no unaccounted advanced interval. Recorded native post-step state matches predicted motion state on every step. Phase/API evidence is complete for this prefix: initialization A_OPEN/phase0; at600 CA_C8/phase1; at1200 CA_C24/phase2/phase0. All7 calls returned successfully. No phase API call or simulation step was issued at the refused1206 red boundary.

Precontrol `[0,600)` has600G steps, no storage supply/crossing. Common external hold `[600,1200)` has3y+597r steps,563 supplied storage observations and0 crossings. First candidate cycle starts1200, planned period24 s, nominal n2, receiver available; observed `[1200,1206)` contains3G+3y and1 actual crossing (`R_flow.0`, bracket `(1200,1201]`, G). Yellow/red crossings0; unique ID check passes. The cycle never reaches its planned end1224, so actual two-car discharge and the complete candidate G/y/r cycle remain unverified.

At stop C=C_applied0.5 vehicle-equivalents, E0 and N1. C−E0.5 and E−N−1 close exactly under the registered convention that E adds2 only at a completed planned cycle end. E0 is an unfinished-cycle boundary outcome; it is not evidence of sustained excess delivery. The first300 s service window has only6 recorded supplied steps; the other five have0. All six are NOT_TESTED_INCOMPLETE_WINDOW with no relative tracking-error result. No full service qualification or highest safe achieved rate is established.

## Safety refusal and smallest defensible diagnosis

Worker status `ABORTED_SAFETY_BEFORE_RED`; decision time and last completed step1206. Getter still reports yellow phase1 with nextSwitch1206, predicting native red before the next motion step. The existing guard checks27 storage and15 ingress vehicles. Direct offline replay of saved full-precision states using the unchanged safety helper reproduces the entire saved guard result exactly.

Only `R_flow.1` fails: storage position203.4880008102335 m, stopline204.49 m, gap1.001999189766508 m, speed0.04573822948686786 m/s, normal deceleration4.5 m/s². The registered positive-speed requirement `1.1 + v + v²/(2*4.5)` gives1.1459706723353782 m and margin−0.14397148256887027 m. It is a creeping remaining front, not an omitted ingress identity. Receiver remains available. Exact-zero exemption does not apply. The worker therefore refuses to advance1206→1207 as specified.

This witness is a failure of the prospective guard, not an observed collision or measured emergency stop. Native log contains17 explicitly retained red-self-loop initialization warnings and no collision/teleport/emergency-braking/emergency-stop entry. Minimum recorded monitored speed delta is−4.5 m/s over1 s. The inherited `simulationStep` floating-point API UserWarning is retained in guardian stderr. None of these absence observations proves the refused red transition safe.

No evidence of a callback/schema/interface, phase timing, missing state or accounting implementation defect was found in this bounded diagnostic. Changing a positive-speed exemption, the1.1 m guard margin, green/yellow duration or nominal packet to continue would change the reviewed contract. This report does not authorize such a change or infer that a safe900 service envelope is impossible. Independent data validation and scientific review must determine whether an admissible minimal repair exists or the Issue safety/capability STOP requires delivery of the current negative qualification evidence. Remaining rates and Phase C remain held.

## Verification and documentation impact

New verification was limited to reading the new raw, exact manifest/protected hashes, prefix sequence/phase/API/crossing checks and replaying the failure witness. All those checks pass. The launched technical qualification fails at the prescribed safety guard; full service and transition qualification were not run. Existing offline tests, neutral/environment tests were not repeated. No production source/configuration, dependency, model, protocol or parameter changed. Only this engineering report and `R300_A07_RUNTIME_ENGINEERING_DIAGNOSTIC.json` were added beyond runner-generated new raw/reservation/ledger.

Documentation impact: root should record the new3-start/0-effective checkpoint, first dynamic safety refusal and held continuation in PROJECT_STATE/WORKLOG. This specialist does not edit governance documents.
