# Independent engineering post-run review — PAIR_3199_R720_DELAYED_S17

**Execution integrity: PASS. Required data-reconciliation issue: OPEN.**
Engineering review scope is the exact authorized start, resource bounds, runtime
and runner binding, provenance hashes, output inventory, and technical run log.
This review does not classify traffic or infer whether U/X vehicles were omitted.

## Bound authorization and execution

- Exact card: `PAIR_3199_R720_DELAYED_S17_CARD_FINAL_REV1.json`, SHA-256
  `08160a2ad225ee9fcc2abcc11d509a88ecf554252f1fb17e35dc69b9404351d4`.
- `docs/DECISIONS.md` D-006 records one authorized start, 120 s wall-clock,
  90,000,000 decimal-byte output trigger, 100 ms polling, accepted slight
  overshoot, and zero retry; the decision is marked consumed.
- Card values reconcile with treatment runtime sidecar SHA-256
  `0b80e870722573ee0ff61a05109c2fc2f7263b6cf7e0fbf1fb4f8b5a7bf5131e` and
  runner SHA-256 `cbfa8937fe22dd0998667cc4fc3df6f44cd61cf1e5cd32c4a5507aa5bb425104`.
  Read-only hashes of the installed SUMO binary, Python executable and local
  additional-file XSD match the sidecar values.
- All five scientific input hashes (demand, additional, accepted network,
  output roles, and sumocfg) match the exact card. The adopted witness-contract
  hash is `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
  The matched-control card, execution receipt, raw manifest and data-review
  hashes also match the treatment card's references.
- One treatment reservation exists and is `FINAL_STATUS_HANDED_OFF`; its
  approved-card, execution-receipt and output-manifest hashes match. It records
  `retry_allowed=false`, return code 0, `stop_reason=null`, and 19.92132 s.
  The capture independently records `start_count=1`, `max_starts=1`, and
  `retry_allowed=false`. The run log ends at simulation time 2700 s with the
  final simulation step reached. The 120 s and 90,000,000-byte triggers did
  not fire; payload was 21,066,503 bytes.
- The package reservation directory contains only the already-completed
  `PAIR_3199_CTRL_S17` control and this authorized treatment. This review found
  no additional reservation or output run for another demand, seed, or
  controller in the pair package. No retry, netconvert or TraCI execution is
  evidenced by the R02 capture or this run's direct SUMO log.

## Raw output integrity

The output manifest SHA-256 is
`92dbe5627f8afbfe26f50bc8d62207ca9a9ed579c6f707481079d8ad795228dd`; the
execution receipt SHA-256 is
`7d77da828ca962178432150bccf26ea7922d59428b31eda564ad4c3c64628d5a`. The
capture SHA-256 is
`00e061736a21c3031b476b2e9c0c1bcee2b669179e48bb375778c070d5f56374` and the
reservation SHA-256 is
`062d4bca70fce7f343d97bc679284516ea52ac33103f1a62615fee33783235fa`.

All 18/18 required output-role files exist and match their manifest SHA-256 and
byte counts. All 25 inventoried raw/support files match the manifest; there
are no missing or unlisted files. The output directory also contains only the
manifest and execution receipt beyond those 25 inventoried files. Raw files
were read and hashed only; none was edited.

## Required data-reconciliation issue

The treatment `sumo.log` (SHA-256
`4be0e443c50ca88ac78e924ac7f4ae2067bd2b7cd5e78b650ead89a2ad563e2a`) contains:

- `Warning: Route file should be sorted by departure time, ignoring 'U_flow'!`
- `Warning: Route file should be sorted by departure time, ignoring 'X_flow'!`
- `Inserted: 1525`

The input schedules M=1333, R=192, U=150 and X=75. The logged inserted count
equals M+R (1525), while the matched control's SUMO log reports 1558, equal to
M+U+X. This numerical correspondence and the two flow-sort warnings require
the independent lifecycle/data review to reconcile actual U/X identities,
departures and arrivals against the raw route/tripinfo/FCD records. They do
**not** by themselves establish that U/X were omitted. Keep the execution
integrity finding separate from that pending reconciliation and leave the
traffic/witness result unclassified here. No rerun is recommended or authorized.

## Disposition

R02 authorization binding, one-start consumption, no-retry behavior, resource
limits, runtime and provenance identity, normal horizon termination, and raw
manifest integrity pass. One required data-reconciliation issue remains open
for the assigned lifecycle/data review; do not treat this engineering report
as a traffic outcome or complete post-run gate. Review confidence is High for
the verified execution/provenance facts. No SUMO, TraCI or netconvert process
was launched during this review; only local files were read and hashed.
