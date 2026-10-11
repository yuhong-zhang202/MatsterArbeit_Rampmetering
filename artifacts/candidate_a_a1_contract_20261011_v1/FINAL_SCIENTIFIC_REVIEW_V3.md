# Issue #8 final scientific review — V3 source/data checkpoint

2026-10-11. Read-only project scientific_reviewer `/root/issue8_science`; parent records the advisory response faithfully. **PASS_FOR_BOUNDED_UNRESOLVED_A1_DERIVATION_AFTER_V3**, subject to actual delivered-commit clean-checkout verification. No unresolved Blocker/Major/required Minor remains in this bounded delivery. This is not user acceptance, A1 safety approval or execution authorization.

## Context and scope

Context Preflight covered AGENTS and scientific-agent instructions, current PROJECT_STATE, DECISIONS, WORKLOG, empty/unfrozen EXPERIMENT_PROTOCOL, Issue #8, upstream PR #5/#7 latest reviews and this source/data package. D-018 Stage 6 closure is preserved; D-019 is historical development authorization. This task is source/static/offline only. STOP3, Candidate A NOT_QUALIFIED, HOLD, unknown highest qualified rate and 900 NOT_TESTED remain. SUMO/TraCI starts and refused-red movements: zero.

Reviewer independently inspected event/source excerpts, specification, proof and coverage ledgers, all 42 V3 input-file hashes, six final data-file hashes, and the V3 data receipt. All matched. Its own read-only numerical probes accepted 32766 and quotient32766.999, rejected32767 and speed1e11, and matched all 42 V2/V3 mapping rows. The data analyst actually ran 33 unit tests/public audit and 10 independent probes. No native C++ build, movement, compiled-binary equivalence or future safety was checked.

## Findings and reconciliation

- Required Minor: finite Python arbitrary-precision arithmetic exceeded an established native `int steps` conversion/`steps+1` domain. V3 now safely truncates the nonnegative quotient and restricts steps≤32766 using the C++ minimum signed-int guarantee, without guessing compiler width. Double-first multiplication is not subjected to a fictitious integer-square limit. Boundary/above-domain tests and independent probes passed. **Addressed.** This is an offline arithmetic domain, not a physical safety cutoff.
- Prose Minor: “no compiler activity” was too broad when Python py_compile ran. Corrected to no native C++ build/execution. **Addressed.**
- Earlier data-review numerical failures and V2 manifest-build/3 ERROR checkpoint remain preserved, with exact historical source bytes. They were technical offline defects, not SUMO failures or new traffic observations.

## Eight acceptance checks

| # | Scientific review of bounded evidence |
|---|---|
| 1 | PASS: pinned source and input identities; event→planning→DriveProcessItems→finalization→traversal/insertion timeline is precisely limited. Actual full A07 branches remain unknown. |
| 2 | PASS for Issue-allowed unresolved delivery: tri-state specification, premises and necessity/sufficiency limits disclosed. Helper has no ELIGIBLE path. |
| 3 | PASS as auditable obligations/exclusions: saved/static scope and UNKNOWN are explicit; complete future affected population/receiver coverage is unproved. |
| 4 | PASS: 42 unique =27storage+15ingress; sole R_flow.1 old refusal; no fabricated red step. |
| 5 | Source/data PASS: adversarial suite, source-domain correction, real 33 PASS and hashes; delivered clean checkout remains parent gate at this checkpoint. |
| 6 | PASS: P0–P10 obligations, minimal separately authorized static observability/proof-gap closure and STOP conditions. |
| 7 | PASS: 536 protected hashes unchanged; 0 starts; historical failures and STOP3/NOT_QUALIFIED/HOLD/900NOT_TESTED retained. |
| 8 | PASS: source mechanism, observed, conditional arithmetic and unknown states separated; no actuator qualification claimed. |

## Five measurement checks and practical limits

| Check | Result and scope |
|---|---|
| Target | PASS for saved42guard/saved1206s/sixwindows, not route cost or formal rate. |
| Coverage | PASS only saved population and exact net1controlledlink/foes0; future world/internal receiver not proved. |
| Omission/duplication | PASS42sets,27+15,window counts[6,0,0,0,0,0],partialC=.5/E0/N1,unobservednull/blank,0cycles. |
| Independent reconciliation | PASS original snapshot old formula, independent finite sums/inverse and data receipt; no public raw-phase reconstruction. |
| Regression | PASS33 methods including finite/native-int domain; cannot substitute for native safety or enable ELIGIBLE. |

## Decision and handoff

**UNRESOLVED_NEEDS_EVIDENCE / NOT_IMPLEMENTABLE_YET** is supported. Neither interface infeasibility nor offline contract readiness is proved. Complete entrants/affected world, native seen/action/modes/devices, joint ordinary-speed bounds, follower safety and receiver/leader/secureGap/reservations remain next-work blockers, not concealed delivery failures. Exact hidden state could be replaced by a rigorously proved sufficient interval; no such joint proof exists yet.

After the clean-checkout gate, submit this bounded Draft for user/Chat review. Proposed next task is static proof-gap closure. A runtime gate implementation or new-identity R300 seed17 smoke each requires separate explicit authorization. No new research decision, phase closure, rate qualification or formal experiment follows.
