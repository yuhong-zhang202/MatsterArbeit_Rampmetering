# O2 single-run diagnostic contract — revision01, static package

## Status and authority

One new technical instrumentation reproduction only: C_STRONG, seed17, simulation [0,450), step1. The user condition is recorded verbatim in authorization_provenance.json. Existing C data omit actual selected leader and blocking cause; parent and scientific reviewer found this condition satisfied. Exact-package static review is still required. The card remains approved=false because the card is immutable; a separate parent release sidecar, bound to the final card SHA and exact PASS_STATIC_FINAL receipt, implements the already-granted conditional authorization. This is not a request for another user approval. The old TV card remains 5/5 consumed and is never read as launch authority. Formal protocol is empty/unfrozen.

No second run, retry, build, GUI, geometry/demand/model/program change, parameter search or statistical/formal conclusion is authorized. SUMO starts<=1, read-only TraCI connection<=1. Connection retries only wait for the same sole child server; they never respawn SUMO. Do not call traci.start, whose implementation may launch again. The supervisor atomically claims one fresh run root before starting the observer. Any crash, unknown reservation, timeout, nonzero, query failure or physical event consumes the attempt and ends the card.

## Minimum scope and unchanged inputs

The only target is the U35/R70/shared-divergence event around398–413, with antecedents385–397 and recovery414–430. Running from0 preserves its antecedent traffic; end450 provides limited recovery/context. No need to observe1740 in this diagnostic. The complete original demand file is byte-identical (M1333/R300/U150/X75 over0–1500); cutoff450 is deliberately censored and must NOT be interpreted as all1858 having had an opportunity to depart. Original network SHA887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca, detector geometry/settings, WAUT C_STRONG selection, urban TLS, type, seed, time step, driving/lane-changing settings and all other behavior settings are unchanged.

Only changes: new isolated input/output paths; end2700→450; native fcd-output.max-leader-distance600; single-client remote port8819; read-only observer and clock advancement. 600m is an observer lookahead covering238.80m shared lane plus317.57m reference path; it is not a capacity/calibration threshold. The API may return a farther same-lane leader; do not treat600 as a strict geometric cap.

Expected original18 XML roles remain; all time-bounded streams now end450, detector bins15×30s, each TLS450 labels. Additional raw observer.jsonl, SUMO separate stdout/stderr, child PID/version/observer receipt, supervisor reservation/receipt/manifest remain auditable. No output references an old raw directory.

## Read-only observer and verified API meaning

Installed SUMO1.26 Python sources and recursive schema bindings are in source_bindings/static receipts. Runtime getters dispatch `_getUniversal`→`_getCmd` with the GET domain command; no behavior setter, load/reload, route change, stop, speed, lane command, subscription or controller is called. Each `simulationStep()` advances exactly one original1s step; `close` ends at450. These are clock/session operations, not traffic behavior interventions. Actual observation neutrality remains a mandatory post-run comparison, not a static fact.

- Native FCD adds leaderID,leaderSpeed,leaderGap; native gap includes ego minGap (physical front-to-rear gap). No leader is represented by emptyID and -1 sentinels, not zero physical spacing.
- `vehicle.getLeader(id,600)` returns `(leaderID,gap_excluding_ego_minGap)` or None/emptyID. Record raw value and separately add actual `getMinGap` for bumper gap. It follows current best lanes and is not a full explanation of every braking constraint.
- `getJunctionFoes`: `(foeID,egoDist,foeDist,egoExitDist,foeExitDist,egoLane,foeLane,egoResponse,foeResponse)`. Empty foes does not prove absence of internal occupancy blocking, and response flags alone are not final causal attribution.
- `getNextLinks`: `(lane,via,priority,opened,foe,state,direction,length)`; preserve full tuple.
- `lane.getLinks(extended=True)`: `(approachedLane,hasPrio,isOpen,hasFoe,approachedInternal,state,direction,length)`. `isOpen` is a hypothetical speed-limit arrival test and ignores foes already within the junction. Never equate it to permission for the observed stopped vehicle.
- `getNextTLS`: `(tlsID,tlsIndex,distance,state)`; both actual TLS program/phase/state also read.
- Per observed vehicle record ID/type/route/routeIndex/lane/front lanePos/XY/angle/speed/acceleration/actual length/minGap. This preserves cross-branch body occupancy when e.g. U35front is1.52m on its Uinternal and5m body rear is still upstream. This is a route/geometry inference, not a newly queried SUMO blocker assignment. Do not remove U just because its front changes lanes/edges.

