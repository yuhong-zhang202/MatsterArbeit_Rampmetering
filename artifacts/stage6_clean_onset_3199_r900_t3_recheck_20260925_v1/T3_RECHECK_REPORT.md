# Candidate A T3 measurement recheck

Scope: already completed `CLEAN3199_A_R900_DELAYED_S17` raw; no new simulation, no post-R P/S/L, Candidate A/C or matched M outcome review.

## Observed evidence

- The auxiliary E1 `p1_merge_section_20_l0` is 20 m into `merge_section_0`. It reports zero entered vehicles in `[630,660)`.
- Native lane changes show `R_flow.11` and `R_flow.12` leaving `merge_section_0` for `merge_section_1` at t=631, pos=8.14 m and t=658, pos=4.56 m. FCD positions bound their first auxiliary entries to `(630,631]` and `(657,658]`. These entries occurred before the 20 m E1.
- The full R240 ledger has 240 bounded auxiliary entries and 240 bounded through entries, zero unknowns. In the three full bins after T2, certain auxiliary entries are 7, 2 and 13; per-vehicle T3 confirms at 690 s. Corresponding E1 counts are 8, 0 and 13, so the literal D-009 E1 condition fails.
- Raw manifest hashes verify 25/25 entries; reconstruction regression checks pass 9/9. Exact source/output hashes and extraction code are in `data/processed/stage6_clean_onset_3199_r900_t3_recheck_20260925_v1/PROVENANCE.json` and `VERIFICATION_RECEIPT.json`.
- The compiled network is bound independently in `artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/CLEAN3199_A_R900_DELAYED_S17_CARD_FINAL_REV3.json` and `PROVENANCE_RECEIPT_REV2.json`: `network.net.xml` SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. This is a cross-reference; the new derived `PROVENANCE.json` does not itself list the network hash.

## Scientific boundary

The previous inference “E1 zero means no actual R auxiliary entry” is false. T3 under the original per-vehicle rule is confirmed by 720 s, while T3 under literal D-009 E1 wording is not. The adopted rule conflict prevents this recheck alone from replacing the historical classification or opening the locked post-R outcome stage. `T3_METHOD_CLARIFICATION_PROPOSAL.md` gives a narrow, explicitly post-result option for separate independent review and user adoption. No witness or NO_WITNESS conclusion is made here.
