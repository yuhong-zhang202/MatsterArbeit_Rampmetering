# R02 single-start runner contract

Status: **RUNTIME/SCHEMA BINDING FIX IMPLEMENTED; CONTROL FINAL REV1 CONSUMED; TREATMENT PRELAUNCH REV1 READONLY-BOUND, AWAITING REVIEWS/AUTHORIZATION**

This fail-closed runner retains the historical, consumed technical-retry
binding `RI3350_CTRL_S17_technical_retry1` and separately supports exactly two
new run IDs: `PAIR_3199_CTRL_S17` and `PAIR_3199_R720_DELAYED_S17`. The consumed
`RI3350_CTRL_S17_attempt1` reservation, card, and outputs remain immutable and
remain bound as the historical retry parent. Pair cards are accepted only at
their exact versioned paths and only when run ID, pair package, exact inputs,
runtime file/hash, output path, and one-use reservation all agree. Unknown IDs,
cross-card IDs, changed hashes, existing output paths, and mismatched runtime
or SUMO_HOME bindings fail closed. The rev2 pair bindings remain drafts; only
the separate control FINAL path records the user's one-start authorization.

An additional exact binding now exists for
`artifacts/stage6_pair_3199_s17_preparation_20260923_v1/PAIR_3199_CTRL_S17_CARD_FINAL_REV1.json`.
It is separate from and does not replace the rev2 draft binding. The final
control path accepts only `FINAL_AUTHORIZED_FOR_ONE_START` plus an exact
authorization record, 90 s / 60,000,000 decimal-byte per-run limits, 100 ms
output polling with accepted overshoot, one start, zero retries, and explicit
prohibitions on treatment, seed23, B/C, and other demand points. Its separate
runtime binding is
`runtime_bindings/PAIR_3199_CTRL_S17_FINAL_REV1.json`. This preparation passed
the local mock suite and read-only runner preflight, but independent
engineering/data/scientific re-review is pending; no reservation or process
has been created.

The current treatment-only prelaunch binding is
`artifacts/stage6_pair_3199_s17_preparation_20260923_v1/PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV2.json`.
It is allowlisted only for read-only `preflight`: its required status is
`PRELAUNCH_READY_AWAITING_AUTHORIZATION`, `execution_authorized=false`, and its
resource proposal is `PROPOSED_NOT_AUTHORIZED`. Runner checks bind the adopted
Stage 6 witness-contract path/hash and seven separate chronology markers:
R activation, first scheduled R departure, first actual R departure, first R
arrival near the merge, first meaningful merge exposure, first M deterioration
and State1 onset. The separate arrival and exposure markers follow the contract's
distinct physical definitions. The prior prelaunch REV1 remains preserved as an
earlier engineering artifact; REV2 supersedes its timeline completeness. The older `LOW_R_BACKGROUND_ACCEPTABLE` gate
is not a treatment-release prerequisite under this scoped prelaunch card.
The ordinary launch validation does not allow this prelaunch-only binding and
fails before creating a reservation or process. This card grants no start.

## Runtime and local schema binding

The failed attempt's SUMO log records that schema resolution tried
`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/data/xsd/additional_file.xsd`
and then could not reach the online schema host. The failed attempt did not
record the process's inherited environment, so the exact historical
`SUMO_HOME` value is unknown. At this inspection, the inherited environment
was set to the framework root, consistent with the logged lookup path.

For the installed SUMO 1.26.0 framework, the usable distribution root is:

`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo`

Under that `SUMO_HOME`, `xsd/additional_file.xsd` is absent; the installed
schema is at `data/xsd/additional_file.xsd`, absolute path
`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo/data/xsd/additional_file.xsd`,
SHA-256 `c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e`.
The runner verifies the canonical SUMO_HOME, exact schema path, file presence,
and schema SHA before Guardian launch and again in Guardian before child spawn.
It explicitly overrides inherited `SUMO_HOME` for both Guardian and simulator
child. Missing or changed schema fails closed before a child is created.

