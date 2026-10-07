# Bounded formal-development analysis contract

Status: DEVELOPMENT ONLY, 2026-10-07. Source authorization: `/Users/yuhongzhang/.codex/attachments/a4c79b11-6f3b-4233-846d-15b3cc796dcb/goal-objective.md`. No formal inference or sweet-spot acceptance threshold is introduced.

## Coverage and eligibility

Coverage is M3600, R750/R900, U360/X180, seeds17/23/42, T0 OPEN / T1 V15 / T2 same V15 plus prospectively registered queue protection. Counts are M3000/U300/X150, R500 at R750 and R600 at R900. Eighteen condition-treatment-seed combinations must be retained. Six existing OPEN and three existing R900 T1 runs may be reused only under unchanged input/measurement semantics and equivalent T1 implementation; nine controlled combinations remain new.

`reuse_audit.py` independently validates all existing cards, receipts, raw manifest files, demand identities and attributes, SUMO/network hashes, additional measurement definitions, urban signal input, time/seed/processing, tripinfo and endpoint summary. `audit_integral.py` separately verifies aggregate time costs against cumulative summary counts. Existing card plan pointers may be historically moved; receipt-bound inputs and raw are the evidence, not an assumption that old documentation paths still exist.

## Per-run and paired checks

1. Check exact release/card/input/raw identities before parsing; preserve technical attempts, failures and replacements separately from valid eighteen-combination coverage. Missing or failed runs remain visible.
2. T=4200, loading M/U/X[0,3000), R[600,3000), evaluation[1200,3000), step1s. Paired plans include IDs, route/type, requested depart semantics and explicit speedFactor; actual departure is an outcome. Require input equality and pre600 trajectory equivalence, including any new all-green wrapper qualification.
3. Reconcile planned/inserted/arrived/unfinished/undeparted for each class. For each planned ID compute S=min(a,T)-p, external=min(d,T)-p, network=min(a,T)-min(d,T), with unavailable future departure/arrival infinite. Report mean per planned vehicle and total seconds. Missing observed segments from a technical failure are not filled to T. Genuine unfinished traffic at T is retained; no completed-only means.
4. Independently compare full cohort costs with cumulative summary integrals; check one-second FCD/summary/controller and fixed detector interval coverage, identity duplicates, raw warnings/collision/teleport/discards, plus endpoint unfinished positions and lane/class distributions.
5. Match actual E1 XML to feedback lane intervals (original 0.0050001 percentage-point rounding tolerance), reconstruct complete 30s means, nominal ALINEA clip[300,900] at target11/K70, update630..4170 and initial900. T2 nominal state updates independently; final command=max(nominal,900) while protection active. Audit trigger/release/hysteresis from the registered observations without selecting thresholds after outcomes.
6. Audit unique actual stopline crossings against FCD and recorded internal-lane transitions, no red/multiple/wrong-front/unsafe interlock crossings, safety formulas and credit conservation. No queue and receiver obstruction/safety rejection are distinct. In each fixed 300s evaluation window, integrate FINAL applied command versus actual crossing IDs; continuous storage availability defines rate qualification. Retain every window, including blocked and untested no-demand windows; original 10% engineering screen is not a traffic-benefit threshold.
7. Retain existing mainline lane/internal coverage and 30s-by100m time-space bins; show equivalent panels with shared limits and independent source mapping. Velocity is a state diagnostic; changing vehicle-second denominators are retained.
8. Shared R/U slow(<1.389m/s) and stopped(<0.1m/s) observations, U during urban green, nearest same-lane R ahead are separate overlapping exposures, not additive causal delays. Use existing meter-anchored body/gap operational-chain definition and continuous>=30s episode rule unchanged. Include shared/internal/storage lengths and body positions. Zero strict episodes remain a negative result rather than a trigger to relax the rule.
9. For T2 versus T1 and each control versus T0, report per-seed class and total differences and descriptive figures. No p-values, confidence intervals, population breakdown probability or numerical sweet-spot acceptance test.

## Outputs and limits

Exclusive derived write locations: `data/processed/formal_development_20261007_v1/`, `results/tables/formal_development_20261007_v1/`, `results/figures/formal_development_20261007_v1/`. Raw is immutable. Preserve source SHA, parser SHA, versions, filters, counts and coverage status. Stop expansion on actual technical/data failures; absence of traffic benefit or uncleared vehicles is a reportable valid result, not a reason to tune parameters or rerun seeds.

The legacy `standard_metering_analysis_20261003/analysis.py` generic algebra checker still clips at1200 and paired class helper assumes R600; these helpers must not be silently applied to current900 cap/R750 cohort. Parameterize an independent adapter in this exclusive derived directory; do not modify the historical source or the engineer's implementation.
