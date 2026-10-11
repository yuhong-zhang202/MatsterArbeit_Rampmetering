# Single native smoke — independent data review

**Data integrity PASS; intended motion smoke NOT_REACHED.** This is an aborted technical smoke at native time0.00, with no completed/accounted motion interval. It gives no native-red safety or rate-qualification result.

## Actual checks and findings

One readonly checker invocation with `--local-raw` returned0/PASS. See INDEPENDENT_REVIEW_RECEIPT.json for exact command and source/result hashes; INDEPENDENT_FAILURE_RESULT.json contains independently parsed values. All8 engineering-bound files,26 frozen V5 files,536 protected files,7 R2 files, exact card/human authorization/release/review references match. All53 raw files total1,804,472bytes; an independent final readback matches every manifest hash. No raw/source/card was changed and no SUMO/TraCI/native-version call or old test rerun occurred.

248 sequential client connection attempts include247 failures and1 successful connection. They concern the sole native child; they are not248 launches. Native-start count1 is supported by the engineering execution receipt and the reviewed startup implementation; process PID was not persisted and remains unknown. CLIexit1/nativeexit0 distinguish the failed bridge outcome from normal child termination.

The single pre-step record is at time0, explicitly step_advance_performed=false; no ACK/post-step file exists. Completed time, accounted time and last ACK remain null. Four loaded IDs are observed before motion; they are not inserted traffic. Native log reports started0.00/ended0.00 and inserted0(loaded4). Native-log inserted0 is a startup counter, not service measuredzero.

Three capture stages and all four logstreams were independently checked against actual byte ranges, fragment bytes/hash, prefix hash and final EOF lengths. Startup ACK stderr is0B; pre-motion stderr is1443B/17 self-loop warnings for CA_C8–CA_C24. EOF adds1443B errorlog and2421B native log; stdout is0B. This supports the recorded capture timing, not an exact warning emission timestamp or unique cause. Configuration-initialization origin is an engineering inference. Warning presence alone is not collision/emergency/red-crossing evidence. Normal child EOF does not prove universal native log coverage.

FCD and15 other parseable XML outputs contain no child observations. `tripinfo.xml` is parseable but contains **three undeparted termination records**: M_flow.0/U_flow.0/X_flow.0, depart=-1,arrival=-1,vaporized=end. Their serialized duration/waiting/loss zeros are not empirical traffic costs; those outcome metrics remain null. `tls_states.xml` is0B and cannot be parsed as XML: missing signal evidence, not a complete traffic log. Originals and the negative output state are preserved.

Failure accounting C/appliedC/E/N and differences are initialized zeros. Derived service observations preserve every field as **null**, with the original initial values separately disclosed. No service window was observed; completecycles0 is a reached-cycle count rather than qualified rate. Initialization603, control activation1200 and firstred1206–1207 are NOT_REACHED. Red crossings, collision, emergency braking and traffic costs are NOT_OBSERVED/null, not zero.

## Scope and preservation

Default checker does not read raw, but still requires the local canonical authorization/release paths. Those execution paths are deliberately not published; the remote consumed-authorization snapshots support manual hash review, not a claim that this checker was run or will fully pass in a clean public checkout. Only explicit `--local-raw` reconstructs the actual logprefix/XML facts against53 ignored private files; publicly committed parsed summaries do not make fullraw remotely accessible. This review has no external clean-checkout gate. Raw manifest and original failure/warning/prelaunch disk-block/cleanup/authorization-write history remain untouched. No repair, warning suppression, retry or continuation is authorized by this report.

No required data correction remains: engineering already separates initial zero/null/unreached. Scientific reviewer must assess interpretation. Stage6 closure, A1 unresolved, Candidate A NOT_QUALIFIED, prior STOP3 and900 NOT_TESTED remain unchanged. User/Chat decides any later narrow technical handling and a separately authorized new run.
