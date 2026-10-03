#!/usr/bin/env python3
"""Summarize specified immutable analysis outputs and optional diagnostic figures."""
from __future__ import annotations
import argparse
import csv
import gzip
import itertools
import xml.etree.ElementTree as ET
import json
import math
import re
import os
from pathlib import Path
import tempfile
from analyze import batch_summary,sha,csv_write

def figures(root,run_ids,target):
    os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='stage6-mpl-'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    target=Path(target)
    if target.exists():raise FileExistsError(target)
    source={};arrays={}
    for name in run_ids:
        p=Path(root)/name/'mainline_cells.csv'
        source[str(p.resolve())]=sha(p)
        rr=list(csv.DictReader(p.open()))
        rr=[r for r in rr if r['lane_track']=='pooled' and 100<=float(r['x_start'])<2200]
        if len(rr)!=21*140:raise ValueError(f'{name}: incomplete plotting grid')
        a={key:np.full((21,140),np.nan) for key in ['speed_mps','model_reference_ratio']}
        seen=set()
        for r in rr:
            cell=int(r['cell'])-1;b=int(float(r['begin'])/30)
            if (cell,b) in seen:raise ValueError('duplicate plot grid cell')
            seen.add((cell,b))
            for key in a:
                if r[key]!='':a[key][cell,b]=float(r[key])
        arrays[name]=a
    target.mkdir(parents=True)
    for key,title,vmax in [('speed_mps','M speed (m/s)',36),('model_reference_ratio','M speed / model reference',1.1)]:
        ncols=4 if len(run_ids)==12 else 2 if len(run_ids)==4 else min(3,len(run_ids));nrows=math.ceil(len(run_ids)/ncols)
        fig,axes=plt.subplots(nrows,ncols,figsize=(5*ncols,3.4*nrows),sharex=True,sharey=True,squeeze=False,layout='constrained')
        cmap=plt.get_cmap('viridis').copy();cmap.set_bad('#eeeeee')
        for ax,name in zip(axes.flat,run_ids):
            im=ax.imshow(arrays[name][key],origin='lower',extent=(0,4200,100,2200),aspect='auto',vmin=0,vmax=vmax,cmap=cmap,interpolation='none')
            for t in [600,1200,3000]:ax.axvline(t,color='white',alpha=.65,lw=.7,ls='--')
            for x in [1300,1800]:ax.axhline(x,color='#f6a83b',alpha=.9,lw=.9,ls=':')
            ax.set_title(name);ax.set_xlabel('Simulation time (s)');ax.set_ylabel('Mainline x (m)')
        for ax in list(axes.flat)[len(run_ids):]:ax.set_visible(False)
        fig.colorbar(im,ax=list(axes.flat)[:len(run_ids)],label=title,shrink=.85)
        fig.suptitle(title+' | 100 m × 30 s, exploratory\nWhite: R activation / evaluation start / demand end; orange: core boundaries',fontsize=12)
        fig.savefig(target/(key+'.png'),dpi=170);fig.savefig(target/(key+'.pdf'));plt.close(fig)
    (target/'provenance.json').write_text(json.dumps({'runs':run_ids,'sources':source,'script_sha256':sha(__file__),
      'aggregation':'pooled M vehicle-second weighted; NA is grey; density and R excluded from speed denominator',
      'limits':'Visual diagnostic only; no automatic capacity or queue-source attribution'},indent=2)+'\n')

def compare_pre_activation(raw_root,run_ids,target):
    def steps(run):
        path=Path(raw_root)/run/'outputs/fcd.xml.gz'
        with gzip.open(path,'rb') as f:
            for _,e in ET.iterparse(f,events=('end',)):
                if e.tag!='timestep':continue
                t=float(e.get('time'));rows={v.get('id'):dict(v.attrib) for v in e if v.get('id','').startswith(('M_','U_','X_'))}
                yield t,rows;e.clear()
    result=[]
    for left,right in itertools.combinations(run_ids,2):
        if left.split('_R')[0]!=right.split('_R')[0] or re.search(r'_S(\d+)',left).group(1)!=re.search(r'_S(\d+)',right).group(1):continue
        pre_n=[0,0];pre_diff=0;first={};first_pre=None
        for a,b in itertools.zip_longest(steps(left),steps(right)):
            if a is None or b is None or a[0]!=b[0]:raise ValueError('paired FCD time mismatch')
            t,aa=a;bb=b[1]
            if t<600:pre_n[0]+=len(aa);pre_n[1]+=len(bb)
            for vid in sorted(set(aa)|set(bb)):
                if aa.get(vid)==bb.get(vid):continue
                record=dict(time=t,id=vid,left=aa.get(vid),right=bb.get(vid))
                first.setdefault(vid[0],record)
                if t<600:pre_diff+=1;first_pre=first_pre or record
        result.append(dict(left=left,right=right,pre600_record_counts=pre_n,pre600_different_ID_seconds=pre_diff,first_pre600_difference=first_pre,first_fullrun_difference_by_class=first,
          limitation='Exact stored FCD matching before ramp activation; post-activation divergence is a diagnostic, not an equality gate'))
    target=Path(target)
    if target.exists():raise FileExistsError(target)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps({'comparisons':result,'sources':{str(Path(raw_root)/r/'outputs/fcd.xml.gz'):sha(Path(raw_root)/r/'outputs/fcd.xml.gz') for r in run_ids},'script_sha256':sha(__file__)},indent=2)+'\n')
    return result

