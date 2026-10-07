# Issue #2 engineering investigation

2026-10-07. Technical investigation only. Base: Draft PR #1 head
`e8bf608a15cf4c4484914467c5550d041c017a62`.

## Context and scope

Read AGENTS.md, the simulation-engineer role, PROJECT_STATE.md, DECISIONS.md,
EXPERIMENT_PROTOCOL.md, recent relevant WORKLOG entries, Issue #2 snapshot,
the final development engineering summary and protected FIX02 sources.
Stage6 remains closed under D-018. D-019 development coverage is complete but
actual service is NOT_QUALIFIED. Protocol is actually empty/unfrozen; no formal
parameters or formal-run authorization are inferred. Scope is new offline
investigation tools and design sketches, not changes to PR #1 or its controller.

## Verified implementation facts

1. `control.py:PulseScheduler` integrates final command at `r/3600` each second,
   consumes one credit per green, enforces at least 3 s between green starts,
   and clips residual credit to 1. Under an ideal permissive guard, its theoretical
   pulse ceiling is 1200/h; the approved development command cap remains 900/h.
   Thus minimum-red discretization alone does not explain a roughly 40% deficit.
   The new test verifies 601 integer commands, 300–900/h, each over 3600 steps:
   number of green opportunities equals command exactly, no lost credit.
   This is an arithmetic scheduler result, not a traffic result.
2. `safe_actuator_fix02.py` retains the old front/receiver/route/leader checks,
   adds a pre-green bound for all storage followers and covered approaching R,
   and leaves the mandatory post-green immediate-red interlock unchanged.
   The bound budgets the green advance plus the following red reaction/braking.
   It is deliberately conservative; it is not an exact Krauss next-step solver.
3. The moving front must be one-step reachable before release. The stopped
   front must be within the existing margin and have receiver clearance.
   Repeated denied steps keep credit at most 1 and lose additional accrual.
   Lost credit is an accounting consequence of denials/capping, not an
   independent additive causal category. Data-role raw decomposition is the
   authoritative source of observed counts and balances.
4. Worker calls `setRedYellowGreenState` before each step, observes state, then
   measures newly entered internal-lane IDs and applies the post check.
   There is no native yellow transition in this current one-step G/r operation.
   Historical observed safety PASS therefore applies to this guarded version,
   not automatically to any new native TLS program.
5. The verified meter controls only ramp_storage→ramp_accel via `:ramp_mid_0_0`.
   Its storage length is 204.49 m. The checked downstream connected path to the
   merge entry is 181.05 m and lookahead is 478.67 m. A freeway merge safe-gap
   theorem cannot simply be applied at this upstream stopline: travel time and
   subsequent lane changes change the relevant conflict state.

## Public implementation and API audit

Public sumoITScontrol HEAD read on 2026-10-07 is
`48a88131f35e2a42f6e0b4511f2f1ee0792daa40`. Exact file hashes and line anchors
are in PUBLIC_SOURCE_AND_ENVIRONMENT_RECEIPT.json.

