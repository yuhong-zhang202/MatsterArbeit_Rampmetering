# Issue #2 — Independent FIX02 failure decomposition

Classification: technical retrospective / exploratory; **not formal analysis**. Investigation baseline: Draft PR #1 head `e8bf608a15cf4c4484914467c5550d041c017a62`. No simulation, controller change, demand change or threshold change was made.

## Context preflight and boundaries

Read `AGENTS.md`, `.codex/agents/data_analyst.toml`, current `docs/PROJECT_STATE.md`, latest D-018/D-019 in `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md` (0 bytes), relevant recent `docs/WORKLOG.md`, and the saved Issue #2. Stage 6 remains completed/preliminary-ready. D-019 development coverage is complete, its service capability failed, and formal design remains unfrozen. The empty protocol is an explicit known boundary, not authorization to choose formal metrics. This report answers only Issue #2 T1: command/credit/service accounting for current FIX02. It does not select a formal actuator, interpret traffic benefits, reopen Stage 6, or change project records.

## Inputs, scope, transformations

Included all 12 current `DEV_M3600_R{750,900}_S{17,23,42}_T{1,2}_A03` controller logs. OPEN and pre-FIX02 attempts are excluded by the explicit current-version task boundary; they remain preserved. Each has 4,200 sequential one-second rows, with 3,600 controlled rows `[600,4200)`: 50,400 total rows / 43,200 controlled rows. Controller CSV bytes and SHA-256 match each raw execution receipt. Per-run `FIX02_DATA_GATE.json` is bound separately. Raw files remain unchanged and local-only.

The script recomputes every controlled-step rate accrual, nominal opportunity, three-second minimum green-start spacing, guard/slot decision, capped credit and drop increment; it validates requested/observed state and stopline bracket counts. It recomputes all six published `[1200,3000)` non-overlapping 300 s windows per run and compares command, crossings, continuous storage supply, selected denial reasons and the unchanged 10% screen to the published 72-row service table. There are no dropped rows, missing runs, duplicate timestamps or duplicate crossing IDs within runs.

For an opportunity-only arithmetic check, the same **observed final command sequence** is replayed without the guard, retaining the three-second minimum spacing and the one-credit cap. This does not simulate vehicles, measure actual service, remove safety physically, or predict a changed closed-loop outcome.

## Exact credit accounting

For any audited interval, with `C = sum(r_final / 3600)`, `G = scheduled greens`, `D = increment in dropped_credit_total`, and boundary credit `B_start`, `B_end`:

`C - G = D + (B_end - B_start)`.

All 6,288 controlled greens correspond to exactly one logged unique crossing each. No logged red or multiple crossing occurs. Thus `G = actual_crossings` for these audited logs. Maximum per-step conservation residual is `2.842170943040401e-14` vehicle-equivalent.

Across the 72 evaluation windows:

- Final-command accrual: **4,905.0891784446385** vehicle-equivalent.
- Actual stopline crossings: **3,331**.
- Dropped credit: **1,572.0036676489306** vehicle-equivalent.
- Sum of window boundary-credit increases: **2.0855107957079424** vehicle-equivalent.
- Therefore the 1,574.0891784446385 deficit is exactly drop plus boundary carry; no unexplained balance term is needed.

Across full `[600,4200)` controls: command **10,142.511991601605**, crossing **6,288**, dropped **3,844.261991601604**, final retained credit summed over runs **10.25** (zero initial credit).

### Service qualification reproduced

**71 FAIL / 1 PASS** across all 72 continuously supplied windows, reproducing the published table. All 12 authoritative run-level gates remain `NOT_QUALIFIED`. The sole PASS is R750/S23/T1 `[2100,2400)`: command 46.529768362071..., actual 43, relative error 0.07586043271576642. Overall window relative error ranges 7.586%–40.000%; no supplied window was excluded or relabeled.

## Seven requested failure categories

