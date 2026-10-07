"""Final endpoint and service-screen diagnostics, directly from audited tables."""
import csv,hashlib,json,os
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2];T=ROOT/'results/tables/formal_development_20261007_v1';F=ROOT/'results/figures/formal_development_20261007_v1';os.environ.setdefault('MPLCONFIGDIR',str(B/'matplotlib_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 costs=read(T/'class_costs_fix02_final.csv');windows=read(T/'service_windows_fix02_final.csv')
 fig,axes=plt.subplots(1,2,figsize=(12,4),sharey=True,layout='constrained')
 for ax,q in zip(axes,['750','900']):
  keys=[(seed,t) for seed in ['17','23','42'] for t in ['T1','T2']];bottom=np.zeros(6)
  for group,color in [('R','#e7973c'),('U','#61a66b'),('M','#3575ad'),('X','#8867a5')]:
   values=[sum(int(r['unfinished'])+int(r['undeparted']) for r in costs if (r['q_ramp'],r['seed'],r['treatment'],r['vehicle_class'])==(q,seed,t,group)) for seed,t in keys]
   ax.bar(np.arange(6),values,bottom=bottom,label=group,color=color);bottom+=values
  for i,n in enumerate(bottom):ax.text(i,n+.7,str(int(n)),ha='center',fontsize=9)
  ax.set_xticks(np.arange(6),[f'S{s}\n{t}' for s,t in keys]);ax.set_title(f'R{q}');ax.set_ylabel('Vehicles not arrived by4200s');ax.set_ylim(0,100)
 axes[-1].legend(title='Vehicle class');fig.suptitle('DEVELOPMENT FIX02: every endpoint vehicle retained in restricted costs')
 p=F/'endpoint_residuals_fix02_final.png';assert not p.exists();fig.savefig(p,dpi=150);plt.close(fig)
 fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True,sharey=True,layout='constrained')
 for i,q in enumerate(['750','900']):
  for j,t in enumerate(['T1','T2']):
   ax=axes[i,j]
   for seed in ['17','23','42']:
    rr=[w for w in windows if (w['q_ramp'],w['treatment'],w['seed'])==(q,t,seed)];assert len(rr)==6
    ax.plot([int(w['begin'])+150 for w in rr],[100*float(w['relative_error']) for w in rr],marker='o',label='S'+seed)
   ax.axhline(10,color='black',ls='--',label='Registered10% screen');ax.set_title(f'R{q} / {t}');ax.set_ylabel('Absolute service error (%)');ax.set_xlabel('Fixed300s window midpoint (s)');ax.legend(fontsize=8)
 fig.suptitle('DEVELOPMENT FIX02: all fixed continuously supplied windows retained')
 p=F/'service_error_fix02_final.png';assert not p.exists();fig.savefig(p,dpi=150);plt.close(fig)
 with (B/'DIAGNOSTIC_RENDER_RECEIPT_FIX02.json').open('x') as f:json.dump(dict(script_sha256=sha(Path(__file__)),source_sha256={str(T/n):sha(T/n) for n in ['class_costs_fix02_final.csv','service_windows_fix02_final.csv']},outputs={str(F/n):sha(F/n) for n in ['endpoint_residuals_fix02_final.png','service_error_fix02_final.png']}),f,indent=2)
if __name__=='__main__':main()
