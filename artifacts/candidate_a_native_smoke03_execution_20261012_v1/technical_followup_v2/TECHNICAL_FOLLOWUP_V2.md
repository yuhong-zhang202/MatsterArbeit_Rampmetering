# SMOKE03 remaining wall budget — V2 metric-scope precision correction

**TraCI-Duration is broader than the command loop alone; remaining runtime problem stays UNRESOLVED.** This is a controlled wording correction following scientific review. V1 and its hashes remain unchanged; all raw data, counts, execution results, source/card/caps/guard and safety/qualification conclusions are unchanged. No fresh fetch, test, native launch or A1 proof.

## What is corrected

V1 described accumulated native walltime around `TraCIServer::processCommands` before each simulationstep. That account was incomplete. Pinned SUMO1.26 `MSNet.cpp` first times `processCommands` at lines793–802, then starts another timed tail at line904. `postMoveStep` calls `libsumo::Helper::postProcessRemoteControl` (line919) and conditionally checks remote-control collisions before adding currentwalltime and accumulating `myTraCIMillis` at lines923–925. Conditional `CMD_EXECUTEMOVE` handling also lies in this tail; this smoke uses standard simulationStep, so the source branch is not evidence that executeMove was exercised.

The recorded153.24s therefore covers command processing/clientwait/IPC/serverquerywork **and the included later remote-control handling tail**, rather than exclusivelyprocessCommands or PythonCPU. Remote-control activity, individual operationtime and fractions are unmeasured; the excerpt does not establish that remotecontrol dominated or changed thisrun. Native log154.78s and launch budget180s remain distinct. Source-to-installedbinary/compiler equivalence is not verified.

## Unchanged evidence and next-step boundary

Real underlyingcalls3,763,936 and cachehits6,718,670 remain recordedprefixcounters, not matchednativewallbenefit. 6944JSONLrows correspond to source append/flush/fsync executions; their latency or costshare remains unknown. No individualhotspot is proven. Controlled1200activation/red1207 remain NOT_REACHED, no rate/safetyqualification.

A minimal versioned timing/instrumentation proposal at existingobserver/control/step/serialization/durability/resource seams remains a recommendation requiring review before another separatelyauthorizednativeattempt. No sourceoptimization, capincrease, skippedcheck or SMOKE04 is delivered by thiscorrection.

[Expanded pinned source excerpts](PERFORMANCE_METRIC_SOURCE_READBACK_V2.json), [unchanged counts and corrected metric scope](BOUNDED_COST_EVIDENCE_V2.json), [V1 preservation and correction receipt](V1_PRESERVATION_CORRECTION_RECEIPT.json).