| Category | What the current evidence establishes | What it does not establish |
|---|---|---|
| 1. Command discretization | Per-second credit uses the final rate in veh/h divided by 3,600; no finite allowed-rate quantization is applied. Unguarded opportunity replay differs from integrated command by **less than 0.961 vehicle in every 300 s window**, showing finite-window integer timing is much smaller than observed shortfalls. | Replay is not a physical service-capacity test; it does not show every replay opportunity could safely cross. |
| 2. Safety denial | 8,147 selected due-denial seconds in evaluation: follower post-red prediction 5,140, follower stop-distance 1,475, leader secure-gap 1,532. Same-step discarded credit associated with these selected reasons totals **1,453.6701947503554**. | These are priority-selected log reasons, not all constraints simultaneously present. Counts are seconds, not independently lost vehicles. Their discard partition is not recoverable service if a guard were removed. |
| 3. Receiver/downstream obstruction | `INTERNAL_RECEIVER_CLEARANCE` is selected in 845 evaluation due-denial seconds, with **118.33347289857522** same-step discarded credit. This is the local internal receiving-clearance check. | It does not establish remote freeway congestion as the unique cause, or predict gains from removing the receiver guard. |
| 4. No demand/queue empty | All 72 evaluation windows have storage supply at every second. **Zero `NO_FRONT` due denials** in evaluation; queue-empty demand cannot explain their failure. Full `[600,4200)` contains 2,129 `NO_FRONT` due-denial seconds and 527.504972890962 associated discarded credit. | Whole-control no-demand losses must not be substituted for supplied-window capacity failures. |
| 5. Dropped/noncompensable credit | Exact conservation identifies capped/discarded credit as the accounting route for essentially all persistent deficit. The scheduler intentionally retains at most one credit; future releases cannot recover discarded credit. | Discard is downstream of constraints; adding discard to safety/receiver “losses” double-counts the same deficit. No independent causal decomposition into recoverable vehicles is available. |
| 6. Phase timing / step length | All observed requested/actual controlled states agree. One-second green / minimum two red seconds enforce spacing; opportunity-only replay of the recorded rate sequence remains within the finite-window count bound above. | No full yellow/all-red cycle is present in this evidence. It does not prove real-world signal realism or physical maximum service under a new phase design. |
| 7. Other confirmed causes | 74 evaluation due denials select `FRONT_NOT_ONE_STEP_REACHABLE`; **zero discarded credit occurs on those selected steps**. No unexplained accounting residual, red/multiple crossing, duplicate crossing or missing control-row defect was found. | Readiness/receiver effects may overlap hidden by log priority. Zero same-step discard does not mean no indirect influence. No additional cause is invented. |

The complete disjoint **same-step bookkeeping** partition is in `category_step_accounting.csv`; detailed selected reasons are in `reason_step_accounting.csv`. Each discarded increment is counted once according to its logged reason, including steps that are not nominal due. This is an observational accounting partition, not a counterfactual causal attribution.

## Verification and reproducibility

Run from repository root:

```sh
python3 data/processed/actuator_investigation_20261007_v1/decompose_fix02.py
# Only after inspecting a necessary change to this investigation outputs:
python3 data/processed/actuator_investigation_20261007_v1/decompose_fix02.py --refresh-derived
```

Default output behavior verifies existing equal bytes without rewriting and stops on a mismatch; `--refresh-derived` explicitly permits regeneration only inside this investigation output directories. An isolated emitter unit check passed creation, equal/no-write, mismatch/stop, and explicit refresh. The actual final full rerun used `--refresh-derived` to update the receipt after these tool corrections; existing numerical tables stayed byte-identical.

Actual environment: Python 3.12.4, standard library only. No SUMO or TraCI launch/import is required. Script SHA-256 and all input/table hashes are recorded in `DECOMPOSITION_RECEIPT.json`. This validates the local script snapshot; it does not claim testing of a future Git commit.

Known-example assertions check conservation with loss, residual credit and boundary carry; category classification keeps ambiguous front-readiness separate. Raw-bound checks cover schema columns, exact timestamps/coverage, rate bounds, initial controlled credit zero and every step's credit continuity/math, green-state agreement, crossing uniqueness/counts, all 72 window numerical and status matches, and 12 authoritative gate totals. The final rerun after continuity/input-binding/output-safety corrections passed in approximately 5 s. The published service-window table hash is included among input bindings.

Produced:

- `decompose_fix02.py` and `DECOMPOSITION_RECEIPT.json` in this directory.
- `results/tables/actuator_investigation_20261007_v1/run_credit_balance.csv` (12 rows).
- `window_credit_balance.csv` (72 rows).
- `reason_step_accounting.csv` (selected-reason interval accounting).
- `category_step_accounting.csv` (12 scope/category aggregate rows).

## Interpretation limits and handoff

Raw crossing brackets are freshly audited; physical sensor/FCD safety remains the **previous independently verified, source-bound FIX02 gate**, not a newly repeated FCD analysis. `sampled_service.json` uses an older stopped-only geometry and may retain `FAIL_RECONCILIATION`; its explicit authoritative replacement is `FIX02_DATA_GATE.json.actual_service` / the V15 FCD service audit. It must not be mistaken for a new FIX02 failure or silently erased.

R900 unfinished endpoint vehicles and all costs truncated at 4,200 s remain in prior reports; this actuator audit neither changes them nor interprets the cost trade-off. Actual-safe rate qualification has not passed. No formal sweet spot, unique U-spillback cause, or universal physical capacity is inferred.

Safest next step: root and engineering/scientific reviewers should compare the two Issue #2 candidate actuator contracts using this observed bottleneck/accounting distinction. A candidate must separately qualify safe physical crossings and command tracking; passing arithmetic alone is insufficient. Any recommendation remains Proposed.
