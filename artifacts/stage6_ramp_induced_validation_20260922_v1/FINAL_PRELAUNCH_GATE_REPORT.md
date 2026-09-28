# RI3350 control — final prelaunch gate disposition

**Date:** 2026-09-23  
**Run ID:** `RI3350_CTRL_S17_attempt1`  
**Disposition:** `PRELAUNCH_BLOCKED — NO FINAL CARD — ZERO SIMULATION STARTS`

Bounded scientific review record: `FINAL_PRELAUNCH_SCIENTIFIC_REVIEW.md`.

## Decision

The user's conditional authorization permits one start only if every prelaunch
gate passes. That condition is not met. In particular, the exact per-run
wall-clock and output-size ceilings and their enforcement semantics are not
bound to an authorized card. The design plan describes 5 min / 150 MB as a
preferred aggregate planning allowance and 10 min / 300 MB as an aggregate
hard planning ceiling across the proposed multi-run localization design; it
does not clearly approve either as this single run's per-run limit. The runner
uses a polled directory-size tripwire that may overshoot, not a strict storage
quota. No value or stronger guarantee is inferred here.

Therefore this report does **not** create an executable card or consume the
conditional authorization. The existing Revision 2 card remains
`DRAFT_NOT_AUTHORIZED`. No SUMO simulation, netconvert, or TraCI run was started.
One `sumo --version` environment query was previously run and is recorded as
an environment probe, not a scientific start.

## Gate results

| Gate | Status | Evidence / limit |
|---|---|---|
| R01 static input semantics | `PASS_BOUNDED` | Existing receipt confirms intended M/U/X equivalence and R removal; runtime/XSD validation is not claimed. |
| R02 one-start runner implementation | `PASS_MOCKED_IMPLEMENTATION; PRELAUNCH_BLOCKED` | 13 tests pass, including one-use/no-retry, spawn-failure consumption, and finite runtime (`NaN`, `+inf`, `-inf`) rejection. No real SUMO launch compatibility or crash-survivor supervision was tested. |
| R03 pairing | `PASS_PLAN_FIXTURES; FUTURE_NOT_EVALUABLE` | No transition realization exists; this is not a control-start blocker under the authorization. |
| R04 production adapter | `PARTIAL — READINESS_BLOCKED` | 24 adapter tests plus 12 reviewed-attribution interface tests pass locally (36 total). Independent data re-audit confirms earlier adapter defects/minors fixed; independent scientific review closes four interface findings plus receipt-tampering hardening. Production integration remains unverified: no trust-root verifier is configured/bound, locked-output event/gate extraction is not integrated, and event-source completeness (especially verified zero events) is not independently checked. No RI3350 raw exists to apply. |
| R05 PRE/control screens | `PASS_SYNTHETIC_FIXTURES; REAL_RAW_NOT_APPLIED` | 16 R05/R06 helper fixtures pass; actual screen rows remain future data. |
| R06 route exposure | `PASS_HELPER_FIXTURES; NOT_APPLICABLE_TO_R0_CONTROL` | Control has scheduled R=0. No R crossing will be imputed. |
| R07 / G6 | `G6_UNKNOWN_ACCEPTED_FOR_CONTROL_ONLY` | Explicitly allowed by user for this no-R control. It is not a suitability PASS and cannot justify transition. |
| Exact runtime/input/output binding | `NOT_FINALIZED` | No final card; resource fields remain unresolved. |
| Engineering prelaunch review | `BLOCKED` | Runner mock contract is implemented. Polling storage tripwire can overshoot and an abrupt runner failure can orphan the child. These limitations must be accepted or technically resolved under the authorized resource contract. |
| Data prelaunch review | `PARTIAL / NOT_READY` | Independent data audit reran the R04 adapter suite at 24/24 and confirmed prior technical findings/minors are fixed. The separate interface suite is locally 12/12 (36 combined with adapter); real raw application remains future. |
| Scientific prelaunch review | `BLOCKED` | Read-only review passes the static reviewed-attribution interface scope with 0/0/0 findings and confirms 36/36 suite result as execution-agent evidence. Production trust-root/event/gate-source integration and resource/card binding remain unresolved. G6 UNKNOWN is not a start blocker under this authorization. |

## Offline verification performed

Commands run with the repository `.venv`:

- R02 runner suite: 13/13 passed.
- R04 adapter suite: 24/24 passed; reviewed-attribution interface: 12/12 passed (36 combined).
- R05/R06 helper suite: 16/16 passed.
- R07 coverage audit fixture: 1/1 passed.
- R01/R03 static audit and matching/mismatch/missing/duplicate fixtures: PASS.
- `py_compile` for runner and R04 adapter: PASS.
- `git diff --check`: PASS.

These are implementation/fixture results, not validation on a newly generated
simulation output.

Current implementation hashes:

- R02 `runner.py`: `49d642d72d2d500e3546266699a70007f609b35b5947426b321ac99ab5be48bc`
- R02 `test_runner.py`: `12698e721be24bc4714b63df88a37f6f1b14067bddc88ef14f4fa83ef815a10c`
- R04 adapter: `5153a8f1eaedf97bffd3102f1bc46b382b67d225bef4f0282e1c05d6d016cb41`
- R04 tests: `9f53bef681af3e5de0c5237496c3b6986c4afa4873bd3264232ba793cd29f65e`
- Reviewed-attribution interface: `d8b078ded1e8b7da38da9ef953cf263db8a063204e4496bf36aae27261cde777`
- Interface tests: `9f61291bb57380ad7fe52bce894eeb5e2a73b6071c511a491afa94514c3ac75d`

## Required next action

Resolve the resource contract explicitly: exact single-run runtime and output
thresholds, whether output size is a monitored stop trigger or a strict quota,
and acceptance/mitigation of the documented abrupt-runner-failure limitation.
Bind a real trusted signature verifier and reviewed, hash-bound mapping from
locked output events/gates and full event-source coverage into the already
specified adjudication interface, without changing the locked classifier.
Apply the final adapter only after raw exists, then bind all input/runtime/
output/code hashes in a new exact card and rerun final preflight review. Do not
execute until those gates pass.

This is preparation only. It does not change demand, geometry, controller,
classifier, thresholds, formal protocol, Stage 6 result, or O2 status.
