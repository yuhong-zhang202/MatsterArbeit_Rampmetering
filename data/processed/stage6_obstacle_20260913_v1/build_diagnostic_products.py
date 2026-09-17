"""Derived descriptive tables and four scientific figures from verified S6-A tables."""
from pathlib import Path
import csv,json,hashlib,itertools,os
from collections import defaultdict,Counter
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
TABLE=ROOT/'results/tables/stage6_obstacle_20260913_v1';FIG=ROOT/'results/figures/stage6_obstacle_20260913_v1'
os.environ.setdefault('MPLCONFIGDIR',str(BASE/'matplotlib_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
def rows(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(name,data,base=TABLE):
    with (base/name).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def main():
    assert json.loads((BASE/'independent_verification.json').read_text())['status']=='passed'
    sums=rows(TABLE/'run_summary.csv');runids=[r['run_id'] for r in sums];windows={'A':(0,1500),'B':(300,1500),'Post':(1500,2700),'Full':(0,2700)}
    files=rows(BASE/'source_file_inventory.csv');tls={}
    for run in runids:
        p=next(r['path'] for r in files if r['run_id']==run and r['source_suffix']=='outputs/tls_states.xml')
        tls[run]={float(n.get('time')):n.get('state')[0] for _,n in ET.iterparse(p,events=('end',)) if n.tag=='tlsState'}
    reg=defaultdict(lambda:[0,0,0,None,None]);shared=[]
    with (TABLE/'lane_class_time.csv').open(newline='') as f:
        for (run,t),group in itertools.groupby(csv.DictReader(f),key=lambda r:(r['run_id'],float(r['time_s']))):
            cells=list(group);regions=defaultdict(lambda:[0,0,None,None])
            for r in cells:
                n=int(r['present']);stopped=int(r['stopped']);key=(r['region'],r['class']);a=regions[key];a[0]+=n;a[1]+=stopped
                if r['min_pos_m']!='':a[2]=float(r['min_pos_m']) if a[2] is None else min(a[2],float(r['min_pos_m']));a[3]=float(r['max_pos_m']) if a[3] is None else max(a[3],float(r['max_pos_m']))
            for (region,c),(n,stop,pmin,pmax) in regions.items():
                for w,(b,e) in windows.items():
                    if b<=t<e:
                        a=reg[(run,w,region,c)];a[0]+=n;a[1]+=stop;a[2]+=int(stop>0)
                        if stop and a[3] is None:a[3]=t
                        if stop:a[4]=t
            R=regions[('shared_approach','R')][1];U=regions[('shared_approach','U')][1]
            shared.append({'run_id':run,'time_s':t,'R_stopped_count':R,'U_stopped_count':U,'RU_shared':int(R>0 and U>0),'TLS_movement0':tls[run][t],'value_state':'observed_zero' if R==U==0 else 'observed','coverage':'complete','reason':'sampled cooccurrence; TLS state is upstream movement context'})
    regionrows=[{'run_id':k[0],'window':k[1],'region':k[2],'class':k[3],'present_vehicle_seconds':v[0],'stopped_vehicle_seconds':v[1],'stopped_labels':v[2],'first_stopped_label':v[3],'last_stopped_label':v[4],'count_value_state':'observed_zero' if v[1]==0 else 'observed','event_time_value_state':'not_applicable' if v[3] is None else 'observed','coverage':'complete','reason':'no stopped event is explicit with complete labels; first/last do not imply uninterrupted episode'} for k,v in reg.items()]
    write('region_window_diagnostics.csv',regionrows);write('shared_label_timeline.csv',shared)
    original=ROOT/'results/tables/stage4_qmain_sequential_20260912_v1/final/revision_03/final_ejmi_envelope_checks.csv'
    ejmi=rows(original)
    for r in ejmi:r.update({'source_path':str(original.relative_to(ROOT)),'source_sha256':sha(original),'role':'historical_registered_output_unchanged_not_new_rule','value_state':'observed'})
    write('historical_ejmi_components.csv',ejmi)
    # Long-form metric registry defines each counter independently.
    registry=[]
    definitions=[('q_contrib_vehph','nVehContrib','3600*sum(nVehContrib)/seconds','veh/h','count zero with complete intervals'),('q_entered_vehph','nVehEntered','3600*sum(nVehEntered)/seconds','veh/h','count zero with complete intervals'),('speed_contribution_weighted_mps','speed,nVehContrib','sum(speed*nVehContrib)/sum(nVehContrib)','m/s','null/no_contributors if denominator zero'),('occupancy_lane_mean_percent','occupancy','duration weighted mean across two lanes','percent','never summed or called density'),('mean_sample_speed_mps','FCD.speed','sum sampled speeds / vehicle-label count','m/s','null/no_contributors when region empty'),('stopped_vehicle_seconds','FCD.speed<=0.1','sum stopped vehicle labels * 1s','vehicle s','zero only over fully checked frames'),('RU_shared_labels','FCD.speed and lane and ID class','intersection of stopped-R and stopped-U labels on shared lane','sampled s','exposure not causal loss'),('distance_to_main_up_end_m','tripinfo.departPos,compiled length','lane length - actual M departPos','m','M only; not the full merge connector'),('outside_at_endpoint','demand number,tripinfo.depart','planned full cohort - entered before endpoint','veh','only1500/2700; no unverified intermediate schedule curve')]
    for mid,raw,rule,unit,limit in definitions:registry.append({'metric_id':mid,'source_field':raw,'aggregation_rule':rule,'unit':unit,'window_rule':'registered A/B/Post/Full or explicit raw label','cohort':'declared vehicle class; downstream E1 mixes M/R','qualification_limit':limit,'status':'exploratory_not_formal_selected'})
    write('metric_registry.csv',registry,BASE)
    allruns='|'.join(runids)
    evidence=[
      ('H1','EJMI sufficient rule or narrow observations may miss other impairment','complete','not_identified','supported_as_candidate','8/8 historical candidate-window rows fail aggregate EJMI; all 12 runs have zero M technical stopped samples, but local FCD speed distributions differ across regions.','EJMI negativity is preserved; slow samples alone are not approved impairment. FCD and E1 speeds have different weighting and populations.','A-MREG|A-SECTION|A-EJMI','Define intended M estimand and an eligible reference before new validation; do not relabel old EJMI.'),
      ('H2','Actual near-merge insertion limits traveled upstream observation domain','complete','observed','supported_as_candidate','All 16622 M actual entries are 0.10-286.75m from main_up end, despite 1394.87m named upstream lane.','This confirms limited realized feeder travel, not that extending geometry or changing insertion will solve Q2/Q4.','A-ENTRY|A-SUMMARY','Priority candidate: specify intended actual entry/observation domain; compare one registered insertion/observation intervention only if scientifically selected.'),
      ('H3','Merge priority or lane-changing restrictions may limit R admission','incomplete','not_identified','supported_as_candidate','R first-downstream counts and upstream expansion are observed; static priority evidence is supplied by engineering.','No raw lane-change/gap-acceptance log; FCD does not establish causal behavioral rule or accepted-gap distribution.','A-RPASS|A-RPROP|A-REGION','Use static engineering findings and entry-domain diagnosis to select one discriminating contrast; do not tune multiple behavior rules.'),
      ('H4','Downstream supply or exit boundary may dominate observations','complete','not_identified','weakened','No M <=0.1m/s sample anywhere on its observed route in any of 12 complete trajectories; downstream records and arrivals remain available.','This weakens a stopped-M queue-at-exit explanation only. Non-stopped speed restriction and detailed downstream effects are not excluded.','A-MREG|A-REGION|A-SECTION','Retain downstream as a check in a selected candidate; do not prioritize boundary redesign solely from current data.'),
      ('H5','Finite loading and delayed entry affect demand-window interpretation','complete','observed','supported_as_candidate','All 12 runs retain R/U entry after1500s; R late entry9-181 and U9-90 vehicles per run; final arrivals1859-2558s.','Post is not zero-inflow recovery; successful full clearance does not justify1500s demand duration or warm-up.','A-ENDPOINT|A-CLASSWINDOW|A-ENTRY','Any new candidate must register symmetric finite horizons considering changed travel time and delayed entry, not copy old sufficiency.'),
      ('H6','TLS and shared urban queue context confound U exposure interpretation','complete','observed','supported_as_candidate','All 12 runs have R/U shared stopped labels under green, red and yellow movement0 contexts.','Green-labeled shared stopping does not isolate ramp-caused delay; TLS is upstream, with unverified within-step ordering.','A-SHARED|A-SHAREDLABEL|A-REGION','Preserve movement-specific TLS and U outcomes; no causal U-loss gate or signal retiming is justified by cooccurrence alone.')]
    diag=[]
    for hid,claim,cov,phen,status,observation,limit,eid,nxt in evidence:diag.append({'hypothesis_id':hid,'claim':claim,'run_ids':allruns,'coverage_status':cov,'phenomenon_status':phen,'candidate_status':status,'observed_result':observation,'alternative_or_limit':limit,'evidence_ids':eid,'next_discriminating_action':nxt,'decision_status':'advisory_pending_scientific_review'})
    write('obstacle_diagnosis.csv',diag,BASE)
    # All four figures use verified table values; common scales, explicit no-data masks.
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':160})
    made=[]
    fig,ax=plt.subplots(figsize=(10,6.5));y=np.arange(12)
    for i,r in enumerate(sums):ax.plot([float(r['M_distance_to_main_up_end_min_m']),float(r['M_distance_to_main_up_end_max_m'])],[i,i],color='#526b87',lw=3);ax.scatter(float(r['M_distance_mean_m']),i,color='#bd4f39',s=25,zorder=3)
    ax.set_yticks(y,[r['run_id']+'  (n='+r['M_count']+')' for r in sums]);ax.invert_yaxis();ax.set_xlim(0,310);ax.set_xlabel('Actual M remaining distance to upstream-lane end [m]');ax.set_title('Observed insertion: ranges and means for all M vehicles\nNominal main_up lane length = 1394.87 m; connector excluded');ax.grid(axis='x',alpha=.25);fig.tight_layout();made.append(('entry_domain.png',fig))
    st=rows(TABLE/'M_space_time_30s.csv');fig,axes=plt.subplots(1,3,figsize=(15,6),sharey=True,layout='constrained');regions=['mainline_origin_observation','mainline_merge_internal','mainline_downstream'];labels=['Traveled upstream portion','Merge-internal lanes','Downstream lanes'];cmap=plt.get_cmap('viridis').copy();cmap.set_bad('#dedede')
    for ax,region,label in zip(axes,regions,labels):
        mat=np.full((12,90),np.nan)
        for r in st:
            if r['region']==region and r['mean_sample_speed_mps']!='':mat[runids.index(r['run_id']),int(float(r['bin_begin'])/30)]=float(r['mean_sample_speed_mps'])
        im=ax.imshow(mat,aspect='auto',extent=[0,2700,11.5,-.5],vmin=15,vmax=36,cmap=cmap,interpolation='nearest');ax.axvline(1500,color='white',lw=1);ax.set_title(label);ax.set_xlabel('Time [s]');ax.set_yticks(range(12),runids)
    fig.colorbar(im,ax=axes,label='M vehicle-label mean speed [m/s]');fig.suptitle('30 s FCD summaries; gray = no M contributors, not zero speed\nAll-run M technical stopped samples (<=0.1 m/s): 0');made.append(('M_space_time.png',fig))
    fig,ax=plt.subplots(figsize=(12,6));colors={'G':'#24845e','g':'#24845e','r':'#bc4a46','y':'#dca638','Y':'#dca638'}
    for i,run in enumerate(runids):
        for phase in ['G','r','y']:
            ts=[float(r['time_s']) for r in shared if r['run_id']==run and r['RU_shared']==1 and r['TLS_movement0']==phase]
            ax.scatter(ts,[i]*len(ts),s=3,color=colors[phase],marker='|',label={'G':'Green','r':'Red','y':'Yellow'}[phase] if i==0 else None)
    ax.set_yticks(range(12),runids);ax.invert_yaxis();ax.set_xlim(0,2700);ax.axvline(1500,color='#343434',ls='--',lw=1);ax.set_xlabel('Raw FCD/TLS label time [s]');ax.set_title('Shared-road stopped R and U cooccurrence\nColor = upstream TLS movement0 context; no causal attribution');ax.legend(ncol=3,loc='upper right');fig.tight_layout();made.append(('RU_TLS_exposure.png',fig))
    fig,axes=plt.subplots(1,2,figsize=(13,6),sharey=True)
    for i,r in enumerate(sums):
        axes[0].scatter(float(r['last_departure_s']),i,color='#a8512f',s=30,label='Last entry' if i==0 else None);axes[0].scatter(float(r['last_arrival_s']),i,color='#294e78',s=30,label='Last arrival' if i==0 else None)
        axes[1].barh(i-.16,float(r['R_late_departures']),height=.3,color='#bc4d3a',label='R after demand end' if i==0 else None);axes[1].barh(i+.16,float(r['U_late_departures']),height=.3,color='#247c83',label='U after demand end' if i==0 else None)
    axes[0].set_yticks(range(12),runids);axes[0].invert_yaxis();axes[0].axvline(1500,ls='--',color='gray');axes[0].axvline(2700,ls=':',color='gray');axes[0].set_xlim(1400,2750);axes[0].set_xlabel('Time [s]');axes[1].set_xlabel('Vehicles entering at/after 1500 s');axes[0].legend();axes[1].legend();fig.suptitle('Finite-horizon accounting: all runs clear, all retain late R/U entry\n1500 s demand end; 2700 s observation end');fig.tight_layout();made.append(('time_and_late_entry.png',fig))
    figure_records=[]
    for name,fig in made:
        path=FIG/name
        if path.exists():raise FileExistsError(path)
        fig.savefig(path,bbox_inches='tight');plt.close(fig);figure_records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'verification':'source tables independently checked; visual inspection pending'})
    evidencepaths={'A-ENTRY':TABLE/'entry_vehicle_records.csv','A-SUMMARY':TABLE/'run_summary.csv','A-MREG':TABLE/'M_region_window.csv','A-SECTION':TABLE/'section_window_metrics.csv','A-EJMI':TABLE/'historical_ejmi_components.csv','A-RPASS':TABLE/'R_passage_events.csv','A-RPROP':TABLE/'R_region_propagation.csv','A-REGION':TABLE/'region_window_diagnostics.csv','A-ENDPOINT':TABLE/'endpoint_accounting.csv','A-CLASSWINDOW':TABLE/'class_window_counts.csv','A-SHARED':TABLE/'shared_exposure.csv','A-SHAREDLABEL':TABLE/'shared_label_timeline.csv'}
    write('diagnostic_evidence_index.csv',[{'evidence_id':eid,'path':str(p.relative_to(ROOT)),'sha256':sha(p),'locator':'run_id/window/region/metric columns as applicable','scope':'exploratory fixed12 archives; no prospective validation or causal conclusion'} for eid,p in evidencepaths.items()],BASE)
    for d in diag:assert all(eid in evidencepaths for eid in d['evidence_ids'].split('|'))
    with (BASE/'diagnostic_products_verification.json').open('x') as f:json.dump({'status':'produced_pending_scientific_and_visual_review','hypotheses':6,'evidence_ids_resolved':len(evidencepaths),'region_window_rows':len(regionrows),'shared_label_rows':len(shared),'historical_EJMI_rows':len(ejmi),'figures':figure_records,'code_sha256':sha(Path(__file__)),'simulation_starts':0},f,indent=2)
if __name__=='__main__':main()
