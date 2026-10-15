"""Tiny hand-built journal-schema records, never SUMO or old-run evaluation."""
from copy import deepcopy
import unittest
import tempfile
import subprocess
import sys
import json
from pathlib import Path
from scripts.actuator_acceptance_20261015_v1.normalize import normalize,project_window,digest,source_ref
from scripts.natural_actuator_qualification_20261015_v1.streaming import pre_position_binding
from scripts.actuator_acceptance_20261015_v1.accuracy import LOCAL_DOMAIN,evaluate

LANES=[':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2']
REF={'path':'synthetic_projection','sha256':'a'*64}


def bind_positions(f):
    q=f['pre']['bound_snapshot'];allstates={v['vehicle_id']:dict(v,lane_id='ramp_storage_0') for v in q['vehicle_states']}
    allstates.update(q.get('receiver_domain_observation',{}).get('vehicles',{}))
    q['terminal_before']={vid:deepcopy(x) for vid,x in allstates.items()}
    same_ack_fcd={vid:dict(lane=x['lane_id'],pos=str(x['position_m']),speed=str(x['speed_m_s'])) for vid,x in allstates.items()}
    f['position_proof']=pre_position_binding(q,same_ack_fcd,f['time_s']);return f


def frame(t):
    states=[dict(vehicle_id='R_flow.'+str(i),population='storage',position_m=200-i*8,
                 speed_m_s=0.,length_m=5.,min_gap_m=2.5,type_id='technical_passenger') for i in range(2)]
    world={v['vehicle_id']:dict(role='R',lane_id='ramp_storage_0',speed_m_s=0.) for v in states}
    q=dict(time_s=t,motion='G',world=world,storage=list(world),vehicle_states=states,receiver=dict(available=True),
           entry_following_before={'R_flow.0':dict(time_s=t,status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',receiver_path_lanes=LANES)},
           receiver_domain_observation=dict(time_s=t,scope='FRESH_COMPLETE_FIXED_RECEIVER_LANES',
               ids_by_lane={l:[] for l in LANES},vehicles={},geometry_m={l:100. for l in LANES}))
    identity=dict(time_s=t,stage='BEFORE_MOTION',active_ids=list(world),vehicle_states={vid:dict(type_id='technical_passenger',route=['ramp_storage','ramp_accel']) for vid in world})
    return bind_positions(dict(time_s=t,pre=dict(time_s=t,bound_snapshot=q),identity=identity,
                ack=[dict(requested_target_s=t+1,ACK_received=True,actual_readback_s=None,actual_time_verified=False),
                     dict(requested_target_s=t+1,ACK_received=True,actual_readback_s=t+1,actual_time_verified=True)],refs=dict(pre_line=t+1)))


def fixture():
    geometry=dict(source=deepcopy(REF),lane_domains=deepcopy(LOCAL_DOMAIN),network_sha256='a'*64,
        receiver_domain_source=deepcopy(REF),receiver_lane_ids=LANES,receiver_geometry_m={l:100. for l in LANES})
    sources={k:dict(path='synthetic/'+k,sha256='a'*64) for k in ('reader','pre','ack','identity','registration','card','manifest')}
    card=dict(prepared_input_sha256={'synthetic/registration':'a'*64},spec=dict(run_id='SYNTHETIC'),sources_sha256={'reader.py':'b'*64},network_sha256='a'*64)
    card['common_runtime_source_sha256']=digest(card['sources_sha256'])
    registration=dict(run_id='SYNTHETIC',opportunity_geometry=geometry)
    reader=dict(run_id='SYNTHETIC',status='UNKNOWN_INCOMPLETE_EVIDENCE',reader_version=dict(current_source_closure_sha256={'reader.py':'b'*64}),
        domains=dict(provenance=dict(status='PASS_NATIVE_HASH_PROVENANCE',card_sha256='a'*64,manifest_sha256='a'*64),
                     native_stream_joins=dict(status='PASS_JOIN_INTEGRITY',entries=[],independent_physical_N=0),
                     accounting=dict(status='PASS_INDEPENDENT_NATIVE_ACCOUNTING')),
        observed_prefix=dict(last_ACK=604),native_terminal_evidence=dict(command_records={
            'pending':dict(status='PENDING',command=dict(global_request_s=603),first_application_s=None)}),per_step_accounting=[])
    for t in range(600,604):
        v=str((t-599))+'/4'
        reader['per_step_accounting'].append(dict(time_begin_s=t,accounting=dict(C_exact_fraction=v,C_selected_exact_fraction=v,
            C_applied_exact_fraction=v,E_scheduled_nominal=0,E_executed_nominal=0,N=0)))
    manifest=dict(run_id='SYNTHETIC',files={sources[k]['path']:{'sha256':sources[k]['sha256']} for k in ('pre','ack','identity')})
    frames=[frame(t) for t in range(600,604)]
    reader['domains']['pre_position_observations']=dict(rows=[f['position_proof'] for f in frames])
    return reader,frames,registration,sources,card,manifest


class NormalizeTests(unittest.TestCase):
    def test_exact_small_actual_schema_to_seven_supports(self):
        args=fixture();result=normalize(*args)
        self.assertEqual(len(result['windows']),7)
        self.assertIsNone(result['windows'][0]['C'])
        self.assertEqual(result['windows'][-1]['C'],'1')
        self.assertEqual(result['windows'][-1]['N'],'0')
        self.assertEqual(result['windows'][-1]['observed_seconds'],4)
        self.assertTrue(result['windows'][-1]['partial'])
        self.assertEqual(len(result['windows'][-1]['pending']),1)
        self.assertEqual(result['original_reader_status'],'UNKNOWN_INCOMPLETE_EVIDENCE')
        self.assertEqual(evaluate(result)['conditional_accuracy'],'NOT_TESTED')
        evidence=project_window(args[1],600,604,args[2]['opportunity_geometry'],args[3]['pre'])
        self.assertEqual(evidence['minimum_ordered_R_count'],2)
        self.assertFalse(evidence['classification_unknown'])
        self.assertEqual(evidence['frame_evidence'][0]['local_R'][0]['vehicle_id'],'R_flow.0')
        f=deepcopy(args[1][0]);q=f['pre']['bound_snapshot']
        previous={vid:dict(lane='ramp_storage_0',pos=str(v['position_m']),speed=str(v['speed_m_s'])) for vid,v in q['terminal_before'].items()}
        q['vehicle_states'][0]['position_m']=180.;q['terminal_before']['R_flow.0']['position_m']=180.
        proof=pre_position_binding(q,previous,600)
        self.assertEqual(proof['FCD_XML_time_s'],599)
        self.assertIn('R_flow.0',proof['unknown'])

    def test_missing_fields_coverage_and_no_available_shortcut(self):
        args=fixture()
        for mutation in ('length','ACK','identity','receiver_domain','far_second','unbound_position','missing_same_ack_fcd'):
            with self.subTest(mutation=mutation):
                frames=deepcopy(args[1]);q=frames[0]['pre']['bound_snapshot']
                if mutation=='length':del q['vehicle_states'][0]['length_m']
                if mutation=='ACK':frames[0]['ack'].pop()
                if mutation=='identity':frames[0]['identity']['active_ids'].pop()
                if mutation=='receiver_domain':del q['receiver_domain_observation']
                if mutation=='far_second':q['vehicle_states'][1]['position_m']=180.;bind_positions(frames[0])
                if mutation=='unbound_position':q['vehicle_states'][1]['position_m']=180.
                if mutation=='missing_same_ack_fcd':frames[0]['position_proof']=pre_position_binding(q,None,frames[0]['time_s'])
                e=project_window(frames,600,604,args[2]['opportunity_geometry'],args[3]['pre'])
                if mutation=='far_second':self.assertEqual(e['minimum_ordered_R_count'],1)
                else:self.assertTrue(e['classification_unknown'])
                self.assertEqual(e['external_blockers'],[])

    def test_retained_legacy_shape_front_only_and_passive_deficit(self):
        # Actual1261 legacy field shape/values; reduced identities are a unit
        # fixture, new full-domain observation is synthetic, NOT run02 evidence.
        args=fixture();f=frame(1261);q=f['pre']['bound_snapshot']
        q['vehicle_states'][0].update(position_m=203.96811645360515,speed_m_s=4.56232916440366)
        q['vehicle_states'][1].update(position_m=190.80202907034123,speed_m_s=1.7229852385502331)
        for x in q['vehicle_states']:q['world'][x['vehicle_id']]['speed_m_s']=x['speed_m_s']
        q['receiver']['front_id']='R_flow.0';bind_positions(f)
        q['entry_following_before']['R_flow.1']=dict(time_s=1261,status='STOP_CURRENT_GAP_BOUND_DENIED',
            leader_id='R_flow.0',receiver_path_lanes=LANES)
        # The rear vehicle's leader in storage must NOT be forced into receiver.
        e=project_window([f],1261,1262,args[2]['opportunity_geometry'],args[3]['pre'])
        self.assertFalse(e['classification_unknown'])
        saved_queries=deepcopy(q['entry_following_before'])
        q['motion']='r';q['entry_following_before']={}
        red=project_window([f],1261,1262,args[2]['opportunity_geometry'],args[3]['pre'])
        self.assertFalse(red['classification_unknown'])
        self.assertEqual(red['frame_evidence'][0]['current_query_scope'],'NOT_SAMPLED_DURING_RED_FULL_FINITE_DOMAIN_RETAINED')
        q['motion']='G';q['entry_following_before']=saved_queries
        front=q['entry_following_before']['R_flow.0'];front.update(status='STOP_CURRENT_GAP_BOUND_DENIED',
            leader_id='M_flow.0',gap_excluding_minGap_m=1.,actual_secure_gap_m=2.)
        q['world']['M_flow.0']=dict(role='M',lane_id=LANES[0],speed_m_s=0.)
        f['identity']['active_ids'].append('M_flow.0')
        f['identity']['vehicle_states']['M_flow.0']=dict(type_id='technical_passenger',route=['main_down'])
        domain=q['receiver_domain_observation'];domain['ids_by_lane'][LANES[0]]=['M_flow.0']
        domain['vehicles']['M_flow.0']=dict(lane_id=LANES[0],position_m=20.,speed_m_s=0.,length_m=5.,route=['main_down'],type_id='technical_passenger')
        q['receiver']['available']=False;bind_positions(f)
        e=project_window([f],1261,1262,args[2]['opportunity_geometry'],args[3]['pre'])
        self.assertFalse(e['classification_unknown'])
        self.assertTrue(e['frame_evidence'][0]['passive_reference_below_observed'])
        self.assertEqual(e['external_blockers'],[])  # M role never proves cause.
        del q['receiver_domain_observation']
        self.assertTrue(project_window([f],1261,1262,args[2]['opportunity_geometry'],args[3]['pre'])['classification_unknown'])

    def test_real_file_hash_cli_has_no_registration_self_hash(self):
        args=fixture();reader,frames,registration,_,card,_=args
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            def save(name,obj):
                p=base/name;p.write_text(json.dumps(obj));return p
            pre=base/'pre.jsonl';ack=base/'ack.jsonl';identity=base/'identity.jsonl'
            pre.write_text(''.join(json.dumps(f['pre'])+'\n' for f in frames))
            ack.write_text(''.join(json.dumps(a)+'\n' for f in frames for a in f['ack']))
            identity.write_text(''.join(json.dumps(f['identity'])+'\n' for f in frames))
            regpath=save('registration.json',registration)
            card['prepared_input_sha256']={str(regpath):source_ref(regpath)['sha256']}
            cardpath=save('card.json',card)
            manifest=dict(run_id='SYNTHETIC',files={str(p):dict(sha256=source_ref(p)['sha256']) for p in (pre,ack,identity)})
            manifestpath=save('manifest.json',manifest)
            reader['domains']['provenance'].update(card_sha256=source_ref(cardpath)['sha256'],manifest_sha256=source_ref(manifestpath)['sha256'])
            readerpath=save('reader.json',reader);out=base/'normalized.json'
            cmd=[sys.executable,'-m','scripts.actuator_acceptance_20261015_v1.normalize']
            for key,path in dict(reader=readerpath,pre=pre,ack=ack,identity=identity,registration=regpath,card=cardpath,manifest=manifestpath,out=out).items():cmd+=['--'+key,str(path)]
            completed=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(completed.returncode,0,completed.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(result['identity']['preregistration_sha256'],source_ref(regpath)['sha256'])
            self.assertEqual(result['identity']['raw_manifest_sha256'],source_ref(manifestpath)['sha256'])
            self.assertNotIn('identity',registration)
            self.assertEqual(result['windows'][-1]['C'],'1')
            self.assertEqual(result['qualification'],'NO_QUALIFICATION_VERDICT')

    def test_misbound_input_and_physical_count_rejected(self):
        for mutation in ('manifest','card','N','duplicate','registration'):
            with self.subTest(mutation=mutation):
                args=list(fixture())
                if mutation=='registration':args[4]['prepared_input_sha256']['synthetic/registration']='c'*64
                if mutation=='manifest':args[5]['files']['synthetic/pre']['sha256']='c'*64
                if mutation=='card':args[4]['sources_sha256']['reader.py']='c'*64
                if mutation=='N':args[0]['per_step_accounting'][-1]['accounting']['N']=1
                if mutation=='duplicate':args[1].append(deepcopy(args[1][-1]))
                with self.assertRaises(ValueError):normalize(*args)


if __name__=='__main__':unittest.main()
