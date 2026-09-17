# Stage3 / Stage5 dependency engineering re-audit

Date: 2026-09-13. Classification: offline technical audit and narrowly authorized repair. New SUMO/netconvert/TraCI/GUI starts: **0/0/0/0**.

## Decision-facing result

**Four silent-pass defects existed in the Stage3 analyzer; existing passing tests did not disprove them. They have now been repaired, with 15 end-to-end invalid-input cases rejected and 33/33 final bounded tests passing.** Confidence: High.

These defects concern invalid-input qualification. They do not by themselves invalidate the eight accepted trajectories, require a new simulation, or establish a different Q1–Q4 result. The data analyst independently reports that none of these invalid-input conditions occurs in the eight real archives and is separately checking fixed-archive output invariance after the repair. That independent final result is not counted as this engineer's own reconstruction. Confidence that no new simulation is technically required for these four defects: High. Final acceptance of Stage3/Stage5 scientific claims remains for the primary agent and scientific reviewer.

The old Stage3 and Stage4 source-hash bindings intentionally reject the repaired working source. Their immutable contracts were not weakened or edited. Historical evidence and the Stage4 final snapshot remain preserved. A new audit-only Stage3 ledger provides the explicit source binding for the repaired-code comparison.

## Context and scope

Reviewed `.codex/agents/simulation_engineer.toml`, `AGENTS.md`, `PROJECT_STATE`, `DECISIONS`, `EXPERIMENT_PROTOCOL` and relevant `WORKLOG` history before implementation review. The protocol exists and is empty, consistently documented as unfrozen. Stage3/4 are recorded as closed; Stage5 T50–T53 are complete and T54 acceptance is pending. D001–D004 are user-approved provisional directions, not formal design freezes. Q2/Q4 and formal design remain unresolved; the current proposed handover is `specific_obstacle`.

Task inputs also included the exploratory completion plan, Stage3 final report and measurement contract, Stage3 production/independent analysis and tests, and the Stage4 final-evidence snapshot tests. Existing dirty/untracked work was preserved. The parent first assigned read-only audit, then explicitly expanded exclusive write ownership to `src/analysis/analyze_stage3_baseline.py` and `tests/test_stage3_baseline.py` for these four defects. No governance, protocol, historical ledger, raw archive, results or earlier processed artifact was edited.

## Findings and repairs

Line references below distinguish preserved original source from repaired current source.

| Finding | Actual pre-repair synthetic observation | Original cause | Small repair and regression |
| --- | --- | --- | --- |
| E01 FCD speed qualification | Remove one R speed at t=1: `missing_speed_count=1`, all 16 coverage rows `passed`, manifest `analyzed_archive_only`; original end-to-end test still passes. | Original lines 527–536 retained a count, but line 999 excluded it from the eligibility condition; coverage at 1030 only tested missing intervals. | Current lines 942–945 reject missing speed, missing/extra frames and unknown identity/lane before deriving tables. Negative FCD speed is rejected; non-finite rejection remains. Tests 18 and 19. |
| E02 unknown identity/lane qualification | Replace `main_down_0` with an unknown lane: coverage still `passed`, manifest written; endpoint correctly becomes `not_verified`. This is a coverage-status contradiction, not proof all downstream gates passed. | Original lines 1026–1030 wrote unknown counters while ignoring them in status. | Same complete-observation gate, tests for unknown lane, unknown ID, missing and extra frame. |
| E03 TLS labels | Replace TLS t=2699 with 2700: 2700 labels still present, coverage `passed`, original end-to-end test passes. | Original line 1018 checked count only. | Current lines 947–949 require exact equality with the contract time grid. Test 20 checks shifted, missing and extra labels. |
| E04 invalid contributed E1 speed | One internal E1 has positive counts but speed=-1: resulting M Full speed is 10 using denominator 90 instead of 180, still `complete`, mainline question `observed`. | Original read_e1 converted invalid contributed speed to null; original lines 408–434 discarded its speed contribution without degrading qualification. | Current read_e1 lines 448–451 and reaggregate_e1 lines 383–388 reject negative counts and positive contributions without finite nonnegative speed. Test 21 covers negative/missing/NaN speed and negative count; test 24 retains legitimate zero-contribution null speed. |

