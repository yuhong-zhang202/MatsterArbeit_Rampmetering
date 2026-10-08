## AI Collaboration

This project uses three project-scoped Codex subagents:

- `simulation_engineer`: SUMO, TraCI, sumoITScontrol, simulation configuration, implementation, debugging, and controlled execution.
- `data_analyst`: reproducible processing, validation, statistical analysis, tables, and figures.
- `scientific_reviewer`: read-only methodological and scientific review.

Agent definitions are stored in `.codex/agents/`. Mandatory routing and context requirements are defined in `AGENTS.md`.

All subagents must read the current project state, decisions, experiment protocol, and work log before substantive work. Project-state documents remain under the control of the primary agent.

## Version Control

This project uses Git for local version control. Source code, simulation configuration, project documentation, thesis files, and project-scoped Codex configuration are tracked.

Generated raw simulation outputs, processed data, tables, figures, local virtual environments, caches, logs, and secrets are excluded through `.gitignore`.

Authorized Stage 2 closeout runs are copied byte-for-byte from their unique `/private/tmp` runtime into `artifacts/stage2_completion_<batch>/runtime_archive/`. These large local archives are ignored by Git. Their tracked execution ledger and source maps under `data/processed/` record original paths, archive-relative paths, sizes, and SHA-256 hashes; analysis resolves files through those maps and does not require the temporary source directory to survive.

No remote repository is configured by default.

## Environment Setup

The verified local environment uses Python 3.13 in a project virtual environment, SUMO 1.26.0, and `sumoITScontrol` 0.1.0. Create and install the Python environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The macOS SUMO Framework installation verified for this project exposes the complete SUMO root under `share/sumo`. Set it for the current shell session without modifying shell startup files:

```bash
export SUMO_HOME="/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo"
export PATH="$SUMO_HOME/bin:$PATH"
sumo --version
sumo-gui --version
```

Verify the Python interfaces from the activated virtual environment:

```bash
python -c "import traci, sumolib, sumoITScontrol"
```

## ALINEA Technical Smoke Test

The fixed upstream ALINEA example comes from `sumoITScontrol` tag `v0.1.0`, commit `5776c6c79a888a37e55079db63eedc7db0570863`. The original inputs are preserved under `config/smoke_tests/alinea/upstream/`; runtime adaptation and outputs are created only under `/private/tmp`.

Run static input validation, the GUI test, or the headless test from the project root:

```bash
.venv/bin/python src/smoke_tests/run_alinea.py --validate-only
.venv/bin/python src/smoke_tests/run_alinea.py --gui --gui-delay-ms 10
.venv/bin/python src/smoke_tests/run_alinea.py --seed 2
```

The GUI test requires a working XQuartz display on macOS. These commands reproduce a technical smoke test only. The upstream network, traffic demand, detector placement, controller settings, and vehicle parameters are not approved thesis experiment parameters.

## Project-Owned Minimal Uncontrolled Scenario

The project-owned technical scaffold is under `config/scenarios/minimal_uncontrolled/`. It contains a two-lane freeway, one entrance ramp, a fixed-time urban signal, and separate freeway-mainline (`M`), ramp-bound (`R`), urban through (`U`), and technical cross-traffic (`X`) routes. `R` and `U` share an urban approach so that finite ramp storage and queue spillback can be checked directly.

The formal project-isolated Tencent MemoryCore seed is stored in Docker volume `tdai-ramp-metering-memory-v1`. Run `node scripts/memory/read_formal_memory.mjs` for a compact L0/L1/L2/L3 persistence check, or add `--full` to retrieve L1 plus the full L2 scenario body and L3. The reader starts the existing `memory-pilot` Colima profile when needed, then starts a disposable container with networking disabled and uses the fixed service/team/agent/user identity. A cold start may take over a minute. Project `.codex/config.toml` also registers the zero-argument, read-only `read_project_memory` MCP tool for explicit recall in new project tasks. Repository documents remain authoritative; MCP recall is on demand and does not automatically capture turns or inject memory on every request. Import evidence and limitations are in `docs/memory/FORMAL_PROJECT_MEMORY_20260909.md`; the official-integration gap audit is in `docs/memory/OFFICIAL_CODEX_INTEGRATION_AUDIT_20260909.md`.

