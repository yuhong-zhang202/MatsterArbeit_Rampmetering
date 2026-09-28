# Data/provenance prelaunch review — REV2

- **Run:** `MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1`
- **Exact card SHA-256:** `f3d7d03e0b521d330a6ccc07d807bd88149ce4eb424e3f3895f917e083234b5e`
- **Disposition:** `PASS_PRELAUNCH`
- **Confidence:** High
- **Findings:** 0 blocker / 0 major / 0 required minor

## Control reference

The exact card binds to successful control `MINIMAL3199_CTRL_S17_TECH_RETRY2` with current hashes for the control card, data/lifecycle review, independent scientific review and raw output manifest. Its `LOW_R_BACKGROUND_ACCEPTABLE` disposition is scoped only to the approved minimal U=X=0 test. Candidate C warnings and strict high-mobility-screen FAIL remain historical; this control is not a clean high-mobility baseline.

## Matched demand audit

Both arm inputs contain 1,333 M identities. IDs and all seven bound attributes match 1,333/1,333: desired departure, route, vType, speedFactor, departPos, departLane and departSpeed. The actual completed control raw has 1,333 M vehroute identities and zero route/vType/speedFactor mismatches. Control R=0 is bound through its exact final card and raw manifest.

Treatment contains exactly 1,333 M and 192 R vehicles. R IDs are contiguous `R_flow.0`–`R_flow.191`, departures are 540–1495 s every 5 s, and the route is `urban_in shared_approach ramp_storage ramp_accel merge_section main_down`. The only identity-set difference is those 192 R vehicles; U/X and duplicates are absent. Global `(depart_ms, id)` order passes. qMain=3199.2, seed17, U=X=0, A_OPEN, 2700-s horizon, 1-s step and network hash `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` match the approved plan.

## Request, runtime and staging

The canonical request (`r02-start-v2`) is 7274 bytes, SHA-256 `6019c720af6a65138ed71a10c3d89e83fb05274cbffe34c23a0caaf70c4e450a`. Its receipt SHA-256 is `5846d84b8c2711a5a1c4b6788a0a7446d5d1708cf0a03174e6049f8edefd572b`; the receipt binds the request hash/size and exact card hash. It records `PERSISTED_UNSENT` with `dispatched=false`. The request’s action, command/config path, output path, reservation path, runtime/schema/runner hashes and 90-s / 75,000,000-byte limits match the REV2 card and runtime sidecar.

Runtime, SUMO 1.26.0 binary, additional schema, Python executable, runner, network and role-source hashes match. Deterministic staging reconstructs `scenario_control.sumocfg` at 2,885 bytes / `839cd0604aa2eef5da3677dae06296995fc3c017b9a84f1f8cf0ed0315d47d54` (8 output-root rewrites plus 1 additional-file rewrite), and `scenario_control.add.xml` at 4,048 bytes / `0a476ff96e378ae8972de96cba1b1748274158a29bc7f9f3408be70996e3b2f0` (12 output-root rewrites); there are no residual old paths. The output directory contains only these two staged files and the unique consumption directory is absent. Engineering reports the 35 treatment and 24 shared-runner tests passed; this review did not rerun them.

## Review boundary

This is a data/provenance prelaunch PASS for the REV2 exact card only. It establishes no treatment outcome and does not broaden the control’s minimal-test scope. The earlier REV1 BLOCKED receipt remains preserved and unchanged.
