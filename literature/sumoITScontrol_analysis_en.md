# Detailed Analysis of `sumoITScontrol` and Its Relevance to the Ramp-Metering Sweet-Spot Study

## Document status

- **Analysed source:** Kevin Riehl, Anastasios Kouvelas, and Michail A. Makridis, “sumoITScontrol: Traffic Controller Collection for SUMO Traffic Simulations,” SUMO Conference Proceedings 7, 2026 (project copy: [`sumoITScontrol.pdf`](./sumoITScontrol.pdf)).
- **Purpose:** Extract controllers, SUMO/TraCI implementation concepts, simulation-design principles, stochastic evaluation methods, and research ideas that may be useful for this master's thesis.
- **Project boundary:** The project scope is still awaiting confirmation by Robert Hilbrich, and no formal experiment protocol has been frozen. All project-specific routes and metrics in this report are therefore **Proposed**, not approved research decisions.
- **Evidence boundary:** The paper supports implementation and methodological choices. It does not establish this project's sweet spot, urban-network spillback effects, or a performance ranking of the controllers.

## 1. Executive summary

The paper is highly relevant to the thesis for two reasons.

First, `sumoITScontrol` provides public, modular reference implementations of established SUMO controllers, including the directly relevant ALINEA, PI-ALINEA, METALINE, and HERO ramp-metering approaches. This reduces duplicated implementation effort and limits comparison bias caused by different projects using materially different code under the same controller name.

Second, the paper treats controller evaluation as a complete stochastic simulation experiment rather than merely running an algorithm and comparing a single number. It addresses warm-up, merge geometry, detector placement, driver heterogeneity, realised-demand validation, common random seeds, repeated runs, variance reporting, effect sizes, and statistical tests. For the present project, this experimental methodology is at least as important as the controller equations.

The most defensible current route is to build a project-owned synthetic network and uncontrolled baseline, then use ALINEA as the primary controlled baseline. Controlled and uncontrolled cases should be compared with matched seeds across the `qMain × qRamp` demand space, jointly evaluating motorway benefits and ramp/urban-network costs. HERO and METALINE only have their full coordination meaning if the approved scope expands to a multi-ramp corridor.

## 2. Problem addressed by the paper

The paper identifies two reproducibility problems in traffic-control research:

1. classical baseline controllers are often reimplemented separately by individual projects, with potentially different code, detector aggregation, control timing, bounds, and edge-case handling;
2. microscopic SUMO simulations are stochastic, so single-run comparisons or mean-only reporting may mistake random variation for control benefits.

The contribution is therefore not a new ramp-metering algorithm. It combines (paper Section 1, PDF pp. 1-3):

- a transparent and extensible controller collection;
- SUMO-oriented guidance for simulation and detector design;
- variance-aware parameter calibration and controller evaluation.

A common controller implementation does not make studies automatically comparable. Comparability still requires the network, demand, vehicle models, time step, detectors, seeds, controller parameters, and metrics to be held constant or documented completely. `sumoITScontrol` primarily removes one source of variation: inconsistent baseline-controller code.

## 3. Structure of the paper

| Section | Content | Relevance to this project |
|---|---|---|
| Section 1, Introduction | Inconsistent baselines and single-run stochastic evaluation | Justifies public baselines and replicated experiments |
| Section 2, Controller Implementation | Ramp-metering and urban signal controllers | Supports controller selection and implementation |
| Section 3, Simulation Design and Sensor Placement | Freeway/urban cases, network, detectors, demand, and behaviour | Supports the design of a project-owned SUMO scenario |
| Section 4, Stochastic Calibration and Evaluation | Replications, common seeds, statistical reporting, and ALINEA calibration | Supports a future experiment and analysis protocol |
| Section 5, Conclusion | Contributions, limitations, and future work | Defines the limits of transferability |
| Appendix A | Controller configurations and demonstration trajectories | Useful as API and reproduction examples, not formal performance rankings |

## 4. How `sumoITScontrol` operates with SUMO

`sumoITScontrol` is not a traffic simulator. SUMO simulates vehicles, car-following, lane changes, roads, and signals. TraCI is the runtime interface between Python and SUMO. `sumoITScontrol` supplies the algorithmic layer that reads traffic states and computes control actions.

