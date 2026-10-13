"""Derive finite common-support summaries from the single independent actual audit."""
import csv,json,pathlib,hashlib
from fractions import Fraction
ROOT=pathlib.Path.cwd();OUT=ROOT/'data/processed/cumulative_full_catalogue_implementation_20261014_v1/native_actual_v1';ENG=ROOT/'artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/native_execution_v1'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 with (OUT/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
d=load(OUT/'ACTUAL_RESULTS_V1.json');cycles=d['accounting']['cycles'];entries=d['independent_actual_entries'];assert d['last_ACK']==d['last_accounted']==1296 and len(cycles)==10 and len(entries)==20
blocks=[]
for b,e in ((1200,1248),(1248,1296)):
 cs=[c for c in cycles if b<=c['begin_s'] and c['end_s']<=e];xs=[x for x in entries if b<=x['time_begin_s']<e]
 C=Fraction(750*(e-b),3600);capplied=sum((Fraction(7200,c['period_s'])*(c['end_s']-c['begin_s'])/3600 for c in cs),Fraction(0));E=sum(c['E'] for c in cs);N=len(xs)
 assert len(cs)==5 and all(c['completed'] for c in cs) and C==capplied==E==N==10
 assert all(x['motion']=='G' for x in xs)
 blocks.append(dict(begin_s=b,end_s=e,periods_s=[c['period_s'] for c in cs],C_exact=str(C),C_applied_exact=str(capplied),E=E,N=N,actual_veh_h=3600*N/(e-b),entry_ids=[x['vehicle_id'] for x in xs],partial=False))
with (OUT/'ACTUAL_CYCLES_V1.csv').open('x',newline='') as f:
 cols=['begin_s','end_s','period_s','G_s','y_s','r_s','N_G','N_y','N_r','E','N','complete','C_minus_N_exact_at_end'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();Ncum=0
 for c in cycles:
  Ncum+=c['N'];x=c['phase_exposure_s'];w.writerow(dict(begin_s=c['begin_s'],end_s=c['end_s'],period_s=c['period_s'],G_s=x['G'],y_s=x['y'],r_s=x['r'],N_G=c['N_G'],N_y=c['N_y'],N_r=c['N_r'],E=c['E'],N=c['N'],complete=c['completed'],C_minus_N_exact_at_end=str(Fraction(750*(c['end_s']-1200),3600)-Ncum)))
receipt=load(ENG/'EXECUTION_RECEIPT_V1.json');checks={};binder=load(ENG/'ENGINEERING_DELIVERY_BINDING_V1.json')
for name,h in binder['files_sha256'].items():
 actual=sha(ROOT/name);checks[name]={'sha256':actual,'match':actual==h}
assert all(x['match'] for x in checks.values())
write('TWO_COMPLETE_BLOCKS_V1.json',{'classification':'FINITE_FIXED750_ONE_SEED_NOT_LONGRUN_QUALIFICATION','blocks':blocks,'whole_window':d['accounting']['accounting'],'independent_entries':20,'all_body_clear':len(d['body_first_clear_ACK'])==20 and not d['body_censored_ids'],'normal_terminal_arrivals':len(d['terminal_results']),'normal_terminal_all_PASS':all(x['status']=='PASS' for x in d['terminal_results']),'future_unobserved':{'N':None,'E':None,'native_safety':None},'native_safety_proven':False,'rate_qualified':False})
write('ACTUAL_AUDIT_COMMAND_RECEIPT_V1.json',{'command':'.venv/bin/python -B scripts/cumulative_full_catalogue_audit_20261014_v1/actual.py --manifest artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/native_execution_v1/RAW_FINAL_SHA256_V1.json --card artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/packages_v1/UA_CUMULATIVE_FULL750_S17_01/card.json --output data/processed/cumulative_full_catalogue_implementation_20261014_v1/native_actual_v1','exec_session_id':85264,'actual_exit_code':0,'attempts':1,'audit_elapsed_s':None,'status':d['status'],'actual_reader_sha256':sha(ROOT/'scripts/cumulative_full_catalogue_audit_20261014_v1/actual.py'),'result_sha256':sha(OUT/'ACTUAL_RESULTS_V1.json'),'engineering_binder_checks':checks,'native_CLI_returncode':receipt['CLI_returncode'],'native_EOF_returncode':receipt['native_EOF_returncode'],'source_test_basis':'card-bound exact125 snapshot; no extra offline test suite in postreview','native_starts_by_data_agent':0,'raw_verification':'single actual reader verified174 files; extraction did not repeat raw scan'})
print('BOUNDED_SUMMARY_PASS',len(checks),'engineeringbindings',blocks)