The earlier `node scripts/memory/read_snapshot.mjs` command still reads the fixed 2026-09-09 thesis-only snapshot from the separate `tdai-ramp-metering-snapshot-20260909` volume. It verifies SHA and makes no model call. The local fallback is `docs/memory/project_snapshot_20260909.md`; do not rerun `store_snapshot.mjs` to update it.

`scripts/memory/zero_cost_layered_harness.mjs` is a maintainer engineering harness for the installed MemoryCore image. It uses synthetic input and a local fake model endpoint to exercise native L0/L1/L2/L3 orchestration and a 41-attempt ephemeral cap without external calls. Its passed result and limitations are recorded in `docs/memory/ZERO_COST_LAYERED_HARNESS_20260909.md`. It is not the production capture/recall bridge and its process-local cap is not approved for paid API use.

`scripts/memory/openai_budget_proxy.mjs` is the separate restart-persistent outbound budget gate; `node scripts/memory/test_openai_budget_proxy.mjs` tests it against a local fake upstream. The regression restores 17 used attempts after restart, reaches 41, and rejects request 42. The proxy requires explicit environment configuration and is not a signal that paid extraction or real-history import has been authorized.

Tencent memory updates are manual and user-triggered. When the user explicitly requests one, prepare a delta bundle, a complete reviewed L3 candidate and an approval manifest based on `docs/memory/incremental_update_approval_TEMPLATE.json`. Validate it first with `node scripts/memory/run_incremental_memory_update.mjs --approval <manifest> --dry-run`. The dry run performs no Keychain access, Docker work, network request, model call or memory write. Paid execution requires a fresh approval for that exact manifest and removes only `--dry-run`; details are in `docs/memory/THESIS_MEMORY_INCREMENTAL_UPDATE_20260909.md`.

Run source validation, the low-load functional check, or the deliberately overloaded spillback check from the project root:

```bash
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --validate-only
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --profile low --seed 17
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --profile stress --seed 17
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --profile low --q-main 1440 --q-ramp 480 --seed 17
.venv/bin/python -m unittest tests/test_minimal_uncontrolled.py
```

Each run creates a new directory under `/private/tmp` and reports planned, inserted, arrived, unfinished, and not-inserted vehicles; route and output-ID checks; network and SUMO warnings; the four historical E1 summaries plus an independent `mainline_merge_entry` group on the two M-only internal connections; and finite-storage observations. The historical upstream E1 group is marked `origin_insertion_contaminated` because `departPos=last` overlaps its position. `--q-main` and `--q-ramp` must be supplied together in veh/h; urban and cross-traffic demand remain fixed technical placeholders.

Stage 2 exploratory runs additionally accept `--warmup-s`, `--measurement-duration-s`, `--demand-end-s`, and `--post-demand-clearance-s`. When supplied together, demand end must equal warm-up plus measurement duration. These controls do not establish scientifically appropriate durations. Clearance stops new scheduled demand; delayed vehicles can still enter during this period.

The summary separates technical completeness from scientific eligibility. Eventual insertion of all vehicles does not demonstrate that requested demand was realized within measurement; inspect window-specific departures and departure delays. Detector settings and duration choices remain provisional, and `capacity_analysis_eligible=false`. These outputs must not be used as capacity estimates, formal experiments, or thesis evidence. See [the Stage 2 diagnostic](docs/探索验证阶段/STAGE2_TIMING_DIAGNOSTIC.md) for the audited exploratory findings and limitations.

The Stage 3 archive-only diagnostic is implemented in `src/analysis/analyze_stage3_baseline.py`. Its `analyze-run` and `aggregate` commands require a registered ledger and measurement contract, reject output-directory reuse, and read only archived Stage 2 artifacts. The completed batch is `data/processed/stage3_baseline_diagnostic_20260912_v2`; interpretation and superseded-revision boundaries are recorded in `docs/探索验证阶段/STAGE3_BASELINE_DIAGNOSTIC_REPORT.md`. This interface is batch-specific and must not be used to launch simulations or as a generic formal-analysis pipeline.