Based on the controller descriptions and appendix configurations (paper Section 2 and Appendix A, PDF pp. 3-16 and 34-45), the typical runtime chain is:

```text
SUMO executes one simulationStep
        ↓
TraCI reads mainline detectors, ramp queues, and current signal states
        ↓
sumoITScontrol aggregates measurements and computes a rate at a control instant
        ↓
TraCI translates the rate into ramp-signal actions
        ↓
SUMO advances to the next time step
```

The user must still provide the SUMO network, demand, vehicle types, detectors, ramp signals, simulation time step, and controller parameters. A typical setup creates a `RampMeter` or `RampMeterCoordinationGroup`, instantiates ALINEA/HERO/METALINE, and calls `controller.execute_control(current_time)` inside the TraCI loop. The per-step call description is supported by the software README/API and the project's technical reproduction; the paper appendix mainly provides object configurations and controller trajectories. API behaviour should therefore not be conflated with an experimental finding from the paper.

The paper's example uses a 0.5 s simulation step and a 60 s control cycle. `execute_control` may be called at every simulation step while a new rate is only applied when the measurement/control interval is reached. The metering rate is not an arbitrary software constant: the selected controller calculates it from measured states and user-specified parameters, subject to `min_rate` and `max_rate`.

## 5. Ramp-metering controllers relevant to the project

### 5.1 ALINEA: recommended primary controlled baseline

ALINEA is a local feedback controller using mainline occupancy downstream of the merge, `c_t`, to maintain traffic near a target occupancy, `c*` (paper Section 2.1.2, PDF pp. 4-5):

```text
r_t = r_(t-1) + K_P (c* - c_t)
```

When measured occupancy is above the target, the controller reduces ramp release; below the target, it increases release. ALINEA is simple, interpretable, locally measurable, and compatible with the currently proposed single-ramp synthetic setting.

Target occupancy, feedback gain, control cycle, and metering-rate bounds are directly relevant to the sweet-spot question because they change the balance between mainline protection and ramp queue growth. The example values `target_occupancy=10`, `K_P=30`, a 60 s cycle, and 5%-100% bounds are demonstration values only and must not be treated as formal project parameters.

### 5.2 PI-ALINEA: sensitivity or extension option

PI-ALINEA adds an occupancy-change term to the current occupancy error and introduces another parameter that requires calibration; its actual effect must be evaluated in this project (paper Section 2.1.2, PDF p. 5). If the thesis focuses on the sweet spot rather than controller design, basic ALINEA should be established first; PI-ALINEA can then be considered as a robustness extension.

### 5.3 METALINE: meaningful only for multi-ramp coordination

METALINE uses gain matrices to control multiple ramps jointly; off-diagonal entries represent interactions between ramps. It is relevant when congestion propagates along a corridor with several closely spaced ramps (paper Section 2.1.3, PDF pp. 5-6).

With a single on-ramp, METALINE has no substantive coordination object. With several ramps, matrix calibration becomes a higher-dimensional research problem. The appendix explicitly states that the demonstrated METALINE configuration was not further optimised and that stabilising some ramps came with instability or queue growth at others. The demonstration therefore does not establish that METALINE is better or worse than another controller.

### 5.4 HERO: multi-ramp queue protection

HERO builds on local ALINEA controllers. When one ramp queue exceeds an activation threshold, that ramp becomes the master and upstream ramps become slaves that redistribute restrictions. The cluster dissolves when the master queue falls below a lower release threshold; the hysteresis between thresholds reduces chattering (paper Section 2.1.4, PDF pp. 6-7).

The queue-spillback motivation is highly relevant to this thesis, but the complete HERO mechanism requires multiple ramps. In a single-ramp project, its queue-threshold and hysteresis ideas may inspire a project-owned queue safeguard, but that safeguard should not be described as a full HERO implementation. HERO becomes an appropriate controller candidate only if a multi-ramp extension is approved.

## 6. Reusable elements of the freeway case study

