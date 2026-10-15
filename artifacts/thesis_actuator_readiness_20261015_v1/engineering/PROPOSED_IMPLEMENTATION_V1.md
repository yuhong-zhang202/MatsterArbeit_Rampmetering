# Reusable ALINEA actuator: bounded engineering design

Status: PROPOSED_FOR_DATA_AND_SCIENTIFIC_REVIEW. Read-only investigation; no implementation, card, release or SUMO start in this task.

## Context and objective

Context Preflight repeated against AGENTS.md, current PROJECT_STATE.md/DECISIONS.md, recent WORKLOG.md, empty/unfrozen EXPERIMENT_PROTOCOL.md and USER_AUTHORITY.md. The user's new task requires ordinary natural-supply operation and supersedes the preceding finite-only delivery objective. The old finite seam remains a valid historical diagnostic artifact; it is insufficient for this new goal. Stage6 closeout, A1 UNRESOLVED, overall NOT_QUALIFIED and the absence of a frozen formal protocol remain unchanged.

Working ownership is read-only code inspection and this engineering artifact only. Existing unrelated WORKLOG, memory and authorization/release modifications are preserved. Root owns current state/publication/literature; independent data and science reviews follow this proposed design. No research question, ALINEA core formula, vehicle model, network, natural demand or formal setting is selected or changed here.

## Defect and smallest useful correction

The 154-source policy uses actual C-N both to select the next period and to demand N=2 for every completed packet. Its native loop prepares a new packet before admission, and cannot continue an ordinary empty/one-car or receiver-denied interval. The recent finite seam corrects attribution and limits use, but still stops instead of operating under those conditions.

Recommend retaining the two-car nominal packet and unchanged period catalogue8..24/G/Y/red parameters, while selecting the period from C-E_scheduled. N remains a measurement, never an input to catch-up. This restores the existing project's original distinction: `src/candidate_a_qualification_20261008/actor.py` explicitly states that E counts nominal packets at planned cycle ends independently of denied starts and supports executed=False/all-red motion. This is a smaller change than a new physical-debt recovery or anti-windup controller, and leaves the project's own-previous clipped ALINEA update unchanged.

At a complete nominal boundary, let D=C_raw-E_scheduled. Choose the existing period T that minimizes abs(D+r_current*T/3600-2), with the existing tie rule. This is a local engineering translation choice, not a theorem supplied by a paper. Do not call C-E a physical service error, do not claim it becomes zero every cycle, and do not promise correction beyond the900veh/h catalogue cap. Dynamic requests can incur visible cycle latency; that is not a reason to exceed the catalogue or force vehicles.

## Transparent ledgers and command application

- C_raw: exact integral of the original held ALINEA request from activation, including blocked or empty intervals. Never reset/rebase it after a shortfall.
- E_scheduled_nominal: two assumed vehicles at each completed planned packet, including packets wholly withheld by the receiver gate. It is a schedule count, not offered or delivered service.
- E_executed_nominal: two at the end of a completed packet whose initial green was genuinely ACK-bound. It is also a nominal count, not N.
- N_actual: all independently bound front-entry IDs on actual G/y/r intervals; no fabricated entries and no unobserved values replaced with zero.
- C_selected: the selected nominal7200/T integral, including withheld nominal packets if retained for decomposition.
- C_applied: the nominal7200/T integral only for genuinely ACK-applied executed packets; zero for a completely withheld red packet. It is neither N nor the original request held after delayed application. Name and definition must be explicit in every output.

Always retain C_raw-N=(C_raw-E_scheduled_nominal)+(E_scheduled_nominal-N). Further separate scheduled-minus-executed nominal opportunity and executed nominal-minus-N; neither term alone proves the physical cause. Pending request IDs, superseded requests, selection/preparation timestamps, real first-G ACK application and partial cycles remain explicit. A red hold records the selected request as withheld/not applied; it must not falsely mark a green application. A request that is superseded while held retains its missing application.

Under this design, a long N=0 interval increases E_scheduled-N but does not increase the selector's catch-up signal. Once supply or receiving recovers, the scheduler resumes the current ALINEA rate and ordinary quantization residual; it does not recover missed physical service. No new cumulative offset or debt forgiveness is needed.

## Natural shortage and receiver-limited execution

