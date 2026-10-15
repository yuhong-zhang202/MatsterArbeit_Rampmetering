# Unified actuator — engineering implementation and offline review

2026-10-13. Verdict: **READY_FOR_INDEPENDENT_DATA_AND_SCIENTIFIC_PRELAUNCH_REVIEW_ONLY**. No new SUMO launch, canonical execution permission, or raw allocation occurred. This is not service qualification or formal experimental readiness.

## Context and actual scope

AGENTS, PROJECT_STATE, DECISIONS, EXPERIMENT_PROTOCOL, WORKLOG and the explicit approved scope/approval snapshot were read. The current task is the user-approved isolated unified actuator implementation. Stage 6 remains closed; A1 remains UNRESOLVED; Candidate A remains NOT_QUALIFIED. The formal protocol is empty/unfrozen. The approved reference uses the project's existing Feedback class (D-019), not the library's percentage-green implementation. Parent owns governance updates and Git delivery.

Baseline is `9eb95e29ccc85423084bc6945668cd36c3298b06`. The new code is an exact **uncommitted source snapshot on this baseline**. Do not claim the baseline commit contains or was tested with the new implementation. `SOURCE_AND_INPUT_BINDING_V1.json` binds the exact runtime, tests, environment and prepared input bytes.

## Minimal implementation

Only new namespaces were written. The adapter and bridge are mechanical copies of the reviewed packet implementation with per-cycle period/yellow parameters, boundary command application and approved technical endpoints. Original `BodyTracker`, current-following receiver guard, native worker, log capture, resource watchdog and production qualification launcher are reused without changes. `adapter.py.DIFF_V1.txt` and `bridge.py.DIFF_V1.txt` show the seams.

The native library has integer periods 8–24, G maximum 4 s, Y=min(5,T−6), red minimum 2 s, requested quota 2. Nearest mapping ties select lower release. This is a nominal mapping conditional on actual two-car discharge. N is uncapped, including multiple entries in one ACK and yellow extras. E increases only after a full cycle. C requested, mapped pending and applied are independently integrated. Before observation, all accounting values are null; a genuinely observed zero and a partially observed window remain distinct.

Every request has its own ID, including identical numerical values. New requests during a cycle remain pending; latest valid pending request wins. Superseded requests remain in the journal. `PREPARED_NOT_OBSERVED` is not actual application: only the first observed G ACK binds `ACK_OBSERVED` and first application time. Constant-command age is separate from application delay. Fresh receiver admission occurs before every new G. A different period selects a different native program only after the previous red boundary is verified; an unchanged period continues natively without reset. Red duration uses the existing reviewed official setter/readback path.

The real ALINEA mode instantiates the unchanged project `Feedback` class with the approved development reference (11%, gain70, clipped300–900, initial900, 30 s). Its own clipped requested rate remains `rate_previous`; mapped720 and measured N are never fed back. The original E1 event-ledger class is AST-identical. It seeds actual ongoing E1 tuples at global1200 and retains their global entry times. Full post-step events cover global1201..1230 and1231..1260. Only the arguments passed into Feedback are shifted by −600. The two E1 IDs, lane identities and 20 m positions are queried and bound. Missing, inconsistent or incomplete event coverage stops.

Original FrameCache rejects the inductionloop domain. The new subclass adds only four fresh read-only E1 getters; every existing domain delegates to the old class. No monkeypatch, getter substitution or legacy cache change was made.

## Safety/check-preservation matrix

| Check | Preservation / validation |
|---|---|
| World identity, route, modes and dynamics | Old identity/inventory AST-identical; all protected536 files hash-identical |
| Current gap emergency9 + margin1.1 m | Same old imported function; real frozen-denial fixture still STOP |
| Fresh new-G receiving space | Original admission check at every boundary; no WAIT substitution for denied admission |
| Per-entry before and after current-gap binding | Post physical guard block byte-identical |
| Collision, teleport, red front entry | Same original counters/STOP rules |
| Normal braking and after-population acceleration | Same original guards; before-only normal arrivals retain pending last-movement audit |
| Yellow local feasibility | Original screen algebra with current cycle's Y; unknown example stops before setter; no new safety proof |
| All crossed bodies through observed rear-clear | Same old BodyTracker; incomplete final-body observation explicitly censored |
| Native phase order and timing | Original motion/readback plus exact generic post-nextSwitch check;17 period XML clocks exercised |
| First controlled red | Same durable checkpoint mechanism, current cycle's actual timing; final EOF still required |
| Logger/EOF, one-use identity, resources | Original runtime capture/watchdog; new canonical card gate and new-only budget guardian |
| Production T1 qualification | Old launcher unchanged; no qualification bypass or formal controller integration |

