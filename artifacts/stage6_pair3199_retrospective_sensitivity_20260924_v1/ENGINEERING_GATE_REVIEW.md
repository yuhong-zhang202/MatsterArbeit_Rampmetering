# Engineering review — retrospective sensitivity Gates A/B

**Scope:** Read-only engineering review for the adopted Stage 6 Amendment V1. No simulator, TraCI or netconvert was started; raw files were not modified. Repaired-treatment data at t>=660 were not opened.

## Findings

- **Gate A (`t<540`):** Engineering inspection found exact same-time M/U/X FCD tuple matches in the audited period: M 32,513; U 3,061; X 1,759. M and X remained exactly matched in Gate B as well. Data_analyst independently recomputed Gate A across all M/U/X with 37,333 vehicle-seconds and no mismatch or unmatched key.
- **Gate B M:** No mismatch found (3,243 common vehicle-seconds in independent data review).
- **Gate B U/source:** Seven U identities (`U_flow.53–.59`) have 198 differing tuples starting at t=540. U54's actual departure coincides with R0's first actual departure; both are on `urban_in_0`. The first treatment U54 position is 341.06 m versus 363.09 m in control; R0 is at 354.86 m. A later same-edge/lane proximity is also recorded by the engineering inspection. This supports a possible shared-source insertion/contact pathway. It does not establish a physical car-following mechanism or distinguish source sequencing from all stochastic effects.
- **Randomness:** The v5 common-input binding fixes common IDs, schedules, routes, types and speedFactors, and pre-treatment trajectories match. It does not expose a SUMO runtime RNG draw-order trace after R is added. Post-activation RNG effects therefore remain unverified.
- **Geometry and measurement:** The pair uses the same accepted network and output/measurement definitions. No affirmative geometry or measurement defect, failed R insertion, or lane-mapping defect was identified in the bounded engineering review. Absence of an identified defect does not establish the physical cause of the U divergence.
- **X classification:** X uses `cross_in -> cross_out`; R uses `urban_in -> shared_approach -> ramp_storage -> ramp_accel -> merge_section -> main_down`. These routes have distinct edges but share the same signalized `urban_tls` on conflicting link indices. X is therefore **not verified outside the R treatment pathway** and is not a clean negative control. Its exact FCD match is descriptive only.

## Engineering gate disposition

The engineering review found no affirmative geometry, measurement, or insertion-failure artifact in the bounded records. It supports retaining U divergence as a possible R-pathway response while leaving source-insertion and post-activation RNG mechanisms unresolved. This does not clear Gate B; the independent scientific reviewer found those unresolved alternatives material to later M attribution.

## Evidence bindings

| Evidence | SHA-256 |
|---|---|
| Shared network | `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` |
| v5 control demand | `b98bbedfb4dc4310526184e4d326bd9a9e03e072683aa67f8116bd56c5f9bd81` |
| v5 treatment demand | `b8aae801122e918731fb8e05a9aa8ca94873f02282d7f1afee57777f6bea96ea` |
| Treatment additional/TLS/detector definition | `f5156ffc1df7115c131bd2cef7bf3c119d86d57d781174a8ade565fb819f49ee` |
| Control raw FCD | `ebefb9486daa7da96242a5ee525c232763ea6460368ad06645891ac8b4ca9a33` |
| Treatment raw FCD | `ac5b74632b6d445aea5d5dfc4d58b3cc4b38d379418483bc71c408daf3c94f89` |
| Control lane changes | `5f34509d313f0ebbdb14f6de1647c97960a74e3be0fde12ce26d7a4467ad9e14` |
| Treatment lane changes | `b0087dc4a9e1159d1b3c3f2b0debee6dfaf51e29c47d7c963666916e41363bbb` |
| Control TLS states | `734e94082733197988dc8dc9694bf3deed9b0a1d53c0b36329ba7331e55729ac` |
| Treatment TLS states | `69589b021a2339b61019f3f1babff583358b50be0d9a3197f07fa816f16179ec` |

The exact cards are bound in the data review receipt: control SHA-256 `0748d37719541d7c76adcd57e07fd764b413fbd21bb16e015b57024175e866da`; treatment SHA-256 `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.

## Sequence deviation disclosure

During its engineering review, the reviewer inspected treatment FCD/lane-change records labeled 591–659 and detector interval coverage ending by 660 before the independent Gate A/B data and scientific signoffs. This was earlier than the frozen plan's sequence. The reviewer did not inspect t>=660 data or any P/S/L, Candidate A/C, M deterioration or witness outcome. This premature exposure-only access is disclosed as a process deviation and was not used to clear Gate B or to make a Gate C/D finding. The data analyst and Gate A/B scientific reviewer did not access records labeled >=591.
