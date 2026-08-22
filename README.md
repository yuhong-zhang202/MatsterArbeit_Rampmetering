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
