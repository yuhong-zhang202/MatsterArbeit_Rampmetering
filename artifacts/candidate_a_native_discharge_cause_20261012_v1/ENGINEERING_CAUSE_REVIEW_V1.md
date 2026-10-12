# Engineering cause review V1 — nominal two-car packet versus actual one-car discharge

Date: 2026-10-12. Scope: read-only investigation of the completed300s donor CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2 and W360 CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01. No SUMO/version invocation, test, source/parameter/guard change or new run. This report is an engineering input for independent trajectory analysis and read-only scientific review, not their replacement.

## Finding 1 — E=2 is an unqualified assumption, not measured capacity

The original [phase/rate contract](../../config/candidate_a_qualification_20261008_v1/PHASE_RATE_CONTRACT.json) explicitly labels nominal_n=2 as UNQUALIFIED_DISCHARGE_ASSUMPTION. Its phase_timing_origin states G3 was an initial short-packet engineering choice to test two-car discharge, without guaranteed startup/headway; y3 was an inherited reference, not a certified minimum. Therefore neither two vehicles per3s green nor two vehicles per3G+3y interval has been established by this contract.

[actor.py lines18–41](../../src/candidate_a_qualification_20261008/actor.py#L18) fixes nominal_n=2. [Lines76–101](../../src/candidate_a_qualification_20261008/actor.py#L76) map period=3600×nominal_n/requested_rate. At300veh/h, period=3600×2/300=24s, with3G+3y+18r. [Lines112–143](../../src/candidate_a_qualification_20261008/actor.py#L112) add nominal2 to E at each completed planned cycle, independently of actual crossings. C integrates300/3600 vehicle-equivalents each second; over72s C=6. E=3×2=6. N counts actual unique IDs and has no two-vehicle upper/lower cap. Actual N=3 is therefore a measured shortfall against an unqualified nominal packet, not evidence that SUMO lost or suppressed three known service events. Partial-cycle E must not be used to infer instantaneous discharge.

The exact arithmetic still matters: do not rewrite historical nominal_n=1 or replace E6 with measured N3 to manufacture tracking success. Each cycle supplies one observed vehicle in these runs, so the72s average150veh/h is descriptive, not a long-term service-capacity estimate.

## Finding 2 — effective green is three seconds; yellow is conditional clearance

Both frozen runs complete the same three cycles: [1200,1224),[1224,1248),[1248,1272). Effective G intervals are [1200,1203),[1224,1227),[1248,1251); y intervals [1203,1206),[1227,1230),[1251,1254); r lasts18s each. Runtime native motion prediction accounts for a transition due at the beginning of the step; a raw getter still showing the preceding color at that boundary is not an extra usable green second. The completed runtime logs record G9/y9/r54 controlled seconds and one green crossing per cycle. No fourth green was executed at1272. These are frozen actual engineering records; independent FCD/TLS/ACK audit should validate the detailed vehicle/phase alignment for the cause analysis.

SUMO1.26 pinned [MSVehicle.cpp3710–3739](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3710-L3739) checks whether braking is possible on yellow; in its eligible branch it selects the waiting velocity and waits. Yellow is not another guaranteed three seconds of discharge. This source branch is a plausible mechanism to compare with the second vehicle's actual position/speed at green end; historical recordings do not log dpi.myVLinkWait, myDistance, ignoreRed or the selected internal branch, so exact branch execution must not be asserted from trajectory similarity alone.

## Finding 3 — geometry and start-up state matter

The actual consumed network snapshot has ramp_storage_0 length204.49m/speed22.22m/s, internal :ramp_mid_0_0 length81.98m/speed25m/s, and ramp_accel_0 length99.07m/speed27.78m/s. The controlled connection is ramp_storage_0→:ramp_mid_0_0→ramp_accel_0 at ramp_mid/link0. The storage lane has no stopOffset child. Crossing N is the actual storage→internal boundary transition, not an E1 detector count far downstream.

Both raw1200 pre-state records show R_flow.0 front203.48895846490217m/speed0 and R_flow.1 front195.9879543879801m/speed0. Thus distances to lane end are1.00104153509783m and8.50204561201991m, respectively. Vehicle length5m and minGap2.5m imply the first pair's bumper gap is2.50100407692207m (front-position difference minus leader length). Both start queued; the second car is not a pre-existing moving vehicle at the stop line.

Pinned [MSVehicle.cpp125](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L125) defines an expected-priority stopping-gap reference1.0m; [lines2728–2778](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L2728-L2778) combine it with lane/type rules and braking. This supports interpreting the approximately1m stopped-front offset as consistent with native stopping behavior, not as a1m network discontinuity. It does not show that every native stop is exactly1m.

Runtime vehicle_states serialize accel2.6m/s², normalDecel4.5m/s², tau1s, actionStepLength1s, length5m and minGap2.5m at activation. The unchanged identity checks additionally require emergencyDecel9m/s², imperfection0.5, maxSpeed55.55555555555556m/s, speedMode31 and laneChangeMode1621. These checks passed through the completed run; not every queried value is separately serialized for every vehicle and step. Actual speed can be well below accel-limited motion due to following, native signal logic and stochastic imperfection. An acceleration bound is not measured acceleration, and tau1/actionStep1/timestep1 have different roles; no manual one-second reaction delay should be added without source support.

The input vType declares only id=technical_passenger and vClass=passenger. It does not explicitly select carFollowModel or write the effective model identifier into these runtime records. Existing pinned Krauss source provides a model-consistent candidate explanation, not an independently recorded per-vehicle model-selection proof. No model setting is changed or promoted to a scientifically justified default here.

## Finding 4 — WAIT observes; it does not issue a vehicle stop or speed command

[receiver_wait.py](../../src/candidate_a_native_receiver_wait_20261012/receiver_wait.py) performs only bound reads and classification. [adapter.py138–169](../../src/candidate_a_native_receiver_wait_20261012/adapter.py#L138) accepts WAIT_NATIVE_FOLLOWING inside an already active green only when the actual-speed gap observation is bound; it leaves the original hypothetical prospective available=False and reasons unchanged. The adapter has no setSpeed, slowDown, setAcceleration or setStop. [bridge.py92–138](../../src/candidate_a_native_receiver_wait_20261012/bridge.py#L92) issues only scheduled TLS program/phase changes at0/600/1200, then lets native successors operate;1224/1248 admission observes without reset. Every successful interval performs exactly one simulationStep(t+1). A WAIT label does not skip that step or shorten green.

Fresh current-speed getSecureGap is a query. At1201 the serialized R_flow.1 query uses speed0 and leader R_flow.0 speed1.3153111228020862m/s; returned secure gap0, observed gap excluding minGap1.3163151997241584m, physical bumper gap3.8163151997241584m and unchanged margin1.1m. The older observer instead queries the hypothetical speed0+2.6 and receives secure gap2.6. This explains the different classifications without proving a commanded deceleration. Native SUMO, rather than the WAIT classifier, continues to choose actual motion. No inference that WAIT caused the observed one-car count is supported by a vehicle setter or skipped-step mechanism in this code.

## Native query and model limits

Pinned [Vehicle.cpp894–929](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L894-L929) shows getSecureGap delegates to the model using the supplied speed/leader inputs; getStopSpeed calls stopSpeed with FUTURE calculation reason. The completed runs do not call or serialize getStopSpeed, so its historical result is UNKNOWN. Even a hypothetical stop-speed calculation would not identify the actual native signal/leader/random branch.

Pinned [MSVehicle.cpp3280–3305](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3280-L3305) clips planned velocity using leader-following speed. [Krauss.cpp66–107](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L66-L107) and [124–150](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L124-L150) describe speed patching/dawdling; stopSpeed also considers actionStepLength and maxNextSpeed. These mechanisms support examining queued startup and leader gap before yellow. They do not prove the exact RNG draw or uniquely separate signal, following and randomness. Cached source pin is fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3, not a new fetch. Compiled binary/source equivalence remains NOT_VERIFIED.

## Bounded interpretation and next step

Confirmed engineering conclusion: the 24s/nominal2 mapping is algebraically correct but its two-car discharge assumption remains unsupported by actual N. The execution core observes real N and preserves the deficit; WAIT does not force one car or freeze vehicles. Longer wall allowance cannot provide more simulated green time when the fixed horizon/phases are unchanged.

Candidate explanation, pending independent trajectory results: queued start-up/following uses much of the3s green; a trailing car still able to stop near green end may then wait under native yellow. Do not name short green, tau, randomness or downstream reception as the unique cause yet. Do not infer meter inability at all rates from these two same-seed, same-physics runs.

Minimum next analytical task is to compare first and second queued vehicles across each G/y transition: pre/post positions/speeds, leader gap, actual acceleration and signal/crossing bracket. Distinguish remaining movement during green from conditional yellow waiting and far-downstream merge obstruction. This can be done from existing raw, with no new API query or run. Only after those findings and scientific review should user/Chat decide whether a separately authorized service-mapping diagnostic is warranted. Possible future choices such as changing G duration or packet size are proposals, not fixes to apply now; keep the old E/N account unchanged. No guard relaxation, model/demand/timestep/phase change, added A1 proof or expanded run matrix is recommended in this task.

## Evidence and review status

Read: AGENTS, current PROJECT_STATE, DECISIONS, empty/unfrozen EXPERIMENT_PROTOCOL and relevant WORKLOG. Stage6 completed remains; Candidate A NOT_QUALIFIED, A1 UNRESOLVED and old STOP3 preserved. Source inspection plus the two consumed1200 pre-state records were read; independent complete per-cycle trajectory analysis is still the data agent's responsibility. This report is engineering-only; final mechanism conclusion awaits data and scientific review. Only this new report was written. Parent owns documentation impact/state/worklog updates.

Full raw remains in /Users/yuhongzhang/.codex/worktrees/native-receiver-wait/Masterarbeit-Ramp-Metering/data/raw/{candidate_a_native_receiver_wait_20261012_v1/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2,candidate_a_native_wait_budget_series_20261012_v1/CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01}/outputs. The exact full-precision pre-state evidence is pre_steps.jsonl at time_s1200. Already-frozen manifests and reviewed runtime receipts preserve all other frames and the unchanged snapshot network/source. No raw bytes were changed.

### Source SHA-256 (read-only bindings)

- `config/candidate_a_qualification_20261008_v1/PHASE_RATE_CONTRACT.json`: `f4af413e055e9f5d9404df0b3644c0538e7fb4cd6082b0e0722cff7740f9ec59`.
- `src/candidate_a_qualification_20261008/actor.py`: `bbfeaeb8168ed55f6001e4aec19d4e54c984aa45933a339d5c5b78479279be68`.
- `src/candidate_a_native_receiver_wait_20261012/receiver_wait.py`: `eff05b5a27f1489fab64fecd41b5e1b1a1c9dd93d3c9003a0e9add54eb99d547`.
- `src/candidate_a_native_receiver_wait_20261012/adapter.py`: `5d61726ca109b3383f7e22ae50e0f84e40149d5adfce3474ad98c9c6c890252a`.
- `src/candidate_a_native_receiver_wait_20261012/bridge.py`: `62024ded76f636a5c2b0147f73e72191243eccbfa719141aa24aea4bd7085159`.
- `artifacts/candidate_a_native_receiver_wait_20261012_v1/design/SOURCE_TRACE_V1.json`: `d375da368c84964189cce78e36f60298dff766b45d9e340165f6e113b1216582`.
- `artifacts/candidate_a_a1_contract_20261011_v1/engineering/SOURCE_EXCERPTS.json`: `1501a767c67ef8c0419e0b06f52490d56ccf95510737eacf4174a697249205bf`.
- `artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/SOURCE_EXCERPTS.json`: `7ee6d516cfb039f813d6cf6d304c0a4fa4719478e970dfc4a9ec384c9bdbf576`.
