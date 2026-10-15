"""Independent math/join checks over saved engineering synthetic records only."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import tempfile
import hashlib
from scripts.natural_actuator_qualification_20261015_v1.episode import EpisodeAudit,RUN,CONTRACT,SOURCE

from scripts.natural_actuator_qualification_20261015_v1.provenance import safety_acceptance_proof,resource_card

FIXTURE=Path(__file__).resolve().parent/'fixtures/actuator_acceptance_episode_v1.json'


def rows():
    saved=json.loads(FIXTURE.read_text())
    assert saved['classification']=='SYNTHETIC_NO_NATIVE_TRAFFIC_OR_SAFETY_EVIDENCE'
    selected={s['time_begin_s']:s for s in saved['steps']}
    pairs=[]
    authority=deepcopy(selected[604]['post']['safety_acceptance']['authority_binding']);authority['run_id']=RUN
    for t in (604,605):
        p=deepcopy(selected[t]['pre']['bound_snapshot']);r=deepcopy(selected[t]['post']);r['safety_acceptance']['authority_binding']=deepcopy(authority)
        # Saved fake source has no native FCD. This test projection is explicitly
        # synthetic; the real scan supplies its independently checked FCD frame.
        f=r['safety_acceptance']['after_frame'];fcd={vid:dict(lane=x['lane_id'],pos=str(x['position_m']),speed=str(x['speed_m_s'])) for vid,x in f['states'].items()}
        for x in f['leaders'].values():
            if x is not None:fcd[x['vehicle_id']]=dict(lane=x['lane_id'],pos=str(x['position_m']),speed=str(x['speed_m_s']))
        pairs.append((p,r,dict(green_end_s=604),p['world'],r['post_world'],fcd))
    return authority,pairs


class EpisodeReaderTests(unittest.TestCase):
    def test_candidate_one_step_closed_legacy_retained_and_eof_pending(self):
        authority,pairs=rows();audit=EpisodeAudit(authority)
        self.assertEqual(audit.step(*pairs[0]),{'R_flow.0'})
        self.assertEqual(pairs[0][1]['braking_observation']['actual_acceleration_m_s2']['R_flow.0'],-4.501)
        with self.assertRaisesRegex(ValueError,'EOF_PENDING'):audit.finish()
        self.assertEqual(audit.step(*pairs[1]),set())
        observations=audit.finish(registry=json.loads(FIXTURE.read_text())['episodes']);self.assertEqual(observations[0]['closure_ACK'],606)
        self.assertFalse(observations[0]['native_safety_proven'])
        self.assertEqual(observations[0]['recomputed_candidates'][0]['acceleration_m_s2'],-4.501)
        self.assertEqual(len(observations[0]['legacy_braking_reasons']),2)
        with self.assertRaises(ValueError):audit.finish(registry=[])

    def test_mutated_math_first_yellow_or_other_hard_risk_rejected(self):
        for mutation in ('delta','first_yellow','collision','warning','other_vehicle','position','summary'):
            with self.subTest(mutation=mutation):
                authority,pairs=rows();p,r,cycle,w,z,fcd=pairs[0]
                if mutation=='delta':r['braking_observation']['actual_acceleration_m_s2']['R_flow.0']=-4.502
                if mutation=='first_yellow':cycle['green_end_s']=603
                if mutation=='collision':r['native_event_counters']['colliding_vehicles']=1
                if mutation=='warning':r['warning_observation']['text']='emergency braking'
                if mutation=='other_vehicle':r['braking_observation']['actual_acceleration_m_s2']['M_flow.0']=-6.
                if mutation=='position':fcd['R_flow.0']['pos']='100'
                if mutation=='summary':r['safety_acceptance']['classifications'][0]['arithmetic']['predicted_speed_m_s']=10.
                with self.assertRaises(ValueError):EpisodeAudit(authority).step(p,r,cycle,w,z,fcd)

    def test_followup_hard_fault_missing_or_wrong_authority_rejected(self):
        authority,pairs=rows()
        for mutation in ('hard','missing_vehicle','time'):
            with self.subTest(mutation=mutation):
                current=deepcopy(pairs);audit=EpisodeAudit(authority);audit.step(*current[0]);r=current[1][1]
                if mutation=='hard':r['braking_observation']['actual_acceleration_m_s2']['R_flow.0']=-4.501
                if mutation=='missing_vehicle':r['safety_acceptance']['after_frame']['states'].pop('R_flow.0')
                if mutation=='time':r['time_begin_s']=606
                with self.assertRaises(ValueError):audit.step(*current[1])
        authority['run_id']='QUAL_NATURAL_ALINEA_R900_S17_02'
        with self.assertRaises(ValueError):EpisodeAudit(authority)
        with self.assertRaises(ValueError):EpisodeAudit().step(*pairs[0])

    def test_exact_new_card_authority_and_fixed_resource_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);standard=root/'docs/development/ACTUATOR_ACCEPTANCE_CRITERIA.md';standard.parent.mkdir(parents=True);standard.write_text('SYNTHETIC STANDARD UNIT FIXTURE')
            h=hashlib.sha256(standard.read_bytes()).hexdigest()
            item=dict(policy=CONTRACT,status='PROPOSED_DEFAULT_INACTIVE',source_commit=SOURCE,configured_model='Krauss',configured_Euler_dt_s=1,
                no_model_or_JM_override=True,standard='docs/development/ACTUATOR_ACCEPTANCE_CRITERIA.md',standard_sha256=h,
                classification='NUMERICAL_SCALE_COMPATIBLE_NOT_CONFIRMED_NUMERIC',followup='ONE_UNCHANGED_STEP_REQUIRED_NO_RENEWAL_WHILE_PENDING')
            card=dict(spec=dict(run_id=RUN,safety_acceptance_contract=item,
                accuracy_acceptance_contract=dict(policy='PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1',status='PROPOSED_PENDING_EXACT_CARD_APPROVAL',
                evaluator='scripts/actuator_acceptance_20261015_v1/accuracy.py',normalizer='scripts/actuator_acceptance_20261015_v1/normalize.py',absolute_bound_vehicles=2,relative_bound=.05,formal_experiment_authorized=False),
                acceptance_observation_contract=dict(policy='FIXED_RECEIVER_DOMAIN_AND_LOCAL20_V1',local_storage_domain_m=[184.49,204.49],minimum_actual_R_fronts=2,
                receiver_lanes=[':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2'],cause='UNESTABLISHED_UNLESS_SEPARATELY_BOUND')))
            approval=dict(status='DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION',run_id=RUN,card_sha256='a'*64,lifts_current_no_SUMO_restriction=True,
                acceptance_contract_approved=CONTRACT,accuracy_criteria_approved='PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1',acceptance_standard_sha256=h,additional_exact_single_start_approved=True)
            proof=safety_acceptance_proof(card,approval,'a'*64,'b'*64,root);self.assertEqual(proof['run_id'],RUN)
            for key in ('acceptance_contract_approved','accuracy_criteria_approved','additional_exact_single_start_approved','acceptance_standard_sha256'):
                broken=deepcopy(approval);broken.pop(key)
                with self.assertRaises((ValueError,KeyError)):safety_acceptance_proof(card,broken,'a'*64,'b'*64,root)
            budget=root/'artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json';budget.parent.mkdir(parents=True);budget.write_text('SYNTHETIC BUDGET UNIT FIXTURE')
            card.update(resources=dict(wall_limit_s=641,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000),
                resources_status='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL',guardian=dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',inner_wall_limit_s=611,cleanup_reserve_s=30,outer_wall_limit_s=641,
                receipt=f'data/raw/natural_actuator_qualification_20261015_v1/{RUN}/guardian_receipt.json',fallback_receipt=f'artifacts/actuator_acceptance_20261015_v1/engineering/runs/{RUN}/guardian_receipt.json'),
                resources_scope=dict(scope_id='NATURAL_QUALIFICATION_20261015_V1',approved_total_monitored_s=900,charged_before_preparation_s=258.87379404105013,
                remaining_before_preparation_s=900-258.87379404105013,start_count_before_preparation=2,unknown_reserved_before_preparation=[],budget_approval_sha256=hashlib.sha256(budget.read_bytes()).hexdigest(),
                old_scope_available_not_pooled=True,current_identity_ordinal=3,additional_exact_single_start_status='PROPOSED_NOT_APPROVED',max_prepared_new_identities=1,further_identity_prepared=False))
            self.assertEqual(resource_card(card,root)['outer_wall_limit_s'],641)
            card['resources']['wall_limit_s']=642
            with self.assertRaises(ValueError):resource_card(card,root)


if __name__=='__main__':unittest.main()
