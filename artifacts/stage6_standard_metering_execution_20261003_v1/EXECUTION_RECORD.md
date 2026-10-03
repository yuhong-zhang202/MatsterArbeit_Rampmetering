# Current-version standard metering execution record

Date:2026-10-03. Classification:EXPLORATORY / technical, not formal. Authority:D-014, latest user requests strict execution of the referenced master plan. Exploration remains PARTIAL. This is a rolling factual record; unresolved gates are not assumed passed.

## Authorized sequence and fixed boundaries

S0 preflight → S1 implementation/measurement/card/scientific review → S2 S17 all-green neutrality → S3 S17 controlled technical pilot → eligible S4 S23/S42 identical-policy exploratory comparisons → S5 independent result review and explicit closure assessment. Negative/mixed results retained. No automatic retries or target/gain sweep; fixed raw/old OPEN runner immutable; formal protocol remains0B/unfrozen.

## Current checkpoints

- S0:read main plan, current state/decisions and required agent instructions; latest execution authorization synchronized as D-014. Authorization/source receipt saved in S0_AUTHORIZATION_RECEIPT.json. Existing input/manifest verification pending engineer report.
- S1:engineering and analysis implementation underway in isolated new script/test/output namespaces; scientific reviewer read-only. Existing detector-specific occupancy calibration checked independently for the candidate policy; it does not demonstrate closed-loop stability or an optimum.
- S2–S4:no starts at this record creation; no release inferred from prior design PASS.

## Prospective implementation review items

Feedback11%/70veh/h per percentage point may be retained for one prospectively locked exploration, subject to concrete implementation/card checks. Reviewer notes that at14.5% a single update subtracts245veh/h:900→655; clipping/oscillation must be logged without outcome-based retuning.600 initial credit0, first900-rate green[603,604); previous complete[600,630)first feedback;119 updates630…4170;4200 terminal only.

Proposed engineering qualification changed before any outcomes:30s>=15 qualified slots is impossible at1200veh/h (at most10). Review uses cumulative>=20 independently prequalified queued/unblocked slots and90% unique front-crossing/qualified-slot service, eachslot<=1 vehicle; fewer opportunities means insufficiently tested, not automatic failure. Real stopping position/reachability and receiving space must be checked before release; empty/blocked slots retain separate accounting. Stopline crossing bracket must match the actual within-step signal, not the later FCD sample light.

Each start counts in original cumulative40total/8control-technical ceilings,120s/250MB perrun/shared8GB raw. Existing18starts remain counted; budget availability never substitutes for release.

### S1 independent prelaunch refinements (before new starts)

NOOP comparator now excludes only summary.step.duration (CPU step time), retained separately; tripinfo.duration remains scientific comparison. ALINEA119 updates; NOOP1 read-only probe at630 aligned toXML600–630. Candidate service qualification is being finalized with real most-front storage vehicle before any speed filter, stoplinegap<=1.1m and speed<0.1m/s, nearest downstream rear receiving space>=vehiclelength+minGap. Entire81.98m connector-empty requirement was rejected as unnecessarily restrictive. These are prospectively reviewed technical screening tolerances, not literature traffic constants; oldsame-geometry B22 parking positions only inform coverage/reachability, not control effects. Exact locked finalcard governs release. Metadata must be obtained from actual runtime, not assumed default5m. No control efficacy is inferred.

Root S1 verification: `.venv/bin/python -m unittest discover -s tests -p "*standard_metering*.py"` passed21 tests. NOOP V1 prepared-card SHA362f0e2aa50c352e9878d46ec2a41d4342ac4e3605d6af445215fa09db13eaea; pending independent exact-card release; no new start inferred from successful static tests.

## Actual technical execution and measurement repair

V1 and V4 cards were prepared but never started. V2 and V3 each started one SUMO process and failed to establish TraCI; their raw receipts and failures remain preserved. TCP connection retries are not separate simulation starts. V3 process return -15 was deliberate cleanup after the startup deadline, not spontaneous early exit.

V5 completed 4200 s with 4050 arrivals; full independent traffic-neutral comparison against existing S17 OPEN passed, excluding only separately retained CPU summary duration. The successful connection occurred after 0.315 s; it does not identify the old failures' unique cause. No additional connection-only diagnostics are needed.

V5 feedback measurement failed: at [600,630), lastInterval API occupancy was 10.3935/10.1693 percent versus XML 11.40/11.57 percent; counts16/20 matched. No tolerance or target adjustment was made. V6 prospectively implements the planned per-step occupancy aggregation fallback: exactly30 samples per window,119 windows, lane-wise XML checks plus traffic neutrality. V6 is prepared, not yet released or run at this checkpoint.

Current cumulative starts21/40, new control/technical3/8, shared raw213593174 bytes. Authority D-015 covers reviewed technical repairs and continuing eligible original steps; scientific gates and original budgets remain intact.

## Final checkpoint:V8 measurement PASS, V9 safety PASS, rate tracking NO-GO

V7 faileddyldstartup; D016 userexplicitly excludedtechnicalstarts fromexperimentallowance. V8 startup60s retrycompleted andactualevent238XML/fullneutral PASS. S17V8 controlledpilotunsafeG→r wasretained. NewV9 safeactuatorrevision predeclaredtechnical, exactreleasedsingleS17, completed23.62s. All32manifests match; noemergencywarnings,556qualifiedcrossings,creditconservation anddata completeness pass. Actualsaturatedservice≈564 vsrequested≈1071veh/h fails originalbiased-service gate; noS23/S42start. Physical26/technical7/experiment19 preserved. Scientificnextdesign choice awaitsuser; fullhandoff docs/stage6/STAGE6_SAFETY_AND_RATE_TRACKING_GPT_SOL_HANDOFF_20261003.md. Noformalprotocolchange/closure.