The paper uses an approximately 4.1 km, two-lane motorway with three metered on-ramps of approximately 200 m. It explores three merge geometries: a single ramp with an approximately 200 m auxiliary lane, a direct merge without an auxiliary lane, and a higher-capacity ramp with an approximately 300 m auxiliary lane (paper Section 3.1, PDF p. 17). The general lesson is not that these dimensions are universally correct, but that merge geometry must be treated as an explicit modelling factor.

### 6.1 Warm-up and temporal resolution

The case runs for 4,200 s: 600 s warm-up followed by one analysis hour, using a 0.5 s simulation step (paper Section 3.1.1, PDF p. 18). The transferable principle is to establish representative traffic conditions before measurement, not to copy 600 s uncritically. The project should verify warm-up adequacy through state stability or pilot runs and state whether control is active during warm-up.

### 6.2 Merge-area modelling

The paper recommends explicit verification of lane-to-lane connections, merge-junction type, priority, and lane-change permissions. Mainline vehicles should not unrealistically use an auxiliary lane intended for ramp traffic. Sufficient acceleration distance is needed between the ramp signal and physical merge; otherwise, low-speed merging can artificially reduce mainline capacity and exaggerate congestion.

This is crucial for the thesis: if merge geometry is unrealistic, an apparent ALINEA benefit may be an artefact of correcting model-induced congestion rather than a genuine control effect.

### 6.3 Detector placement

- E2 lane-area detectors may be placed upstream of the ramp signal to measure queue length and occupancy; the paper gives approximately 50 m as an example **detector length**, not a 50 m distance from the signal.
- Mainline detectors should cover each mainline lane but exclude auxiliary merge lanes, which would bias flow and occupancy measurements.
- Mainline detectors may be upstream of, within, or downstream of the merge depending on the objective; classical ALINEA typically uses downstream occupancy around 40-100 m after the merge.
- E1 detectors support point-flow measurements, whereas E2 detectors support spatial occupancy, density, and queue measurements.

If a connected urban component is approved, candidate observation roles include mainline control detectors, ramp queue detectors, and urban-impact detectors. Controller inputs should be distinguished from evaluation outputs so that the controller is not assessed only by the state variable it is designed to regulate. The detector principles come from paper Section 3.1.2 (PDF pp. 19-20); urban-impact detectors are a Proposed project extension.

### 6.4 Demand and driver behaviour

The paper stresses that nominal demand is not necessarily the realised inflow. Safety insertion constraints and congestion may prevent or delay vehicle insertion. Every project scenario should therefore record planned demand, realised inflow, and failed/delayed insertion behaviour (paper Section 3.1.3, PDF pp. 20-22).

The case uses probabilistic rather than strictly periodic arrivals and several behavioural levels for mainline and ramp vehicles to create more realistic merging conflicts, shock waves, and capacity drops. The heterogeneity principle is useful, but the specific `tau`, `lcAssertive`, acceleration, and deceleration values in Table 3 are not calibrated project parameters. Some may also interact with safety warnings observed in the upstream smoke test and require independent review.

The proposed `departSpeed="max"`, `departLane="free"`, and `departPos="last"` settings may be evaluated as candidates. `insertionChecks="none"` relaxes insertion constraints; although it can support high flows, it requires explicit validation for unrealistic insertions, emergency braking, or collisions and should not be adopted merely because the paper uses it.

## 7. Methodological principles to adopt

### 7.1 Matched uncontrolled and controlled comparisons

For every `qMain × qRamp` scenario, uncontrolled and ALINEA cases should use the same network, demand, vehicle distribution, duration, and random seed. Each seed then forms a paired result, reducing noise from stochastic traffic realisations.

### 7.2 Replication rather than single runs

The paper recommends at least 10-20 repetitions per configuration. This is a practical recommendation, not proof of adequate power for every metric. Pilot variance and event frequency should inform the formal replication count, especially for threshold or rare events such as breakdown and spillback. Stopping rules and failed-run handling must be specified in advance.

### 7.3 Report effects and uncertainty together

