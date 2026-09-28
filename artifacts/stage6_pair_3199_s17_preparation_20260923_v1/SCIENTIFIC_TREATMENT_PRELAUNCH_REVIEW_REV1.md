# Independent scientific prelaunch review — PAIR_3199_R720_DELAYED_S17

**Disposition:** `PASS` — Blocker/Major/required Minor = `0/0/0`  
**Confidence:** High for card-to-contract alignment; Moderate for attribution from a future single exploratory pair.

## Scope and provenance

The exact treatment card is `PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV1.json`, SHA-256 `263c63f356b02353655a5e8e06eb7089d527e82f8137f45a8ecaf63054fd38a4`. It binds `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`. User adoption is explicitly limited to Stage 6 exploratory validation of the PAIR3199 matched pair; the formal experiment protocol is unchanged.

## Scientific assessment

The treatment settings match the reviewed contract: qMain 3199.2 veh/h, seed 17, A_OPEN, R=720 veh/h over `[540,1500)`, and matched M/U/X, geometry, vehicle behavior and horizon. `PAIR3199_CTRL_S17` is a candidate comparator only; it is not called a clean normal baseline. The existing `LOW_R_BACKGROUND_ACCEPTABLE=NOT_EVALUABLE`, failed fixed screens and Candidate C/low-speed warning history remain intact.

The card explicitly does not require the old `LOW_R_BACKGROUND_ACCEPTABLE` gate for this treatment release. It records all five chronology markers: R activation, first R departure, first meaningful merge exposure, first M deterioration, and State1 onset. The adopted contract remains bound for realized exposure, matched same-time/location/lane/cell comparison, independent raw recalculation, event ordering, alternative-cause checks, and the outcome labels. No classifier, threshold, or formal protocol change is specified.

Treatment-only limits are positive and marked `PROPOSED_NOT_AUTHORIZED`: 120 seconds and 90,000,000 bytes, with 100 ms polling and possible stop overshoot. They do not authorize a launch. Engineering and data/provenance prelaunch reviews both pass for this card.

## Measurement boundary

The measurement target and comparison windows are specified prospectively. Actual treatment coverage, omissions/duplicates, lifecycle, realized R exposure and independent raw reconciliation do not exist yet and must be checked after any separately authorized start. This review does not establish treatment completeness, event chronology, a treatment effect, or witness status.

## Conclusion

The exact card is scientifically suitable to await separate authorization under the scoped Stage 6 exploratory contract. It is not execution-authorized. No SUMO, TraCI, or netconvert process was started; this reviewer made no file changes.
