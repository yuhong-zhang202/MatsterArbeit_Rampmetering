# Independent Data / Provenance Prelaunch Review — MINIMAL3199

**Disposition:** `BLOCKED_PENDING_REQUIRED_REGRESSION_FIXTURE_COVERAGE`  
**Findings:** Blocker 0 / Major 0 / required Minor 1  
**Confidence:** High for static inputs and binding; High for the identified test coverage gap.  
**Execution:** No SUMO, TraCI, or netconvert process was started. Both cards remain `DRAFT_NOT_AUTHORIZED`.

## Context preflight and scope

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the approved plan `artifacts/stage6_minimal_ramp_induced_breakdown_existence_test_20260924_v1/PLAN.md`, the v5 matched-input repair report and independent data/scientific reviews, and the MINIMAL3199 adapter, prepared files, cards, runtime bindings, manifest, R02 runner and tests. The project remains in Stage 6 exploratory preparation; formal protocol is not frozen. Prior PAIR3199 results remain `NOT_EVALUABLE`. This review covers static planned inputs and provenance only, not realized trajectories or scientific validity.

## Static input and binding checks

- Parsed control and treatment demand using the adapter's strict element/attribute checks. The M sets contain **1,333/1,333** records and match per vehicle on ID, integer-ms desired departure, full route, vType, speedFactor, departPos, departLane and departSpeed. Route and vType definitions match between arms.
- All vehicle records are globally sorted by `(depart_ms, id)`. Treatment R records are `R_flow.0`–`R_flow.191`, scheduled from 540.000 through 1495.000 s in 5 s increments. Control has no R vehicle record.
- Manifest class ledgers explicitly mark U and X as `PASS_ZERO` with planned count 0 in both arms; control R is explicitly `PASS_ZERO`/0. Treatment has R count 192. Missing U/X ledger entries fail closed in the adapter.
- Treatment-only vehicle identities are exactly the R class by the reviewed structural checks. Thus the static planned-demand difference is R only.
- The 15 entries in `scripts/stage6/minimal3199/prepared/PROVENANCE_RECEIPT.json` all recomputed to their recorded hashes. Both cards bind their arm input hashes, manifest, runtime sidecar, output-role file, plan, runner and network. The accepted network hash is `887c2324…c700ca`; R02 runner hash is `7b65231a…d094aee7`. Runtime bindings identify SUMO 1.26.0, the expected `SUMO_HOME`, Python 3.13.0 and the proposed 90 s / 60,000,000-byte control limits. These are proposals, not resource authorization.
- Both exact output paths and the shared output root are absent. Cards are draft-only, `execution_authorized=false`, `run_command=null`, and retry count is zero.
- With the bound project interpreter, R02 read-only preflight passed for both cards and launch verification rejected each draft. The host's unrelated Python 3.12 correctly failed the bound-interpreter check; rerunning under `./.venv/bin/python` passed. No simulator process was started.

## Regression checks and required issue

Ran `PYTHONPATH=. ./.venv/bin/python tests/test_minimal3199_adapter.py -v`: **10/10 PASS**. The suite covers the exact pair, explicit-zero omission, M speedFactor mismatch, R in control, non-R treatment addition, unsorted records, input/runtime hash and output collision checks, card/run-ID mismatch, read-only draft preflight and launch refusal, and card hash/path mismatch.

**Required Minor 1 — incomplete negative-fixture coverage for exact identity/schedule invariants.** The implementation compares M departure/route/type and checks the R schedule/ID set, but the dedicated suite has no mutation fixtures proving rejection of M ID, desired-depart, route or vType mismatches, nor a malformed/missing/shifted R ID or departure. Add focused fixtures for these locked invariants and rerun the targeted suite. I did not change tests or inputs under this review assignment. Until then, these code paths are inspectable but not regression-demonstrated, so this data/provenance gate is not PASS.

## Boundary

This is not an execution approval. The control is not data-review-ready for a single-start authorization until the required regression fixtures are added and an exact-card/R02 preflight is repeated against the resulting hashes. No scientific input, classifier, P/S/L definition, geometry, demand parameter, vehicle behavior, or formal protocol was edited.
