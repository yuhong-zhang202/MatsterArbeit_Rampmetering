"""Read-only FIX02 command/credit audit. No SUMO, tuning, or raw writes."""
import argparse, csv, hashlib, io, json, math, platform, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/processed/actuator_investigation_20261007_v1'
TABLE = ROOT / 'results/tables/actuator_investigation_20261007_v1'
BASE = 'e8bf608a15cf4c4484914467c5550d041c017a62'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--refresh-derived',action='store_true',help='Explicitly refresh only this investigation generated tables and receipt')
ARGS=parser.parse_args()

def emit(path,content):
    data=content.encode('utf-8')
    assert path.parent in {OUT,TABLE}, 'output outside owned investigation directories'
    if path.exists():
        if path.read_bytes()==data: return
        if not ARGS.refresh_derived: raise RuntimeError(f'Existing derived output differs: {path}; inspect changes before --refresh-derived')
    path.write_bytes(data)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def close(a,b):
    assert math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-10),(a,b)

def category(reason):
    if reason in ['FOLLOWER_STOP_DISTANCE','FOLLOWER_POST_RED_PREDICTION','LEADER_SECURE_GAP']:
        return 'safety'
    if reason=='INTERNAL_RECEIVER_CLEARANCE': return 'receiver'
    if reason=='NO_FRONT': return 'no_demand'
    if reason in ['STOPPED_FRONT_OR_RECEIVER_NOT_READY','FRONT_NOT_ONE_STEP_REACHABLE']:
        return 'front_readiness_or_receiver_not_uniquely_separable'
    if reason in ['STOPPED_READY','MOVING_READY','ALLOW']: return 'allowed_or_spacing'
    return 'other'

def balance(command,greens,dropped,initial,final):
    return command-greens-dropped-final+initial

# Known-example tests cover attribution-independent finite-window accounting.
close(balance(75,45,30,0.5,0.5),0)
close(balance(2.25,2,0,0,0.25),0)
close(balance(0.5,1,0,0.75,0.25),0)
assert category('FOLLOWER_POST_RED_PREDICTION')=='safety'
assert category('STOPPED_FRONT_OR_RECEIVER_NOT_READY').startswith('front_readiness')

