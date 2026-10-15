"""Thin read-only PRE/ACK/identity projection for the Proposed accuracy screen.

Physical entries and accounting must already be independently checked by the
bound seven-domain reader. No FCD scan, model query or qualification occurs here.
"""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from scripts.actuator_acceptance_20261015_v1.accuracy import (
    SCHEMA, OPPORTUNITY, SUPPORTS, LOCAL_DOMAIN, reference, need, evaluate)

FIELDS = {'C':'C_exact_fraction','C_selected':'C_selected_exact_fraction',
          'C_applied':'C_applied_exact_fraction','E_scheduled':'E_scheduled_nominal',
          'E_executed':'E_executed_nominal','N':'N'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def records(path):
    with Path(path).open() as stream:
        for line, text in enumerate(stream,1):
            yield line,json.loads(text)


def native_frames(pre_path, ack_path, identity_path, last_ack=None):
    """Stream actual journal schemas, preserving original line references.

    PRE t is BEFORE_MOTION t; this does not relabel XML FCD time as PRE time.
    The existing reader's physical join supplies FCD provenance independently.
    """
    acknowledgements=iter(records(ack_path)); identities=iter(records(identity_path))
    for line,pre in records(pre_path):
        t=pre['time_s']
        if last_ack is not None and t>=last_ack:break  # unexecuted terminal preparation is not a missing motion ACK
        pair=[next(acknowledgements),next(acknowledgements)]
        before=None;before_line=None
        for identity_line,row in identities:
            if row.get('time_s')==t and row.get('stage')=='BEFORE_MOTION':
                before=row;before_line=identity_line;break
            need(row.get('time_s',t)<=t,'IDENTITY_TIME_PASSED_PRE')
        yield dict(time_s=t,pre=pre,ack=[r for _,r in pair],identity=before,
                   refs=dict(pre_line=line,ack_lines=[n for n,_ in pair],identity_line=before_line))


def frame_projection(frame, geometry):
    """Calculate actual local fronts; incomplete evidence never becomes opportunity."""
    t=frame.get('time_s');result=dict(projection_schema='LOCAL_RECEIVER_FRAME_V1',time_s=t,local_R=[],errors=[],refs=deepcopy(frame.get('refs')),
                                    supply_complete=False,receiver_complete=False,receiver_context=None)
    try:
        need(type(t) is int,'UNKNOWN_FRAME_TIME')
        pre=frame['pre'];q=pre['bound_snapshot'];identity=frame['identity'];ack=frame['ack']
        need(pre['time_s']==q['time_s']==identity['time_s']==t and identity['stage']=='BEFORE_MOTION','FRAME_IDENTITY_CLOCK')
        need(len(ack)==2 and all(x['requested_target_s']==t+1 and x['ACK_received'] is True for x in ack),'ACK_PAIR_MISSING')
        need(ack[0]['actual_time_verified'] is False and ack[0]['actual_readback_s'] is None and
             ack[1]['actual_time_verified'] is True and ack[1]['actual_readback_s']==t+1,'ACK_READBACK_UNBOUND')
        world=q['world'];need(set(world)==set(identity['active_ids']),'WORLD_IDENTITY_POPULATION')
        states=q['vehicle_states'];storage={vid for vid,v in world.items() if v['lane_id']=='ramp_storage_0'}
        selected=[v for v in states if v['population']=='storage']
        by={v['vehicle_id']:v for v in selected}
        need(len(by)==len(selected) and set(by)==storage==set(q['storage']),'STORAGE_POPULATION_MISSING_OR_DUPLICATE')
        for vid,v in by.items():
            meta=identity['vehicle_states'][vid];w=world[vid]
            need(v['type_id']==meta['type_id'] and isinstance(meta['route'],list) and 'ramp_storage' in meta['route'], 'VEHICLE_ROUTE_TYPE_UNBOUND')
            for key in ('position_m','speed_m_s','length_m','min_gap_m'):
                need(type(v[key]) in (int,float) and math.isfinite(v[key]),'MISSING_LOCAL_BODY_OR_SPEED')
            need(v['length_m']>0 and v['min_gap_m']>=0 and v['speed_m_s']>=0 and abs(v['speed_m_s']-w['speed_m_s'])<=1e-9,'INVALID_LOCAL_DYNAMICS')
            need(w['role']=='R' and vid.startswith('R_flow.'),'LOCAL_NON_R_POPULATION')
            if 184.49<=v['position_m']<=204.49:
                result['local_R'].append({k:v[k] for k in ('vehicle_id','position_m','speed_m_s','length_m','min_gap_m','type_id')})
        proof=frame['position_proof']
        need(proof['PRE_time_s']==proof['actual_ACK_s']==t and proof['FCD_XML_time_s']==t-1,'PRE_POSITION_WITNESS_CLOCK')
        for vid,v in by.items():
            need(vid in proof['verified'] and vid not in proof['unknown'],'LOCAL_PRE_POSITION_NOT_INDEPENDENTLY_BOUND')
            witness=proof['verified'][vid]
            need(abs(v['position_m']-witness['position_m'])<=1e-9 and abs(v['length_m']-witness['length_m'])<=1e-9 and
                 abs(v['position_m']-float(witness['fcd_position_m']))<=.51e-8,'LOCAL_PRE_POSITION_PROJECTION_MISMATCH')
        result['local_R'].sort(key=lambda x:(-x['position_m'],x['vehicle_id']))
        result['supply_complete']=True
        # Preserve actual receiver context without turning a READY/available flag
        # into a policy-independent capacity certificate.
        receiver=q.get('receiver');queries=q.get('entry_following_before')
        result['receiver_context']=deepcopy(dict(receiver=receiver,native_receiver_decision=q.get('native_receiver_decision'),entry_following_before={}))
        need(isinstance(receiver,dict) and isinstance(queries,dict),'MISSING_RECEIVER_CONTEXT')
        # New finite-domain observation is required. Old prospective/READY
        # records alone cannot establish its missing lane-population coverage.
        domain=q['receiver_domain_observation']
        need(domain['time_s']==t and domain['scope']=='FRESH_COMPLETE_FIXED_RECEIVER_LANES','RECEIVER_DOMAIN_TIME_SCOPE')
        lanes=geometry['receiver_lane_ids'];need(set(domain['ids_by_lane'])==set(lanes),'RECEIVER_DOMAIN_LANES')
        ids=[vid for lane in lanes for vid in domain['ids_by_lane'][lane]]
        need(len(set(ids))==len(ids) and set(ids)==set(domain['vehicles']),'RECEIVER_DOMAIN_DUPLICATE_OR_MISSING_ID')
        expected={vid for vid,w in world.items() if w['lane_id'] in lanes}
        need(set(ids)==expected,'RECEIVER_WORLD_POPULATION')
        need(domain['geometry_m']==geometry['receiver_geometry_m'],'RECEIVER_GEOMETRY_DRIFT')
        for lane in lanes:
            for vid in domain['ids_by_lane'][lane]:
                v=domain['vehicles'][vid]
                need(vid in proof['verified'] and vid not in proof['unknown'] and abs(v['position_m']-proof['verified'][vid]['position_m'])<=1e-9 and
                     abs(v['length_m']-proof['verified'][vid]['length_m'])<=1e-9,'RECEIVER_PRE_POSITION_NOT_INDEPENDENTLY_BOUND')
                need(v['lane_id']==world[vid]['lane_id']==lane,'RECEIVER_LANE_JOIN')
                for key in ('position_m','length_m','speed_m_s'):
                    need(type(v[key]) in (int,float) and math.isfinite(v[key]),'RECEIVER_BODY_OR_SPEED_MISSING')
                need(v['length_m']>0 and v['speed_m_s']>=0 and isinstance(v['route'],list) and
                     v['type_id']==identity['vehicle_states'][vid]['type_id'],'RECEIVER_METADATA_UNBOUND')
        result['receiver_complete']=True
        result['receiver_domain_observation']=deepcopy(domain)
        need(len({v['position_m'] for v in by.values()})==len(by),'AMBIGUOUS_STORAGE_FRONT_POSITIONS')
        front=max(by,key=lambda vid:by[vid]['position_m']) if by else None
        need((receiver.get('front_id',front) or None)==front,'RECEIVER_FRONT_POPULATION_MISMATCH')
        query=queries.get(front) if front else None
        result['receiver_context']['entry_following_before']={front:deepcopy(query)} if front else {}
        if front and q.get('motion')=='r' and query is None:
            result['current_query_scope']='NOT_SAMPLED_DURING_RED_FULL_FINITE_DOMAIN_RETAINED'
        elif front:
            need(isinstance(query,dict) and query.get('time_s')==t,'MISSING_FRONT_FRESH_CURRENT_QUERY')
            need(set(query['receiver_path_lanes'])==set(lanes),'CURRENT_QUERY_PATH_UNBOUND')
            status=query['status']
            if status in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','STOP_CURRENT_GAP_BOUND_DENIED'):
                leader=query['leader_id']
                need(leader in domain['vehicles'] and
                     all(type(query[k]) in (int,float) and math.isfinite(query[k]) for k in
                         ('gap_excluding_minGap_m','actual_secure_gap_m')) and
                     query['gap_excluding_minGap_m']>=0 and query['actual_secure_gap_m']>=0,'CURRENT_QUERY_NUMERIC_OR_LEADER_UNBOUND')
                # Complete passive-reference deficit remains in the opportunity
                # sample. It is not evidence for an external-service exemption.
                result['passive_reference_below_observed']=query['gap_excluding_minGap_m']<query['actual_secure_gap_m']
            else:
                need(status=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD','CURRENT_QUERY_UNKNOWN')
    except (KeyError,TypeError,ValueError) as exc:
        result['errors'].append(str(exc))
    return result


def _projected_window(frames,begin_s,end_s,geometry,source):
    """Frames are finite joined actual-schema objects; return evidence, never N."""
    need(geometry['lane_domains']==LOCAL_DOMAIN and reference(source),'UNBOUND_LOCAL_GEOMETRY_OR_PROJECTION')
    selected=[f for f in frames if begin_s<=f['time_s']<end_s]
    times=[r['time_s'] for r in selected]
    expected=list(range(begin_s,end_s))
    complete=times==expected
    supply=sum(r['supply_complete'] for r in selected) if len(set(times))==len(times) else 0
    receiver=sum(r['receiver_complete'] for r in selected) if len(set(times))==len(times) else 0
    unknown=not complete or any(r['errors'] for r in selected)
    evidence=dict(definition=OPPORTUNITY,source=deepcopy(source),domain='LOCAL_STORAGE_20M_AND_DOWNSTREAM_BOUNDARY',
        geometry_source=deepcopy(geometry['source']),lane_domains=deepcopy(geometry['lane_domains']),
        receiver_geometry_source=deepcopy(geometry['receiver_domain_source']),receiver_lane_ids=deepcopy(geometry['receiver_lane_ids']),
        count_basis='ACTUAL_R_FRONTS_IN_FIXED_DOMAIN_PER_1S',supply_covered_seconds=supply,receiver_covered_seconds=receiver,
        minimum_ordered_R_count=min((len(r['local_R']) for r in selected if r['supply_complete']),default=0),
        classification_unknown=unknown,external_blockers=[],external_cause_status='NOT_ESTABLISHED_NO_CAUSAL_EXCLUSION',
        frame_evidence=selected)
    return evidence


def project_window(frames,begin_s,end_s,geometry,source):
    """Public pure frame interface always computes the observations itself."""
    return _projected_window((frame_projection(f,geometry) for f in frames),begin_s,end_s,geometry,source)


def normalize(reader,frames,registration,sources,card,manifest):
    """Generate all seven supports from independent reader's cumulative series.

    Source references are constructed/hashed by CLI or supplied by a verified
    caller. This does not re-prove reader certificates or rerun a raw audit.
    """
    need(all(reference(sources.get(k)) for k in ('reader','pre','ack','identity','registration','card','manifest')),'MISSING_BOUND_NORMALIZER_INPUT')
    geometry=registration['opportunity_geometry']
    registered=[h for path,h in card['prepared_input_sha256'].items() if Path(path).resolve()==Path(sources['registration']['path']).resolve()]
    need(registered==[sources['registration']['sha256']],'REGISTRATION_NOT_PREPARED_INPUT_BOUND')
    identity=dict(run_id=card['spec']['run_id'],card_sha256=sources['card']['sha256'],
        raw_manifest_sha256=sources['manifest']['sha256'],execution_source_sha256=card['common_runtime_source_sha256'],
        network_sha256=card['network_sha256'],preregistration_sha256=sources['registration']['sha256'])
    need(registration['run_id']==identity['run_id']==reader['run_id']==manifest['run_id'],'READER_RUN_MISMATCH')
    need(geometry['network_sha256']==identity['network_sha256'],'NETWORK_BINDING_MISMATCH')
    need(card['common_runtime_source_sha256']==digest(card['sources_sha256']),'EXECUTION_SOURCE_NETWORK_BINDING')
    closure=reader['reader_version']['current_source_closure_sha256']
    need(bool(closure) and all(card['sources_sha256'].get(k)==v for k,v in closure.items()),'READER_CLOSURE_NOT_EXECUTION_CARD')
    for key in ('pre','ack','identity'):
        matches=[v for path,v in manifest['files'].items() if Path(path).resolve()==Path(sources[key]['path']).resolve()]
        need(len(matches)==1 and (matches[0]['sha256'] if isinstance(matches[0],dict) else matches[0])==sources[key]['sha256'],'PROJECTION_FILE_NOT_MANIFEST_BOUND_'+key)
    provenance=reader['domains']['provenance'];joins=reader['domains']['native_stream_joins'];accounting=reader['domains']['accounting']
    need(provenance['status']=='PASS_NATIVE_HASH_PROVENANCE' and provenance['card_sha256']==identity['card_sha256'] and
         provenance['manifest_sha256']==identity['raw_manifest_sha256'],'READER_PROVENANCE_UNBOUND')
    need(joins['status']=='PASS_JOIN_INTEGRITY' and accounting['status']=='PASS_INDEPENDENT_NATIVE_ACCOUNTING','UNVERIFIED_READER_MEASUREMENT')
    steps=reader['per_step_accounting'];by={r['time_begin_s']:r for r in steps}
    need(len(by)==len(steps),'DUPLICATE_ACCOUNTING_STEP')
    last=reader['observed_prefix']['last_ACK']
    need(sorted(by)==list(range(600,last)),'ACCOUNTING_GAP_OR_OUTSIDE_PREFIX')
    position_rows=reader['domains']['pre_position_observations']['rows']
    position_by={p['PRE_time_s']:p for p in position_rows}
    need(len(position_by)==len(position_rows) and sorted(position_by)==list(range(600,last)),'PRE_POSITION_CERTIFICATE_COVERAGE')
    material=[]
    for f in frames:
        if 600<=f['time_s']<last:
            f=dict(f,position_proof=position_by[f['time_s']])
            material.append(frame_projection(f,geometry))
    need([f['time_s'] for f in material]==list(range(600,last)),'JOINED_FRAME_GAP_OR_DUPLICATE')
    entries=joins['entries'];ids=[r['vehicle_id'] for r in entries]
    need(len(set(ids))==len(ids) and len(ids)==joins['independent_physical_N'],'ENTRY_IDS_DUPLICATE_OR_COUNT')
    need(all(600<=r['time_begin_s']<r['time_end_s']<=last and r['time_end_s']==r['time_begin_s']+1 for r in entries),'ENTRY_TIME_OUTSIDE_ACK')
    terminal=reader.get('native_terminal_evidence',{});commands=terminal.get('command_records',{})
    need(isinstance(commands,dict),'MISSING_COMMAND_RECORDS')
    pending=[deepcopy(v) for v in commands.values() if v.get('status')=='PENDING']
    delays=[dict(request_id=k,first_application_s=v['first_application_s'],delay_s=v['first_application_s']-v['command']['global_request_s']) for k,v in commands.items() if v.get('first_application_s') is not None]
    windows=[]
    evidence_payload={}
    for a,b in SUPPORTS:
        stop=min(b,last);observed=max(0,stop-a)
        row=dict(begin_s=a,end_s=b,observed_seconds=observed,partial=observed!=b-a,pending=deepcopy(pending) if (a,b)==(600,4200) else [],
            pending_scope='TERMINAL_SNAPSHOT' if (a,b)==(600,4200) else 'NOT_RECONSTRUCTED_FROM_TERMINAL_SUMMARY',
            application_delays=deepcopy([d for d in delays if a<=d['first_application_s']<stop]),
            measurement_source=deepcopy(sources['reader']),event_support='COMPLETIONS_A_LT_END_LE_B_ENTRIES_A_LE_BEGIN_LT_B')
        for output,key in FIELDS.items():
            row[output]=None if not observed else str(Fraction(str(by[stop-1]['accounting'][key]))-(Fraction(str(by[a-1]['accounting'][key])) if a>600 else Fraction()))
        if observed:
            physical=sum(a<=e['time_begin_s']<stop for e in entries)
            need(Fraction(row['N'])==physical,'INDEPENDENT_ENTRY_WINDOW_MISMATCH')
        evidence=_projected_window(material,a,b,geometry,sources['pre']);row['opportunity']=evidence
        evidence_payload[str(a)+':'+str(b)]=evidence
        windows.append(row)
    identity['normalized_projection_sha256']=digest(dict(sources=sources,evidence=evidence_payload))
    output=dict(schema=SCHEMA,identity=identity,preregistration=dict(opportunity_definition=OPPORTUNITY,
        source=deepcopy(sources['registration']),opportunity_geometry=deepcopy(geometry)),
        measurement_status='INDEPENDENT_NORMALIZED_PROJECTION_VALIDATED',safety_status=reader.get('safety_status','NOT_A_SAFETY_VERDICT_USE_BOUND_READER'),
        windows=windows,normalizer_sources=deepcopy(sources),original_reader_status=reader['status'],
        lifecycle_scope='TERMINAL_PENDING_AND_OBSERVED_FIRST_APPLICATION_HISTORY; NOT_PER_WINDOW_RECONSTRUCTION',
        projection_digest_definition='SHA256_CANONICAL_JSON_OF_SOURCES_AND_OPPORTUNITY_EVIDENCE',
        qualification='NO_QUALIFICATION_VERDICT',terminal_pending=deepcopy(pending),
        terminal_observation={k:deepcopy(terminal.get(k)) for k in ('status','error','last_completed_s','last_accounted_s','partial_final_cycle','body_censored_ids','last_selected_cycle')})
    output['six_window_union']=evaluate(output)['fixed_evaluation_union']
    return output


def source_ref(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
    return dict(path=str(path),sha256=h.hexdigest())


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('reader','pre','ack','identity','registration','card','manifest','out'):p.add_argument('--'+name,required=True)
    args=p.parse_args();out=Path(args.out)
    need(not out.exists() and 'data/raw' not in str(out.resolve()),'REFUSE_EXISTING_OR_RAW_OUTPUT')
    sources={k:source_ref(getattr(args,k)) for k in ('reader','pre','ack','identity','registration','card','manifest')}
    reader=json.loads(Path(args.reader).read_text())
    result=normalize(reader,native_frames(args.pre,args.ack,args.identity,reader['observed_prefix']['last_ACK']),
                     json.loads(Path(args.registration).read_text()),sources,
                     json.loads(Path(args.card).read_text()),json.loads(Path(args.manifest).read_text()))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
