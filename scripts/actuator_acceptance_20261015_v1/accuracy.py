"""Proposed normalized-window screen; no raw reader, simulation or qualification.

Input certificates are references to independently validated projections, not proof
that those projections are true. This module verifies their schema/support and
arithmetic only. Raw FCD/TLS/ACK identity verification belongs to the bound reader.
"""
from copy import deepcopy
from fractions import Fraction
import re
import math

SCHEMA = 'ACTUATOR_ACCURACY_NORMALIZED_V1'
OPPORTUNITY = 'PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1'
WINDOWS = [(1200 + 300*k, 1500 + 300*k) for k in range(6)]
SUPPORTS = WINDOWS + [(600, 4200)]
LOCAL_DOMAIN = [{'lane_id':'ramp_storage_0','start_pos_m':184.49,'end_pos_m':204.49}]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def number(value):
    need(not isinstance(value, bool), 'BOOLEAN_NUMBER')
    try:
        n = Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        raise ValueError('NONFINITE_OR_INVALID_NUMBER') from None
    need(n >= 0, 'NEGATIVE_ACCOUNTING_QUANTITY')
    return n


def reference(value):
    return (isinstance(value, dict) and isinstance(value.get('path'), str)
            and bool(value['path']) and sha(value.get('sha256')))


def metrics(c, n, duration):
    difference = c - n
    bound = max(Fraction(2), c/Fraction(20))
    return dict(C=str(c), N=str(n), signed_error_vehicles=str(difference),
                absolute_error_vehicles=str(abs(difference)), bound_vehicles=str(bound),
                requested_veh_h=str(c*3600/duration), actual_veh_h=str(n*3600/duration),
                signed_error_veh_h=str(difference*3600/duration),
                relative_error=(str(difference/c) if c >= 20 else None),
                relative_status=('DEFINED' if c >= 20 else 'SMALL_OR_ZERO_DENOMINATOR'),
                raw_target=('MET' if abs(difference) <= bound else 'NOT_MET'))


def opportunity(row):
    """Use predeclared observation certificates, never N/E or available booleans."""
    evidence = row['opportunity']
    need(evidence.get('definition') == OPPORTUNITY, 'UNREGISTERED_OPPORTUNITY_DEFINITION')
    need(reference(evidence.get('source')), 'UNBOUND_OPPORTUNITY_PROJECTION')
    duration = row['end_s'] - row['begin_s']
    if evidence.get('supply_covered_seconds') != duration or evidence.get('receiver_covered_seconds') != duration:
        return 'UNKNOWN'
    need(evidence.get('domain') == 'LOCAL_STORAGE_20M_AND_DOWNSTREAM_BOUNDARY', 'UNKNOWN_OPPORTUNITY_DOMAIN')
    need(reference(evidence.get('geometry_source')) and isinstance(evidence.get('lane_domains'), list) and
         bool(evidence['lane_domains']) and all(isinstance(x, dict) and isinstance(x.get('lane_id'), str)
         and type(x.get('start_pos_m')) in (int,float) and type(x.get('end_pos_m')) in (int,float)
         and math.isfinite(x['start_pos_m']) and math.isfinite(x['end_pos_m']) and x['start_pos_m'] < x['end_pos_m'] for x in evidence['lane_domains']), 'MISSING_FIXED_OBSERVATION_GEOMETRY')
    need(evidence['lane_domains'] == LOCAL_DOMAIN and evidence.get('count_basis') == 'ACTUAL_R_FRONTS_IN_FIXED_DOMAIN_PER_1S', 'UNKNOWN_LOCAL_BACKLOG_COUNT_BASIS')
    minimum = evidence.get('minimum_ordered_R_count')
    need(type(minimum) is int and minimum >= 0, 'MISSING_SUPPLY_POPULATION')
    if evidence.get('classification_unknown') is not False:
        return 'UNKNOWN'
    if minimum < 2:
        return 'BACKLOG_OPPORTUNITY_NOT_ESTABLISHED'
    blockers = evidence.get('external_blockers')
    need(isinstance(blockers, list), 'MISSING_RECEIVER_BLOCKER_EVIDENCE')
    for blocker in blockers:
        need(isinstance(blocker, dict) and all(isinstance(blocker.get(k), str) and blocker[k]
             for k in ('vehicle_id', 'lane_id', 'route_connection')), 'MISSING_BLOCKER_ID_GEOMETRY')
        need(reference(blocker.get('source')), 'UNBOUND_BLOCKER_RECORD')
    if blockers:
        # A policy-coupled or unattributed rejection must not exclude bad service.
        if any(x.get('policy_independent') not in (True, False) for x in blockers):
            return 'UNKNOWN'
        if all(x.get('policy_independent') is True for x in blockers):
            if not all(reference(x.get('independence_evidence')) and x.get('independence_basis') ==
                       'TRAJECTORY_AND_BOUNDARY_NOT_ROLE_OR_AVAILABLE' for x in blockers):
                return 'UNKNOWN'
            return 'EXTERNAL_LIMIT_OBSERVED'
        return 'POLICY_COUPLED_OPPORTUNITY'
    return 'OBSERVED_BACKLOG_OPPORTUNITY'


