# Remaining wall-budget technical series — V1 proposed design

## Context and authority
Stage 6 remains completed / preliminary_ready. Candidate A is NOT_QUALIFIED; A1 remains UNRESOLVED. The formal protocol is empty, so these are bounded technical runs. The explicit four-budget user goal is retained at artifacts/candidate_a_native_budget_cycles_20261012_v1/USER_GOAL_AND_STEERING_V1.json. The later independent WAIT repair was reviewed, executed once, and transplanted; it did not cancel the four-budget goal.

## Minimal implementation footprint
Create only src/candidate_a_native_wait_budget_series_20261012/profile.py, bridge.py and scripts/candidate_a_native_wait_budget_series_20261012_v1/cli.py plus two focused offline configuration checks and new engineering evidence. Reuse the receiver_wait adapter, receiver helper, actor, FrameCache, observer, watchdog, native log capture, admission and checkpoint logic byte for byte. New bridge is the 227-line reviewed WAIT bridge with ONLY its profile import changed. Profile (114-line original) changes metadata, identities, authorization paths and integer wall budgets only, and includes both original core and new wrapper hashes. No monkeypatch or safety-source changes.

## Identities and fixed conditions
CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01: 360 s.
CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W420_01: 420 s.
CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W480_01: 480 s.
All use the SAME independent worktree, input network, exact demand XML (qMain3600/qRamp900/qUrban360/qCross180), seed17, requested service300, timestep1, native G3/y3/r18 and activation1200. Mandatory durable provisional checkpoint1207, terminal1272 before the fourth green. Startup60, output300,000,000 B, free-space floor5,000,000,000 B and watchdog0.2 s unchanged. Fresh strict admission at1200/1224/1248; known danger, current-gap denial, unknown coverage, phase/model/identity mismatch or log anomaly STOP unchanged. No reruns, no additional seeds or safety proof.

## Reuse of completed 300-second observation
DIAG01_V2 supplies the completed 300 s allowance observation: one start; final1272; three cycles; loop144.796481 s, monitored-through-cleanup144.848700 s, wholeCLI145.409144 s; C=appliedC=E=6, N=3. These are different timer scopes. Reuse is justified ONLY if every common-core source hash and the route/dynamic/configuration conditions match exactly. New metadata wrappers have different hashes; disclose this rather than pretending all runs have identical whole-source SHA. Compare canonicalized scenario/additional XML after stripping only declared absolute input/output locations, not physical attributes. Require bridge text equality after the single profile-import normalization. Preserve the failed older W300 as separate historical evidence; it is not the reused completed baseline.

## Bounded workflow and evidence
First freeze this design, then two minimum offline checks: (1) exact cards/spec/resources/core/input equivalence for all three identities; (2) invalid budget and missing release must reject without output allocation or spawn. Do not rerun the11-test WAIT suite or old suites. Independent data and scientific prelaunch review required. At most three actual starts, sequential360→420→480, with engineering→data→science actual review before each next start; no automatic retry. Authorization and release generated only per identity after those gates. On new safety-source change or inability to establish core/input equality, STOP and report before native execution.

## Interpretation limits
A cap is an allowance, not a requested native duration or a reason to extend the1272 horizon. Larger allowances do not force longer runs. Same seed repetition is technical repeatability, not independent stochastic evidence. Report actual C/E/N, actual yellow/red transitions and all log/coverage scope. The smallest tested allowance that completed the fixed objective is descriptive, not statistical optimality. No service qualification, transferable safety, ALINEA effect or formal sweet spot follows. The existing CLI-only compatibility warning is retained separately from the four native log streams; absence of native messages does not mean every CLI warning is absent. SUMO compiled-binary/source equivalence remains NOT_VERIFIED.
