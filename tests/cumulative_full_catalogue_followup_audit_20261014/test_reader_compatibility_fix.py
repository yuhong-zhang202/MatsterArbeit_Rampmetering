"""Two known audit defects only; lexical probe and tiny synthetic Y schema."""
import ast,copy,pathlib,types,unittest
from scripts.cumulative_full_catalogue_followup_audit_20261014_v1.yellow import yellow_record,yellow_coverage
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import catalogue
ROOT=pathlib.Path(__file__).resolve().parents[2]
OLD=ROOT/'data/processed/dynamic_minimum_qualification_20261015_v1/reader_fix_v1/preimages/ACTUAL_BOUND_V2_079ed695.py'
NEW=ROOT/'scripts/cumulative_full_catalogue_followup_audit_20261014_v1/actual.py'
def probe(source):
    f=next(q for q in ast.parse(source).body if isinstance(q,ast.FunctionDef) and q.name=='audit')
    call=next(q for q in f.body for q in (q.body if isinstance(q,ast.For) else [q]) if False) if False else None
    call=next(q for q in ast.walk(f) if isinstance(q,ast.Assign) and isinstance(q.value,ast.Call) and isinstance(q.value.func,ast.Attribute) and q.value.func.attr=='audit_terminal')
    assign=next(q for q in ast.walk(f) if isinstance(q,ast.Assign) and isinstance(q.value,ast.Call) and isinstance(q.value.func,ast.Name) and q.value.func.id=='terminal_scope')
    args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[])
    function=ast.FunctionDef(name='normal_arrival_probe',args=args,body=[copy.deepcopy(call),copy.deepcopy(assign),ast.Return(value=ast.Name(id='result',ctx=ast.Load()))],decorator_list=[],type_params=[])
    tree=ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[]));calls=[]
    env={'terminal':types.SimpleNamespace(audit_terminal=lambda *a:calls.append(a) or 'MODULE_ARRIVAL_CALL_OBSERVED'),'q':{'vehicle_id':'synthetic'},'trip_by':{'synthetic':{}},'lanes':{},'terminal_scope':lambda *a:{'runtime_stop':False},'receipt':{},'last':1296,'approved_end':1296,'account':{},'active':set()}
    exec(compile(tree,'actual_normal_arrival_lexical_probe','exec'),env);return env['normal_arrival_probe'],calls

def tiny(period):
    p=catalogue(period);t=1204;vid='R_flow.synthetic';cycle=dict(begin_s=1200,end_s=1200+period,**p)
    row=dict(vehicle_id=vid,population='storage',time_s=t,speed_m_s=0.,position_m=190.,length_m=5.,normal_decel_m_s2=4.5,action_step_s=1.,native_future_safety_proven=False,one_step_Euler_stop_possible=True,distance_to_meter_m=204.49-190.,stop_possible=True,clear_possible=False)
    y=dict(time_s=t,source_post_frame_time_s=t,yellow_s=p['yellow_s'],status='PASS',rows=[row],covered_ids=[vid],screen_stage='PREPARED_BEFORE_FIRST_Y_MOTION',source_program=p['program'],source_motion='y')
    world={vid:dict(lane_id='ramp_storage_0',speed_m_s=0.)};meta={vid:dict(position_m=190.,length_m=5.,normal_decel_m_s2=4.5)}
    return y,[cycle],world,meta

class ReaderCompatibilityTests(unittest.TestCase):
 def test_old_shadow_fails_new_normal_arrival_call_uses_module(self):
    old,calls=probe(OLD.read_text())
    with self.assertRaises(UnboundLocalError):old()
    self.assertEqual(calls,[])
    new,calls=probe(NEW.read_text());self.assertEqual(new(),'MODULE_ARRIVAL_CALL_OBSERVED');self.assertEqual(len(calls),1)
 def test_exact_legal_Y_catalogue_and_reject_duration_or_type(self):
    for period in range(8,25):
        y,cs,w,m=tiny(period)
        self.assertTrue(yellow_record(y,cs,w,m,1205))
        self.assertEqual(y['yellow_s'],2 if period==8 else 3 if period in (9,10) else 5)
    for period,bad in ((8,3),(9,2),(10,4),(11,4),(24,3)):
        y,cs,w,m=tiny(period);y['yellow_s']=bad
        with self.subTest(period=period),self.assertRaises(ValueError):yellow_record(y,cs,w,m,1205)
    for mutation in ('period_float','duration_float','duration_bool','cycle_Gmax_wrong'):
        y,cs,w,m=tiny(10)
        if mutation=='period_float':cs[0]['period_s']=10.0
        elif mutation=='duration_float':y['yellow_s']=3.0
        elif mutation=='duration_bool':y['yellow_s']=True
        else:cs[0]['max_green_s']=4
        with self.subTest(mutation=mutation),self.assertRaises(ValueError):yellow_record(y,cs,w,m,1205)
 def test_missing_firstY_and_unknown_bound_fields_still_reject(self):
    y,cs,w,m=tiny(24);post=[None]*1205;pre=[None]*1205;post[1203]={'post_world':w};pre[1204]={'bound_snapshot':dict(time_s=1204,motion='y',program=cs[0]['program'],terminal_before=m)}
    phase={'status':'PASS_CONTINUOUS_PHASES','cycles':[dict(begin_s=1200,green_end_s=1204,observed_motion_sequence='GGGGy')]}
    self.assertEqual(yellow_coverage([y],phase,cs,post,pre,1205,False)['validated_records'],1)
    with self.assertRaisesRegex(ValueError,'MISSING_OBSERVED_YELLOW_SCREEN'):yellow_coverage([],phase,cs,post,pre,1205,False)
    for mutation in ('unknown_speed','missing_position','wrong_ID','wrong_clock'):
        q=copy.deepcopy(y)
        if mutation=='unknown_speed':q['rows'][0]['speed_m_s']=None
        elif mutation=='missing_position':q['rows'][0].pop('position_m')
        elif mutation=='wrong_ID':q['covered_ids']=[]
        else:q['source_post_frame_time_s']=1203
        with self.subTest(mutation=mutation),self.assertRaises((ValueError,KeyError,TypeError)):yellow_record(q,cs,w,m,1205)
if __name__=='__main__':unittest.main()
