# Independent scientific prelaunch review — E1 R900 REV17

**Disposition:** PASS  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Confidence:** High for design alignment; Moderate for interpreting exposure differences across R rates.

Reviewed exact card: `MINIMAL3350_E1_R900_DELAYED_S17_CARD_FINAL_REV1.json`, SHA-256 `f0387580053ad6b862ec2874a4eb55e5c9a468a3f23db561af40d6c9e6499908`.

The current user instruction conditionally authorizes exactly one E1 start after all three exact-card prelaunch reviews pass. It supersedes the earlier plan-only `NO_RUN_AUTHORIZATION` for this single E1 run. The 3350.4 control and matched R720 `NO_WITNESS` meet the adopted E1 entry gate. The candidate preserves the exploratory scope: seed 17, U=X=0, A_OPEN, delayed R900 over `[540,1500)`, 240 planned R vehicles, and 1,396 M vehicles matched to control. Engineering and data/provenance reviews pass. The run-specific resource contract is 120 seconds / 100,000,000 bytes / 100 ms polling; the output directory is unique and absent.

**Observation:** The R900 vector's first 192 identities have 0/192 speedFactor matches to the R720 vector. This does not invalidate R900 versus R0, but it limits attributing any later R900-versus-R720 exposure increase solely to nominal qRamp. Preserve this caveat in interpretation.

This review does not authorize E2 or any other run. No process was started and no file was written by the reviewer.