def occupancy_diagnostic(root,run_ids,target):
    import statistics
    rows=[];summaries=[];sources={}
    for name in run_ids:
        directory=Path(root)/name;p=directory/'detectors.csv';sources[str(p.resolve())]=sha(p)
        data=list(csv.DictReader(p.open()));z=json.loads((directory/'summary.json').read_text())
        bytime={}
        for r in data:
            if r['source'] not in ['p1_main_down_20_l0.xml','p1_main_down_20_l1.xml']:continue
            bytime.setdefault(float(r['begin']),[]).append(r)
        local=[]
        for begin,rs in sorted(bytime.items()):
            if len(rs)!=2:raise ValueError('missing downstream E1 lane')
            n=sum(float(r['nVehContrib']) for r in rs)
            row=dict(run_id=name,begin=begin,end=begin+30,occupancy_two_lane_mean_pct=sum(float(r['occupancy']) for r in rs)/2,
             flow_two_lane_sum_veh_h=sum(float(r['flow']) for r in rs),nVehContrib=n,
             speed_count_weighted_mps=sum(float(r['speed'])*float(r['nVehContrib']) for r in rs if float(r['nVehContrib'])>0)/n if n else None,
             occupancy_lane0_pct=float(next(r for r in rs if r['source'].endswith('l0.xml'))['occupancy']),occupancy_lane1_pct=float(next(r for r in rs if r['source'].endswith('l1.xml'))['occupancy']))
            local.append(row);rows.append(row)
        eps=z['state']['windows']['active']['P']['episodes'];first=min((r['report_begin'] for r in eps),default=None)
        windows=[('baseline',300,600),('evaluation',1200,3000)]
        if first is not None:
            windows += [('pre_first_supported_P',max(600,first-150),first),('first_supported_P_following150s',first,min(first+150,3000))]
        for label,start,end in windows:
            rs=[r for r in local if start<=r['begin']<end]
            if not rs:continue
            occ=sorted(r['occupancy_two_lane_mean_pct'] for r in rs);n=sum(r['nVehContrib'] for r in rs)
            summaries.append(dict(run_id=name,window=label,begin=start,end=end,bins=len(rs),occupancy_mean_pct=statistics.mean(occ),occupancy_median_pct=statistics.median(occ),
              occupancy_min_pct=min(occ),occupancy_max_pct=max(occ),flow_mean_veh_h=statistics.mean(r['flow_two_lane_sum_veh_h'] for r in rs),
              speed_count_weighted_mps=sum(r['speed_count_weighted_mps']*r['nVehContrib'] for r in rs if r['nVehContrib'])/n if n else None,
              first_supported_P_begin=first))
    target=Path(target)
    if target.exists():raise FileExistsError(target)
    target.mkdir(parents=True);csv_write(target/'downstream_20m_30s.csv',rows);csv_write(target/'window_summary.csv',summaries)
    (target/'provenance.json').write_text(json.dumps({'sources':sources,'script_sha256':sha(__file__),'units':'occupancy percent, arithmetic average of two mainline lanes; sum flows; speed weighted by E1 nVehContrib',
       'scope':'All vehicles crossing detectors, M and R mixed. First P is supported state start, not confirmed clean breakdown onset. S17 exploratory controller calibration only; not critical occupancy estimation.'},indent=2)+'\n')
    return summaries

