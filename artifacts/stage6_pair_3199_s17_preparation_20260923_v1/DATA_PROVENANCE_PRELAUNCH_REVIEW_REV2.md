# Independent data/provenance prelaunch review — pair rev2

**Disposition: PASS. Blocker/Major/required Minor = 0/0/0. Confidence: High.** Independent read-only reviewer: project `data_analyst`.

Both rev2 card hashes, runtime sidecar hashes, identity-manifest hashes and declared scientific input hashes match the current R02 binding receipt. Compared with revision 1, the qMain/qRamp, demand windows, seed, accepted network, TLS program, vehicle type/routes/behavior, time step and horizon are unchanged. Demand remains M=1333 [0,1500), U=150, X=75 in both arms; control has no R source (planned R=0), treatment adds R=192 [540,1500), exactly 720 veh/h. Both use seed17, A_OPEN, 1 s steps, 2700 s horizon and the same accepted network.

Each arm binds 18 unique, run-scoped output roles. Config, additional outputs and raw targets are separated by run ID. Both future raw output paths and the one-use consumption directory are absent. Runtime sidecar, card, runner hash, run ID and resource scope match. Both resource caps remain `PROPOSED_NOT_AUTHORIZED`.

The prior `PROVENANCE_RECEIPT.json` is retained as revision-1 history; current cards/runner/reviews are bound by `PROVENANCE_RECEIPT_REV2.json`. This review used existing runtime evidence and did not probe the host. Actual runtime compatibility, detector coverage, realized insertion/merge exposure and post-run raw reconciliation remain unverified. No raw data was read or parsed, and no execution tool was invoked.
