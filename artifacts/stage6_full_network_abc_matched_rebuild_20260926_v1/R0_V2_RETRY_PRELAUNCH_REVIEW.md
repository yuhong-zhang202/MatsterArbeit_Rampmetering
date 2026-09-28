# R0 V2 technical retry exact review

**Card:** `FULLNET3350_R0_S17_REBUILD_V2_TECH_RETRY_CARD.json`, SHA-256 `4488b378f4364dd6275123b98f2e367fcdda9c3affc50afb9786ad68d234c1a6`.  
**Disposition:** `PASS_FOR_ONE_VERSIONED_R0_TECHNICAL_RETRY`; no R0 outcome or A/B/C release.

- `simulation_engineer` independently returned engineering **PASS**: V2 four-arm demand XML is byte-identical to V1; normalized configs and additional files differ only by new input/raw paths. Thirteen package files and four source hashes match, static audit and runner preflight pass, twenty output refs point to unused V2 raw paths, and the new reservation is absent. Bound resource limits remain 120 s, 100,000,000 bytes and 100 ms. Runner V2, SUMO binary, `SUMO_HOME` and both local XSD hashes match the card. V1 ten raw files and failed reservation are unchanged.
- `data_analyst` independently returned data/provenance **PASS**: card/manifest hashes, all V1→V2 demand bytes, seed17, network, 0–2700 s horizon, one-second step and A/B/C programs match; the old failed raw remains hash-identical and the new root is unused.
- `scientific_reviewer` returned `PASS_FOR_ONE_VERSIONED_R0_TECHNICAL_RETRY` after checking the V1 pretraffic failure and V2 environment-only fix. It required this engineering/data review to be recorded before launch; both are recorded above. The V1 attempt remains `TECHNICAL_PRETRAFFIC_FAILURE / NO_SCIENTIFIC_OUTCOME`, with its one-use card consumed. The V2 run cannot itself establish R0 normality or any A/B/C phenomenon.

No SUMO process was started in these reviews. The only permitted next process is one V2 R0 launch under the exact card and its resource limit.
