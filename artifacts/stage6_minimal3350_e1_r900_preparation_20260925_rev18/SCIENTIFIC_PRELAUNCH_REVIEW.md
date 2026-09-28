# Independent scientific prelaunch review — E1 R900 technical retry

**Disposition:** PASS  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Confidence:** High for scientific-condition continuity; Moderate for cross-rate exposure interpretation.

Reviewed exact card: `MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY1_CARD_FINAL_REV1.json`, SHA-256 `d71c0580a4020b3f94a39d8d8e134560ca1181dd2c08d06ae230ff7218377f5d`.

The retry preserves qMain 3350.4, seed 17, U=X=0, A_OPEN, delayed R900 over `[540,1500)`, 240 planned R vehicles, and the same 1,396-vehicle common M vector. The demand input is byte-identical to the first E1 attempt; the R vector and witness-contract hashes are unchanged. The sumocfg/additional references now bind to REV18's staged inputs and distinct output root. No scientific-input change was identified.

The earlier E1 attempt remains `NOT_EVALUABLE`; its output is preserved separately and its one-start authorization is consumed. The current user explicitly authorized one independent technical retry after fresh engineering/data/scientific PASS reviews. This review releases only the exact retry card; it does not authorize E2 or any other run.

**Observation retained:** The first 192 R identities' speedFactors match 0/192 to the R720 vector. This does not invalidate R900 versus R0, but limits attributing a later R900-versus-R720 exposure increase solely to nominal qRamp.

No future outcome was inspected. The reviewer changed no files and started no processes.