For labels385..430 inclusive record every active vehicle whose front lies on urban_in, urban TLS internal, shared_approach, both divergence internals, urban_out, ramp_storage, ramp_mid internal or ramp_accel, plus explicit U34/35/36 andR68..72 wherever active. Full IDs/gaps include missing-target lists, never fabricated zero rows. Labels0/1/2 additionally record snapshots to test alignment. Native FCD covers every label0..449. Each step records before/after simulation clock and observed collision/teleport/emergency lists plus departed/arrived IDs.

TraCI post-step clock is recorded separately from `fcd_label_candidate=before`. The data gate must compare exact vehicle fields against native FCD and archived C; no blanket assumption of event/display alignment. TLS queries may reflect a different phase-update instant than pre-step TLS output at transition labels; preserve both timestamps and verify documented alignment from actual data. No relabeling to make it appear equal.

## Execution and finite resource governance

Use only the card-bound .venv Python path with -B; supervisor starts one observer process group, observer starts exactly one headless SUMO child in the same group. Before connecting and again before any step, `/usr/sbin/lsof` must show port8819 belongs only to that child PID. A foreign listener blocks without stepping it. No version-probe SUMO launch. Version is read via getVersion on the same authorized connection. Old C output proves the bound binary reported1.26.0; runtime must agree.

180 wall seconds and200,000,000 bytes are observed stop-lines with50ms polling, not hard CPU/filesystem quotas; overshoot is possible during a polling interval and terminal receipt/manifest writes. Both SUMO and observer outputs count. No hidden retries or automatic extension. Original full2700s C took2.139209792003385s and59,992,537bytes. Added native fields and46 targeted snapshots increase traffic-neutral logging; the180s/200MB conservative ceiling is operational headroom, not measured runtime guarantee. The compiled/traffic input is never altered to fit the budget.

On confirmed collision/teleport, the observer writes physical_stop_request with IDs, source/time and immediately stops without advancing another step; supervisor terminates the group and preserves partial evidence. Primary may also write an explicit observed physical stop marker. Emergency stops are recorded independently; do not equate them to collisions. Invalid lane/connection, XML/load errors, unavailable API or malformed response, wrong program/clock/process ownership, nonzero, or any new structural anomaly stop interpretation/execution; no retry. Ordinary queues under C are the diagnostic target, not by themselves a new structural failure.

After completion, independent engineering checks child and observer group absent, exact final bytes/hash of all files, XML role completeness and clock450. Data reviewer then checks observer coverage/alignment, original-common FCD prefix equality, all time-bounded output prefixes, physical events, and explicit450 censoring. A mismatch prevents attributing new traces to archived C. Even perfect neutrality does not guarantee the logged selected leader identifies the ultimate bottleneck; internal blocking cause may remain Unknown. O2 thresholds and existing science findings are not changed by this package.

## Post-run interpretation boundaries

The package is designed to distinguish whether U35's selected leader/foes/internal-link states are compatible with direct R following, blocked internal exit, or another constraint during398–413. Combine observed antecedent R movement/meter states and cross-branch tails; do not declare meter spillback solely from one mean delay or leader ID. Keep the original strict all-stopped meter-anchored storage-cross metric unchanged pending explicit scientific review. The observer is not a causal intervention and cannot resolve all counterfactual causes from one run.

The correct next step is exact static engineering/data/scientific review of this package. This engineering task does not launch it. Parent may bind a released approval sidecar to the final card under the existing conditional user authorization after the review. No additional user confirmation is required within that scope.
