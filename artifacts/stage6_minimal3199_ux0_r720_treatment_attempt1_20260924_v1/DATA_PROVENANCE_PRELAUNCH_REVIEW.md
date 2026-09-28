# Data/provenance prelaunch review — MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1

- **Disposition:** `BLOCKED_MISSING_START_REQUEST`
- **Exact card SHA-256:** `924d4fce7098d5d69e60dc6ecb50b00b6c1a4b0eb527d0153f7681969b58d714`
- **Confidence:** High
- **Finding count:** 0 blocker / 0 major / 1 required minor

## Context and control reference

Read current `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/WORKLOG.md`, and the approved U=X=0 minimal existence plan. The completed control is `MINIMAL3199_CTRL_S17_TECH_RETRY2`; its independent scientific disposition is `LOW_R_BACKGROUND_ACCEPTABLE` for this minimal-test control gate only. That review explicitly preserves the Candidate C short-warning history and high-mobility-screen FAIL; this is not a clean high-mobility baseline. The card’s references to the control card, data review, scientific review and raw output manifest all match current hashes.

## Verified matched inputs and treatment-only delta

The treatment input hash is `b57a0f3723be40bd1725a478f4ec7f57c1aacfbac0f2e57a5d94f31dce758c83` and the control input hash is `5df62660b9b9e2cc02734794ef2d361a3a97c30fa38a1e4fcbf550f0a2a1e405`. M has 1,333/1,333 identical identities and zero mismatches in desired departure, route, vType, speedFactor, departPos, departLane and departSpeed. The actual retry2 control raw has all 1,333 M vehroute records; route, type and speedFactor agree 1,333/1,333. Control R=0 is bound to its final card and output manifest.

The treatment demand contains 1,525 materialized vehicles: exactly 1,333 M and 192 R, with no U/X identities, no flows, and no duplicate IDs. R identities are exactly `R_flow.0`–`R_flow.191`; desired departures are 540, 545, …, 1495 s (5 s spacing), on the R route. The treatment-only ID delta is exactly those R identities. Global ordering by `(depart_ms, id)` is valid. Fixed conditions match: qMain=3199.2, seed17, U=X=0, A_OPEN, 2700 s, same network SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`.

## Runtime and staging

Card, input manifest, staging provenance, runtime sidecar and runner hashes match their actual files. SUMO 1.26.0 binary, additional schema, Python executable and role-source hashes match the card. Deterministic staging independently reconstructs both exact files: `scenario_control.sumocfg` 2,885 bytes / `839cd0604aa2eef5da3677dae06296995fc3c017b9a84f1f8cf0ed0315d47d54` (8 output-root substitutions and 1 add-file substitution); `scenario_control.add.xml` 4,048 bytes / `0a476ff96e378ae8972de96cba1b1748274158a29bc7f9f3408be70996e3b2f0` (12 output-root substitutions). No old roots remain. The output directory contains only those two staged files; the unique consumption directory is absent. Engineering reports no Guardian/SUMO dispatch.

## Required issue

The assigned review specifically asks to verify a persisted but unsent `START_REQUEST`. `START_REQUEST.json` is absent from the attempt package, and no request hash is bound by its card or input manifest. Engineering’s statement that no request was dispatched proves there was no launch, but does not provide request bytes/values to verify. Therefore this data/provenance receipt cannot PASS as scoped. Required resolution: persist the exact-card-bound request without dispatch, or obtain a hash-bound engineering rationale that it is intentionally created only after the three review receipts, then rerun this review.

No scientific input or protocol was modified. No process was launched.
