# Independent actual-data review: CA_FIXED_R300_S17_A07

Disposition: **NOT_QUALIFIED_SAFETY_GUARD_STOP**. The observed prefix is independently reconciled through1206s. The intended4200s horizon was not completed. No fixed rate is yet safely qualified;450/600/750/900 remain unrun/held, and PhaseC remains unprepared/held. This is exploratory engineering evidence; formal protocol remains0B/unfrozen and Stage6 closure is unchanged.

## Context and input authority

Context reviewed: AGENTS.md, PROJECT_STATE.md, DECISIONS.md, WORKLOG.md, empty EXPERIMENT_PROTOCOL.md, Issue4 snapshot/AUTHORIZATION, phase/rate contract, actual source snapshots, exact A07 release/card, prior measurement and A04/A05 failure audits. PROJECT_STATE still described A07 awaiting review/release when this audit began; the exact release, guardian and execution ledger establish the newer actual attempt. No project-state inference was taken from memory.

The final data gate is `R300_A07_ACTUAL_DATA_GATE_V2.json`; V2 supersedes the preserved initial `R300_A07_ACTUAL_DATA_GATE.json` by adding full native program/next-switch and per-step acceleration/guard verification. Both have the same observed outcome. Reproduce with `python3 data/processed/candidate_a_qualification_20261008_v1/audit_r300_a07_actual.py`. The script uses standard library only and never starts SUMO or imports the actor.

Authoritative raw directory: `data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07/`. All45 guardian manifest entries and inventory identities were independently hash-verified, including source, input and network snapshots; all67 protected baseline hashes match. Card SHA256 is69fa8d4584b8b52868efd68eb9fc4d5153dc92fd29811be9aaf3a4724b95412d. Guardian receipt agrees exactly with the single A07 execution-ledger entry and the exact release hash. Child SUMO_HOME/schema hashes and `xml-validation=always` are preserved.

## Observed motion, phase and crossings

CSV/FCD/TLS/native summary independently cover1206 consecutive completed steps. FCD and TLS labels are0..1205, while API completed times are1..1206: API pre(t) corresponds to FCD(t−1), and post(t+1) corresponds to FCD(t). This was verified against21170 storage/ingress observations, every crossing and the terminal snapshot; it was not assumed from code.

Motion follows G[0,600), y[600,603), r[603,1200), G[1200,1203), y[1203,1206). Native nextSwitch, actual program/phase, all7 logged API requests and their boundary times match the snapshotted programs. At1203, the pre getter still showsG/nextSwitch1203 while the actual motion and post getter showy. At1206, y/nextSwitch1206 predictsr, but that next motion step is not executed. Thus the observed phase prefix is consistent; a full qualification cycle is not verified.

Independent FCD storage→internal reconstruction finds exactly one unique crossing: R_flow.0, API bracket(1200,1201], FCD entry label1200, G. Yellow/red crossings and duplicate/missed observed crossings are0. PRECONTROL and EXTERNAL_HOLD each have600 steps, C=E=0 and actual N=0. The nominal packetn=2 remains unqualified.

## Safety stop and accounting boundary

The failure snapshot checks all42 remaining (27 storage and15 ingress) storage/ingress vehicles before prospective red. The independently recomputed sole failed witness is R_flow.1: position203.488000810m, positive speed0.0457382295m/s, remaining gap1.001999190m. The locked rule1.1+v+v²/(2×4.5) requires1.145970672m, giving margin−0.143971483m. FCD at1205 independently confirms pos203.49/speed0.05; even its most favourable rounding interval leaves a negative margin. No speed shortcut, new margin or hypothetical failed motion was substituted.

Native summaries contain0 collisions/teleports throughout; native logs contain no emergency braking/stop warning. All17 red self-loop startup warnings are retained separately; guardian stderr also preserves the inherited floating-point simulationStep API UserWarning. All recorded normal acceleration bounds pass, including independent FCD speed-difference checks within output rounding. These facts do not qualify the stopped run or prove safety of the unexecuted transition.

The sole planned cycle[1200,1224) is unfinished. At actual stop, C=C_applied=0.5 vehicle-equivalents, E=0 and N=1; E is due at the planned cycle end, so no partial packet is prepaid. Separate terms are C−C_applied=0, C_applied−E=0.5, E−N=−1, summing to C−N=−0.5. The negative E−N is an unfinished-boundary term; it proves neither complete-cycle overservice nor a physical service deficit. Actual complete-cycle discharge distribution is unavailable.

All six original300s service windows are retained. The first has only6/300 observed steps; the other five have0/300. Every window is `NOT_TESTED_INCOMPLETE_WINDOW`, with tracking error blank/null. Zero observed sums in windows with no recorded steps denote the empty observed subset, not an estimate or replacement of the missing window. No full-window supply assertion, zero-filled result,6s qualification error or rate-capacity estimate is made.

## Lifecycle, outputs and limitations

All4050 scheduled input IDs are classified without exclusion:1467 inserted,1267 arrived,200 in-network unfinished at1206s,73 due source backlog and2510 future scheduled/not yet due. Tripinfo has1541 rows, including74 undeparted (73due plus one future M at1206); the native incremental loaded count1542 is not the whole input cohort. Native final inserted/running/arrived and FCD/vehroute/tripinfo identities reconcile. No unfinished observations are converted to arrivals; no costs or traffic effects are analysed.

Derived outputs under `results/tables/candidate_a_qualification_20261008_v1/`: SERVICE_WINDOWS(6 rows), PHASE_LEDGER_THIN(1206), CROSSINGS_RECONSTRUCTED(1), CYCLES(1 unfinished), PRE_RED_WITNESSES(42), LIFECYCLE_COUNTS(4), LIFECYCLE_IDS(4050), NATIVE_WARNINGS(17), each prefixed `R300_A07_`. Sources, filters, time mapping and transformations are implemented in the audit script; the V2 JSON binds the full raw manifest. Known examples validate the red envelope, inclusive10% reference, failed/incomplete/insufficient-supply windows.

Remaining limitations: no complete cycle/window or4200s coverage; one development seed; no independent recalculation of SUMO's logged secureGap API value. Receiver front/leader identities, nonnegative secureGap and available state are checked; no denied start occurs in this observed prefix. These limitations cannot support a300/900 capacity conclusion, unavoidable collision, sweet spot, formal effect or changed research scope.

Safest next step: hold every further launch. Engineering diagnosis and independent scientific review must classify whether the locked contract permits a genuine minimal technical repair or requires stopping the Issue scope. This data review authorizes no repair/retry. Parent should minimally update PROJECT_STATE/WORKLOG with the actual early stop; analyst write restrictions prohibit governance edits. Raw, source, configuration, metrics and tolerance remain unchanged by this audit.
