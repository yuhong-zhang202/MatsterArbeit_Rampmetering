# Project State

**Last updated:** 2026-08-23
**Document role:** Current project snapshot. Replace stale operational information instead of using this file as a decision history.

## Current Phase

Project setup, collaboration governance, and research-scope confirmation.

No formal experiment protocol is frozen, and no formal thesis experiment has started.

The local technical environment and the fixed upstream ALINEA example have completed a technical smoke test. This does not change the pending research scope or formal experiment status.

## Current Technical Environment

- macOS 15.3 on Apple Silicon (Apple M3, arm64).
- SUMO and `sumo-gui` 1.26.0 from the EclipseSUMO macOS Framework.
- Session-level `SUMO_HOME`: `/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo`.
- Project `.venv`: Python 3.13.0 with `sumoITScontrol` 0.1.0, TraCI 1.26.0, and sumolib 1.26.0.
- Fixed upstream smoke-test source: `sumoITScontrol` tag `v0.1.0`, commit `5776c6c79a888a37e55079db63eedc7db0570863`.

## Technical Smoke-Test Status

- Static input, checksum, import, and dependency validation passed.
- The ALINEA GUI run completed with reliable SUMO-generated visual evidence: at simulation time 600 s the scene contained 47 vehicles and traffic light `J0` reported state `G`.
- The completed GUI run executed 8,400 simulation steps, called `execute_control(...)` 8,400 times, and recorded 69 controller updates.
- Headless runs with seeds 2 and 3 both exited with status 0 and completed the same 8,400-step control chain.
- All runtime models, detector XML files, summaries, and GUI evidence were written under `/private/tmp`; no smoke-test output was written to `data/raw/` or used as thesis evidence.
- The upstream example emits technical warnings, including missing yellow phases, vehicle `tau` below the simulation step, collision teleports, emergency braking, and use of the deprecated TraCI `getCurrentTime()` API. These warnings did not prevent the smoke test from completing, but the upstream example must not be reused as a formal experiment configuration without separate review and correction.

## Current Working Topic

Use SUMO and `sumoITScontrol` to investigate the sweet spot of freeway ramp metering: the balance between preventing congestion on the freeway and avoiding queue spillback into the connected urban road network.

**Status:** `Proposed — pending confirmation from Robert Hilbrich`

## Current Supervision Situation

- **Robert Hilbrich:** Current day-to-day supervisor, as reported by the student. The proposed research approach is awaiting his response.
- **Kai Nagel:** Expected to participate in the interim presentation and final defense, as reported by the student.
- **Peter Wagner:** Originally proposed and supervised the topic but is no longer able to continue supervising for health reasons, as reported by the student. His earlier emails remain historical project guidance and do not constitute Robert Hilbrich’s approval.

## Historical Research Starting Point Confirmed by Peter Wagner

Peter Wagner explicitly recommended:

- reading the `sumoITScontrol` paper and getting its algorithm implementation to run;
- beginning with a synthetic SUMO example;
- scanning `qMain` and `qRamp`;
- examining travel times, speeds, densities, and capacity limits;
- adding a ramp-metering algorithm after establishing the uncontrolled baseline;
- checking whether control improves the uncontrolled case;
- paying particular attention to effects in a connected urban road network;
- determining the urban-network details later through discussion;
- examining real German examples while remaining cautious about the difficulty of obtaining and using real data.

These points are historical guidance from Peter Wagner. They are not equivalent to confirmation by the current supervisor.

## Current Working Concept Pending Confirmation

The current project concept proposes:

- using ALINEA as the primary ramp-metering algorithm;
- building a synthetic system containing a freeway mainline, an entrance ramp, and a connected urban road component;
- scanning the `qMain × qRamp` demand space;
- comparing uncontrolled and controlled cases under matched conditions;
- separately accounting for mainline vehicles, ramp vehicles, and unrelated urban through-traffic;
- investigating controller parameters such as target occupancy;
- using multiple random seeds;
- identifying regions where control is beneficial, ineffective, or harmful;
- defining and locating a system-level sweet spot using total system loss and group-specific effects.

These elements remain provisional until they are confirmed or revised with Robert Hilbrich.

## Formal Decisions

No formal research decisions are currently recorded.

`docs/DECISIONS.md` should remain empty until an explicit decision is approved for recording.

## Formal Experiment Status

- No formal experiment protocol is frozen.
- No formal experiment batch has started.
- Environment checks, official examples, exploratory runs, and smoke tests are not formal thesis experiments.
- Outputs from such preliminary runs must not be presented as thesis evidence.

## Pending Supervisor Confirmation

The following issues are awaiting confirmation or discussion with Robert Hilbrich:

- whether the overall research approach and scope are appropriate;
- the car-following model and treatment of capacity drop;
- the formal definition and metrics of the sweet spot;
- the required depth and complexity of the connected urban network;
- the formal experimental parameters, ranges, and replication design;
- the thesis language;
- the timetable, interim presentation, and related organizational arrangements.

## Current Blocker

Robert Hilbrich has not yet responded to the proposed research approach.

This does not block reversible technical preparation, but it does block freezing the final scientific design.

There is no remaining blocker to reproducing the fixed technical smoke test. The upstream demo warnings remain technical limitations, and the macOS GUI requires a working XQuartz display.

## Work That May Proceed Now

- maintain the local project structure and collaboration rules;
- archive original project and supervisor materials;
- read the core paper and official documentation needed for initial setup;
- review the upstream ALINEA example warnings and decide the smallest technically defensible corrections for a future project-owned scenario;
- repeat the fixed environment check or smoke test when tool versions change.

## Work Deferred Until Scope Confirmation

- full demand-grid experiments;
- formal data production;
- freezing `docs/EXPERIMENT_PROTOCOL.md`;
- treating default model parameters as scientifically justified choices;
- drawing thesis conclusions from preliminary runs;
- large-scale drafting of results or discussion chapters.

## Next Actions

1. Review and document the upstream demo warnings before using any part of it as the basis for a project-owned scenario.
2. Continue reading the core `sumoITScontrol` paper and relevant official SUMO documentation without treating example settings as approved parameters.
3. Update the research scope after Robert Hilbrich replies, then design and freeze a formal experiment protocol before producing thesis evidence.
