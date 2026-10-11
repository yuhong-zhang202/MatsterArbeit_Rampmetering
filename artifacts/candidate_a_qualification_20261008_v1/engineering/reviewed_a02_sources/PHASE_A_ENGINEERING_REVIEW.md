# Candidate A Phase A engineering review

Status: **offline package ready for independent review; no traffic run released or executed**. Technical qualification only, based on PR #3 head `35651751a2e03d1906ff32a267a95077553c4404`. This report does not change Stage 6 closeout, research parameters, protocol status or formal authorization.

## Context and boundaries

Mandatory context reviewed: AGENTS; simulation-engineer role instructions; PROJECT_STATE; DECISIONS; empty EXPERIMENT_PROTOCOL; WORKLOG; Issue #4 snapshot; PR #3 technical/data/scientific reports and source-to-design ledger; protected FIX02 runner; actual compiled network and additional/configuration inputs. Formal protocol remains empty/unfrozen. Current work implements only Candidate A; all old 67 protected paths remain unchanged. No environment installation or Candidate B implementation.

## Prospective actor and mapping

New native programs use G=3 s, yellow=3 s, red>=2 s, nominal packet n=2, and integer periods 8–24 s. Yellow retains the existing B/C reference and red retains the existing minimum spacing. Green is a prospectively fixed short-packet technical choice; these choices do **not** prove minimum safe timing or two actual vehicles per cycle. Minimum period8 can nominally represent900 because `Tmin <= 4*n`; actual discharge must be measured. No outcome-based timing replacement or safety relaxation is authorized.

Cumulative ideal periods `7200/r` are rounded down, and each discrete period is the difference between successive cumulative boundaries. For750 this produces9/10 s periods, rather than repeatedly choosing a biased period. Green/yellow transitions are native; red self-loops until a planned, receiver-safe cycle start. Pending feedback applies only at the next planned boundary, even when that cycle is denied, with maximum23 s integer-grid latency. Feedback cannot restart green.

Separate completed-step ledgers preserve command C, cycle-applied command, nominal opportunity E, and unique actual stopline crossing N. E includes every completed planned cycle, including denied ones; N includes G/y/r crossings without clipping to n. A before-motion failure accrues no fictitious next-second C. A post-motion failure retains completed-step C/N, actual last completed time, and the failure snapshot. The exact identity is `C-N = (C-C_applied)+(C_applied-E)+(E-N)`.

For fixed commands, arbitrary finite-window mapping error is conservatively bounded by `<2*n+2*r/3600` vehicle equivalents (at900, <4.5), including boundary/partial cycles. This is not an actual tracking guarantee. Variable inputs require the recorded exact latency term and rate-weighted quantization terms; a generic rate-independent <n bound is not claimed.

## Native semantics, observation and safety

The static audit binds SUMO1.26 source and installed TraCI API, compiled network, and runtime guards. At native begin-of-step events, a getter may still show the old phase when nextSwitch equals current t. The worker predicts that pending transition before motion and checks the actual post-step state. Offline tests cover same-time G/y and y/r boundaries; runtime behavior remains unqualified.

Compiled ingress/storage/internal lengths are113.08/204.49/81.98 m. At unchanged type maximum speed plus acceleration, maximum one-step advance58.15556 m is smaller than ingress and internal lengths. Newly observed internal IDs therefore yield a stopline-crossing interval `(t,t+1]`, not an invented precise crossing time; the internal lane cannot be skipped in one step. All relevant vehicle IDs, colors, cycle assignments, observations and command delays are retained.

Before G, receiver storage and route-aware native secure gaps are checked. Before any pending transition into red, all remaining storage and ingress vehicles are checked against a normal braking envelope `1.1+v+v²/(2*b)` for every positive speed. Only exactly stationary vehicles are exempt, under native-red compliance. Low positive speed near the line is explicitly tested. Unknown or unsafe state saves the attempt and closes without another simulationStep; no forced red or yellow extension. Normal braking, collision, teleport and red-crossing failures are retained. Old FIX02 safety results are not transferred.

## Fixed-rate cards and supply fixture

Final five A02 cards cover300/450/600/750/900, unchanged M3600/R900 seed17 demand and1 s step. A01 snapshots were never launched and are explicitly superseded. The exact paths and hashes are in PHASE_A_FINAL_CARDS.json.

All Phase B cards share open until600, native yellow[600,603), red[603,1200), then the qualification actor. This is an external prequeue fixture, not an ALINEA command; prefix C/E are0, actual N and raw lifecycle/source/in-network states remain available. It changes the traffic initial state and supports only prequeued service qualification, never fair OPEN effect claims. Prefix length cannot be extended after observing results.

Six300 s windows[1200,3000) retain the original10% C-versus-N tracking screen. Storage R must be present at every pre-step of a window; insufficient supply is NOT_TESTED. Supplied service failures and receiver denials remain failures. No effective supplied windows is NOT_TESTED, never PASS. Independent data review determines qualification from raw records. Phase C has natural activation600 without preload and remains prohibited unless all five fixed-rate gates including900 pass.

## Verification and execution gate

- 18/18 offline tests pass; syntax checks pass. Exact tested-source hashes and log hash: PHASE_A_OFFLINE_RECEIPT.json.
- All67 protected files match; all five final cards validate source/input/configuration bindings and XML/program structure.
- Environment and official/native source anchors: STATIC_API_GEOMETRY_ENVIRONMENT_AUDIT.json.
- Offline XSD validation was not run because lxml is absent; no dependency was installed. Native inherited `xml-validation always` remains enabled. This limitation is not hidden as a pass.
- New SUMO scenario starts: **0**. No Phase C card generated or released.

Runner defaults to offline preparation/checking. Launch requires exact card hash, bound independent science review and one-use root release. Fresh immutable attempts, source/config/network snapshots, guardian receipt and replacement-chain evidence are mandatory. Existing effective configurations cannot be rerun to select a better outcome. Limits:180 s wall/run,60 s startup,300 MB/run,4 GB new raw,5 GB free-space reserve. Issue max7 effective configurations and its five STOP conditions remain intact.

Safest next step: independent exact-source/card scientific prereview, then **only one fixed300 launch** if root explicitly releases it. Inspect its raw accounting and failure preservation independently before any remaining fixed-rate release. Runtime discharge, phases and safety are still unverified; a failed technical qualification is a valid result, not permission to tune protected inputs.
