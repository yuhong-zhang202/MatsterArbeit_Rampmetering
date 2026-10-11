# PR #9 phase-type red-evidence correction — V6

2026-10-11. User-authorized repair on original Draft PR #9 from a41bf0fc57cb9aa971ac42bad191219c13d98d2e. Reviewer P2: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/9#discussion_r4241992993 . No new Issue.

## Scope and semantics
Previous equality check allowed bool True and float1.0 to equal integer1. With valid nonempty red IDs, this misclassified synthetic evidence as INELIGIBLE/OBSERVED_RED_ANOMALY. V6 requires exact non-boolean integer phase_before before checking phase1. Invalid type/value yields UNKNOWN with PHASE_MISMATCH and no red anomaly. Integer1 bound positive/empty controls and prior mode/dynamics policy behavior remain. No ELIGIBLE path. Exact Python int is consistent with JSON integer representation; no coercion.

Only isolated diagnostic/audit binding/checker/tests change. Normative A1/A2 safety contract, native helpers/mathematics, production guard/actor/config, raw, research design and upstream PRs unchanged. Exact V5 source/binder/checker, actual pre-fix counterexamples and old results retained. Prior V5 PASS did not cover malformed phase types; that scope is superseded by V6, not retrospectively rewritten.

## Evidence and verification
Engineering receipts, input SHA-256 bindings and exact prior snapshot in [V6](v6/ENGINEERING_REVIEW_V6.md); independent data review in [processed V5](../../../data/processed/candidate_a_a1_contract_20261011_v5/DATA_REVIEW_PHASE_P2.md). Engineering43/43 methods PASS (2new methods/24phase subcases); independent38newphase+53oldmode/red+19schema+10numericprobes PASS and publicauditPASS. Full commands/environment/source/input hashes in receipts. Actual delivered-code cleancheckout pending. These are synthetic/offline checks, not new traffic or native red observations.

42 saved witnesses remain (27storage/15ingress), conditionalcanBrake42/42, actual full native branch0/42, refused-red observations0. Sixwindows [6,0,0,0,0,0], firstpartial C/appliedC=.5/E0/N1, fiveunobserved null/blank,0completecycles;536protectedfiles unchanged. Publicaudit binds committed receipts/excerpts and derived thin ledger, not complete ignoredraw reconstruction/native provenance.

## State and handoff
A1 UNRESOLVED_NEEDS_EVIDENCE/NOT_IMPLEMENTABLE_YET and A1/A2 unverified; STOP3/NOT_QUALIFIED/HOLD/highestqualifiedrateunknown/900NOT_TESTED remain. Stage6 prior closeout stays; formalprotocol empty/unfrozen. SUMO/TraCI starts0. Complete future vehicle coverage, native branch/event authentication and joint braking/follower/receiver bounds remain unproved. Bounded correction PASS does not qualify actuator or authorize execution. Next user/Chat reviews original Draft; suggestions are not execution authorization.
