# Optional detector filter semantics — technical evidence

Confidence: High for documented/parser default semantics; actual repaired SUMO loading remains untested.

The installed SUMO1.26 `data/xsd/additional_file.xsd` marks `vTypes` and `nextEdges` optional in E1/E2 declarations (lines148–149 and187–188). XSD uses string types; it did not reject explicit empty strings. The real revision03 parser did reject those strings. Therefore passing XSD alone is insufficient.

The exact upstream [v1_26_0 NLHandler.cpp](https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_26_0/src/netload/NLHandler.cpp) reads both attributes through optional-string access with empty defaults in E1 lines936–937 and E2 lines1057–1058. Omission therefore requests the parser's default filters. [Official E1 documentation](https://sumo.dlr.de/docs/Simulation/Output/Induction_Loops_Detectors_%28E1%29.html) and [E2 documentation](https://sumo.dlr.de/docs/Simulation/Output/Lanearea_Detectors_%28E2%29.html) define the default vehicle-type filter as all types and the default future-edge filter as empty, imposing no future-edge restriction. Non-empty values deliberately restrict detection and must remain intact.

This is operational equivalence to the registered intended unfiltered measurement, not a claim that the rejected old XML ever ran. Repair removes only22explicit-empty attributes per additional file; non-empty filters, IDs, positions, lanes, periods, thresholds and all non-detector inputs remain unchanged apart from new archive paths/identities. Installed binary and local schema hashes remain bound. Upstream version-tag code plus local package metadata provides version-specific source evidence; it is not a binary-runtime test.

Sources were read through the web tool on2026-09-20. Direct shell HTTP fetching failed DNS and was preserved in source_fetch_receipt.json; no downloaded C++ bytes or source hashes are fabricated. The local installed schema and package metadata have exact hashes in the static/card bindings.
