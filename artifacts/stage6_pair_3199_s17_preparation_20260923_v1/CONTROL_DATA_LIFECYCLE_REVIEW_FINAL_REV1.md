# PAIR_3199_CTRL_S17 — raw data and lifecycle review

**Overall review: NOT_EVALUABLE** (Blocker/Major/required Minor = **0/0/1**). **Raw integrity/lifecycle processing: PASS.** **`LOW_R_BACKGROUND_ACCEPTABLE`: NOT_EVALUABLE.** Confidence is High for hashes, lifecycle joins, and locked labels; Moderate for the background adjudication.

## Scope and provenance

Read-only review of exactly `PAIR_3199_CTRL_S17`; no treatment outputs inspected. Exact card SHA-256 `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`; execution capture records one SUMO start, return code 0, 24.881003 s, no retry, and no further analysis at capture. Raw `output_manifest.json` SHA-256 `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`. Independent engineering/data/scientific final prelaunch records are bound and PASS 0/0/0.

The exact card also retains a nonempty `required_unresolved_prelaunch_items` array naming those same three reviews. This conflicts with the hash-bound final prelaunch disposition and review receipts. It is recorded as required minor DM-01; this review does not rewrite the card or infer whether it is merely stale metadata.

The prior locked methodology, locked analyzer, R04 adapter and witness criteria were read and hash-bound. Locked analyzer method SHA-256 `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`; analyzer SHA-256 `78f001b7909bdda6797eae6aab5bf6bf0dd70bce83262d8f2619c3fa71149c55`. The existing R04 adapter was applied offline to immutable raw using pair-specific path/hash bindings and serialization-only compatibility handling. Final successful result is under `data/processed/stage6_pair_3199_s17_control_postrun_20260923_v4/`; previous failed processing-attempt directories v1–v3 were preserved and are not analysis results.

## Integrity and lifecycle

All 18/18 required output roles and all 25/25 manifest-listed files have matching size/hash; XML parses and declared grids are complete. FCD covers exact integer labels 0–2699 and 111,883 unique time-ID observations. The 1,558 scheduled identities reconcile across route/tripinfo/FCD with no missing, unexpected, or duplicate identities. The integer-SUMOTime schedule and two-decimal `departDelay` reconciliation passed for all number-flow departures.

| Class | Scheduled | Inserted in source window | Late / never inserted | Arrived | Unfinished | Depart delay min / median / max (s) |
|---|---:|---:|---:|---:|---:|---|
| M | 1333 | 1333 | 0 / 0 | 1333 | 0 | 0 / 0.5 / 0.875 |
| R | 0 | 0 | 0 / 0 | 0 | 0 | explicit `PASS_ZERO` |
| U | 150 | 150 | 0 / 0 | 150 | 0 | 0 / 0 / 0 |
| X | 75 | 75 | 0 / 0 | 75 | 0 | 0 / 0 / 0 |

All 1,333 M identities appear in FCD upstream (23,223 samples), core (23,654), and downstream (18,861); 14,237 core M samples fall in [540,1440). The control has no R source or observed R. It therefore establishes zero-R exposure only; it cannot establish treatment-side R entry or the matched pair effect.

## Locked state analysis and fixed screens

The unchanged locked classifier yields P=`NO_QUALIFYING_EVENT`, S=`NO_QUALIFYING_EVENT`, L=`NO_QUALIFYING_EVENT`, Candidate A=`NO_SPATIAL_CANDIDATE`, and Candidate C=`EARLY_WARNING_PRESENT_NOT_STATE1`. The locked event grid is complete (22×3×90); it retains 42 single-bin L short candidates overall, 20 in core cells. Core warning starts occur at 720, 750, 990, 1170, 1380, 1410 and 1470 s; physical episode count remains `NOT_ESTIMATED`.

Fixed screens remain failed: PRE has 3/30 PASS and 27/30 FAIL; control [540,1440) has 17/150 PASS and 133/150 FAIL. Most failures include measured speed ratio below 0.85; later windows also overlap locked disturbance masks. These outcomes retain the legacy fixed-screen/F5 meaning; they are not recoded.

There are repeated spatially distributed low-ratio patterns beyond isolated warnings. In pooled core cell-bins, mean normalized speed ratio is 0.877 in [540,720) and 0.847 in [720,1500), with M density rising from 15.14 to 15.99 veh/lane-km. Lane0 has an eight-bin (240 s) sub-0.85 sequence in cell13 from 780 to 1020 s; pooled core has a five-bin (150 s) sequence in cell15 from 360 to 510 s. Across the demand interval, sub-0.85 observed core cell-bins are 128/245 for lane0, 66/245 for lane1, and 83/245 pooled. This is not a State1 classification: locked P/S/L remain negative and Candidate A is absent. It is nevertheless unresolved evidence against treating P/S/L negativity as proof that the low-R background is free of sustained collective self-congestion.

## Artifact ledger

- **Insertion starvation:** no affirmative evidence; all classes inserted in-window, M maximum departure delay 0.875 s, no late/never-inserted or unfinished vehicles.
- **Downstream receiving blockage:** no affirmative signal in observed downstream taps: M continues through 20 m/200 m E1 detectors; active-window mean speeds are about 27–29 m/s, and summary mean waiting is zero. This bounded tap evidence does not prove absence beyond observed coverage.
- **TLS:** `ramp_mid` is `A_OPEN/G` for all 2,700 labels; no direct mainline TLS restriction is indicated by the bound route/lane observations. `urban_tls` follows its configured technical-placeholder program.
- **Geometry/lane mapping:** accepted network hash matches; route/type checks pass; no M auxiliary, unexpected-lane, or out-of-domain FCD samples. No affirmative geometry mismatch found.
- **Measurement/parser:** all required file hashes, XML, FCD labels, detector grids, identity joins, and locked event-source completeness checks pass.
- **Residual scientific alternative:** the persistent/recurrent low-ratio pattern is not assigned a cause by this control-only review. It may be localized/recurring merge interaction or a more collective self-congested state; available locked positive rules do not qualify an event, but they do not resolve this new low-R background criterion.

## Decision

Do **not** assign `LOW_R_BACKGROUND_ACCEPTABLE` on this review. The correct current value is **`NOT_EVALUABLE`**: raw/lifecycle integrity passes, but the bounded no-self-congestion adjudication is not resolved. P/S/L-negative alone is insufficient; fixed PRE/control screens fail; Candidate C and long/repeated sub-0.85 evidence require independent scientific adjudication under the unchanged contract. This review does not authorize or recommend launching treatment.

No classifier, threshold, geometry, demand, vehicle behavior, or protocol was changed. Raw files remain immutable. SUMO starts during this analysis = 0; TraCI = 0; netconvert = 0; treatment inspected = no; new run created = no.

## Outputs

Derived tables and complete evidence ledger are in `data/processed/stage6_pair_3199_s17_control_postrun_20260923_v4/`. Hash-bound reviewer receipt: `CONTROL_DATA_REVIEW_HASH_RECEIPT_FINAL_REV1.json` in the pair package. The first adapter attempts v1–v3 are preserved as processing failures and are not substituted for the completed v4 application.
