# Independent scientific post-run review — MINIMAL3350 R720 REV7

**Disposition:** `NO_WITNESS`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Confidence:** High for locked classification and pair evaluability; Moderate for physical interpretation and generalization.

The pre-R M gate passed: 34,491 identical M vehicle-second tuples per arm over [0,540), with no missing keys or differences. All 1,396 M vehicles arrived in each arm, and all 192 R vehicles arrived in treatment. FCD covers all 2,700 frames.

R first departed at 540 s and first entered the through lane at 582 s. Unique R through-lane entries in the consecutive 30 s bins were 4, 5 and 6, confirming T3 meaningful exposure at 660 s. The first small M tuple divergence was at 584 s, after R entry but before T3 confirmation. It does not establish the positive ordering required for a witness.

Locked P/S qualifying events are absent in both arms; Candidate A is absent. Treatment has 65 Candidate C warning bins overall and 28 in core primary-window bins, versus 28 and 0 in control. Isolated P/S low bins and these warnings do not meet the locked sustained State1 criteria. Therefore the matched pair is an evaluable negative under the unchanged classifier: no witness was established. This does not imply ramp traffic has no effect under other conditions.

All vehicles arrived, downstream E1 passage exists, no mainline-red records were found, and `ramp_mid` remained green. The queue export has empty lane arrays, so queue morphology cannot be assessed. Upstream two-lane E1 reports 1,397 entries in both arms against 1,396 planned M, without ID attribution. The fixed M speedFactor vector came from a previous full-network run; it supports this exact matched pair but not an independent U=X=0 random draw or cross-seed inference.

No escalation outcome was inspected. This review does not authorize or prepare R900/R1080 or higher-qMain runs.
