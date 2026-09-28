# MINIMAL3199 R720 treatment — engineering prelaunch review, revision 2

- **Disposition:** `PASS_PRELAUNCH`; Blocker/Major/required Minor = `0/0/0`.
- **Exact card:** `artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1_CARD_FINAL_REV2.json`; SHA-256 `f3d7d03e0b521d330a6ccc07d807bd88149ce4eb424e3f3895f917e083234b5e`.
- **Request persistence:** `START_REQUEST.json` is canonical `r02-start-v2`, 7274 bytes, SHA-256 `6019c720af6a65138ed71a10c3d89e83fb05274cbffe34c23a0caaf70c4e450a`. Its sidecar binds the exact card SHA and request SHA, output/reservation paths, 90 s / 75,000,000-byte resources, and `dispatched=false`. The card binds request and sidecar paths/schema only; the request digest is not embedded into its own card or request, avoiding a hash cycle.
- **Fail-closed behavior:** preflight and the launch preparation path reconstruct the request and require byte-for-byte and sidecar equality. A request/path/resource/schema mismatch is rejected. Review-gated dispatch remains separate; missing data/scientific reviews keep this package unlaunchable.
- **Matched static inputs:** M `1333/1333` exactly match on identity, desired depart, route, vType, speedFactor, departPos, departLane and departSpeed; control R=0; treatment adds R192 (`R_flow.0..191`); U/X are explicitly zero.
- **Resources:** wall-clock stop trigger 90 s; output trigger 75,000,000 bytes; 100 ms polling; slight overshoot accepted; one start, no retry.
- **Staging:** only `scenario_control.add.xml` (4048 B, `0a476ff96e378ae8972de96cba1b1748274158a29bc7f9f3408be70996e3b2f0`) and `scenario_control.sumocfg` (2885 B, `839cd0604aa2eef5da3677dae06296995fc3c017b9a84f1f8cf0ed0315d47d54`) exist in the output directory; transform counts and no-old-path checks pass. Consumption is absent.
- **Tests:** treatment/minimal modules `35/35 PASS`; R02 regression suite `24/24 PASS`.
- **Execution:** no Guardian request was sent and no process started. `make_plan` is expected to report `launchable_now=false` until fresh data/provenance and scientific receipts plus their hash sidecar pass.
