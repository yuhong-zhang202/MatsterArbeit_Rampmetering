# Stage 6 3350 Reference-Offset Analysis — Scientific Review

Date: 2026-09-22  
Disposition: **PASS — OFFLINE_DESCRIPTIVE_ONLY**

## Scope

The review covered the M3350 raw-FCD offset analysis, its locked Candidate-C inputs, the v2 reference-library hierarchy, output hashes, weighting sensitivity and independent reconciliation. No SUMO or classifier run occurred.

## Accepted interpretation

- Primary reference: same-run, same-cell, same-lane M3350 screened support.
- Secondary reference: fixed same-cell/same-lane A0 support only where M3350 support is absent.
- No cross-cell donor and no pooled reference synthesized from one lane.
- Headline values are event-equal means of event-level 30 s-bin means; `weighting_sensitivity.csv` supplies overlap-bin-equal sensitivity values.
- Independent raw XML reconciliation covers one lane1 same-run event, one lane0 A0-fallback event and one pooled unknown event; all 9 checks pass.

## Findings

Lane1 has complete reference-supported evidence over the 45 Candidate-C events: event-equal mean speed offset −1.519 m/s, ratio offset −0.0597, M density offset +2.399 veh/lane-km and M+R density offset +2.206 veh/lane-km. The overlap-bin-equal sensitivity is −1.713 m/s, −0.0629, +2.455 and +2.247 respectively. Lane0 has A0 fallback support only in cells 13 and 17; cells 14–16 remain `UNKNOWN`. Same-bin lane differences are descriptive target-run contrasts, not normal-state comparisons.

Candidate-C cell episodes last 30–180 s. These are warning-episode durations only, not State 1 or physical queue durations.

## Separate conclusions

**State:** M3350 contains persistent local deviations from the screened high-mobility context, most defensibly on lane1 and partially on supported lane0 cells. This does not establish validated normal-state deviation, State 1, breakdown, capacity drop or a metering opportunity.

**Transition:** A complete normal → sustained deterioration transition is not established. Warnings begin at 270 s and are intermittent across cells, with no independently validated normal pre-state or continuous network-level worsening sequence.

## Limitations

Single seed, correlated cell episodes, incomplete lane0 donor support and no formal normal-state calibration. The analysis must not change P/S/L, Candidate C, the reference rule, formal protocol, O2 or Stage 6 status.

Evidence: [analysis report](/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/data/processed/stage6_3350_reference_offset_20260922_v1/REPORT.md), [analysis receipt](/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/data/processed/stage6_3350_reference_offset_20260922_v1/analysis_receipt.json), [independent reconciliation](/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/data/processed/stage6_3350_reference_offset_20260922_v1/offset_independent_reconciliation.json).
