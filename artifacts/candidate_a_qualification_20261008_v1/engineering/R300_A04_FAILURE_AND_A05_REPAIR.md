# R300 A04 startup failure and A05 minimal repair

## Executed attempt

Command: `.venv/bin/python scripts/candidate_a_qualification_20261008_v1/runner.py --launch config/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A04/card.json --release artifacts/candidate_a_qualification_20261008_v1/RELEASE_FIXED_R300_A04.json`.

A04 exact card/source/static checks passed. Worker and SUMO were actually started, but the connection adapter failed before any simulationStep: `TypeError: 'PosixPath' object is not callable`. Worker status ABORTED_TECHNICAL; last completed/accounted time0; cycle0; C/E/N0. **No traffic/safety/service qualification result; no300s window observed.** This is a technical startup failure, not an effective qualification run.

Guardian elapsed5.63024 s and payload787016 bytes; no resource limit trigger. Native stdout/stderr are empty; the guardian stderr retains the TypeError. No native traffic warning or safety outcome can be claimed because no motion step occurred. Failure raw remains immutable at `data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A04/outputs/`.

Original `worker_receipt.json`, `failure_snapshot.json`, `guardian_receipt.json`, all header-only phase/crossing/cycle files and exact source/config/card/network snapshots are retained. The append-only engineering `execution_ledger.jsonl` records the attempted launch and hashes. Failure snapshot SHA256: `44cf27e50063570d8460079169b773ba7301b0fd300d5ae83b600f4516c8197b`.

## Diagnosis and minimal correction

The protected inherited `connect_traci(traci_module,port,process,trace,...)` calls `trace(event)` for every connected/failed attempt. A04 passed a Path rather than a callable. A05 replaces that argument with an exclusive-created `startup_trace.jsonl` callback, retaining each JSON event without overwriting old trace files. No actor, safety envelope, native phase behavior, nominal n, demand, seed,1s step, protected upper law or resource limit changed.

An offline mock calls the actual inherited connection helper with a mocked TraCI module/process, verifies successful callback delivery, multiple JSONL events and refusal to overwrite. No socket/SUMO startup is used by the test. Full24/24 tests and syntax checks pass; all67 protected hashes pass. Test/source/repair/card binding: `R300_A05_REPAIR_OFFLINE_RECEIPT.json`. All five new A05 cards are source-consistent in `PHASE_A_A05_FINAL_CARDS.json`.

## Next gate

No retry has been launched. Independent failure-accounting and incremental science review must precede an exact A05 R300 replacement release binding this failed snapshot and repair evidence. Other four rates and Phase C remain HOLD. Failed A04 sources/card/raw are preserved, not overwritten or treated as a valid traffic result.
