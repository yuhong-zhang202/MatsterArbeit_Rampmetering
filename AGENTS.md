# Project Agent Instructions

## 1. Project Scope and Document Routing

This repository supports a TU Berlin master's thesis project.

Do not use this file as a source for the current research scope, supervision status, project phase, pending questions, thesis language, or next tasks. These are dynamic and must be obtained from the appropriate project documents.

Use the following documents according to the task:

- Read `docs/PROJECT_STATE.md` when the task depends on the current project status, research scope, blockers, or next steps.
- Read `docs/DECISIONS.md` when the task depends on an accepted research or implementation decision.
- Read `docs/SUPERVISOR_FEEDBACK.md` and the relevant original source under `docs/supervision/` when the task depends on supervisor guidance.
- Read `docs/EXPERIMENT_PROTOCOL.md` before formal simulation work or when evaluating experimental parameters.
- Read `thesis/outline.md` and relevant writing guidance before thesis-structure or thesis-writing tasks.
- Read only the documents relevant to the current task. Do not bulk-read the entire repository without a clear reason.
- If a required document is missing or empty, treat the relevant information as unknown. Do not infer it from old chats, filenames, or AI memory.

## 2. Decision and Approval Boundaries

- Do not independently change the research question, study scope, simulation design, control algorithm, evaluation metrics, formal parameters, or thesis structure.
- Treat AI-generated suggestions as `Proposed` by default.
- Do not promote an item to `User-approved`, `Supervisor-confirmed`, or `Frozen` without explicit supporting evidence and user authorization.
- `Supervisor-confirmed` requires an explicit supervisor statement in an available source.
- Do not interpret the absence of feedback as approval.
- When project documents conflict, report the conflict instead of silently choosing one version.
- Ask the user when missing information would materially affect the result.
- Do not modify `AGENTS.md` unless the user explicitly requests it.

## 3. Research Integrity

- Never fabricate or invent publications, citations, quotations, data, simulation outputs, parameters, software behavior, or supervisor statements.
- AI output is not academic evidence.
- Academic claims must be traceable to genuine sources.
- Do not describe software defaults, provisional assumptions, or AI suggestions as empirically validated or supervisor-approved choices.
- Distinguish clearly between observed simulation results, calculated statistics, assumptions, interpretations, and recommendations.
- Preserve uncertainty and limitations. Do not overstate what a synthetic simulation can establish.
- Keep material AI-assisted work traceable so that its use can be reviewed and disclosed when required.

## 4. File and Data Safety

- Treat `data/raw/` as immutable and read-only.
- Write cleaned, transformed, or aggregated data only to `data/processed/`.
- Write tables to `results/tables/` and figures to `results/figures/`.
- Do not silently overwrite existing datasets, results, figures, or tables.
- Do not delete, move, rename, truncate, or replace original source files without explicit user approval.
- Preserve unrelated user changes and restrict edits to the files required by the task.
- Inspect the existing state before editing. If conflicting or unexpected changes are present, stop and report them.
- Avoid destructive commands and broad filesystem operations.

## 5. Experiment Reproducibility

- Distinguish clearly between environment checks, smoke tests, exploratory runs, pilot experiments, and formal experiments.
- Do not present smoke-test, exploratory, or pilot outputs as thesis evidence.
- Formal experiments require an explicitly frozen `docs/EXPERIMENT_PROTOCOL.md`.
- Every formal run must preserve, where applicable: run ID, timestamp, software versions, configuration snapshot, demand settings, random seed, controller settings, output paths, and run status.
- Controlled and uncontrolled comparisons must use matched conditions and random seeds unless the protocol explicitly states otherwise.
- Never silently exclude failed, incomplete, missing, or anomalous runs.
- Do not draw a formal conclusion from a single stochastic run.
- If reproducibility information is unavailable, report the limitation.

## 6. Implementation and Verification

