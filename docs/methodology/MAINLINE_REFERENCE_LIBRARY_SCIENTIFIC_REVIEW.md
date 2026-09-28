# Mainline reference-state library — implementation review record

Date: 2026-09-22. Disposition: **PASS_WITH_LIMITED_REQUIRED_TRACEABILITY_CAVEATS**.

This is the final independent read-only scientific review of the offline implementation. It does not approve classifier integration, a formal protocol, a new simulation, a baseline, or a physical normal-state claim.

## Reviewed artifacts and hashes

|Artifact|SHA-256|
|---|---|
|selector|`6635b0cbbdd4afa1ce0dad0c3741e73064e4279434bef626c4e9eff14c878b50`|
|REPORT.md|`620155da1729295d38a08f79d3486ebd2832363b4238fddb44e12a52ddf5490b`|
|reference_library_receipt.json|`e9ab9cedcbb9fb82ce4c56be917a0cd65349f32a278325c90ae301e7368453d7`|
|raw_reconciliation_receipt.json|`0a39f24787584d40317b2e4b6f77be3edb92915b8d07ee7c20bf222e50863058`|
|reference_candidate_ledger.csv|`aaeed9d7f8ec56548b4200b5758e7d433fa168445ce6eff39857fcdcf13c25a2`|
|fixture receipt|`72f142776bc9c5f30a74bc021685e2a88a3231e02dcbc25152449cc6162917e5`|

## Findings

The implementation now derives cell/lane length from the bound network shapes, computes both M and M+R spatial density, validates XML parsing, exact 0–2699 labels, duplicate `(time,vehicle)` keys, missing fields, speedFactor and unexpected M lanes fail-closed, binds raw output-manifest and run receipts, and emits independent lane0/lane1/pooled memberships. Fixtures call the shared period-status helper used by candidate selection. The independent data audit reconciled one A0 and one M3350 cell/block within `<5e-11`; this is selected-slice, not exhaustive, validation.

Both runs produce 704 candidate periods (2 runs × 22 cells × 16 blocks), 2,112 ledger rows (704 per lane scope), and zero accepted pooled periods. The machine-readable Candidate-C disturbance catalogue is absent, so every period correctly carries `DISTURBANCE_MASK_UNKNOWN`. This is a data-contract outcome, not evidence of normality, congestion, onset or breakdown. Revision03 supplemental metrics remain excluded.

## Caveats before any non-empty bank is interpreted

The current empty bank is safe to preserve. Before a future implementation accepts any bank member, exact route/additional/config/TLS snapshots must be bound in the receipt and the summary must retain lane-specific and M+R dimensions. The selected-slice reconciliation does not certify every row. These are traceability conditions for future scientific use, not defects in the present conservative zero-acceptance result.

No SUMO/netconvert/TraCI, P/S/L reclassification, demand selection, geometry/controller/input change, or formal-protocol change occurred. Stage 6 remains `PARTIAL`; O2 remains `NOT_RESOLVED`; the formal protocol remains empty/unfrozen.
