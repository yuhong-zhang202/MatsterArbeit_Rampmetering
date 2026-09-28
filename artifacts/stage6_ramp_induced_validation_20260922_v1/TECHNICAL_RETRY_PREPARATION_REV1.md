# RI3350 Technical Retry — Offline Preparation Record, Revision 1

Date: 2026-09-23  
Status: **offline repair and bounded engineering/data review complete; no retry card generated; no retry authorized or launched**

## 1. Consumed attempt disposition

`RI3350_CTRL_S17_attempt1` is preserved as a consumed technical failure. SUMO
started (PID 20984) and exited with return code 1 after 22.979167 s wall-clock,
while loading `scenario_control.add.xml`; the logs report no traffic-step
progression. This is not a claim that SUMO never started. The output manifest
records 6 of 18 required role files present and 12 missing; present traffic XML
outputs are empty shells. Therefore this attempt is **NOT EVALUABLE** for
traffic state, classifier events, demand adequacy, controller performance,
baseline suitability, or urban/network effects. Missing outputs are not
verified zero events. No post-hoc scientific inference is made.

Immutable evidence retained:

- Exact card: `control_card_FINAL_RI3350_CTRL_S17_attempt1_REV1.json`,
  SHA-256 `c306646c4b73ec86b243a7936e2bf5f838d4c764c37756d763e9c4c2365c97e3`.
- Execution receipt SHA-256:
  `12d0c48771208b815403bbd7b331e9bb22407f7476a0d55222a373962cbc2156`.
- Output manifest SHA-256:
  `b9bbad589e7cdaf68344e4a8dc5d44a3db4689dcaaf8a0b67cbb8007aecf4451`.
- Consumed reservation SHA-256:
  `309759c8fa498cedac00ff2bc865b86432658e26552c4830912790960ead37d9`.

Independent scientific post-run interpretation: `PASS_FAILURE_INTERPRETATION`,
High confidence. It confirms initialization failure and forbids traffic-state
inference from the empty/incomplete files. The review noted that current-state
documentation was stale; this revision updates it. The source receipt and old
card/output are not rewritten.

## 2. Root cause and bounded confidence

The preserved SUMO log says local schema lookup failed at
`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/data/xsd/additional_file.xsd`,
then SUMO attempted the schema URL host and DNS resolution failed. The old
execution receipt does not record the child process environment, so the exact
historical `SUMO_HOME` value cannot be asserted. At this inspection the
inherited environment points to the framework root, consistent with the
logged search path.

The installed SUMO 1.26.0 distribution root is
`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo`.
In this installation the literal `$SUMO_HOME/xsd/additional_file.xsd` is
absent; the schema is at `$SUMO_HOME/data/xsd/additional_file.xsd`, SHA-256
`c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e`.
Thus the direct cause established by the logs is a failed local lookup at the
wrong path followed by unavailable network fallback. The stale inherited
`SUMO_HOME` is the best-supported explanation for that path, but its exact
value at attempt1 is unrecorded.

The source `scenario_control.add.xml` retains its original standard online
`xsi:noNamespaceSchemaLocation`; it was not edited to bypass validation. The
failed materialized XML validates against the installed local XSD using
`xmllint --nonet --noout --schema`. This establishes local XML/schema
conformance only, not successful SUMO runtime behavior.

## 3. Offline-only repairs

### R02 runtime/schema binding

The one-use runner now validates the canonical `SUMO_HOME`, exact local schema
path, schema presence, and expected plus card-supplied schema SHA. It passes an
explicit corrected environment from launcher to Guardian and from Guardian to
simulator child. The Guardian rechecks the binding before child spawn; missing
or mismatched schema fails closed before spawning. A distinct retry ID and
output/reservation target are configured in the runner, but no retry card or
reservation has been created.

R02 tests: **31/31 PASS**, using mocks, temporary fixtures, and fake Python
children only. `py_compile` passed. No SUMO, netconvert, or TraCI command was
invoked. Independent engineering review: **PASS**, Blocker/Major/required
Minor `0/0/0`.

### R04 manifest compatibility and output binding

