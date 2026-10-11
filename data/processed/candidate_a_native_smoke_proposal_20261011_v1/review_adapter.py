"""Few independent interface/accounting probes; no native launch or raw input."""
import ast, hashlib, importlib.util, json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))

def review():
    binder_path=ROOT/'artifacts/candidate_a_native_smoke_proposal_20261011_v1/engineering/INPUT_BINDINGS_R2.json'
    binder=json.loads(binder_path.read_text())
    for p,h in binder['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    preserved=json.loads((BASE/'YELLOW_BINDINGS.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in preserved['files'].items())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in preserved['protected_old_files'].items())
    adapter_path=ROOT/'src/candidate_a_native_smoke_20261011/adapter.py';tree=ast.parse(adapter_path.read_text())
    attrs=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert not any(x in attrs for x in ['simulationStep','setPhase','setProgram','setRedYellowGreenState','start'])
    tpath=ROOT/'tests/candidate_a_native_smoke_20261011/test_adapter.py'
    spec=importlib.util.spec_from_file_location('offline_native_fixture',tpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    outcomes=[]
    a,c=mod.at_red();r=a.prepare_step(c,1206);assert r['shadow_envelope']['safe'] is False and not r['step_advance_performed'];c.advance_fake();r=a.reconcile_step(c,mod.warning(c));assert a.paused and r['accounting']['E']==0 and r['accounting']['N']==0
    outcomes.append({'probe':'shadow_refusal_advisory_partial_cycle_mandatory_pause','result':'PASS','C':r['accounting']['C'],'E':0,'N':0,'full_cycles':0})
    c=mod.FakeConnection();a=mod.StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake()
    try:a.reconcile_step(c,None);raise AssertionError('missing warnings accepted')
    except mod.DiagnosticStop:assert a.paused and a.last_completed==1201 and not a.receipts[-1]['accounting_complete']
    outcomes.append({'probe':'missing_warning_interval_retains_unaccounted_completed_prefix','result':'PASS'})
    c=mod.FakeConnection();a=mod.StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake();c.vehicle.getAcceleration=lambda v:(_ for _ in ()).throw(RuntimeError('offline missing getter'))
    try:a.reconcile_step(c,mod.warning(c));raise AssertionError('missing getter accepted')
    except RuntimeError:assert a.paused and a.receipts[-1]['accounting_complete'] and a.last_completed==a.last_end==1201
    outcomes.append({'probe':'post_getter_exception_terminal_keeps_accounted_prefix','result':'PASS'})
    a,c=mod.at_red();a.prepare_step(c,1206);c.advance_fake();c.storage=[];c.internal=['R_flow.1']
    try:a.reconcile_step(c,mod.warning(c));raise AssertionError('red crossing accepted')
    except mod.DiagnosticStop:assert a.paused and a.ledger.N==1 and a.ledger.E==0
    outcomes.append({'probe':'actual_fake_red_N_retained_and_stop','result':'PASS'})
    return {'status':'PASS','classification':'OFFLINE_INTERFACE_ACCOUNTING_PROBES_NOT_NATIVE_BEHAVIOR','probes':outcomes,'engine_bindings_match':len(binder['files']),'preserved_old_files':len(preserved['protected_old_files']),'native_api_calls_or_starts':0,'launch_bridge':'NOT_IMPLEMENTED','authorization':'PREPARATION_ONLY','limits':'Fake fixture/schema binding does not verify native warning completeness, world coverage, physics, whole joint safety, yellow adequacy or service qualification.'}

if __name__=='__main__':print(json.dumps(review(),indent=2))