Before repair, E01–E04 are Major for general future analyzer reuse because invalid data can acquire a misleading passing status. They are not demonstrated Major errors in the finite historical numerical results: actual occurrence must be established separately. After repair the four identified paths are closed by direct tests. This is not a claim that every conceivable invalid schema has been exhaustively tested.

The diagnostic `scan_fcd` helper retains missing-speed/unknown counters for inspection; the production `analyze_run` entry rejects these conditions before producing evidence. No traffic definition, stop threshold, time window, formula or simulation configuration changed.

## Coverage of the requested engineering mechanisms

The original twelve named failure-mode tests were executed anew, rather than reusing their old receipt. The original suite also had guardrails, clipping, propagation and integration checks. Internal-lane test 05 only exercised presence with non-stopped speed, and the propagation test directly supplied episode rows. An old Stage2 test covers internal stopped lanes but uses different code. Therefore it was not sufficient evidence for Stage3's FCD-to-stopped-region path. New test 22 now verifies stopped vehicles on all three R internal lanes, their three disjoint region assignments and six Full rows (vehicle and region representations).

Propagation order continues to derive from contract coordinates, verifies adjacency, and rejects overlapping event memberships. Ordered and reversed fixtures pass. This establishes sampled first-observation ordering, not a continuous physical queue or a causal mechanism. The 1 Hz first-R unique-event and cross-bin unknown checks pass; the `(previous, first]` resolution is unchanged. Full-episode parent/slice, source-boundary and missing-frame censor flags pass. New test 23 explicitly checks departure labels 1499/1500/1501 with half-open accounting at t=1500.

E1 tests retain contribution weighting, A/B anchors, missing detector coverage, duplicate intervals and known short tails. New test 24 explicitly checks all-zero q/null v and a 15-second tail with q=720 and complete-window q=320. Reaggregation remains a conservation check; the T34 code separately records bin extrema, their time ranges and tied-extrema sampled support. It does not establish structural or stochastic robustness.

## Static observation-domain recheck

New read-only source-map-bound checks cover all eight Stage3 archives: **152 lane checks (19/run), 48 E1 checks (6/run), 16 E2 checks (2/run)**. The compiled lane set and lengths match the contract; E1 lane/position/period and original runtime output path match; each E2 starts at zero, ends at the length of its named lane (238.80 m or 204.49 m), and retains its registered period and runtime path. The five propagation spans are continuous and ordered. Evidence: `static_observation_recheck.json`.

This is static archived metadata verification. No detector was newly loaded and no live E2 measurement was rerun. Historical loading evidence remains historical. Per-vehicle E1 completeness is still not established.

## Stage4 final snapshot dependency

Only the two production and two independent final-snapshot tests were selected. They freshly verify the immutable snapshot SHA-256 `f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516`, canonical embedded ledger, four executed candidate identities, four runtime/source maps, **116 archived file hashes and sizes**, four candidate manifests/receipts and the selected branch binding. They also confirm mutable operational metadata is not the normative snapshot input. These four tests pass before and after this repair.

No full Stage4 116-test historical count is being claimed as a fresh run. Numerical Stage4 reconstruction is assigned to the data analyst. The old missing `b745...efff5` ledger snapshot is still explicitly historical/unavailable; the later immutable snapshot is the operative repair. No historical snapshot was fabricated.

## Exact verification and execution counts

All Python execution used `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python`; Python reported 3.13.0. Existing SUMO versions were only read from metadata, never launched.

