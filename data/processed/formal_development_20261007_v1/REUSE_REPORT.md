# Independent reuse eligibility audit

Classification: DEVELOPMENT, not formal inference. Date:2026-10-07.

**Existing-data gate: 9/9 PASS**: six OPEN and three R900 V15. All raw manifest hashes, receipt/card/input hashes, network/binary, time/seed/model, explicit speed factors/departure semantics, fixed city signal and detector definitions match their contracts. R750 cohorts have3950 planned vehicles, R9004050; all nine runs completely inserted/arrived by4200 with no collision/teleport/discard or SUMO warning.

Independent planned-cohort tripinfo costs equal cumulative summary source/in-network/total integrals (largest floating residual2.3e-13s). Completed/unfinished/never-inserted known examples pass. The three old T1 log/event/E1 checks additionally reproduce all600 crossings,238 XML lane windows and nominal clip[300,900], without applying the historical1200 checker.

**Reuse condition still required:** a new wrapper must preserve input and T1 execution semantics; one representative new OPEN/neutrality comparison will qualify that addition. Do not confuse old data validity with proof that new code is neutral. The coverage table therefore retains a pending-wrapper label.

**New controlled combinations required:** R900 T2 seeds17/23/42; R750 T1 andT2 seeds17/23/42. New wrapper OPEN R900S17 is an additional baseline/qualification launch; it is not a second T1 or T2 combination. Failed starts/technical retries remain separate from18-cell coverage.

Sources: `reuse_audit.json`, `reuse_integral_audit.json`, `audit_reuse.py`, `audit_integral.py`, `ANALYSIS_CONTRACT.md`; initial coverage and independent class costs are under results/tables/formal_development_20261007_v1/. All originals remain unchanged.

Limit: historical safety statements are supported by bound existing gate reports plus independent log arithmetic; this audit does not rerun getSecureGap or prove every subsecond event. New runs require their own pre600, feedback, service, queue-state and endpoint checks. No new simulation or formal significance test was performed.
