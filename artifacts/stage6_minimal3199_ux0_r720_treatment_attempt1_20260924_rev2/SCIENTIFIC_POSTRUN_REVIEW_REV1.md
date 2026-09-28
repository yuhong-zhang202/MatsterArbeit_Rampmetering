# Independent Scientific Post-run Review — MINIMAL3199 R720 Treatment

- **Disposition:** `NO_WITNESS` for this matched pair only
- **Confidence:** High for locked-rule classification; Moderate for physical interpretation of the L-only difference
- **Findings:** Blocker / Major / required Minor = 0 / 0 / 0
- **Scope:** Stage 6 exploratory U=X=0 existence test; qMain=3199.2, seed17, R=0 control versus delayed R=720 treatment. This is not a formal experiment or a conclusion about other qMain values.

## Execution and integrity

One Guardian and one SUMO start; SUMO exited 0 at 2700 s after 3.165857 s and produced 21,151,489 payload bytes. Neither the 90 s nor 75,000,000-byte stop trigger fired. No retry occurred. Engineering post-run review passed with 0/0/0 findings. The 18 required output roles and seven support files were hash/size verified.

## Matched control and exposure

Pre-R Gate A passed: 480 pre-540 M departures matched and 32,513 M vehicle-second tuples per arm matched exactly over `[0,540)`. Lifecycle reconciliation found M 1,333/1,333 and R 192/192 arrived, no unfinished vehicles, and explicit U=X=0. R first appeared at activation/departure 540 s, reached the approach at 541 s, auxiliary merge section at 582 s and through lane at 583 s. T3 meaningful exposure was confirmed at 660 s from three positive auxiliary E1 bins (4/3/6 entries), before the 720 s cap.

## Locked classification and matched comparison

Locked P and S numerical positives were both zero; Candidate A was zero. One L-profile numerical candidate remains at merge-core cell 13 over `[720,780)`. The control has a low-speed warning in `[720,750)` and then recovers; treatment is lower in both physical lanes in `[750,780)` (treatment-minus-control speed-ratio differences: lane0 −0.0864, lane1 −0.1017). Candidate C warnings remain preserved.

This L-only pattern does not meet the approved witness criterion (P-primary or coherent qualifying S). Retain it as sensitivity evidence; do not erase it or promote it to a witness.

## Alternatives, limits, and stop

Ramp-storage E2 reports a maximum of eight vehicles and zero reported jam length. The queue-export has no lane-occupancy sequence, so it cannot establish queue absence. Complete FCD/E1/E2 timing, downstream detector coverage, and lifecycle reconciliation support an evaluable locked classification, but they do not remove all uncertainty about queue mechanisms or the physical source of the L-only difference. This limitation narrows physical interpretation; it does not convert the unchanged P/S classification into `NOT_EVALUABLE`.

**Final classification: `NO_WITNESS`.** It means this pair did not satisfy the locked witness rule; it does not mean no disturbance or no R effect occurred. Stop here. Do not run another qMain, seed23, or B/C.

## Hash-bound evidence

See `SCIENTIFIC_POSTRUN_REVIEW_REV1.json` for the full SHA-256 binding of the plan, contract, control/treatment cards, engineering review, data/lifecycle report, processing manifest, gate, classifier, matched table, execution receipt, and output manifest.
