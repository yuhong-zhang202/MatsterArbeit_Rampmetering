"""Independent observed source-scale episode audit, exact future run03 only.

No runtime classifier import and no motion authority. Every legacy braking peak
is retained; only a fully bound candidate and its next observed step can be
reported separately from other alarms.
"""
import math
from copy import deepcopy
from scripts.natural_service_audit_20261015_v1.actual import need,near

CONTRACT='FIRST_YELLOW_SOURCE_SCALE_OBSERVATION_V1'
RUN='QUAL_NATURAL_ALINEA_R900_S17_03'
SOURCE='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
LOCAL=('ramp_storage_0',':urban_diverge_1_0')
DYNAMICS=dict(accel=2.6,decel=4.5,emergency_decel=9.,tau=1.,action_step=1.,sigma=.5,max_speed=55.55555555555556,min_gap=2.5)


def numeric(x):return type(x) in (int,float) and math.isfinite(x)


def frame_check(f,t,world,metadata,fcd=None):
    need(f['time_s']==t and set(f['world_ids'])==set(world) and
         f['coverage']=='FRESH_COMPLETE_STORAGE_INGRESS_AND_NATIVE_LEADER' and
         f['storage_length_m']==204.49 and f['ingress_length_m']==113.08,'EPISODE_FRAME_SCOPE')
    need(set(f['lane_ids'])==set(LOCAL),'EPISODE_LANE_DOMAIN')
    ids=[]
    for lane in LOCAL:
        actual={v for v,x in world.items() if x['lane_id']==lane}
        need(len(f['lane_ids'][lane])==len(set(f['lane_ids'][lane])) and set(f['lane_ids'][lane])==actual,'EPISODE_LOCAL_POPULATION')
        ids.extend(actual)
    need(set(f['states'])==set(ids),'EPISODE_STATES_POPULATION')
    for vid,x in f['states'].items():
        need(x['vehicle_id']==vid and x['time_s']==t and x['lane_id']==world[vid]['lane_id'] and
             near(x['speed_m_s'],world[vid]['speed_m_s']),'EPISODE_WORLD_SPEED')
        need(x['type_id']=='technical_passenger' and x['speed_mode']==31 and x['lane_change_mode']==1621 and
             x['route']==['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'] and
             set(x['dynamics'])==set(DYNAMICS) and all(numeric(x['dynamics'][k]) and abs(x['dynamics'][k]-v)<=1e-8 for k,v in DYNAMICS.items()),'EPISODE_MODEL_OR_MODES')
        need(numeric(x['position_m']) and numeric(x['length_m']) and near(x['length_m'],5.) and x['speed_m_s']>=0,'EPISODE_BODY_UNKNOWN')
        if fcd is None:
            need(vid in metadata and near(x['position_m'],metadata[vid]['position_m']) and near(x['length_m'],metadata[vid]['length_m']),'EPISODE_PRE_POSITION_METADATA')
        else:
            need(vid in fcd and fcd[vid]['lane']==x['lane_id'] and abs(x['position_m']-float(fcd[vid]['pos']))<=.51e-8,'EPISODE_POST_FCD_POSITION')

    for vid,lead in f['leaders'].items():
        if lead is None:continue
        leader=lead['vehicle_id']
        need(leader in world and lead['time_s']==t and lead['lane_id']==world[leader]['lane_id'] and
             near(lead['speed_m_s'],world[leader]['speed_m_s']) and numeric(lead['length_m']) and lead['length_m']>0,'EPISODE_NATIVE_LEADER_WORLD')
        if fcd is None:
            need(leader in metadata and near(lead['position_m'],metadata[leader]['position_m']) and near(lead['length_m'],metadata[leader]['length_m']),'EPISODE_PRE_LEADER_POSITION')
        else:
            need(leader in fcd and fcd[leader]['lane']==lead['lane_id'] and abs(lead['position_m']-float(fcd[leader]['pos']))<=.51e-8,'EPISODE_POST_LEADER_POSITION')


