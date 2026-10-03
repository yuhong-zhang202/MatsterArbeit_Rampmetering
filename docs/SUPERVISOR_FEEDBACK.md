# Supervisor Feedback

**Last updated:** 2026-09-30
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

### Received 2026-08-25 — Initial Scope, Technical Starting Point, and Timeline

**Source:** `docs/supervision/2026-08-25_robert_hilbrich_reply.md`

**Source-date limitation:** The supplied email body did not include its exact sent date or subject. The record uses the date on which the student supplied the reply.

**Record status:** Current supervisor guidance

#### Explicit Feedback

Robert Hilbrich stated that:

- he would support the student with the master's thesis and welcomed the use of SUMO;
- `sumoITScontrol` is a sensible initial framework because, to his knowledge, there is no comparable overall SUMO framework combining several established control methods with systematic multi-seed evaluation;
- beginning with ALINEA is appropriate because it is established and comparatively manageable;
- the proposed synthetic scenario is sensible and should initially remain simple: one freeway, one on-ramp, and a small upstream urban network with an initially fixed-time traffic signal;
- scanning the uncontrolled traffic-demand grid is a good first step for understanding scenario behaviour, especially near breakdown;
- `qRamp <= C - qMain` may be used as an intentionally simplified starting hypothesis, but actual capacity is variable and unknown, merging affects effective capacity, and capacity drop may reduce outflow after breakdown;
- ramp demand may exceed the admissible inflow and therefore create a queue, while finite ramp storage can require releasing more traffic to protect the subordinate network even when the freeway lacks residual capacity;
- a particularly interesting core question is when ramp metering should be reduced or overridden in favour of the subordinate network;
- the initial car-following choice should be SUMO's standard Krauß model with default parameters; without empirical calibration data, special parameterization should not be used to force desired behaviour;
- the first diagnostic question is whether the selected scenario produces plausible breakdown and capacity drop; if not, possible causes include car following, lane changing and merging, ramp geometry, and demand;
- high-flow vehicle insertion must be configured and validated so that insertion does not cap realized demand; he named `departPos="last"`, `departLane="best"`, and `departSpeed="max"` as example settings;
- the proposed schedule is realistic: an interim presentation to Prof. Nagel around late October or early November, subsequent refinement and official registration, and then the four-month thesis period, implying submission around February or March;
- by the interim presentation, the framework should run, the scenario should be built, and initial uncontrolled-case results should be available so that the research question and scope can be reviewed before registration;
- writing in English would not be a problem for him, but any chair-level or examination-rule requirements must still be checked.

#### Project Relevance

This reply supports the overall working direction and a staged initial scope: `sumoITScontrol`, ALINEA, a deliberately simple synthetic freeway–ramp–urban scenario, and uncontrolled demand-grid exploration before controlled comparisons.

It also sharpens the central research interest toward the finite-storage conflict between protecting freeway flow and avoiding spillback into the subordinate network.

The Krauß defaults and the named departure settings are starting and diagnostic guidance, not empirically validated thesis parameters. The reply does not freeze a formal experiment protocol.

#### Explicitly Unresolved

The reply does not determine:

- the final wording of the research question or thesis title;
- a formal sweet-spot or override rule;
- the exact network geometry, ramp storage, demand ranges, or grid resolution;
- the final metrics, seed count, statistical analysis, or exclusion rules;
- whether the initial model produces plausible breakdown and capacity drop;
- the final scope after the interim presentation;
- whether institutional rules permit the thesis to be written in English.

### 2026-09-30 — Merge validation before an uncontrolled demand grid

**Source:** Robert Hilbrich email dated 2026-09-30 12:57:52 UTC. The original email is retained locally at `docs/supervision/2026-09-30_robert_hilbrich_reply.md` and omitted from public GitHub synchronization; this record preserves the explicit guidance needed for the project.

**Record status:** Current supervisor guidance; the email does not approve an exact new network, demand grid, controller or formal experiment.

#### Explicit Feedback

Robert Hilbrich advised that:

- the fixed 22 s and 28 s green-time programs should not currently be used to establish the A/B/C relationship; pulsed release at qRamp=900 veh/h could create dense vehicle platoons and disturb the mainline more than an open ramp, so fewer ramp vehicles per minute do not necessarily imply less freeway disturbance;
- the freeway and ramp merge should first be checked for correct, capacity-relevant representation: two mainline lanes, a separate ramp acceleration lane creating a short three-lane section, and a return to two lanes after ramp vehicles change lanes into the mainline;
- lane-to-lane connections should preserve both mainline lanes and lead the ramp into its own acceleration lane, rather than directly combining ramp and mainline traffic into one downstream lane at a junction; possible unnecessary mainline use of the acceleration lane and suitable lane-change restrictions should be checked;
- actual mainline insertion should be checked against requested demand, including `departLane`, `departPos`, `departSpeed` and accumulated `departDelay`; `best`/`last`/`max` were examples, not a frozen parameter set;
- after these checks, an uncontrolled `qMain × qRamp` grid should identify where the modeled merge approaches its critical range and breakdown; suitable operating points could then be selected for comparing control methods;
- the previous exploratory work should not be regarded as failed merely because the system's capacity boundary has not yet been located.

#### Project Relevance and Limits

The email establishes an order for the next exploratory checks. It does not confirm that the current model has plausible breakdown, identify its capacity boundary, choose grid values or seed count, validate a controller, mark Stage 6 complete, or freeze `docs/EXPERIMENT_PROTOCOL.md`.