- Inspect the relevant code, configuration, and existing changes before editing.
- Make the smallest defensible and reversible change that satisfies the task.
- Do not expand the task scope without user approval.
- Do not initialize repositories, install dependencies, change environments, or run large experiment batches unless the task explicitly authorizes it.
- After modifying code or configuration, run the smallest relevant test or smoke test that can validate the change.
- A command completing without an error is not sufficient proof that the scientific behavior is correct.
- Do not claim success without reporting the evidence used for verification.
- If verification cannot be completed, state exactly what remains unverified.
- Apply the documentation updates required by Section 10 after material work.

## 7. Subagent Coordination

- Use the primary agent for ordinary, small, or tightly coupled tasks.
- Use subagents only for clearly bounded work that benefits from independent expertise, parallel reading, testing, or review.
- The `simulation_engineer` may support SUMO, TraCI, sumoITScontrol, implementation, configuration, and testing, but may not make research decisions independently.
- The `scientific_reviewer` must remain read-only and focus on methodological weaknesses, unsupported assumptions, confounding factors, reproducibility risks, and overextended conclusions.
- The `data_analyst` must treat raw data as read-only and write derived data and outputs only to their designated directories.
- Do not allow multiple agents to edit the same file concurrently.
- Prefer read-only parallel review over parallel write-heavy work.
- The primary agent must reconcile disagreements and report them to the user. Do not resolve scientific disagreements through majority voting.
- Subagent output remains advisory and does not automatically become a project decision.

### Mandatory Routing Check

Before every material task, the primary agent must classify the task before doing substantive work:

```text
Subagent Routing Check:
- Does this task involve simulation implementation, configuration, environment setup, debugging, testing, or simulation execution?
- Does this task involve data parsing, cleaning, aggregation, statistics, tables, figures, or result validation?
- Does this task involve research design, protocol changes, scientific validity, interpretation, or thesis-level claims?
```

If the answer is yes, the corresponding project-scoped custom agent must be used.

### Required Routing

The primary agent MUST use `simulation_engineer` for material tasks involving:

- SUMO, TraCI, or sumoITScontrol installation or environment checks;
- simulation networks, routes, detectors, traffic lights, controllers, or configuration;
- simulation code, experiment runners, parameter scans, debugging, or tests;
- smoke tests, pilot simulations, or formal simulation runs;
- technical simulation-performance or compatibility problems.

The primary agent MUST use `data_analyst` for material tasks involving:

- simulation-output parsing or schema validation;
- data cleaning, transformation, or aggregation;
- random-seed and scenario-coverage checks;
- statistics, uncertainty, robustness, or anomaly analysis;
- result tables, heatmaps, figures, or visualizations;
- validation of processed results.

The primary agent MUST use `scientific_reviewer` for material tasks involving:

- research questions, hypotheses, or methodological choices;
- experimental design or changes to `docs/EXPERIMENT_PROTOCOL.md`;
- demand ranges, metrics, seeds, warm-up periods, breakdown definitions, or exclusion rules;
- scientific interpretation of simulation results;
- formal sweet-spot identification;
- claims intended for the thesis;
- freezing a protocol or marking an important research milestone complete;
- final review of simulation or analysis work that affects scientific validity.

### Combined Workflows

Use the following default sequence:

```text
Environment setup or technical smoke test:
simulation_engineer

Experiment-pipeline design:
simulation_engineer -> scientific_reviewer

Formal data analysis:
data_analyst -> scientific_reviewer

End-to-end formal experiment:
simulation_engineer -> data_analyst -> scientific_reviewer
```

Wait for each required agent before proceeding to the next stage when later work depends on earlier output.

Do not allow write-capable agents to edit overlapping files concurrently.

Prefer sequential work for write-heavy tasks. Parallel work is allowed only for independent read-only investigations or clearly non-overlapping scopes.

### Context Requirement

Every custom subagent must perform the Context Preflight defined in its project agent instructions before substantive work.

The primary agent must provide the subagent with:

- a bounded task;
- relevant input paths;
- allowed write paths;
- prohibited changes;
- expected verification;
- required output or report.