Supply0/1, distant/late vehicles and ordinary start-up/following are observed conditions. They must not stop a completed packet or be automatically called actuator faults. Log storage/ingress IDs, positions, speeds, crossing brackets, original receiver observations and native following decisions. Report known witnesses and leave unresolved causal attribution explicit. In particular, a frame with two storage vehicles does not prove two deliverable vehicles within a green.

For a normally executed packet, retain existing quota-driven early green closure and the unchanged maximum green, yellow and red durations. An actual N<2 at the complete end records a service deficit and continues. No virtual second crossing is inserted. Existing current-following WAIT may continue during G only under its existing bound native-query decision; actual gap-floor failures, missing inputs or unsafe states still stop.

At a later complete cycle boundary, the signal is already in fully cleared red. Evaluate the existing strict fresh receiving gate before selecting any green program. If the gate returns a valid known receiving limitation, keep this nominal packet all-red by extending the actual current red before simulationStep can switch. Bind duration, actual program/phase/state/nextSwitch and the absence of a green setter/ACK. E_scheduled still advances at that nominal end, E_executed and C_applied do not. Re-evaluate at the next ordinary boundary; this may add at most the selected packet duration before recovery is reconsidered, which must be measured and reported. It avoids a new asynchronous release or complex state machine. Unknown receiver data remains STOP, not WAIT.

For withheld packets the ledger and adapter must explicitly accept all-red actual motion and skip assumptions requiring an initial G ACK or a yellow phase that was never executed. They must retain world identity, arrivals, safety, signal-clock, warning, body-clearance, crossing and EOF checks. There can be no new front entry on a held red; already-entered vehicle tails are a separate observation. The actual signal program can remain the preceding program while held; do not claim the selected new program was applied.

N>2 is not sufficient by itself to prove a collision or red entry. The new work's minimum target is removing the N<2 fault assumption. The final design review must state whether the existing conservative overquota stop remains for this qualification or whether legal G/y excess is a recorded service deviation; this is not silently changed here. A recurrent unexplained overdelivery can block qualification even with no safety event.

## Natural600 activation and4200 horizon

Use the existing unchanged natural candidate `artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R900_S17_T1_A03/`, which has horizon4200, meter activation600, seed17, M3000/R600/U300/X150, original Feedback11/70/300..900/initial900, network SHA887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca and routes SHA99151ed51419c8d490c0f0b1a91bea23f6be70c5486890a04e1e06b3de5d808e. This is an existing development input, not a new formal demand choice or matched-effect claim.

Remove the technical pre-queue program hold at600..1200. Parameterize activation600 throughout ledger, bridge, adapter and E1 producer, and preserve real Feedback's30s windows600..630 etc. Do not hide the change by translating the connection's reported clock. Keep the unchanged precontrol OPEN until600; at activation, an available receiver permits OPEN G -> chosen program G as a same-colour continuation. The natural request file has no R departures before600; bind and verify this exact input plus the actual activation frame. Subsequent new greens still require completed clearance and the strict receiving gate.

If a general input has a blocked receiver while the initial precontrol signal is still G, all-red cannot be commanded abruptly. The exact natural candidate is expected to have no local R at activation; an unexpected non-empty/denied first frame must stop before unsafe setters with a precise unsupported initial-transition classification. Supporting arbitrary preloaded initial congestion would require an explicit normal yellow/red transition using the unchanged existing transition timing and corresponding ledger support. Do not quietly add an unsafe direct G->R shortcut or treat the special no-preloaded-R condition as universal qualification.

The current yellow responsibility seam was approved and observed only for finite diagnostics. Reusing its complete-input native responsibility behavior for a longer natural technical observation needs explicit source/card scope and scientific safety review; it is not inherited as a universal certificate. Keep actual safety/UNKNOWN stops, original timing and all failed-witness rows. Do not tune timing or model after outcomes to manufacture a pass.

## Minimum implementation ownership

Prefer one new namespace `src/candidate_a_natural_service_20261015/` with `policy.py`, `adapter.py`, `producer.py`, `bridge.py`, `profile.py` and a small explicit budget module if the existing ledger cannot represent a genuinely authorized new allocation. Preserve all old154 and finite-scope sources/cards/readers byte-for-byte. Reuse existing parameters, Command/Feedback, E1 event ledger, identity/inventory/safety and body helpers, frame cache, warning capture and resource watchdog. Avoid time-shift facades or a second controller framework.

