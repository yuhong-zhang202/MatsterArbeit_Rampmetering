# Scientific Major: independent nonactive pool binding — engineering V4

**PASS_FOR_AFFECTED_OFFLINE_REVIEW_ONLY; data/science final review and current small clean-checkout check pending.** No simulation, permission or raw; original87 V3 source/card/receipts remain historical, original01/73 runtime/900/motion/guard/math/NUM are unchanged. Current profile only accepts packages_v4/02; packages/v2/v3 explicitly reject.

Context Preflight refreshed AGENTS/STATE/D018-D019/WORKLOG and empty-unfrozen protocol, plus SCIENTIFIC_FINDING_NONACTIVE_POOLS_V1.md. F01/F02 are not reopened. The previous041632a8 clean8 PASS remains accurate for that snapshot; no claim that it tests V4.

## Actual old-source counterexample and minimal fix

Added one nonempty fixture with active R0, loaded R0/R9, pending R10 and vehicle states for all three. Removing R9 from both journal loaded IDs and state rows produced actual regression FAIL on historical V3 evidence.py: expected ValueError was not raised (NONACTIVE_OMISSION_OLD_SOURCE_FAIL_V1.log). The exact old evidence and test/source preimages are preserved. This is an executed counterexample, unlike the prior static scientific finding.

identity_prefix now supplies original PRE bound_snapshot to identity_journal for each BEFORE and final extraPRE. time_s, loaded and pending_ids are required, duplicate-free and precisely matched by membership; active remains bound to world. Omitting an ID plus its state, missing source fields, duplicating source/journal IDs or swapping loaded/pending roles raises UNKNOWN. No requirement of disjoint or subset pools is invented; actual overlapping membership must match the original independent snapshot.

Every AFTER with a next PRE at the same simulation time also cross-checks both nonactive pools against that PRE. The final AFTER without a next PRE is explicitly returned as SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK. Its known row types/dynamics/active world are still checked, but independent nonactive pool completeness is not claimed. The actual result descriptor was clarified accordingly. No new getter, telemetry platform, mode, vehicle setter, or private safety proof was added.

## Actually executed verification

- Old source omission regression: actual FAIL (0.000s), retained.
- Only three affected methods: actual PASS0.239s. Covers omission+state deletion for BEFORE/extraPRE, pending omission, wrong-pool AFTER-nextPRE, duplicates, missing PRE source field, proper nextPRE join, explicit terminal single-journal scope, previous extraPRE errors, and public temp/source/card gate using packages_v4. No other suite or native run was repeated.
- Package_v4 prepare/check-card and static environment metadata/file-hash checks PASS; no native version process/import/spawn.

Only the new pool method and necessary old extraPRE fixture/source fields/current-card path were changed. Previous phase/body/yellow/EOF/math tests remain available as prior snapshot evidence, rather than pretended reruns on V4. Runtime behavior and actual phase checks are unchanged. Final actual.py result-scope wording changed after the affected tests; actual logic still calls the same identity_prefix whose current implementation was executed.

SOURCE_CARD_HISTORY_RECONCILIATION_V4.json verifies historical V3 changed live paths against exact saved preimages and preserves its original binder. New source/input/test/card files are bound by the V4 binder. The old FAIL, warnings, V1/V2/V3 prepared cards and review records are not silently overwritten.

## Limits and next gate

This is only an offline audit-coverage repair. Last AFTER nonactive pool completeness without next PRE remains single-source and explicitly unverified independently; it is not a safety/service qualification. All future N/E/phase/body/safety observations are null; execution/resources/canonical authority remain false or proposed. Native private branch, actual Y3/G5 service/populations/EOF/overhead remain unobserved. Parent owns governance; next is independent data affected review, small current-checkpoint clean verification and read-only science. No native retry is authorized.
