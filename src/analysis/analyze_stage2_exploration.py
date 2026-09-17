"""Archive-only analysis for the fixed Stage 2 completion batch.

No simulation imports or subprocesses. Nominal flow times are diagnostic checks,
never a reconstructed schedule for unobserved vehicles.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import json
import math
import posixpath
from pathlib import Path
import shlex
import sys
import xml.etree.ElementTree as ET

from build_stage2_g1_diagnostic import (digest, e1_row, check_intervals,
    summarize_e1, crossing_event, reserve_directories)

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ('M', 'R', 'U', 'X')
WINDOWS = {'Full': (0,2700), 'A': (0,1500), 'B': (300,1500), 'Post': (1500,2700)}
DETECTORS = {'merge_upstream_e1_l0':'main_up_0', 'merge_upstream_e1_l1':'main_up_1',
             'mainline_merge_entry_e1_l0':':freeway_merge_1_0', 'mainline_merge_entry_e1_l1':':freeway_merge_1_1',
             'merge_downstream_e1_l0':'main_down_0', 'merge_downstream_e1_l1':'main_down_1'}
VEHICLE_FIELDS = ['run_id','vehicle_id','class','planned_time_s','reported_schedule_s','plan_source','actual_depart_s','arrival_s','departDelay_s','completed_duration_s','status','observation_end_s','schedule_time_status']
COHORT_FIELDS = ['run_id','class','time_s','planned_before','entered_before','arrived_before','in_network_before','outside_confirmed','unaccounted_count','plan_count_status','schedule_time_status','departure_coverage_status','arrival_coverage_status','fcd_available','fcd_raw_in_network','fcd_raw_stopped','semantics']
MERGE_FIELDS = ['run_id','vehicle_id','previous_time_s','previous_lane','first_downstream_time_s','first_downstream_lane','interval_semantics','time_precision','boundary_30s_ambiguous','status','reason']
WINDOW_FIELDS = ['run_id','family','entity','window','metric','value','unit','denominator']


def dump(path, value):
    with Path(path).open('x') as f: json.dump(value,f,indent=2,allow_nan=False); f.write('\n')


def table(path, rows, fields):
    with Path(path).open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


class ArchiveResolver:
    def __init__(self, map_path, project_root=ROOT):
        self.map_path=Path(map_path).resolve();self.project=Path(project_root).resolve()
        self.mapping=json.loads(self.map_path.read_text())
        if self.mapping.get('archive_status')!='complete': raise ValueError('Archive is not complete')
        self.root=(self.project/self.mapping['archive_runtime_relative_path']).resolve()
        if self.project not in self.root.parents: raise ValueError('Archive escapes project')
        self.original=posixpath.normpath(self.mapping['source_runtime_path'])
        self.files={};self.hashes={}
        for entry in self.mapping['file_map']:
            raw=self.project/entry['archive_relative_path'];path=raw.resolve()
            if self.root not in path.parents or raw.is_symlink(): raise ValueError('Archive path escapes attempt or is symlink')
            if any(p.is_symlink() for p in raw.parents if p!=self.project): raise ValueError('Archive symlink ancestor')
            key=posixpath.normpath(entry['original_absolute_path'])
            if not key.startswith(self.original+'/') or key in self.files: raise ValueError('Invalid/duplicate original source mapping')
            if digest(path)!=entry['sha256']: raise ValueError('Archive source hash mismatch')
            self.files[key]=path;self.hashes[str(path)]=entry['sha256']
    def resolve(self, original_path):
        value=str(original_path)
        key=posixpath.normpath(value if value.startswith('/') else self.original+'/'+value)
        if key not in self.files: raise ValueError(f'No archive mapping; original fallback prohibited: {key}')
        return self.files[key]
    def verify(self):
        for path,expected in self.hashes.items():
            if digest(path)!=expected: raise ValueError('Archive source changed during analysis')


def category(vid):
    parts=vid.split('_flow.')
    if len(parts)!=2 or parts[0] not in CLASSES or not parts[1].isdigit(): raise ValueError(f'Unknown vehicle ID: {vid}')
    return parts[0]


def finite(value):
    v=float(value)
    if not math.isfinite(v): raise ValueError('Nonfinite numeric value')
    return v


def classify(record, confirmed_not_entered=False):
    if record is None: return 'not_entered_confirmed' if confirmed_not_entered else 'record_missing_unknown'
    if record['depart']<0:return 'record_missing_unknown'
    return 'arrived' if record['arrival']>=0 else 'entered_unfinished'


def endpoint_counts(planned,entered,arrived,coverage):
    if min(planned,entered,arrived)<0 or not arrived<=entered<=planned: raise ValueError('Inconsistent endpoint counts')
    return {'outside_confirmed':planned-entered if coverage else None,
            'in_network':entered-arrived if coverage else None,
            'unaccounted_count':0 if coverage else planned-entered}


def before(value,t):return value is not None and 0<=value<t


def read_trips(path):
    records={}
    for node in ET.parse(path).getroot().findall('tripinfo'):
        vid=node.attrib['id'];category(vid)
        if vid in records: raise ValueError('Duplicate trip ID')
        records[vid]={k:finite(node.attrib[k]) for k in ('depart','arrival','departDelay','duration')}
        if records[vid]['arrival']>=0 and records[vid]['arrival']<records[vid]['depart']: raise ValueError('Arrival precedes departure')
    return records


def read_fcd(path,route_ids):
    frames={};observed=set();previous={};events={};sample_counts=Counter()
    for _,step in ET.iterparse(path,events=('end',)):
        if step.tag!='timestep':continue
        t=finite(step.attrib['time'])
        if t in frames or (frames and t<=next(reversed(frames))): raise ValueError('Duplicate/nonmonotonic FCD time')
        counts=Counter();stopped=Counter();seen=set()
        for v in step:
            a=v.attrib;vid=a['id'];c=category(vid);lane=a['lane'];speed=finite(a['speed'])
            if vid in seen:raise ValueError('Duplicate vehicle in FCD frame')
            seen.add(vid);observed.add(vid);counts[c]+=1;stopped[c]+=int(speed<=.1)
            sample_counts[(lane,c)]+=1
            if c=='R':
                if lane.startswith('main_down_') and vid not in events:events[vid]=crossing_event(vid,previous.get(vid),(t,lane))
                previous[vid]=(t,lane)
        frames[t]={'counts':dict(counts),'stopped':dict(stopped)}
        step.clear()
    if any(t<0 or t>=2700 or t!=int(t) for t in frames):raise ValueError('Unexpected FCD time domain')
    return frames,observed,events,sample_counts


def analyze_run(run,resolver):
    rid=run['run_id'];summary=json.loads(resolver.resolve('summary.json').read_text());cmd=summary['sumo_command']
    def option(flag):return cmd[cmd.index(flag)+1]
    if int(option('--seed'))!=run['seed'] or float(option('--end'))!=2700:raise ValueError('Seed/end mismatch')
    if '1.26.0' not in summary['sumo_version']:raise ValueError('Unapproved SUMO version')
    config=ET.parse(resolver.resolve(option('-c'))).getroot()
    demand=ET.parse(resolver.resolve(config.find('input/route-files').attrib['value'])).getroot()
    net=ET.parse(resolver.resolve(config.find('input/net-file').attrib['value'])).getroot()
    add=ET.parse(resolver.resolve(config.find('input/additional-files').attrib['value'])).getroot()
    flows={n.attrib['id'].split('_')[0]:n.attrib for n in demand.findall('flow')}
    if set(flows)!=set(CLASSES):raise ValueError('Missing/extra flow class')
    planned={c:int(flows[c]['number']) for c in CLASSES}
    if any(float(f['begin'])!=0 or float(f['end'])!=1500 for f in flows.values()):raise ValueError('Demand window mismatch')
    requested=summary['simulation']['requested_demand_vehph']
    if requested!={'M':run['q_main'],'R':run['q_ramp'],'U':run['q_urban'],'X':run['q_x']}:raise ValueError('Demand identity mismatch')
    loops={n.attrib['id']:n for n in add.findall('inductionLoop')}
    if set(loops)!=set(DETECTORS):raise ValueError('Six detector identities required')
    e1=[];wr=[];independent_checks=0
    def metric(family,entity,window,name,value,unit,denom=None):
        wr.append(dict(zip(WINDOW_FIELDS,[rid,family,entity,window,name,value,unit,denom])))
    for ident,node in loops.items():
        lane=node.attrib['lane']
        if lane!=DETECTORS[ident]:raise ValueError('Detector lane mismatch')
        if ident.startswith('mainline_merge_entry'):
            connections=[n for n in net.findall('connection') if n.get('via')==lane]
            if len(connections)!=1 or connections[0].get('from')!='main_up' or connections[0].get('to')!='main_down':raise ValueError('Internal detector topology mismatch')
        path=resolver.resolve(node.attrib['file']);nodes=ET.parse(path).getroot().findall('interval')
        block=[e1_row(n.attrib,ident,lane) for n in nodes];check_intervals(block)
        role='origin_insertion_contaminated' if ident.startswith('merge_upstream') else 'aggregate_M_merge_entry' if ident.startswith('mainline_merge_entry') else 'downstream_passage'
        for r in block:r.update(run_id=rid,measurement_role=role)
        e1.extend(block)
        for name,(a,b) in WINDOWS.items():
            s=summarize_e1(block,a,b)
            for field,unit in [('flow_vehph','veh/h'),('speed_mps','m/s'),('occupancy_pct','%'),('nVehContrib','veh')]:
                metric('E1',ident,name,field,s[field],unit,s['speed_contribution_denominator'] if field=='speed_mps' else s['covered_seconds'])
            metric('E1',ident,name,'nVehEntered',sum(r['nVehEntered'] for r in block if a<=r['begin_s'] and r['end_s']<=b),'veh')
            # Independent XML arithmetic for every published detector/window.
            chosen=[n for n in nodes if a<=float(n.get('begin')) and float(n.get('end'))<=b]
            n=sum(int(n.get('nVehContrib')) for n in chosen)
            if n!=s['nVehContrib'] or abs(n*3600/(b-a)-s['flow_vehph'])>1e-8:raise ValueError('Independent E1 count/flow mismatch')
            valid=[n for n in chosen if int(n.get('nVehContrib'))>0 and float(n.get('speed'))>=0]
            w=sum(int(n.get('nVehContrib')) for n in valid)
            if w and abs(sum(float(n.get('speed'))*int(n.get('nVehContrib')) for n in valid)/w-s['speed_mps'])>1e-10:raise ValueError('Independent E1 speed mismatch')
            independent_checks+=1
    for name,bounds in WINDOWS.items():
        s=[summarize_e1([r for r in e1 if r['detector_id']==ident],*bounds) for ident in loops if ident.startswith('mainline_merge_entry')]
        w=sum(v['speed_contribution_denominator'] for v in s)
        metric('E1_group','internal_M',name,'flow_vehph',sum(v['flow_vehph'] for v in s),'veh/h',bounds[1]-bounds[0])
        metric('E1_group','internal_M',name,'speed_mps',sum(v['speed_mps']*v['speed_contribution_denominator'] for v in s if v['speed_mps'] is not None)/w if w else None,'m/s',w)
        metric('E1_group','internal_M',name,'nVehContrib',sum(v['nVehContrib'] for v in s),'veh')
    trips=read_trips(resolver.resolve(option('--tripinfo-output')))
    routes={}
    for n in ET.parse(resolver.resolve(option('--vehroute-output'))).getroot().findall('vehicle'):
        vid=n.attrib['id'];category(vid)
        if vid in routes:raise ValueError('Duplicate vehroute ID')
        routes[vid]={'depart':finite(n.attrib['depart']),'arrival':finite(n.get('arrival','-1')),'edges':n.find('route').get('edges').split()}
    frames,observed,events,lane_samples=read_fcd(resolver.resolve(option('--fcd-output')),set(routes))
    summary_steps=ET.parse(resolver.resolve(option('--summary-output'))).getroot().findall('step')
    if not summary_steps:raise ValueError('No simulation summary steps')
    end=summary_steps[-1].attrib
    demand_boundary=next((n.attrib for n in summary_steps if finite(n.attrib['time'])==1499),None)
    actual={vid:v for vid,v in trips.items() if 0<=v['depart']<2700}
    valid_arrived={vid for vid,v in actual.items() if before(v['arrival'],2700)}
    route_actual={vid for vid,v in routes.items() if 0<=v['depart']<2700}
    anomaly=sum(int(end.get(k,'0')) for k in ('collisions','teleports','discarded'))
    complete_time=float(end['time'])==2699
    dep_verified=complete_time and len(actual)==int(end['inserted']) and set(actual)==route_actual and observed<=set(actual) and not anomaly
    arr_verified=dep_verified and len(valid_arrived)==int(end['arrived']) and all((v['arrival']>=0)==(routes[k]['arrival']>=0) for k,v in actual.items())
    qualifies={'plan_count_status':'verified_declared_flow_number','schedule_time_status':'unverified',
               'departure_coverage_status':'verified' if dep_verified else 'unverified',
               'arrival_coverage_status':'verified' if arr_verified else 'unverified'}
    vehicle=[];endpoint={};timeline=[];discrepancy={}
    for vid in sorted(set(trips)|set(routes)|observed):
        v=trips.get(vid);c=category(vid)
        # Do not create absent plan IDs from a nominal uniform-flow formula.
        vehicle.append(dict(zip(VEHICLE_FIELDS,[rid,vid,c,None,v['depart']-v['departDelay'] if v and v['depart']>=0 else None,
            'observed_record_only; full plan-ID expansion unverified',v['depart'] if v else None,v['arrival'] if v and v['arrival']>=0 else None,
            v['departDelay'] if v and v['depart']>=0 else None,v['duration'] if v and v['arrival']>=0 else None,classify(v),2700,'unverified'])))
    for c in CLASSES:
        subset={k:v for k,v in actual.items() if category(k)==c}
        if len(subset)>planned[c]:raise ValueError('Actual class count exceeds declared plan')
        diff=[abs((v['depart']-v['departDelay'])-1500*int(k.split('.')[-1])/planned[c]) for k,v in subset.items()] if planned[c] else []
        discrepancy[c]={'max_nominal_schedule_discrepancy_s':max(diff) if diff else None,'observed_members':len(diff),'qualification':'unverified even if discrepancies are zero'}
        for name,(a,b) in WINDOWS.items():
            metric('cohort',c,name,'actual_departures',sum(a<=v['depart']<b for v in subset.values()),'veh')
            metric('cohort',c,name,'arrivals',sum(a<=v['arrival']<b for v in subset.values()),'veh')
            completed=[v['duration'] for v in subset.values() if a<=v['arrival']<b]
            metric('completed_arrivals_subset',c,name,'duration_mean_s',sum(completed)/len(completed) if completed else None,'s',len(completed))
        for t in range(0,2701,30):
            entered=sum(before(v['depart'],t) for v in subset.values());arrived=sum(before(v['arrival'],t) for v in subset.values())
            # Endpoint counts do not need exact individual plan times. Mid-run
            # planned-before stays unknown. All declared demand ends at 1500.
            boundary_record=demand_boundary if t==1500 else end if t==2700 else None
            known_endpoint=boundary_record is not None and int(boundary_record['loaded'])==sum(planned.values()) and int(boundary_record['inserted'])==sum(before(v['depart'],t) for v in actual.values())
            counts=endpoint_counts(planned[c],entered,arrived,dep_verified and arr_verified) if known_endpoint else {'outside_confirmed':None,'in_network':entered-arrived if dep_verified and arr_verified else None,'unaccounted_count':None}
            frame=frames.get(t)
            timeline.append(dict(zip(COHORT_FIELDS,[rid,c,t,planned[c] if known_endpoint else 0 if t==0 else None,entered,arrived,counts['in_network'],counts['outside_confirmed'],counts['unaccounted_count'],*qualifies.values(),frame is not None,frame['counts'].get(c,0) if frame else None,frame['stopped'].get(c,0) if frame else None,'trip:event<t; FCD:raw label; no forced alignment'])))
            if t==2700:endpoint[c]={'planned':planned[c],'entered':entered,'arrived':arrived,**counts}
    merge=[]
    for vid in sorted(k for k in actual if category(k)=='R'):
        if routes[vid]['edges'][-2:]!=['ramp_accel','main_down']:raise ValueError('R route mismatch')
        if vid in events:e=events[vid]
        else:e={'vehicle_id':vid,'previous_time_s':None,'previous_lane':None,'first_downstream_time_s':None,'first_downstream_lane':None,'interval_semantics':'(previous_raw_label,first_downstream_raw_label]','time_precision':'unresolved','boundary_30s_ambiguous':None,'status':'not_observed_before_end' if vid not in valid_arrived else 'unresolved','reason':'no_downstream_sample'}
        merge.append({'run_id':rid,**e})
    missing_frames=sorted(set(range(2700))-set(frames))
    e1_invalid=[r for r in e1 if r['missing_reason']=='negative_speed_with_contributions']
    core=dep_verified and arr_verified and not missing_frames and not e1_invalid and not any(e['status']=='unresolved' for e in merge)
    audit={'run_id':rid,'status':'analyzed','qualification':qualifies,'plan_counts':planned,'actual_trip_class_counts':dict(Counter(category(k) for k in actual)),
           'endpoint':endpoint,'schedule_check':discrepancy,'source_windows':summary['time_windows'],'requested_demand':requested,
           'six_e1_rows':len(e1),'independent_E1_window_checks':independent_checks,'E1_per_ID_coverage':'not_verified',
           'FCD_frames':len(frames),'FCD_missing_times':missing_frames,'FCD_unique_IDs':len(observed),'FCD_lane_class_sample_counts':{f'{k[0]}/{k[1]}':v for k,v in lane_samples.items()},
           'merge_status_counts':dict(Counter(e['status'] for e in merge)),'merge_bin_ambiguous':sum(e['boundary_30s_ambiguous'] is True for e in merge),
           'invalid_E1_speed_with_contributions':e1_invalid,'core_evidence_status':'passed_for_descriptive_contract' if core else 'blocked_or_requires_review',
           'clearance_status':'complete' if dep_verified and arr_verified and all(v['outside_confirmed']==0 and v['in_network']==0 for v in endpoint.values()) else 'censored' if dep_verified and arr_verified else 'unknown',
           'last_actual_departure_s':max((v['depart'] for v in actual.values()),default=None),'last_arrival_s':max((v['arrival'] for v in actual.values() if v['arrival']>=0),default=None),
           'limitations':['Individual schedules unverified: no inferred mid-run outside counts or exact cohort external delay.','Internal E1 is M-only aggregate passage; per-ID omissions/duplicates unverified.','Origin E1 contaminated by insertion; downstream E1 may be affected by lane changes.','No breakdown/capacity-drop/steady-state or statistical classification.']}
    resolver.verify()
    return audit,vehicle,timeline,e1,wr,merge


def comparisons(rows):
    selected=[r for r in rows if r['family'] in ('E1_group','cohort') and r['window'] in ('A','B','Post')]
    index={(r['run_id'],r['family'],r['entity'],r['window'],r['metric']):r for r in selected};out=[]
    for prefix in ('ML','MH','RL'):
        for seed in (17,23):
            for key,treat in index.items():
                if key[0]!=f'{prefix}{seed}':continue
                base=index.get((f'C{seed}',*key[1:]))
                if base is None:continue
                value=treat['value']-base['value'] if treat['value'] is not None and base['value'] is not None else None
                out.append({'contrast':f'{prefix}{seed}-C{seed}','family':key[1],'entity':key[2],'window':key[3],'metric':key[4],'baseline':base['value'],'treatment':treat['value'],'difference':value,'unit':treat['unit'],'baseline_denominator':base['denominator'],'treatment_denominator':treat['denominator']})
    return {'status':'descriptive_same_seed_only','contrasts':out,'seed_claim':'Two seeds are not statistical robustness; no hypothesis tests.'}


def plots(e1,timeline,directory):
    if not e1:return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ids=list(dict.fromkeys(r['run_id'] for r in e1))
    fig,axes=plt.subplots(len(ids),2,figsize=(13,3*len(ids)),squeeze=False,sharex=True,sharey="col")
    for i,rid in enumerate(ids):
        for ident in DETECTORS:
            if ident.startswith('merge_upstream'):continue
            s=[r for r in e1 if r['run_id']==rid and r['detector_id']==ident]
            for j,field in enumerate(('flow_vehph','speed_raw_mps')):
                y=[r[field] if j==0 or r['speed_valid'] else math.nan for r in s]
                axes[i,j].step([r['begin_s'] for r in s]+[2700],y+[y[-1]],where='post',label=ident.replace('mainline_merge_entry','internal').replace('merge_downstream','downstream'),linewidth=.8)
                axes[i,j].set_ylabel(f'{rid}: '+('veh/h' if j==0 else 'm/s'))
        for ax in axes[i]:ax.axvline(1500,color='black',ls='--');ax.set_xlim(0,2700);ax.set_xlabel('Simulation time (s)');ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=7,ncol=2);fig.suptitle('Exploratory raw passage measurements; internal M and downstream lanes; not capacity/Breakdown')
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(directory/'passage_timeline.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(len(ids),2,figsize=(13,3*len(ids)),squeeze=False,sharex=True,sharey="col")
    for i,rid in enumerate(ids):
        for j,c in enumerate(('R','U')):
            s=[r for r in timeline if r['run_id']==rid and r['class']==c]
            ax=axes[i,j]
            for f in ('entered_before','arrived_before'):ax.step([r['time_s'] for r in s],[r[f] for r in s],where='post',label=f)
            at_end=next(r for r in s if r['time_s']==2700)
            ax.set_title(f'{rid} {c}; outside at 2700={at_end["outside_confirmed"]}')
            ax.axvline(1500,color='black',ls='--');ax.set_ylabel('Cumulative vehicles');ax.set_xlabel('Simulation time (s)');ax.set_xlim(0,2700);ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8);fig.suptitle('Observed cumulative insertion / arrival; NOT outside waiting curves (schedule unverified)')
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(directory/'cohort_observed_timeline.png',dpi=130);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('ledger','output-dir','table-dir','figure-dir'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();ledger=json.loads(args.ledger.read_text());out=args.output_dir;tables=args.table_dir;fig=args.figure_dir
    reserve_directories([out,tables,fig]);dump(out/'ledger_snapshot.json',ledger)
    audits=[];vehicles=[];timelines=[];e1=[];windows=[];merge=[];sources={}
    for run in ledger['runs']:
        attempt=next((a for a in run['attempts'] if a['attempt_id']==run['selected_attempt_id']),None)
        if attempt is None:
            audits.append({'run_id':run['run_id'],'status':run['status'],'reason':'No selected attempt; retained in coverage'});continue
        map_path=Path(attempt['source_manifest']) if attempt.get('source_manifest') else args.ledger.parent/'source_maps'/f'{attempt["attempt_id"]}.json'
        if not map_path.is_absolute():map_path=ROOT/map_path
        try:
            resolver=ArchiveResolver(map_path)
            result=analyze_run(run,resolver)
            audits.append(result[0]);vehicles.extend(result[1]);timelines.extend(result[2]);e1.extend(result[3]);windows.extend(result[4]);merge.extend(result[5])
            sources[str(map_path)]=digest(map_path);sources.update(resolver.hashes)
        except (ValueError,KeyError,FileNotFoundError,ET.ParseError) as error:
            audits.append({'run_id':run['run_id'],'status':'blocked','reason':str(error)})
    table(tables/'vehicle_accounting.csv',vehicles,VEHICLE_FIELDS)
    table(tables/'cohort_timeline.csv',timelines,COHORT_FIELDS)
    table(tables/'e1_native.csv',e1,list(e1[0]) if e1 else ['run_id','detector_id','lane_id','begin_s','end_s'])
    table(tables/'run_window_summary.csv',windows,WINDOW_FIELDS)
    table(tables/'merge_events.csv',merge,MERGE_FIELDS)
    dump(out/'run_audit.json',{'runs':audits,'all_logical_records':len(ledger['runs']),'stage2_acceptance':'pending_user'})
    dump(out/'comparison.json',comparisons(windows));plots(e1,timelines,fig)
    sources[str(Path(__file__).resolve())]=digest(__file__)
    sources[str(Path(__file__).with_name('build_stage2_g1_diagnostic.py'))]=digest(Path(__file__).with_name('build_stage2_g1_diagnostic.py'))
    dump(out/'manifest.json',{'command':shlex.join([sys.executable,*sys.argv]),'archive_only':True,'tmp_fallback':False,'source_sha256':sources,
        'output_sha256':{str(x.resolve()):digest(x) for x in [*out.glob('*.json'),*tables.glob('*.csv'),*fig.glob('*.png')]},
        'analysis_windows':WINDOWS,'classification':'exploratory','schedule_time_status':'unverified'})
    print(json.dumps([{'run_id':a['run_id'],'status':a['status'],'core':a.get('core_evidence_status'),'reason':a.get('reason')} for a in audits],indent=2))
    if any(a['status']=='blocked' for a in audits):raise SystemExit(2)


if __name__=='__main__':main()