The new adapter/loop need real activation and withheld-red branches; a newly added ledger that is not called by the native path is insufficient. New profile/source closure must include actual imported helpers and the independent new reader, inherited raw inputs and exact terminal-analysis version. Original uncorrected reader and processed terminal repair keep separate identities. Root owns authorization/canonical release and repository documentation. Data owns the independent new audit and processed evidence; science is read-only after a bound implementation. No overlapping writes.

## Necessary offline checks before native release

Use a few grouped deterministic fixtures, not a rate/seed matrix:

1. Identical request histories with full,0/1 and blocked service produce the same C-E nominal period sequence; C/E/N decomposition remains exact and unmet physical service does not cause catch-up after recovery. Cover a dynamic request inside a held packet and raw own-previous ALINEA/E1 decisions.
2. Empty/one/late cases continue through multiple complete packets; valid receiver denial creates all-red packets with zero green setters, no false application, preserved nominal opportunities and correct next-boundary recovery. Unknown input and unsafe initial transition fail closed.
3. The real new loop and adapter enforce G/y/red clocks, strict receiver admission/current-gap checks, actual G ACK and pending/superseded status. Inject bad ACK, collision/braking/red-entry/unknown-coverage faults; safety/data faults must not become benign constraint records.
4. Complete terminal, partial terminal, censored tail and request pending at EOF retain their real support. Denied starts never invent Y or G exposure, N2 or full-window success. Purpose/card/source/release checks refuse old or absent bindings before output/launch.

Tests establish implementation behavior only. The independent reader must reconstruct C and nominal schedule from logged original requests/actual interval support, N from actual entry IDs, phase applications and hold acknowledgements, and require complete E1/vehicle/warning/EOF coverage before a technical judgement. It must not use reported C/E/N fields as its only evidence or require each nominal packet's N=2.

## Candidate run, resource estimate and authorization boundary

First candidate: one unchanged natural M3600/R900/U360/X180 seed17 technical run to4200 with activation600, actual ALINEA and full evaluation1200..3000, plus the initial and clearance intervals. Observe requests and service during loading, any natural limitation, sustained demand and demand clearance. An unobserved receiver-blocked state remains NOT_TESTED; do not manufacture it by changing demand. Only a clearly motivated first-run finding may justify the second permitted identity; do not schedule it automatically.

Observed old Dynamic and realALINEA costs were155.480803208s and157.092606667s for1296 simulated seconds. Simple4200/1296 scaling gives about504..509s wall time. Their frozen raw manifests contain442,183,368 and442,380,604 bytes, scaling to roughly1.43GB. These are rough engineering estimates: active-duration, population, congestion, disk fsync and new hold logging differ, so they are not promises. Read-only disk check at investigation showed35,459,895,296 free bytes.

Propose first-run wall ceiling900s, startup60s, minimum free5GB and no arbitrary byte cap, with continuous monitoring and preserved child cleanup. This is a proposed resource envelope only. The old same600 stage already spent475.645467625s, leaving124.354532375s; it cannot finance the expected natural run and cannot be reset by a new namespace. Root must establish a valid additional allocation or stop at the fully prepared authorization boundary. Preserve all old charges, reservations and manifests. Maximum two starts is not itself an exact card, numeric budget or canonical release. If execution is blocked by this gate, deliver complete implementation/offline/review/card preparation without claiming natural qualification.

## Source evidence and unresolved choices

Owning sources read: original cumulative policy/producer; native-yellow adapter/bridge/profile/budget; original qualification actor and worker; natural A03 card/input; original Feedback implementation; new finite seam; last native receipts/manifests; `docs/development/ACTUATOR_SOURCE_TO_DESIGN_LEDGER_20261007.md`.

The local source-to-design ledger separates rate selection, signal operation and measured service; it records Kotsialos2006 full-text access and Papageorgiou/Papamichail2008 abstract-only access. Root is currently retrieving the requested original papers, FHWA and SUMO official sources. This engineering proposal does not pretend to have newly read inaccessible full text or attribute the C-E recurrence, exact packet timings,900 ceiling or native safety qualification to those papers.

Before implementation: data and science should resolve the signal-ledger semantics for withheld packets, initial same-G activation, legal G/y overquota classification and the scope of yellow-native responsibility. These are finite, testable interface questions. A requirement to change ALINEA core, vehicle dynamics, natural demand, original phase timings, research metrics or formal protocol is outside this proposed repair and must return to the user.
