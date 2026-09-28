# Final prelaunch review — `MINIMAL3199_CTRL_S17_TECH_RETRY1`

**Overall disposition:** `MINIMAL3199_CTRL_TECHNICAL_RETRY_PRELAUNCH_READY_AWAITING_AUTHORIZATION`  
**Execution status:** `DRAFT_NOT_AUTHORIZED`; a separate user authorization is required.  
**SUMO / Guardian / TraCI / netconvert starts for this repair:** 0 / 0 / 0 / 0.

## Exact objects reviewed

| Object | SHA-256 |
|---|---|
| Draft exact card | `5f9c8f17476296cab5b30c59b9dd60bda1f4b066b956a897bbd53be43a50be22` |
| Input manifest | `6944ba949a0e9aa40c11cfc22e430248a61e748aa789685a8b14812fc3ab313e` |
| R02 runner | `74a9d51716006e5283e7e04cef0f0a82df17f26695b7fb444c8ffd29d41e664a` |
| Runtime binding | `3bb37acdcea05687cc779a361dfd5c7f824421a30469ae9ec0858884c49300b4` |
| Engineering review | `9d3794b8940b6c5e23fd0f0467d32e432c44fdb96817eb44ea89cfaaa04e976e` |
| Corrected provenance receipt | `2c27f1c8b9c97ea13e0ef925515e04700589c0c718f1527ae1f3bbae2cbabe11` |

## Review dispositions

- **Engineering — `PASS_STATIC_BINDING`.** The missing `additional_schema` resolver binding and Guardian START map assertion are repaired fail-closed. Staging is deterministic and shared by preflight/launch, with counted source→target substitutions and expected staged byte/hash bindings for both config and additional XML. Regression suite: 9/9 PASS. Fresh output and consumption paths are absent.
- **Data/provenance — `PASS`, Blocker/Major/required Minor 0/0/0, High confidence.** Card, manifest, runner, runtime, source and staged bindings are consistent. Receipt `offline_tests`, count and test result all say 9/9. The previously failed attempt and its raw inventory remain intact; the new attempt has no raw output or consumption record.
- **Scientific — `PASS_BOUNDED_CONTROL_INPUT_ALIGNMENT`, Blocker/Major/required Minor 0/0/0, High confidence.** The draft retains qMain=3199.2, seed17, R/U/X=0 and the previously reviewed M/geometry/vehicle/classifier/measurement bindings. The stage-path transformations change destinations and staged-file references only. This review establishes no traffic result, control suitability, treatment authorization, or formal-protocol change.

## Provenance and limitations

The earlier source/staged sumocfg hash difference was caused by necessary staging path substitutions, not by a documented scientific-input change. The new deterministic rule replaces exactly 8 old output paths in the sumocfg, then exactly 1 prepared additional-file path; it replaces exactly 12 old output paths in the additional XML. Any unexpected count or residual old path fails closed. Source/staged sumocfg hashes are `a6be97aba1ab00d6f17ae15788d45765d0a0efca7e297cc1423e4fb720853b1c` → `1906f98e1e108a9019919d29fa4c9c6086659fdbedd231d16531ec275505650c` (2,656 → 2,802 bytes). Source/staged additional-file hashes are `6bd3555c983db506800cab40524767229a3a03c94e893e0ccdc506f95690d8ef` → `6b93195465eb66462394905fcf6bd450c8e3b863517bef436f5177f0a54c9470` (3,796 → 3,940 bytes).

Expected staged bytes are specification-bound; they were not materialized in a run directory because no launch occurred. The card remains a draft, its proposed resource values are not authorization, and the consumed earlier `MINIMAL3199_CTRL_S17` authorization cannot be reused. No scientific inputs, geometry, classifier, thresholds, vehicle behavior, or formal protocol were modified.
