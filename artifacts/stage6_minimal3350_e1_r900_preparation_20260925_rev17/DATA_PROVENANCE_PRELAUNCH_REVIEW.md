# Data/provenance prelaunch review — E1 qRamp900 REV17

**Disposition: `PASS_DATA_PROVENANCE_PRELAUNCH` (Blocker/Major/required Minor = 0/0/0; confidence High).** Fresh review of the FINAL exact card. REV15 is historical only. No process was started; this data review does not independently authorize execution.

- Card SHA-256: `f0387580053ad6b862ec2874a4eb55e5c9a468a3f23db561af40d6c9e6499908`.
- Run condition: qMain 3350.4, seed 17, A_OPEN, delayed R900 over `[540,1500)`, 1,396 M and 240 R; U/X are explicit zero conditions.
- Independent adapter check: PASS, 1,396/1,396 M identities and all bound attributes match the common manifest and accepted control; the sole treatment-only addition is R_flow.0–239. R schedule is 540000, 544000, …, 1496000 ms (4,000 ms interval; 1500000 ms excluded).
- R vector and source are hash-bound fixed identity-keyed materialization; this does not claim independent U=X=0 RNG generation or capacity.
- Matched-control release gate binds the exact accepted control card, data/lifecycle receipt, scientific receipt and output manifest. Required exploratory disposition is `LOW_R_BACKGROUND_ACCEPTABLE`. The legacy strict clean-high-mobility gate remains false and distinct.
- Card, input manifest, provenance receipt, scientific input files, runtime, runner, START request and request receipt hashes reconcile. START request schema is `r02-start-v2`; config is under this run's v17 output directory and reservation is under REV17 consumption. Receipt is `PASS_PERSISTED_UNSENT`, `dispatched=false`.
- All 18 data output-role targets plus two runner log targets are distinct and absent; output directory and reservation are absent.
- Resource contract: 120 s, 100,000,000 decimal bytes, 100 ms polling, slight overshoot accepted; retries = 0. The adopted D-008 plan itself grants no run authorization and its post-run exposure/stop gates remain applicable.
- REV17 focused tests: 12 passed, 0 failed. Static preflight: `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launchable_now=false` pending all fresh exact-card reviews.

The JSON receipt uses the runner-declared nested-binding schema and was checked directly with `minimal3350_treatment_data_receipt_valid`; validator result: `true`.

Machine-readable receipt SHA-256: `1d88f47e0e0499a8f82e1a886e65e1e69fdafe04b22acbb9effe5e9cabb705e7`.