def evaluate_row(row, global_valid):
    result = {'input': deepcopy(row), 'conditional_accuracy': 'NOT_TESTED'}
    try:
        a, b = row['begin_s'], row['end_s']
        need((a, b) in SUPPORTS and type(a) is int and type(b) is int, 'UNREGISTERED_SUPPORT')
        observed = row['observed_seconds']
        need(type(observed) is int and 0 <= observed <= b-a, 'INVALID_OBSERVED_SUPPORT')
        need(type(row['partial']) is bool, 'MISSING_PARTIAL_FLAG')
        need(isinstance(row['pending'], list) and isinstance(row['application_delays'], list), 'MISSING_LIFECYCLE_PROJECTION')
        if observed == 0:
            need(all(row.get(k) is None for k in ('C', 'N', 'E_scheduled', 'E_executed', 'C_selected', 'C_applied')),
                 'UNREACHED_QUANTITIES_MUST_BE_NULL')
            result.update(measurement='NOT_REACHED', raw_target='NOT_TESTED', opportunity='NOT_TESTED')
            return result
        amounts = {k:number(row[k]) for k in ('C', 'N', 'E_scheduled', 'E_executed', 'C_selected', 'C_applied')}
        need(all(amounts[k].denominator == 1 for k in ('N', 'E_scheduled', 'E_executed')), 'NONINTEGER_EVENT_COUNT')
        need(amounts['E_executed'] <= amounts['E_scheduled'], 'EXECUTION_EXCEEDS_SCHEDULE')
        need(reference(row.get('measurement_source')), 'UNBOUND_WINDOW_MEASUREMENT')
        need(row.get('event_support') == 'COMPLETIONS_A_LT_END_LE_B_ENTRIES_A_LE_BEGIN_LT_B', 'AMBIGUOUS_EVENT_SUPPORT')
        result.update(metrics(amounts['C'], amounts['N'], observed))
        result['accounting'] = {k:str(v) for k,v in amounts.items()}
        c, es, ex, n = [amounts[k] for k in ('C', 'E_scheduled', 'E_executed', 'N')]
        result['decomposition'] = {'C_minus_E_scheduled':str(c-es),
            'E_scheduled_minus_E_executed':str(es-ex), 'E_executed_minus_N':str(ex-n),
            'sum_equals_C_minus_N': (c-es)+(es-ex)+(ex-n) == c-n}
        complete = observed == b-a and row['partial'] is False
        result['support'] = 'COMPLETE' if complete else 'PARTIAL'
        result['measurement'] = 'NORMALIZED_ARITHMETIC_VALID' if global_valid else 'UNBOUND_GLOBAL_INPUT'
        if not complete:
            result['observed_prefix_raw_target'] = result['raw_target']
            result['raw_target'] = 'PARTIAL_NOT_A_COMPLETE_TARGET_VERDICT'
            result['opportunity'] = 'NOT_TESTED_PARTIAL'
            return result
        result['opportunity'] = opportunity(row)
        if global_valid and result['opportunity'] in ('OBSERVED_BACKLOG_OPPORTUNITY', 'POLICY_COUPLED_OPPORTUNITY'):
            result['conditional_accuracy'] = 'ACCEPTABLE_WINDOW' if result['raw_target'] == 'MET' else 'NOT_ACCEPTABLE_ACCURACY'
    except (KeyError, TypeError, ValueError) as exc:
        result.update(measurement='UNKNOWN_INVALID_INPUT', error=str(exc), conditional_accuracy='NOT_TESTED')
    return result


