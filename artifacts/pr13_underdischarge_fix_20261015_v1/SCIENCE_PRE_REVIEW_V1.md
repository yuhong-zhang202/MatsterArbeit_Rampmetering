# Scientific pre-review: PR13 underdischarge P1

2026-10-15. Primary agent preserves the read-only advice returned by project `scientific_reviewer` `/root/pr13_p1_science`; this is not user acceptance or a new scientific decision.

## Approved implementation scope for review

GO only to implement and verify a new, explicitly finite diagnostic contract. The old unconditional complete-packet N=2 assertion is reachable with no front vehicle or one vehicle; a `SATURATED` label cannot itself prove two vehicles were physically available. Complete N=0/1 means the nominal two-vehicle diagnostic target was not met, with cause unestablished; it does not prove an actuator fault.

The new adapter and actual loop wrapper must reject general qualification/formal uses before movement or setters. A complete underdelivered packet must preserve C/E/N and raw supply/readiness/receiver/WAIT observations, persist a neutral structured stop before selecting another packet, and never retry or catch up. A complete packet ending exactly at the observation endpoint must also be assessed; a terminal partial packet must not be compared with a completed quota. Safety/UNKNOWN/duplicate/red-entry/N>2 failures must not be downgraded. Safety failures take precedence if both exist.

The original executed 154-source version, cards, bindings, raw, existing results and failures remain unchanged. Tests must exercise the new adapter through the real old loop with fake movement, not claim native behavior. A new independent reader must distinguish observation-accounting completeness from diagnostic-target failure. General constrained-supply continuation remains unresolved and blocks direct formal/general reuse.

## Rejected expansion

Do not implement continuation or a nonrecoverable-service offset in this fix. The initially discussed `max(cycle_delta_C - cycle_N, 0)` mixes request changes and cycle delays with unavailable service and lacks causal support. A separately discussed nominal-shortfall bookkeeping alternative would also be a new policy proposal, not a consequence established by N<2. The primary agent withdrew both continuation/offset instructions before the agreed final implementation scope. No original request, cumulative debt, or N is reset or rewritten.

## Required checks and limits

- Fake complete N0 and N1: neutral target-not-met stop with persisted observations and no next packet or movement.
- Complete N2: unchanged nominal selection and accounting.
- Partial versus exact-end complete: distinct treatment, including pending commands.
- Unsupported purpose: rejected at both adapter and actual loop entry.
- N>2 and at least one original UNKNOWN/safety failure: hard failure retained.
- Independent data review must verify the new result classification and stop-boundary accounting.

Measurement target is original request integral C, complete nominal E, and unique physical entry N; synthetic offline tests only establish code/interface behavior. Native coverage is not newly verified. No new service/safety qualification, formal adoption, protocol freeze, SUMO run or merge is supported.
