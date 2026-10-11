# Issue #6 — independent scientific review

**2026-10-11. Final disposition: `PASS_FOR_BOUNDED_ISSUE6_INVESTIGATION`; unaddressed Blocker/Major/required Minor 0/0/0.** This records the read-only `scientific_reviewer` `/root/issue6_science` findings returned to the primary agent. It is an advisory scientific/method review of the investigation, not user acceptance, supervisor confirmation, a replacement safety contract, or Candidate A qualification.

## Scope and context

The reviewer performed the required Context Preflight: `AGENTS.md`, current `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, empty/unfrozen `docs/EXPERIMENT_PROTOCOL.md`, live Issue #6 and bounded Issue #2/#4 and PR #5 status. It read the draft [safety-contract reassessment](../../docs/development/CANDIDATE_A_SAFETY_CONTRACT_REASSESSMENT.md), [engineering review](engineering/ENGINEERING_REVIEW.md), [data review](../../data/processed/candidate_a_safety_contract_20261011_v1/DATA_REVIEW.md) and bound A07/V3 evidence. No reviewer file write, SUMO/TraCI start, contract change or research decision occurred.

## Findings and disposition

The draft's current-contract STOP3 boundary, A1 as only a priority for *further derivation*, A2 without an invented numerical bound, and HOLD/NOT_QUALIFIED/900-not-tested/formal-protocol limits agree with the engineering and data evidence. No Blocker or Major finding. Two minor completion points were identified: the candidate-specific A1/A2 source-vs-inference mapping was thin, and the final review needed an accurate saved link. The source/inference ledger was added to the main report before this record; this file supplies the review link. These actions address the two findings. The reviewer did not certify an A1/A2 eligibility predicate or an implementation.

The reviewer kept execution, measurement and qualification separate: the existing prefix stopped under STOP3; its saved prefix is boundedly measurable; there is **no** complete safety or service qualification. The rejected red step, all-vehicle native branch inputs, receiver/foe completeness, repeated cycles and sustained rate remain unobserved or unverified. A future alternative contract and new minimal technical smoke require separate user/Chat approval and engineering/data/science gates. Robert has not confirmed this proposed contract direction.

## Five measurement checks

| Check | Result and limit |
|---|---|
| Target definition | Passed for distance in metres, 42 guard states, C/applied C/E in vehicle equivalents and N as stopline crossings, bounded to 1206 s prefix and six 300 s planned windows. No whole-run cost inference. |
| Actual coverage | Passed only for already executed prefix; engineering mapped 204.49 m storage, 113.08 m ingress, 81.98 m receiver and one controlled link. Future A1/A2 enumeration/eligibility not verified. |
| Omission/duplication | Passed for saved prefix: 42 unique states and 42 matched witnesses; five unobserved windows remain null, not zero. Prior 4050-cohort accounting remains historical and is not used to infer post-stop outcomes. |
| Independent accounting | Passed for guard arithmetic, phase and saved prefix: data analyst recalculated all 42 margins. Refused red motion and physical secure-gap response were not independently observed/recomputed. |
| Regression protection | Existing V3 missing-value and original guard checks passed for their scopes. A1/A2 have no implementation or regression tests yet; required future adversarial boundaries are listed in the report. |

## Final readback boundary

After the initial review, a read-only offline A07/V3 audit script and five tests were added. They reproduce existing measurements only and cannot validate an unexecuted red step or a proposed A1/A2 rule. The primary agent and reviewer independently ran all five tests and the audit (PASS, matching the saved receipt). Final readback confirmed script scope, report links, all seven Issue answers and the review chain. The reviewer briefly flagged an apparent tagged-source line mismatch from a web viewer; direct GitHub Contents API bytes and the engineering source readback resolved it: `MSVehicle.cpp` has 381688 original bytes, SHA-256 `8499ebe445906b19395d5c70945b012f320a439327e9cb3c20f0abd26d15a6a4`, with physical lines 125/2728/2871 as cited. The web viewer compressed/omitted blank lines and displayed different line numbers. No tracked evidence changed in this check. This review must not be cited as approval to execute the next Issue.
