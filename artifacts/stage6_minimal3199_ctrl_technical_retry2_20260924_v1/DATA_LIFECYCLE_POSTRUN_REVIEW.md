# Data / lifecycle post-run review — MINIMAL3199_CTRL_S17_TECH_RETRY2

**Disposition:** `PASS_DATA_LIFECYCLE_WITH_RETAINED_CANDIDATE_C_WARNINGS`  
**Confidence:** High  
**Findings:** 0 blockers / 0 major / 0 required minor; 2 non-blocking review notes.

## Scope and provenance

Reviewed only the exact retry2 control raw. Raw files were immutable. Bound card SHA-256: `b387a750f9f41fe7439d79ead7133fc07ac817fe8da497a8e045433a4accee5a`; execution-manifest SHA-256: `551fdfbe78530662f2a437436d8a36813902d5728ac88b03a7a316382d7bca9a`; engineering post-run receipt SHA-256: `3c7d798178dbb2bdfbddf732f88356621025c25a092167cf6f86dad54e1b117c`; raw output-manifest SHA-256: `07cd3cd1707e3717f9401f3e164a932cb6c10196af1461f267869f1d582e5e5e`; execution receipt SHA-256: `f9f783f19cc61d342de09ab7dc6172e56645b7e1604d7447ad6e0582a7bd2348`. The processing manifest verifies all 19 derived artifact hashes. Locked method SHA-256 is `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`; locked analyzer SHA-256 is `78f001b7909bdda6797eae6aab5bf6bf0dd70bce83262d8f2619c3fa71149c55`.

## Lifecycle and exposure

The exact condition is qMain 3199.2 veh/h, seed 17, R=0, U=0, X=0, with 1,333 materialized M vehicles. All 1,333 M identities are in vehroute/tripinfo; 1,333 departed and arrived before 2700 s; zero are unfinished, boundary-censored, or missing. Actual departure delay relative to each materialized desired departure is min/median/max 0 / 0.5 / 0.875 s. Input-to-output identity, route, vType and speedFactor match 1,333/1,333 each; each actual departure was reconciled to its materialized desired departure, with insertion delay recorded separately. R/U/X are explicit zero from the card and demand identities; none appears in route, tripinfo, or FCD records.

FCD has all 2,700 integer-second labels (0–2699), 97,723 M vehicle-time samples and all 1,333 M identities; each reaches the locked core observation region. Nine of nine E1 roles have 90 continuous 30-second intervals each. The two downstream E1 detectors record 1,333 entries each. Both E2 roles have 90 complete intervals and zero entries, consistent with no ramp/shared-approach traffic. Both TLS IDs have complete 2,700-label coverage; `ramp_mid` is green throughout. All 1,333 M vehicles finish by 1576 s.

## Locked classifier and retained warnings

P, S and L each return `NO_QUALIFYING_EVENT`; Candidate A returns `NO_SPATIAL_CANDIDATE`. Candidate C returns `EARLY_WARNING_PRESENT_NOT_STATE1` with 20 merge-core warning rows. The locked analyzer contains 42 L-profile low-state rows; each is one 30-second bin (`SHORT_LOW_STATE_CANDIDATE`), so none reaches the locked two-bin L duration. Some same-bin patches span adjacent cells; they are retained in `locked_candidate_events.csv`. No threshold or classifier setting was changed.

The separate high-mobility/reference screen is `FAIL` in 160/180 rows. That stricter screen is not relabeled PASS and is not the R=0 eligibility requirement in the adopted minimal plan. It documents the low-speed-ratio background that the future treatment comparison must account for.

## Artifact limitations

No source/insertion artifact is evident: every planned M identity inserted, delays are at most 0.875 s, and every M vehicle arrived. No downstream failure is evident in vehicle completion or downstream E1 passage. `queues.xml` has complete timestamps but empty `<lanes/>` elements; therefore it supplies no queue-occupancy series and cannot independently establish absence of queues. The repeated short Candidate C patches remain for scientific adjudication and must not be erased or described as a clean normal baseline.

## Analysis implementation note

The exact locked analyzer source and method hashes were verified. The analysis reused its unchanged calculations and thresholds. In-memory format adapters handled the R02 run-folder naming, materialized vehicle schedules, and a CSV field added by the adapter exporter; they did not alter P/S/L or Candidate A/C logic. This is disclosed in the JSON receipt so the source adapter's own hash does not misrepresent those call-site adaptations.

## Interpretation boundary

The data support adequate M exposure, complete lifecycle/measurement, explicit zero R/U/X, and no locked sustained P/S/L event. This control is **not** certified as a clean high-mobility baseline. The minimal plan does not define the older `LOW_R_BACKGROUND_ACCEPTABLE` label, so this review does not assign it. No treatment or witness conclusion is available from this control alone.

Processed outputs: `data/processed/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/r04_locked_offline_analysis_v8`.

## Superseded analysis snapshots

Seven partial processing snapshots (`r04_locked_offline_analysis` and `_v2` through `_v7`) were preserved during R02/materialized-demand adapter diagnosis. They are non-authoritative and are not used for the reported findings; `r04_locked_offline_analysis_v8` is the complete analysis output. No raw files or earlier outputs were overwritten or deleted.