def neighbors(f,vid):
    """Reconstruct real rear-front distances; no secure-gap threshold waiver."""
    x=f['states'][vid];station=lambda z:z['position_m']-(113.08 if z['lane_id']==LOCAL[1] else 0)
    followers=[(station(z),v,z) for v,z in f['states'].items() if v!=vid and station(z)<=station(x)]
    result=dict(follower_id=None,leader_id=None,follower_gap_excluding_minGap_m=None,leader_gap_excluding_minGap_m=None,physical_overlap=False,minGap_infringement=False)
    if followers:
        pos,other,z=max(followers);gap=station(x)-x['length_m']-pos-z['dynamics']['min_gap']
        need(gap>=-1e-6,'EPISODE_FOLLOWER_BODY_OR_MINGAP')
        result.update(follower_id=other,follower_gap_excluding_minGap_m=gap)
    q=f['following'][vid]
    need(q['time_s']==f['time_s'] and q['vehicle_id']==vid,'EPISODE_QUERY_TIME')
    if q.get('leader_id'):
        lead=f['leaders'][vid];need(lead['vehicle_id']==q['leader_id'] and lead['lane_id']==q['leader_lane_id'],'EPISODE_LEADER_ID')
        lengths=q['path_geometry_m'];base={};accum=0.
        for lane in ('ramp_storage_0',':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0'):
            base[lane]=accum;accum+=lengths[lane]
        base['merge_section_1']=base['merge_section_2']=base['merge_section_0']
        gap=base[lead['lane_id']]+lead['position_m']-lead['length_m']-x['position_m']-x['dynamics']['min_gap']
        need(numeric(gap) and gap>=-1e-6 and near(gap,q['gap_excluding_minGap_m']),'EPISODE_LEADER_BODY_OR_MINGAP')
        result.update(leader_id=q['leader_id'],leader_gap_excluding_minGap_m=gap)
    else:
        need(q['status']=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD' and not any(z['lane_id']==LOCAL[0] and z['position_m']>x['position_m'] for v,z in f['states'].items() if v!=vid),'EPISODE_ABSENT_LEADER_UNBOUND')
    return result


class EpisodeAudit:
    def __init__(self,authority=None):
        if authority is not None:
            need(authority.get('enabled') is True and authority.get('run_id')==RUN and authority.get('contract')==CONTRACT and authority.get('source_commit')==SOURCE and
                 authority.get('status')=='EXACT_ACCEPTANCE_CONTRACT_AUTHORITY_VERIFIED' and authority.get('configured_model')=='Krauss' and
                 authority.get('configured_Euler_dt_s')==1 and authority.get('no_model_or_JM_override') is True,'UNBOUND_EPISODE_AUDIT_AUTHORITY')
        self.authority=authority;self.pending=None;self.observations=[];self.registry=[]

    def step(self,p,r,cycle,world,post,fcd):
        item=r.get('safety_acceptance');t=r['time_begin_s']
        if self.authority is None:
            need(item is None or item.get('enabled') is False,'UNAPPROVED_EPISODE_ANNOTATION')
            return set()
        need(item and item['enabled'] is True and item['contract']==CONTRACT and item['authority_binding']==self.authority and
             item['native_safety_proven'] is False,'EPISODE_AUTHORITY_OR_CONTRACT')
        classes=item['classifications'];bo=r['braking_observation']
        need(all(numeric(x) for x in bo['speed_difference_m_s2'].values()) and all(numeric(x) for x in bo['actual_acceleration_m_s2'].values()),'EPISODE_BRAKING_REQUIRED_UNKNOWN')
        bad={v for v,x in bo['speed_difference_m_s2'].items() if x< -4.5-1e-6}|{v for v,x in bo['actual_acceleration_m_s2'].items() if x< -4.5-1e-6}
        if self.pending is not None:
            need(t==self.pending['time_end_s'] and not bad and not r.get('reasons') and not item['remaining_reasons'] and
                 not r['warning_observation']['text'] and not any(r['native_event_counters'].values()),'EPISODE_FOLLOWUP_HARD_OR_TIME')
            need(len(classes)==1 and classes[0]['decision']=='CLOSED' and classes[0]['classification']=='FOLLOWUP_CLOSED_OBSERVED' and
                 classes[0]['vehicle_ids']==self.pending['vehicle_ids'] and classes[0]['frame']==item['after_frame'] and item['followup_pending'] is None,'EPISODE_FOLLOWUP_BINDING')
            frame_check(item['after_frame'],t+1,post,p['terminal_before'],fcd)
            for vid in self.pending['vehicle_ids']:
                need(vid in item['after_frame']['states'],'EPISODE_FOLLOWUP_MISSING_VEHICLE')
                neighbors(item['after_frame'],vid)
            self.observations[-1]['closure_ACK']=t+1;self.registry[-1]['followup']=deepcopy(classes[0]);self.pending=None
            return set()
        if not bad:
            need(classes==[] and item['followup_pending'] is None and not item['remaining_reasons'],'SPURIOUS_OR_HIDDEN_EPISODE')
            return set()
        need(cycle and cycle['green_end_s']==t and p['motion']==r['motion']=='y' and p.get('acceptance_first_yellow') is True and
             r['post_signal_application_binding']['status']=='BOUND_BEFORE_LEDGER' and r['post_signal_application_binding']['actual_phase']==1 and
             not r.get('reasons') and not item['remaining_reasons'] and not r['warning_observation']['text'] and
             set(r['native_event_counters'])=={'colliding_vehicles','starting_teleports','ending_teleports'} and not any(r['native_event_counters'].values()),'EPISODE_FIRST_YELLOW_OR_HARD_RISK')
        need({c['evidence']['vehicle_id'] for c in classes}==bad and len(classes)==len(bad),'EPISODE_BRAKING_POPULATION')
        before=p['acceptance_safety_before'];after=item['after_frame']
        frame_check(before,t,world,p['terminal_before']);frame_check(after,t+1,post,p['terminal_before'],fcd)
        recomputed=[]
        for c in classes:
            e=c['evidence'];vid=e['vehicle_id'];x=before['states'][vid];y=after['states'][vid]
            need(c['contract']==CONTRACT and c['decision']=='ONE_UNCHANGED_STEP_FOLLOWUP_REQUIRED' and c['classification']=='NUMERICAL_SCALE_COMPATIBLE' and c['legacy_strict_FAIL_retained'] is True and c['native_safety_proven'] is False and c['actual_branch_identified'] is False,'EPISODE_CANDIDATE_LABEL')
            need(e['before']==before and e['after']==after and e['dt_s']==1 and e['first_yellow'] is True and e['motion']=='y' and
                 e['signal_binding']=='BOUND_BEFORE_LEDGER' and e['entered_link'] is False and e['body_coverage_complete'] is True and
                 e['hard_reasons']==[] and e['native_warning_text']=='' and e['native_event_counters']==r['native_event_counters'] and
                 'body_observation' in r and 'body_observation_error' not in r and not any(z['vehicle_id']==vid for z in r['actual_crossings']),'EPISODE_EVIDENCE_BINDING')
            need(x['lane_id']==y['lane_id']==LOCAL[0] and 0<=x['position_m']<204.49 and 0<=y['position_m']<204.49,'EPISODE_STORAGE_LOCATION')
            dv=post[vid]['speed_m_s']-world[vid]['speed_m_s'];a=bo['actual_acceleration_m_s2'][vid]
            need(numeric(a) and near(dv,bo['speed_difference_m_s2'][vid]) and near(a,dv) and near(e['acceleration_m_s2'],a) and near(e['delta_m_s2'],dv),'EPISODE_ACCELERATION_RECOMPUTE')
            offset=204.49-x['position_m']-(x['speed_m_s']-4.5);pred=x['speed_m_s']-4.5-.001
            need(1e-6< -a-4.5<=.001+1e-6 and 4.501<x['speed_m_s']<9 and .1<=offset<=1. and
                 abs(pred-y['speed_m_s'])<=1e-6 and abs(y['position_m']-x['position_m']-y['speed_m_s'])<=1e-6,'EPISODE_SOURCE_SCALE_ARITHMETIC')
            for label,frame in (('before',before),('after',after)):
                independently=neighbors(frame,vid)
                for key,value in independently.items():
                    recorded=c['neighbors'][label][key]
                    need((near(recorded,value) if numeric(value) else recorded==value),'EPISODE_NEIGHBOR_SUMMARY')
            arithmetic=c['arithmetic']
            need(arithmetic['eps_distance_m']==.001 and arithmetic['dt_s']==1 and near(arithmetic['excess_m_s2'],-a-4.5) and
                 near(arithmetic['inferred_stop_offset_m'],offset) and near(arithmetic['predicted_speed_m_s'],pred) and
                 arithmetic['private_stopDist_observed'] is False,'EPISODE_ARITHMETIC_SUMMARY')
            recomputed.append(dict(vehicle_id=vid,acceleration_m_s2=a,delta_m_s2=dv,before_speed_m_s=x['speed_m_s'],after_speed_m_s=y['speed_m_s'],
                before_position_m=x['position_m'],after_position_m=y['position_m'],conditional_stop_offset_m=offset,predicted_speed_m_s=pred))
            required={'ORDINARY_BRAKING_EXCEEDED:'+vid,'UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+vid}
            need(required<=set(r['legacy_braking_reasons']),'EPISODE_LEGACY_FAIL_NOT_RETAINED')
        expected=dict(time_begin_s=t,time_end_s=t+1,vehicle_ids=sorted(bad))
        need(item['followup_pending']==expected,'EPISODE_PENDING_TIME_BINDING')
        self.pending=expected
        self.registry.append(dict(event=deepcopy(expected),classifications=deepcopy(classes),followup=None))
        self.observations.append(dict(classification='INDEPENDENT_SOURCE_SCALE_COMPATIBLE_OBSERVATION',time_begin_s=t,
            vehicle_ids=sorted(bad),recomputed_candidates=recomputed,legacy_braking_reasons=r['legacy_braking_reasons'],closure_ACK=None,native_safety_proven=False))
        return bad

    def finish(self,registry=None,followup=None):
        need(self.pending is None and followup is None,'EPISODE_EOF_PENDING_FOLLOWUP')
        if registry is not None:need(registry==self.registry,'EPISODE_RECEIPT_REGISTRY_MISMATCH')
        return self.observations
