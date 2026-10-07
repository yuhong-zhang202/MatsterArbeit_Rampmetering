# Bounded development trial — 2026-10-07

Status: completed / awaiting user and supervisor discussion. All18 comparison cells complete; final independent scientific PASS_FOR_DEVELOPMENT_CLOSEOUT. Service capability remains NOT_QUALIFIED; no further launch or formal experiment authorization.

## Purpose and source

This trial checks implementation, measurement, completion and descriptive effects before supervisor discussion. It does not reopen Stage 6 or seek a formally accepted sweet spot. The user authorizes development implementation, the temporary queue parameters after engineering/scientific review, bounded simulation execution, ordinary technical repair and independent analysis.

The complete [user objective](../../artifacts/formal_development_20261007_v1/AUTHORIZATION.md) is an exact local copy of the supplied attachment. SHA-256: `19c0dea1120384913bcac46f987070c9ecf78b0d88e0cfac12c37e217cf356d9`. D-019 records only this actual authorization. The [original design draft](../正式实验设计草案v1.md) is preserved; development choices are not formal or supervisor-approved parameters.

## Fixed scope

- M3600, R750/900, U360, X180 veh/h; seeds17/23/42 only.
- T0 OPEN, T1 existing V15 ALINEA/actuator, T2 the same plus one simple threshold/hysteresis queue override.
- T1 target11%, gain70 veh/h/percentage-point, feedback30s, rates300/900/900 veh/h, step1s. T2 rQ900; bounded nominal ALINEA state continues without feedback of the final override command.
- M/U/X requests [0,3000); R and control start600, R requests end3000; diagnostic window[1200,3000); common endpoint4200s.
- At most12 development control combinations and6 corresponding OPEN baselines, including qualified reuse. Actual technical attempts are separately recorded; there is no authority to add demand, seeds, candidates or relax gates.
- No R825/M3500, fresh formal seeds, second ALINEA candidate, 60/90 formal matrix, protocol edits, email, resource purchase or outcome-driven retuning.

## Sequence and responsibility

1. Independent data review binds the six old OPEN and three old R900 V15 runs to inputs/raw and decides reuse. Engineering preserves old code/raw and prepares an independent runner, exact new queue contract and minimal offline checks.
2. Before the first start, lock the queue parameters, measurement/time-order contract, resource envelope and hashes. Scientific review then releases an exact eligible launch.
3. S17 R900: establish T0/T1 equivalence and audit T2. Then S17 R750: establish T0/T1 and audit T2. New-run full-green neutrality should double as an OPEN baseline where equivalent, rather than two duplicate starts.
4. After the two S17 technical/data gates, complete S23/S42 under unchanged qualified policy. Poor effects or unfinished vehicles do not stop this sequence; implementation/data errors require evidence-based repair first.
5. Independent analysis and scientific review produce a development summary and formal-design recommendations. Stop at development completed / awaiting user and supervisor discussion.

simulation_engineer owns the independent code and engineering artifacts, and launches authorized new raw output. data_analyst owns new processed/tables/figures and independent checks. scientific_reviewer remains read-only. The primary agent owns this document, state/authorization/log records and final handoff.

## Measurement and qualification rules

Planned M/R/U/X cohorts remain complete, including source waiting and unfinished vehicles. Each demand/seed shares identical requests, network, urban signal, behavior, simulation seed and endpoint across treatments. Full lifecycle cost is used when all arrive; otherwise restricted cost through4200 and endpoint positions/queues are retained. No treatment receives extra green or extra time.

Queue-risk observations and continuous physical queue evidence are separate quantities. Include the relevant internal connection; do not sum disjoint E2 measurements into a continuous queue. Preserve the existing strict≥30s chain definition and its negative evidence. Actual final commands, stop-line crossings, receiver obstruction, safety denial and no-demand periods are separately recorded.

Applicable fixed300s engineering windows compare integrated final command with actual crossings. Windows without continuous demand do not prove service capacity and are not automatic policy failures; blocked eligible windows cannot be silently removed. Outcome changes are descriptive within-demand paired differences, without formal significance or acceptance thresholds.

## Required deliverables and completion evidence

| Deliverable | Evidence required |
|---|---|
| Pre-start plan and parameters | Exact queue rule, geometry/old-trajectory rationale, units, time order, source/input hashes, pre-start engineering/science review |
| Coverage | 18 demand×treatment×seed entries, source/new/reused/failed/not-executed classifications |
| Execution/repair ledger | All physical attempts, purpose/revision/input/seed/wall time/bytes/failure/replacement; independent coverage ledger |
| Data and plots | Class costs/source/net decomposition, mainline space-time, command/discharge/queue/override plots, endpoint residuals |
| Independent checks | Raw-bound input matching, lifecycle/reconciliation, new policy/time-order/measurement qualification and limits |
| Final summary | Reliable components; T2 mechanics/effects; completion status; formal-design changes;3–5 questions for Robert |
| Documentation | PROJECT_STATE/WORKLOG updated, D-019 limited to authorization, draft and empty protocol preserved |

## Progress

At initial registration: source copied exactly; engineering implementation/resource/parameter work and independent reuse audit are underway. No SUMO start is released at this checkpoint. Subsequent exact engineering, scientific, data and final-summary documents provide completion evidence; this initial entry is not a completion claim.


### FIX02 progress — 2026-10-07

The pre-repair checkpoint is preserved in the independent DATA_CHECKPOINT_REPORT. The R750/S17 failure led to an authorized minimum safety-code correction,15 passing offline tests and exact scientific release. Corrected T1 A03 completed4200s and passed independent data/observed safety checks; its six service windows remain NOT_QUALIFIED under10%. All four old controlled outcomes are non-equivalent under the corrected guard and cannot fill the corrected policy comparison. Six OPEN slots remain reusable under the reviewed NOOP equivalence. All four S17 replacements now pass independent data/observed safety/rule checks; all24 supplied service windows remain NOT_QUALIFIED. Corrected coverage contains6 OPEN plus4 controls. The remaining8 S23/S42 cards have passed exact independent scientific review and are released in fixed order with a persisted independent gate after each run. Full sources, failures, review and gates are under artifacts/formal_development_20261007_v1 and data/processed/formal_development_20261007_v1.


### Final closeout — 2026-10-07

All18 cells are complete under a common corrected control version. Independent data and final scientific review pass for development delivery;71/72 supplied rate windows fail and all12 control-level service qualifications remain NOT_QUALIFIED. Full report, tables,19figures, all16attempts and resource estimates: [development summary](DEVELOPMENT_TRIAL_SUMMARY_20261007.md). Earlier progress entries above are historical; they do not supersede this closeout. Stop at discussion, with Stage6closed and formal protocol0B/unfrozen.
