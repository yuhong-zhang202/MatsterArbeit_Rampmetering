# Independent engineering prelaunch review — pair rev2

**Disposition: PASS. Blocker/Major/required Minor = 0/0/0. Confidence: High.** Independent read-only reviewer: project `simulation_engineer`.

The runner accepts only three exact allowlisted bindings: the consumed RI3350 technical retry and these two pair run IDs. Pair run IDs bind to fixed card/package/input/runtime-sidecar/output/consumption paths. The runner checks card and input hashes, runtime sidecar hash and content, canonical per-run sidecar path, runtime/resource run scope, runner hash, Python executable/version/package bindings, SUMO binary path/hash/version evidence, canonical `SUMO_HOME` and local schema path/hash, positive finite resource values, output-role provenance, existing output refusal, DRAFT refusal, one-use reservation and zero retry. Pair `run_command` remains null and cards stay `DRAFT_NOT_AUTHORIZED`.

Cross-arm sidecar-path and scope tampering tests reject the control-to-treatment relabeling. Independent rerun of mock suite: **16/16 PASS**. `py_compile` and `git diff --check` PASS. Current runner, test, card and runtime-sidecar hashes match `R02_ENGINEERING_BINDING_RECEIPT_REV2.json`. Existing RI3350 retry parent/reservation checks remain explicit.

Per-run proposed limits: **90 s** and **60,000,000 decimal bytes**. Basis: preserved successful RI3350 retry actual wall-clock **24.465112 s** and output payload **21,720,062 bytes** (proposals are approximately 3.68× time and 2.76× output). The 100 ms output polling trigger can overshoot and is not a hard quota. Both values are `PROPOSED_NOT_AUTHORIZED`; no prior run authorization transfers.

Test-source limitation: the former 23-test source was overwritten before preservation and could not be recovered. The current 16-case mock suite retains the nine PAIR-specific gates and reconstructs selected Guardian/durability contracts from the prior receipt. It is not the original suite and does not demonstrate real SUMO/runtime compatibility. No SUMO/netconvert/TraCI or runtime probe occurred.
