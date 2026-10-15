# Fixed750 braking STOP — bounded technical recovery proposal

2026-10-13. **PROPOSED_CONDITIONAL_NUMERICAL_COMPATIBILITY_REPAIR; not implementation or native release.** The new direct user instruction permits a confirmed technical repair within the original resource envelope, but forbids arbitrarily increasing the braking limit, modifying substantive safety criteria/model/seed, or ignoring alarms. Current source/guard/card/raw remain unchanged.

## Assessment

The original measurement is correct: both speed difference and native acceleration are−4.501m/s². Independent750 data review confirms the FCD positions, finite values, identities and first-yellow interval; this is not a parser/rounding error. The original strict4.5/tolerance1e−6 contract genuinely failed and its result must remain historical.

There is now a concrete **source-consistent numerical mechanism**, beyond merely finding a warning tolerance. Pinned SUMO1.26 red/yellow planning limits its desired stop offset by the Euler braking distance, then the Krauss stopping-speed inverse subtracts a1mm numerical distance margin. Recomputing those expressions produces the observed after-speed with zero double-precision residual. Removing only that margin from the mathematical reference produces exactly−4.5. This supports a technical mismatch between an exact physical4.5 comparator and this native numerical stopping implementation **if** the monitored requirement is nominal normal braking with explicitly accounted numerical effects.

It does not prove that no stronger braking can occur, or that this exact private branch executed. Actual `majorStopOffset`, `stopDist`, `myVLinkWait`, selected safe-speed constraints and compiled-source identity were not traced. The conditional branch is compatible with the declared default model/options and this observed trajectory, but source-expression agreement is not unique causal identification or a full safety certificate.

## Reproducible source-expression match

`SOURCE_EXPRESSION_REPLAY_V1.json` SHA869183e078e231e7376f6b0ec2b86dc500e92f875249bcc9db2bddb03ce83e77 records the actual inputs, conditional assumptions, equations, outputs and hashes. One local Python calculation, no SUMO/build/test/model change:

| Item | Value / scope |
|---|---|
| Before speed / nominaldecel / dt / action headway |4.69222772465427m/s /4.5m/s² /1s /1s|
| Distance to lane end |0.5186298599310248m|
| Euler brakeGap with zero reaction headway |0.19222772465426985m|
| Necessary conditional offset saturation |majorStopOffset≥0.326402135276755m, with no overriding stop/device constraint|
| POSITION_EPS lower offset bound |0.1m, therefore does not bind in this branch|
| Native inverse distance g=brakeGap−NUMERICAL_EPS |0.19122772465426985m|
| Inverse result n=0, headway1s |speed0.19122772465426985m/s|
| Actual post speed |0.19122772465426985m/s — residual0|
| Predicted / observed acceleration |−4.501m/s² /−4.501m/s²|
| Same branch mathematical reference without1mm offset |speed0.19222772465426985, acceleration−4.5|

Official sources at commitfa7df22d7f1c4ae245192ecc32410a49f1ffb2a3, all matching previous pinned cache receipts:

1. [MSFrame506–507/537–538](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSFrame.cpp#L506-L507): yellow minimum-decel default3; default car-follow modelKrauss. Current card/config/type contains no overriding model or yellow-decel option. Defaults are implementation references, not new approved research parameters.
2. [MSVehicle2728–2776](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L2728-L2776): red/yellow stopDecel selection, braking distance, offset cap and stop distance. The unobserved major-stop-offset condition is explicitly retained above.
3. [Krauss101–107](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L101-L107) and [MSCFModel849–871](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L849-L871): stopping-speed inverse explicitly subtracts NUMERICAL_EPS from distance.
4. [MSCFModel189–197](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L189-L197): finalization can accept a lower safe-speed bound, rather than universally enforcing ordinarydecel as a mathematical physical maximum.

The separate native warning comparison [MSVehicle4916–4928](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L4916-L4928) does not supply proof of this generating branch or safety. Absence of warning is never an acceptance condition by itself.

## Smallest proposed correction for independent review

Do **not** raise the global limit to4.501 or enlarge1e−6. Keep raw delta-v/native alpha, the old strict criterion result and every alarm visible. A small isolated numerical-event classifier can be proposed in the current actuator seam, with nominaldecel4.5 unchanged, rather than replacing the executor:

- Default is the original STOP. Consider only an identity/time-bound R vehicle on the unchanged single storage lane at a verified controlled yellow stopping interval, with unchanged model/dynamics/options, complete before/after observations, no line crossing and upstream body/position coverage.
- Replay the declared Euler stop reference with the observed speed/geometry and **explicit source conditions**. Require independent agreement of actual delta-v and native alpha with its exact source-compatible result within the existing numerical comparison tolerance. Preserve the unresolved private-offset attribution in the record; do not invent it as an observed getter value.
- Record `SOURCE_COMPATIBLE_NUMERICAL_STOP_CANDIDATE`, raw−4.501, strict legacy failure and the source reference−4.5 as separate quantities. The correction is a classification of the1mm implementation term, not a rewrite of real acceleration to−4.5. Both metrics remain exportable for independent auditing.
- All larger or mismatched excess, wrong phase/lane/modes, missing/inconsistent values, entry/body uncertainty, collision/teleport/red-entry/native warning, current gap9+1.1 and other vehicle braking violations still STOP. Unknown source-condition binding must STOP, not become a numerical allowance.

**Critical boundary:** accepting such a classified event changes the literal predicate that stops on any observed physical magnitude above4.500001. It is a technical compatibility correction only if independent scientific review accepts the intended requirement as *nominal normal braking excluding this specifically documented native distance-discretization term*. If the intended requirement is an absolute physical4.5 ceiling, the proposed exception is a substantive standard change and is **not authorized** by the user's recovery instruction. Likewise, if the reviewer requires the private branch to be observed rather than a configuration-bound compatible reference, the present data do not suffice to enable it. In either case report the exact boundary instead of hiding it behind the word“numerical”.

This is the explicit issue for data/science to decide before implementation. No complete A1 proof, new algorithm or arbitrary tolerance tuning is proposed.

## Verification/retry envelope, conditional only

After that independent decision, a minimum regression should distinguish the preserved real−4.501 source-compatible case from larger/mismatched/unknown braking and wrong phase/coverage. It must validate raw value retention and untouched hard checks. The current failed750 raw,61-source version, old guard and reports remain immutable. Future source/card/analysis deltas must be versioned.

Only a new **UA_FIXED750_S17_02** identity at the same request750→720/T10/Gmax4/Y4/minred2/quota2, input/seed17 and end1270 is eligible after exact three-role release. No card or permission is prepared now. E14 is still a full-cycle request, not an expected guarantee of N14: the old seventh G had only one entrant. No green extension, yellow shortening, new seed, timing/offset change or quota manipulation is allowed to make it pass. Actual count, deficits and failure prefixes must remain explicit. Completion or continuation into the already approved dynamic/real-ALINEA tasks depends on the new full post reviews, not this proposal.

Known settled spend322.5027397919912 monitored s /325646309B leaves877.4972602080088s /874353691B. Existing single300s/300MB/start60s/free5GB rules remain. Necessary review-released recovery/retries use that envelope; no budget reset or extra point is proposed. Source inquiry now stops; parent should route this concrete conditional proposal through independent data then scientific review.
