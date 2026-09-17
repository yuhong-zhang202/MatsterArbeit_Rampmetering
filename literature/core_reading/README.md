# Core Reading Package

**Prepared and re-verified:** 2026-09-04  
**Purpose:** First-stage literature and documentation for the traffic-flow and measurement knowledge gate before further uncontrolled SUMO exploration.

This directory keeps the current learning materials together. A file is labelled `full text` only when its type, title, authors, and page count were checked locally.

## Local files

| Reading unit | Local file | Availability | Verification |
|---|---|---|---|
| Treiber & Kesting (2013), *Traffic Flow Dynamics: Data, Models and Simulation*, 1st ed. | `Traffic Flow Dynamics.pdf` | Full content; source provenance should be replaced with a TU Berlin/Springer copy when available | PDF, 504 page objects ending at printed page 503; title, authors, edition, ISBN and DOI checked |
| Brilon, Geistefeldt & Regler (2005), *Reliability of Freeway Traffic Flow: A Stochastic Concept of Capacity* | `RELIABILITY OF FREEWAY TRAFFIC FLOW.pdf` | Full text | PDF, 20 pages; title, authors and ISTTT16 citation checked |
| Cassidy & Bertini (1999), *Some Traffic Features at Freeway Bottlenecks* | `Some trac features at freeway bottlenecks.pdf` | Full text | PDF, 18 pages; journal pages 25–42 and DOI checked; filename contains a `traffic` typo |
| Papageorgiou & Kotsialos (2002), *Freeway Ramp Metering: An Overview* | `Freeway_ramp_metering_an_overview.pdf` | Full text | PDF, 11 pages; IEEE journal pages 271–281 and DOI checked |
| Eclipse SUMO documentation | `sumo_docs/` | Four focused offline pages for the current learning stage | VehicleInsertion, E1, E2 and TripInfo pages checked against the official documentation snapshot |

## Stable online access

- Treiber & Kesting 2013 first edition: <https://doi.org/10.1007/978-3-642-32460-4>
- Treiber & Kesting 2025 second edition: <https://doi.org/10.1007/978-3-031-93922-8>
- Cassidy & Bertini postprint record: <https://digitalcommons.calpoly.edu/cenv_fac/307/>
- Cassidy & Bertini DOI: <https://doi.org/10.1016/S0191-2615(98)00023-X>
- Papageorgiou & Kotsialos institutional record: <https://sndbx.library.tuc.gr/view/61894?locale=en>
- Papageorgiou & Kotsialos DOI: <https://doi.org/10.1109/TITS.2002.806803>
- SUMO Vehicle Insertion: <https://sumo.dlr.de/docs/Simulation/VehicleInsertion.html>
- SUMO E1: <https://sumo.dlr.de/docs/Simulation/Output/Induction_Loops_Detectors_(E1).html>
- SUMO E2: <https://sumo.dlr.de/docs/Simulation/Output/Lanearea_Detectors_(E2).html>
- SUMO TripInfo: <https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html>

## Verification notes

- The local complete textbook is the **2013 first edition**, not the 2025 second edition used in the original reading recommendation. For the first learning block, use Chapter 3, *Cross-Sectional Data*, and Chapter 4, *Representation of Cross-Sectional Data*. Do not use 2025 chapter or page references with this file.
- The textbook content identity is verified, but its previous filename identified a third-party mirror rather than Springer or an institutional repository. Prefer a TU Berlin/Springer copy for a traceable source.
- The SUMO pages are official documentation snapshots, but they are not pinned to the project's SUMO 1.26.0 installation. Verify version-sensitive fields, defaults and behavior against 1.26.0 before relying on them in an experiment.
- Only the four focused pages in `sumo_docs/` are retained. The redundant full-site ZIP and extracted site snapshot were removed after verification.
- The PDFs were checked by metadata/text extraction and representative first/last-page rendering. This verifies identity and apparent completeness; it does not turn their claims into evidence for the synthetic SUMO scenario.

The web-chat tutor prompt is stored in `WEB_CHAT_LITERATURE_TUTOR_PROMPT_ZH.md` and has been adjusted to the local 2013 first edition.

## Exploratory validation completion methods

The later [2026-09-09 methods review](../EXPLORATORY_VALIDATION_REVIEW_20260909.md) adds targeted primary-source guidance from Sargent, FHWA 2019 and SUMO for defining exploratory outputs, measurable checks and intended-use limits. It supports the [Proposed completion plan](../../docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md); it is not an additional completed experiment or an empirical calibration of this synthetic scenario.
