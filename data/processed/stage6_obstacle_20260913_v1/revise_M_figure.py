"""Preserve first figure; widen color limits to include all observed bin means."""
from pathlib import Path
import csv,os,json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(BASE/'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
TABLE=ROOT/'results/tables/stage6_obstacle_20260913_v1';FIG=ROOT/'results/figures/stage6_obstacle_20260913_v1'
with (TABLE/'run_summary.csv').open() as f:runs=[r['run_id'] for r in csv.DictReader(f)]
with (TABLE/'M_space_time_30s.csv').open() as f:rows=list(csv.DictReader(f))
values=[float(r['mean_sample_speed_mps']) for r in rows if r['mean_sample_speed_mps']]
assert min(values)>=20 and max(values)<=38
fig,axes=plt.subplots(1,3,figsize=(15,6),sharey=True,layout='constrained');cmap=plt.get_cmap('viridis').copy();cmap.set_bad('#dedede')
for ax,region,label in zip(axes,['mainline_origin_observation','mainline_merge_internal','mainline_downstream'],['Traveled upstream portion','Merge-internal lanes','Downstream lanes']):
    mat=np.full((12,90),np.nan)
    for r in rows:
        if r['region']==region and r['mean_sample_speed_mps']:mat[runs.index(r['run_id']),int(float(r['bin_begin'])/30)]=float(r['mean_sample_speed_mps'])
    im=ax.imshow(mat,aspect='auto',extent=[0,2700,11.5,-.5],vmin=20,vmax=38,cmap=cmap,interpolation='nearest');ax.axvline(1500,color='white',lw=1);ax.set_title(label);ax.set_xlabel('Time [s]');ax.set_yticks(range(12),runs)
fig.colorbar(im,ax=axes,label='M vehicle-label mean speed [m/s]');fig.suptitle('30 s FCD summaries; gray = no M contributors, not zero speed\nAll-run M technical stopped samples (<=0.1 m/s): 0')
path=FIG/'M_space_time_revision_02.png'
if path.exists():raise FileExistsError(path)
fig.savefig(path,dpi=160,bbox_inches='tight');plt.close(fig)
with (BASE/'M_figure_revision_02.json').open('x') as f:json.dump({'supersedes':'results/figures/stage6_obstacle_20260913_v1/M_space_time.png','current':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reason':'First color maximum36 clipped five observed bin means; revised range20..38 contains all values','actual_min':min(values),'actual_max':max(values),'data_changed':False},f,indent=2)
