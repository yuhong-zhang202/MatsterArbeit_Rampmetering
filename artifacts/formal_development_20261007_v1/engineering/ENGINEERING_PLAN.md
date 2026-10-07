# Bounded formal-design development: engineering prelaunch plan

Date: 2026-10-07. Classification: DEVELOPMENT, not a formal experiment.
Status: awaiting offline verification and independent exact-card release.
Historical preregistration status above is preserved. Current execution
evidence and holds: `RATE_SHORTFALL_DIAGNOSIS.md` and
`FIX02_DIAGNOSIS.md`; these supersede the initial status and do not
change any registered traffic parameter or release future starts.
Authority: the user's complete goal objective, preserved by the primary agent
in `../AUTHORIZATION.md`; D-019 records the new bounded authorization. Stage6
remains closed and the formal protocol remains empty/unfrozen.

## Scope and reuse

Only M3600, R750/900, U360, X180, seeds17/23/42, OPEN/T1/T2. Existing
network, city signals, vehicle model/attributes, 1s step, 4200s horizon, demand
windows, target11%, gain70/percentage-point, 300/900/900 bounds are retained.
Independent reuse audit: `data/processed/formal_development_20261007_v1/reuse_audit.json`.
Six historic OPEN and three R900 V15 controls are conditionally reusable;
the new wrapper must first pass one new R900S17 OPEN as its all-green
neutrality and development baseline. Do not add a second identical NOOP.
Three R750 T1 and six T2 are then nine new control combinations; ten new
simulations including the representative OPEN if reuse qualifies. Technical
attempts and failed replacements are retained separately from combo coverage.

## Temporary queue protection, prospectively fixed

Detailed numeric contract: `PARAMETER_CONTRACT.json`. All choices are temporary
development parameters authorized for this task, not Robert-approved or formal.
Compiled route coordinates run along shared(238.80m), internal urban-diverge
(113.08m), and storage(204.49m), with the meter at their cumulative downstream
end. Actual vehicle front and length define rear position. The 81.98m ramp-mid
internal lane is downstream of the meter and is not counted upstream.

Every pre-step second, risk extent is the farthest low-speed R rear upstream
of the meter in **storage or upstream urban-diverge internal**. Low speed is
strictly <1.389m/s; no low R yields extent0. Gaps are permitted. This is an
extent proxy, not a continuous meter-anchored physical queue or storage capacity.
Shared-lane low R is independently observed and logged, but shared-only city-red
R cannot trigger protection. A single upper-stream slow R can trigger if it
persists; that conservative proxy does not identify a unique queue origin.

Trigger at extent>=261.03m for10 consecutive observations: storage204.49 plus
half internal113.08/2, leaving56.54m geometric distance before shared boundary.
Release at extent<=102.245m for30 consecutive observations: half storage.
These fractions and confirmation durations provide a transparent development
hysteresis; they are not calibrated queue/safety thresholds. Intermediate
extent preserves active state; broken confirmation resets its streak.

State starts inactive at t600, streaks0; no commands beyond t4200. Invalid,
missing, duplicate, nonfinite or unmapped required observation stops before the
next simulation step, retaining failure evidence. Empty observed lanes are valid.

T2 final command=max(nominal ALINEA,900) when active; otherwise nominal.
Nominal ALINEA continues its own clipped feedback state and is never overwritten
by final command or actual service. T1 and OPEN record the same observation,
with override disabled. All policies retain their own controller to4200; no
temporary all-green clearance. R900 protection may fail to reduce accumulated
queue because900 command has no guaranteed recovery surplus; this is an outcome,
not implementation failure or permission to adjust thresholds/cap.

## Minimal source changes and measurement

New independent source lives in `scripts/formal_development_20261007_v1/`.
`control.py` is a byte-identical V15 feedback/pulse copy. `v15_worker.py` extracts
the original startup, E1 event ledger, guard, crossing/interlock and worker code;
the unchanged `src/stage6_safe_actuator_v10.py` is directly used. New code changes
only scoped paths, cards/guardian, pre-step observations, final-command selection
and its additional log. Original source/raw/cards remain untouched.

`queue_override.csv` contains4200 pre-step-labelled observations, nominal raw and
clipped rates, trigger observation, active state/streaks/transitions, final rate,
post-step crossings, safety reason and dropped credit. `controller_steps.csv`
command_rate is final command. `feedback_updates.csv` remains nominal recurrence.
Old analysis helpers with1200 orR600 hardcoding must not certify the new runs.
The independent data agent reconstructs final-command credit/rate and full cohorts.
Physical shared exposure and historical strict30s continuous-chain diagnostics
remain separate from this deliberately gap-permitting risk proxy.

**2026-10-07 clarification of the historical sentence above:** the CSV can
contain4200 labels for a complete run, but labels0..599 carry empty/precontrol
observation placeholders. There are3600 actual registered pre-step queue
observations at600..4199. Do not describe all4200 rows as queue measurements.
The observed field/population and control times remain unchanged. Partial
failed runs contain only the preserved rows up to their termination.

## Resource proposal and stopping

Read-only disk snapshot: approximately25.60GB free (25,001,692KiB). Historic
18OPEN raw approximately198.84MB and technical/control raw approximately211.96MB.
The completed V15 S17 SUMO log reports22.68s. Extra observation queries/logs may
increase time and size; this is an estimate, not a performance guarantee.

Proposed new envelope:180s per attempt including startup, startup deadline60s,
300MB per attempt,4GB new-development raw, minimum5GB free reserve,0.2s polling.
These independently chosen limits are not inherited old card budgets. Ten
planned new runs at the per-run ceiling require up to3GB; actual receipts are
used for later estimates. Stop the owned process group on a limit, keep all
partial raw and a failed receipt. No deletion, resource purchase or outside
scope run. Small polling/termination overshoot is recorded, never hidden.

## Qualification and sequencing

1. Offline: unit boundaries, exact periods, risk internal mapping, shared-only
negative case, confirmation interruption, invalid values, hysteresis, independent
nominal state, and final-rate pulse credit without burst. Source/input hashes
and pure preflight bind the exact prospective contract.
2. Independent science review and primary-agent release for first R900S17 OPEN.
3. Independent OPEN neutrality/input/data gate; reuse R900S17 T1 if qualified.
4. Exact release of R900S17 T2; audit triggers/release and final-command service.
5. R750S17 T1 thenT2; data gates before seeds23/42. Poor traffic outcomes do not
stop valid coverage, but implementation/data errors require evidence-based repair.
6. Rate eligibility: fixed300s windows with nonempty storage every decision second;
integrate final command, retain receiving/safety denial. Report all windows. With
none eligible, report NOT_TESTED and separately state the prior bounded actuator
qualification plus actual crossing evidence; do not manufacture a qualifying window.

No SUMO start is authorized by this engineer's plan alone. No formal evaluation
seeds, protocol changes, statistical acceptance thresholds or email to Robert.
