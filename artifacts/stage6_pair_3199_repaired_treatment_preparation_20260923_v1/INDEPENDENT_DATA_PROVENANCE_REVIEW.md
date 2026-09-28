# Independent data/provenance prelaunch review — repaired PAIR3199 treatment

**Disposition: PASS for static input/provenance preparation only.** Findings: Blocker 0 / Major 0 / required Minor 0. This review does not authorize execution and does not establish future insertion or trajectory equivalence.

## Context preflight and boundary

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/WORKLOG.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, v5 repair receipts/manifest/invariant report and its independent data review, and the new package including `INDEPENDENT_ENGINEERING_REVIEW.md/.json`.

The current phase is offline preparation following v5's matched-input repair. Stage 6 remains partial, O2 is unresolved, and the formal protocol is unfrozen. D-005 scopes the witness contract to this exploratory pair. The prior treatment remains `NOT_EVALUABLE`; its one-start D-006 authorization is consumed. The new card is a separate draft and execution is unauthorized.

## Independent checks and evidence

- Ran the v5 strict checker offline against v5 `control/demand.rou.xml` and the new package's treatment demand. Result: **PASS**, no failures.
- The checker found 1,558/1,558 exact common M/U/X vehicle records: IDs, integer-ms desired departure schedules, route/type, and explicit speedFactor; route definitions 4/4 and vType definitions 1/1 agree. Counts are control M/U/X/R = 1,333/150/75/0 and treatment = 1,333/150/75/192.
- Treatment-only set is exactly 192 identities, `R_flow.0`–`R_flow.191`; control-only identities = 0. The R schedule is 192 records over `[540,1500)`, integer offset 5,000 ms (first 540.000 s, last 1495.000 s), route `R_route`, type `technical_passenger`.
- The repaired treatment demand SHA-256 is `b8aae801122e918731fb8e05a9aa8ca94873f02282d7f1afee57777f6bea96ea`, identical to v5. The new package receipt's 11 listed file hashes all recompute successfully. Card, manifest, runtime-sidecar, runner, network, demand, sumocfg, additional file, output-role file and adopted contract hashes all match the card/receipt bindings. New exact card SHA-256: `593cabd4c82a8b7b735e6ebc000d836bebab80a9c8962e20f2865a5bbf4dbed0`.
- Existing control linkage was checked against the final control card and its recorded artifacts. The final control card's original demand SHA-256 `6bbdc1d9148b05286c25b94f23c37174951c9f3e4a544ef8b9a322fbc42ab631` matches its file and the v5 manifest source. The new card's control raw-card, data-review, execution-receipt and output-manifest hashes all match their files.
- The treatment card explicitly preserves control `historical_low_r_status=NOT_EVALUABLE` and `use_as_clean_normal_baseline=false`; it does not reuse the old treatment card or raw output. The new output root and output directory are absent and distinct. The new consumption directory exists but is empty.
- The card remains `DRAFT_NOT_AUTHORIZED`, `execution_authorized=false`, and `run_command=null`. The resource proposal (90 s / 75,000,000 decimal bytes, 100 ms polling, slight overshoot possible) is explicitly `PROPOSED_NOT_AUTHORIZED`.
- The current independent engineering review is `PASS_PREPARATION_ONLY_NOT_AUTHORIZED`, 0/0/0, and records the exact bound-interpreter R02 suite as 22/22 PASS. No simulation-related process was started by this data review.

## Interpretation limits

The static check verifies planned inputs, not realized vehicle insertion, lifecycle, or traffic trajectories. In particular, it cannot establish that M/U/X trajectories before meaningful R exposure will be equivalent. The preregistered post-run gate correctly makes unexplained material pre-R divergence `NOT_EVALUABLE` and permits post-R witness analysis only after that gate passes. Recorded speedFactor lexical precision follows the v5 provenance method; this is not evidence of unrecorded floating-point bits or future runtime random behavior.

**Data/provenance prelaunch review: PASS**, limited to hashes, planned identity/schedule/route/type/speedFactor matching, treatment-only R identities, control provenance preservation, and output-path isolation. **SUMO starts = 0; TraCI starts = 0; netconvert starts = 0.**
