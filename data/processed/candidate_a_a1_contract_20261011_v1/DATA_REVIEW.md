# Issue #8 independent data review

2026-10-11. Project `data_analyst` `/root/issue8_data`. **Disposition: `PASS_FOR_BOUNDED_UNRESOLVED_A1_EVIDENCE_DELIVERY`, subject to parent delivered-commit clean-checkout verification.** This evaluates evidence integrity, input coverage disclosure and offline arithmetic; it does not qualify A1, A2 or Candidate A. `UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET`, current-contract STOP3, NOT_QUALIFIED, HOLD and 900 NOT_TESTED remain accurate.

## Context and scope

Read AGENTS, project data-agent instructions, PROJECT_STATE, DECISIONS, WORKLOG and the empty EXPERIMENT_PROTOCOL; live Issue #8 snapshot, new engineering contract/specification/ledgers, and latest PR #5 V3 and PR #7 P1/P3 scientific reviews. Stage 6 is closed under D-018; D-019 is historical bounded development authorization. Formal protocol remains 0 bytes/unfrozen. This is **exploratory offline engineering evidence analysis**, not formal experimental analysis. No new official metric, threshold, exclusion rule or simulation was selected. Missing historical native state is disclosed rather than guessed. No SUMO/TraCI starts or rejected 1206→1207 movement executions.

Owned only this new processed directory and [independent data check](../../../scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py). No raw, production code, existing result, engineering file, project governance or protocol was edited. All 42 observations and all six planned service windows were retained; no failed run or unknown observation was excluded.

## Inputs, independent calculations and results

[Post-repair independent receipt](POST_REPAIR_INDEPENDENT_RECEIPT.json) records exact source/helper/test/input SHA-256, commands and full stdout/stderr. The check reads the versioned [V2 R1 input binding](../../../artifacts/candidate_a_a1_contract_20261011_v1/engineering/v2/INPUT_BINDINGS_V2_R1.json), the committed A07 snapshot, V3 gate/windows and **derived** thin phase ledger, protected net and new engineering source/coverage records. Its defaults require no ignored raw and no network.

| Check | Independent result and limit |
|---|---|
| Input/protected identities | All active input hashes match; **536/536** protected existing files match, zero drift. Historical V1 binding is retained for its original source snapshot; active helper/tests use V2 R1. |
| Saved vehicle universe | **42 unique IDs = 27 storage + 15 ingress**, exact snapshot/witness set equality. Storage has five positive-speed vehicles and 22 zeros; ingress has 15 zeros. This is saved guard coverage, not complete future affected-vehicle coverage. |
| Old guard replay | Independently computed storage length from XML, projected gap `204.49 − position`, old zero-speed rule and positive-speed `1.1+v+v²/(2b)`. All 42 witness requirements/margins/safe flags match within 1e-12 m. Sole refusal **R_flow.1**: v=0.04573822948686786 m/s, gap=1.001999189766508 m, required=1.1459706723353782 m, margin=−0.14397148256887027 m. |
| Conditional source subpredicates | Independently summed Euler decrement distances for all 42; conditional can-brake **42/42**, given explicitly projected `seen`, zero lane offset and bound model/default premises. Independently inverted the finite-sum stopping-distance function by bisection; all 42 scalar stop-speed projections match within 1e-10 m/s. No helper formula was reused for this independent inverse. |
| Complete native branches | **0/42 determined**, with **0 observed refused-red movements**. Each row preserves UNKNOWN branch / UNOBSERVED red outcome. Geometric projection/default scalar arithmetic does not supply saved DriveProcessItem/action/device/override states or complete joint receiver/follower finalization. |
| Static topology | XML confirms one controlled ramp_mid connection and configured `foes=0`. This only addresses configured crossing foes at that junction; dynamic receiver/leader/shadow/lateral paths remain unproved. |
| Derived rows and service windows | **1206 contiguous derived phase rows**, six retained windows, observed row counts **[6,0,0,0,0,0]**. Independently summed first-window C=applied C=0.5, E=0, N=1, latency=0, quantization=0.5, shortfall=−1. All seven fields are null/CSV blank in the five unobserved windows; all six full-window tracking errors remain null. |
| Cycle/crossing interpretation | One recorded crossing and zero complete cycles. Partial six-second accounting never becomes rate qualification; missing windows never become measured zero. |

The 42 conditional arithmetic booleans are **not** 42 reconstructed complete native branches. The missing-state conclusion is limited to this evidence and this derivation. It does not prove interface infeasibility: a separately derived conservative sufficient interval covering every possible native speed/branch could substitute for exact hidden-state reconstruction. No such joint interval proof currently exists. An RNG seed alone is insufficient, but an exact RNG state need not be mandatory if all its admissible outputs are bounded safely.

