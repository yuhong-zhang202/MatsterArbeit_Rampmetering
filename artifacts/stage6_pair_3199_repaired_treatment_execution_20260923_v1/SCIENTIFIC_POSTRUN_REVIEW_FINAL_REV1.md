# Independent scientific post-run review — repaired PAIR3199 treatment

**Contract outcome: `NOT_EVALUABLE`**  
**Scientific review disposition:** `NOT_EVALUABLE` — Blocker/Major/required Minor = **0/1/0**  
**Confidence:** High for the contract-based disposition; Moderate for the physical explanation and its downstream implications.

## Context and question

Completed the required Context Preflight: `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`. Reviewed the bounded scan plan, the adopted Stage 6 exploratory witness contract, the v5 matched-input repair and its independent reviews, the exact FINAL card and prelaunch reviews, the engineering post-run integrity receipt, the data/lifecycle post-run review, and the earlier consumed treatment's `NOT_EVALUABLE` record. Stage 6 remains exploratory; the formal protocol remains unfrozen. The earlier treatment remains a separate immutable attempt.

The question is whether the preregistered pre-meaningful-merge trajectory gate justifies stopping before any post-R classifier or witness/no-witness interpretation. It does. This disposition does not infer whether P/S/L or Candidate A/C would have detected an event; those analyses were not run under the failed gate.

## Provenance reviewed

