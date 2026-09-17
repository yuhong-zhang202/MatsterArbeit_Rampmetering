# Stage 6 A tool capability audit

Status: archive-only engineering audit complete. No listed execution interface was invoked.

- `src/scenarios/run_minimal_uncontrolled.py` accepts profile, paired main/ramp demand, seed, timing and binary options. It has no current scenario-directory, output-directory, urban-demand, insertion-position or compiled-network-reuse interface.
- The runner uses a fixed scenario root, creates a random temporary runtime, materializes E2 endpoints, builds the network before evaluating `--validate-only`, and queries binary versions. It cannot be treated as an offline validator.
- `src/scenarios/check_e2_coverage.py` starts TraCI and is prohibited in A and offline C.
- `src/analysis/stage2_queue_diagnostic.py` contains old temporary paths. The existing `--reanalyze-summary` route materializes runtime state and is not the Stage 6 archive-only adapter.
- Historical Stage 3/4 analyzers remain bound to their original source/batch contracts. The repaired Stage 3 source has a different hash; Stage 6 uses a separate contract and does not loosen old guards.
- `build_stage3_t34_review.py` must not be reused until the unpaired-key silent-skip behavior is replaced and tested.
- Whole-suite tests may launch simulation tools. Only the new archive adapter's bounded fixtures were run in A.

Required before SG6-L: an isolated Stage 6 scenario/runtime interface, fail-closed card validator, compiled-network reuse or an explicitly revised build budget, exclusive output paths, deterministic materialization binding, and the two end-to-end fixtures identified by scientific review.

Observed Stage 6 A invocation counts: SUMO 0; netconvert 0; TraCI 0; GUI 0.