def evaluate(document):
    """Keep all supplied rows, six registered windows and H; never emit QUALIFIED."""
    identity_errors = []
    try:
        need(document.get('schema') == SCHEMA, 'UNKNOWN_SCHEMA')
        identity = document['identity']
        need(isinstance(identity['run_id'], str) and identity['run_id'], 'MISSING_RUN_ID')
        for key in ('card_sha256', 'execution_source_sha256', 'raw_manifest_sha256', 'normalized_projection_sha256', 'preregistration_sha256', 'network_sha256'):
            need(sha(identity.get(key)), 'MISSING_IDENTITY_'+key)
        need(document['preregistration']['opportunity_definition'] == OPPORTUNITY, 'UNREGISTERED_OPPORTUNITY')
        need(reference(document['preregistration'].get('source')), 'UNBOUND_PREREGISTRATION')
        need(document['preregistration']['source']['sha256'] == identity['preregistration_sha256'], 'PREREGISTRATION_HASH_MISMATCH')
        need(document.get('measurement_status') == 'INDEPENDENT_NORMALIZED_PROJECTION_VALIDATED', 'MEASUREMENT_NOT_VALIDATED')
    except (KeyError, TypeError, ValueError) as exc:
        identity_errors.append(str(exc))
    rows = document.get('windows', [])
    if not isinstance(rows, list):
        rows = []; identity_errors.append('WINDOWS_NOT_LIST')
    supports = [(r.get('begin_s'), r.get('end_s')) for r in rows if isinstance(r, dict)]
    if sorted(supports, key=repr) != sorted(SUPPORTS, key=repr):
        identity_errors.append('MISSING_DUPLICATE_OR_UNKNOWN_SUPPORT')
    try:
        geometry = document['preregistration']['opportunity_geometry']
        need(reference(geometry['source']) and geometry['lane_domains']==LOCAL_DOMAIN and
             geometry['network_sha256']==document['identity']['network_sha256'] and
             reference(geometry.get('receiver_domain_source')) and isinstance(geometry.get('receiver_lane_ids'),list)
             and bool(geometry['receiver_lane_ids']), 'MISSING_PREREGISTERED_GEOMETRY')
        for row in rows:
            if row.get('observed_seconds') == row.get('end_s',0)-row.get('begin_s',0):
                need(row['opportunity'].get('geometry_source') == geometry['source'] and
                     row['opportunity'].get('lane_domains') == geometry['lane_domains'] and
                     row['opportunity'].get('receiver_geometry_source') == geometry['receiver_domain_source'] and
                     row['opportunity'].get('receiver_lane_ids') == geometry['receiver_lane_ids'], 'OPPORTUNITY_GEOMETRY_DRIFT')
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        identity_errors.append(str(exc))
    try:
        if not identity_errors:
            h = next(r for r in rows if (r['begin_s'],r['end_s']) == (600,4200))
            if h['observed_seconds'] == 3600:
                for key in ('C','N','E_scheduled','E_executed','C_selected','C_applied'):
                    subtotal = sum((number(r[key]) for r in rows if r is not h and r.get(key) is not None), Fraction())
                    need(number(h[key]) >= subtotal, 'HORIZON_SUBWINDOW_INCONSISTENCY_'+key)
    except (KeyError, TypeError, ValueError) as exc:
        identity_errors.append(str(exc))
    evaluated = [evaluate_row(r, not identity_errors) for r in rows]
    eligible = [r for r in evaluated if r['conditional_accuracy'] in ('ACCEPTABLE_WINDOW', 'NOT_ACCEPTABLE_ACCURACY')
                and (r['input']['begin_s'], r['input']['end_s']) in WINDOWS]
    failure = any(r['conditional_accuracy'] == 'NOT_ACCEPTABLE_ACCURACY' for r in eligible)
    pairs = [(x,y) for x in eligible for y in eligible if x['input']['end_s'] == y['input']['begin_s']
             and number(x['C']) >= 20 and number(y['C']) >= 20 and number(x['C'])+number(y['C']) >= 50]
    fixed_rows = [r for r in evaluated if isinstance(r['input'],dict) and (r['input'].get('begin_s'),r['input'].get('end_s')) in WINDOWS]
    fixed_union = {'status':'UNKNOWN_INCOMPLETE_OR_INVALID', 'support':[1200,3000], 'raw_target':'NOT_TESTED'}
    if len(fixed_rows) == 6 and not identity_errors and all(r.get('measurement') in ('NORMALIZED_ARITHMETIC_VALID','NOT_REACHED') for r in fixed_rows):
        observed = [r for r in fixed_rows if r.get('accounting')]
        duration = sum(r['input']['observed_seconds'] for r in observed)
        if duration:
            amounts = {k:sum((number(r['accounting'][k]) for r in observed),Fraction()) for k in ('C','N','E_scheduled','E_executed','C_selected','C_applied')}
            fixed_union.update(metrics(amounts['C'], amounts['N'], duration))
            fixed_union['accounting'] = {k:str(v) for k,v in amounts.items()}
            fixed_union['observed_seconds'] = duration
            fixed_union['status'] = 'COMPLETE' if duration==1800 and all(r.get('support')=='COMPLETE' for r in fixed_rows) else 'PARTIAL'
            if fixed_union['status']=='PARTIAL':
                fixed_union['observed_prefix_raw_target'] = fixed_union['raw_target']
                fixed_union['raw_target'] = 'PARTIAL_NOT_A_COMPLETE_TARGET_VERDICT'
    aggregate = None
    if eligible:
        aggregate = metrics(sum((number(r['C']) for r in eligible), Fraction()),
                            sum((number(r['N']) for r in eligible), Fraction()), len(eligible)*300)
    persistent = any(Fraction(x['signed_error_vehicles']) > Fraction(x['bound_vehicles'])
                     and Fraction(y['signed_error_vehicles']) > Fraction(y['bound_vehicles'])
                     and metrics(number(x['C'])+number(y['C']), number(x['N'])+number(y['N']),600)['raw_target']=='NOT_MET'
                     for x,y in pairs)
    raw_pairs = [(x,y) for x in fixed_rows for y in fixed_rows if x.get('support')==y.get('support')=='COMPLETE'
                 and x.get('measurement')==y.get('measurement')=='NORMALIZED_ARITHMETIC_VALID'
                 and x['input']['end_s']==y['input']['begin_s']]
    raw_persistent = any(Fraction(x['signed_error_vehicles']) > Fraction(x['bound_vehicles'])
                         and Fraction(y['signed_error_vehicles']) > Fraction(y['bound_vehicles'])
                         and metrics(number(x['C'])+number(y['C']),number(x['N'])+number(y['N']),600)['raw_target']=='NOT_MET'
                         for x,y in raw_pairs)
    all_complete = len(evaluated)==7 and all(r.get('support')=='COMPLETE' and r.get('measurement')=='NORMALIZED_ARITHMETIC_VALID' and r.get('opportunity') not in ('UNKNOWN', 'NOT_TESTED_PARTIAL') for r in evaluated)
    verdict = 'NOT_TESTED'
    if failure:
        verdict = 'NOT_ACCEPTABLE_ACCURACY'
    elif all_complete and pairs and aggregate and aggregate['raw_target']=='MET':
        verdict = 'ACCEPTED_ON_OBSERVED_OPPORTUNITY'
    elif aggregate and aggregate['raw_target']=='NOT_MET':
        verdict = 'NOT_ACCEPTABLE_ACCURACY'
    return {'schema':'ACTUATOR_ACCURACY_RESULT_V1', 'criterion_status':'PROPOSED_NOT_APPROVED',
            'identity':deepcopy(document.get('identity')), 'identity_errors':identity_errors,
            'conditional_accuracy':verdict, 'windows':evaluated, 'eligible_aggregate':aggregate, 'fixed_evaluation_union':fixed_union,
            'minimum_opportunity_coverage_met':bool(pairs), 'persistent_underdischarge':persistent, 'raw_persistent_underdischarge_any_adjacent_windows':raw_persistent,
            'measurement_status':document.get('measurement_status','UNKNOWN'),
            'safety_status':document.get('safety_status','UNKNOWN'),
            'raw_failures_outside_eligible': [[r['input']['begin_s'],r['input']['end_s']] for r in evaluated if r.get('raw_target')=='NOT_MET' and r['conditional_accuracy']=='NOT_TESTED'],
            'not_a_full_domain_accuracy_verdict':True, 'qualification':'NO_QUALIFICATION_VERDICT', 'lifecycle_evaluation':'PRESERVED_NOT_INDEPENDENTLY_REVALIDATED',
            'scope':'NORMALIZED_INPUT_ARITHMETIC_AND_PREDECLARED_OBSERVATION_CERTIFICATES_ONLY'}
