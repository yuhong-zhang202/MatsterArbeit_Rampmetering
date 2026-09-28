# RI3350 Control — Final Conditional Prelaunch Review, Revision 2

Date: 2026-09-23  
Run: `RI3350_CTRL_S17_attempt1`  
Disposition: **ALL REQUIRED PRELAUNCH REVIEWS PASS — CONDITIONAL AUTHORIZATION GATES SATISFIED**

This record supersedes the current-status conclusion in
`FINAL_PRELAUNCH_GATE_REPORT.md`; that earlier report is preserved as a
historical snapshot. It is limited to one R=0 control run. It does not change
the scientific design, controller, demand, geometry, classifier, formal
protocol, or authorize any other run.

## Independent dispositions

| Review | Disposition | Blocker / Major / required Minor | Bound evidence |
|---|---|---:|---|
| Engineering | `PASS` | 0 / 0 / 0 | R02 Guardian review: runner `f8c3129e193fad38feddb8b4853638303faf1ee2f92706753db611fb50909a54`, tests `94d29353cc59ee90467a9eb88e5feeb5595037d26e6a4ae4ace7c28165184265`; suite 23/23 |
| Data | `PASS_STATIC_PRODUCTION_MAPPING` | 0 / 0 / 0 | R04 source mapper `a5becfcf327dc2b9bc02ca6336526cd3a98509ffc2c7c2356a65d4088ce6bf6a`, adapter `b2cdc1a14ba2cf1152539ff7e4469ffb6f7e157e770e4dade0a1ef95af6ecf2a`; suite 40/40 |
| Scientific | `PASS_SCIENTIFIC_PRELAUNCH` | 0 / 0 / 0 | R04 mapping scientific review plus overall conditional prelaunch review; exact locked source/method/design hashes below |

R02’s previously identified required minor—directory fsync after atomic
reservation replacement and before `DISARMED`—was corrected. The independent
engineering reviewer verified file fsync → atomic replace → containing
directory fsync; the initial one-use reservation directory is also fsynced
before Guardian startup. Abrupt launcher exit is tested with a fake Python
child. No SUMO/netconvert/TraCI call was made by these tests.

R04 validates the complete `22 cells × 3 profiles × 90 bins` source grid,
derives all maximal low-state runs from the locked analyzer’s unchanged
`low_state_bin` values, cross-checks event identities/bounds and attribution
coverage, and hashes method/analyzer/design/roles/raw-manifest sources. A
verified zero-event receipt requires complete sources and a complete all-false
grid; missing or invalid input is UNKNOWN/FAIL, never a zero-event finding.
Numerical/reference gates are copied from locked event output; the population
sub-gate calls the original hash-bound helper. The classifier was not changed.
Actual control raw application is explicitly deferred until raw exists.

## Accepted one-run contract

- At most one SUMO start; technical retries: zero.
- Wall-clock monitored stop trigger: 180 seconds.
- Output-tree monitored stop trigger: 300,000,000 bytes (decimal bytes).
- Poll interval: 100 ms. Output overshoot between polls is accepted. This is a
  monitored stop trigger, not a hard disk quota.
- On trigger: SIGTERM to the simulator process group; wait 5 seconds; then
  SIGKILL if still alive.
- These values apply only to this run.
- Guardian cleans up if the launcher exits while Guardian remains operational.
  Guardian/host crash, shutdown, or power loss is not covered. No claim of a
  hard quota or complete OS-failure immunity is made.

## Scientific scope and deferred checks

R01 is bounded static input/hash validation; it is not runtime/XSD validation.
R03 observed pairing is deferred until a paired transition raw exists. R05
real-raw application and R06 actual ramp exposure are deferred; the control has
scheduled R=0, so no R exposure will be inferred. G6 remains `UNKNOWN`, not
`PASS`; it is not a suitability finding and does not release any next run.
R05/R06 fixture readiness is not promoted to real-data validation. No baseline
candidate, mechanism conclusion, or O2 resolution follows from this prelaunch
record.

## Locked scientific inputs

- Method SHA-256: `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`
- Design SHA-256: `62fb63eb49ae98b58bc45ad6bc7d60cd21fcdb73b3327c34b97c5151b01ca355`
- Classifier/analyzer SHA-256: `78f001b7909bdda6797eae6aab5bf6bf0dd70bce83262d8f2619c3fa71149c55`
- Accepted network SHA-256: `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`
- Formal experiment protocol: empty and unchanged.

Control configuration and demand are bound by the original input manifest; the
final card carries their exact file hashes. The original DRAFT card remains
untouched and is not an execution input.

## Authorization sequence and stop

The user's current conditional authorization is satisfied by the three
independent `0/0/0` reviews above. Therefore create a new immutable exact card
for this run only, bind the reviewed runner/Guardian and R04 application hashes,
all science/environment/input/output-role hashes, 180 s/300,000,000-byte
resource triggers, and one-start/retry-zero flags. Compute its exact SHA-256,
run the runner's read-only preflight, and only if that exact hash preflights
successfully, execute one `launch` with the same hash. Every simulator start
attempt consumes the unique reservation. After the run, finish engineering,
data and scientific post-run review, update the outcome records, and STOP.

No transition, seed23, B/C, retry, extra demand point, or any other
SUMO/netconvert/TraCI run is authorized. The formal protocol remains unchanged
and unfrozen; Stage 6 remains PARTIAL; O2 remains NOT_RESOLVED.