Primary results should include a mean or median, standard deviation or interquartile range, 95% confidence interval, effect size, and distribution plots. A percentage improvement alone is insufficient (paper Section 4.1, PDF pp. 24-25). For matched seeds, the primary object should be the paired difference per seed. The formal protocol should pre-specify estimands, confidence intervals, and tests by outcome type rather than branching only on normality: continuous paired differences may use a paired t-test, paired permutation, or bootstrap approach, while binary breakdown/spillback events require methods for paired event data such as paired risk differences or McNemar's test. The exact method remains subject to protocol approval.

### 7.4 Separate calibration from final evaluation

The paper frames calibration through three components: parameter space, objective function, and stochastic sampling strategy. The project should additionally avoid using the same scenarios and seeds both to choose ALINEA parameters and to claim final effectiveness. A calibration/evaluation split, or an explicit exploratory/confirmatory distinction, would reduce overfitting and post-hoc claims.

### 7.5 Address multiple comparisons and regional conclusions

A `qMain × qRamp` grid produces many cells. Cell-wise significance testing creates a multiple-comparison problem. A sweet spot should not be defined only by isolated `p < 0.05` cells; it should combine effect size, uncertainty, spatial continuity across the demand grid, and the trade-off among mainline, ramp, and urban user groups.

### 7.6 Preserve complete reproducibility information

Formal runs should preserve run ID, timestamp, software versions, configuration snapshot, demands, seed, controller parameters, output paths, and run status. Failures, teleports, collisions, anomalous queues, and missing outputs must be retained and handled transparently rather than silently excluded.

## 8. Mapping paper concepts to the project

| Paper concept | Project use | Status |
|---|---|---|
| Public ALINEA implementation | Primary controlled baseline | Proposed; compatible with current direction |
| Uncontrolled baseline | Build the uncontrolled demand map first | Proposed; necessary |
| Multiple random seeds | Common seeds for controlled/uncontrolled cases | Proposed; protocol must be frozen |
| Warm-up | Establish representative state before measurement | Principle usable; duration must be validated |
| Merge-geometry review | Check acceleration distance, priority, and lane connections | Reversible technical preparation |
| Mainline and queue detectors | Observe motorway state and ramp-storage pressure separately | Reversible technical preparation |
| Realised-demand validation | Distinguish specified `qMain/qRamp` from actual inflow | Should be part of data validation |
| Stochastic parameter calibration | Calibrate `K_P`, `c*`, and other candidates | Formal scope pending confirmation |
| HERO/METALINE | Multi-ramp coordination extension | Not applicable to a single-ramp core study |
| Urban signal controllers | Possible complex urban-network extension | Should not automatically expand the thesis scope |

## 9. Proposed staged research route

1. **Technical baseline:** build a project-owned minimal motorway/single-ramp network and resolve upstream-demo issues involving yellow phases, `tau`, collisions/teleports, emergency braking, and deprecated APIs.
2. **Uncontrolled demand map:** scan a small `qMain × qRamp` range and verify realised inflow, capacity, breakdown, and queue-formation mechanisms.
3. **ALINEA baseline:** add ALINEA under matched conditions with a small set of interpretable provisional parameters and verify the complete control chain.
4. **Parameter calibration:** use separate calibration seeds/scenarios to study target occupancy, `K_P`, cycle duration, and rate bounds.
5. **Urban connection:** add a minimal but explicit urban component and define vehicle groups, ramp spillback, and impacts on unrelated urban through-traffic.
6. **Formal sweet-spot evaluation:** after freezing the protocol, compare uncontrolled and controlled conditions using common seeds and report system-wide and group-specific effects.
7. **Optional extension:** introduce HERO or METALINE only after supervisor approval of a multi-ramp scope.

## 10. Candidate evaluation framework (Proposed)

Mainline occupancy alone is insufficient as a final outcome because it is both an ALINEA input and close to its control objective. Candidate outcomes include:

- **Motorway:** total time spent, travel time/delay, throughput, speed, occupancy, and breakdown occurrence/duration;
- **Ramp users:** mean/maximum/high-quantile queue length, waiting time, and spillback occurrence/duration;
- **Urban through-traffic:** travel time and delay for vehicles unrelated to the ramp movement;
- **System level:** total loss across all vehicles while retaining group-level results, so that aggregate improvement cannot hide severe harm to one group;
- **Control behaviour:** metering rates, signal changes, time at rate bounds, and oscillation.

