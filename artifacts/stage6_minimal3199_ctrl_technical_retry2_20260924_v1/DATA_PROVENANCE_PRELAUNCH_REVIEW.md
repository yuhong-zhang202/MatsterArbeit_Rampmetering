# Data/provenance prelaunch review — MINIMAL3199_CTRL_S17_TECH_RETRY2

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Blocker / Major / required Minor:** `0 / 0 / 0`  
**Confidence:** High for static input and execution provenance.  
**Scope:** Read-only review of the exact-card inputs, runtime, persisted START request, staging, and output/consumption bindings. This is not an engineering or scientific review and establishes no simulation outcome.

## Exact-card binding

| Object | SHA-256 |
|---|---|
| FINAL card | `b387a750f9f41fe7439d79ead7133fc07ac817fe8da497a8e045433a4accee5a` |
| Execution manifest | `551fdfbe78530662f2a437436d8a36813902d5728ac88b03a7a316382d7bca9a` |
| Persisted START_REQUEST | `45d6f25b3f2f099cf67286859c0421cf23f0e0055ca6c31cea8d380c17fac64e` |
| Runtime binding | `95f3d7bdae0dfd5f629d28e1ebf2bcdb0e957c6eb790f61307442704a82c373d` |
| R02 runner | `4f31c3e1be5d4aba841ebb2ca00a6f7df90f2d6a434819ac83ed262d4401b529` |
| Adapter | `9f7a459a167884533f5f044018bf209a24ed154173d044ce80baa7640a6311b8` |
| Approved U=X=0 plan | `06b0f04f1144ef8497b4d64906ae27b1377b544abd6e0639133c8d85a3fabc23` |
| Rev3 source receipt (historical input/design scope) | `28addb6e2c26ee2de3810f88fb8896134393793e820874da61ebdbef316b1f44` |

## Checks

- Scientific condition matches the adopted plan: qMain `3199.2`, seed `17`, `A_OPEN`, control `R=0`, explicit `U=0` and `X=0`, and planned M count `1333`.
- Independently parsed the bound rev3 control/treatment demand XML: M counts `1333/1333`; identical M ID sets; zero mismatches across ID, depart, route, type, speedFactor, departPos, departLane, and departSpeed. Control identity classes are M=1333/R=0/U=0/X=0; treatment has M=1333/R=192/U=0/X=0. The control arm adds no R demand.
- Card and manifest bind the same current run ID, card, inputs, output directory, resource values, runtime, runner, and schema. Runtime binary, additional schema, and Python interpreter hashes match the bound sidecar. The historical rev3 receipt is explicitly designated as input/design provenance only; its earlier runner hash is not used as the retry2 execution binding.
- Ordered staging contract records 8 sumocfg output-root replacements, 1 sumocfg additional-file path replacement, and 12 additional-XML output-root replacements. Staged control sumocfg is 2,802 bytes / SHA-256 `f91c2fa87b12e83e39d27051e01d56f231d9a0a074e6ea445200d294adbf677b`; staged additional XML is 3,940 bytes / SHA-256 `354c1dcffc9f4b18d6e92f1dd4658098f0e24b3d2ab30671df4a1faefb6d62f3`. The files exist under the unique retry2 output path.
- The persisted `START_REQUEST.json` is schema `r02-start-v2`, for `MINIMAL3199_CTRL_S17_TECH_RETRY2`, with output directory and SUMO config command bound to the retry2 path, card/manifest/runtime/runner/schema hashes consistent with the FINAL card, 90 s and 60,000,000-byte limits, and 18 bound output-role definitions matching the source role file. The role records retain the historical source `path` strings; the runner validates those records against the bound role source, while its output-manifest builder maps artifacts by role basename under the separately bound retry2 output directory. Actual staged config/additional paths point to retry2. Request provenance says it was validated and persisted but not sent; `guardian_invoked=false`, `launch_invoked=false`, `simulator_started=false`.
- The retry2 consumption/reservation path is absent. The retry2 output inventory contains exactly the two staged inputs; there is no traffic output, output manifest, execution receipt, or other attempt artifact. Earlier failed attempts remain separate and untouched.
- No process was launched for this review. No scientific input, network, behavior, classifier, threshold, or formal protocol was changed.

## Interpretation boundary

This PASS covers static input/provenance binding only. It does not establish successful Guardian/SUMO startup, realized insertion, lifecycle completion, exposure, or any P/S/L or Candidate A/C result. The request has not been sent and the one-use reservation remains absent.
