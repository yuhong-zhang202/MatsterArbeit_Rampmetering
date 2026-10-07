# FIX02 final engineering execution summary

2026-10-07. Bounded DEVELOPMENT completed; no more simulations. Final scientific synthesis review remains the primary agent's required next gate.

The exact remaining-eight release was executed sequentially in its fixed order, with an independent persisted data/integrity/observed-safety/rule PASS before each subsequent launch. All12 corrected controls have completed4200s and all12 corresponding independent gates are now persisted and hashed in FINAL_EXECUTION_LEDGER.json. Six accepted OPEN baseline slots yield18 corrected comparison cells. All service capability dispositions remain NOT_QUALIFIED; this is not900veh/h service qualification or formal effect evidence. Accounted endpoint vehicles remain included in finite-horizon analysis.

## Actual execution and resources

- Actual worker attempts:16; physical SUMO starts:15; completed new runs:14; failed attempts:2. These counts are enumerated from actual receipts, not prepared-card suffixes. The completed14 comprise12 FIX02 controls, one new neutral OPEN and one old-guard diagnostic T2. The failures are the preserved pre-SUMO sandbox socket failure and original R750/S17 post-green safety abort. Offline FIX01 and card preparations add no worker/SUMO starts.
- All-attempt guardian time sum:875.307419s. This is the sum of execution durations, not total project elapsed time including analyses/reviews.
- All-attempt payload bytes:1323070588; actual new raw directory bytes including receipts:1323153268 (1.323153GB).
- The12 corrected controls consumed775.498666s of guardian time and1247732760B payload. Per-run time range49.848–99.317s, median62.116s, mean64.625s. Per-run payload range94580952–112299779B, mean103977730B.
- All runs stayed below180s/run and300MB/run; new raw stayed below4GB. Free disk at final readback:20340084736B, above5GB reserve. Startup60s and polling0.2s remained unchanged. No raw cleanup or resource purchase occurred.

## Implementation, provenance and warnings

The corrected safety precondition is the independently reviewed green-step advance plus unchanged post-red braking requirement. Actual entrant bounds were recorded in every corrected run; the intended-front heuristic and mandatory original post interlock remain. Engineering completion summaries checked every run's guardian manifest and4200s log; the independent data agent performed the full native replay, occupancy, cohort and endpoint gates. No traffic outcome or rate failure caused retuning or reruns.

The original src/stage6_safe_actuator_v10.py, original V15 runner/control sources, original parameter contract, network, SUMO binary and old raw are preserved. The earlier development source version is archived under pre_fix02_sources with exact hashes. Final ledger readback confirms all frozen corrected and immutable source hashes, original contract and repair addendum still match the first corrected card. No source/parameter changes occurred during the12 corrected executions.

Completed workers retain the TraCI `UserWarning: API change now handles step as floating point seconds`; SUMO traffic-error logs remained empty. This interface warning is not a concealed traffic warning. The separate engineering summary collector initially failed to parse the trailing punctuation in the SUMO end-time string; its report-only parser was corrected. That event did not modify simulation code/cards/raw or create another simulation attempt. All historical technical failures and the original negative rate results remain preserved.

## Evidence and exact commands

FINAL_EXECUTION_LEDGER.json contains every actual receipt path/hash, run status, resource usage and all12 independent gate paths/hashes. Its SHA256 is `4caff96d12fb7f489575bd4af3b70acf461fc786535172a5612956d4de6f6a0b`. Each `DEV_*_TECHNICAL_COMPLETION.json` contains the exact executed launch command, card/receipt hashes, manifest check, endpoint log and runtime entrant coverage. All launch commands used the existing `.venv/bin/python -B scripts/formal_development_20261007_v1/runner.py launch --card <exact card> --release <exact release>` through the approved local TraCI permission path.

The final summary command was `.venv/bin/python -B artifacts/formal_development_20261007_v1/engineering/finalize_execution_ledger.py`: PASS. No active launch lock remains. No optional tests or additional simulations follow. Formal protocol remains unchanged/unfrozen; Stage6 remains closed. The data analyst owns the final18-cell analysis and figures; the primary owns WORKLOG/PROJECT_STATE/README updates and independent final scientific review. No such final scientific review is claimed by this engineering summary.
