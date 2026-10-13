"""Local historical900 replay, explicitly not a native run of the new source."""
import ast
import json
from pathlib import Path
from src.candidate_a_unified_alinea_20261013.policy import Ledger, require, parameters


def source_compatibility(root):
    root=Path(root)
    old=(root/'src/candidate_a_issue12_packet_policy_20261012/adapter.py').read_text()
    new=(root/'src/candidate_a_unified_alinea_20261013/adapter.py').read_text()
    def function(source,name):
        node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name==name)
        return ast.dump(node,include_attributes=False)
    require(all(function(old,x)==function(new,x) for x in ('identity','inventory')), 'PHYSICAL_IDENTITY_CODE_CHANGED')
    def safety_block(s):return s[s.index('        errors = []'):s.index('        if errors:')]
    require(safety_block(old)==safety_block(new), 'POST_PHYSICAL_GUARD_BLOCK_CHANGED')
    require(parameters(8)['phases']==(('G',4,1),('y',2,2),('r',2,0)), '900_PHASES_CHANGED')
    return {'identity_inventory_AST_identical':True,'post_physical_guard_block_byte_identical':True,
        'body_and_current_gap_imports':'UNCHANGED_OLD_MODULES',
        '900_cache_non_E1_domains':'INHERITED_SUPER_DISPATCH_UNCHANGED',
        'expected_metadata_differences':['new run ID','new code namespace','command IDs and journals',
            'prepared versus actual ACK application statuses','generic phase-clock diagnostic fields'],
        'programID900':'I12_PACKET8 unchanged',
        'new_native_source_900_tested':False}


def replay_historical900(root):
    root=Path(root);raw=root/'data/raw/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/outputs'
    rows=[x for line in (raw/'post_steps.jsonl').open() if (x:=json.loads(line))['time_begin_s']>=1200]
    events=[json.loads(x) for x in (raw/'policy_phase_requests.jsonl').read_text().splitlines()]
    bytime={x['time_s']:x for x in events}
    ledger=Ledger(900);matched=[];expected_calls=[(1200,'setProgram','I12_PACKET8'),(1200,'setPhase',0)]
    for row in rows:
        t=row['time_begin_s'];new,c=ledger.begin_step(t)
        if new:ledger.mark_cycle_start(True)
        motion=ledger.motion_at(t)
        if motion=='y' and c['green_end_s'] is None:ledger.close_green(t,'MAX_GREEN_DEADLINE')
        require(motion==row['motion'] and row['accounting_complete'], 'HISTORICAL_MOTION_OR_ACCOUNTING_CHANGED')
        signal=row['phase_observation']
        require(type(signal['phase_after']) is int and
            signal['phase_after']=={'G':0,'y':1,'r':2}[motion] and
            signal['state_after']==motion and row.get('reasons') is None,
            'NEW_EARLY_SIGNAL_BINDING_WOULD_REJECT_HISTORICAL900')
        ids=[x['vehicle_id'] for x in row['actual_crossings']]
        ledger.end_step(t+1,ids,motion)
        actual_switch=row['phase_observation']['next_switch_after_s']
        gend=c['green_end_s'] if c['green_end_s'] is not None else c['begin_s']+4
        expected_switch=c['begin_s']+4 if motion=='G' else gend+2 if motion=='y' else c['end_s'] if c.get('red_clock_bound') else gend+4
        require(actual_switch==expected_switch,'NEW_GENERIC_CLOCK_WOULD_REJECT_HISTORICAL900')
        q=bytime.get(t+1)
        if q:
            for request in q['requests']:
                method,value=request['method'],request['value']
                if method=='setPhase':
                    require(motion=='G' and c['N_G']>=2 and value==1,'QUOTA_SETTER_LOGIC_CHANGED')
                    ledger.close_green(t+1,'ACTUAL_QUOTA_ACK')
                    require(q['actual_readback']=={'time_s':t+1,'phase':1,'state':'y','nextSwitch_s':t+3},'YELLOW_SETTER_READBACK_CHANGED')
                elif method=='setPhaseDuration':
                    require(motion=='r' and value==c['end_s']-(t+1),'DURATION_SETTER_LOGIC_CHANGED')
                    require(request['actual_readback']=={'time_s':t+1,'program':'I12_PACKET8','phase':2,'state':'r','nextSwitch_s':c['end_s']},'RED_SETTER_READBACK_CHANGED')
                    c['red_clock_bound']=True
                else:raise ValueError('UNEXPECTED_HISTORICAL_SETTER')
                expected_calls.append((t+1,method,value))
        matched.append({'time_begin_s':t,'motion':motion,'actual_entry_ids':ids,
            'expected_post_nextSwitch_s':expected_switch,'actual_post_nextSwitch_s':actual_switch})
    actual_calls=[]
    for line in (raw/'pre_steps.jsonl').open():
        row=json.loads(line)
        if row['time_s']>=1200:
            actual_calls.extend((x['time_s'],x['method'],x['value']) for x in row['phase_requests'])
    actual_calls.extend((r['time_s'],r['method'],r['value']) for x in events for r in x['requests'])
    require(sorted(expected_calls,key=lambda x:x[0])==sorted(actual_calls,key=lambda x:x[0]),'SETTER_SEQUENCE_CHANGED')
    require(len(rows)==72 and ledger.N==ledger.E==18 and all(x['completed'] for x in ledger.rows),'HISTORICAL_COMPLETE_ACCOUNTING_CHANGED')
    return {'status':'PASS_LOCAL_REPLAY_NOT_NEW_NATIVE900','source_compatibility':source_compatibility(root),
        'matched_motion_clock_entry_rows':matched,'setter_calls':expected_calls,'accounting':ledger.accounting(),
        'scope':'Recorded actual900 input/count/phase trace replay plus unchanged physical guard code; not reexecution of vehicle physics or future guarantee'}
