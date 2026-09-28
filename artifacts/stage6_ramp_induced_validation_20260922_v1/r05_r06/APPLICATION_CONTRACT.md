# R05 / R06 Offline Adapter Contract

Status: implementation helpers and synthetic fixtures only. This contract neither
applies the rules to a future run nor authorizes execution.

## R05 — Direct control PRE screen

Inputs must be produced by the exact locked classifier adapter, not by revised
supplemental metrics:

- `cell_lane_bins`: one record per `(cell, scope, bin_start_s)` with `observed_labels`,
  `unique_M`, `mean_ratio`, `M_density`, `MR_density`; scopes are `lane0`, `lane1`,
  and `pooled`. Ratios/densities must use the locked method's vehicle-specific
  model-reference speed and physical lane lengths.
- `event_rows`: union of locked P/S/L events, Candidate A spatial events, and
  Candidate C warnings; each row has `family`, `cell`, `start_s`, `end_s` using
  half-open seconds. These are masks only; they do not replace P's three prior
  local reference bins.
- `catalog_completeness`: bind `source_sha256`, `catalog_sha256`, processed event
  count, row count, `complete=true`, and full family coverage `P,S,L,A,C`. A
  verified zero-row catalog is valid; missing receipt is UNKNOWN. The helper
  recomputes both hashes from supplied source/catalog bytes and checks parsed
  row counts. The XML-to-row parser must independently attest full traversal and
  is not included here.

The adapter emits 30 rows exactly: 2 blocks `[360,450)`, `[450,540)` × 5 core
cells 13–17 × 3 scopes. Each row evaluates all constituent bins separately:
30 labels; unique M >= 2; mean normalized ratio >= 0.85; positive finite M and
M+R densities; no event overlap in the target/adjacent cells and no block end
after the earliest known disturbance onset in the target/adjacent cells. The
whole PRE gate passes only if all 30 rows pass; any unknown row yields UNKNOWN.
Missing metrics/labels/fields are UNKNOWN; complete observed gate failures are
FAIL. Duplicate/missing/out-of-domain keys or unknown status labels can never
produce PRE PASS. No bank enrolment or reference-library update is performed.

## R06 — Route-bounded R crossings and exposure

First produce ordered per-R-vehicle FCD observations mapped to monotone route
progress using the exact vehroute and compiled network/connection mapping. Do
not infer progress from a lane suffix. Preserve the mapping source/hash. For
each boundary (`SOURCE_INSERT`, `AUX_ENTRY`, `THROUGH_ENTRY`, `DOWNSTREAM_ENTRY`),
derive at most one route-checked interval per vehicle. Adjacent observations
bracket `(previous_time, current_time]`; missing route/progress/bounds is UNKNOWN.
If an aux-lane sample is skipped, infer AUX_ENTRY only if the route-progress
bracket demonstrably spans the auxiliary-entry boundary. Lane-change records may
corroborate but cannot invent a precise time.

For half-open 30 s bins, `certain` means the entire interval lies in exactly one
bin; `possible` means it intersects the bin and includes certain IDs. Do not sum
these sets. Exact crossing at 30 s belongs `[30,60)`; `(29,30]` is possible in
both adjacent bins and certain in neither. Missing intervals are retained as
per-bin UNKNOWN, never zero; known certain/possible IDs remain visible. Empty
crossing lists imply zero only with hash-bound lifecycle/FCD/route coverage and
reconciled scheduled R population. Keep vehicle IDs, evidence locators and hashes.

T2 is the earliest AUX_ENTRY interval; overlapping earliest intervals preserve
all candidate IDs and unresolved order. T3 is the first three consecutive,
complete bins starting no earlier than the T2 upper bound, each with at least
one certain AUX_ENTRY; confirmation is the end of the third bin and must be
<=720 s. Candidate-P ongoing exposure is reported independently per qualifying
bin using the separately reviewed rule; it does not alter the locked classifier.

## Validation boundary

The included fixtures validate gate arithmetic, half-open boundaries, missing
catalog/route propagation, duplicate crossing rejection, T2 ambiguity, T3 deadline
and ongoing exposure. They do not validate the future raw XML parser, compiled
network route-map construction, or any RI3350 result. Before application, bind the
parser and route mapping to the future raw manifest and inspect connections read-only.