## Numeric defect, controlled repair and actual tests

Independent finite-extreme probes found one required offline-helper repair: finite tiny deceleration caused `OverflowError`; finite huge speed produced NaN brake arithmetic; a huge finite stop gap caused `OverflowError`. The diagnostic sometimes returned INELIGIBLE from unrepresentable arithmetic instead of UNKNOWN. This was a helper robustness defect, **not a native SUMO safety finding**. [Original numeric failure](PRE_REPAIR_NUMERIC_FAILURE.json) and [independent replay of hash-matched preserved V1 bytes](PRE_REPAIR_PRESERVED_BYTES_REPLAY.json) retain the failures. The preserved old contract SHA is `d507300af57dd91bf92131f393fefe0524a5f3f15b5a88953e875cbf45ac3e91`.

The engineering owner corrected only the isolated helper: intermediate numeric-domain checks and exception handling reject unrepresentable source arithmetic as ValueError, and the diagnostic returns UNKNOWN. This introduces no replacement physical clearance or approved safety threshold. Original 26-test PASS and original bindings remain historical; they did not cover these finite-extreme counterexamples. Engineering also retained a V2 binding-build failure and the resulting **31 tests / 3 ERROR** run; its empty binding is not active. The corrected active binding is V2 R1. The first combined independent run encountered an input-binding mismatch during that controlled revision and produced no false PASS receipt.

After V2 R1, the independent analyst actually executed:

```sh
python3 scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py --output data/processed/candidate_a_a1_contract_20261011_v1/POST_REPAIR_INDEPENDENT_RECEIPT.json
```

The deterministic check uses exclusive output creation. It ran the two commands below and recorded both return codes 0:

```sh
python3 -m unittest discover -s tests/candidate_a_a1_contract_20261011_v1 -v
python3 scripts/candidate_a_a1_contract_20261011_v1/audit_public.py
```

**31/31 unit tests PASS; 0 FAIL, 0 ERROR, 0 SKIP. Public audit PASS. Six independent finite-extreme probes PASS after repair.** Three diagnostic probes now return UNKNOWN and three scalar probes raise ValueError. Changed modes/dynamics, new type, missing/nonfinite inputs, unenumerated ingress, receiver/foe unknown, stale phase/link/time, committed approaches and forged proof flags have bounded fail-closed test coverage. No snapshot can enable an ELIGIBLE path in this helper. These tests challenge input/state logic and algebra; they do not execute native vehicles.

Tested helper SHA `5cbaa36cacf2d0e409e507efb64f15f7416c0a73f765805bb78d3c3635c6dfb6`; test SHA `563138bd6ab677da3d7faea7c3d32cbf65243b04c4836ff076467dd77d841866`; independent-check SHA `db14c72984fbbe40a966e0c3490e0f25c1cb229f18b77d0cd726d92021ebd109`. Complete active inputs and hashes are in the receipt. Standard-library Python **3.13.0** was actually used. Parent must verify the delivered code commit in a clean checkout with ignored raw absent before making that delivery claim; this analyst receipt does not claim that gate has already passed.

## Source and public/local capability boundary

[Local source readback](LOCAL_FETCHED_SOURCE_READBACK.json) independently rehashed all **20** previously fetched official files and matched **36** excerpt texts to their physical lines. This checks the engineer-fetched bytes in an ephemeral local temporary directory; it did **not** perform an independent remote retrieval and is not a clean-checkout dependency. Official source commit is `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3` (v1_26_0).

Default public verification binds committed receipt/excerpt bytes and their fixed source URLs. It does not independently fetch full official source files, certify a compiled binary, reconstruct ignored original raw phase rows or recover future native state. The thin ledger remains explicitly derived. No optional raw enhancement was added in Issue #8; upstream PR #7 local-raw verification remains a separately scoped historical capability.

## Findings and safest next step

Required numeric robustness finding: **addressed and independently rechecked**. Unaddressed data-integrity Blocker/Major/required Minor: **0/0/0**, subject to parent clean-checkout delivery gate and subsequent scientific review. Existing proof gaps are accurately retained as unresolved engineering obligations, not concealed test failures or qualification passes.

Data supports `UNRESOLVED_NEEDS_EVIDENCE`: current observations cannot establish complete affected-vehicle/entrant coverage, actual full native branch, ordinary-braking and noncrossing finalized-speed intervals, follower-chain safety, or dynamic receiver/leader/reservations. A1/A2 remain unvalidated; STOP3/HOLD and four later unexecuted rates remain. Next is independent scientific review followed by bounded Draft delivery, then user/Chat review. Any future static gap-closure, runtime gate implementation or separately identified R300 smoke needs its own explicit authorization.
