# Scientific prelaunch STOP V1 — first application signal binding

2026-10-13. Scope: UA_FIXED300_S17_01/card SHA2c2330d4c977fb26c8ef52a36a16d56a7a6c94cb5334e8d5557f19eb967bed09, common runtime900dcebb4f4568e6de93730977284c04f1573d02d19e6ac97ef38d79dc5702b9, source in fd17250 and unchanged in1b6bd30. This is the parent record of the successfully run read-only scientific review message, not a reviewer-authored file.

Verdict: do not release this card. No SUMO, native reservation or canonical permission exists.

Concrete finding: adapter.py invokes ledger.end_step with expected pending motion before the post signal phase/state/program/controlled-link checks. The ledger may emit ACK_OBSERVED and first_application_s for the first green before those real signal checks run. If post phase or program is wrong while nextSwitch is equal, the run will STOP but its application journal may still incorrectly claim a real green application. This undermines closed-loop technical qualification evidence; it does not prove native SUMO unsafe.

Smallest correction requested: perform the same actual signal identity checks before registering an observed application, keeping all physical guards unchanged. Add one combined regression for unchanged nextSwitch with wrong post signal or program: STOP, first_application_s remains null, no ACK_OBSERVED. Preserve V1 source/card/reports and issue a new bound V2 source/card; no SUMO, timing/guard/model/research change or A1 extension.

The reviewer found no other substantive first-card conflict at this point; final GO remains unissued. Engineering repair, independent data re-review and scientific exact-card re-review are mandatory. Historical STOP3/A1_UNRESOLVED/CandidateA_NOT_QUALIFIED and old raw remain unchanged.

## Final read-only review conclusion

Reviewer final verdict: STOP V1; exactly one Major, no other new substantive conflict in necessary first-card checks. Measurement target passed; actual native coverage not verified; omitted/misbound application evidence has the Major above; independent reconciliation is offline-only, actual result not verified; existing five engineering/four data methods have PASS evidence, new negative was required. No reviewer tests or SUMO were run.
