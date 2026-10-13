"""Independent observed-signal prerequisite, not future safety qualification."""
LINKS=[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]]
def validate(row,expected):
    b=row.get('post_signal_application_binding')
    if not isinstance(b,dict):raise ValueError('MISSING_ACTUAL_SIGNAL_APPLICATION_BINDING')
    ok=(b.get('status')=='BOUND_BEFORE_LEDGER' and type(b.get('actual_phase')) is int and
        b['actual_phase']==expected['phase'] and b.get('actual_state')==expected['state'] and
        b.get('actual_program')==expected['program'] and b.get('actual_controlled_links')==LINKS and
        type(b.get('ACK_s')) in (int,float) and b['ACK_s']==expected['ACK_s'] and
        b.get('expected_phase')==expected['phase'] and b.get('expected_state')==expected['state'] and
        b.get('expected_program')==expected['program'])
    if not ok:raise ValueError('UNBOUND_ACTUAL_SIGNAL_NOT_AN_APPLICATION')
    return {'status':'PASS_ACTUAL_SIGNAL_BINDING_ONLY','native_safety_proven':False}
