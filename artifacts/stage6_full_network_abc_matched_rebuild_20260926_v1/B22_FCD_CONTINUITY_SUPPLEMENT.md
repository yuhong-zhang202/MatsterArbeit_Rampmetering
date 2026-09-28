# Default B22 per-vehicle FCD continuity supplement

**Date:** 2026-09-26  
**Reviewer:** independent `data_analyst`, read-only raw audit.  
**Disposition:** `PASS_FCD_PER_VEHICLE_CONTINUITY` (High confidence). No change to the negative B22 scientific disposition or Stage 6 `PARTIAL`.

The completed B22 receipt and all 22/22 output files match recorded sizes and SHA-256; the duplicate execution receipt is byte-identical. Demand, tripinfo, vehroute and FCD each contain exactly the same 1,861 IDs (M1396/R240/U150/X75), all departed and arrived. The FCD has every integer timestamp 0–2699 and 179,991 vehicle observations. The reviewer checked each ID's observed timestamp sequence from first through last: zero duplicate ID/timestep, noninteger time, interior missing second or ID mismatch. First FCD second equals realized tripinfo depart for every vehicle; last equals arrival minus one second for every vehicle; zero endpoint exceptions.

This closes the default B22 per-vehicle sample-completeness caveat for the reported local M and R/U FCD measures. It does not resolve early distant M divergence, establish a physical freeway response, prove a continuous spillback front, or justify a new run. No raw/processed/script/document from the historical run was overwritten and no SUMO process was started.
