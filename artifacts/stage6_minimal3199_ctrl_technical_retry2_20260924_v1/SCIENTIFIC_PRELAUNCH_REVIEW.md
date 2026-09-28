# Independent scientific prelaunch review — MINIMAL3199_CTRL_S17_TECH_RETRY2

**Disposition:** PASS  
**Blocker / Major / required Minor:** 0 / 0 / 0  
**Confidence:** High for static scientific alignment and scope.

This record transcribes the read-only `scientific_reviewer` disposition returned after reconciling the superseded retry1 draft paragraph in `docs/PROJECT_STATE.md`. The reviewer verified that the current PROJECT_STATE and WORKLOG agree on retry1's consumed pre-SUMO Guardian failure and retry2's separate one-start scope. `docs/EXPERIMENT_PROTOCOL.md` remains unfrozen.

The exact card retains qMain=3199.2 veh/h, seed17, M=1,333, R=U=X=0, A_OPEN, and the approved 0–2700 s horizon. The network, demand, additional file, output-role source, and locked method bindings are unchanged. Staging replaces output destinations and the additional-file reference only. Retry2's runner hash is bound in its card, runtime, manifest, and START request; rev3 runner references remain historical provenance only.

The 90 s / 60,000,000-byte stop triggers, 100 ms polling, accepted slight overshoot, and zero-retry rule apply to this one attempt. Treatment, qMain=3350, seed23, B/C, and all other demand runs remain excluded. Retry1's technical failure is not treated as traffic evidence.

## Reviewed hashes

- FINAL card: `b387a750f9f41fe7439d79ead7133fc07ac817fe8da497a8e045433a4accee5a`
- Execution manifest: `551fdfbe78530662f2a437436d8a36813902d5728ac88b03a7a316382d7bca9a`
- Persisted START request: `45d6f25b3f2f099cf67286859c0421cf23f0e0055ca6c31cea8d380c17fac64e`
- Runtime binding: `95f3d7bdae0dfd5f629d28e1ebf2bcdb0e957c6eb790f61307442704a82c373d`
- Current runner: `4f31c3e1be5d4aba841ebb2ca00a6f7df90f2d6a434819ac83ed262d4401b529`
- Engineering review JSON: `5cf690592c55cbf2080013d909f894104ef1890b6a9d61d2c55fb6e74d73473e`
- Data/provenance review JSON: `c4220e4c2c38df6d3dc61e2042185e581a184ae9693e423e3b8fa6bc8f6173fb`
- Approved minimal plan: `06b0f04f1144ef8497b4d64906ae27b1377b544abd6e0639133c8d85a3fabc23`
- Locked P/S/L method: `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`

The reviewer evaluated static alignment only. No simulation was run and no outcome was examined. This PASS applies only to this exact retry2 card.
