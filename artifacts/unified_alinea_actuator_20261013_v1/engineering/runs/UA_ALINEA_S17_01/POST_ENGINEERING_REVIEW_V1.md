# UA_ALINEA_S17_01 engineering post-review V1

**Completed at ACK1272 / CLI exit0. Two real non-initial Feedback requests actually applied. GO for independent data → scientific post-review only. No qualification or further simulation.**

## Bound native execution and resource evidence

One start, no retry: exec session24974, CLI23439/owned SUMO23461, port56095. Card SHA56da7b966ac9b2e302032243ef2a0058c2b114a6f47306389d56c9dc8203a086; releasee62da819567ac6db29168bc366c1303a75f073949476a14d7cfc5163781a50ca; unchanged64-sourceea180197848843bd3cca7d326a7016454fe8bd0db406302a64ad11f03347b29b over implementation1749e040 (evidence HEADff309c8 bytes equal). Fresh source/env/input/card/release gates PASS. All64 current and raw snapshot hashes still match; no code, environment, seed, timing, model, guard or research change.

Actual command: `.venv/bin/python scripts/candidate_a_unified_alinea_20261013_v1/cli.py --execute artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_ALINEA_S17_01/card.json --release artifacts/unified_alinea_actuator_20261013_v1/engineering/releases/UA_ALINEA_S17_01/EXECUTION_RELEASE.json`.

Startup24.638545167s connected; monitored elapsed startup/cleanup151.6604771669954s. Single300s/raw300000000B/startup60/free5000000000B and total1200s/raw1200000000B remain.112rawfiles/164060455B frozen with outside-raw manifest05ee359c299a15c5352f24635135cbe43fbfd20c2ed688d5b2697af15a03beec. No raw changes after freeze. Budget still conservatively reserves300s/300MB until independent post gates; engineering does not settle or spend the remainder.

## Real measurement → Feedback → request → applied ACK

Actual main_down20m two-lane E1s used. Activation global1200/logical600 sampled actual detector tuples; ongoing events at activation were **observed empty in both lanes**, not missing data.72 consecutive real post E1 observations global1201..1272 retained, including full[1200,1230) and[1230,1260) windows; all raw global entry/leave five-tuples, contributors and ongoing/cross-window states are in feedback_events.jsonl for independent audit.

At global1230/logical630: lane occupancies7.296530162747482% /9.659084500640347%, mean8.477807331693914%, contributors12/17. Own previous requested900veh/h; raw1076.553486781426veh/h, clipped900veh/h. Explicit feedback:1230 applied at1232, first G ACK1233, delay2s.

At global1260/logical660: lane occupancies11.292688537954138% /11.21895811676647%, mean11.255823327360304%, contributors17/20. Own previous requested900veh/h; raw/clipped882.0923670847787veh/h. Explicit feedback:1260 applied at1264, first G ACK1265, delay4s. Both real non-initial requests applied; no pending unobserved feedback at terminal. No made-up occupancy or scheduled fixed command substitutes these measurements; own clipped previous state was not replaced by mapped policy or N.

The new882.092367 request maps to900/T8. Therefore the **physical native period remains T8 throughout** despite a changed controller requested rate. Initial setProgram/setPhase0 only at1200; feedback applications used actual native boundary and real signal ACK without caller restarting G midcycle. This demonstrates the real feedback interface and request identity application, not a native physical response to varying periods or a freeway protection effect. Source formula/pinned implementation values and real occupancy arithmetic require independent validation.

## Actual accounting / monitors

Nine completed T8 cycles, two G entries each; E=N18, yellow/red entries0. Actual C17.940307890282597, pending=applied18, quantization−0.05969210971740433vehicle-equivalent; pending−applied integral0 **does not mean delay seconds are zero** (actual delays2/4). No partial final cycle or body censor; all18 entrant tails observed rear-clear.72 control phase-clock rows/1272 post rows;35 post WAIT classifications.

First controlled red began1206; mandatory provisional checkpoint at ACK1207; all four final native streams bound at process EOF/native returncode0, no critical/unrecognized native message. All observed collision/teleport counters0, remaining STOP reasons empty. Restricted numerical-event classifications0; observed minimum delta/native alpha−4.5m/s². Numerical authority stays bound but inactive here. Original FrameCache Python float-step API UserWarning retained on calling tool output; no native warning suppression.

Journal1338 normal arrived IDs require independent final-tripinfo precision8 BEGIN/arrivalSpeed reconciliation; this is not a realtime complete last-step braking claim. Original75001 strict FAIL and75002 E14/N13 service shortfall remain; neither is revised by this short closed-loop result.

## Handoff and limits

Independent data checks all112raw inventory/hash, genuine E1windows/ongoing states/two-lane source identity, exact Feedback own-state/raw/clipping/quantization, request IDs/actual applications and continuous TLS/FCD/ACK, all N/integrals, body/logEOF and1338 normal arrivals. Scientist then decides the bounded technical delivery. Current short seed17 feedback case is not formalALINEA effectiveness, long-term rate qualification, sweet spot, transferable parameters, native safety proof, or uniquely observed private stop branch. No further native/tests/point or tuning; parent owns STATE/WORKLOG, final scope report and resource settlement after post review.
