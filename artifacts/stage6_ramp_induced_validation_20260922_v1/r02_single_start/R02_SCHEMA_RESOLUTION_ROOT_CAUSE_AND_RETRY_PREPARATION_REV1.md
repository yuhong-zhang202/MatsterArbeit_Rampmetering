# R02 schema-resolution root cause and technical-retry preparation

Status: **offline engineering repair prepared; retry card absent; no retry authorized or run**

## Finding

The consumed `RI3350_CTRL_S17_attempt1` failed during SUMO initialization while
resolving the `additional_file.xsd` schema. Its SUMO log records an attempted
read at:

`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/data/xsd/additional_file.xsd`

That path does not exist in the installed SUMO framework. The log then reports
that the online schema host could not be resolved. The old execution receipt
does not capture the child process environment, so the exact historical
`SUMO_HOME` value is **not recorded**. At the current inspection, the inherited
value is the framework root, consistent with the path in the log, but this is
not proof of the historical environment value.

The preserved `sumo.log` SHA-256 is
`eb410058ce366eb6f51e8b7d06125f74ad3deef2edd9b0f40069ffde08e33f7c`; the
preserved `sumo_error.log` SHA-256 is
`582e0125f6727489f13d68a6fa05a0c9f0f1c7d179230f6bf719f07c62fb6a4c`.
The failed materialized additional XML itself remains unchanged at SHA-256
`974456839f649babd5923a4931a1f5c1b3c5bfc277bd9a8ae6a4c927063ae753`.

For this installation, the correct SUMO distribution root is
`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo`.
The installed schema is at
`$SUMO_HOME/data/xsd/additional_file.xsd`, not `$SUMO_HOME/xsd/additional_file.xsd`.
The literal `$SUMO_HOME/xsd/additional_file.xsd` path is absent; the `data/xsd`
path is present. Schema SHA-256:

`c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e`

## Minimal runtime-only repair

R02 now binds the canonical SUMO_HOME, absolute schema path, and schema SHA in
the runtime card. The launcher explicitly replaces inherited `SUMO_HOME` in
the Guardian environment; Guardian validates the same schema binding before
spawn and explicitly overrides inherited `SUMO_HOME` in the simulator child.
Missing path, unexpected canonical directory, or hash mismatch fails closed
without starting a child. No scientific XML/config input was edited.

The failed materialized `scenario_control.add.xml` was checked offline using
the local schema and `xmllint --nonet --noout --schema`; it validates. This
confirms XML/schema conformance, not successful SUMO execution.

In-memory normalization checks show that the failed materialized additional
XML and SUMO config reduce byte-for-byte to their existing source files when
the output directory substitutions are reversed. Bound input SHA-256 values
remain:

| Input | SHA-256 |
|---|---|
| `control_input/scenario_control.add.xml` | `6355c6a6deaf0b7aadbdca59a8349c4e0e96e47b9ff5f89b8498b9ad02adcd59` |
| `control_input/scenario_control.sumocfg` | `87ba0d7d671f1f72f45d7fda3c3e857a1622263a9c2ce4d3f1ef625745f7ab7c` |
| `control_input/demand_control.rou.xml` | `0edeb776e6656f3fd22f1e8d0b4c07ece17903695c901af576d93fb205b26865` |
| accepted network `network.net.xml` | `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` |

## Retry boundary

The proposed distinct ID is `RI3350_CTRL_S17_technical_retry1`, with output
directory
`artifacts/stage6_ramp_induced_validation_20260922_v1/outputs/RI3350_CTRL_S17_technical_retry1`
and a distinct one-use reservation. No card or reservation for that ID has
been created. The previous card authorizes only the already-consumed first
attempt and is not carried forward. The prior 180-second and 300,000,000-byte
monitored triggers were explicitly run-scoped to attempt1 and have been
removed as runner-wide fixed values; retry resource limits remain unresolved
and require separate approval. No final exact retry card is to be emitted
until engineering, data, and scientific reviews are complete; any resulting
card must remain disabled until the user approves its exact hash.

## Offline verification

- R02 suite: `.venv/bin/python -m unittest discover -s artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start -v` — **31 passed**. Uses fixture repositories, mocked orchestration, and fake Python children only; an invalid schema hash also verifies Guardian rejects START before spawning the fake child.
- Static compile: `.venv/bin/python -m py_compile .../runner.py .../test_runner.py` — **passed**.
- XML schema check: `/usr/bin/xmllint --nonet --noout --schema <bound local schema> <failed output>/scenario_control.add.xml` — **validates**.
- SUMO, netconvert, and TraCI launches for this repair: **none**.

## Implementation hashes

| File | SHA-256 |
|---|---|
| `runner.py` | `abba1b31970a4690a262881cec1ea0957b2386c65a20c4105a711cebf3c80154` |
| `test_runner.py` | `c3f86778f353a604070f9949959de65e4cb2281c64036d3ff6924e45ad0eb857` |
| `R02_RUNNER_CONTRACT.md` | `a2adcd9fdccec3251f743caea3ead1f7a76ee8b481a1c9fad123e2c4a0553fbe` |

No conclusion about freeway performance, demand adequacy, or scientific
baseline suitability follows from this initialization failure.
