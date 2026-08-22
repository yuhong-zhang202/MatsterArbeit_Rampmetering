# Supervisor Feedback

**Last updated:** 2026-08-22  
**Document role:** Evidence-based record of explicit supervisor feedback. Current operational status belongs in `PROJECT_STATE.md`.

## Recording Rules

- Record only feedback that can be traced to an identifiable email, meeting note, or other source.
- Separate explicit supervisor statements from student or AI interpretation.
- Preserve the date and source location.
- Do not interpret silence as approval.
- Historical feedback remains recorded even when the supervision arrangement changes.
- Current decisions derived from feedback belong in `DECISIONS.md` only after approval.

## Peter Wagner

### 2026-06-18 — Initial Topic and Supervision Proposal

**Source:** `docs/supervision/Re: Anfrage zur Betreuung einer Abschlussarbeit (对话).pdf`, pages 1–2  
**Record status:** Historical supervisor guidance

#### Explicit Feedback

Peter Wagner stated that:

- he could in principle imagine supervising the thesis;
- it was then unclear whether TU Berlin rules would allow him to act as the official first examiner;
- if that were not possible, Kai Nagel could take over the official role while Peter Wagner provided the substantive supervision;
- the student was free to propose another personally interesting topic;
- the ramp-metering sweet spot was a proposal rather than a mandatory topic;
- the core problem was the balance between too much ramp restriction, which causes queues to spill back into the subordinate network, and too little restriction, which causes congestion on the freeway;
- the topic could be investigated with microscopic simulation in SUMO;
- the open-source `sumoITScontrol` algorithms could be tested within a master’s thesis.

#### Project Relevance

This email established the original topic direction and the central freeway-versus-urban-network trade-off.

It did not define a final research question, experimental protocol, evaluation metric, or controller configuration.

### 2026-07-15 — Recommended Starting Procedure

**Source:** `docs/supervision/Re: Anfrage zur Betreuung einer Abschlussarbeit (对话).pdf`, pages 3–4  
**Record status:** Historical supervisor guidance

#### Explicit Feedback

Peter Wagner recommended that:

- the student first work into the topic and register the thesis after becoming sufficiently confident with it;
- under the arrangement at that time, Kai Nagel would be the official first examiner and Peter Wagner would provide the actual supervision;
- the student should begin with the `sumoITScontrol` paper;
- the student should get the provided algorithm implementation to run;
- a synthetic example should be used as the starting point;
- `qRamp` and `qMain` should first be systematically scanned;
- travel times, speeds, densities, and capacity limits should be examined;
- the relation `qRamp + qMain <= qCap` could serve as an illustrative simplest-case starting point rather than a guaranteed empirical result;
- the control algorithm should then be added to determine whether it improves the uncontrolled case;
- particular attention should be paid to what happens in a connected urban road network;
- the details of the urban-network component should be determined later through joint discussion;
- real German examples should be examined for orientation;
- he did not then have real data available and warned that real data would be a challenge of its own.

#### Project Relevance

This email defines a clear preliminary workflow:

1. understand and run `sumoITScontrol`;
2. construct a synthetic baseline;
3. scan `qMain × qRamp`;
4. identify capacity behaviour;
5. add control;
6. compare controlled and uncontrolled cases;
7. examine effects on the connected urban network.

#### Explicitly Unresolved

The email did not determine:

- that ALINEA must be the only or final algorithm;
- the formal sweet-spot definition;
- the final urban-network geometry;
- the car-following model or capacity-drop parameterization;
- the demand ranges or grid resolution;
- the number of random seeds;
- the final performance indicators;
- the thesis language.

### 2026-07-18 — Student Reply

The message dated 2026-07-18 is the student’s proposed implementation plan, not supervisor feedback.

It must not be treated as supervisor confirmation.

## Robert Hilbrich

No explicit feedback from Robert Hilbrich is currently available in the project records.

**Current status:** `Awaiting response`

When a reply or meeting note becomes available:

1. archive the original source under `docs/supervision/`;
2. add a dated evidence-based entry here;
3. distinguish explicit feedback from interpretation;
4. update `PROJECT_STATE.md` if the current scope, blockers, or next steps change;
5. update `DECISIONS.md` only after the user approves recording a resulting decision.
