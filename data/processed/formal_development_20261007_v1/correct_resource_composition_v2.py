"""Preserve alternative equal-three-arm estimate; bind draft60 two-arm composition."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.load((B/'FINAL_DATA_RECEIPT_FIX02.json').open());s=d['stratified_resource_samples'];d['supersedes_resource_composition_only']='FINAL_DATA_RECEIPT_FIX02.json used alternative20each60-run composition; actual draft60 is30OPEN+30T1.'
for n,counts in [('60',{'OPEN':30,'T1':30,'T2':0}),('90',{'OPEN':30,'T1':30,'T2':30})]:
 d['resource_estimates'][n]=dict(runs_by_treatment=counts,wall_mean_minutes=sum(s[t]['mean_wall_s']*count for t,count in counts.items())/60,wall_observed_range_minutes=[sum(s[t][k]*count for t,count in counts.items())/60 for k in ['min_wall_s','max_wall_s']],mean_decimal_GB=sum(s[t]['mean_bytes']*count for t,count in counts.items())/1e9,observed_range_decimal_GB=[sum(s[t][k]*count for t,count in counts.items())/1e9 for k in ['min_bytes','max_bytes']])
d['resource_scope']='Draft60 =30OPEN+30T1; draft90 =30OPEN+30T1+30T2. Current empirical strata OPENn1/T1n6/T2n6. Arithmetic ranges, not confidence intervals or future bounds; setup/analysis/review/retries/changed logging excluded; no run authorization.'
d['correction_script_sha256']=sha(Path(__file__))
with (B/'FINAL_DATA_RECEIPT_FIX02_V2.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
p=B/'DATA_REPORT_FIX02_FINAL.md';text=p.read_text();text=text.replace('Sources/gates/table hashes: FINAL_DATA_RECEIPT_FIX02.json.','Sources/gates/table hashes: FINAL_DATA_RECEIPT_FIX02_V2.json (actual draft resource composition).')
a=text.index('Future equal-treatment-mix projections');z=text.index('\n\n## Reproducibility',a);e=d['resource_estimates']
text=text[:a]+f"Future draft projections use completed current OPEN n=1, T1 n=6, T2 n=6 strata. **60runs =30OPEN+30T1;90runs =30OPEN+30T1+30T2.** Mean arithmetic estimates:60≈{e['60']['wall_mean_minutes']:.2f}min/{e['60']['mean_decimal_GB']:.3f}GB;90≈{e['90']['wall_mean_minutes']:.2f}min/{e['90']['mean_decimal_GB']:.3f}GB. Observed-sample arithmetic ranges:60 {e['60']['wall_observed_range_minutes'][0]:.2f}–{e['60']['wall_observed_range_minutes'][1]:.2f}min/{e['60']['observed_range_decimal_GB'][0]:.3f}–{e['60']['observed_range_decimal_GB'][1]:.3f}GB;90 {e['90']['wall_observed_range_minutes'][0]:.2f}–{e['90']['wall_observed_range_minutes'][1]:.2f}min/{e['90']['observed_range_decimal_GB'][0]:.3f}–{e['90']['observed_range_decimal_GB'][1]:.3f}GB. OPEN n=1 is a material limitation. These are not confidence intervals, upper bounds or approval. Setup, analysis, review, retries and future logging changes are excluded. Prior receipt's20each60-run estimate is preserved as an alternative mix, superseded for the draft projection."+text[z:]
text=text.replace('Refused states and dropped credit are separately retained.','The sole passing window is R750/S23/T1 [2100,2400):43 actual crossings versus46.529768 requested,7.586043%error. That run still fails its overall all-window screen. Refused states and dropped credit are separately retained.')
text=text.replace('Tables: coverage_fix02_final.csv','Tables: shared_exposure_controls_fix02_final.csv(36 control-only class rows for[1200,3000)), coverage_fix02_final.csv')
text+='\n\nVisual verification: mainlineR900 grid, R750/S42/T2 command-risk panel, R900 class-cost panel, endpoint and service-error plots inspected; axes, units and source values agree. All19PNG files pass image decoding and final table/hash checks. Remaining same-template panels were checked programmatically, not individually visually inspected.\n'
with (B/'DATA_REPORT_FIX02_FINAL_V2.md').open('x') as f:f.write(text)
print(json.dumps(d['resource_estimates']))