The subagent must not work from the delegated prompt alone without reading the required project-state files.

### Failure and Override Rules

- If a required custom agent is unavailable or fails to start, the primary agent must not silently replace it.
- Report the failure and the unreviewed scope to the user.
- A model-availability failure may use the documented inheritance fallback.
- Explicit user instructions may narrow or disable delegation for a specific task.
- Routine discussion, file organization, status recording, supervisor-feedback recording, and purely mechanical formatting do not require a subagent unless they contain substantive simulation, analysis, or scientific decisions.
- Do not spawn all agents automatically for trivial tasks.

### Final Reporting

After every material task, the primary agent must include:

```text
Subagent routing:
- simulation_engineer: used / not required / unavailable
- data_analyst: used / not required / unavailable
- scientific_reviewer: used / not required / unavailable
```

For every used agent, briefly state:

- assigned scope;
- result;
- whether its findings were addressed;
- remaining limitations.

Do not claim that required scientific review occurred if the reviewer was not successfully run.

## 8. Communication and Task Reporting

- Communicate with the user in Chinese by default.
- Use English for code, variable names, configuration fields, filenames created for programmatic use, and code comments.
- Distinguish facts, assumptions, proposals, and unresolved questions.
- Explain technical issues in clear language without hiding relevant uncertainty.
- At the end of a material task, report:
  - what was changed;
  - which files were affected;
  - what verification was performed;
  - any failures, anomalies, or limitations;
  - unresolved questions and the safest next step.
- Summarize relevant evidence instead of flooding the main conversation with raw logs.

## 9. Maintenance

- Keep this file concise and limited to stable, repeatedly applicable rules.
- Store changing project status in `docs/PROJECT_STATE.md`, not here.
- Store durable decisions in `docs/DECISIONS.md`, not here.
- Store supervisor guidance in `docs/SUPERVISOR_FEEDBACK.md`, not here.
- Store formal experiment settings in `docs/EXPERIMENT_PROTOCOL.md`, not here.
- Add or revise rules only when the user explicitly requests it, especially after a repeated workflow problem has been identified.

## 10. Documentation Maintenance Triggers

After every substantive task, perform a Documentation Impact Check before reporting completion.

A substantive task includes environment setup, dependency changes, code or configuration changes, simulations, data processing, statistical analysis, figure generation, thesis-structure changes, or the receipt of new project evidence. Ordinary discussion, explanation, read-only inspection without new findings, and unchanged-status checks do not require documentation updates.

Apply these triggers:

- Update `docs/PROJECT_STATE.md` when the current phase, working scope, supervision status, blockers, pending questions, formal-experiment status, or next actions change.
- Update `docs/SUPERVISOR_FEEDBACK.md` only when new explicit supervisor feedback is available from an identifiable email, meeting note, or other source. Preserve the source reference and distinguish explicit feedback from interpretation.
- Update `docs/DECISIONS.md` only after the user explicitly approves recording a decision or changing its status.
- Update `docs/EXPERIMENT_PROTOCOL.md` only with explicit user authorization. Never change a frozen protocol silently.
- Append a concise entry to `docs/WORKLOG.md` after material environment, code, simulation, analysis, or artifact work. If the file is empty and no template has been approved, report that logging is pending instead of inventing a format.
- Update `README.md` only when project structure, installation steps, dependencies, setup commands, execution commands, or user-facing project usage change.
- Update `thesis/outline.md` only after the user approves a thesis-structure change.
- Update `AGENTS.md` only when the user explicitly requests it.

Routine factual updates to `PROJECT_STATE.md`, `WORKLOG.md`, and applicable `README.md` content are considered part of the substantive task and do not require a separate reminder. Decision records, protocol changes, thesis-structure changes, and agent-rule changes still require the approvals defined above.

Make documentation updates minimal and evidence-based. Do not rewrite an entire document when a small patch is sufficient. Do not add a timestamp when nothing changed. In the final task report, identify which documentation files were updated and why.
