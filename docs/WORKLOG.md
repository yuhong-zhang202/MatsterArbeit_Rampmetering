# Work Log

Append one entry after each material task. Do not record ordinary discussion or unchanged-status checks.

## Entry Format

## YYYY-MM-DD — Task title

- **Goal:** What this task intended to achieve.
- **Work performed:** What was actually done.
- **Files changed:** Files created or modified.
- **Commands and verification:** Commands, tests, or checks performed.
- **Outcome:** Success, partial success, or failure.
- **Problems and limitations:** Errors, anomalies, or unverified items.
- **Next step:** Safest immediate follow-up.

## 2026-08-22 — Project-scoped agent configuration closeout

- **Goal:** Close out the interrupted project-scoped Codex agent configuration task without starting further runtime tests.
- **Work performed:** Created and reviewed the three project-scoped agent configurations for `simulation_engineer`, `scientific_reviewer`, and `data_analyst`; removed explicit model overrides so all three temporarily inherit the model selected by the parent desktop session; preserved the configured reasoning efforts, sandbox modes, full role responsibilities, and Context Preflight requirements.
- **Files changed:** Across the interrupted configuration task and this closeout: `AGENTS.md`, `README.md`, `.codex/config.toml`, `.codex/agents/simulation_engineer.toml`, `.codex/agents/scientific_reviewer.toml`, `.codex/agents/data_analyst.toml`, and `docs/WORKLOG.md`.
- **Commands and verification:** Parsed `.codex/config.toml` and all three agent TOML files with Python standard-library `tomllib`; all four files passed static parsing. Static checks also confirmed the three agent names and required fields, retained reasoning efforts and sandbox modes, complete Context Preflight rules, one Subagent Coordination section, one Mandatory Routing Check, and one README AI Collaboration section. The `scientific_reviewer` previously completed a read-only Context Preflight successfully while inheriting the parent model.
- **Outcome:** Partial success. All three project-scoped agent configurations exist and passed static validation, and the `scientific_reviewer` completed the limited inherited-model runtime preflight described above. The three agents must not be treated as having all passed runtime testing.
- **Problems and limitations:** The `simulation_engineer` runtime test was not completed because the CLI child thread failed with `no thread with id`. The `data_analyst` was not runtime-tested. All three agents temporarily inherit the parent agent model, and no further runtime validation was performed during this closeout.
- **Next step:** Reopen the project and perform full runtime validation from a normal desktop session; do not use nested CLI subagent testing for that validation.

## 2026-08-22 — Local Git repository initialization

- **Goal:** Verify that project-scoped Codex configuration was reloaded and establish a stable local version-control baseline before environment installation or simulation-code changes.
- **Work performed:** Confirmed the project root and loaded `AGENTS.md`; parsed `.codex/config.toml` and all three project agent TOML files with Python standard-library `tomllib`; confirmed that no agent has an explicit `model` field and that reasoning efforts are `high` for `simulation_engineer` and `scientific_reviewer` and `medium` for `data_analyst`; created `.gitignore`; preserved the nine empty project directories with `.gitkeep`; added the README version-control note; initialized a local Git repository on `main`; and created the initial commit successfully.
- **Files changed:** `.gitignore`, `README.md`, `docs/WORKLOG.md`, and `.gitkeep` files under `literature/`, `config/`, `src/`, `tests/`, `data/raw/`, `data/processed/`, `results/tables/`, `results/figures/`, and `thesis/chapters/`.
- **Commands and verification:** Used `tomllib` for static TOML parsing; ran `git rev-parse --is-inside-work-tree` before initialization; reviewed the file inventory and file sizes; checked text files for private-key, credential-assignment, and email patterns; inspected the existing supervision PDF for version-control suitability; ran `git init -b main`; checked `git status`, branch, Git identity, ignored files, staged changes, the staged diff, the final commit, tracked files, and remotes.
- **Outcome:** Success. The local repository was initialized on `main`, the project baseline was committed, and no remote repository was configured.
- **Problems and limitations:** Existing `.DS_Store` files are ignored. Future raw simulation outputs, processed data, result tables and figures, virtual environments, caches, logs, temporary files, and secrets are excluded. No credentials or large generated files were found. The supervision correspondence PDF contains personal names, email addresses, and private correspondence; it is retained only in this local repository and must be reviewed before any future publication or remote push. No SUMO command, dependency installation, simulation, or subagent was run.
- **Next step:** Before configuring any remote repository, review private supervision source material and define an appropriate publication policy; perform environment installation and simulation work only in a separate authorized task.

## 2026-08-23 — SUMO ALINEA technical smoke-test environment

- **Goal:** Establish an isolated SUMO, TraCI, sumolib, and `sumoITScontrol` environment and verify the fixed official ALINEA example as a technical smoke test rather than a formal thesis experiment.
- **Work performed:** Completed project Context Preflight and a read-only environment audit; verified the existing SUMO 1.26.0 macOS Framework installation; created the ignored project `.venv`; installed pinned direct dependencies; acquired only the fixed upstream ALINEA demo inputs from `sumoITScontrol` tag `v0.1.0`; preserved upstream files with SHA-256 provenance; implemented a project wrapper that uses session-level `SUMO_HOME`, temporary runtime copies and detector outputs, GUI/headless selection, explicit seeds, control-call evidence, and SUMO-generated GUI screenshots; and documented the reproducible setup and current technical status.
- **Files changed:** `.gitattributes`, `requirements.txt`, `README.md`, `docs/PROJECT_STATE.md`, `docs/WORKLOG.md`, `src/smoke_tests/run_alinea.py`, `config/smoke_tests/alinea/UPSTREAM.md`, and the fixed upstream files under `config/smoke_tests/alinea/upstream/`. The ignored `.venv/` was created locally. `.gitattributes` preserves the byte-identical upstream whitespace while retaining normal whitespace checks elsewhere.
- **Commands and verification:** Verified macOS 15.3 on Apple M3/arm64, Homebrew 6.0.12, SUMO and `sumo-gui` 1.26.0, and Python 3.13.0; installed `sumoITScontrol==0.1.0`, `traci==1.26.0`, and `sumolib==1.26.0`; `pip check`, package imports, AST/compile checks, wrapper help, static validation, upstream checksum comparison, and mock screenshot timing tests passed. After XQuartz 2.8.6 became available, a GUI run exited 0, completed 8,400 steps, called ALINEA 8,400 times, recorded 69 updates, and generated a 600 s screenshot with 47 vehicles and `J0` state `G`. Headless seed 2 and seed 3 runs both exited 0, completed 8,400 steps and 69 updates, and took approximately 5.63 s and 4.36 s respectively. Runtime outputs were written only under `/private/tmp`.
- **Outcome:** Success for the technical smoke-test scope. The fixed official ALINEA example ran through both GUI and headless execution paths, and the controller was demonstrably invoked. These runs are not formal experiments or thesis evidence.
- **Problems and limitations:** The first GUI attempt failed with an X display error before XQuartz was updated and ready; the successful rerun is the accepted evidence. The upstream demo emits missing-yellow-phase, short-`tau`, collision-teleport, emergency-braking, and deprecated-API warnings. The wrapper records summary metadata and detector outputs but does not persist the full controller time series or stdout/stderr. Python 3.13 satisfies upstream metadata but is not explicitly covered by upstream CI. An unrelated untracked `dashboard/` directory appeared during the task and was not modified, staged, or included.
- **Next step:** Review the upstream warnings and isolate reusable controller-integration patterns before creating any project-owned synthetic scenario; wait for Robert Hilbrich's scope confirmation before formalizing parameters or freezing the experiment protocol.