published=list(csv.DictReader((ROOT/'results/tables/formal_development_20261007_v1/service_windows_fix02_final.csv').open()))
index={(r['run_id'],int(r['begin'])):r for r in published}
assert len(index)==len(published)==72
runs=[]; windows=[]; reasons=[]; bindings=[{'path':'results/tables/formal_development_20261007_v1/service_windows_fix02_final.csv','sha256':sha(ROOT/'results/tables/formal_development_20261007_v1/service_windows_fix02_final.csv')}]; max_step_residual=0.; total_crossings=0
for q in [750,900]:
 for seed in [17,23,42]:
  for treatment in ['T1','T2']:
   rid=f'DEV_M3600_R{q}_S{seed}_{treatment}_A03'
   raw=ROOT/'data/raw/formal_development_20261007_v1'/rid/'outputs'
   receipt=json.loads((raw/'execution_receipt.json').read_text())
   p=raw/'controller_steps.csv'; digest=sha(p)
   assert digest==receipt['output_manifest'][p.name]['sha256']
   bindings.append({'path':str(p.relative_to(ROOT)),'sha256':digest,'bytes':p.stat().st_size})
   proc=ROOT/'data/processed/formal_development_20261007_v1'/f'FIX02_{treatment}_R{q}_S{seed}_A03'
   gate=json.loads((proc/'FIX02_DATA_GATE.json').read_text())
   assert gate['run_id']==rid and gate['actuator']['status']=='PASS' and gate['rate_capability']=='NOT_QUALIFIED'
   bindings.append({'path':str((proc/'FIX02_DATA_GATE.json').relative_to(ROOT)),'sha256':sha(proc/'FIX02_DATA_GATE.json')})
   with p.open() as f:
    reader=csv.DictReader(f)
    need={'time_begin_s','time_end_s','command_rate_veh_h','credit_before','credit_after','nominal_slot_scheduled','guard_allowed','guard_reason','slot_scheduled','requested_state','observed_state','queue_vehicle_count','crossing_bracket_ids_json','red_crossing_bracket_ids_json','dropped_credit_total'}
    assert need<=set(reader.fieldnames)
    rows=list(reader)
   assert len(rows)==4200
   assert [float(r['time_begin_s']) for r in rows]==list(range(4200))
   audit=[]; previous_drop=0.; previous_credit=0.; last_green=None; ideal_credit=0.; ideal_last=None; seen=set()
   for r in rows[600:]:
    t=int(float(r['time_begin_s'])); assert float(r['time_end_s'])==t+1
    rate=float(r['command_rate_veh_h']); assert 300<=rate<=900
    before=float(r['credit_before']); after=float(r['credit_after']); drop=float(r['dropped_credit_total']); dd=drop-previous_drop
    close(before,previous_credit); previous_credit=after
    green=r['slot_scheduled']=='True'; allowed=r['guard_allowed']=='True'
    nominal=before+rate/3600>=1-1e-10 and (last_green is None or t-last_green>=3)
    assert nominal==(r['nominal_slot_scheduled']=='True')
    assert green==(nominal and allowed)
    expected=before+rate/3600-int(green); expected_drop=max(0,expected-1)
    close(dd,expected_drop); close(after,min(expected,1))
    close(balance(rate/3600,int(green),dd,before,after),0)
    max_step_residual=max(max_step_residual,abs(balance(rate/3600,int(green),dd,before,after)))
    if green: last_green=t
    assert r['requested_state']==('G' if green else 'r') and r['observed_state']==r['requested_state']
    ids=json.loads(r['crossing_bracket_ids_json']); redids=json.loads(r['red_crossing_bracket_ids_json'])
    assert len(ids)==int(green) and not redids and not (seen & set(ids)); seen.update(ids)
    ideal_credit+=rate/3600
    ideal_green=ideal_credit>=1-1e-10 and (ideal_last is None or t-ideal_last>=3)
    if ideal_green: ideal_credit-=1;ideal_last=t
    # This is an opportunity-only counterfactual arithmetic replay; no vehicle-state or safety claim.
    assert ideal_credit<=1+1e-8
    audit.append(dict(t=t,command=rate/3600,before=before,after=after,drop=dd,green=int(green),cross=len(ids),supply=int(r['queue_vehicle_count'])>0,denied=nominal and not allowed,reason=r['guard_reason'],category=category(r['guard_reason']),ideal_green=int(ideal_green),ideal_credit=ideal_credit))
    previous_drop=drop
   assert len(seen)==gate['actuator']['counts']['actual_crossings'];total_crossings+=len(seen)
   for lo,hi,kind in [(600,4200,'whole_control')]+[(b,b+300,'evaluation_window') for b in range(1200,3000,300)]:
    a=[r for r in audit if lo<=r['t']<hi]; command=sum(r['command'] for r in a); greens=sum(r['green'] for r in a); dropped=sum(r['drop'] for r in a); initial=a[0]['before'];final=a[-1]['after']
    residual=balance(command,greens,dropped,initial,final);close(residual,0)
    denied=Counter(r['reason'] for r in a if r['denied']); drop_reason=defaultdict(float)
    for r in a: drop_reason[r['reason']]+=r['drop']
    rec=dict(run_id=rid,q_ramp=q,seed=seed,treatment=treatment,begin=lo,end=hi,command_credit=command,greens=greens,actual_crossings=sum(r['cross'] for r in a),dropped_credit=dropped,initial_credit=initial,final_credit=final,credit_balance_residual=residual,storage_supply_seconds=sum(r['supply'] for r in a),denied_due_seconds=sum(denied.values()),ideal_unguarded_opportunities=sum(r['ideal_green'] for r in a),ideal_window_count_difference=command-sum(r['ideal_green'] for r in a),denied_reasons_json=json.dumps(denied,sort_keys=True),dropped_credit_same_step_reason_json=json.dumps(drop_reason,sort_keys=True))
    if kind=='evaluation_window':
     ref=index[(rid,lo)]; close(command,float(ref['final_command_credit']));assert rec['actual_crossings']==int(ref['actual_crossings']) and rec['storage_supply_seconds']==300 and rec['denied_due_seconds']==int(ref['denied_due_seconds'])
     assert denied==json.loads(ref['denied_reasons_json']);err=abs(greens-command)/command
     close(err,float(ref['relative_error']));rec['relative_error']=err;rec['engineering_status']='PASS' if err<=0.1 else 'FAIL';assert rec['engineering_status']==ref['engineering_status'];windows.append(rec)
    else: runs.append(rec)
    for reason in sorted(set(denied)|set(drop_reason)):
     reasons.append(dict(run_id=rid,begin=lo,end=hi,scope=kind,selected_reason=reason,category=category(reason),denied_due_seconds=denied[reason],dropped_credit_same_step=drop_reason[reason]))

