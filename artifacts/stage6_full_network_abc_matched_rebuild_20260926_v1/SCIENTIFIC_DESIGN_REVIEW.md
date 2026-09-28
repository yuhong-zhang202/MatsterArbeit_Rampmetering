# Independent scientific design review

**Reviewed design SHA-256:** `c917ed32e2cbd783299487a02b78684bbef512527a5562100a6f654dd97200b9`  
**Reviewer:** project `scientific_reviewer` subagent, read-only  
**Disposition:** `PASS_FOR_EXPLORATORY_PRELAUNCH_DESIGN` (High confidence in design logic; exact-card and runtime evidence pending).

The initial review held the design for two reasons: one fixed-condition negative result could not justify a project-wide `FAILED` label, and the design lacked an explicit scientific-start and technical-retry bound. Both were corrected before this final review. The reviewed design now permits at most four sequential scientific starts, one each for R0/A/B/C, with separately reviewed, versioned technical repair only for an identified engineering failure. It retains the old `A_NOT_EVALUABLE` and corrected `NOT_PAIRABLE` records, keeps fixed-time signal programs distinct from ALINEA, and compares C's M outcome against both A and B.

The reviewer accepted a prospectively generated common speedFactor vector from the SUMO passenger default `normc(1,0.1,0.2,2)` distribution via `random.Random(170026).gauss(1,0.1)`, rejection at `[0.2,2]`, deterministic ID ordering and ten-decimal serialization. This is a new independent realization, not a reconstruction of an old SUMO RNG stream. Before execution, bind the code, algorithm, vector, vType and per-arm equality to hashes; check finite/bounded values, counts and XML chronology. The reviewer identified no remaining design-level blocker. Detector coverage, insertion, unfinished vehicles and raw reconciliation remain runtime gates. This review is not an exact-card or outcome review.
