# Phase A A04 final incremental review

**Offline ready, 0 SUMO starts; no release.** Source/timings/inputs are now locked for exact independent review. Final cards and source/test hashes: `PHASE_A_A04_FINAL_CARDS.json` and `PHASE_A_A04_OFFLINE_RECEIPT.json`. Superseded A01/A02/A03 cards remain intact and were never launched. A02/A03 reviewed source snapshots are preserved under `reviewed_a02_sources/` and `reviewed_a03_sources/`.

A03 fixed post-advance incomplete accounting and accurately split PRECONTROL/EXTERNAL_HOLD prefix counts; the full explanation remains in `PHASE_A_A03_INCREMENTAL_REVIEW.md`.

A04 adds direct `phase_api_requests_json` to each completed-step row. Every native `setProgram`/`setPhase` invocation records time, method, value and whether the call returned; requests are appended before invoking the API, so attempted failed calls remain in failure snapshots. This includes initial t0 OPEN, prefix t600 native yellow setup, and executed safe cycle boundaries. No-request steps contain `[]`; feedback itself issues no phase API calls. Actual program/phase/color/next-switch observations remain separately recorded. This changes only auditable logging, not native phase behavior or any parameter.

Verification: full previous21 tests plus2 directed mock tests pass (**23/23**); syntax check and all67 protected hashes pass. Tests exercise successful/failed API request logging and unchanged no-midcycle-reset behavior. No neutral/SUMO/environment startup test, installation or Phase C card occurred.

Root may request an exact A04 scientific incremental check, then release R300 A04 only. Runtime and all traffic safety/service qualifications remain unverified. No additional implementation optimization is proposed.
