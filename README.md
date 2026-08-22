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
