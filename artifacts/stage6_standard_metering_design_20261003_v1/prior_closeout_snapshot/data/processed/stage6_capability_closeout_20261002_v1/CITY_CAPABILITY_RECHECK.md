# Historical V2 city-side capability: bounded independent recheck

Date: 2026-10-02. Scope: exploratory, read-only raw reanalysis of matched default V2 A/OPEN versus B22, seed17. No original nonpairable RI3350, no sigma0 and no new simulations. This is an evidence-applicability audit, not a controller-benefit or sweet-spot claim.

## Context and source boundaries

AGENTS, current PROJECT_STATE, DECISIONS, empty EXPERIMENT_PROTOCOL, recent WORKLOG and Robert's archived 2026-09-30 reply were reviewed. The project is paused after uncontrolled localization; Robert does not ask for further forced fixed-time A/B/C. Existing independent B scientific review and FCD-continuity supplement were read first. They already establish matched exogenous demand, exact pre540 trajectories and complete cohorts; the present bounded check independently reproduces the city-side quantities and a small physical context.

Sources: `data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/{A,B}/outputs/` (`B` is B22). Five files per arm were hash/size-matched to each execution receipt: tripinfo, FCD, TLS states, ramp-storage E2 and shared-boundary E2. Each FCD has 2700 ordered seconds, 1861 IDs matching tripinfo, continuous per-ID observations and correct departure/arrival endpoints. All cohorts arrive. No exclusions. Script and source hashes: `city_recheck.json`; reproducible script: `recheck_city.py` in this directory. Only new derived artifacts were written.

## Reproduced empirical observations

Complete-cohort mean network residence (arrival minus departure) is R: A88.312500s / B242.133333s, difference +153.820833s (240 vehicles per arm); U: A64.913333s / B91.386667s, difference +26.473333s (150 per arm). Every R/U vehicle has departDelay0 in both arms. Thus the measured excess is internal residence, not external insertion wait or end-censoring.

In the fixed half-open active window [540,1500), U shared-approach residence is A2277 versus B3491 vehicle-seconds. The previously reported **987** means B U samples with speed **<1.389m/s (about5km/h)**, versus A0. It is neither <5m/s nor a stop definition. Separately, speed<0.1m/s gives B508 stopped U vehicle-seconds versus A0. Shared R slow samples under the same1.389m/s cutoff are A0/B2487, and stopped samples A0/B1261.

For the whole2700s E2 record, B has shared jam-positive22/90 thirty-second bins (maximum19 jammed vehicles; first990–1020), and ramp-storage44/90 (maximum27; first570–600). A has zero for both. Detector jam counts are mixed-class and restricted to their detector coverage; they are not automatically a continuous physical queue front across all internal connectors.

## Physical context and alternatives

Urban TLS program/phase/state is exactly identical in all2700 labels between A and B. Ramp TLS differs as intended: A continuouslyG, B990G/135y/1575r. Of B's987 slow U vehicle-seconds on the shared lane,980 coincide with at least one slow R on that same lane;902 have R as the nearest observed vehicle ahead on the same lane. These are spatial co-occurrence and nearest-observed-ahead descriptions, not a TraCI-reported unique braking-cause identification.

511 of987 U slow vehicle-seconds occur while the urban entry movement has green;476 occur during red/yellow. Example t1064: U_flow.103 is at shared pos216.60m, speed1.25m/s; R_flow.122 is ahead at225.04m, speed0.48m/s (front-position gap8.44m); urban stateGr, ramp state r. This selected example is retained with adjacent snapshots in JSON.

Consequently, external insertion waiting is ruled out for these R/U costs, and “only direct stopping at the urban red light” is not a sufficient account of the observed shared-lane phenomenon. The configured urban signal and priority arrangement are common to A/B. Their interaction with changed queues/arrival timing may contribute and has not been causally decomposed. No claim is made that every second of additional U residence is uniquely caused by ramp spillback, nor that all priority or vehicle-following alternatives are eliminated.

## Applicable conclusion and unresolved limits

The matched historical V2 series independently supports city-side scenario capability: substantial internal ramp cost accompanies shared-lane R/U low-speed/stopped exposure and additional internal U residence. These observations can be used as a qualified city-side capability layer alongside the new uncontrolled mainline-state evidence, provided the separate engineering transfer check confirms relevant geometry/connections/routes/signals remain applicable.

It does not establish that the new R900 uncontrolled point has the same urban effect, that one operating point simultaneously demonstrates both sides, that fixed B22 protects M, that a continuous meter-anchored queue spans all connectors, or that a feasible sweet spot exists. ALINEA efficacy and formal performance tolerances remain untested/unfrozen. Original negative B22 and nonpairable RI3350 dispositions are unchanged. The scoped evidence is enough for a capability discussion; overall scientific acceptance remains the primary agent/scientific review and user decision.

## Derived artifacts

- `city_recheck.json`: raw-bound numbers, validation, TLS comparison and three FCD snapshots.
- `results/tables/stage6_capability_closeout_20261002_v1/tripinfo_recheck.csv`.
- `results/tables/stage6_capability_closeout_20261002_v1/lane_exposure_recheck_complete.csv`: explicit zeros for unobserved slow/stopped quantities; the initial sparse CSV is preserved.
- `results/tables/stage6_capability_closeout_20261002_v1/e2_recheck.csv`.