The production adapter now validates the runner's `artifact_roles` plus
`support_files` manifest (including all 18 required roles, path containment,
role metadata, sizes, SHA-256, XML roots and time-grid coverage) and rejects
the obsolete `files` schema at the raw boundary. Only after source manifest and
every required output are validated does it make a deterministic temporary
legacy-manifest projection for the unchanged hash-locked analyzer. Projection
paths point to the exact validated raw files; neither raw files nor the
classifier are copied or modified. Both original-manifest and projection
hashes are recorded. Missing/incomplete sources fail closed; only complete
source traversal may support a verified-zero event result.

The adapter is bound to the distinct path/ID
`RI3350_CTRL_S17_technical_retry1`; a fixture rejects the consumed attempt1
directory. R04 tests: **27/27 PASS**. Independent data prelaunch review:
**PASS_PRELAUNCH_DATA**, Blocker/Major/required Minor `0/0/0`. This is a
static/fixture review, not real-raw application; no attempt1 raw was applied.

## 4. Scientific-input invariance

The offline changes affect runtime environment binding and data-manifest
compatibility only. Hashes remain identical to the consumed exact card:

| Bound input | SHA-256 |
|---|---|
| Control SUMO config | `87ba0d7d671f1f72f45d7fda3c3e857a1622263a9c2ce4d3f1ef625745f7ab7c` |
| Demand (`qMain=3350.4`, `R=0`, `U=150`, `X=75`, seed 17) | `0edeb776e6656f3fd22f1e8d0b4c07ece17903695c901af576d93fb205b26865` |
| Additional/detector/TLS input | `6355c6a6deaf0b7aadbdca59a8349c4e0e96e47b9ff5f89b8498b9ad02adcd59` |
| Accepted network | `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` |
| Design | `62fb63eb49ae98b58bc45ad6bc7d60cd21fcdb73b3327c34b97c5151b01ca355` |
| Locked method | `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7` |
| Locked classifier/analyzer | `78f001b7909bdda6797eae6aab5bf6bf0dd70bce83262d8f2619c3fa71149c55` |
| Output-role contract | `e33b7439cc15b7b68048fa2bf63f659769b93e4718650c11eeda46959404b2b3` |

The original materialized attempt1 config/additional XML normalize back to
their input templates byte-for-byte after reversing only output-path
substitution. No demand, seed, geometry, TLS, vehicle behavior, timing,
classifier, or protocol change was made.

Current implementation hashes:

- R02 runner: `abba1b31970a4690a262881cec1ea0957b2386c65a20c4105a711cebf3c80154`
- R02 tests: `c3f86778f353a604070f9949959de65e4cb2281c64036d3ff6924e45ad0eb857`
- R04 adapter: `8ea2d77c33001b32c9068a94c5f64fa3448add4262396f27c8cdb4e656581542`
- R04 tests: `cf0c60de7e517d894c6802859eb7de1945c6a71d6d544dc85e380846239bc851`

## 5. Card and authorization boundary

No technical-retry exact card or retry reservation is created in this
revision. R02 engineering and R04 data reviews passed, but the independent
scientific prelaunch review could not be obtained in this task; therefore the
user's condition for generating a card is not met. This report is not an exact
launch card and cannot be used to run the retry.

The attempt1 approval of 180 s and 300,000,000-byte polling stop triggers was
expressly scoped to attempt1 and is not carried forward. A new retry requires
a separate resource contract and explicit approval of its exact card SHA.
There is no new start authorization. No SUMO/netconvert/TraCI, retry,
transition, seed23, B/C, or other run may be launched under this report.

`docs/EXPERIMENT_PROTOCOL.md` remains unchanged and unfrozen; Stage 6 remains
PARTIAL and O2 remains NOT_RESOLVED.

## Addendum — retry-only resources authorized; scientific gate pending

Later on 2026-09-23, the user approved for this technical retry only a 180 s
wall-clock monitored stop trigger and a 300,000,000-byte output polling stop
trigger, with polling overshoot accepted. This does not extend to transition,
seed23, B, or C runs. An independent retry scientific prelaunch review remains
unobtained: the reviewer invocation returned an agent-thread-limit error. The
previous scientific review only classified attempt1's failure and cannot
substitute. Consequently no exact retry card/hash, reservation, or new start
has been created. The user's conditional authorization to make one start with
technical retries zero is not exercisable until independent scientific review
also passes with all issue counts zero and exact input identity is reconfirmed.
