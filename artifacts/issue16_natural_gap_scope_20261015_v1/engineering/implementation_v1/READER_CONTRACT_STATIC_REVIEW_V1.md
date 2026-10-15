# Approved contract reader: independent static engineering review V1

**GO_FOR_NONRUNNING_IMPLEMENTATION_REVIEW. No material compatibility blocker found in the approved runtime-to-reader contract seam.** This is not a traffic qualification, new-card release or SUMO execution authorization.

Context Preflight was refreshed against the updated STATE/WORKLOG and explicitly approved decision; the original full context and this implementation's boundaries remain in ENGINEERING_IMPLEMENTATION_REPORT_V1.md. Data owns the three changed native-reader modules and its tests. No reader/runtime/card/raw/governance file was edited during this review.

## Checked source and responsibilities

Read the complete new diff and relevant owning call chains in actual.py, provenance.py and streaming.py, plus test_current_gap_reader.py and final DATA_ADAPTATION_REPORT_V1.md. The actual audit calls provenance.verify before passing its validated current_gap_contract into streaming.scan. Absent card metadata retains old semantics; present metadata requires the exact approved contract, strict prospective new-G declaration, real user receipt path/hash and nonexecution boundary. Lower-level unit fixtures intentionally inject the pure helper contract and do not claim full-card/native provenance.

Independent following_observation first runs the unchanged legacy following validator. The native query status, numeric values, ID/time/speed/modes, legacy-margin and original floor denial are not changed to PASS. A complete approved passive role adds BELOW_NATIVE_REFERENCE_OBSERVED with its legacy alarm retained as a separately named observation. Leader body coordinates/route distance and post FCD position bind that observation. Old reference semantics remain when the card has no new contract. Missing/corrupt geometry/query/role/approval remains rejected or UNKNOWN.

Only that query-floor diagnostic is reclassified. Collision/teleport counters, braking, red new-front entry, phase/ACK/body/identity/log/setter abnormalities remain independent alarms or required-evidence failures in the unchanged stream checks. A preexisting hazard alarm is not removed by the new helper. Receiver classification retains the original false availability; at an executed new cycle G the independent check still requires available=true and READY. The source/card/release verification remains upstream, not replaced by an observation label.

Old exact-source and explicit postanalysis version separation remain. The latter allows only three owning readers to differ from the executed card. The newly changed runtime adapter/profile is not added to that exception. Thus the old173-source card cannot be claimed to match the current runtime, and the preserved oldV3 reader result was not rerun or relabelled under the new contract.

## Binding and evidence

DATA_ADAPTATION_REPORT_V1.md SHA256 f914fa73daa7988ce3cc08dfe1ced57c998cfc3fbf20218ab7a3e35408683c07 and DATA_ADAPTATION_BINDING_V1.json SHA256 e240b0699116d9b874d867afe313ac4a3c808ff0a5aeefca9562843de9683cde independently matched. All35 data-bound entries matched their recorded bytes/hash. The original26-item engineering binding remains its own implementation evidence; this new receipt does not rewrite it.

The final data report correctly distinguishes its first3groups PASS0.072s, strengthened original-query comparison3groups PASS0.068s, then only affected saved-loop1method PASS0.067s. It does not claim a final-source full-suite rerun. The649/650 original query comparisons retain every old field excluding only the two additive keys. Synthetic saved collision/braking/badACK retain the original failure reason and accounting/ACK boundary.

The fixture does not contain REQUESTED/feedback/command_records event streams. Its C/E/N integration and pending/selected/applied snapshot checks are useful local evidence, not complete lifecycle/request-origin/E1 verification. The report explicitly limits those domains to NOT_TESTED and preserves partial/held periods. No fake events or extra framework were added to fill that absence.

## Commands and limits

Only source/document reads and a Python stdlib JSON/hash/byte check of the final35-item binding were performed. No tests, audit entry point, simulation/native/version command, raw analysis or environment change was run by this reviewer. Reader test timings are inspected data-agent evidence, not independent rerun results.

Full4200/sixwindows, native ordinary movement under the new contract, real receiver hold/recovery, physical service and future safety remain NOT_TESTED/NOT_QUALIFIED. ALINEA tracking numerical accuracy is not assigned an invented tolerance. New-card preparation still needs the already identified exact run02/resource identity update and corresponding reader guardian equality update; current900/870 equality was deliberately not silently changed here. Root will obtain one scientific final review before that separate preparation stage; no canonical or native permission is created by this GO.

Documentation impact: root owns current-state/WORKLOG/Issue delivery updates. This review writes only this new engineering receipt and its independent binding.
