# Prospective Stage 6 matched full-network audit

This script is prepared for the versioned matched reconstruction. It does not
read the historical `FULLNET3350_A_R900_S17` post-activation data and does not
run SUMO. It writes no result until a new raw pair exists.

## Input spec

Create a JSON file with ordered `R0`, `A`, then optionally `B`, `C` arms. Paths
point to each new run's immutable `outputs/` directory and its prospective
materialized route file. Each output directory needs an `output_manifest.json`
plus `fcd.xml`, `tripinfo.xml`, `vehroute.xml`, `lanechanges.xml`, and
`ramp_storage_e2.xml`. Example for the first sequential gate:

```json
{
  "expected_counts": {"M": 1396, "R": 240, "U": 150, "X": 75},
  "arms": {
    "R0": {"raw_outputs": "/absolute/new/R0/outputs", "demand_xml": "/absolute/new/R0/demand.rou.xml"},
    "A": {"raw_outputs": "/absolute/new/A/outputs", "demand_xml": "/absolute/new/A/demand.rou.xml"}
  }
}
```

Run from the repository root after the independent run integrity review:

```sh
python3 -B scripts/stage6/fullnet_abc_analysis_20260926/analyze.py \
  --spec /absolute/path/to/new_pair_spec.json \
  --output data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/pair_r0_a
```

The output directory must not exist. Use a fresh directory for each later
prefix and retain earlier outputs. The script verifies raw manifest hashes,
materialized demand identity and exogenous fields, expected class counts,
tripinfo/vehroute consistency, all 2700 FCD seconds and all 90 E2 bins before
writing CSV tables. The receipt binds input hashes and reports unexpected M
lane/coordinate samples. Any such samples require independent review.

## Outputs and limits

- `lifecycle.csv`: planned, inserted, arrived, unfinished, never inserted,
  demand-period insertion and FCD identities by class.
- `exogenous.csv`, `pre_R_pairability.csv`: requested-input checks and exact
  FCD tuples plus a coarse lane/position/speed diagnostic before 540 s.
- `R_exposure.csv`: first and cumulative observed auxiliary and through-lane
  R entries at fixed cutoffs. Through entries combine 1 s FCD and lanechange
  events; unresolved detector/temporal coverage must be reviewed separately.
- `M_core_30s.csv`, `M_core_pairwise_30s.csv`: every cell 13–17 and complete
  30 s bin, including pre-activation and late tail, with M-only speed, count
  and density. Empty bins have null speed, never an invented zero.
- `route_costs.csv`: M/U/R observed external insertion wait, in-network
  residence and timeLoss, with unfinished and never-inserted counts. Means use
  all planned identities and are incomplete if any vehicle never inserted;
  unfinished residence ends at the fixed horizon. They are not pure spillback
  costs or complete travel times for censored cohorts.
- `R_occupation.csv`, `ramp_storage_E2_30s.csv`: lane occupation/stopped R
  time and detector jam length/count. These are diagnostics; they do not
  reproduce the historical meter-anchored queue algorithm or prove physical
  spillback across a mapped storage boundary.

The code does not apply the locked P/S/L classifier, decide A/B/C support,
infer causality, assign a Stage 6 status, or estimate uncertainty from one
seed. Scientific review must inspect full time/space patterns, source and
downstream alternatives, detailed queue morphology, and the legacy diagnostics.

Synthetic fixture verification:

```sh
python3 -B -m unittest discover -s scripts/stage6/fullnet_abc_analysis_20260926 -p 'test_*.py' -v
```
