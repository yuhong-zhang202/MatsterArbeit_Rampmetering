"""Isolated source-scale observations; fake motion is not native validation."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from src.candidate_a_natural_service_20261015 import acceptance_safety as s, bridge, profile, budget, guardian
from src.candidate_a_natural_service_20261015.adapter import StepAdapter
from src.candidate_a_natural_service_20261015.producer import Producer
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture


def authority():
    # Synthetic constructor input, never a stored approval/release or launch.
    return dict(enabled=True,contract=s.CONTRACT,source_commit=s.SOURCE,
        status='EXACT_ACCEPTANCE_CONTRACT_AUTHORITY_VERIFIED',configured_model='Krauss',
        configured_Euler_dt_s=1,no_model_or_JM_override=True,run_id='SYNTHETIC_ONLY',
        approval_sha256='0'*64,execution_card_sha256='1'*64)


def frame(t, speed, pos, vid='any_vehicle'):
    state=dict(vehicle_id=vid,time_s=t,lane_id=s.STORAGE,type_id='technical_passenger',
        route=['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'],
        speed_mode=31,lane_change_mode=1621,speed_m_s=speed,position_m=pos,length_m=5.,
        dynamics=dict(accel=2.6,decel=4.5,emergency_decel=9.,tau=1.,action_step=1.,
                      sigma=.5,max_speed=55.55555555555556,min_gap=2.5))
    return dict(time_s=t,world_ids=[vid],lane_ids={s.STORAGE:[vid],s.INGRESS:[]},
        states={vid:state},following={vid:dict(vehicle_id=vid,time_s=t,
            status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD')},leaders={},storage_length_m=s.LENGTH,
        ingress_length_m=113.08,coverage='FRESH_COMPLETE_STORAGE_INGRESS_AND_NATIVE_LEADER')


def evidence(vid='any_vehicle', t=100):
    v=4.56232916440366; vn=v-4.501; x=203.96811645360515
    return dict(vehicle_id=vid,dt_s=1,before=frame(t,v,x,vid),after=frame(t+1,vn,x+vn,vid),
        first_yellow=True,motion='y',signal_binding='BOUND_BEFORE_LEDGER',entered_link=False,
        body_coverage_complete=True,hard_reasons=[],native_warning_text='',
        native_event_counters=dict(colliding_vehicles=0,starting_teleports=0,ending_teleports=0),
        acceleration_m_s2=-4.501,delta_m_s2=-4.501)


def export(name, value):
    if directory:=os.environ.get('ACTUATOR_SAFETY_EXPORT'):
        p=Path(directory);p.mkdir(parents=True,exist_ok=True)
        with (p/(name+'.json')).open('x') as f:json.dump(value,f,indent=2,default=bridge.encoded)


class SafetyTests(unittest.TestCase):
    def test_scale_context_neighbors_and_hard_faults(self):
        e=evidence();positive=s.classify(e)
        self.assertEqual(positive['classification'],'NUMERICAL_SCALE_COMPATIBLE')
        self.assertFalse(positive['actual_branch_identified'])
        negative=[]
        for label,change in (
            ('larger_peak',lambda x:x.update(acceleration_m_s2=-4.502,delta_m_s2=-4.502)),
            ('other_phase',lambda x:x.update(motion='G')),
            ('not_first_yellow',lambda x:x.update(first_yellow=False)),
            ('wrong_dt',lambda x:x.update(dt_s=.5)),
            ('native_warning',lambda x:x.update(native_warning_text='warning')),
            ('red_entry',lambda x:x.update(entered_link=True)),
            ('hard_fault',lambda x:x.update(hard_reasons=['RED_CROSSING'])),
            ('missing_frame',lambda x:x.pop('before')),
            ('missing_follower_coverage',lambda x:x['after'].pop('coverage')),
            ('wrong_model',lambda x:x['after']['states']['any_vehicle']['dynamics'].update(tau=2)),
            ('other_road',lambda x:x['after']['states']['any_vehicle'].update(lane_id='main_up_0'))):
            x=deepcopy(e);change(x);result=s.classify(x)
            self.assertEqual(result['decision'],'STOP',label);negative.append(dict(label=label,result=result))
        # Separate physical overlap from the stricter minGap infringement.
        for pos,reason in ((197.,'MIN_GAP_INFRINGEMENT'),(201.,'PHYSICAL_BUMPER_OVERLAP')):
            x=deepcopy(e)
            for f in (x['before'],x['after']):
                follower=deepcopy(f['states']['any_vehicle']);follower.update(vehicle_id='follower',position_m=pos)
                f['states']['follower']=follower
            result=s.classify(x);self.assertIn(reason,result['reason'])
            negative.append(dict(label=reason,result=result))
        export('pure_scale_cases',dict(classification='SYNTHETIC_NO_NATIVE_EVIDENCE',positive=positive,negative=negative))

    def test_adapter_pending_closed_repeated_episode_and_terminal(self):
        a=StepAdapter(None,acceptance_authority=authority())
        def call(e,errors=None,end=4200):
            a.last_completed=e['after']['time_s'];a.end_s=end
            p=dict(time_s=e['before']['time_s'],acceptance_safety_before=e['before'],
                   acceptance_first_yellow=e['first_yellow'],motion=e['motion'])
            row=dict(post_signal_application_binding=dict(status='BOUND_BEFORE_LEDGER'),actual_crossings=[],
                     body_observation={},native_event_counters=e['native_event_counters'],
                     braking_observation=dict(actual_acceleration_m_s2={e['vehicle_id']:e['acceleration_m_s2']},
                         speed_difference_m_s2={e['vehicle_id']:e['delta_m_s2']}))
            errors=errors if errors is not None else ['ORDINARY_BRAKING_EXCEEDED:'+e['vehicle_id'],
                                                    'UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+e['vehicle_id']]
            with patch.object(s,'observe_frame',return_value=e['after']):
                return a._acceptance_observation(None,p,row,errors,'')
        first=call(evidence());self.assertFalse(first['remaining_reasons']);self.assertIsNotNone(a.acceptance_followup)
        pending=call(evidence(t=101));self.assertIn('ACCEPTANCE_FOLLOWUP_NOT_CLOSED',pending['remaining_reasons'])
        # Close with a genuinely observed no-excess next frame; no lifetime ban.
        close=evidence(t=101);close.update(acceleration_m_s2=0,delta_m_s2=0)
        closed=call(close,errors=[]);self.assertIsNone(a.acceptance_followup)
        self.assertEqual(closed['classifications'][0]['decision'],'CLOSED')
        second=call(evidence(t=200));self.assertFalse(second['remaining_reasons'])
        self.assertEqual(len(a.acceptance_episodes),2)
        a.acceptance_followup=None
        terminal=call(evidence(t=300),end=301)
        self.assertIn('ACCEPTANCE_EOF_FOLLOWUP_NOT_OBSERVED',terminal['remaining_reasons'])
        dormant=StepAdapter(None)
        result=dormant._acceptance_observation(None,{}, {}, ['ORDINARY_BRAKING_EXCEEDED:any_vehicle'],'')
        self.assertEqual(result['remaining_reasons'],['ORDINARY_BRAKING_EXCEEDED:any_vehicle'])
        for invalid in ({}, {'enabled':True}, {**authority(),'source_commit':'wrong'}):
            with self.assertRaisesRegex(ValueError,'ACCEPTANCE_CONTRACT_NOT_AUTHORIZED'):
                StepAdapter(None,acceptance_authority=invalid)
        export('adapter_episode_cases',dict(first=first,pending=pending,closed=closed,
            second=second,terminal=terminal,dormant=result,classification='SYNTHETIC_NO_NATIVE_EVIDENCE'))

    def test_real_fake_loop_default_stop_and_optin_one_step_followup(self):
        spec=importlib.util.spec_from_file_location('acceptance_natural_fixture',
            profile.ROOT/'tests/candidate_a_natural_service_20261015/test_natural.py')
        fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
        class World(fixture.NaturalWorld):
            def __init__(self,xml):
                super().__init__(xml,case='empty')
                self.vehicle.getAcceleration=lambda v:-4.501 if v=='R_flow.0' and self.time==605 else 0.
                self.vehicle.getLanePosition=self.position
                self.vehicle.getLeader=lambda v,d:None
            def position(self,vid):
                if vid=='R_flow.0':
                    return (203.96811645360515-(604-self.time)*4.56232916440366 if self.time<=604
                            else 204.0294456180088)
                return super().position(vid)
            def simulationStep(self,end):
                super().simulationStep(end)
                if end==601:self.departed=['R_flow.0']
                if end>=601:self.vspeed['R_flow.0']=4.56232916440366 if end<=604 else .06132916440366 if end==605 else .06132916440366
        saved=[]
        for active in (False,True):
            with tempfile.TemporaryDirectory() as tmp:
                package=Path(tmp)/'pkg';out=Path(tmp)/'out'
                profile.stage_package(profile.ROOT,package,out,610);out.mkdir()
                w=World(package/'scenario.add.xml')
                a=StepAdapter(w.observe,end_s=610,yellow_diagnostic_mode=True,
                    acceptance_authority=authority() if active else None,
                    acceptance_observation_mode=active)
                cap=LogCapture(out);worker=bridge.protected_worker();error=None
                try:
                    bridge._diagnostic_loop(w,NS(observe=w.observe,request_phase=worker.request_phase),cap,out,
                        dict(wall_limit_s=300,run_limit_bytes=None,minimum_free_bytes=0),
                        fixture.old.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,Producer())
                except Exception as exc:error=type(exc).__name__+':'+str(exc)
                finally:cap.close_handles()
                logs={p.name:[json.loads(x) for x in p.read_text().splitlines()]
                      for p in out.glob('*.jsonl') if p.name in ('pre_steps.jsonl','post_steps.jsonl','step_ack.jsonl','control_setters.jsonl')}
                record=dict(active=active,error=error,last_completed_s=a.last_completed,
                    last_accounted_s=a.last_end,episodes=a.acceptance_episodes,logs=logs,
                    classification='FAKE_LOOP_NO_NATIVE_PHYSICS_OR_SAFETY_EVIDENCE')
                export('loop_'+str(active),record);saved.append(record)
                if active:
                    self.assertIsNone(error)
                    self.assertEqual(a.last_completed,610)
                    self.assertEqual(a.acceptance_episodes[0]['followup']['decision'],'CLOSED')
                    event=next(x for x in a.receipts if x['time_end_s']==605)
                    self.assertTrue(event['legacy_braking_reasons'])
                    self.assertFalse(event['safety_acceptance']['remaining_reasons'])
                else:
                    self.assertIn('ORDINARY_BRAKING_EXCEEDED:R_flow.0',error)
                    self.assertEqual(a.last_completed,605)

    def test_exact_authority_resource_and_guardian_identity_fail_closed(self):
        import hashlib
        resources=dict(wall_limit_s=641,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000)
        bound=dict(start_count=2,unknown_reserved=[],remaining_s=641.1262059589499)
        with self.assertRaisesRegex(ValueError,'START_CAP'):
            budget.effective_limits(resources,bound)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();task,_=profile.paths_for_run(profile.ACCEPTANCE_RUN)
            card_path=root/task/'packages_v1'/profile.ACCEPTANCE_RUN/'card.json'
            card_path.parent.mkdir(parents=True)
            card=dict(spec=profile.acceptance_spec(),environment=dict(
                python='.'.join(map(str,__import__('sys').version_info[:3])),files_sha256={}))
            card_path.write_text(json.dumps(card));card_sha=profile.sha(card_path)
            approval=root/'synthetic_authority.json'
            a=dict(status='DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION',run_id=profile.ACCEPTANCE_RUN,
                   card_sha256=card_sha,lifts_current_no_SUMO_restriction=True)
            release={}
            def save():
                approval.write_text(json.dumps(a))
                release['direct_execution_authority']=dict(path='synthetic_authority.json',sha256=profile.sha(approval))
            save()
            with self.assertRaisesRegex(ValueError,'CONTRACT_AND_START_NOT_APPROVED'):
                s.runtime_authority(card,card_path,release,root)
            # The real release gate must reject this legacy-style approval
            # before worker context or any raw/worker/native allocation.
            user=root/profile.ACCEPTANCE_USER;user.parent.mkdir(parents=True,exist_ok=True);user.write_text('SYNTHETIC NONEXECUTING TEST ONLY')
            release.update(status='CANONICAL_NATURAL_EXECUTION_RELEASE',card_sha256=card_sha,
                budget_approval_sha256='a'*64,reviews={role:dict(path='synthetic_authority.json',sha256=profile.sha(approval))
                    for role in ('engineering','data','science')},
                user_authority=dict(path=str(profile.ACCEPTANCE_USER),sha256=profile.sha(user)))
            rejected_release=root/'synthetic_rejected_release.json';rejected_release.write_text(json.dumps(release))
            with patch.object(profile,'validate_prepared',return_value=card),\
                 patch.object(budget,'accounting',return_value={**bound,'budget_approval_sha256':'a'*64}),\
                 patch.object(guardian,'require_worker_context') as worker_gate:
                with self.assertRaisesRegex(ValueError,'CONTRACT_AND_START_NOT_APPROVED'):
                    profile.validate_release(card_path,rejected_release,root)
                worker_gate.assert_not_called()
            self.assertFalse((root/profile.RAW).exists())
            a.update(acceptance_contract_approved=s.CONTRACT,additional_exact_single_start_approved=True,
                accuracy_criteria_approved=card['spec']['accuracy_acceptance_contract']['policy'],
                acceptance_standard_sha256=card['spec']['safety_acceptance_contract']['standard_sha256']);save()
            auth=s.runtime_authority(card,card_path,release,root)
            self.assertEqual(budget.effective_limits(resources,bound,auth)['wall_limit_s'],611)
            for key,value in (('card_sha256','f'*64),('run_id',profile.RUN),
                              ('accuracy_criteria_approved','wrong'),('acceptance_standard_sha256','f'*64),
                              ('additional_exact_single_start_approved',False)):
                old=a[key];a[key]=value;save()
                with self.assertRaisesRegex(ValueError,'CONTRACT_AND_START_NOT_APPROVED'):
                    s.runtime_authority(card,card_path,release,root)
                a[key]=old
            save()
            for b in ({**bound,'unknown_reserved':['unsettled']},{**bound,'start_count':3}):
                with self.assertRaisesRegex(ValueError,'THIRD_EXACT_START'):
                    budget.effective_limits(resources,b,auth)
            with self.assertRaisesRegex(ValueError,'THIRD_EXACT_START'):
                budget.effective_limits({**resources,'wall_limit_s':642},bound,auth)
            # Exercise real identity routing without spawning any process.
            context=root/task/'runs'/profile.ACCEPTANCE_RUN/'guardian_context.json'
            context.parent.mkdir(parents=True);release_path=root/'synthetic_release.json'
            release_path.write_text(json.dumps(release));token='synthetic_unusable_token'
            record=dict(run_id=profile.ACCEPTANCE_RUN,guardian_pid=os.getppid(),
                token_sha256=hashlib.sha256(token.encode()).hexdigest(),
                card_sha256=card_sha,release_sha256=profile.sha(release_path))
            context.write_text(json.dumps(record))
            with patch.dict(os.environ,{guardian.CONTEXT_ENV:str(context),guardian.TOKEN_ENV:token}),\
                 patch.object(guardian,'identity',return_value=dict(status='OBSERVED',pid=7,pgid=7,sid=7)):
                self.assertEqual(guardian.require_worker_context(card_path,release_path,root)['run_id'],profile.ACCEPTANCE_RUN)
                record['run_id']=profile.RUN;context.write_text(json.dumps(record))
                with self.assertRaisesRegex(ValueError,'GUARDIAN_BINDING_MISMATCH'):
                    guardian.require_worker_context(card_path,release_path,root)
            self.assertFalse((root/profile.RAW).exists())
            # Proposed preparation is separate from activation, with 641/611.
            self.assertEqual(card['spec']['safety_acceptance_contract']['status'],'PROPOSED_DEFAULT_INACTIVE')
            self.assertEqual(profile.paths_for_run(profile.RUN)[0],profile.TASK)
        registration=profile.acceptance_registration(profile.ROOT)
        geometry=registration['opportunity_geometry']
        self.assertEqual(registration['run_id'],profile.ACCEPTANCE_RUN)
        self.assertEqual(geometry['network_sha256'],profile.sha(profile.ROOT/profile.NETWORK))
        self.assertEqual(set(geometry['receiver_geometry_m']),set(s.RECEIVER_LANES))
        self.assertEqual(geometry['lane_domains'],[dict(lane_id=s.STORAGE,start_pos_m=184.49,end_pos_m=204.49)])
        self.assertEqual(set(registration),{'run_id','opportunity_geometry'})
        self.assertNotIn('card_sha256',json.dumps(registration))
        self.assertNotIn('manifest',json.dumps(registration))


if __name__=='__main__':unittest.main()
