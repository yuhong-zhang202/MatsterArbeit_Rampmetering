# Stage 6 cross-control artifact diagnosis — engineering review

**Scope:** Read-only comparison of `RI3350_CTRL_S17_technical_retry1` and `PAIR_3199_CTRL_S17` only. This review assesses whether the recurring low speed-ratio pattern supplies affirmative evidence of a shared technical/model/measurement artifact capable of systematically spoiling a later ramp-induced witness comparison. It does not adjudicate `LOW_R_BACKGROUND_ACCEPTABLE`, choose qMain, certify absence of self-congestion, or release treatment.

**Engineering recommendation for the narrow artifact question:** `NO_SYSTEMATIC_ARTIFACT_EVIDENCE` (moderate confidence). No tested common failure signature points to source insertion starvation, a direct mainline TLS restriction, an unintended receiving blockage at the observed downstream taps, a geometry/lane-map mismatch, or an FCD/E1 processing mismatch. The lane0 mobility deficit is real in native detector and FCD observations and is not pinned to one fixed cell. Its microscopic origin is unproven. The independent data and scientific reviews must decide the overall A/B/C disposition and whether the pattern still prevents the *separate* low-R-background gate.

## Bound inputs and comparison

| Item | RI3350 | PAIR3199 | Engineering observation |
|---|---|---|---|
| Exact FINAL card SHA-256 | `28be8560664c75f0176b048206f50b50392c3ed1c03a64dae02d2e01c0daf91e` | `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da` | Distinct runs and outputs |
| Output manifest SHA-256 | `e72ee6da030083da1ce3c96996c7169d80e7734d71e788eb3e8b326d11cfb3cd` | `da15103c64be65eb6b83fc37a505418c81c33cf490db48f03a5fd15d984a74d8` | Both previously passed independent raw-manifest audits |
| Network SHA-256 | `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` | same | Identical accepted compiled network bytes |
| Additional detectors/TLS selector | 14 elements | 14 elements | After stripping output `file`/`dest` paths, element/attribute sequence identical, SHA-256 of normalized representation `e971f90bc3a349c6987fc9ddc139aef254932627637f51b747c7c7dd839cbe82` |
| Execution | SUMO 1.26.0, seed17, 1 s, 0–2700 s, A_OPEN | same | Same relevant runtime/configuration semantics; qMain and output paths differ |

The network has `main_up_0 → merge_section_1 → main_down_0` as logical lane0 and `main_up_1 → merge_section_2 → main_down_1` as lane1. `merge_section_0` is the ramp auxiliary lane. Both through lanes have the same 33.33 m/s network speed. The auxiliary is 294.51 m, `main_down` 496 m. The locked R04 lane map follows those through-lane connections; this review found no card/network/lane-map inconsistency. A previously accepted static geometry review is in `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/prelaunch_reviews/engineering_review_revision02.json`. This check does not prove that the geometry cannot induce a physical lane-dependent flow pattern.

## Pattern and possible fixed-location signature

Values below are descriptive 30 s cell-bin counts from the two hash-bound processed `cell_lane_bins.csv` files, restricted to core cells 13–17 and [540,1440). A low ratio means `<0.85`; this is not a State1 event rule.

| Run | lane0 low bins by cells 13/14/15/16/17 | lane1 low bins by cells 13/14/15/16/17 | Longest observed lane0 low streak in these cells |
|---|---|---|---|
| RI3350 | 19/20/20/21/19 out of 30 per cell | 8/8/9/8/10 | cell15, 600–870 s (270 s); cell16, 600–840 s (240 s) |
| PAIR3199 | 17/16/15/16/16 out of 30 per cell | 9/10/10/10/9 | cell13, 780–1020 s (240 s); cell15, 1140–1290 s (150 s) |

Both runs have a broad lane0 deficit and intermittent lane1 low bins, with differing streak times and maxima. Cells 12 and 18 also have lane0 low bins (RI3350 17/18; PAIR3199 13/14 of 30), so it does not begin or remain solely at a single merge-core cell. These fixed-cell summaries alone do not establish propagation or recovery physics; the data review owns the full spatiotemporal assessment.

