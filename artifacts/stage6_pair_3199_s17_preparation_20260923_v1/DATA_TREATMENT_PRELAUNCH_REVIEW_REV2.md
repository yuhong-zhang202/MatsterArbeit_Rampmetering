# Independent data/provenance prelaunch review — PAIR_3199_R720_DELAYED_S17 REV2

**Disposition: PASS.** Blocker/Major/required Minor = **0/0/0**. Confidence: High for static provenance and exact binding. This is a fresh read-only review of REV2; it is not a launch authorization or a review of future treatment outcomes.

## Context and scope

Completed the required context preflight by reading `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`. The current recorded decision is the user's scoped adoption D-005: the Stage 6 exploratory witness contract applies only to this PAIR3199 matched pair, does not enter the formal protocol, does not rewrite the control history, and does not authorize execution. The formal experiment protocol remains unset/unfrozen. Also read the exact adopted contract and its independent scientific PASS, REV2 treatment card and input snapshots, Rev2 engineering review and read-only preflight, and the existing control card/raw/processed receipts and post-run reviews. No raw/processed data, scientific inputs, protocol, classifier or thresholds were edited; no SUMO, TraCI, netconvert, or analysis pipeline was run.

## REV2 card and binding checks

The recomputed SHA-256 for `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV2.json` is `6e810adfe70c03ff321ba47a4fff6593323e5b4a78884ce8e6971ffd86bb8d25`, matching the requested hash. The card's internal `card_revision` is 4; the file is the package's PRELAUNCH_REV2 snapshot. The runtime sidecar recomputes to `5c72fa902c828b2d85efc4f5adf4ff1d534526d2ccebdf352fb5c2d703cefb6f`, and the bound runner recomputes to `482056a14df16af779ef8c8ad8182c313775a3392caa24e1e5224e9f0c1c8a37`. The design-plan and contract hashes also match their current files.

All six scientific input bindings match the card: demand `6fe53e5b294184704ee5dbd575ccb2c225c17b57014c5c981b60ba557a9ae400`; additional `13dc69427f24014e02c4ded173ba5d2db12ebf2666c0b77f2cc486a19755332a`; accepted network `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`; output-role file `7dab35372984ccd3e7f103afaaf0dff59ecf4df6dc13d4c66dea5190fa77155d`; sumocfg `70a082e81a32f3a759a8b26cd9cbf426358d7cf4f40eedcef72d3f272d851072`; expected-identity manifest `a69ba23ed1a82957904c8abc4aee774decf94d0210c07d29d051c0162f7aef1b`.

The card retains qMain=3199.2 veh/h, M=1333 on [0,1500), U=150, X=75, seed17, A_OPEN, 1 s steps and 2700 s horizon. Treatment demand is R=192 on [540,1500), equivalent to qRamp=720 veh/h. The treatment input snapshots and pair input-diff record preserve the intended matched design: the sole scientific demand difference is adding R; the common M/U/X, network, routes/type, seed, TLS and horizon are unchanged.

## Contract, seven markers, and control history

The card binds the user-adopted contract at SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`. Scope is explicitly limited to this Stage 6 exploratory treatment and excludes the formal protocol. REV2 has seven separate ordered timeline markers: `R_demand_activation`, `first_scheduled_R_departure`, `first_actual_R_departure`, `first_R_arrival_near_merge`, `first_meaningful_merge_exposure`, `first_M_deterioration`, and `State1_onset`. They match the clarification in the adopted contract's event-order requirement and separate planned/actual departure and arrival/exposure.

The old `LOW_R_BACKGROUND_ACCEPTABLE` gate is explicitly not required for this treatment release (`false`); the treatment gate is the adopted exploratory witness contract. Exact control bindings match: control card `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`; control data review `6c8c2a381a5a2fc1102953ed58a5a1cd022a0c22789b0bbbd486d86a7b0ac799`; execution receipt `a6a1a67282ff9e19f0205ce4b681cef34315bc04ad65f9588d7b269fadcfd336`; raw output manifest `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8`.

All **27/27 raw files** and **25/25 processed outputs** again recompute to the hashes in the existing independent control receipt. Control raw/data records remain explicit R=`PASS_ZERO`, overall/background status `NOT_EVALUABLE`, P/S/L=`NO_QUALIFYING_EVENT`, Candidate C=`EARLY_WARNING_PRESENT_NOT_STATE1`, and fixed screen counts PRE 3/30 PASS and control 17/150 PASS (thus the historical screen failures remain). Low-speed/C warnings are retained. `use_as_clean_normal_baseline=false`. The prior control data review's DM-01 card-metadata finding remains in its original report; it is not a data hash mismatch and this review does not clear or rewrite it.

## Resource and path disposition

The proposed limits remain treatment-scoped metadata only: 120 s and 90,000,000 decimal bytes, with 100 ms polled output stop trigger and possible overshoot. Status is `PROPOSED_NOT_AUTHORIZED`; no start authorization is inferred. REV2 card remains `execution_authorized=false`, `run_command=null`, and requires approval. Its read-only preflight receipt binds the exact card SHA, reports `PREFLIGHT_PASS_NO_PROCESS_STARTED` and launch authorization false. At review time the treatment output directory and unique consumption/reservation file are both absent.

**Conclusion:** Exact REV2 input, contract, runtime, runner, control, and path/provenance bindings pass this data review. This does not establish treatment lifecycle, actual R departure/merge exposure, event ordering, data completeness or a witness; those are unknown until a separately authorized run and post-run review. No SUMO/TraCI/netconvert starts occurred.
