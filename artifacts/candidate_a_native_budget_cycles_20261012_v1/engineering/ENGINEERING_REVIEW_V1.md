# Engineering review — native Candidate A four-budget/three-cycle minimum implementation

2026-10-12 Europe/Berlin. Verdict: PASS_FOR_BOUNDED_OFFLINE_THREE_CYCLE_IMPLEMENTATION_PRELAUNCH_REVIEW, pending independent data and scientific release. No native execution, SUMO version process, real TraCI connection, executable authorization/release or new raw identity exists.

## Context and change scope

Context Preflight completed using AGENTS.md, latest PROJECT_STATE, DECISIONS, empty EXPERIMENT_PROTOCOL and relevant WORKLOG; the empty/unfrozen formal protocol is a known formal-run blocker, not a silently inferred setting. New task is the user's explicitly authorized bounded technical goal: four sequential budget allowances5/6/7/8 minutes, native controlled yellow/red, three complete24s cycles, actual discharge measurement, suitable tested allowance. Stage6 closeout and old STOP3/A1UNRESOLVED/NOT_QUALIFIED/900NOT_TESTED remain. Parent records current goal and owns state/worklog; this engineer did not alter governance files.

Only new src/candidate_a_native_budget_cycles_20261012/{adapter,bridge,profile}.py, new CLI, new tests and this new engineering package were written. Old536protected hashes, the old SMOKE04card1fe30783... and all25old-card source hashes matched. No old source, guard, formal design, vehicle dynamics, demand, G/y/r durations or dt was changed. Latest same-frame cache, protected worker, native launch/connect, receiving observation, crossing/CycleLedger, shadow policy, LogCapture and resource watchdog/cleanup are reused.

## Exact behavior

Native successor0 matches already-reviewed G3/y3/r18 XML. New adapter predicts pending red→green at1224/1248 with rawphase2/r,nextSwitch=t, then verifies actualpostphase0/G. It does not reset phase at those boundaries. Fresh admission/coverage/receiving checks run before every new automatic-green motion. Denied or UNKNOWN receiver stops before this motion, possibly earlier in prior-red postmonitoring. Other pre/post checks retain old thresholds and STOP semantics.

At1207 a mandatory checkpoint verifies first controlledred1206→1207, ACK/time/accounting, pendingabsence, phase2/r,nextSwitch1224, link and captured log identity. Checkpoint file is created exclusively and flush/fsync completes before checkpoint_verified becomes true. It is a provisional in-run log checkpoint; final owned-process normal EOF and four-stream binding remain mandatory. There is no timer/phase/connection/ledger restart. At1272, exactly3ledgers complete; lastmotion1271→1272red,nextSwitch1272; no fourthgreen event executes.

New post rows serialize already-read unrounded before∩after speed differences, after-population actual acceleration values and exact checkedIDs, arrived/before-only exclusions, postworld, nativeeventcounters and phasefields. No new brake inequality or hypothetical global coverage claim. Failure/partial getter records remain partial; UNKNOWN still stops. Before-only/arrived vehicles are explicitly excluded from these intervalbrake checks. The native4stream logger retains the prior conditional synchronousstderr/otherstreamfinalEOF boundary; parentPython stderr is not universal per-step coverage. Old integerstep API warning semantics remain unchanged and must be reported if emitted.

## Actual offline verification and preserved failures

- `.venv/bin/python -m unittest discover -s tests/candidate_a_native_budget_cycles_20261012 -v`: V1nine methods, exit1 due one testexpectationFAIL. Unknownreceiver observedat1224 already stopped the previousredpostmonitor; test incorrectly expected the nextgreen admissionreason. Productionchecks unchanged. ActualFAILlog and exacttestpreimage retained.
- V2same nine methods with corrected testexpectation: exit0,9PASS. Its exactsource is reconstructed by the recorded single-line transform of preservedV1, explicitly not a contemporaneoussource-hash receipt.
- V3adds two required actual-prepared-card checks: exit0,11PASS. Complete XML-drivenfake3cycles with N3 ratherthan forcing nominalE6;1207durablecheckpoint/failureblock, pendingred→green noextra setters,0Nobservedcase, arrived/braking coverage, redcrossing/brake/phase/stderrSTOP, strict300/360/420/480andothercaps, canonicalmissingpermissionsbeforeallocation/spawn. Purefakes are not vehiclephysics or nativeperformance proof.
- `.venv/bin/python scripts/candidate_a_native_budget_cycles_20261012_v1/cli.py --prepare`: exit0, four exactnewcards. Direct actualprofile.validate(... require_environment=True) passed allfour by reading installedfiles/hash/metadata, without runningnativebinary. validate_release correctly denied missingcanonicalauthorization before any nativeallocation/launch.
- Existing old8cachetests notrerun: relevant oldbytes match; changedcycle/checkpoint functionality has11newtests. No cleancheckout/nativevalidation claimed this delivery.

Actualcodesource/input/card hashes are frozen in INPUT_BINDINGS_V1.json; SOURCE_TRACE design binds completeofficialcachedfiles to originalpinnedreceipts. All11V3tests correspond to these implementationbytes. Cardcommands/environment/resource/inputs are recorded, not software-version guesswork. Detailed logs and V1 failure are linked by OFFLINE_VERIFICATION_RECEIPT_V3.json.

## Four cards, release and result interpretation

CARD_CHECK_ALL_V1.json binds eachcardSHA. AllsameM3600/R900/U360/X180,seed17,command300,dt1,end1272,checkpoint1207; onlywallcap/runidentity/outputpath differ. Startup60s/output300MB/free5GB/watchdog0.2s retained. These are allowance ceilings: early STOP/hard1272end still apply; do not intentionally pad tobudget.

Release requires exactper-run human-goal reference, card/authorization hashes and engineering/data/science receipts. Parent must complete postrunreview before issuing nextrelease. Receipt status ABORTED_UNKNOWN alone must not be used to classify a failure: inspect error, watchdogreason, actualACK/accounted prefix and finalEOF logstatus. A pure budgetresourceSTOP with bound known evidence may proceed to next already-authorizedbudget afterreviews. Braking/receiver/identity/phase/log UNKNOWN or anomaly stops theseries for mechanism diagnosis; a larger budget cannot remedy it. A wall watchdog kill with unresolvedEOFlogcoverage is not automatically a cleanbudgetonlyfinding. No blind retry/automaticthresholdrelaxation.

C=C_applied=6andE6 require72actualreconciledcontrolseconds; N may be below/above6 and is measured. Unobserved exports must be null despite rawinitializedledgerzeros; observedpartialprefix remains real, incompletecyclesdo notqualifyrates. Independentdata must matchactualNIDs/intervals withFCDt poststateforACKt+1 and bindTLSmotion; freewayE1sameintervalcountsare notmeterN.

Native firstred/cyclephysics, realruntime, outputsize, receivingavailability and actualdischarge accuracy remainunverified. This offlinePASS is not A1proof, longtermratequalification, universal safety or formalexperimentalreadiness. Smallest observed successful budget is a bounded recommendation, not a probability-based reliable optimum.
