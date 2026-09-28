# New matched R0 exact prelaunch review

**Card:** `FULLNET3350_R0_S17_REBUILD_V1_CARD.json`, SHA-256 `8ea2e804cd585e5352ed4a1de55ad229ed35701f440c8f2dfed3f23b74fcf042`.  
**Design:** `EXPLORATORY_DESIGN.md`, SHA-256 `c917ed32e2cbd783299487a02b78684bbef512527a5562100a6f654dd97200b9`.  
**Input manifest:** `inputs/INPUT_MANIFEST.json`, SHA-256 `e5d3cb85765c5f1987e01ad21c98b99ac6694dfc72805434f73c7445bd717b68`.

Independent project-scoped reviews before any start:

- `simulation_engineer`: engineering static **PASS**. Exact card and 13/13 package-file plus 4/4 source hashes match; runner preflight returns `PREFLIGHT_PASS_NO_PROCESS_STARTED`, 20 output references stay in the new arm directory, the reservation/raw target is absent, and the bound limits are 120 s, 100,000,000 bytes and 100 ms polling.
- `data_analyst`: input/provenance **PASS**. Independent XML parsing gives R0 M1396/U150/X75/R0 and A/B/C M1396/R240/U150/X75; all common requested fields and all A/B/C R fields match. All 1,861 prospective speedFactors were independently regenerated with zero mismatches. The 1.074 s M period and `M_flow.502=539.148 s` agree with historical R0 requested scheduling, without importing an old outcome as a new input.
- `scientific_reviewer`: `PASS_FOR_ONE_R0_START`, High confidence in static binding. The symbolic `best/max/last` semantics, prospective vector, seed17, detector/config references and network/binary hashes match the reviewed design. The review authorizes scientific interpretation only after R0 insertion/lifecycle, measurement and later pre-R R0/A gates; old R0 `CONTROL_NOT_EVALUABLE` remains unchanged.

This record permits one R0 start under the exact card. It does not release A, B or C and does not assert an R0 scientific outcome.
