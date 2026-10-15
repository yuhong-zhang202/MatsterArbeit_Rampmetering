# Exact two-card scientific review V1: release held

2026-10-14. Root records the read-only reviewer finding before any new native launch.

**STOP: current136-source cards cannot be released. One Major affects the second-run resource audit.** No native test or production-budget/guard change is needed to repair it.

## Major: aggregate usage tested against the single-run limit

New `scripts/cumulative_full_catalogue_followup_audit_20261014_v1/actual.py`, reviewed line154, checks `elapsed > 300 or before['charged_monitored_s'] + elapsed > 300`. Production budget's charged_monitored_s accumulates the two new identities; its aggregate limit is600. Thus180 seconds previously plus180 seconds now incorrectly becomes RESOURCE_CAP_OBSERVED_EXCEEDED even though both single and combined limits are respected.

Minimal correction: obtain the single300 and aggregate600 limits from the exact card separately. Add one affected regression with nonzero history180+180PASS, single-run over300 rejection and aggregate over600 rejection. Preserve oldreader/card/source evidence; updated reader needs new exact source/card binding and affected independent review. Do not rerun the broad suite, modify productionbudget/watchdog, guard, parameters or SUMO. User continuing authority covers this technical repair without another reply.

## Other checks and boundaries

Context preflight complete. All27data binder entries and136sources forbothcards match. Bridge differs only in profile/budget imports and normal-end dynamicpartial permission; early anomaly/UNKNOWN still stops. Original policy/Adapter/Producer/Feedback/safety code unchanged. E1 namingMinor corrected inPLANV2.

| Measurement check | Finding |
|---|---|
| Target | OfflinePASS: dynamicrequest/Feedbackstate and completeE versus fullwindowN supports explicit. |
| Actual coverage | No newnative evidence; syntheticlogs do not prove traffic/tails/EOF coverage. |
| Missing/duplicate | OfflinePASS: partial/null/censor and earlySTOP protected. |
| Independent accounting | Request/phase portionsPASS; resource accountingFAIL untilMajor repaired. |
| Regression | Existingwiring covered; nonzero aggregatehistory counterexample missing. Add onlynecessarycheck. |

After repair, resume exactgates and dynamicfirst. ALINEA waits for dynamicactual engineering/data/science review and resource settlement. Neither offlinePASS nor future normalpartialexit establishes long-run, fullrange or servicequalification.
