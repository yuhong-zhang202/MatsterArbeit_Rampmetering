# Issue #8 independent data re-review — source integer-domain correction

2026-10-11. Project `data_analyst` `/root/issue8_data`. **Disposition: `PASS_FOR_BOUNDED_UNRESOLVED_A1_EVIDENCE_DELIVERY_AFTER_V3_DOMAIN_CORRECTION`, subject to delivered-commit clean checkout and final scientific readback.** This version supersedes only the active helper/test binding and numeric-domain coverage in the [historical data review](../candidate_a_a1_contract_20261011_v1/DATA_REVIEW.md). All earlier reports, receipts, failure records and source bytes remain intact. A1 is still **UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET**; no runtime eligibility or physical safety qualification follows.

## Scope and preserved history

Context Preflight remains the same ongoing Issue #8 task: AGENTS, data-agent instructions, PROJECT_STATE, DECISIONS, WORKLOG, empty/unfrozen EXPERIMENT_PROTOCOL, Issue #8, PR #5/#7 latest scientific reviews and bounded engineering inputs. Stage 6 closed/D-018 and historical D-019 authorization are unchanged. Scientific review identified one required Minor in the isolated offline helper: Python's arbitrary-precision integer could produce a finite result outside a proven native C++ `int` conversion/`steps+1` domain. This is an offline source-equivalence limit, not a production guard or traffic-safety observation.

Before repair, the analyst independently reproduced `speed=1e11, decel=4.5 → steps=22222222222`, returning finite brake distance `1.111111111061111e21`. [Counterexample receipt](PRE_V3_INTEGER_DOMAIN_COUNTEREXAMPLE.json) preserves exact V2 helper SHA. [Old independent script bytes](PRE_V3_INDEPENDENT_CHECK_SOURCE.py) retain SHA `db14c72984fbbe40a966e0c3490e0f25c1cb229f18b77d0cd726d92021ebd109`; the V1 report, post-repair receipt and final bindings remain unchanged. The earlier finite-extreme FAILs and V2 binding-build failure/3 ERROR run also remain preserved. No history is relabelled as uniformly passing.

Only the engineering owner modified the new isolated helper/tests and versioned engineering evidence. The analyst changed only its own independent script and wrote this new processed directory. No production guard/actor/worker/config, raw, official protocol, researcher decision or existing experimental output was changed. SUMO/TraCI starts and refused-red movement executions remain **0**.

## Source-domain justification and independent checks

[V3 source-domain receipt](../../../artifacts/candidate_a_a1_contract_20261011_v1/engineering/v3/CPP_INTEGER_DOMAIN_SOURCE_RECEIPT.json) distinguishes the pinned SUMO `MSCFModel.cpp:92–98` expression from the language guarantee: actual native `int` width is not inferred. A nonnegative truncation count **≤32766** makes both the conversion and integer `steps+1≤32767` representable within the language-guaranteed signed-int minimum range. The later expression starts with `speedReduction` (double), so its multiplications are already double arithmetic; there is no claimed integer-square overflow. This restriction is a **conservative portable offline source-arithmetic domain**, not a new physical speed/deceleration cutoff, compiled-native test or safety threshold.

[Post-V3 independent receipt](POST_V3_INDEPENDENT_RECEIPT.json) binds active [engineering V3 inputs](../../../artifacts/candidate_a_a1_contract_20261011_v1/engineering/v3/INPUT_BINDINGS_V3.json), tested helper/test bytes and commands. [Normal-domain regression](V2_V3_NORMAL_REGRESSION.json) compares old/new independent receipts directly.

| Independent check | Actual result |
|---|---|
| Version/protected identity | All active V3 input hashes match; **536/536** protected old files unchanged. V1/V2 bindings remain historical, with V3 selected explicitly. |
| Normal saved witnesses | **All 42 mapping rows exactly equal** to V2 independent results: 27 storage +15 ingress; sole old refusal R_flow.1. Conditional Euler finite sums and scalar stop-speed inverse still match all 42. |
| Conditional versus actual branch | 42/42 conditional can-brake arithmetic; **0/42 complete actual native branches determined**, no observed refused red motion. UNKNOWN/UNOBSERVED remain. |
| Service/observation accounting | 1206 contiguous derived rows; six retained window counts **[6,0,0,0,0,0]**, first partial C/applied C=0.5/E=0/N=1; five unobserved windows null/blank, all full-window tracking errors null, zero complete cycles. |
| Finite extreme/domain adversaries | **10/10 independent probes PASS**. Tiny decel and huge finite numerical inputs fail as ValueError/UNKNOWN. `1e11/4.5` cannot become a permissive or binding denial result. Exact 32766-step boundary returns the independently expected finite distance; 32767-step boundary raises ValueError. |
| Offline unit tests/public audit | **33/33 PASS; 0 FAIL, 0 ERROR, 0 SKIP.** Default public audit PASS, return codes 0. No ignored raw or runtime network dependency. |

Actual command:

```sh
python3 scripts/candidate_a_a1_contract_20261011_v1/independent_data_check.py --output data/processed/candidate_a_a1_contract_20261011_v2/POST_V3_INDEPENDENT_RECEIPT.json
```

The deterministic script exclusively creates new outputs and actually executes the project's 33-test command and public audit; both full outputs are in the receipt. Python **3.13.0** was used. Tested helper SHA `0c26a985627d8640bedd245dfd3211aa36a71d35eda860f37413938cd8b7c45c`; test SHA `fcda0720c1aebbfeff882fcdb8ad27c9e154a17ebc72ce88686f2a11aff17219`; independent checker SHA `f0c4075450e16022de63becae90cc8bd352df6cda09141e97abc6a97bc733f5c`. No delivered-commit clean-clone PASS is claimed here; parent must record that gate after committing the exact source/evidence.

## Disposition and unresolved safety evidence

Required scientific Minor concerning native integer conversion/`steps+1` domain: **addressed and independently rechecked** within the documented portable offline subdomain. No unaddressed data-integrity Blocker/Major/required Minor remains. Final scientific confirmation and parent delivery gate remain pending.

The public audit verifies bound published receipts/excerpts and derived phase data. The prior separate local-source readback (20 complete fetched source files, 36 exact excerpts) is retained as local evidence; it is not a default public-checkout capability. Neither mode certifies a compiled binary, independently reconstructs ignored raw phase records, or observes the unexecuted 1206→1207 movement.

Complete affected-vehicle/entrant coverage, dynamic receiver/leader/foe state, joint finalized-speed intervals and follower-chain safety remain unproved. Exact hidden branch reconstruction is one possible proof route; independently justified conservative sufficient intervals might substitute, so missing historical states do not establish interface infeasibility. The helper never enables ELIGIBLE. **STOP3, NOT_QUALIFIED, HOLD, A1/A2 unverified and 900 NOT_TESTED remain.** The next action is final scientific review and bounded Draft delivery for user/Chat review, with no simulation authorization implied.
