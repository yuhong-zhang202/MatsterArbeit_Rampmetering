# Project State

**Last updated:** 2026-08-22  
**Document role:** Current project snapshot. Replace stale operational information instead of using this file as a decision history.

## Current Phase

Project setup, collaboration governance, and research-scope confirmation.

No formal experiment protocol is frozen, and no formal thesis experiment has started.

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

## Work That May Proceed Now

- maintain the local project structure and collaboration rules;
- archive original project and supervisor materials;
- install and verify SUMO, Python, and `sumoITScontrol`;
- read the core paper and official documentation needed for initial setup;
- run the official ALINEA example;
- perform clearly labelled environment checks and smoke tests.

## Work Deferred Until Scope Confirmation

- full demand-grid experiments;
- formal data production;
- freezing `docs/EXPERIMENT_PROTOCOL.md`;
- treating default model parameters as scientifically justified choices;
- drawing thesis conclusions from preliminary runs;
- large-scale drafting of results or discussion chapters.

## Next Actions

1. Complete the initial project-management documents and source-material organization.
2. Verify the local environment and run the official ALINEA example on the Mac.
3. Update this document after Robert Hilbrich replies and before the formal experimental design is frozen.