def seed_summary(rows,target):
    from collections import defaultdict
    groups=defaultdict(list)
    for row in rows:
        if row['analysis_status']!='PASS':raise ValueError('failed run blocks seed aggregation')
        groups[(row['q_main_requested'],row['q_ramp_requested'])].append(row)
    out=[]
    for (m,r),rs in sorted(groups.items()):
        seeds=[x['seed'] for x in rs]
        if len(seeds)!=len(set(seeds)):raise ValueError('duplicate demand/seed')
        item=dict(q_main=m,q_ramp=r,seed_count=len(rs),seeds=json.dumps(sorted(seeds)),inference='descriptive x/n only; not a probability estimate')
        for profile in 'PLS':
            item[profile+'_positive_seeds']=sum(x['evaluation_'+profile+'_seconds']>0 for x in rs)
            item[profile+'_positive_fraction_text']=str(item[profile+'_positive_seeds'])+'/'+str(len(rs))
            item[profile+'_seconds_by_seed']=json.dumps({x['seed']:x['evaluation_'+profile+'_seconds'] for x in rs},sort_keys=True)
        for c in 'MRUX':
            key=c+'_scheduled_system_time_observed_mean_s';vv=[x[key] for x in rs if x[key] is not None]
            item[key+'_min']=min(vv) if vv else None;item[key+'_max']=max(vv) if vv else None
        out.append(item)
    target=Path(target);csv_write(target/'seed_summary.csv',out);(target/'seed_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

def queue_and_handoff(root,run_ids,target):
    queue_rows=[];sources={};handoff=[]
    for name in run_ids:
        directory=Path(root)/name;summary=json.loads((directory/'summary.json').read_text())
        path=directory/'urban_ramp_queue.csv';sources[str(path.resolve())]=sha(path)
        rs=list(csv.DictReader(path.open()));lanes=sorted({r['lane'] for r in rs})
        for lane in lanes:
            for window,start,end in [('whole',0,4200),('evaluation',1200,3000)]:
                lr=[r for r in rs if r['lane']==lane and start<=float(r['begin'])<end]
                for c in 'MRUX':
                    row=dict(run_id=name,lane=lane,window=window,vehicle_class=c)
                    for suffix in ['vehicle_seconds','stopped_seconds','slow5_seconds']:
                        row[suffix]=sum(float(r.get(c+'_'+suffix) or 0) for r in lr)
                    for suffix in ['all','stopped','slow5']:
                        row['max_simultaneous_'+suffix]=max((float(r.get(c+'_max_simultaneous_'+suffix) or 0) for r in lr),default=0)
                    queue_rows.append(row)
        card=next(p for p in summary['source_hashes'] if p.endswith('/card.json'))
        handoff.append(dict(run_id=name,card=card,card_sha256=sha(card),analysis_summary=str((directory/'summary.json').resolve()),analysis_summary_sha256=sha(directory/'summary.json'),
                            class_cohorts=summary['classes'],state=summary['state']['status']))
    csv_write(Path(target)/'queue_summary.csv',queue_rows)
    (Path(target)/'handoff_data_index.json').write_text(json.dumps({'runs':handoff,'queue_sources':sources,
      'queue_definition':'FCD vehicle seconds and max simultaneous vehicles per lane/class; stopped speed<0.1m/s, diagnostic slow speed<5m/s. All nonfreeway connectors included; no physical storage-cross claim. Missing sparse queue cells imply zero observed occupancy under complete FCD.',
      'cost_definition':'Whole scheduled cohort, including external insertion wait. Observed system time ends at arrival or horizon4200; incomplete cohorts retained. Completed trip means labelled separately.',
      'control_status':'No ALINEA or other new control run performed. Candidate baseline cards require a separate prospective matched control plan/review before use.'},indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--processed-root',default='data/processed/stage6_boundary_search_20261002_v1');p.add_argument('--runs',nargs='+',required=True);p.add_argument('--table-out',required=True);p.add_argument('--figure-out');p.add_argument('--raw-root',default='data/raw/stage6_boundary_search_20261002_v1');p.add_argument('--compare-pre600',action='store_true');p.add_argument('--occupancy-out');p.add_argument('--seed-summary',action='store_true');p.add_argument('--handoff',action='store_true')
    a=p.parse_args()
    missing=[n for n in a.runs if not ((Path(a.processed_root)/n/'summary.json').exists() or (Path(a.processed_root)/n/'failure.json').exists())]
    if missing:raise ValueError('Missing analysis results: '+','.join(missing))
    rows=batch_summary(a.processed_root,a.table_out,a.runs)
    if a.seed_summary:seed_summary(rows,a.table_out)
    if a.handoff:queue_and_handoff(a.processed_root,a.runs,a.table_out)
    if a.figure_out:figures(a.processed_root,a.runs,a.figure_out)
    if a.occupancy_out:occupancy_diagnostic(a.processed_root,a.runs,a.occupancy_out)
    if a.compare_pre600:compare_pre_activation(a.raw_root,a.runs,Path(a.table_out)/'pre600_comparison.json')
    print(json.dumps({'runs':len(rows),'tables':a.table_out,'figures':a.figure_out}))
if __name__=='__main__':main()