| Execution in this audit | Fresh result |
| --- | --- |
| Initial suite via a Python unittest harness selecting `tests.test_stage3_baseline`, `tests.test_verify_stage3_baseline`, `tests.test_stage4_qmain.Stage4FinalEvidenceSnapshotTests`, `tests.test_verify_stage4_qmain.IndependentFinalEvidenceSnapshotChecks` | 26/26; 0 failures/errors/skips. Stage3 counter: 24 fixture calls, 94 assertions. |
| Four separate supplemental in-memory checks before repair | 4/4; 13 assertions: internal stopped lanes, endpoint boundary, zero E1, short-tail flow. |
| Four original synthetic archive probes | 4 completed probes; four misleading coverage-passes reproduced. These are defect demonstrations, not passing validation cases. |
| First post-repair same selected suite | 33/33; 0 failures/errors/skips. Stage3 counter: 40 fixture calls, 183 assertions; 15 invalid-input variants all reject before manifest/table output. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/run_offline_checks.py final_script_validation` | 33/33 again, to verify the delivered reproducible runner. This repeats the same cases, not 33 new independent cases. |
| `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/reproduce_original_probes.py original_probe_script_validation` | Failed during the first synthetic probe: relocating the preserved module did not restore its constructor's default project root. Retained with INCOMPLETE. No historical input or simulation was changed. |
| Same original-probe script with `original_probe_script_validation_revision_02` after fixing the relocation adapter | 4/4 original defects reproduced using preserved source. Source guards remain active and bind the synthetic ledger to the preserved code hash. |
| AST parse of modified production and test source; old Stage3/Stage4 context validation | 2/2 parses pass; both historical contexts correctly reject the new source hash. |

Thus **96 unittest test-method executions occurred across 26+4+33+33**, with repetitions explicitly identified. The final unique selected suite contains **33 tests**, not 96 independent tests. The four original defect cases were completed twice; one separate script attempt failed before producing its first manifest. The counter's 19 category strings include helper categories and must not be relabeled as 19 contractual failure modes. Temporary-directory destinations were redirected into this audit directory; assertions and production behavior were unchanged for ordinary suites. The original-probe script additionally retains its own synthetic fixture directories for inspection.

## Source preservation and reproducibility boundary

Original production SHA-256: `195fcc2f8c534919eac540fd4e3692e111dda447d15373dec14b64f052a47b96`; complete bytes are in `original_analyze_stage3_baseline.py`.

Original test SHA-256: `f8d15550366a300116a5f7c4ef731651e3f14ee801e4790a24f712e5ddc55e63`; complete bytes are in `original_test_stage3_baseline.py`.

Repaired production SHA-256: `6558f971bc713397e26a41fd4b2b4a71255a38ff7b6122d77df6056b88b6b8f6`.

Repaired test SHA-256: `4c040d6c080319e9f40c7a300acde482d30fb42b51fdc693b888841f98d6dc77`.

Use `audit_only_execution_ledger_revision_02.json` for repaired-code Stage3 archive comparison; SHA-256 `22bc5506f0b9df2976b2dc7100fde7ab9729e469836cf7d8d8a0bd5ef2316b38`. Its original ledger path/hash and derivation are recorded; only the two code-hash entries and explicit audit provenance differ. The initial audit-ledger file retained a historical test-source hash and is superseded by revision_02. Neither authorizes simulation.

Old Stage3 `validate_context` raises `analysis code hash is absent or stale in ledger`; old Stage4 raises `registered source-code hash mismatch: analyze_stage3_baseline.py`. These expected failures preserve version integrity. Do not rerun an old registered analysis with new code by weakening these guards. Use a preserved source context for historical reproduction or a separately recorded audit derivation for new code. Source relocation in the original-probe helper is test-only and does not edit those contracts.

## Handover and limitations

The smallest remaining task is independent eight-archive output-invariance verification followed by scientific review. There is no engineering reason to rerun SUMO for an offline qualification repair. T54 should rely on the repaired-code check and explicit finite-domain qualifications, not a blanket statement that the old tests proved generic fail-closed behavior.

The parent agent owns documentation impact updates: WORKLOG should record the new technical findings/repair; PROJECT_STATE/README should explain the active-source versus historical-contract boundary if this repaired source is retained. No decision or formal-protocol change is implied. This specialist has not edited those governance files.
