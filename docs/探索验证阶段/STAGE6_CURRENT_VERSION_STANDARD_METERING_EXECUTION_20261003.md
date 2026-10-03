# Stage 6 current-version standard metering execution

> Historical rolling execution checkpoint through V9. V15 subsequently completed matched S17/S23/S42 controls and Stage 6 exploratory validation closed under D-018. Current results and the formal-design handoff are in [the final closeout](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md); the older pending steps below are preserved as history.

Date:2026-10-03. Classification:technical/exploratory, not formal. Rolling record; unresolved gates are explicitly retained. User authorizations:D-014 strict plan execution and D-015 technical repair followed by continuation. Formal protocol remains empty/unfrozen.

## Evidence and acceptance boundary

The18 existing uncontrolled runs locate a sampled M3600/R750–900 transition from transient disturbance to persistent severe congestion in this demand schedule and network. This is not a universal capacity estimate. Original RI3350 is not pairable and is excluded from current-version effects. Old rebuilt fixed-time B22/B28 remain historical evidence only. The user requires a coherent current-version evidence chain, including mainline protection and ramp/shared-urban exposure; limited closeout was rejected.

Authoritative execution plan:STAGE6_CURRENT_VERSION_STANDARD_METERING_PLAN_20261003.md. Source inputs, exact cards, scientific releases and raw receipts:artifacts/stage6_standard_metering_execution_20261003_v1/ and data/raw/stage6_standard_metering_20261003_v1/. Derived independent audits:data/processed/stage6_standard_metering_execution_20261003_v1/.

## Technical sequence to the current checkpoint

V1/V4 cards were prepared but not started. V2/V3 each failed TraCI startup; no traffic effects can be inferred. Their raw receipts are retained. V3 −15 return was deliberate cleanup. V5/V6 completed4200s with4050 arrivals and full traffic neutrality against the unchanged S17 OPEN. Successful connection establishes a working path, not a unique diagnosis of the earlier failures.

V5 lastInterval occupancy disagreed with matched XML. V6 used30 true per-step samples per window, but173/238 lane-window occupancies still underestimated XML (mean difference−1.351785 percentage points,max−5.892472). All238 counts agreed and the3570-sample aggregation was internally exact. SUMO v1_26_0 source shows lastStep occupancy can omit completed cross-step tails and early-leave contributions; XML accumulates those events. This proves the interfaces are not generally equivalent, without attributing every observed residual to a vehicle. Target11%,gain70 and tolerance were not changed.

V7 reconstruction is under implementation/review:retain per-detector/vehicle/entry events across windows, update ongoing records with actual exits and clip individual durations to each completed30s window. It must pass actual XML alignment before control. No ALINEA run is claimed at this checkpoint.

Current starts22/40 total and4/8 newcontrol/technical; sharedraw229475449B. V7 plus three eligible controls would reach the8-start cap. Failures do not reset the cap.

## Result and handoff

Pending actual measurement release, sequential S17 service/data validation, eligible matched S23/S42, independent paired analysis and scientific closure assessment. Exploration remains PARTIAL; no formal handoff is unlocked.

## V7 actual checkpoint superseding the implementation checkpoint

V7 single reviewed start FAILED before any simulation step, guardianwall13.508s.13 rawmanifest hashes/sizes pass; five CSVs haveheaders only.80 sampled stacks locate this observed failure in macOSdyld dependency loading/mapSegments/fcntl; specific library and underlying cause remain unknown. Therefore V7 event method,238XML matches andtraffic neutrality are NOT_EVALUABLE, not disproven. NoALINEA started. Counts23/40 total and5/8 new. The unchanged three-seed sequence requires a further measurementNOOP plus3controls, one more start than the remaining allocation. Only an explicit cap8→9 amendment could release that allocation; it would not itself pass technical/scientific gates. Root requested this narrow resource approval, pending response. Do not change seeds or bypass NOOP to fit remaining slots.

## D-016 resource-accounting correction and V8 repair

User explicitly excludes technical diagnosis/repair from experiment allowance and requests retry after minimal repair, avoiding optional tests. Earlier remaining-slot obstruction is superseded. Physical23 starts and5 technical launches remain preserved, experiment count18 existing uncontrolled/0 controlled. Keep120s totalwall/250MB/shared8GB limits and all matching/measurement gates. Candidate V8 extends TraCI startup allowance10→60s, removes the conflicting101-attempt loop bound and synchronizes passive diagnostic time labels; only targeted late-ready/timeout tests are necessary. No binary replacement or system signature/trust modification. Static codesign failure on binary and24 directly bundled libraries is retained as a clue, not a proved cause:V5/V6 succeeded on the same binary. V8 must still pass actual238window/XML andneutrality before ALINEA.

## V8 verification and first actual controlled pilot

V8 NOOP passed238XML occupancies/counts,7140event groups andfull4200s trafficneutrality/4050arrivals. First S17ALINEAV8 thencompleted17.565s; matching/feedback/allvehicles and228of228 qualifiedfront service pass, butunsafe G→r transitions were observed. Two moving vehicles fall19.77/16.35m/s to0 withinone step andclamp atstopline;10emergencybrakes include8redemergency stops. Science NO-GO samepulse S23/S42, perpredeclaredactuator gate. Preserve thispilot asdiagnostic, notqualifiedstandardmetering efficacy. Reported M/R/U time changes andsharedphysical exposure are descriptive andpotentially influenced bydefectiveactuation. Strong≥30s uninterruptedchain criterion notmet.

Physical25starts,technical6,chargeableexperiment19/control1 (D016). S23/S42 cardsprepared only. Currentnext action:small prospective safeactuator correction, verifyexistingraw dangerousapproaches andservice opportunities, then exactreview beforeone S17retry. Do notchange11/70/demand/network/vtype ordeclareexplorationcomplete.

## Final node and direct continuation

V9 safetyrepair retrycompleted23.62s, allnecessary safety/data checks pass andwarnings0, buteffective rate-tracking NO-GO underoriginalservice-bias gate:queued evalrequested≈1071veh/h,actual564veh/h. R49/U6unfinished retained; noS23/S42. Physical26/technical7/experiment19,sharedraw302898421B,processescleaned. Usermustapprove feasibleactuator/parameterresearchrevision beforechangedruns; do notsimplylowerupperto550forgate success (600R/one-hour implies≥50unserved). Fullstepwise source-backed continuation:STAGE6_SAFETY_AND_RATE_TRACKING_GPT_SOL_HANDOFF_20261003.md. ExplorationPARTIAL,formalprotocolunfrozen.
