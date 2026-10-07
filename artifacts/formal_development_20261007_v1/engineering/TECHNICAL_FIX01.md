# Pre-start technical correction 01

Date: 2026-10-07. Actual SUMO/worker starts: **0**.

Independent scientific review found that the extracted V15 worker accessed
`card["startup_deadline_s"]` during connection, while the development preparer
omitted that field. Without repair this would fail after starting the SUMO child.
The issue was caught before any launch; no simulation failure or raw directory
was created. Original prepared A01 cards remain intact.

Minimal repair: card startup_deadline_s=60 and resources.startup_limit_s=60,
matching the existing prospective contract and unchanged startup helper.
`validate_worker_card` now checks all worker-required direct and nested card
fields before importing TraCI or calling Popen. The primary preflight invokes
the same pure validator. No network, model, timestep, signal, demand, feedback,
actuator, queue definition, threshold or control policy changed.

Regression: AST-discovered card-read paths must be covered by the validation
registry; each registry key deletion must fail. A direct call to the worker
with the formerly missing startup field removed raises ValueError, and patched
Popen.assert_not_called confirms the failure occurs before a child can start.
Fixed60s and mismatch values are checked. All ten offline tests and compilation
pass. Four new A02 prepared cards pass pure preflight and preserve the A01
request, feedback, queue and network values.

Evidence:

- `pre_start_fix01_original/`: original source snapshots, hashes and verification.
- `OFFLINE_VERIFICATION_FIX01.json`: actual commands, exit codes and regression.
- `STATIC_PREFLIGHT_FIX01.json`: new card hashes and superseded A01 references.
- `SOURCE_PROVENANCE_FIX01.json`: exact revised source hashes.

A02 denotes the second **preparation** of these cards, not a second physical
attempt. Both execution and coverage ledgers still have zero new runs. New
independent review and a primary-agent exact-card release remain necessary.