def write_csv(name,rows):
 f=io.StringIO(newline='')
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 emit(TABLE/name,f.getvalue())
write_csv('run_credit_balance.csv',runs);write_csv('window_credit_balance.csv',windows);write_csv('reason_step_accounting.csv',reasons)
aggregates=[]
for scope in ['whole_control','evaluation_window']:
 for cat in ['safety','receiver','front_readiness_or_receiver_not_uniquely_separable','no_demand','allowed_or_spacing','other']:
  selected=[r for r in reasons if r['scope']==scope and r['category']==cat]
  aggregates.append(dict(scope=scope,category=cat,denied_due_seconds=sum(r['denied_due_seconds'] for r in selected),dropped_credit_same_step=sum(r['dropped_credit_same_step'] for r in selected)))
write_csv('category_step_accounting.csv',aggregates)
assert len(runs)==12 and len(windows)==72
assert Counter(r['engineering_status'] for r in windows)=={'FAIL':71,'PASS':1}
summary={'classification':'TECHNICAL_EXPLORATORY_NOT_FORMAL','base_commit':BASE,'python':platform.python_version(),'script_sha256':sha(Path(__file__)),'raw_rows':50400,'controlled_rows':43200,'runs':12,'windows':72,'window_status_counts':dict(Counter(r['engineering_status'] for r in windows)),'run_rate_qualification':'12 NOT_QUALIFIED per retained authoritative gates','actual_crossings_full_control':total_crossings,'max_step_credit_residual':max_step_residual,'full_command_credit':sum(r['command_credit'] for r in runs),'full_dropped_credit':sum(r['dropped_credit'] for r in runs),'evaluation_command_credit':sum(r['command_credit'] for r in windows),'evaluation_actual_crossings':sum(r['actual_crossings'] for r in windows),'evaluation_dropped_credit':sum(r['dropped_credit'] for r in windows),'pass_windows':[r for r in windows if r['engineering_status']=='PASS'],'max_abs_ideal_window_count_difference':max(abs(r['ideal_window_count_difference']) for r in windows),'input_bindings':bindings,'table_bindings':[{ 'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(TABLE.glob('*.csv'))],'limitations':['Logged reasons are priority-selected, not exhaustive independent constraints. Same-step dropped-credit association is an accounting partition, not recoverable causal service after removing one guard.','Unguarded replay keeps observed final command sequence; it is only scheduler arithmetic. Removing safety would change trajectories and feedback.','Actual crossing counts independently reconciled to raw step brackets; physical/FCD safety is inherited from version-bound FIX02 gates, not freshly rerun here.','Raw outputs remain local-only and immutable; no network/model/controller/parameters/thresholds changed.','R900 endpoint truncation retained; this audit does not re-estimate traffic effects.']}
emit(OUT/'DECOMPOSITION_RECEIPT.json',json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['input_bindings','table_bindings','pass_windows','limitations']},indent=2))
