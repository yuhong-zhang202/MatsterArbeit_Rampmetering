# Independent scientific prelaunch review — PAIR_3199_R720_DELAYED_S17 REV2

**Disposition:** `PASS` — Blocker/Major/required Minor = `0/0/0`  
**Confidence:** High for card-to-contract alignment; Moderate for attribution from a future single exploratory pair.

## Context and provenance

The user adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md` only for Stage 6 exploratory validation of the matched pair `PAIR3199_CTRL_S17` + `PAIR_3199_R720_DELAYED_S17`. This is not part of the formal experiment protocol. The exact treatment card is `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV2.json`, SHA-256 `6e810adfe70c03ff321ba47a4fff6593323e5b4a78884ce8e6971ffd86bb8d25`; the contract SHA-256 is `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.

## Scientific assessment

The fixed values remain qMain=3199.2 veh/h, seed17, A_OPEN, R=720 veh/h over `[540,1500)`, with matched geometry, M/U/X, vehicle behavior and horizon. The existing PAIR3199 control is only a candidate comparator. Its `LOW_R_BACKGROUND_ACCEPTABLE=NOT_EVALUABLE`, fixed-screen failures and low-speed/C warnings remain preserved; it is not described as a clean normal baseline. The old LOW_R gate is not a treatment release prerequisite under this narrowly adopted contract.

REV2 explicitly distinguishes all seven ordered markers: R demand activation; first scheduled R departure; first actual R departure; first R arrival near the merge; first meaningful merge exposure; first M deterioration; and State1 onset. The bound contract governs actual exposure, matched comparison at the same time/location/lane/cell, independent raw recalculation and alternative-cause review. Classifier, thresholds, scientific inputs and formal protocol remain unchanged.

Independent engineering and data/provenance REV2 reviews both pass. The treatment-only resource proposal remains 120 seconds and 90,000,000 bytes, marked `PROPOSED_NOT_AUTHORIZED`.

## Measurement boundary and conclusion

Actual treatment coverage, lifecycle, R merge exposure, event order and treatment-control effects cannot be checked before the run. Those checks remain mandatory after any separate authorization. This review finds REV2 scientifically suitable to await a separate single-start authorization; it does not itself authorize a run or establish a witness. No SUMO, TraCI or netconvert process was started; the reviewer made no file changes.
