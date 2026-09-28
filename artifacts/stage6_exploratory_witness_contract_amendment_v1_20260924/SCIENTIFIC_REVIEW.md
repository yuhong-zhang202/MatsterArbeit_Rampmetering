# Independent scientific review — Stage 6 witness contract Amendment V1

**Disposition:** PASS for publication as a versioned, optional Stage 6 exploratory methodology amendment. Blocker / Major / required Minor = **0 / 0 / 0**. Confidence: **High** for the causal time structure and contract boundary; **Moderate, unverified** for the physical explanation of the seven U-vehicle differences.

**Reviewed exact document:** `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_AMENDMENT_V1.md`, SHA-256 `89a8c30df302620a5d7d2fa1e6fb7f4cde350a7321ba270005a6d008605ed719`.

**Reviewer route:** independent project `scientific_reviewer`, read-only. The reviewer completed the project Context Preflight: `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/WORKLOG.md`, the parent witness contract, the previous causal review, and this draft. `docs/EXPERIMENT_PROTOCOL.md` is empty and the formal protocol is not frozen. The reviewer did not inspect repaired-treatment t>=591 P/S/L, Candidate A/C, M-deterioration, or witness outcome; did not run SUMO or edit files.

## Findings

1. The four gates distinguish the pre-treatment period (`t<540`), post-treatment shared source period (`540<=t<591`), observed freeway-entry/exposure accumulation (`591<=t<660`), and earliest T3 confirmation (`t>=660`). The first observed R through-lane entry at 591 is not treated as T3. Three complete, positive-certain 30 s bins can establish T3 no earlier than 660.
2. M must remain matched through the pre-entry period. X is required to remain matched only if independently shown to be outside the R treatment pathway. U divergence after R activation is retained as a possible treatment-pathway response; it is neither automatically a confound nor established as a physical effect. Source insertion, randomness, lane/route mapping, measurement and downstream explanations remain mandatory later checks.
3. The amendment discloses that it was proposed after the seven-U divergence was observed. Use on the existing raw is explicitly `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS`. The parent contract, original `NOT_EVALUABLE` histories, locked classifier thresholds, event window and formal protocol remain unchanged.
4. Review and explicit user adoption of the amendment, plus a frozen raw-only analysis plan, must precede post-591 outcome inspection. This PASS supports scientific adoptability; it does not itself adopt the amendment or change the pair's disposition.

## Limits and next permissible analysis

This was a methodology review, not a raw-data or measurement revalidation. Actual spatial coverage, missing/duplicate samples, independent t<591 raw reconstruction and the physical cause of U divergence remain unverified here. After user adoption, the existing hash-bound raw can in principle support a staged **offline** sensitivity re-evaluation: independent data, engineering and scientific pre-outcome gates first, then locked outcome analysis only if those gates pass. No new SUMO run is intrinsically needed. If existing raw cannot exclude a material source, insertion, stochastic, downstream or measurement alternative, keep `NOT_EVALUABLE` and seek a separate decision before any new design or run.

**Required issues:** none. **Result analysis performed in this review:** none.
