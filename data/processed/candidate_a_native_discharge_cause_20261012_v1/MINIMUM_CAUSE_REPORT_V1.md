# Minimum discharge shortfall analysis — existing two native runs

2026-10-12 Europe/Berlin. **Observed result: every one of six sampled cycles releases one vehicle.** In each cycle the second vehicle starts about8.502m before the controlled line, remains stationary through the firstgreen second, and has not reached the line when the3s green ends. It then approaches/stops near the line duringyellow/red; R1/R2 pass only at the nextcycle's firstgreen step. This observation chain is sufficient to explain why nominal2 was not achieved here; it does not prove a unique SUMOinternal decision cause.

## Scope and evidence

CurrentSTATE/AGENTS/DECISIONS/known0Bunfrozenprotocol/WORKLOG reviewed. Latest task authorizes only low-cost existingdata analysis. Rawfiles read-only; no newSUMO/tests/fulloldaudit/parameter/signal/model/guard/protocol/decision changes. Analysis is exploratorytechnical diagnosis, not formal causalproof or qualification. Prior Stage6/STOP3/A1UNRESOLVED/NOT_QUALIFIED remain.

Used only the two latest frozenmanifest identities: WAIT_DIAG01_V2 SHA990386cf... and WAIT_BUDGET_W360_01 SHA61aae130... in the independentworktree. Eachmanifest selects five relevantfiles: FCD, nativeTLS, pre/postobservations andACK. Their originalSHA bindings were independently checked. No additional historicalraw scanned. One deterministic extraction command passed: **sixcycles,300selected first/second-car snapshotrows**, exactselectedfield equality betweenruns. Positionusesunrounded nativepre/currententrygetter when available; otherwiseFCDprecision2, labeled perrow. Controlledline is storage laneend204.49m. FCDlabel t is postmovement for(t,t+1], matched to ACKt+1; no inventedsubsecond crossings. CSVemptyfields are unobserved/notapplicable, notzeros.

## Six-cycle numeric result

All first/second vehicles are stationary at greenbegin. Firstfront is203.489m, about1.001m beforeline. Secondfront is195.988m, about8.502m beforeline; front-to-frontgapabout7.501m andbumpergapabout2.501m. Exactnumbers and sources are in SIX_CYCLE_SUMMARY_V1.csv/JSON.

| Run / cyclebegin | First → second | Second speed afterG1/G2/G3 (m/s) | Second advance inG (m) | Remaining atGend (m) | ActualcycleN | Secondnextcrossing |
|---|---|---|---:|---:|---:|---|
|300 /1200|R0→R1|0 /0.793890 /2.699776|3.493666|5.008380|1|(1224,1225]|
|300 /1224|R1→R2|0 /1.532250 /2.618426|4.150676|4.351430|1|(1248,1249]|
|300 /1248|R2→R3|0 /1.615719 /3.893182|5.508901|2.993206|1|Notobservedby1272|
|360 /1200|R0→R1|0 /0.793890 /2.699776|3.493666|5.008380|1|(1224,1225]|
|360 /1224|R1→R2|0 /1.532250 /2.618426|4.150676|4.351430|1|(1248,1249]|
|360 /1248|R2→R3|0 /1.615719 /3.893182|5.508901|2.993206|1|Notobservedby1272|

R0/R1/R2 frontentries in(1200,1201],(1224,1225],(1248,1249] allmatchnativeFCD/TLS/ledgerG and uniqueIDs. R3absence is endcensoring, not a claimed failure to evercross. Crossingsteps are24s apart; exactsubsecond headway unobserved. Bothruns C=appliedC=E6,N3; nominal2/cycle is an **unqualifiedmapping assumption**, not a measuredphysical packet orNcap. Actual72sdescriptive150veh/h is not300qualification orlong-termcapacity.

## Receiving state and yellow/red trajectory

Atgreenend the precedingcar is moving in the internal lane at5.331761/5.209786/5.672616m/s. Its rearclearance is4.290343/3.810033/6.358121m, stillbelow the oldprospectivebody requirement7.5m. Oldprospective receiver remainsFalse. The separate actual-speed followinggap observation for the secondcar passes unchanged1.1m margin: gap6.798722/5.661463/6.851327m versus actualsecuregap+margin3.799776/3.718426/4.993182m. These are different predicates; actualfollowingPASS must not be rewritten as oldprospectiveavailableTrue orfutureclearanceproof. WAIT preserves the olddenial; it is observation, not a newvehicle-speed command.

After the firstyellow movement the oldreceiver reportsAVAILABLE in allthreecycles. The secondcar stilldoesnotcross: atyellowend its position/speed are203.488001m/0.045738m/s,203.395644m/0.150885m/s,203.468864m/0.020464m/s. It settles near1m beforeline and is actually0m/s atcycleend. Thus there is **no observed permanent receivingblock** throughoutthecycle; availability eventually returns while the signal isyellow/red. Full24s first/second trajectory and recordedleaders/currentgap fields are retained in SELECTED_TRAJECTORIES_V1.csv/JSON; red-periodunrecordedleaderqueries remainnull.

## What can and cannot be concluded

Confirmed: queuedsecondcar initiallywaits onegreenstep, thenadvances but remainsupstream atgreenend; signalG3/y3/r18 is correctlyobserved; onlyonefrontentry occurs; nextcycle restarts from a stoppedfrontabout1m upstream. No countingerror, forcedNlimit2, unknownmissingcrossing orwrongphase/timestep was found in these necessaryfields. Native currentfollowing records, prospectiveclearance and actualtrajectory are jointlyconsistent; getters/WAIT do not themselves issue vehicle setters.

Limited inference: **queue startup/following time plus short3s green, followed by yellow-compatible stopping**, is a plausible mechanism for onevehicle/cycle. The data establish insufficientdistance covered withinG, not that anyone particularcar-followingbranch/reactionparameter caused theinitialwait. Source-definednominal2 lacks demonstrateddischarge qualification underthisqueuedcontext. Native getStopSpeed/finalfollow-speedconstraintselection/yellowbranchinputs/effectivecarFollowModelID were not serialized, so no unique nativeyellow orfollowingdecision is asserted. No claimallUloss/spillback ordownstreamcapacitycausality is made.

The two runs use the same seed/commonruntime andphysicalinputs with differentmetadatawrapper/wholeSOURCEsnapshots. All300selectedsnapshotfields and sixcyclesummaries match exactly afterdroppingrun/budgetlabels. This is repeatableobservation underthese sameinputs, **not two independent stochasticreplicates**, and lowerW360walltime is not a trafficperformancecause.

## Minimal next step

For the present question, **no newsimulation is necessary**: retain onevehicle/cycle and theunqualifiednominal2 mismatch, with theobservedtrajectory chain anduncertaininternalbranch distinction. If a later approvedtask must testwhetherdifferentG can supporttwo, or identifyaunique mechanism, it wouldneed a separatelydefined controlledcomparison/observationplan. This report proposesno numericretuning, updatesnoofficialmetrics anddoesnotauthorize suchruns. Parentengineering/scientific review shouldbound anyfuturedecision; do not fabricateN6 orcounttechnicalPASS asservicequalified.
