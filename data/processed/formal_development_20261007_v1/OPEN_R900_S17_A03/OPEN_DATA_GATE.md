# OPEN R900 S17 A03 independent data gate

**PASS_OPEN_NEUTRALITY_AND_DATA**, DEVELOPMENT ONLY. No new simulation for this analysis.

All17 traffic-output comparisons are exactly equal across the full4200 labels. Only summary computational duration (not trip duration) is excluded. Full FCD4200, tripinfo4050, vehroute4050, TLS8400, summary4200, lanechange1305, and11 detector files each140 intervals match. Pre600:600/600 equal.

All raw manifest/input/card hashes verified by the parameterized parser. E1 feedback238 lane intervals match XML;7140 complete event observation groups reconstruct occupancies, error0. Full requested M3000/R600/U300/X150 inserted/arrived, no endpoint vehicle, teleport/collision/discard or warnings. Independent integral/class cost residuals0.

Queue monitoring:3600 complete pre-step observations independently match native FCD(t−1), including internal lanes and actual body lengths. Maximum position/speed rounding residual<0.005001; no ambiguous low-speed boundary observations. Raw high-precision snapshots independently reproduce risk and shared extent. OPEN_DISABLED throughout with no nominal/final/override commands. Strict unchanged>=30s continuous shared-chain episodes0.

Control service/rate and override trigger/release qualification: **NOT_TESTED (OPEN has no control)**. This is monitor/neutrality evidence, not controller-effect evidence. Existing qualified T1 code is unchanged; the full wrapper neutral result and input/measurement audit satisfy the new reuse conditions for six legacy OPEN and threeR900 T1 data sets. New OPEN replaces900S17 T0 coverage; the original remains immutable.

A02 remains a preserved pre-SUMO sandbox worker failure, not an analyzed traffic cohort. No failed or unexecuted control is converted into an outcome.

Evidence:OPEN_DATA_GATE.json, neutral_comparison.json, pre600_comparison.json, feedback_xml_audit.json, event_feedback_audit.json, integral_cost_audit.json, queue_spatial_audit.json, operational_chain.json, summary.json and analysis_source_snapshot.py. A scientific/engineering release remains separate from this data gate.
