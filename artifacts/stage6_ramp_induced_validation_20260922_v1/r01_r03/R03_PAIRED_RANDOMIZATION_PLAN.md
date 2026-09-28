# R03 paired-randomization plan — RI3350

Status: `PASS_PLAN_AND_FIXTURES; ACTUAL_REALIZATION_UNKNOWN`. This is an offline implementation/readiness artifact, not a claim that two stochastic runs will be trajectory-matched.

## Frozen prelaunch parity contract

The control (`RI3350_CTRL_S17_attempt1`) and the already specified transition arm must retain identical scheduled M/U/X fleets and explicit attributes: same seed 17, M=1396, U=150, X=75, begin/end `[0,1500)`, same route/type definitions, M `departPos=100`, U/X `departPos=last`, `departLane=best`, `departSpeed=max`, same network bytes, 1 s step, horizon 2700 s, A_OPEN, TLS, detector and behavior inputs. The sole intended treatment difference is the R flow (control absent/0; transition R192 over `[540,1500)`) plus isolated run/output identifiers/paths. There is no transition input package in this task, so its realized parity is not verified here.

Do not pin or overwrite per-vehicle `speedFactor` or other stochastic attributes to make matching pass. A common seed does not guarantee common random numbers when one arm has an extra R flow and changed event ordering. Existing M/U/X IDs and explicit source attributes are prelaunch-matchable; actual insertion time, precise sampled speedFactor, and pre-R trajectories require both future runs' immutable raw outputs.

## Required future post-run paired audit

1. Join by class plus vehicle ID; never drop unmatched IDs to improve parity.
2. Verify planned and actual M/U/X ID sets, scheduled time, route/type, explicit depart attributes, and precise `speedFactor` separately. Exact parsed values are compared; do not invent a tolerance.
3. Compare actual insertion/departure and FCD samples for common M/U/X IDs over `[0,540)`: time, lane, position/x, speed. Preserve mismatching IDs and maximum absolute numeric differences per field. Missing coverage is `UNKNOWN`, not an implicit match.
4. Report post-540 differences as outcomes, not parity failures. Still flag different sampled properties among post-R generated vehicles as a potential stochastic-composition issue.
5. If pre-R attributes/trajectories differ, record the mismatch; do not reseed, modify demand, or assert strict common-random-number matching. Scientific handling is not decided by this adapter.

The adapter fixture verifies exact equality and fail-visible mismatches using synthetic rows only. It cannot establish actual insertion, sampled attributes, trajectories, or causal identification before both outputs exist.