The only changed runtime setting for a future retry is this explicit local
schema-resolution binding. Scientific inputs, geometry, demand, detector/TLS
semantics, classifier, and protocol are not changed. The failed materialized
additional XML validates against the installed schema with local
`xmllint --nonet`; no network schema fetch is needed.

## One-use and output behavior

Every exact card must bind unchanged scientific input hashes, runner/Guardian
SHA, SUMO binary path/hash/version, project Python evidence, SUMO_HOME, schema
path/hash, a unique per-run output destination, one start, retry count zero,
and positive finite monitored resource triggers. Runtime binding files and
card-embedded values are compared. Pair runner bindings are independently
scoped to each card and output path.

The preserved RI3350 retry receipt reports 24.465112 s wall clock and
21,720,062 payload bytes. The completed full-horizon matched PAIR3199 control
reports 24.881003 s and 20,821,740 payload bytes. The brief TV_A capture
(1.143858 s, 25,522,462 observed peak bytes) is not treated as a full-horizon
analogue. Treatment-only proposed limits are 120 s and 90,000,000 decimal
bytes, marked **`PROPOSED_NOT_AUTHORIZED`**; these are separate from the
control's previously authorized 90 s / 60,000,000 bytes. This is not
authorization and is not inherited from the
RI3350-only 180 s / 300,000,000-byte contract. The output-size control is a
100 ms polled stop trigger with possible overshoot, not a hard quota. The
runner will reject a pair launch unless a future exact card explicitly binds
resource status `AUTHORIZED_FOR_THIS_RUN`.

The one-use reservation is created and durably fsynced before Guardian
startup. Guardian READY must precede START. It owns the child process group;
launcher pipe disappearance triggers process-group termination and Guardian
self-finalization. The runner writes a deterministic output manifest and an
immutable execution receipt after child exit. Normal disarm follows durable
final-status handoff including parent-directory fsync. Tests use only fake
Python children; they do not start SUMO.

## Retry-card / invocation boundary

The RI3350 retry card and its one start are historical and consumed. Pair
revision-2 cards and runtime bindings remain immutable offline-review artifacts;
both remain `DRAFT_NOT_AUTHORIZED`, `execution_authorized=false`, and have no
command. The user has explicitly authorized exactly one control start and
accepted its pair-specific 90 s / 60,000,000-byte polling-stop contract. The
control FINAL revision binds this authorization, but remains unconsumed pending
independent re-review. Treatment has no authorization. The final card's exact
hash is required for read-only preflight or launch:

```sh
.venv/bin/python artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py \
  preflight --repo "$PWD" \
  --card artifacts/stage6_pair_3199_s17_preparation_20260923_v1/PAIR_3199_CTRL_S17_CARD_FINAL_REV1.json \
  --approved-card-sha256 <FINAL_CARD_SHA256>
```

Preflight does not consume the one-start authorization. Launching the final
card consumes it before Guardian startup; any spawn failure, timeout, cap
breach or nonzero exit remains consumed, and no retry or subsequent demand
point follows.

## Verification boundary

The R02 offline pair suite uses temporary repositories, fake SUMO/Python/schema
files, and mocked Guardian orchestration. It verifies exact pair ID/card path
binding, per-arm output and reservation isolation, runtime and provenance hash
refusal, draft/resource authorization refusal, one-use/no-retry, and output
collision refusal. It also reconstructs regression checks for reservation
fsync ordering, Guardian invalid-start/no-child behavior, polled stop-trigger
boundaries, SIGTERM/SIGKILL process-group escalation, and deterministic output
manifest inventory. The former test file was unavailable for restoration, so
these are targeted reconstructed checks rather than the historical 23-test
suite. The suite does not execute any binary or inspect the host runtime, and
does not prove SUMO compatibility or scientific validity. Static XML checks
are outside the runner and cannot prove runtime behavior.