- [RampMeter source](https://github.com/DerKevinRiehl/sumoITScontrol/blob/48a88131f35e2a42f6e0b4511f2f1ee0792daa40/src/sumoITScontrol/ramp_meter.py#L83)
  accepts green share, sets green=`int(share*cycle)`, red=`cycle-green`, edits
  phases 0/1 and resets phase0 after loading the logic.
- [ALINEA source](https://github.com/DerKevinRiehl/sumoITScontrol/blob/48a88131f35e2a42f6e0b4511f2f1ee0792daa40/src/sumoITScontrol/control/ramp_metering/ALINEA.py#L72)
  passes percentage/100. This is not the project's veh/h interface. The default
  saturation_flow field is not used in the examined rate-to-signal function.
  No actual 300–900/h guarantee, clearance qualification or one-car counting
  follows from copying this function. Reuse separation of controller and signal
  operation, with a separately qualified unit conversion and transition layer.
- Installed distribution is 0.1.0. Its files have different full hashes from
  the pinned public HEAD, although read-back finds the same relevant mapping
  expressions. Neither installed source nor dependency versions were changed.

[SUMO official traffic-light documentation](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#controlling-traffic-lights-via-traci)
supports changing to a yellow phase and letting the program finish transitions.
`setPhaseDuration` changes only the current remaining duration; direct state
commands put transition responsibility on the script.
[The safety documentation](https://sumo.dlr.de/docs/Simulation/Safety.html)
warns about insufficient yellow and tau below step/action-step. A native TLS
program does not itself prove safe braking or a precise per-green vehicle count.
No universal minimum yellow duration is inferred for this ramp.

## Candidate A — Proposed cycle/discrete operation

**Input:** unchanged final r_cmd [veh/h], including existing queue override.
**State:** current program/phase, phase entry time, pending command timestamp,
chosen cycle, nominal n (1 or 2), optional fractional-cycle residual,
per-cycle measured crossings and time-integrated command ledger.

**Logic:** select only a prospectively qualified tuple (G duration, yellow,
red/clearance, nominal n). Apply a new command at a documented safe cycle
boundary, never restart green at every feedback update. Native phase order is
G→yellow→red, adding all-red if the controlled-link clearance requires it.
TraCI enters the appropriate transition phase or changes remaining phase time;
do not mix persistent online state commands with a supposedly automatic program.
Yellow may permit passage; count ALL stopline crossings, including yellow,
and bind them to the cycle. n is a target/qualified discharge statistic until
measured; a TLS does not enforce one/two vehicles just by duration.

**Safety:** retain vehicle dynamics, tau/actionStep=1 s, route/link identity,
receiver availability, collision/emergency-braking/wrong-crossing monitoring,
and conservative stopping/clearance coverage. The current immediate-red
postcheck is specific to a 1 s green followed immediately by red. A longer
G/y/r policy needs its own prospectively reviewed transition invariant; it must
not bypass an unsafe red just because a phase index exists. This is a proposed
replacement proof obligation, not permission to disable the current interlock.

**Contract:** nominal rate q=3600*n/C. Actual rate is separately measured crossings
per elapsed window. With G+Y+R_min=T_min at 1 s resolution, nominal 900/h requires
T_min≤4*n: ≤4 s for one nominal vehicle or ≤8 s for two. Nominal 300/h uses C=12*n.
If qualified startup/discharge and transition timing cannot fit this inequality,
900/h is infeasible for that tuple. Do not shorten yellow/red to make it fit.

| Command [veh/h] | n=1 ideal cycle [s] | n=2 ideal cycle [s] |
|---|---:|---:|
|300|12|24|
|450|8|16|
|600|6|12|
|750|4.8|9.6|
|900|4|8|

Integer cycle choice quantizes rate. Nearest one-car cycle at command810/h maps
to720/h (5 s), error11.111%; a 10% service gate could fail from that mapping alone.
Mixing adjacent integer periods using a cycle-count residual can track the mean
period more closely: nine one-car cycles at810/h total40 s. This does not mean
nine actual vehicles discharge. Switching latency, variable command integration,
finite-window partial cycles and discharge variation remain explicit errors.

**Required logs:** final/nominal command and override, pending/applied timestamp,
program ID, phase and residual duration, commanded/mapped nominal flow,
actual crossing IDs/time/signal, cycle membership, queue/receiver availability,
safe-transition state, warnings, incomplete cycle and unused opportunity count.

**Gates:** unchanged inputs; pre-control neutrality; observed/API phase sequence;
all crossings reconciled; no unsafe transition/collision/emergency braking;
qualified cycle discharge under sustained supply; original window service screen
reported without erasing old failures; all mapping/latency deficits reconciled.
Do not confuse static phase-program consistency with passing these runtime gates.

**Minimum difference from FIX02:** new execution adapter and measurement ledger;
no feedback/demand/network/urban/override change. New phase timing, n and their
qualification are engineering proposals awaiting next-task approval.

## Candidate B — Proposed explicit safe-gap opportunities

**Input:** same final r_cmd. **State:** exact time-integrated command, owed credit,
bank limit/expiry policy, last release, minimum safe headway, front and receiver
states, checked route coverage, explicit release denial class and actual crossings.

**Logic:** command creates opportunities; release needs demand, receiver, validated
physical following/stopline safety and transition safety. Credit denial policy is
documented: retain/defer, explicit expiry or cap loss. Credits cannot override
safety or cause undocumented catch-up platoons. Use a single state-based predicate
with reason witnesses, not a series of undocumented new interlocks.

**Safety:** for a retained one-step single-car G/r operation, preserve FIX02
predictor and post-red interlock until an equivalent safer transition contract
is demonstrated. getSecureGap is car-following model dependent; it is not a
complete mainline merging forecast at a stopline 181.05 m upstream. Retaining
the same guard and adding a bank is not evidence of higher actual service.

**Contract:** q_opportunity is limited by admissible opportunities and safe
headway; q_actual remains measured. 900/h needs roughly75 successful crossings
in300 s, i.e. sustainable4 s average safe service including transitions.
A6 s safe service interval imposes600/h, even with900/h command and unlimited
credit. If maximum opportunity rate is capped at900/h, accumulated denial at
900 command cannot generally be repaid within the same window. Raising the
upper bound or compressing safety headways is outside this investigation.

**Credit identity:** integral command = successful opportunities + explicit
discarded credit + ending bank − starting bank. This is opportunity accounting;
if an opportunity releases no vehicle, actual-crossing deficit needs a separate
term. Demand/receiver/safety/actuator timing reasons must be distinguishable,
with first-veto and simultaneous predicates logged. Denial seconds are not
independent lost vehicles.

**Logs/gates:** Candidate A's crossing/input/safety records plus nominal due,
eligibility witnesses, credit before/after/dropped/expired and headway limitation.
Test every denial class and exact balance, then qualify actual saturated service
and transition safety. Failure mode is persistent unavailable safe gaps with
bank growth or explicit drops; no guarantee of tracking is claimed.

**Minimum difference:** extract one reviewed eligibility contract and one ledger,
preserve measurement identity and protected sources. A future alternative gap
predicate needs offline replay and independent safety review before runtime use.

## Bounded offline feasibility and decision advice

New `offline_contracts.py` imports no SUMO/TraCI and cannot launch a simulation.
Ten meaningful tests passed under project Python3.13.0. They cover:

- existing scheduler ideal 300–900/h all integer commands and exact denial balance;
- Candidate A full G/y/r mathematical fit and bounded fractional-cycle error;
- a one-car5 s transition envelope that correctly REJECTS900/h (nominal ceiling720);
- Candidate B ideal command accounting, all three denial classes, headway-constrained
  bank growth, and a6 s headway counterexample that cannot attain900/h;
- invalid timings/rates/nonsequential input.

The two-car (G=3,y=2,r_min=3 s) test is an **algebraic fixture**, not a selected
signal program or evidence that two vehicles actually cross safely in it.
It demonstrates how a fully specified8 s envelope can represent the command
range arithmetically. None of the test fixtures are scientific parameters.
No new SUMO scenario, smoke, netconvert, demand or formal run was started.
No smoke is necessary to make this theoretical-only scope explicit; actual
qualified A/B performance remains open, requiring its own engineering task.

**Technical recommendation (Proposed):** A first, because a small fully specified
cycle/transition catalogue and command-to-expected-service ledger directly expose
the lost startup/discharge/clearance time and can allow a small qualified packet.
It avoids retaining an immediate-red single-car restriction as an implicit
capacity assumption. It is not a guarantee of900/h or authorization to implement.
B remains secondary if strict individual release is required and a physical
gap/transition contract can both qualify and meet the needed service rate.

**Next minimum task:** approve a bounded actuator-implementation card; maintain
protected feedback/model/override; establish native phase and cycle crossing
instrumentation; derive/qualify one- or two-car timings without unsafe shortening;
review command mapping/latency and unchanged rate/safety screens; then authorize
one representative sustained-supply technical test before any control reruns.
If safe envelope cannot cover900/h, report infeasibility and return the decision;
do not change the model/step/upper bound or disguise a lower actual rate.
Fallback remains contingent on both candidates' qualified feasibility failure;
current theoretical checks provide no basis to adopt it as thesis scope.

## Verification and limitations

Command: `.venv/bin/python -m unittest discover -s tests/actuator_investigation_20261007 -v`.
Result:10/10 PASS,18.594 s; receipt binds tested source hashes.
Live version-only call: SUMO1.26.0; binarySHA matches existing pinned binary.
Python3.13.0, traci/sumolib1.26.0, installedsumoITScontrol0.1.0.
No phase API integration, physical gap theorem, actual A/B service or traffic
benefit was tested. No production source, parameter, protocol or raw result was
modified. Protected hashes are checked in OFFLINE_TECHNICAL_RECEIPT.json.
Root handles governance/documentation impact and final scientific review.
