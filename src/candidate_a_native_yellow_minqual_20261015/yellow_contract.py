"""Explicit approved diagnostic interpretation, never a native safety certificate."""
from src.candidate_a_cumulative_full_catalogue_20261014.policy import yellow_scope
POLICY = 'NATIVE_YELLOW_RESPONSIBILITY_COMPLETE_INPUT_DIAGNOSTIC_V1'
INPUT_SCOPE = 'ORIGINAL_HARD_FRESH_FRAME_AND_POPULATION_JOINS_REQUIRED'

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def require_contract(value):
    require(isinstance(value,dict) and set(value)=={'policy','enabled'} and
            value['policy']==POLICY and type(value['enabled']) is bool and
            value['enabled'] is True, 'UNKNOWN_OR_UNAPPROVED_YELLOW_CONTRACT')
    return value

def annotate_yellow_scope(scope, vehicles, time_s, yellow_s, enabled=False):
    require(type(enabled) is bool, 'UNKNOWN_YELLOW_CONTRACT_ENABLE')
    # Existing caller world/ID/model/mode/geometry/phase joins remain hard.
    # This exact pure replay is result/schema binding, not independent physics.
    expected = yellow_scope(vehicles, time_s, yellow_s)
    require(isinstance(scope,dict) and all(k in scope and scope[k]==v
            for k,v in expected.items()), 'UNKNOWN_YELLOW_RESULT_OR_BINDING')
    require(expected['status'] in ('PASS','UNKNOWN'), 'UNKNOWN_YELLOW_SCHEMA')
    for row in scope['rows']:
        require(all(type(row[key]) is bool for key in
                ('one_step_Euler_stop_possible','stop_possible','clear_possible')),
                'UNKNOWN_YELLOW_BOOL_SCHEMA')
    failed=[r['vehicle_id'] for r in expected['rows']
            if r['stop_possible'] is False and r['clear_possible'] is False]
    witness=expected['status']=='PASS'
    require(witness==(len(failed)==0), 'UNKNOWN_YELLOW_WITNESS_AGGREGATE')
    decision=dict(policy=POLICY,enabled=enabled,
        original_witness_status=expected['status'],witness_established=witness,
        failed_witness_ids=failed,
        interpretation=('LEGACY_WITNESS_ESTABLISHED' if witness else
            'DIAGNOSTIC_WITNESS_NOT_ESTABLISHED' if enabled else 'STRICT_STOP_NO_WITNESS'),
        input_scope=INPUT_SCOPE,allow_prepared_step=(witness or enabled),
        future_native_safety_proven=False,safety_certified=None)
    # Original status and original rows are preserved without mutation.
    return dict(scope,diagnostic_yellow_contract=decision)