## Actual verification

`OFFLINE_TESTS_V1.log`: 4 methods PASS, 1 ERROR. The actual failure was unsupported E1 domain access. Exact failing source/test preimage is retained under `failed_v1/`. No native run was involved.

`OFFLINE_TESTS_V4.log`: final-source five methods PASS, 10.014 s. Command:

```
.venv/bin/python -m unittest discover -s tests/candidate_a_unified_alinea_20261013 -v
```

Coverage: all17 XML periods with the real protected setter helper; early G closure and actual red clock; explicit dynamic requests applied at1200/1224/1234/1242 with delays0/23/8/5; same-value and superseded IDs; observed-zero/partial/unobserved accounting and excess actual N; complete XML-driven dynamic bridge; actual project Feedback/E1 seed/window bridge; independent clipped750 state versus mapped720; original gap and yellow-unknown STOP; old-stage exclusion and exhausted new reservation budget. Movement and E1 values in these fixtures are synthetic offline inputs, not observed traffic physics.

`HISTORICAL900_COMPATIBILITY_V1.json`: local recorded900 replay PASS for all72 motion/nextSwitch/entry rows and20 setter requests, including exact times, values and red readbacks. Original identity/world functions and physical post-guard code remain identical. ProgramID900 remains I12_PACKET8. Expected differences are new namespace/run IDs, command journals and explicit application-status/phase-clock metadata. The historical result is **not a native900 run of the new code SHA**, nor proof for other rates or closed loop. Full local raw is required for this replay; the public offline suite has no such raw dependency.

`PREPARE_FIXED300_V1.log`: only `UA_FIXED300_S17_01` prepared. `FRESH_CARD_AND_PERMISSION_CHECK_V1.log`: exact source/input/environment/card validation PASS; deliberately absent canonical permission rejected before native import/spawn or raw allocation. No other task cards were prepared. All536 protected files are unchanged; the copied E1 ledger class is AST-identical to its reviewed source.

## Frozen first card and outputs

Card: `packages/UA_FIXED300_S17_01/card.json`, SHA-256 `2c2330d4c977fb26c8ef52a36a16d56a7a6c94cb5334e8d5557f19eb967bed09`.

Common runtime digest: `900dcebb4f4568e6de93730977284c04f1573d02d19e6ac97ef38d79dc5702b9` (61 source/approval/dependency records). Future cards must match this digest unless an explicitly versioned technical repair is independently reviewed.

This card is fixed300, seed17, end1272, expected3 full T24 cycles; qRamp remains900. Only after exact-card release would output be allocated under `data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED300_S17_01/outputs`.

Inherited pre/post/ACK, phase/duration, admission/body, FCD/TLS, native logs and terminal-arrival journals remain. New `command_events.jsonl` records REQUESTED, SUPERSEDED, PREPARED_NOT_OBSERVED and ACK_OBSERVED. `feedback_events.jsonl` records raw E1 activation seed, every real post-ACK five-tuple, and global/logical decisions/windows with old requested state, raw/clipped output and request ID. Per-cycle rows carry program/T/Y, actual G close, quota, complete/partial status and command binding. Receipt explicitly lists pending commands, partial final cycle and censored bodies.

The **new-stage-only** total envelope is1200 monitored s /1.2GB; single-run300s/300MB, startup60s, free reserve5GB. Old Issue12 costs are excluded, retained as history. Unknown allocations conservatively charge full single ceilings. Actual costs are settled only by exact raw/receipt hashes and three-role review records. No fixed start-count limit is substituted for this resource budget.

## Limits and next gate

No actual new300/750/dynamic/ALINEA behavior has been observed. Offline fixtures do not certify physical safety, sustained rate tracking or freeway benefit. Last-step normal-arrival braking remains a required independent precision8/tripinfo post-run check, not claimed online coverage. Real ALINEA may clip to a constant rate; at least one non-initial Feedback decision must actually reach an observed G ACK. End1272 may leave a partial cycle or censored rear body; this is reported, not promoted to a complete safety/service PASS.

Safest next step: independent data prelaunch review, then scientific exact-card review. Runtime permissions and a SUMO launch remain prohibited until those gates and parent release are complete. No formal design, protocol, decision state or old evidence was changed by this implementation.