The Stage 4 T42 offline adapter is `src/analysis/analyze_stage4_qmain.py`. It validates the immutable registration payload, fixed C/MH references, planned-versus-realized entry accounting, complete observation schema, sequential branch/final decisions and launch counters. The user-authorized T43 block is complete and Stage 4 is closed; the bounded result and limits are in `docs/探索验证阶段/STAGE4_TARGETED_VALIDATION_REPORT.md`. Stage 5 T50–T53 are complete, with T54 user acceptance pending in `docs/探索验证阶段/EXPLORATORY_VALIDATION_T54_ACCEPTANCE_PACKAGE_REVISION_02.md`; the independent re-review and corrections are in `docs/探索验证阶段/STAGE3_STAGE5_ASTRA_REVIEW_20260913.md`. No formal experiment has started.

The 2026-09-13 Stage 3 parser repair changes its source hash. Historical Stage 3/4 ledgers still bind the preserved original source and must not be rebound silently. Fixed-archive verification of the repaired source uses the audit-only ledger under `data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/`; see the re-review for reproduction paths and the old contrast-builder reuse restriction.

The runner now sets each E2 to its compiled named-lane extent and adds explicit internal/external `fcd_lane_observations`, preserving the older ordinary-edge summaries. For an isolated no-step coverage check, invoke `.venv/bin/python src/scenarios/check_e2_coverage.py --net-file <compiled-net> --additional-file <runtime-additional> --sumo-binary <sumo-path>`; optional `--output` must be a new path. For retained trajectories, `.venv/bin/python src/analysis/internal_lane_accounting.py --fcd <fcd-xml> --network <compiled-net> --output <new-path-under-data/processed>` produces the corrected accounting without a simulation. Observed lane length is not automatically permitted queue storage; E2 and FCD stopping definitions are not interchangeable.

For the retained low and longest Stage 2 runs only, `src/analysis/stage2_queue_diagnostic.py --output <new-json-path>` reaggregates queue-event timelines without running SUMO. Invoke it with `.venv/bin/python`, choose a new path under `data/processed/`, and retain the original runtime directories identified in the script. It refuses existing output paths, verifies source hashes and assumes all scheduled vehicles eventually arrived; it is not a general incomplete-run analyzer or a formal causal analysis.

`src/analysis/render_stage2_geometry.py` renders the retained compiled geometry using Pillow from the bundled desktop Python runtime, without installing packages or running SUMO. Pass new `--png`, `--svg` and `--manifest` paths under `results/figures/` and `data/processed/`; existing artifacts are refused. The reviewed output is `results/figures/stage2_geometry_20260909_v4.png`. Earlier versions are superseded. The companion SVG embeds the PNG; neither is a live GUI screenshot or proof of effective storage/detector coverage.

`src/analysis/build_stage2_replay.py` creates a bounded 390–430 s offline replay of the repaired retained Stage 2 trajectory. Run with `.venv/bin/python` and supply `--run`, `--reference` (paired accounting v2), `--template` (literal replay fragment), `--output-dir` (new directory under `data/processed/`) and `--html` (new thread visualization path). The saved `data/processed/stage2_replay_20260909/manifest.json` records the exact source/template paths and hashes. Existing outputs are refused. This fixed-clip diagnostic reads saved FCD/network/TLS only; it does not launch SUMO or evaluate phase durations.

`src/analysis/build_stage2_g1_diagnostic.py` builds the bounded offline G1 v2 mainline/merge diagnostic from a retained runtime. Supply `--runtime-dir`, and three new exclusive directories via `--output-dir`, `--table-dir`, and `--figure-dir`; existing paths are refused. The reviewed output is the `_r2` batch under `data/processed/`, `results/tables/`, and `results/figures/`. The tool preserves the source run's windows separately from analysis windows A `[0,1500)` and B `[300,1500)`, retains no-contribution E1 speeds as missing, and reports sampled R merge-crossing brackets rather than exact crossing times. Its upstream E1 overlaps `departPos=last` insertion and is not a valid conventional upstream traffic-state detector. Run only `python -m unittest discover -s tests -p 'test_stage2_g1_diagnostic.py'` for its dedicated offline tests; the tool and test do not launch SUMO.

