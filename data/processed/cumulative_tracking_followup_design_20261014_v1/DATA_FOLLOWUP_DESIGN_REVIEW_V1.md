# Existing-state data review of the750 follow-up candidate

Disposition: **GO_FOR_BOUNDED_CANDIDATE_DESIGN_REVIEW_ONLY**. Existing evidence makes T9/Y3 + T10/Gmax5/Y3 worth evaluating as a proposed catalogue for750. No implementation or native execution is authorized by this report; sustained applicability and actual two-car service remain unproved.

## Context / inputs / method

Read mandatory AGENTS, current PROJECT_STATE, DECISIONS, empty unfrozen EXPERIMENT_PROTOCOL and relevant WORKLOG. Stage6 closure/qualification/scientific scope remain unchanged. Inputs are the frozen UA_CUMULATIVE750_S17_01 yellow_scope_attempts.jsonl, phase-request trace, prior independently audited ACTUAL_RESULTS_V1.json and phase/cycle/accounting results. The old fixed-T10 continuation report supplies its already-reviewed fifth-green-step fact. No full FCD or terminal audit was repeated. extract_yellow_snapshots_V1.py independently recomputed unchanged stop/clear formulas for every attempt row, checked unique IDs, exact covered populations, timestamps and original predicate agreement, then evaluated only Y3 on the same inputs. The extraction completed exit0; it is not a simulation/test suite or production implementation.

## Eight actual attempts and277 bound snapshots

| Attempt s | Cycle / actual green seconds | Bound rows | Original Y / result | Actual cycleN | Same-state Y3 |
|---|---|---|---|---|---|
|1204|T10 /4|41|3 /PASS|2|allPASS|
|1214|T10 /4|39|3 /PASS|2|allPASS|
|1224|T8 /4|37|2 /PASS|2|allPASS|
|1232|T10 /4|35|3 /PASS|2|allPASS|
|1242|T10 /4|33|3 /PASS|2|allPASS|
|1253|T10 /5|31|3 /PASS|2|allPASS|
|1262|T10 /4|30|3 /PASS|2|allPASS|
|1272|T8 /4|31|2 /UNKNOWN: R_flow.15|1, partial|allPASS|

The first seven attempts are quota-close setter records; at1253 this happens at the fifth-green-step deadline after quota2 is finally observed. The last attempt is MAX_GREEN_DEADLINE_PREPARATION, rejected before its first-Y movement. Previous source integrity/TLS/ACK/FCD coverage is reused from the actual audit; this extraction does not independently redo those layers. First seven populations satisfy stop-only; final population has30 stop-only and one neither underY2. Under same-stateY3 R15 becomes clear-only, while its stop screen stays false. R15 input distance0.1681315103m/speed4.9879585746m/s yields clear-time2.5566317183s: Y3 admits both the unchanged timing and travel-distance screens. Original Y2 UNKNOWN remains retained. No future Y3 population, native behavior, collision outcome or downstream following response was simulated. Monotonicity here applies only to these same finite inputs and unchanged stop/clear screen, not to altered trajectories.

At1248–1258, independently audited entries R_flow.10 ACK1249 and R_flow.11 ACK1253 show the second entry occurred in the fifth G second. Thus four observed G seconds did not suffice for two entries in this sample. The earlier fixed-T10 new03 report separately confirms R13 still0.51862986m short at ACK1264 and crossing during the fifth G step toACK1265. These are distinct versions/series, not a paired causal comparison or universal minimum-green rule. A T9/Gmax4 candidate must retain the possibility N<2; merely lengthening Y does not establish two green entries. Current stoppedT8 has N1 and unobserved y/r; those counts remain null in OBSERVED_CYCLES_V1.csv, not measured zero.

## Nominal arithmetic and scope limits

Assuming two actual cars per completed contiguous packet, T9 corresponds800veh/h and T10 corresponds720veh/h. Their mixtures cover only720–800, not300–900. At750, twoT9 plus threeT10 take48s and nominally release10cars. Example ordering10/9/10/9/10 gives completed-boundary C−E fractions1/12,−1/24,1/24,−1/12,0. This is an arithmetic illustration, not a tested scheduler output. Any repeated block returns nominal error to0 **only if actualN equals the assumed quota**. A missing actual car adds1 to C−N; no nominal schedule calculation repairs that physical deficit. Full300 requires nominal period24s;900 requires8s. Extra idle/variablequota or other periods would be separate designs, not demonstrated capabilities of this two-period catalogue. Original900/T8 and strict guard/NUM rules were not modified.

## Interpretation / handoff

Confirmed: an existing same-stateY3 screening solution to the final failed localY2 condition, and an observed fifth-green-step need for a second car in one currentT10 cycle. Inference: combining a longer-yellow fast packet with a G5-capableT10 is a defensible bounded design candidate for750. Unknown: future populations, sustained success, T9 green discharge, full-range scheduling, private SUMO branches, real ALINEA performance and safety qualification. Changing timing changes later states, so current allPASS snapshots cannot be called a counterfactual run success.

The original runSTOP/target1296 incomplete, final partial packet, all prior failures and raw paths remain unchanged. Scripts/CSV/JSON and input hashes are frozen below this new processed namespace. No source/guard/model/card/raw/doc was edited; no tests/SUMO/retry were run. Parent owns documentation-impact updates and scientific reconciliation. Engineering may propose a policy; user/scientific review must decide any implementation or new-run scope. This report does not resolve the overall original-ALINEA300–900 goal.
