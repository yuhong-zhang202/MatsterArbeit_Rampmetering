# Phase A partial-source scientific review

Date: 2026-10-08. Read-only reviewer: project `scientific_reviewer` (`issue2_science`). Recorded by the primary agent from its returned report.

Disposition: **HOLD_FOR_SAFETY_HELPER_CORRECTION; no SUMO release.** This snapshot covers only the initial actor and safety helper, not the runner, tests, cards or runtime qualification. It preserves the findings even after correction.

Reviewed source SHA-256:

- `src/candidate_a_qualification_20261008/actor.py`: `65b3d1574a33a3f9090fc352e61560e799cfe03418598d80fbbd579a5fb30333`.
- `src/candidate_a_qualification_20261008/safety.py`: `a28583a5a2e9a7a4496f308e6af9cbb9aa515b3d1e431d0869c7d4431651b692`.

## Required corrections

**Major: nonzero low-speed shortcut.** The initial helper returns required stopping distance zero for `speed < 0.1`. A read-only counterexample uses R position 204.4899 m, speed 0.099 m/s and remaining distance 0.0001 m; the helper returns safe. This disproves its stated one-reaction-step plus normal-braking mathematical witness, without predicting an actual SUMO collision. Restrict the shortcut to exactly zero speed under a documented native-red no-acceleration premise, apply the explicit envelope to every positive speed, and test the near-stopline low-speed case.

**Required contract clarification: variable-rate residual bound.** Cumulative ideal-period rounding gives less than one second of cumulative timing error. Fixed-rate and changing-rate command integrals require different bounds: changing-rate `C_applied - E` is a rate-weighted sum, so a universal packet bound does not follow. State the fixed-rate bound and either a justified variation/boundary bound or exact per-window changing-rate accounting without an unsupported uniform claim. Report `C - C_applied` latency separately.

## Full-package prerequisites

- Bind the red guard's reaction/braking assumption to the installed native event order and actual runner call timing. Its formula assumes travel at current speed during the reaction step; it does not cover arbitrary acceleration unless separately bounded.
- Bind the pending-phase predictor to positive phase durations, one due native transition, no intermediate API reset, and matching observed `nextSwitch`. Verify actual observations; prediction is not runtime proof.
- Bind ingress/crossing coverage to actual type maximum speed/acceleration, 1 s step and compiled lane lengths; capture must verify populations, positions and types.
- Count every G/y/r internal entry, denied cycles and window boundary, with unique IDs and 1 s brackets. Nominal `n` never replaces observed discharge.
- Before an unsafe/unknown next motion step, terminate and preserve evidence. Do not advance to wait for a safer state.
- Keep E for denied virtual cycles, explicitly as a nominal target rather than qualified physical capacity.

Measurement target definition passes only at the partial-source design level. Runtime coverage, omissions/duplicates, independent numerical verification and regression protection remain **Not verified**. The primary agent forwarded both required corrections to engineering; the revised exact package requires a later prelaunch review.
