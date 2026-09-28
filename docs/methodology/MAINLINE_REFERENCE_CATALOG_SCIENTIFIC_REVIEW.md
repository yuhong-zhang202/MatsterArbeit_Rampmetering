# Mainline Reference Catalogue and Rerun — Scientific Review

Date: 2026-09-22  
Scope: offline A0 / LOC_M3350 Candidate-C catalogue and unchanged reference-library rerun  
Disposition: **PASS_WITH_LIMITED_EXPLORATORY_SCOPE**

## Review basis

The reviewer inspected the project context, locked method/specification, A0 and M3350 application receipts, v2 catalogue, receipts, ledger, audits and report. No SUMO or classifier execution was performed during review.

## Findings

1. Candidate C provenance is correct. A0 contains 26 and M3350 contains 45 source events. Both are exactly the locked `profile=L`, `is_merge_core=True`, `low_speed_bins>=1` subset and bind the reviewed method hash, analyzer hash and application receipt. The known `revision03` supplemental diagnosis is not used.
2. The catalogue is cell-level, not lane-level. Every row therefore reports `lane=pooled` and `lane_assignment_status=NOT_AVAILABLE_FROM_LOCKED_C`; no per-lane trigger is inferred. Source IDs and catalogue IDs are unique, complete and half-open 30 s boundaries are valid.
3. The reference rule was not changed. The existing P/S/L mask, fixed 100 m cells, 30 s bins, fixed 90 s blocks, 0.85 mobility threshold, population checks and post-disturbance exclusion remain in force; the complete C catalogue only replaces the prior missing-mask state.
4. The independent structural/hash audit passes. The independent numerical audit recomputes one accepted and one `LOW_MOBILITY`-rejected pooled block for each run directly from raw FCD, vehroute and compiled network, including lane/pooled speed ratio, M density, M+R density, disturbance-mask reason and final status. All four slices match the ledger.
5. Route/demand, additional, SUMO configuration and TLS-output snapshots are hash-bound in `input_snapshot_manifest.json` and referenced by the library receipt.

## Result interpretation

The unchanged screen yields 704 pooled candidate periods per run and 2,112 ledger rows. A0 has 82 accepted pooled periods (7,380 s); M3350 has 38 (3,420 s). These are **screened high-mobility reference contexts**, not proof of normal traffic, free flow, absence of disturbance, State 1, breakdown, capacity drop, or a formal thesis baseline. They are single-seed same-run correlated periods.

## Remaining limitations

The bank is exploratory and diagnostic only. Any later donor use requires explicit supervisor/protocol authorization, matched-condition validation and an independent justification that the screened context is scientifically comparable to the target analysis. The result does not resolve O2 or Stage 6.

## Evidence

- Catalogue and rerun: `data/processed/stage6_mainline_reference_library_20260922_v2/`
- Structural/hash and numerical audit: `data/processed/stage6_mainline_reference_library_20260922_v2/data_audit_review.json`
- Independent raw slices: `data/processed/stage6_mainline_reference_library_20260922_v2/independent_numeric_reconciliation.json`
- Input snapshots: `data/processed/stage6_mainline_reference_library_20260922_v2/input_snapshot_manifest.json`

Subagent disposition: the scientific reviewer initially identified two required traceability fixes (independent numerical slice verification and complete input-snapshot binding); both were completed and rechecked before this PASS disposition.
