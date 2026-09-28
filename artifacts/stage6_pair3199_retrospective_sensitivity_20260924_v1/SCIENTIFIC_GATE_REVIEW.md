# Independent scientific review — Gates A/B

**Disposition:** Gate A passes; Gate B does not clear. Stop this sensitivity analysis with `NOT_EVALUABLE`. Do not proceed to Gate C or D. This is not a witness or no-witness finding.

**Required issue:** the U/source/insertion/RNG alternatives remain material and unresolved for later M attribution. Blocker/Major/required Minor: **0/1/0** (one Major: Gate B cannot clear). Confidence: **High** that Gate B is not cleared under the adopted amendment; **Moderate** about the physical mechanism behind U divergence.

## Gate findings

- **Gate A (`t<540`): PASS.** Independent data review found 37,333 common M/U/X vehicle-second records with exact tuple equality and no unmatched sample keys. The count/status lifecycle supplement confirms all planned vehicles were loaded, inserted and arrived, with no terminal unfinished/waiting vehicles or teleports. It did not compare arrival times.
- **Gate B M: PASS.** All 3,243 common M vehicle-second records match.
- **Gate B X:** 178 tuples match descriptively. X is not verified outside the R pathway: its route crosses the same `urban_tls` on a conflicting signal link used by R. This does not show X divergence or prove an effect, but exact equality cannot certify an unaffected negative-control stream.
- **Gate B U:** 198 differing tuples across seven identities begin at t=540, coincident with R's first actual departure and same-lane presence near the first U difference. This supports a possible R-related source/approach interaction. Available evidence does not distinguish physical treatment response from insertion-order, stochastic/RNG or source-queue mechanisms. Those could affect later M attribution independently of freeway merge exposure. The amendment requires stopping as `NOT_EVALUABLE` when a material source, insertion or randomness alternative remains unresolved.

No affirmative geometry or measurement defect was identified by the engineering inspection. The result is uncertainty about mechanism, not proof of a technical defect. The engineering summary was subsequently written into the hash-bound companion [engineering review](ENGINEERING_GATE_REVIEW.md); its scope and sources are listed there.

## Premature exposure-only inspection

An engineering-only review opened treatment records labeled 591–659 and checked interval coverage before A/B signoff, contrary to the frozen sequence. This process deviation must remain disclosed. It does not change the A/B evidence or disposition: the data analyst stopped before reading label 591, and this scientific reviewer did not inspect exposure values or any t>=660 outcome. The premature exposure check cannot be used to bypass Gate B.

## Review boundary

The reviewed inputs were the adopted Amendment V1, the parent contract, frozen analysis plan, hash-bound Gates A/B data review, provenance summary, U-difference table, lifecycle supplement and engineering findings. No t>=591 record was inspected in this independent scientific review. No P/S/L, Candidate A/C, M deterioration or witness analysis was performed. No simulation was run.

**Next step:** retain `NOT_EVALUABLE`; preserve prior historical dispositions. No SUMO rerun is implied.
