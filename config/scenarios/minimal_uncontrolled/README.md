# Minimal uncontrolled technical scenario

This project-owned SUMO scenario exists only for technical validation and
exploratory smoke/stress testing. It is not a frozen thesis experiment and
none of its geometry, signal timing, demand, duration, or seed values is a
scientifically justified parameter.

The scenario contains:

- `M`: two-lane freeway mainline traffic;
- `R`: urban traffic that uses the entrance ramp and joins the freeway;
- `U`: urban through-traffic that shares the approach with `R` and diverges
  before the ramp;
- `X`: technical cross traffic used to exercise a fixed-time urban signal.

`R` and `U` share `urban_in` and `shared_approach`. The downstream end of
`shared_approach`, at `urban_diverge`, is the technical finite-storage
boundary. A stopped `R` vehicle on `shared_approach` therefore constitutes a
technical boundary crossing. This is a deliberately simple observable, not a
formal spillback definition.

`run_minimal_uncontrolled.py` copies these sources to a new directory under
`/private/tmp`, builds `network.net.xml` with `netconvert`, generates a
technical demand profile, and writes every runtime output only to that
temporary directory. Four lane-specific induction loops provide technical
30-second flow, speed, and occupancy observations upstream and downstream of
the merge. Their positions and aggregation period are placeholders.

```bash
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --validate-only
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --profile low
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py --profile stress
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --profile low --q-main 1440 --q-ramp 480 --seed 17
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --profile low --q-main 2600 --q-ramp 600 --seed 17 \
  --warmup-s 600 --measurement-duration-s 600 \
  --post-demand-clearance-s 900
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --reanalyze-summary /private/tmp/example_run/summary.json
```

`--q-main` and `--q-ramp` are veh/h inputs and must be provided together.
They parameterize only `M` and `R`; `U` and `X` remain fixed technical
placeholders. A custom invocation is one technical test point, not a demand
grid or a scientifically selected condition.

`--warmup-s`, `--measurement-duration-s`, and
`--post-demand-clearance-s` define exploratory warm-up, measurement, and
post-demand clearance windows. The demand ends after warm-up plus measurement
unless the matching `--demand-end-s` is also supplied explicitly. Omitting all
four timing options preserves the earlier technical behavior: demand and
measurement span the profile duration, with no separate warm-up or clearance.

The runner stores the raw E1 interval series and separate warm-up, demand,
measurement, and clearance summaries. Initial detector comparisons use the
same `nVehContrib` vehicle weighting for speed as the main speed summary and
do not assume that speed must rise. Queue output is a descriptive difference
and direction between two trailing technical windows. It is not a stable-state
test, a claim that growth persists, or an automatic Breakdown or Capacity Drop
classification. All window lengths remain technical candidates until
separately reviewed; the example above does not freeze them.

The two E2 detectors now have a deliberately narrow technical target: each
observes its own named lane, not an inferred multi-lane storage path. After
network compilation, the runner writes `pos=0` and `endPos` equal to the actual
compiled lane length. For the current network these lengths are 238.80 m for
`shared_approach_0` and 204.49 m for `ramp_storage_0`. Source XML uses
`endPos=-0.1` only as a safe standalone fallback; it excludes the last 0.1 m
until the runner replaces it with the exact compiled endpoint. Do not interpret
the source fallback as the executed runner configuration or as a formal
storage definition.

`src/scenarios/check_e2_coverage.py` loads isolated copies of a network and
additional file through TraCI without advancing simulation time. It redirects
outputs away from the supplied runtime and reports actual detector anchors and
lengths. A legacy detector's full successor chain is not established by the
starting-lane API alone.

New `fcd_lane_observations` accounting explicitly separates named and internal
lanes, with unknown/malformed/duplicate observations surfaced. The composite
ramp path contains the two long internal connections, `ramp_storage_0` and
`ramp_accel_0`; it excludes the shared approach, urban inlet, merge-internal
connection and freeway. Prior named-edge summaries retain their original
scope. Lane counts and mutually exclusive group counts are separate views,
not quantities to add together. These are sampled observations, not effective
queue capacity or causal delay; E2 halting/jam definitions must not be assumed
identical to the FCD speed threshold.

Insertion timing is reported separately from eventual insertion. For each
window and class, the summary records nominal planned departure slots, actual
departures, and directly reported `departDelay`. It also records vehicles
waiting to enter at demand end, late departures during clearance, and vehicles
still not departed at simulation end. The nominal slots are reconstructed from
the flow `begin`, `end`, and `number`; the summary reports their discrepancy
from `tripinfo`'s `depart - departDelay` value. Because no acceptable
`departDelay` or late-insertion criterion has been approved, demand-period
realization eligibility is explicitly `not_evaluated`, even when every vehicle
eventually enters.

`--reanalyze-summary` reads a prior runtime's XML outputs and writes corrected
departure, detector, and queue descriptions to a new
`/private/tmp/minimal_uncontrolled_reanalysis_*` directory. It does not run
SUMO or overwrite the source summary or runtime outputs.

The `low` profile is a functional test. The `stress` profile intentionally
overloads the placeholder system to test whether a ramp queue can cross the
finite-storage boundary and affect the shared urban approach. Neither output
may be used as thesis evidence. Every run reports separate technical
eligibility for fixed-window detector descriptions and for end-of-run vehicle
outcomes. The latter is rejected when any vehicle class exceeds the technical
placeholder end-censoring threshold or when no post-demand clearance is
configured. It is also rejected when planned vehicles depart during clearance;
this is a conservative technical diagnostic, not a formal exclusion rule.
Final insertion completeness is reported separately and must not be read as
timely realization of the requested demand. None of these gates constitutes
capacity-analysis eligibility while the experiment protocol is not frozen.
