# Scientific review record: freeway protectable-state definition

Date: 2026-09-21.
Disposition: **PASS_METHOD_DEFINITION**.
Open Blocker / Major / required Minor: **0 / 0 / 0**.

This is a primary-agent-authored record of the independent read-only `scientific_reviewer` response, not a file authored by that reviewer. The reviewer independently confirmed the final report hash after the required corrections.

Reviewed report: `docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md`.
SHA-256: `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`.

## Scope and disposition

PASS covers the exploratory methodological definition and implementation specification only. It does not certify unimplemented processing, classify A/B/C, validate the numerical thresholds, resolve O2, or approve a formal protocol. Stage 6 remains PARTIAL; the protocol remains empty. No simulation was started.

The reviewer confirmed the core source interpretation: literature supports a collective, persistent and attributable state definition; German freeway 70 km/h, 5 min aggregation and controller target occupancy are not transferable ground truth. Capacity drop is not necessary for State 1, but any efficiency claim requires its own evidence. The proposed numerical P/S/L profiles are acceptable only as explicitly conventional, retrospective exploratory screens.

Source spot checks included Brilon PDF pp. 5–6; Treiber PDF p. 351; Cassidy PDF pp. 4, 15–16; Papageorgiou PDF pp. 2, 4; and sumoITScontrol PDF pp. 4–5, 18, 34. The primary report provides the full source paths and relevant printed/PDF locators.

## Required corrections closed

1. Preserve duration-qualified episodes with no eligible onset reference as `ONSET_REFERENCE_UNRESOLVED`; do not produce a false negative at run level.
2. Prevent spatial duplication using deterministic cell-event IDs and unions of temporal intervals. Physical episode count remains unestimated.
3. Distinguish qualifying-episode-associated low-speed continuation from fully qualified State 1 burden; require per-bin density/attribution eligibility for the latter.

All three were required Minor clarifications and were verified in the final report. No Blocker or Major remained. These wording/logic corrections did not require new research authorization.

## Mandatory measurement checks

|Check|Disposition|
|---|---|
|Measurement target|PASS at specification level: M population, local domain, time, units and missing/censored cases specified.|
|Actual coverage|NOT VERIFIED independently in this review; relies on prior mapping and the analyst's read-only capability inspection, not a full raw/network rescan.|
|Omission/duplication|PASS as a specification; implementation remains NOT VERIFIED.|
|Independent numerical reconciliation|NOT VERIFIED: no new application/classification was performed.|
|Regression protection|NOT VERIFIED: offline fixture requirements exist, but code/tests are pending.|

Confidence: High for literature-transfer cautions, capacity-drop distinction and archived field capability; Moderate for suitability of the provisional numerical screen; classification accuracy, actual results and generalization remain Unknown.

## Analyst audit and remaining limits

Independent `data_analyst` inspected existing schemas/examples, mapping and context without writes or classifications. It confirmed vehroute speedFactor, FCD population/coordinates, native E1 records and straight through-lane mapping. It warned that model speed normalization is not independently measured free-flow speed, M/R cannot be separated by the shared vehicle type, missing population is not recovery, and one downstream-moving slow vehicle is not an upstream congestion wave. These points were incorporated.

The next task is offline implementation, failure-case tests, actual raw completeness/hash checks, P/S/L and Candidate A application, followed by independent scientific review. No new SUMO run is required to calculate these rules; local causal attribution can still remain unresolved.

## Source identity anchors

|Repository source|SHA-256|
|---|---|
|`literature/core_reading/Traffic Flow Dynamics.pdf`|`8572ddc37f33a1ee61b08594ec8dd05071b326417e7ba0ab1f0ed108d5c65e71`|
|`literature/core_reading/RELIABILITY OF FREEWAY TRAFFIC FLOW.pdf`|`a08bf601e57bc48c05384087cbca9608bf275a1ca65ea37fb260e628c8f79268`|
|`literature/core_reading/Some trac features at freeway bottlenecks.pdf`|`6412650e4c1ceb7cbe6b5752996a8d08f629d956f87d7466af1e4a016dd1f843`|
|`literature/core_reading/Freeway_ramp_metering_an_overview.pdf`|`7567bf06c870a97abb58a178bd1270a6db53412fbcc283dd13907ec508b41822`|
|`literature/sumoITScontrol.pdf`|`5daab95dfe29da68d04f79043094b262dbb49b1166c00e97d7cedf3666a76800`|
