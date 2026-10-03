#!/usr/bin/env python3
"""Exploratory boundary search analysis; immutable raw, explicit configuration.

No state classifier is enabled unless a reviewed classifier configuration is given.
FCD first observations have one simulation-step resolution, not exact crossing times.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

DEFAULTS = dict(horizon=4200, step=1, bin_seconds=30, evaluation_start=1200,
                evaluation_end=3000, cell_m=100, mainline_end_x=2200,
                slow_speed_mps=15, stopped_speed_mps=0.1, mainline_lanes=2)
MAIN_LANES = {'main_up_0','main_up_1',':freeway_merge_0_0',':freeway_merge_0_1',
 'merge_section_1','merge_section_2',':merge_end_0_0',':merge_end_0_1','main_down_0','main_down_1'}
QUEUE_LANES = {'ramp_storage_0', ':urban_diverge_1_0', 'shared_approach_0'}

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def number(x):
    v=float(x)
    if not math.isfinite(v): raise ValueError(f'nonfinite value {x}')
    return v

def vehicle_class(vid):
    c=vid.split('_')[0]
    if c not in 'MRUX' or len(c)!=1: raise ValueError(f'unknown vehicle class {vid}')
    return c

def in_window(t,start,end): return start<=t<end

def demand_rows(path):
    root=ET.parse(path).getroot()
    if root.tag!='routes' or root.findall('flow'): raise ValueError('materialized vehicles required')
    out={}
    for v in root.findall('vehicle'):
        vid=v.attrib['id']
        if vid in out: raise ValueError('duplicate demand ID')
        out[vid]={'class':vehicle_class(vid),'scheduled':number(v.attrib['depart']),'speedFactor':number(v.attrib['speedFactor'])}
    if not out: raise ValueError('empty demand')
    return out

def trip_rows(path):
    out={}
    for _,e in ET.iterparse(path,events=('end',)):
        if e.tag!='tripinfo': continue
        vid=e.attrib['id']
        if vid in out: raise ValueError('duplicate tripinfo ID')
        vehicle_class(vid)
        out[vid]={k:number(e.attrib[k]) for k in ['depart','arrival','departDelay','duration','timeLoss','waitingTime']}
        e.clear()
    return out

def lanechanges(path):
    result=defaultdict(list)
    for _,e in ET.iterparse(path,events=('end',)):
        if e.tag=='change':
            vid=e.attrib['id'];vehicle_class(vid)
            if e.get('from')=='merge_section_0' and e.get('to') in {'merge_section_1','merge_section_2'}:
                result[vid].append({'time':number(e.get('time')),'position':number(e.get('pos'))})
            e.clear()
    return dict(result)

def fcd_scan(path,cfg,demand=None,lane_speeds=None):
    horizon=cfg['horizon'];dt=cfg['step'];width=cfg['bin_seconds'];cell_m=cfg['cell_m'];alphas=(.6,.7,.8)
    def fresh():return dict(n=0,total_n=0,speed_sum=0.,ratio_sum=0.,slow_n=0,ids=set(),max_count=0,max_slow_count=0,group_slow_seconds=0,alpha_n=Counter(),alpha_group_seconds=Counter())
    bins=defaultdict(fresh);ids={};first_events={};queues=defaultdict(Counter);invalid_m=[];labels=0
    lane_track={l:(1 if l in {'main_up_1',':freeway_merge_0_1','merge_section_2',':merge_end_0_1','main_down_1'} else 0) for l in MAIN_LANES}
    for _,step in ET.iterparse(gzip.open(path,'rb') if str(path).endswith('.gz') else path,events=('end',)):
        if step.tag!='timestep':continue
        t=number(step.get('time'))
        if t!=labels*dt or t>=horizon:raise ValueError(f'missing/repeated timestep: expected {labels*dt}, got {t}')
        labels+=1;seen=set();now=Counter();slow=Counter();normslow=Counter();queue_now=Counter();b=int(t//width)
        for v in step:
            if v.tag!='vehicle':continue
            vid=v.attrib['id'];c=vehicle_class(vid)
            if vid in seen:raise ValueError(f'duplicate vehicle at timestep {vid}/{t}')
            seen.add(vid);speed=number(v.get('speed'));x=number(v.get('x'));lane=v.get('lane')
            if speed<0:raise ValueError('negative speed')
            if vid not in ids:ids[vid]={'first':t,'last':t,'n':0,'class':c}
            z=ids[vid]
            if z['n'] and t!=z['last']+dt:raise ValueError(f'interior FCD gap {vid}')
            z['last']=t;z['n']+=1;ev=first_events.setdefault(vid,{})
            if lane.startswith('merge_section_'):ev.setdefault('merge_edge',t)
            if lane=='merge_section_0':ev.setdefault('auxiliary_observed',t)
            if lane in {'merge_section_1','merge_section_2'}:ev.setdefault('mainline_observed',t)
            if lane.startswith('main_down_'):ev.setdefault('downstream',t)
            if lane not in MAIN_LANES and not lane.startswith(('merge_section_',':freeway_merge_',':merge_end_')):
                queues[(b,lane)][f'{c}_vehicle_seconds']+=dt;queue_now[(lane,c,'all')]+=1
                for label,cutoff in [('stopped',cfg['stopped_speed_mps']),('slow5',5)]:
                    if speed<cutoff:queues[(b,lane)][f'{c}_{label}_seconds']+=dt;queue_now[(lane,c,label)]+=1
            if lane not in MAIN_LANES or not 0<=x<=cfg['mainline_end_x']:
                if c=='M':invalid_m.append([vid,t,lane,x])
                continue
            cell=min(int(x//cell_m),int(cfg['mainline_end_x']/cell_m)-1)
            keys=[(b,cell,'pooled'),(b,cell,str(lane_track[lane]))]
            for key in keys:
                r=bins[key]
                if c in 'MR':r['total_n']+=1
            if c!='M':continue
            factor=demand[vid]['speedFactor'] if demand is not None else 1
            limit=lane_speeds[lane] if lane_speeds is not None else 33.33
            if factor<=0 or limit<=0:raise ValueError('invalid model speed reference')
            ratio=speed/(factor*limit)
            for key in keys:
                r=bins[key];r['n']+=1;r['speed_sum']+=speed;r['ratio_sum']+=ratio;r['slow_n']+=speed<cfg['slow_speed_mps'];r['ids'].add(vid);now[key]+=1
                if speed<cfg['slow_speed_mps']:slow[key]+=1
                for alpha in alphas:
                    if ratio<=alpha:r['alpha_n'][alpha]+=1;normslow[(key,alpha)]+=1
        for key,n in now.items():
            r=bins[key];r['max_count']=max(r['max_count'],n);r['max_slow_count']=max(r['max_slow_count'],slow[key]);r['group_slow_seconds']+=dt*(slow[key]>=cfg.get('diagnostic_slow_group_size',3))
            for alpha in alphas:r['alpha_group_seconds'][alpha]+=dt*(normslow[(key,alpha)]>=2)
        for (lane,c,kind),n in queue_now.items():
            r=queues[(b,lane)];key=f'{c}_max_simultaneous_{kind}';r[key]=max(r[key],n)
        step.clear()
    if labels*dt!=horizon:raise ValueError(f'incomplete FCD horizon {labels*dt}/{horizon}')
    rows=[]
    for b in range(math.ceil(horizon/width)):
        seconds=min(width,horizon-b*width)
        for cell in range(int(cfg['mainline_end_x']/cell_m)):
            for track in ['pooled','0','1']:
                r=bins[(b,cell,track)];n=r['n'];lanes=2 if track=='pooled' else 1
                row={'begin':b*width,'end':min((b+1)*width,horizon),'cell':cell,'x_start':cell*cell_m,'lane_track':track,
                 'samples':n,'unique_M':len(r['ids']),'population_valid':len(r['ids'])>=2,'speed_mps':r['speed_sum']/n if n else None,
                 'model_reference_ratio':r['ratio_sum']/n if n else None,'slow_fraction':r['slow_n']/n if n else None,
                 'mean_M_count':n*dt/seconds,'density_veh_per_km_lane':n*dt/seconds/(cell_m/1000*lanes),
                 'total_MR_density_veh_per_km_lane':r['total_n']*dt/seconds/(cell_m/1000*lanes),
                 'mean_slow_M_count':r['slow_n']*dt/seconds,'max_M_count':r['max_count'],'max_slow_M_count':r['max_slow_count'],'slow_group_seconds':r['group_slow_seconds']}
                for alpha in alphas:
                    tag=str(alpha).replace('.','p');row['slow_fraction_'+tag]=r['alpha_n'][alpha]/n if n else None;row['simultaneous_ge2_slow_seconds_'+tag]=r['alpha_group_seconds'][alpha]
                rows.append(row)
    return {'cells':rows,'ids':ids,'events':first_events,'queue_bins':[dict(begin=b*width,lane=l,**r) for (b,l),r in sorted(queues.items())],
            'invalid_m':invalid_m,'timesteps':labels,'lane_track_mapping':lane_track}

def lifecycle(demand,trips,fcd,cfg):
    if set(trips)-set(demand) or set(fcd['ids'])-set(demand):raise ValueError('unplanned trip/FCD IDs')
    h=cfg['horizon']; rows=[]; warnings=[]
    for vid,d in demand.items():
        tr=trips.get(vid);obs=fcd['ids'].get(vid);depart=tr['depart'] if tr and tr['depart']>=0 else None
        arrived=tr is not None and tr['arrival']>=0
        if obs and depart is None:raise ValueError(f'FCD ID without inserted tripinfo {vid}')
        if depart is not None and obs is None:raise ValueError(f'inserted ID without FCD {vid}')
        if obs and not 0<=obs['first']-depart<=cfg['step']:raise ValueError(f'FCD departure endpoint {vid}')
        if arrived and not 0<=tr['arrival']-obs['last']<=cfg['step']:raise ValueError(f'FCD arrival endpoint {vid}')
        if obs and not arrived and obs['last']!=h-cfg['step']:raise ValueError(f'unfinished FCD endpoint {vid}')
        ext=(depart if depart is not None else h)-d['scheduled']
        if ext < -1e-6:raise ValueError(f'depart before schedule {vid}')
        if depart is not None and abs(ext-tr['departDelay'])>0.011:raise ValueError(f'departDelay mismatch {vid}')
        ev=fcd['events'].get(vid,{})
        rows.append(dict(id=vid,vehicle_class=d['class'],scheduled=d['scheduled'],depart=depart,
          arrival=tr['arrival'] if arrived else None,status='arrived' if arrived else 'unfinished' if depart is not None else 'undeparted',
          external_wait_observed_s=ext,in_network_observed_s=(tr['arrival'] if arrived else h)-depart if depart is not None else 0,
          scheduled_system_time_observed_s=(tr['arrival'] if arrived else h)-d['scheduled'],
          duration_completed_s=tr['duration'] if arrived else None,timeLoss_observed_s=tr['timeLoss'] if tr and depart is not None else None,
          **ev))
    sums=[]
    for c in 'MRUX':
        rr=[r for r in rows if r['vehicle_class']==c];insert=[r for r in rr if r['depart'] is not None];complete=[r for r in rr if r['status']=='arrived']
        sums.append(dict(vehicle_class=c,planned=len(rr),inserted=len(insert),arrived=len(complete),unfinished=sum(r['status']=='unfinished' for r in rr),
         undeparted=sum(r['status']=='undeparted' for r in rr),max_departDelay_s=max((r['external_wait_observed_s'] for r in insert),default=None),
         mean_completed_duration_s=sum(r['duration_completed_s'] for r in complete)/len(complete) if complete else None,
         scheduled_system_time_observed_total_s=sum(r['scheduled_system_time_observed_s'] for r in rr),
         external_wait_observed_total_s=sum(r['external_wait_observed_s'] for r in rr),
         in_network_observed_total_s=sum(r['in_network_observed_s'] for r in rr)))
    time=[]
    for t in range(0,h+1,cfg['bin_seconds']):
        for c in 'MRUX':
            rr=[r for r in rows if r['vehicle_class']==c]
            scheduled=sum(r['scheduled']<t for r in rr);departed=sum(r['depart'] is not None and r['depart']<t for r in rr)
            arrivals=sum(r['arrival'] is not None and r['arrival']<t for r in rr)
            time.append(dict(time=t,vehicle_class=c,scheduled_before=scheduled,departed_before=departed,arrived_before=arrivals,
                             source_backlog=scheduled-departed,in_network=departed-arrivals))
    return rows,sums,time,warnings

def detector_rows(raw,cfg):
    rows=[]
    for path in sorted(list(raw.glob('p1_*.xml'))+list(raw.glob('*_e2.xml'))):
        previous=0
        for _,e in ET.iterparse(path,events=('end',)):
            if e.tag!='interval':continue
            begin=number(e.get('begin'));end=number(e.get('end'))
            if begin!=previous or end-begin!=cfg['bin_seconds']:raise ValueError(f'detector gap/interval {path}')
            previous=end
            rows.append(dict(source=path.name,**{k:number(v) if k!='id' else v for k,v in e.attrib.items()}));e.clear()
        if previous!=cfg['horizon']:raise ValueError(f'detector horizon {path}')
    return rows

def event_bins(vehicles,cfg):
    rows=[]
    for begin in range(0,cfg['horizon'],cfg['bin_seconds']):
        end=min(begin+cfg['bin_seconds'],cfg['horizon'])
        for c in 'MRUX':
            rr=[r for r in vehicles if r['vehicle_class']==c]
            row=dict(begin=begin,end=end,vehicle_class=c)
            for event in ['depart','merge_edge','first_aux_to_mainline_time','downstream','arrival']:
                row[event+'_count']=sum(r.get(event) is not None and in_window(r[event],begin,end) for r in rr)
            rows.append(row)
    return rows

def runs(values,step):
    groups=[]
    for value in sorted(values):
        if not groups or value!=groups[-1][-1]+step:groups.append([value])
        else:groups[-1].append(value)
    return groups

def classify(cells,cfg):
    rule=cfg.get('classifier')
    if not rule:return {'status':'NOT_CLASSIFIED','reason':'reviewed classifier not supplied'}
    if rule.get('version')!='exploratory_normalized_v1' or not rule.get('review_reference'):raise ValueError('reviewed normalized classifier version required')
    width=cfg['bin_seconds'];core=set(range(13,18));pooled={(r['cell'],r['begin']):r for r in cells if r['lane_track']=='pooled'}
    if width!=30:raise ValueError('reviewed classifier requires30s bins')
    def valid(r):return r is not None and r['population_valid'] and r['model_reference_ratio'] is not None
    import statistics
    baseline={}
    for c in range(22):
        rr=[pooled.get((c,t)) for t in range(300,600,30)]
        eligible=all(valid(r) and r['model_reference_ratio']>=.85 for r in rr)
        median=statistics.median([r['density_veh_per_km_lane'] for r in rr]) if all(valid(r) for r in rr) else None
        baseline[c]={'eligible':eligible and median is not None and median>0,'median_density':median}
    output={}
    for window,start,end in [('active',600,3000),('evaluation',cfg['evaluation_start'],cfg['evaluation_end'])]:
        profiles={}
        for name,alpha,duration in [('P',.7,3),('L',.8,2),('S',.6,4)]:
            tag=str(alpha).replace('.','p');low={c:set() for c in range(22)};episodes=[]
            for c in range(22):
                for t in range(0,cfg['horizon'],30):
                    r=pooled.get((c,t))
                    if valid(r) and r['model_reference_ratio']<=alpha and r['slow_fraction_'+tag]>=.5 and r['simultaneous_ge2_slow_seconds_'+tag]>=15:low[c].add(t)
            def onset(c,t):
                # The immediate predecessor is relative to maximal numeric-low episode,
                # not a later density-supported subepisode.
                while t-30 in low[c]:t-=30
                prev=[pooled.get((c,u)) for u in range(t-90,t,30)]
                return all(valid(r) and r['model_reference_ratio']>=.85 for r in prev)
            for c in range(21):
                if not ({c,c+1}&core):continue
                for seq in runs(low[c]&low[c+1],30):
                    if len(seq)<duration:continue
                    cs=sorted({c,c+1}&core)
                    episodes.append(dict(kind='same_adjacent_pair',cells=[c,c+1],begin=seq[0],end=seq[-1]+30,
                      onset='ONSET_SUPPORTED' if all(onset(k,seq[0]) for k in cs) else 'ONSET_UNRESOLVED'))
            for c in core:
                if not baseline[c]['eligible']:continue
                supported={t for t in low[c] if pooled[(c,t)]['density_veh_per_km_lane']>=1.25*baseline[c]['median_density']}
                for seq in runs(supported,30):
                    if len(seq)<duration:continue
                    episodes.append(dict(kind='same_core_density',cells=[c],begin=seq[0],end=seq[-1]+30,
                      onset='ONSET_SUPPORTED' if onset(c,seq[0]) else 'ONSET_UNRESOLVED'))
            episodes=[dict(ep,report_begin=max(start,ep['begin']),report_end=min(end,ep['end'])) for ep in episodes if ep['begin']<end and ep['end']>start]
            union=sorted({t for ep in episodes for t in range(ep['report_begin'],ep['report_end'],30)})
            profiles[name]={'alpha':alpha,'duration_bins':duration,'episodes':episodes,'supported_time_union_seconds':len(union)*30,
                'supported_bin_begins':union,'numeric_low_episodes':[{ 'cell':c,'begin':seq[0],'end':seq[-1]+30} for c in range(22) for seq in runs(low[c],30) if seq[0]<end and seq[-1]+30>start]}
        output[window]=profiles
    eval_times=list(range(cfg['evaluation_start'],cfg['evaluation_end'],30))
    coverage={c:sum(valid(pooled.get((c,t))) for t in eval_times) for c in core}
    free_counts={c:sum(valid(pooled.get((c,t))) and pooled[(c,t)]['model_reference_ratio']>=.85 for t in eval_times) for c in core}
    if any(n!=len(eval_times) for n in coverage.values()):status='MEASUREMENT_INCOMPLETE'
    elif output['evaluation']['P']['episodes']:status='SUSTAINED_CONGESTION_CANDIDATE'
    elif all(n>=57 for n in free_counts.values()) and not output['active']['L']['episodes']:status='FREE_FLOW_CANDIDATE'
    else:status='TRANSITION_OR_DISTURBED'
    return {'status':status,'windows':output,'baseline_density_support':baseline,'core_valid_bin_counts':coverage,'core_free_bin_counts':free_counts,
      'interpretation':'New exploratory operational classifier. Onset, source/delivery/downstream attribution and controllability remain separate.', 'rule':rule}

def csv_write(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def measurement_gate(state,invalid_m):
    if invalid_m:
        state={**state,'descriptive_status_before_invalid_lane_gate':state['status'],'status':'MEASUREMENT_INCOMPLETE','invalid_M_lane_gate':'FAILED'}
    return state

def check_summary(path,classes,cfg):
    count=0;last=None;anomalies=Counter()
    for _,e in ET.iterparse(path,events=('end',)):
        if e.tag!='step':continue
        if number(e.get('time'))!=count*cfg['step']:raise ValueError('summary timestep gap')
        count+=1;last=dict(e.attrib)
        for k in ['collisions','teleports','discarded']:anomalies[k]=max(anomalies[k],int(e.get(k,'0')))
        e.clear()
    if count*cfg['step']!=cfg['horizon']:raise ValueError('summary horizon mismatch')
    totals={k:sum(r[k] for r in classes) for k in ['planned','inserted','arrived','unfinished','undeparted']}
    for key,derived in [('loaded','planned'),('inserted','inserted'),('arrived','arrived'),('ended','arrived'),('running','unfinished'),('waiting','undeparted')]:
        if int(last[key])!=totals[derived]:raise ValueError(f'summary lifecycle mismatch {key}')
    return dict(final=last,anomaly_maxima=dict(anomalies),lifecycle_reconciled=True)

def validate_receipt(raw,card_path=None):
    p=raw/'execution_receipt.json'
    receipt=json.loads(p.read_text())
    if receipt.get('status')!='COMPLETED' or receipt.get('return_code')!=0:raise ValueError('execution not completed')
    for name,meta in receipt['output_manifest'].items():
        f=raw/name
        if Path(name).name!=name:raise ValueError('unsafe manifest name')
        if f.stat().st_size!=meta['bytes'] or sha(f)!=meta['sha256']:raise ValueError(f'raw hash mismatch {name}')
    if card_path and sha(card_path)!=receipt['card_sha256']:raise ValueError('card hash mismatch')
    return receipt

def analyze(raw,demand_path,config,out,card_path=None):
    cfg={**DEFAULTS,**config};raw=Path(raw);out=Path(out)
    if out.exists():raise FileExistsError(f'will not overwrite {out}')
    receipt=validate_receipt(raw,card_path)
    fcd_path=raw/'fcd.xml.gz' if (raw/'fcd.xml.gz').exists() else raw/'fcd.xml'
    sources={str(p.resolve()):sha(p) for p in [fcd_path,raw/'tripinfo.xml',raw/'lanechanges.xml',Path(demand_path),Path(__file__)]}
    demand=demand_rows(demand_path)
    if card_path:
        card=json.loads(Path(card_path).read_text())
        if cfg['horizon']!=card['horizon_s']:raise ValueError('horizon/card mismatch')
        if dict(Counter(r['class'] for r in demand.values()))!={c:n for c,n in card['counts'].items() if n}:raise ValueError('demand/card count mismatch')
        sources[str(Path(card_path).resolve())]=sha(card_path)
        if sha(demand_path)!=card['input_sha256']['demand.rou.xml']:raise ValueError('demand hash mismatch')
    sources[str((raw/'execution_receipt.json').resolve())]=sha(raw/'execution_receipt.json')
    trips=trip_rows(raw/'tripinfo.xml')
    network_path=Path(cfg['network']) if cfg.get('network') else Path(ET.parse(Path(demand_path).parent/'scenario.sumocfg').find('.//net-file').get('value'))
    lane_speeds={e.get('id'):number(e.get('speed')) for e in ET.parse(network_path).iter('lane')}
    sources[str(network_path.resolve())]=sha(network_path)
    if card_path and sha(network_path)!=card['network_sha256']:raise ValueError('network hash mismatch')
    realized=set()
    for _,e in ET.iterparse(raw/'vehroute.xml',events=('end',)):
        if e.tag!='vehicle':continue
        vid=e.get('id')
        if vid not in demand or vid in realized:raise ValueError('vehroute unknown/duplicate ID')
        realized.add(vid)
        reported=e.get('speedFactor')
        if reported is None:raise ValueError('vehroute missing speedFactor')
        decimals=len(reported.partition('.')[2])
        if decimals<4:raise ValueError('vehroute speedFactor precision below archived four decimals')
        if abs(number(reported)-demand[vid]['speedFactor'])>0.5*10**(-decimals)+1e-10:raise ValueError('vehroute speedFactor mismatch')
        e.clear()
    if realized!={v for v,t in trips.items() if t['depart']>=0}:raise ValueError('vehroute inserted ID mismatch')
    sources[str((raw/'vehroute.xml').resolve())]=sha(raw/'vehroute.xml')
    fcd=fcd_scan(fcd_path,cfg,demand,lane_speeds)
    changes=lanechanges(raw/'lanechanges.xml');vehicles,classes,times,warnings=lifecycle(demand,trips,fcd,cfg)
    if set(changes)-set(demand):raise ValueError('unplanned lanechange IDs')
    for r in vehicles:
        ch=changes.get(r['id'],[]);r['aux_to_mainline_changes']=len(ch)
        r['first_aux_to_mainline_time']=min((x['time'] for x in ch),default=None)
        r['first_aux_to_mainline_position']=ch[0]['position'] if ch else None
    for log in sorted(raw.glob('*.log')):
        sources[str(log.resolve())]=sha(log)
        warnings.extend({'source':log.name,'line':line} for line in log.read_text(errors='replace').splitlines() if re.search(r'(?i)\b(warning|error)\b',line))
    detectors=detector_rows(raw,cfg)
    events=event_bins(vehicles,cfg)
    for p in sorted(list(raw.glob('p1_*.xml'))+list(raw.glob('*_e2.xml'))):sources[str(p.resolve())]=sha(p)
    state=measurement_gate(classify(fcd['cells'],cfg),fcd['invalid_m'])
    summary_check=check_summary(raw/'sumo_summary.xml',classes,cfg)
    sources[str((raw/'sumo_summary.xml').resolve())]=sha(raw/'sumo_summary.xml')
    summary={'analysis_kind':'EXPLORATORY','config':cfg,'source_hashes':sources,'timesteps':fcd['timesteps'],'execution_status':receipt['status'],'run_id':receipt['run_id'],
      'classes':classes,'state':state,'summary_reconciliation':summary_check,'warnings':warnings,'invalid_M_observations':fcd['invalid_m'],
      'lane_track_mapping':fcd['lane_track_mapping'],'event_definition':'FCD first observations; lanechange from auxiliary to mainline is separate; windows half-open',
      'censoring':'All planned vehicles retained. Observed system time is restricted at horizon; completed-duration mean is separately labelled.'}
    out.mkdir(parents=True)
    for name,rows in [('vehicles',vehicles),('classes',classes),('cumulative',times),('mainline_cells',fcd['cells']),('urban_ramp_queue',fcd['queue_bins']),('events',events),('detectors',detectors)]:csv_write(out/(name+'.csv'),rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

def batch_summary(processed_root,table_out,run_ids=None):
    rows=[]
    for directory in sorted(Path(processed_root).iterdir()):
        if not directory.is_dir() or (run_ids is not None and directory.name not in run_ids):continue
        p=directory/'summary.json'
        if not p.exists():
            fail=directory/'failure.json'
            if fail.exists():rows.append(dict(run_id=directory.name,analysis_status='FAILED',error=json.loads(fail.read_text())['error']))
            continue
        z=json.loads(p.read_text());cfg=z['config'];card_paths=[p for p in z['source_hashes'] if p.endswith('/card.json')]
        card=json.loads(Path(card_paths[0]).read_text()) if card_paths else {}
        r=dict(run_id=z['run_id'],analysis_status='PASS',state=z['state']['status'],q_main_requested=card.get('q_main_veh_h'),q_ramp_requested=card.get('q_ramp_veh_h'),seed=card.get('seed'))
        for window in ['active','evaluation']:
            for profile in 'PLS':r[window+'_'+profile+'_seconds']=z['state'].get('windows',{}).get(window,{}).get(profile,{}).get('supported_time_union_seconds')
        for c in z['classes']:
            for k in ['planned','inserted','arrived','unfinished','undeparted','max_departDelay_s','mean_completed_duration_s','scheduled_system_time_observed_total_s','external_wait_observed_total_s','in_network_observed_total_s']:r[c['vehicle_class']+'_'+k]=c[k]
            r[c['vehicle_class']+'_scheduled_system_time_observed_mean_s']=c['scheduled_system_time_observed_total_s']/c['planned'] if c['planned'] else None
        events=list(csv.DictReader((directory/'events.csv').open()));duration=cfg['evaluation_end']-cfg['evaluation_start']
        for c in 'MR':
            rr=[x for x in events if x['vehicle_class']==c and cfg['evaluation_start']<=float(x['begin'])<cfg['evaluation_end']]
            for field in ['depart_count','merge_edge_count','first_aux_to_mainline_time_count','downstream_count']:
                r[c+'_evaluation_'+field]=sum(int(x[field]) for x in rr);r[c+'_evaluation_'+field+'_veh_h']=r[c+'_evaluation_'+field]*3600/duration
        cumulative=list(csv.DictReader((directory/'cumulative.csv').open()))
        for c in 'MRUX':r[c+'_source_backlog_max_30s']=max(int(x['source_backlog']) for x in cumulative if x['vehicle_class']==c)
        r['summary_lifecycle_reconciled']=z['summary_reconciliation']['lifecycle_reconciled'];r['summary_anomalies']=json.dumps(z['summary_reconciliation']['anomaly_maxima'],sort_keys=True);r['warnings']=json.dumps(z['warnings']);r['invalid_M_observations']=len(z['invalid_M_observations'])
        rows.append(r)
    target=Path(table_out)
    if target.exists():raise FileExistsError(target)
    target.mkdir(parents=True);csv_write(target/'batch_summary.csv',rows);(target/'batch_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--raw');p.add_argument('--demand');p.add_argument('--card');p.add_argument('--config',required=True);p.add_argument('--out',required=True)
    a=p.parse_args()
    if a.card:
        card=json.loads(Path(a.card).read_text());a.raw=card['output'];a.demand=str(Path(a.card).parent/'demand.rou.xml')
    if not a.raw or not a.demand:p.error('--card or both --raw and --demand required')
    try:
        config=json.loads(Path(a.config).read_text());config['analysis_config_sha256']=sha(a.config)
        s=analyze(a.raw,a.demand,config,a.out,a.card)
        print(json.dumps({'out':a.out,'state':s['state'],'classes':s['classes']}))
    except Exception as e:
        failure={'analysis_status':'FAILED','raw':a.raw,'card':a.card,'error':str(e),'analyzer_sha256':sha(__file__)}
        out=Path(a.out)
        if not out.exists():
            out.mkdir(parents=True);(out/'failure.json').write_text(json.dumps(failure,indent=2)+'\n')
        print(json.dumps(failure));raise
if __name__=='__main__':main()