## Technical alternative checks from native outputs

| Alternative | Direct observation | Limit |
|---|---|---|
| Source starvation/insertion | RI3350 tripinfo has M/U/X 1396/150/75, PAIR3199 1333/150/75, R absent in both; all are eventually arrived and no M departs after 1500 s. Maximum serialized M `departDelay` is 1.00 s and 0.88 s respectively. Active-window `summary.xml` `waiting` maximum is zero. | This excludes a large persistent source queue in these records, not every sub-second insertion interaction. |
| TLS | Native `tls_states.xml` has 2700 distinct labels per signal per run. `ramp_mid` is `A_OPEN/G` at all 2700 labels in both. `urban_tls` has the same state counts in both: `Gr` 2025, `rG` 405, `yr` 135, `ry` 135. The mainline network connections have no `tl` attribute. | Urban-side signal influence on U/X exists but no direct mainline red signal is indicated. |
| Downstream receiving | In [540,1440), M-weighted native E1 mean speeds at downstream 20 m/200 m are RI3350 lane0 26.98/26.72 m/s, lane1 29.03/28.79; PAIR3199 lane0 27.04/26.91, lane1 29.00/28.74. Each downstream detector records M throughout the interval and has zero 30 s bins with a valid mean speed below 20 m/s. Summary maximum active `halting` is 3 in both, final `running=0`, `collisions=0`, `teleports=0`; `sumo_error.log` is empty. | Downstream E1 taps and summary do not image all receiving space or establish a capacity-drop test. |
| Lane-dependent behavior/change | Native upstream 1300 m E1 already shows a lane0/lane1 contrast: RI3350 27.08/29.31 m/s, PAIR3199 27.34/29.48 m/s. M lane-change transitions in [540,1440) are 179 and 211; merge-section transitions are 29 and 30, respectively. Raw FCD has 0 M samples on `merge_section_0` or ramp lanes, versus 6558/8101 M samples on merge through lanes 1/2 for RI3350 and 6098/7832 for PAIR3199. | A similar upstream lane gap does not identify whether keep-right/speed-gain lane changes, interactions or stochastic vehicle trajectories caused it. Transition counts are not unique vehicles or causal evidence. |
| Measurement/processing | Identical detector IDs, lanes, positions and 30 s periods in both additional files; no missing native TLS labels, detector roles, FCD/tripinfo identities or error-log messages in earlier reviewed receipts. Native E1 speed asymmetry agrees in direction with processed lane0 lower speed ratios; all logical M lanes are route-consistent. FCD SHA-256 RI3350 `d88b84cac46578bfccb84e529677867a980228c0488268b6c19dd4900e68f565`, PAIR3199 `ebefb9486daa7da96242a5ee525c232763ea6460368ad06645891ac8a33`. | E1 absolute mean speed and speed-factor-normalized FCD ratio are different quantities; independent raw-FCD bin recomputation belongs to data review. |

The E1 figures are `nVehContrib`-weighted means of native 30 s interval speeds over [540,1440); negative no-vehicle speed sentinels are excluded. This arithmetic was performed offline directly from existing immutable XML. Source insertion, geometry and detector conclusions are bounded to these two realized seed17 controls.

## Boundaries and next step

No affirmative structural artifact was detected. A common lane0 slowdown exists but its cause is unresolved; the observed broad spatial distribution, changing streak locations, upstream lane asymmetry, identical validated geometry, full insertion and continued downstream passage do not by themselves justify declaring a model defect. The scientific reviewer should assess whether this *artifact-only* finding permits bounded scanning while retaining the existing `LOW_R_BACKGROUND_ACCEPTABLE=NOT_EVALUABLE` status and treatment prohibition unless a separate exact gate is satisfied.

No files in `data/raw/`, processed analyses, scientific inputs, geometry, demand, classifier, thresholds, normal screen or protocol were edited. No SUMO, netconvert or TraCI process was started for this review.
