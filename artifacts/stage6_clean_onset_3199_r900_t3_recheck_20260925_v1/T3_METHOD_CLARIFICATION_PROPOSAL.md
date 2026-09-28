# T3 method clarification proposal — NOT ADOPTED

Status: `PROPOSED_NOT_ADOPTED`. Scope: Stage 6 exploratory Candidate A (`CLEAN3199_A_R900_DELAYED_S17`) only. This proposal was written **after** inspecting that run's auxiliary E1 exposure counts. It is not a prospective preregistration or a change to the locked P/S/L classifier, 0.85 reference, event windows, geometry, vehicle behavior or formal experiment protocol.

## Conflict to resolve

The earlier reviewed Stage 6 validation plan and exploratory witness contract define T3 as three consecutive complete 30 s bins with positive **certain route-consistent per-vehicle R auxiliary-entry counts**, reconstructed using FCD and native lane changes with interval bounds. That witness contract was adopted only for its scoped D-005 pair; both documents provide methodological lineage, not independent authority over D-009. The later adopted D-009 clean-onset plan says “previously fixed three consecutive positive complete auxiliary E1 bins.” Its literal E1 condition is different: the E1 detector is at 20 m within the auxiliary lane and may miss a vehicle that enters that lane and leaves it before 20 m. No rule precedence is silently inferred here.

## Proposed narrow interpretation, subject to independent review and explicit adoption

For a clearly labelled `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS` of the already existing Candidate A raw, interpret D-009's “previously fixed” T3 as the earlier, per-vehicle route-consistent certain-entry method. Keep auxiliary E1 counts as an independently reported detector diagnostic; never substitute them for boundary crossings or hide their disagreement. Use the same fixed 30 s bins and T3 confirmation deadline t<=720. Use all R identities, preserve interval censoring and boundary cases, and require three consecutive complete bins **after T2** with at least one certain entry each. Freeze the reconstruction code, full ledger and hashes before any post-R P/S/L or matched M outcome is opened. If this clarification is adopted, T3 passage only opens subsequent locked analysis; it does not establish a witness or guarantee evaluability.

## Preservation and stop boundary

The original `NOT_EVALUABLE / EXPOSURE_GATE_NOT_MET` receipt remains an immutable historical classification under the literal D-009 E1 wording. A new sensitivity receipt, if later authorized, must sit beside it and state the post-result origin of this clarification. The alternative is to retain literal E1 as decisive for D-009 and stop Candidate A at its historical classification, while correcting the physical statement that zero E1 counts imply zero auxiliary entries. Neither option licenses a new SUMO run, R1080, threshold change, or outcome analysis before a recorded scientific decision.