A preliminary sweet-spot concept is a demand region in which the mainline gains a practically meaningful improvement supported by uncertainty estimates while ramp and urban losses remain below pre-defined acceptable limits. The limits, weights, and regional decision rule must be specified before formal evaluation and confirmed by the supervisor.

## 11. Elements that cannot be copied directly or are not established by the paper

1. Case-study parameters are not calibrated project parameters.
2. A 10-minute warm-up, 0.5 s step, and 20 seeds are not universally sufficient.
3. The urban intersection and freeway ramp-metering examples are separate cases; they do not validate ramp-induced urban spillback.
4. The ALINEA calibration objective combines mean queue length and occupancy violation; it is not the proposed system-level sweet-spot objective.
5. The METALINE and HERO appendices mainly show trajectories and do not provide complete replicated, significance-tested performance comparisons.
6. The paper does not provide the project's formal definitions of breakdown, spillback, capacity drop, or sweet spot.
7. Sensor noise, communication delays, mixed traffic, and automated large-scale benchmarking are not yet systematically covered.

## 12. Critical assessment of the paper's methodology

The paper's strength is the integration of controller code, network design, and stochastic statistics in one open framework. Its ALINEA calibration example clearly demonstrates that although `K_P=10` has a better mean than `K_P=5`, the reported two-sided test gives `p=0.46`, which is insufficient to reject the no-difference hypothesis.

Several points require care. The methodological guidance recommends common-seed paired designs, whereas the Table 4 example subsequently uses a two-sample t-test. The paper first compares ten `K_P` values and then uses the same results to select the lowest observed mean, `K_P=10`, for a test against `K_P=5`. This is post-selection inference without correction for the multiplicity introduced by parameter screening. The reported `p=0.46` is therefore an exploratory illustration, not validation of an optimum or ranking. The paper also does not list the exact seeds, failed-run rules, normality diagnostics, or an independent calibration/evaluation design in the main text (paper Section 4.3, PDF pp. 26-27). The project should adopt the variance-aware principle while using independent evaluation or pre-specified comparisons and a more complete statistical protocol.

## 13. Conclusion

This paper can serve as one of the core technical and methodological references for the thesis. Its most directly reusable elements are the ALINEA reference implementation, TraCI control loop, separation of mainline and ramp-queue detectors, merge-area modelling checks, warm-up principle, realised-demand validation, common seeds, replicated experiments, and variance-aware reporting.

The correct way to use the paper is not to copy its case study, but to translate its ideas into a project-owned, reproducible experimental system centred on the sweet-spot question. ALINEA is technically compatible with the currently proposed single-ramp setting; HERO and METALINE should remain multi-ramp extensions. The paper can guide a reliable experiment, but the final network scope, metrics, parameters, replication count, and sweet-spot definition still require project-specific validation and supervisor confirmation.

## References

[1] K. Riehl, A. Kouvelas, and M. A. Makridis, “sumoITScontrol: Traffic Controller Collection for SUMO Traffic Simulations,” *SUMO Conference Proceedings*, vol. 7, 2026. Project copy: [`sumoITScontrol.pdf`](./sumoITScontrol.pdf).

[2] M. Papageorgiou, H. Hadj-Salem, J.-M. Blosseville, et al., “ALINEA: A Local Feedback Control Law for On-Ramp Metering,” *Transportation Research Record*, vol. 1320, no. 1, pp. 58-67, 1991. Cited by [1].

[3] I. Papamichail, M. Papageorgiou, V. Vong, and J. Gaffney, “Heuristic Ramp-Metering Coordination Strategy Implemented at Monash Freeway, Australia,” *Transportation Research Record*, vol. 2178, no. 1, pp. 10-20, 2010. Cited by [1].

[4] M. Papageorgiou, J.-M. Blosseville, and H. Haj-Salem, “Modelling and Real-Time Control of Traffic Flow on the Southern Part of Boulevard Périphérique in Paris: Part II: Coordinated On-Ramp Metering,” *Transportation Research Part A*, vol. 24, no. 5, pp. 361-370, 1990. Cited by [1].
