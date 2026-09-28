# Supersession notice

This first generated package is retained for audit history and is **superseded** by `stage6_pair_3199_matched_input_repair_20260923_v2`.

The v1 materializer read `speedFactor` from `tripinfo.xml`, whose configured output precision is two decimals. That precision can collapse distinct per-vehicle values and is not acceptable for a 100% exact matching invariant. The corrected v2 reads the higher-precision per-vehicle `speedFactor` from immutable `vehroute.xml`. Do not use v1 inputs for any future run preparation.

No SUMO run was made while finding or correcting this serialization-precision issue.
