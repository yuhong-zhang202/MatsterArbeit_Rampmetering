# MINIMAL3199 R720 treatment — engineering prelaunch review

- **Disposition:** `PASS_PRELAUNCH` (Blocker/Major/required Minor = `0/0/0`).
- **Run/card:** `MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1`; exact card SHA-256 `924d4fce7098d5d69e60dc6ecb50b00b6c1a4b0eb527d0153f7681969b58d714`.
- **Condition:** qMain 3199.2, seed 17, U=X=0, A_OPEN, delayed R=720 on `[540,1500)`, horizon 2700 s.
- **Static matched input check:** M `1333/1333` exact across ID, desired depart, route, vType, speedFactor, departPos, departLane, departSpeed; control R=0; treatment R=192, exactly `R_flow.0..191`; explicit U/X zero in both arms.
- **Resources:** 90 s wall-clock trigger; 75,000,000-byte output trigger, 100 ms polling, slight overshoot accepted; one start maximum; retries zero.
- **Runtime/binding:** SUMO 1.26.0 binary, SUMO_HOME, schema, Python environment, runner, manifest and runtime sidecar hashes verify.
- **Staging:** output contains only `scenario_control.add.xml` (4048 B, `0a476ff96e378ae8972de96cba1b1748274158a29bc7f9f3408be70996e3b2f0`) and `scenario_control.sumocfg` (2885 B, `839cd0604aa2eef5da3677dae06296995fc3c017b9a84f1f8cf0ed0315d47d54`); deterministic source rewrite counts match and no old output root remains. Consumption path absent.
- **Runner correction:** START validator previously hard-coded the control's 60,000,000-byte cap. It now obtains both resource values from the exact run binding, preserving control's 60 MB and matching this treatment's 75 MB contract. Valid `r02-start-v2` acceptance is unit-tested under a mock PASS receipt gate; invalid resource/path/schema requests fail closed. No Guardian dispatch occurred.
- **Verification:** minimal3199 modules `33/33 PASS`; R02 shared runner module `24/24 PASS`. The old completed repaired-v5 card is rejected on its stale runner hash, as required by fail-closed provenance; its immutable historical raw is unaffected.
- **Execution gate:** `make_plan` returns `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launchable_now=false`, because data/provenance and scientific exact-card receipts and the receipt-hash sidecar are pending.
- **Process counts:** SUMO 0, Guardian 0, TraCI 0, netconvert 0.

This is an engineering execution-binding review only. It does not classify treatment data or replace data/provenance or scientific review.
