# Fixed750 — strict braking STOP, engineering prefix delivery

2026-10-13. **STOP_FOR_CURRENT_TECHNICAL_SCOPE; PASS_FOR_FROZEN_PREFIX_DELIVERY_ONLY.** Independent data/scientific post reviews remain pending. No retry, tolerance adjustment, source change or subsequent task/card occurred.

## Identity and actual outcome

Context preflight read AGENTS/current STATE/DECISIONS/empty formal protocol/recent WORKLOG. The current user-approved isolated scope and exact engineering/data/scientific card GO authorize this one technical run; no formal experiment or qualification is inferred.

Card SHA9f8dab32a6392a3efaf33bff78ae211f67165ff009cb938abd2bbc59152ffc92; release SHAa466bab8d09693d4d2fb2c6e1261d8ba78839487e461f8cc2041f29d6ea441d4; common61-source digest a2b25659131bae5d9628ff5ab2f35e0c89987705daa5ef84a67ce426967b4b2b. Existing project.venv Python and source checkpoint6706d4a61e8f0953baaa39b1c3666ebe4f3b6e38 were used. Fresh gates passed; no environment/source change. Native PID11694, CLI11672, port51507, tool session34093. One child connected after25.014673583s, within60s; connection polling did not restart the child.

The exact command was `.venv/bin/python scripts/candidate_a_unified_alinea_20261013_v1/cli.py --execute artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_FIXED750_S17_01/card.json --release artifacts/unified_alinea_actuator_20261013_v1/engineering/releases/UA_FIXED750_S17_01/EXECUTION_RELEASE.json` from the main project directory.

Actual final ACK/accounting time **1265s**, not the planned1270s. CLI returned1. Bridge status `ABORTED_UNKNOWN` retains the actual reason: `ORDINARY_BRAKING_EXCEEDED:R_flow.13;UNKNOWN_OR_EXCESSIVE_ACCELERATION:R_flow.13`. The values are finite and known; this is a strict ordinary-braking contract rejection, not a time-limit failure or evidence of missing log coverage. Monitored startup/loop/cleanup elapsed **170.451689125s**, below300s. Watchdog reason/error are null.

Six complete10s cycles1200–1260 each have G4/y4/r2 and two G entrants. The seventh1260–1270 cycle is observed only through1265: G4/y1/r0 and one G entrant. It is incomplete; its full-cycle E remains0. Actual prefix C=13.5416666667, mapped-pending=applied13, complete-cycle E12 and independent observed N13. No nominal14 or partial-cycle qualification is substituted. Requested750 and mapped720 remain separate. A prefix ratio or agreement with mapped integral cannot override the braking STOP.

## Exact stop input and bounded source context

At1264→1265, **R_flow.13** remains on ramp_storage_0, with speed4.69222772465427→0.19122772465426985m/s. Both delta-v over1s and the native acceleration getter equal **−4.501m/s²**. The unchanged limit is−4.5 with1e−6 tolerance: the observed magnitude exceeds normaldecel by0.001. Its pre-position is203.97137014006898m on the204.49m storage lane,0.518629859931m before the line, length5m. Actual post position is not present in post_world and is left to independent FCD inspection; it is not invented.

Pre-TLS is pending G/phase0 with nextSwitch1264; actual ACK1265 is y/phase1 with nextSwitch1268, program/link/time binding valid. This is the first yellow interval of cycle7. The bound local yellow screen had stop_possible=false and clear_possible=true; that feasibility classification is not proof of future motion. R_flow.13 has no observed meter entry in this prefix. All13 actual entrants have recorded rear-clear ACKs; no body is censored. Detailed fields/hashes are in `STOP_INPUT_DETAIL_V1.json`.

One bounded query of the existing official SUMO1.26 cache found numerical context, not a traced causal branch. All four source hashes match the original pinned receipt at commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`:

- [config.h.cmake229–230](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/config.h.cmake#L229-L230) defines NUMERICAL_EPS0.001.
- [Krauss stopSpeed101–107](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L101-L107) delegates to maximumSafeStopSpeed; [MSCFModel796–815](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L796-L815) compares stop deceleration against myDecel+NUMERICAL_EPS when considering emergency relaxation.
- [MSVehicle3712–3727](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3712-L3727) uses internal distance/model brakeGap for yellow stopping; [4908–4928](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L4908-L4928) computes acceleration and subtracts normaldecel plus NUMERICAL_EPS in native warning logic.

`PINNED_NUMERICAL_EPS_SOURCE_QUERY_V1.json` binds cache paths, full hashes, official URLs and limits. This can explain why a0.001 excess is treated differently by native warning logic and the stricter project monitor. Actual private branch variables were not traced; model selection and compiled-source equivalence were not independently proven. It does **not** establish the origin of this velocity, collision safety, a false-positive verdict, or permission to relax the guard. The current contract STOP remains intact.

## Freeze and next gate

Full raw parent is frozen: **109 files /162,395,236B**, manifest SHA4234288ec3b6cd86f7247364bf03cb99f5e2eca4996a66650b6e94cdced6df9f. The manifest is outside raw. Final owned-process EOF is complete and reports `BOUND_NO_OBSERVED_NATIVE_MESSAGE`; all recorded collision/teleport counters are0. This does not negate the braking failure.

The final post journal uses the pre-existing STOP `retained_receipts` wrapper. A first flat-row inspection raised KeyError:status; `INSPECTION_SCHEMA_ERROR_V1.json` preserves that reader error. Only engineering inspection flattened the existing wrapper; raw/runtime were not edited. The65 controlled receipts are signal-bound/accounted, with13 entrant IDs and six complete cycles. **1333 normal-arrival records require independent precision8/tripinfo last-movement audit.** Full FCD/TLS/ACK/phase/command/EOF validation and scientific scope interpretation remain pending.

Current source bytes remain identical to the card. No resource settlement was created; the existing guardian retains a full300s/300MB conservative reservation until three-role post review. Dynamic and real-ALINEA tasks are held after this STOP. Source context is advisory only; no additional simulation or guard adjustment is recommended as already authorized. Parent owns factual STATE/WORKLOG updates and the next decision after independent review.