- Run/attempt: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`; execution UUID `b095cce4-baba-4c40-aa79-08b5e58b9ce1`.
- FINAL exact-card SHA-256: `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.
- Adopted contract SHA-256: `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- V5 input invariant report SHA-256: `509f1a46873b6922ce22e18f4100fa2dcb84a632d80ee9a014750efc6c857d54` (planned-input match: 1,558/1,558 common M/U/X; exactly R192 treatment-only).
- Treatment raw output manifest SHA-256: `f36f336473792c2af246abf75c3b7b2e9217abb537e7b42e15685e6af46b7173`; FCD SHA-256: `ac5b74632b6d445aea5d5dfc4d58b3cc4b38d379418483bc71c408daf3c94f89`.
- Data gate receipt SHA-256: `112d8721f3b7b524c21c3a9071a19e0eb19d70f226bc54d875eeaa3ae83275e1`.
- Data report SHA-256: `fcabdde57ceb07a181b0878007ebf2bbdf501d532f36555c9d7bdccad4a1c20e`; structured data review SHA-256: `554cbe2443cacdb93ce2393ae50d526fadbd4829573036e25e2962268dee27ca`.
- Engineering integrity report SHA-256: `d0db9324efd940985aae22ea76918cc734444440d255d1911c81ba5e353806c7`; engineering provenance receipt SHA-256: `d4c1d8eb600ebea1dd3dd693b16fbf949641e9bd5a169b8c9b70f892a78aac4c`.

The independent data review reports that all 25 manifest-inventoried payload/support files match their recorded hashes. Engineering records one authorized start, normal return code 0 at the 2,700 s horizon, 18/18 required output roles, and no retry. Run completion and raw integrity pass; these do not establish scientific eligibility.

## Scientific assessment

The v5 construction fixed the *planned input* contrast: common M/U/X identity, scheduled departure, route, vType and stored speedFactor records match, with R_flow.0–191 the only added demand. The post-run data review then compared realized M/U/X FCD observations by common vehicle and absolute second before the first observed R through-merge frame at t=591 s:

- 41,042/41,042 common vehicle-second keys were available in both runs; no unmatched or duplicate keys were reported.
- 40,844 tuples matched exactly; 198 (0.482%) differed. All differences were U records, affecting seven identities (`U_flow.53`–`U_flow.59`); M and X tuples matched throughout this interval.
- The first difference was `U_flow.54` at t=540 s, coincident with the first actual R departure/FCD record on `urban_in_0`. Differences persisted through t=590 s. Reported U position differences later reach roughly 20–40 m and include lane-label divergence.
- R first appears on the acceleration lane at t=587 s and first enters a through-merge lane / records the native merge lane change at t=591 s. The three-bin certain-entry exposure sequence confirms at t=660 s.

The timing matters: this is **pre-meaningful-merge exposure, but not pre-R activation or pre-R presence**. Calling it simply “pre-R divergence” would be imprecise. Its coincidence with R's first departure and shared source/approach location makes an R-related interaction plausible; the record does not establish whether the U displacement is a direct source-side treatment effect, another simulator interaction, or a measurement-level difference. Nor does it establish that it caused any later M change. Because the divergence occurs before the merge exposure whose effect the contract seeks to attribute, and its relevance to subsequent onset is unresolved, the two arms cannot support a clean merge-pressure attribution under the preregistered gate.

The exact-match fraction alone is not a pre-registered effect-size threshold and is not treated as one. The scientific basis for stopping is the specific, persistent, spatially substantial U divergence and unresolved alternative pathway, not an invented percentage cutoff. The card/contract explicitly required post-R witness analysis only after the pre-meaningful-R trajectory gate passed. It did not pass. Therefore stopping before locked P/S/L, Candidate A/C, event chronology, and causal alternative checks is methodologically consistent. **No inference is made about the presence or absence of a post-R State1 event.**

### Material finding — Major (1)

Realized M/U/X pre-meaningful-merge trajectory equivalence is not established: seven U identities diverge from the instant R first departs, for observations spanning the pre-merge interval. This leaves an R-source/approach pathway temporally prior to merge exposure unresolved. The required corrective action for this already authorized pair is to retain `NOT_EVALUABLE` and stop; no additional analysis or simulation is authorized by this review. User/supervisor confirmation is not required to preserve the preregistered conservative disposition. A new test or revised gate would require a separate decision and authorization; it is not recommended or initiated here.

No separate engineering finding is raised: the engineering report is limited to execution and raw integrity and passes that scope. No additional scientific blocker or required minor is identified.

## Mandatory measurement checks

1. **Measurement target — passed for the gate actually reviewed.** Target is exact FCD tuple equality `(x,y,pos,lane,speed,type)` for common M/U/X vehicle IDs at each absolute integer-second label, over t=0–590 s, ending before the first observed R through-merge frame. The reviewed measure is trajectory matching, not a whole-route traffic claim. The gate report does not compare departure delay or unfinished vehicles as part of this trajectory statistic; lifecycle is reported separately.
2. **Actual coverage — not fully verified.** The data review reports FCD labels 0–2699 and identifies observed R acceleration/through-merge transitions; engineering confirms the accepted network binding. The scientific review did not independently map every internal lane, branch, boundary coordinate or detector extent against the compiled network. Detector configuration/label completeness alone would not establish physical coverage of every relevant location.
3. **Omitted/duplicated observations — passed for the pre-merge key set and reported lifecycle census.** The data review reports 41,042 common M/U/X vehicle-time keys per arm in the comparison interval, zero one-arm-only keys, and no duplicate `(second, vehicle ID)` rows. Its broader lifecycle census reports 1,750/1,750 planned identities in vehroute/tripinfo/FCD and no unfinished vehicles. These statements are taken from the hash-bound data review; no second census was run here.
4. **Independent reconciliation — passed within the gate review's scope, with limitation.** The independent data reviewer reports direct comparison of immutable raw FCD and binds the raw manifest/FCD hashes and derived gate receipt. This scientific review did not independently recompute those rows. The contract's required raw re-computation of decisive P/S event bins and matched post-R intervals was not triggered because the pre-merge gate failed; no post-R aggregates or detector comparisons are endorsed.
5. **Regression protection — not applicable to this scientific disposition.** This review does not assess measurement-code tests. The v5 planned-input checker had separate 12/12 tests and independent reviews, but those tests do not validate the post-run trajectory-gate analyzer or detector extent. No claim about those broader regression cases is made.

## Final contract result and stop

**`NOT_EVALUABLE`** is the only supported allowed result for this repaired attempt. It is neither `RAMP_INDUCED_WITNESS_ESTABLISHED` nor `NO_WITNESS`. The justified bounded statements are: (a) the run completed with full reported lifecycle/raw inventory; (b) the planned common input binding passed; (c) M/X matched exactly in the reviewed pre-merge interval while seven U trajectories did not; and (d) the treatment-control pair therefore did not pass the preregistered pre-meaningful-merge gate. Nothing is concluded about locked event status, post-R M deterioration, or whether R can induce it.

The current single-start authorization is consumed. This review recommends no rerun, retry, demand scan, or B/C preparation. Stop after recording this review; preserve all prior cards, raw data, classifier outputs, contract text and historical dispositions unchanged.
