# SMOKE03 CLI warning — source and coverage clarification

**One Python/TraCI API warning was captured in CLI stderr. Native SUMO stderr remains0B; these are different streams.** No warning was suppressed, data changed, code/card adjusted or newSUMO/test/fetch run.

InstalledTraCI1.26 `connection.py:368–370`, alreadyhash-bound in the approvedcardenvironment, warns when `type(step) is int and step >=1000`. It continues the same `CMD_SIMSTEP` call with format`D`; `_pack:163–164` encodes `float(step)` as an8-byte rawdouble. PinnedofficialSUMOserver`TraCIServer.cpp:1168–1175` reads thatdouble and maps positive targetseconds throughTIME2STEPS. The displayed`frame_cache.py:61` location followswarningstacklevel2 at directdelegation; it isnot the emitter of a native SUMO warning.

Approvedbridge passesinteger`t+1`, then independently verifiesactualsimulationtimeequalsrequestedtarget. All1157 verifiedACKtargets1..1157 matchactualfloatseconds1.0..1157.0. Thus thisprefix hasno observedwrong-unit/step-time error; warning alone doesnotshow timeconversionfailure or safetyanomaly. This is a source-specificcompatibilitynotice interpretation, not a blanketclaimthat allPythonwarningsare harmless or futurebehaviorcertified. Exactwarningtimestamp isnotrecorded; sourcepredicate only supports the inference that integer1000 is thefirsteligible request.

OnlineLogCapture covers fourownednativeSUMOfiles (`sumo_stderr.log`, `sumo_stdout.log`, `sumo_error.log`, `sumo.log`). ParentPythonCLIstderr is a separate completion-captured/hash-bound file and wasnot included in perstepnativeclassifier/STOPcoverage. FinalBOUND_NO_OBSERVED_NATIVE_MESSAGE thereforemeans nativefourstreamsilence/eventclassification only, not anentirewarning-freeCLI or universalruntimecoverage. The observedCLIAPIwarning mustbe disclosed separately; no safety/qualificationconclusion follows.

[Exactwarning/source/ACK/coverage receipt](CLI_WARNING_SOURCE_AND_COVERAGE_RECEIPT.json). OriginalCLIstderr remains byte-for-byte preserved under existingengineeringbinding.
