"""Render source-bound development coverage, descriptive costs and state plots.

Only complete independently audited new folders are selected. No inference.
"""
import argparse, csv, json, os, sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'matplotlib_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from audit_reuse import sha

TABLE=ROOT/'results/tables/formal_development_20261007_v1'
FIG=ROOT/'results/figures/formal_development_20261007_v1'

def read_csv(path):
    with Path(path).open() as f:return list(csv.DictReader(f))

def dump_csv(path,rows):
    with Path(path).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def old_processed(run):
    if run['treatment']=='T0':return ROOT/'data/processed/stage6_boundary_search_20261002_v1'/run['run_id']
    seed=run['seed'];suffix='' if seed==17 else f'_s{seed}'
    return ROOT/f'data/processed/stage6_safe_actuator{suffix}_v15_audit_20261003_v1'

def capability_status(run,treatment):
    if run is None:return 'NOT_TESTED'
    if treatment=='T0':return 'NOT_APPLICABLE'
    path=run['processed']/'final_command_windows.json'
    if not path.exists():return 'SEPARATE_HISTORICAL_QUALIFICATION'
    windows=json.loads(path.read_text())
    eligible=[w for w in windows if w['eligible_continuous_supply']]
    if not eligible:return 'NOT_TESTED_NO_CONTINUOUS_SUPPLY'
    return 'NOT_QUALIFIED_10PCT' if any(w['engineering_status']=='FAIL' for w in eligible) else 'PASS_ELIGIBLE_WINDOWS_ONLY'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--label',default='final');args=ap.parse_args()
    label=args.label
    assert label.replace('_','').isalnum()
    audit=json.loads((HERE/'reuse_audit.json').read_text());registry={};provenance={};rawsources={}
    for run in audit['runs']:
        if not run['eligible_existing_data']:continue
        q=run['classes'][0]['q_ramp'];key=(q,run['seed'],run['treatment']);processed=old_processed(run)
        s=json.loads((processed/'summary.json').read_text())
        source=Path(run['raw'])/'fcd.xml.gz'
        assert s['source_hashes'][str(source)]==sha(source)
        # Independent class recomputation must agree before using existing state panels.
        classes={r['vehicle_class']:r for r in s['classes']}
        for c in run['classes']:
            for original,own in [('scheduled_system_time_observed_total_s','system_time_T_s'),('external_wait_observed_total_s','source_wait_T_s'),('in_network_observed_total_s','in_network_T_s')]:assert abs(classes[c['vehicle_class']][original]-c[own])<1e-6
        registry[key]=dict(run_id=run['run_id'],processed=processed,raw=Path(run['raw']),classes=s['classes'],reuse=True)
        provenance[str(processed/'summary.json')]=sha(processed/'summary.json');rawsources[str(source)]=sha(source)
    for processed in sorted(HERE.iterdir()):
        if not processed.is_dir() or not(processed/'adapter_provenance.json').exists():continue
        s=json.loads((processed/'summary.json').read_text());p=json.loads((processed/'adapter_provenance.json').read_text());cardpath=next(Path(x) for x,h in s['source_hashes'].items() if Path(x).name=='card.json')
        card=json.loads(cardpath.read_text());assert sha(cardpath)==p['card_sha256']
        q=card.get('ramp_veh_h',card.get('q_ramp_veh_h'));t=card.get('treatment','T1');t='T0' if t=='OPEN' else t
        if q is None:q=750 if card['counts']['R']==500 else 900
        key=(q,card['seed'],t)
        registry[key]=dict(run_id=s['run_id'],processed=processed,raw=Path(card['output']),classes=s['classes'],reuse=False)
        provenance[str(processed/'adapter_provenance.json')]=sha(processed/'adapter_provenance.json')
    failed={}
    for receipt_path in sorted((ROOT/'artifacts/formal_development_20261007_v1/receipts').glob('*.json')):
        r=json.loads(receipt_path.read_text())
        if r.get('status')=='FAILED' and r.get('treatment') in ['T1','T2']:
            failed[(r['ramp_veh_h'],r['seed'],r['treatment'])]=r['run_id']
            provenance[str(receipt_path)]=sha(receipt_path)
    costs=[];coverage=[];comparisons=[]
    for seed in [17,23,42]:
        for q in [900,750]:
            for t in ['T0','T1','T2']:
                run=registry.get((q,seed,t))
                failure=failed.get((q,seed,t))
                coverage.append(dict(q_main=3600,q_ramp=q,seed=seed,treatment=t,status='REUSED_DATA' if run and run['reuse'] else 'NEW_INDEPENDENTLY_AUDITED' if run else 'FAILED_ATTEMPT_NO_EFFECT_DATA' if failure else 'NOT_RUN',run_id=run['run_id'] if run else failure or '',processed=str(run['processed']) if run else '',capability=capability_status(run,t)))
                if not run:continue
                for c in run['classes']:
                    costs.append(dict(q_main=3600,q_ramp=q,seed=seed,treatment=t,run_id=run['run_id'],vehicle_class=c['vehicle_class'],planned=c['planned'],inserted=c['inserted'],arrived=c['arrived'],unfinished=c['unfinished'],undeparted=c['undeparted'],system_time_T_s=c['scheduled_system_time_observed_total_s'],mean_system_time_T_s=c['scheduled_system_time_observed_total_s']/c['planned'],source_wait_T_s=c['external_wait_observed_total_s'],in_network_T_s=c['in_network_observed_total_s']))
            for control,baseline in [('T1','T0'),('T2','T0'),('T2','T1')]:
                c=registry.get((q,seed,control));b=registry.get((q,seed,baseline))
                if not c or not b:continue
                cb={x['vehicle_class']:x for x in c['classes']};bb={x['vehicle_class']:x for x in b['classes']}
                for group in 'MRUX':
                    assert cb[group]['planned']==bb[group]['planned']
                    for field in ['scheduled_system_time_observed_total_s','external_wait_observed_total_s','in_network_observed_total_s']:
                        comparisons.append(dict(q_ramp=q,seed=seed,contrast=control+'-'+baseline,vehicle_class=group,metric=field,baseline=bb[group][field],control=cb[group][field],difference=cb[group][field]-bb[group][field]))
    dump_csv(TABLE/f'coverage_{label}.csv',coverage);dump_csv(TABLE/f'class_costs_{label}.csv',costs)
    if comparisons:dump_csv(TABLE/f'paired_descriptive_{label}.csv',comparisons)
    for q in [750,900]:
        fig,axes=plt.subplots(3,3,figsize=(13,9),sharex=True,sharey=True,layout='constrained');last=None
        for i,seed in enumerate([17,23,42]):
            for j,t in enumerate(['T0','T1','T2']):
                ax=axes[i,j];run=registry.get((q,seed,t));ax.set_title(f'{t} / seed {seed}')
                if run:
                    path=run['processed']/'mainline_cells.csv'
                    reaggregated=HERE/'PANEL_R750_S17_RAW_REAGG/mainline_cells.csv'
                    if (q,seed,t)==(750,17,'T0') and reaggregated.exists():path=reaggregated
                    provenance[str(path)]=sha(path)
                    grid=np.full((22,140),np.nan)
                    for r in read_csv(path):
                        if r['lane_track']=='pooled' and r['speed_mps']:
                            x=int(r['cell']);b=int(float(r['begin'])/30)
                            if 0<=x<22 and 0<=b<140:grid[x,b]=float(r['speed_mps'])
                    last=ax.imshow(grid,origin='lower',aspect='auto',extent=[0,4200,0,2200],vmin=0,vmax=35,cmap='viridis')
                else:ax.text(.5,.5,'Failed attempt; no 4200s result' if (q,seed,t) in failed else 'Not run',transform=ax.transAxes,ha='center',fontsize=9)
                ax.axvline(600,color='white',lw=.5);ax.axvline(3000,color='white',lw=.5)
                if i==2:ax.set_xlabel('Time (s)')
                if j==0:ax.set_ylabel('Mainline position (m)')
        if last is not None:fig.colorbar(last,ax=axes,label='M speed (m/s)')
        fig.suptitle(f'DEVELOPMENT M3600/R{q}: observed M speed, common 30s/100m bins; blank = no sample')
        target=FIG/f'mainline_M3600_R{q}_{label}.png';assert not target.exists();fig.savefig(target,dpi=150);plt.close(fig)
    for (q,seed,t),run in registry.items():
        if t=='T0':continue
        rows=read_csv(run['raw']/'controller_steps.csv');qpath=run['raw']/'queue_override.csv';qrows=read_csv(qpath) if qpath.exists() else None
        selected=rows[600:];times=np.arange(600,4200);rates=np.array([float(r['command_rate_veh_h']) for r in selected]);queue=np.array([int(r['queue_vehicle_count']) for r in selected])
        fig,axes=plt.subplots(3,1,figsize=(11,7),sharex=True,layout='constrained')
        axes[0].plot(times,rates,label='Final command',lw=.8)
        if qrows:
            axes[0].plot(times,[float(r['nominal_clipped_veh_h']) for r in qrows[600:]],label='Nominal ALINEA',lw=.8,alpha=.8)
            active=np.array([r['override_active'].lower()=='true' for r in qrows[600:]])
            axes[2].plot(times,[float(r['risk_extent_m']) for r in qrows[600:]],label='Storage/internal risk extent')
            axes[2].fill_between(times,0,340,where=active,alpha=.12,label='Override active')
            axes[2].axhline(261.03,color='red',ls='--',label='Trigger threshold');axes[2].axhline(102.245,color='green',ls=':',label='Release threshold')
        else:axes[2].text(.5,.5,'Legacy T1: new risk observation not recorded',transform=axes[2].transAxes,ha='center')
        for begin in range(1200,3000,300):
            batch=rows[begin:begin+300];actual=sum(len(json.loads(r['crossing_bracket_ids_json'])) for r in batch)*12
            axes[0].hlines(actual,begin,begin+300,color='black',lw=2,label='Actual crossing rate, fixed 300s' if begin==1200 else None)
        axes[0].set_ylabel('Rate (veh/h)');axes[1].plot(times,queue,lw=.8);axes[1].set_ylabel('R storage vehicles\n(not stopped queue)');axes[2].set_ylabel('Extent (m)');axes[2].set_xlabel('Pre-step command time (s)')
        axes[0].legend(fontsize=8);axes[2].legend(fontsize=8) if qrows else None
        fig.suptitle(f'DEVELOPMENT R{q} / S{seed} / {t}: final command and observed service')
        target=FIG/f'commands_R{q}_S{seed}_{t}_{label}.png';assert not target.exists();fig.savefig(target,dpi=150);plt.close(fig)
        provenance[str(run['raw']/'controller_steps.csv')]=sha(run['raw']/'controller_steps.csv')
        if qrows:provenance[str(qpath)]=sha(qpath)
    for q in [750,900]:
        fig,axes=plt.subplots(1,3,figsize=(13,4.5),layout='constrained',sharey=True)
        colors=['#3575ad','#e7973c','#61a66b','#8867a5'];groups=list('MRUX')
        for ax,seed in zip(axes,[17,23,42]):
            available=[t for t in ['T0','T1','T2'] if (q,seed,t) in registry];positions=np.arange(len(available));bottom=np.zeros(len(available))
            for group,color in zip(groups,colors):
                values=[next(c['scheduled_system_time_observed_total_s'] for c in registry[(q,seed,t)]['classes'] if c['vehicle_class']==group)/3600 for t in available]
                ax.bar(positions,values,bottom=bottom,label=group,color=color);bottom+=np.array(values)
            ax.set_xticks(positions,available);ax.set_title(f'Seed {seed}');ax.set_ylabel('Planned-cohort system time (veh h)')
        axes[-1].legend();fig.suptitle(f'DEVELOPMENT M3600/R{q}: group costs to4200; missing policies not imputed')
        target=FIG/f'class_costs_R{q}_{label}.png';assert not target.exists();fig.savefig(target,dpi=150);plt.close(fig)
    failure_path=HERE/'FAILED_R750_S17_T1_A02_audit3/FAILED_ATTEMPT_AUDIT.json'
    if failure_path.exists():
        x=json.loads(failure_path.read_text());provenance[str(failure_path)]=sha(failure_path)
        v=x['unsafe_follower_evidence']['R_flow.3'];fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained');pos=np.arange(2)
        ax.bar(pos-.18,[v['pre_gap_m'],v['post_gap_m']],.36,label='Observed available distance')
        ax.bar(pos+.18,[v['pre_required_m'],v['post_required_m']],.36,label='Rule required distance')
        ax.set_xticks(pos,['Pre653: green permission','Post654: red interlock']);ax.set_ylabel('Distance (m)');ax.legend()
        ax.set_title('FAILED R750/S17 T1: R_flow.3 pre-rule passes; post-rule fails\nRaw FCD/sensor reconciliation; no complete treatment result')
        target=FIG/f'failed_R750_S17_envelope_{label}.png';assert not target.exists();fig.savefig(target,dpi=150);plt.close(fig)
    with (HERE/f'render_provenance_{label}.json').open('x') as f:json.dump(dict(script_sha256=sha(__file__),sources=provenance,bound_raw_fcd=rawsources,covered=len(registry),expected=18,failed_without_complete_data=len([r for r in coverage if r['status']=='FAILED_ATTEMPT_NO_EFFECT_DATA']),not_run=len([r for r in coverage if r['status']=='NOT_RUN']),classification='DEVELOPMENT_DESCRIPTIVE',no_inference=True,python=sys.version,matplotlib=matplotlib.__version__,numpy=np.__version__,figure_units='M speed m/s; coordinates m; rates veh/h; costs veh h'),f,indent=2);f.write('\n')
    print(json.dumps({'covered':len(registry),'expected':18,'paired_comparison_rows':len(comparisons)}))

if __name__=='__main__':main()