The earlier [Stage 6 obstacle-resolution plan](docs/探索验证阶段/STAGE6_OBSTACLE_RESOLUTION_EXECUTION_PLAN.md) and [registration template](docs/探索验证阶段/STAGE6_VALIDATION_CARD_TEMPLATE.json) are retained as historical records; the template is non-executable and does not authorize runs.


## Stage 6 exploratory closeout and formal-design handoff (2026-10-03)

Stage 6 exploration is `completed / preliminary_ready` under D-018 after current-version uncontrolled demand localization and matched safe standard-metering comparisons for seeds 17/23/42. The three controlled V15 runs passed independent safety, rate, detector and vehicle-accounting gates; they show mainline improvement with substantial R/U costs and observable shared-road R/U exposure. The tested policy increases total network system time, so no sweet spot is claimed. The strict 30-second continuous slow-chain test remains negative. Read the [closeout and exact formal-design handoff](docs/探索验证阶段/STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md) before further work; [PROJECT_STATE](docs/PROJECT_STATE.md) has the current phase. The former limited closeout and V8/V9 attempts remain historical. `docs/EXPERIMENT_PROTOCOL.md` is empty and unfrozen; no formal simulation is authorized.

The [full exploratory validation report](docs/探索验证阶段/STAGE6_EXPLORATORY_VALIDATION_FULL_REPORT_20261003.md) lists the original O/G/Q criteria, all 18 current-version uncontrolled outcomes, the three paired V15 results, technical failures, evidence limits and final item-by-item disposition.

The V15 exploratory runner is `scripts/stage6/standard_metering_20261003/runner.py` and requires the project `.venv/bin/python` with TraCI. Existing card/release/receipt identities are one-use and must not be relaunched. Any future formal run requires a separately reviewed and frozen protocol.

## Bounded formal-design development (2026-10-07)

The user-authorized D-019 trial has its own [plan](docs/development/DEVELOPMENT_TRIAL_PLAN_20261007.md), [development summary](docs/development/DEVELOPMENT_TRIAL_SUMMARY_20261007.md) and immutable authorization/parameter/release records under `artifacts/formal_development_20261007_v1/`. Read the summary and current project state for its completion and qualification status. The [original formal design draft](docs/正式实验设计草案v1.md) remains a preserved proposal; development does not freeze the formal protocol.

The separate development entry point is `.venv/bin/python -B scripts/formal_development_20261007_v1/runner.py`. `preflight --card <existing-card.json>` checks a card without launching; `launch --card <card.json> --release <release.json>` requires an exact reviewed release and unused output location. Local TraCI socket permissions are required for execution. Completed or failed run identities are never relaunched. Independent raw-bound analyses, source snapshots and gates are under `data/processed/formal_development_20261007_v1/`; tables and figures use the matching `results/tables/` and `results/figures/` subdirectories. Historical controls and the FIX02 development implementation must not be pooled into one policy effect.


## Candidate A engineering qualification — Issue #4 (2026-10-08)

Read the [qualification/STOP report](docs/development/CANDIDATE_A_QUALIFICATION_20261008.md). Separate actor/runner: `scripts/candidate_a_qualification_20261008_v1/runner.py`; offline tests: `.venv/bin/python -m unittest discover -s tests/candidate_a_qualification_20261008 -v`. Execution requires exact unused reviewed card/release, local TraCI socket access and installed SUMO1.26 schemas. Current result is **NOT_QUALIFIED / STOP_EXPANSION**; consumed cards/releases cannot be reused and no further launch is released. Highest verified rate and900capability remain unknown. This is engineering evidence, not formal results or a Stage6 reopening.
