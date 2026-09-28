# MAINLINE REFERENCE SELECTION SPEC — proposal v1

Date: 2026-09-22. **PROPOSED / OFFLINE DIAGNOSTIC ONLY / NOT CLASSIFIER INTEGRATION AUTHORIZATION.**

Purpose: deterministically create screened high-mobility reference banks and contextual comparison tables. No output of this specification is a P/S/L classification, physical breakdown verdict or next-run release. `NORMAL_STATE_NOT_VALIDATED` accompanies every bank until independent calibration is approved. The method proposal explains rationale and limitations.

## 1. Eligible inputs and frozen manifest

Only existing `TV_A_S17_attempt1` under `data/raw/stage6_targeted_validation_20260920_v1/` and `LOC_M3350_S17_attempt1` under `data/raw/stage6_baseline_localization_20260921_v1/` are in scope. A0 supplies the only external bank; 3350 cannot calibrate A0 or serve as its external donor. Same-run banks are descriptive, not independent replicates.

Bind raw manifests, FCD, vehroute, tripinfo, all used E1 files, compiled network, route/additional/config snapshots, locked method/analyzer/config, original event/early-warning outputs and this spec by SHA-256. Network must equal `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. Check open TLS, vehicle behavior/type, sensing, route and timing compatibility; only declared qMain and stochastic realization may differ. qRamp/qUrban/qX fixed at720/360/180 veh/h. No old-geometry or controlled run. Missing/conflicting provenance yields `INPUT_NOT_VERIFIED`, not automatic inclusion.

## 2. Preprocessing and geometry

Raw immutable; future derived files go to a new versioned `data/processed/` directory and tables to a new `results/tables/` directory. Do not overwrite history. Validate exact 0–2699 labels, duplicate (time,id), M/R/U/X route joins, positive precise vehroute speedFactor, finite speed/x, lane whitelist and complete XML. Use vehroute, not rounded tripinfo speedFactor. Do not use revision03 supplemental metrics/timeline or non-event `reference_eligible=False` as donor labels.

Use unchanged physical-x 100 m cells [0,2200), internal through-lane mapping and actual lane-length denominator. Mainline through whitelist: `main_up_0/1`, `:freeway_merge_0_0/1`, `merge_section_1/2`, `:merge_end_0_0/1`, `main_down_0/1`. Exclude auxiliary `merge_section_0`; unexpected M lanes cause a mapping error, not silent dropping. Preserve left/right through-lane identity across edge names using archived connections. No identity inference from equal suffix alone.

## 3. Temporal periods and population

Use unchanged half-open 30 s bins anchored at0. Generate only complete non-overlapping donor blocks [90j,90(j+1)) wholly inside demand [0,1500); j=0…15. Discard [1440,1500) only from bank eligibility as an incomplete block; preserve those bins in diagnostics. No warm-up, time shifting or post-demand donor. Every lane-bin and pooled-bin needs complete observation labels, positive M exposure and at least two unique M IDs. Empty labels contribute zero density; empty bins have missing speed, not free flow. Reject a block if any of its lane-bins fails.

## 4. Speed and lane screen

For each M vehicle-time sample compute r=v/(actual lane speed limit * precise speedFactor); retain v in m/s. The sample-weighted mean r must be >=0.85 in every bin, independently for each of the two through lanes and pooled. Use all samples; no clipping, fastest vehicles, best lane or target-based normalization. The 0.85 and 90 s conventions are inherited exploratory screens; per-lane application is a proposed donor safeguard, not a changed classifier population gate. Passing does not establish empirical free flow.

## 5. Density and exposure support

For every bin record M and M+R spatial density as vehicle-time sample count/(30 * mapped lane-km), independently by lane and pooled; reference density must be positive and finite. Record first/last bin, density differences, range and adjacent-cell density. Missing concentration makes the block ineligible. **No critical-density cutoff is available:** report `CONCENTRATION_MEASURED_NORMALITY_UNVALIDATED`; do not label high-mobility donors proven low-concentration/free states or select lowest-density windows.

For each bank retain ranges of M density, M+R density, unique M exposure and lane share over its eligible bins. Unique exposure is distinct M IDs in that lane-bin; lane share is that lane's M vehicle-time sample count divided by the pooled through-lane M sample count in the same cell-bin (pooled share is1). SpeedFactor support is the min/max of precise factors over all M samples in the bank, not a range of bin means. Target support requires both its minimum and maximum sample factors inside that interval. Vehicle-type support requires the target's observed type-ID set to be a subset of the bank's set, with identical archived definitions for each type; type frequency differences remain reported, not assumed eliminated.

Per target bin, report a componentwise in-range/out-of-range flag using inclusive observed bank min/max on the same cell and lane. Failed type support or any out-of-range required dimension means `OUTSIDE_REFERENCE_SUPPORT`; missing means `SUPPORT_UNKNOWN`. Evaluate both lanes and pooled; any failure makes the cell-bin not comparable. These rectangles are conservative diagnostics, not a joint-distribution model; inside-range is necessary for contextual transportability, not proof of exchangeability or matched composition. Do not filter/reweight donors against a target's values. Outside-support comparisons may be printed only as descriptive extrapolation and cannot trigger automatic fallback to a more favorable bank.

## 6. Occupancy and flow

Attach existing E1 records only through verified detector/cell mapping; retain lane data, no-contribution speed NA, native counts/flow/occupancy. No interpolation to uninstrumented cells. Mark `E1_NOT_COLOCATED` or `E1_MISSING` where applicable; lack of colocation is not bank failure. Report unique M and R crossing counts at each cell's downstream physical boundary from successive FCD positions (deduplicate vehicle/boundary; timestamp at first observed downstream label; flag gaps); this is an approximate 1 s passage metric, not raw E1 flow. Record downstream/adjacent-cell low-state context. No ALINEA target or occupancy cutoff is used.

## 7. Exclusions and event-overlap mask

Construct one target-independent mask per donor run/cell from unchanged archived P/S/L/Candidate A/C outputs, including short candidates and early warnings. Exclude any donor block intersecting any registered disturbance interval in the cell or its immediately adjacent cells; intervals use original onset/end, never slide. In addition, this first conservative bank accepts only blocks ending at or before the earliest such disturbance onset (minimum over profiles and the cell/neighbors). This removes all later/recovery periods regardless of whether recovery was resolved; it may deliberately leave no bank. Do not relax it if 3350 has no donor. It also prevents event-specific reference reselection.

Missing required event catalogue/coverage produces `DISTURBANCE_MASK_UNKNOWN`, not an empty mask. Known source-insertion, direct-TLS, downstream-tailback or geometry-artifact intervals must be supplied by provenance-bound existing audit records and exclude overlapping blocks. If only unresolved attribution exists, retain `ATTRIBUTION_NOT_VALIDATED` and prohibit interpreting the bank as a cleared physical normal state; do not invent manual interval exclusions. State exactly which artifact checks were observed vs unavailable.

## 8. Recovery periods and missing observations

Post-disturbance/recovery periods are excluded from the primary donor bank; they may be reported in a separate diagnostic table only. Never call population disappearance recovery. Preserve locked recovery labels; record that absent reference density can mechanically prevent evaluating recovery. No new recovery duration or external density substitution. Missing data and no population are separate reason codes; neither is imputed. Errors affecting raw normalization or mapping stop the affected bank, not just a few inconvenient rows.

## 9. Reference aggregation

For every cell/lane retain all passing blocks; no minimum block count beyond one complete block is claimed to provide representativeness. Report exact numbers of blocks, bins, unique vehicles and vehicle-time samples. Every available bank in this two-run, single-seed proposal carries `LIMITED_REFERENCE_SUPPORT`; there is no subjective "few blocks" decision or invented adequacy threshold. Aggregate eligible 30 s bin means with equal bin weights, not vehicle-time weights across bins. Report median, 25th/75th percentile (linear interpolation at index (n-1)p), min/max for r, absolute speed and densities. Keep per-block values and lane tables; pooled summaries never override a lane failure. Quantiles are descriptive and correlated, not independent-sample confidence intervals or anomaly cutoffs.

## 10. Fallback hierarchy

Compute banks once, before target comparisons. Keep R1's exact three preceding bins and legacy classification in separate immutable columns. Primary contextual bank: same-run R2/R4. If it has zero eligible blocks, external A0 R3/R4 may supply context for3350. Never use a target result, out-of-range direction or apparent classification benefit to switch banks. If both banks exist, report both but do not merge them; primary remains same-run. If neither exists, `INDEPENDENT_REFERENCE_NOT_AVAILABLE`. If a bank exists but target support is absent/unknown, `INDEPENDENT_REFERENCE_NOT_COMPARABLE`; no extra fallback. A0 never uses3350 as fallback.

## 11. State/transition logic and prohibited inferences

Keep separate fields:

- `local_reference_status`: VALID / UNAVAILABLE_PAST / INSUFFICIENT_POPULATION / MISSING_DATA / SCREEN_FAILED, with all reasons preserved; for display precedence use missing past, missing data, population, speed screen, valid.
- `independent_reference_status`: AVAILABLE / NOT_AVAILABLE / NOT_COMPARABLE / INPUT_NOT_VERIFIED; AVAILABLE means screened diagnostic bank plus componentwise support, not normality validation.
- `transition_observation_status`: preserve locked eligibility; no donor creates a normal-to-congested transition. Rejected observed pre-state -> NOT_IDENTIFIED; missing past -> NOT_OBSERVED. `ONSET_LEFT_CENSORED` only if an already-observed low-state condition begins at the first adequately populated observation without earlier usable state; otherwise leave censoring UNDETERMINED, never infer it from reference failure alone.
- `historical_classifier_result`: copied unchanged with source hash. `normal_state_validation`: NOT_VALIDATED.

There is **no new P-positive, State 1, breakdown onset, density-gate result or recovery classification output**. No-reference is an acceptable terminal result. No p-values, breakdown probabilities, causal demand/control effects, capacity drop, replication or G6/G7 release may be inferred.

## 12. Required output contract

Produce input_manifest/receipt with hashes, bank_selection_config, cell_lane_bin_metrics, every candidate_block with all eligibility/rejection reasons, disturbance/artifact mask provenance, accepted_bank_membership, bank_summaries, target_support_comparisons, immutable historical_classification_copy, and limitations report. Use IDs `(donor_run,cell,lane,block_start)`; one membership per block, no duplicate overlapping bank windows. Publish counts of all generated/accepted/rejected blocks and mutually nonexclusive rejection totals. Preserve full rows even when no bank qualifies. These outputs are proposals for a subsequent authorized offline task, not generated in this task.

## 13. Minimum verification before future use

Fixtures: no traffic; one vehicle; missing label/duplicate ID; wrong speedFactor/lane limit; edge-pos versus physical-x confusion; one stressed lane masked by pooled mean; exact 0.85 boundary; incomplete final block; event on block boundary; adjacent-cell event; unknown disturbance catalogue; post-event high mobility excluded; no same-run bank with eligible external bank; existing same-run bank outside support (no switching); external lower density cannot enter P; no donor; short event cannot become sustained. Independently reconcile one raw lane/cell/bin in each run, joins and all bank members. Test mass/count denominators and hash history before/after. Independent data and scientific review required before using resulting diagnostics; successful execution alone is insufficient.

## 14. Revision and approval boundary

This algorithm is executable as a diagnostic selection proposal, not validated as physical-state classification. A future state-only classifier needs an explicitly reviewed concentration/spatial gate and independent validation; no cross-run density replacement is permitted here. Approval to implement this spec is not approval to change P/S/L, run SUMO, change demand profiles, select a baseline or freeze the formal protocol. Keep the historical A0/3350 classifications and all previous receipts intact.
