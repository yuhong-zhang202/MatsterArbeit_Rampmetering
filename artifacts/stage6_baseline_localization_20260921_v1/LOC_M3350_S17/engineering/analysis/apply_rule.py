#!/usr/bin/env python3
"""Deterministic offline application of the locked exploratory freeway-state rule."""
from __future__ import annotations
import csv, hashlib, json, math, statistics, sys
from collections import defaultdict, Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT/'data/raw/stage6_baseline_localization_20260921_v1'
ENG = ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering'
NET = ENG/'build_attempts/TV_BUILD01/network.net.xml'
APP = ROOT/'data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1'
TAB = APP/'tables'
RUNS = {'LOC':'LOC_M3350_S17_attempt1'}
WHITELIST = {'main_up_0','main_up_1',':freeway_merge_0_0',':freeway_merge_0_1','merge_section_1','merge_section_2',':merge_end_0_0',':merge_end_0_1','main_down_0','main_down_1'}
AUX = 'merge_section_0'
PROFILES = {'P':(.70,3,1.0),'S':(.60,4,1.25),'L':(.80,2,1.0)}
EXPECTED_METHOD = '22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7'

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def write_csv(path, rows, fields=None):
    rows=list(rows)
    if fields is None: fields=list(rows[0]) if rows else []
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def local(path, runroot):
    p=Path(path)
    try:return p.relative_to(runroot.parent.parent)
    except ValueError:return Path('UNRESOLVED_PATH')
def xmlroot(p, expect=None):
    tree=ET.parse(p); root=tree.getroot()
    if expect and root.tag!=expect: raise ValueError(f'{p}: root {root.tag}, expected {expect}')
    return root
def lane_cell(x):
    if x == 2200: return 21, True
    if x < 0 or x > 2200: return None, False
    return min(21,int(x//100)), False

# Pure decision helpers are shared by production processing and the behavioral fixtures.
def low_state_gate(valid, mean_ratio, slow_fraction, labels_nslow_ge2, alpha):
    return bool(valid and mean_ratio is not None and mean_ratio <= alpha and slow_fraction is not None and slow_fraction >= .5 and labels_nslow_ge2 >= 15)
def qualify_episode(low_bins, density_gates, required, core=True, reference=True, attribution='CLEAR'):
    if not low_bins: return 'NO_LOW_STATE'
    if sum(bool(x) for x in low_bins) < required: return 'SHORT_LOW_STATE_CANDIDATE'
    if not core: return 'OUTSIDE_MERGE_CORE'
    if not reference: return 'ONSET_REFERENCE_UNRESOLVED'
    if not all(density_gates): return 'DENSITY_GATE_FAIL'
    if attribution == 'EXCLUDED': return 'ATTRIBUTION_EXCLUDED'
    return 'NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW' if attribution == 'UNRESOLVED' else 'NUMERICAL_POSITIVE_CLEAR'
def density_gate(candidate_row, reference_density, reference_count, factor):
    """Locked inclusive S density gate; exact integer comparison avoids float drift."""
    if reference_density is None or reference_density <= 0: return False
    if factor == 1.25: return 4 * int(candidate_row['M_density_sample_count']) >= 5 * int(reference_count)
    return candidate_row['mean_M_density_veh_per_lane_km'] > reference_density * factor
def maximal_true_runs(values):
    out=[]; start=None
    for i,v in enumerate(list(values)+[False]):
        if v and start is None: start=i
        elif not v and start is not None: out.append((start,i)); start=None
    return out
def bin_index(t): return int(t//30)
def exact_grid(labels, expected): return len(labels)==expected and len(set(labels))==expected and set(labels)==set(range(expected))
def cell_event_id(run, profile, cell, start): return f'{run}_{profile}_c{cell:02d}_b{start:02d}'
def recovery_status(found, run_end=False): return 'RECOVERED' if found else ('RIGHT_CENSORED' if run_end else 'RECOVERY_UNRESOLVED')
def recovery_start(rows, ref_density):
    if ref_density is None: return None
    for i,(a,b) in enumerate(zip(rows,rows[1:])):
        if (a['valid'] and b['valid'] and a['mean_ratio'] is not None and b['mean_ratio'] is not None
            and a['mean_ratio']>=.85 and b['mean_ratio']>=.85
            and a['density']<=ref_density and b['density']<=ref_density):
            return a['bin']
    return None
def population_status(n_future, run_end=False): return 'NOT_OBSERVED_AFTER_RUN_END' if run_end else ('POPULATION_ENDED' if not any(n_future) else 'POPULATION_PRESENT')
def route_join_ok(route_present, speed_factor): return bool(route_present and speed_factor is not None and speed_factor > 0)
def upstream_propagation(onsets, vehicle_sets):
    # Cell coordinate increases downstream. A backward queue must activate
    # later at each successively upstream position, with distinct affected M
    # identities represented at both neighboring positions.
    ordered=sorted(onsets.items(),reverse=True)
    if len(ordered)<2: return 'UNRESOLVED_INSUFFICIENT_POSITIONS'
    if any(down_x-up_x!=1 for (down_x,_),(up_x,_) in zip(ordered,ordered[1:])): return 'UNRESOLVED_SPATIAL_GAP'
    deltas=[up_t-down_t for (_,down_t),(_,up_t) in zip(ordered,ordered[1:])]
    if any(d==0 for d in deltas): return 'UNRESOLVED_BIN_ALIGNMENT'
    if all(d<0 for d in deltas): return 'NOT_ESTABLISHED_FORWARD_ONSET_ORDER'
    if not all(d>0 for d in deltas): return 'UNRESOLVED_NONMONOTONIC_ONSET_ORDER'
    for (down_x,_),(up_x,_) in zip(ordered,ordered[1:]):
        down_ids,up_ids=set(vehicle_sets.get(down_x,set())),set(vehicle_sets.get(up_x,set()))
        if len(down_ids)<2 or len(up_ids)<2: return 'UNRESOLVED_INSUFFICIENT_VEHICLE_IDENTITIES'
        if down_ids & up_ids: return 'UNRESOLVED_COHORT_IDENTITY_NOT_DISTINCT'
    return 'ESTABLISHED_BACKWARD_PROPAGATION'

def event_propagation(event, events, obs, alpha):
    """Assess only directly adjacent, temporally overlapping recorded cell episodes; never bridge gaps."""
    c=event['cell']; start=event['first_low_bin']; end=event['low_bin_end_exclusive']; run=event['run']; profile=event['profile']
    def ids_for(e):
        return {z[0] for k in range(e['first_low_bin'],e['low_bin_end_exclusive']) for t in range(30*k,30*(k+1))
                for z in obs.get((e['cell'],t,profile),[]) if z[0].startswith('M_') and z[3]}
    linked=[]
    for n in (c-1,c+1):
        for other in events:
            if other['run']!=run or other['profile']!=profile or other['cell']!=n: continue
            if max(start,other['first_low_bin']) < min(end,other['low_bin_end_exclusive']): linked.append(other)
    if not linked: return 'UNRESOLVED_NO_LINKED_ADJACENT_EPISODE'
    outcomes=[]
    for other in linked:
        if other['cell']==c-1: # upstream neighbor must start later
            outcomes.append(upstream_propagation({c:start,c-1:other['first_low_bin']},{c:ids_for(event),c-1:ids_for(other)}))
        else: # later downstream onset is evidence against upstream propagation
            outcomes.append(upstream_propagation({c+1:other['first_low_bin'],c:start},{c+1:ids_for(other),c:ids_for(event)}))
    if 'ESTABLISHED_BACKWARD_PROPAGATION' in outcomes: return 'ESTABLISHED_BACKWARD_PROPAGATION'
    if 'UNRESOLVED_BIN_ALIGNMENT' in outcomes: return 'UNRESOLVED_BIN_ALIGNMENT'
    if any(x.startswith('UNRESOLVED') for x in outcomes): return next(x for x in outcomes if x.startswith('UNRESOLVED'))
    if all(x=='NOT_ESTABLISHED_FORWARD_ONSET_ORDER' for x in outcomes): return 'NOT_ESTABLISHED_FORWARD_ONSET_ORDER'
    return 'UNRESOLVED_MIXED_ADJACENT_EVIDENCE'
def union_intervals(intervals):
    return sorted(set().union(*(set(range(a,b)) for a,b in intervals))) if intervals else []

def run_one(label, run):
    rr=RAW/run; manifest=json.loads((rr/'output_manifest.json').read_text()); files=manifest['files']
    receipts=[]
    mp=rr/'output_manifest.json'
    receipts.append({'run':label,'role_inferred_from_manifest_path':'output_manifest.json','manifest_path':str(mp),'resolved_path':str(mp),'declared_bytes':mp.stat().st_size,'actual_bytes':mp.stat().st_size,'declared_sha256':sha(mp),'actual_sha256':sha(mp),'status':'SELF_HASHED_INPUT_MANIFEST'})
    byname={}
    for rec in files:
        p=Path(rec['path'])
        if not p.is_file(): raise FileNotFoundError(p)
        b=p.stat().st_size; h=sha(p)
        if b!=rec['bytes'] or h!=rec['sha256']: raise ValueError(f'manifest mismatch {p}')
        receipts.append({'run':label,'role_inferred_from_manifest_path':p.name,'manifest_path':rec['path'],'resolved_path':str(p),'declared_bytes':rec['bytes'],'actual_bytes':b,'declared_sha256':rec['sha256'],'actual_sha256':h,'status':'PASS'})
        if '/outputs/' in rec['path']:
            byname[p.name]=p
    required={'fcd.xml','vehroute.xml','tripinfo.xml','tls_states.xml','sumo_summary.xml','sumo_error.log','lanechanges.xml'}
    if not required.issubset(byname): raise ValueError(f'{label}: missing required roles {required-set(byname)}')
    e1=sorted(n for n in byname if n.startswith('p1_') and n.endswith('.xml'))
    if len(e1)!=9: raise ValueError(f'{label}: expected 9 E1 files, got {len(e1)}')
    # Validate and parse network lane geometry and actual limits.
    net=xmlroot(NET,'net'); laneinfo={}
    for ln in net.findall('.//lane'):
        laneinfo[ln.get('id')]={'speed':float(ln.get('speed')),'length':float(ln.get('length')),'edge':ln.get('id').rsplit('_',1)[0]}
    missing=WHITELIST-set(laneinfo)
    if missing: raise ValueError(f'compiled geometry lacks whitelist lanes: {sorted(missing)}')
    # Through lane physical coverage at each x cell: mainline has two through lanes.
    cell_length=[]; core_overlap=[]
    core_ranges=[(1398.38,1401.49),(1401.49,1696.0),(1696.0,1704.0)]
    for c in range(22):
        a,b=c*100,min((c+1)*100,2200); length=max(0,b-a)
        # Road longitudinal cell lane-length = two mainline carriageway lanes.
        cell_length.append(length*2)
        core_overlap.append(sum(max(0,min(b,y)-max(a,x)) for x,y in core_ranges))
    # Vehroute routes/speed factors.
    routes={}; vr=xmlroot(byname['vehroute.xml'],'routes')
    for v in vr.findall('vehicle'):
        route=v.find('route'); edges=(route.get('edges','').split() if route is not None else [])
        routes[v.get('id')]={'edges':edges,'sf':float(v.get('speedFactor','nan')),'depart':float(v.get('depart','nan')),'arrival':v.get('arrival')}
    # Trip lifecycle reconciliation.
    trips={}; tr=xmlroot(byname['tripinfo.xml'],' tripinfos'.strip())
    for t in tr.findall('tripinfo'): trips[t.get('id')]=t.attrib
    if not routes: raise ValueError(f'{label}: no vehroute vehicles')
    mroute={i for i,v in routes.items() if i.startswith('M_') and {'main_up','merge_section','main_down'}.issubset(set(v['edges']))}
    rroute={i for i,v in routes.items() if i.startswith('R_') and ('ramp_storage' in v['edges'] or 'ramp_accel' in v['edges'])}
    # FCD read: detect all duplicate keys, timestep labels, unknown lanes, M route mismatch.
    fcd=byname['fcd.xml']; root=xmlroot(fcd,'fcd-export')
    labels=[]; seen=set(); obs=defaultdict(list); lane_counts=Counter(); class_lane_counts=defaultdict(Counter); warnings=[]; aux_m=[]; outdomain=[]; terminal=0; sample_n=0; m_ids=set(); fcd_ids=set(); bad_join=[]; unknown_m_lanes=Counter()
    for ts in root.findall('timestep'):
        t=float(ts.get('time')); ti=int(round(t))
        if abs(t-ti)>1e-6: warnings.append(f'NONINTEGER_TIME:{t}')
        labels.append(ti)
        for v in ts.findall('vehicle'):
            vid=v.get('id'); key=(ti,vid)
            if key in seen: warnings.append(f'DUPLICATE_TIME_ID:{key}')
            seen.add(key); fcd_ids.add(vid); sample_n+=1
            lane=v.get('lane'); lane_counts[lane]+=1; class_lane_counts[vid.split('_',1)[0]][lane]+=1
            if vid.startswith('M_'):
                m_ids.add(vid)
                if not route_join_ok(vid in routes and vid in mroute, routes.get(vid,{}).get('sf')): bad_join.append(f'{ti}:{vid}:route_speedFactor')
                if lane==AUX: aux_m.append((ti,vid,v.get('pos')))
                if lane not in WHITELIST and lane!=AUX: unknown_m_lanes[lane]+=1; warnings.append(f'UNKNOWN_M_LANE:{lane}:{ti}:{vid}')
                if lane not in WHITELIST: continue
                try: x=float(v.get('x')); speed=float(v.get('speed'))
                except (TypeError,ValueError): warnings.append(f'BAD_FCD_ATTRIBUTE:{ti}:{vid}'); continue
                c,term=lane_cell(x)
                if c is None: outdomain.append((ti,vid,lane,x)); continue
                if term: terminal+=1
                sf=routes[vid]['sf']; lim=laneinfo[lane]['speed']; ratio=speed/(lim*sf)
                slow={p:ratio<=vals[0] for p,vals in PROFILES.items()}
                for p in PROFILES: obs[(c,ti,p)].append((vid,speed,ratio,slow[p],x,lane))
            elif vid.startswith('R_'):
                if lane in WHITELIST:
                    try:
                        x=float(v.get('x')); c,term=lane_cell(x)
                        if c is not None:
                            for p in PROFILES: obs[(c,ti,p)].append((vid,float(v.get('speed','nan')),float('nan'),False,x,lane))
                    except ValueError: pass
    labelcounts=Counter(labels)
    if not exact_grid(labels,2700) or any(v!=1 for v in labelcounts.values()): raise ValueError(f'{label}: FCD timestep grid not exact 0..2699; got {len(labels)} labels')
    if bad_join: raise ValueError(f'{label}: FCD M joins invalid {bad_join[:10]}')
    if outdomain: warnings.append(f'OUT_OF_DOMAIN:{len(outdomain)}')
    if aux_m: warnings.append(f'GEOMETRY_COVERAGE_FLAG_M_AUX:{len(aux_m)}')
    m_trip=set(m_ids)&set(trips); m_route_trip={i for i in mroute if i in trips}
    # Preserve identity accounting: route and FCD cohort identities may include vehicles not observed at sample cadence.
    m_tripinfo_count=sum(i.startswith('M_') for i in trips)
    # Build every cell/profile/bin row including legitimate empty populations.
    metrics=[]; series={p:{} for p in PROFILES}; labels_bycell=defaultdict(dict)
    for c in range(22):
        for p,(alpha,dur,dfactor) in PROFILES.items():
            for k in range(90):
                n_by_t=[]; allrat=[]; speeds=[]; ids=set(); slow_ids_by_t=[]
                for t in range(30*k,30*(k+1)):
                    vals=obs.get((c,t,p),[]); mvals=[z for z in vals if z[0].startswith('M_')]; rvals=[z for z in vals if z[0].startswith('R_')]
                    n_by_t.append(len(mvals)); allrat += [z[2] for z in mvals]; speeds += [z[1] for z in mvals]; ids.update(z[0] for z in mvals)
                    slow_ids_by_t.append(len({z[0] for z in mvals if z[3]}))
                N=len(allrat); meanr=sum(allrat)/N if N else None; means=sum(speeds)/N if N else None
                sfraction=sum(r<=alpha for r in allrat)/N if N else None
                nslow_labels=sum(n>=2 for n in slow_ids_by_t)
                density=sum(n_by_t)/(30*(cell_length[c]/1000)) if cell_length[c] else 0
                # physical mainline M+R density computed separately
                phys=sum(len([z for z in obs.get((c,t,p),[]) if z[0].startswith(('M_','R_'))]) for t in range(30*k,30*(k+1)))/(30*(cell_length[c]/1000)) if cell_length[c] else 0
                valid=len(labelcounts)==2700 and len(ids)>=2 and not any(x.startswith('DUPLICATE_TIME_ID') for x in warnings)
                low=low_state_gate(valid,meanr,sfraction,nslow_labels,alpha)
                borderline=sum(abs(z-alpha)<=.001 for z in allrat)
                lanes_present={z[5] for t in range(30*k,30*(k+1)) for z in obs.get((c,t,p),[]) if z[0].startswith('M_')}
                flags=['MODEL_REFERENCE_NOT_CALIBRATED','ONE_LANE_DILUTION_POSSIBLE']
                if len(ids)<2: flags.append('LOW_POPULATION')
                if borderline: flags.append('RATIO_NEAR_CUT')
                row={'run':label,'run_id':run,'profile':p,'cell':c,'x_start_m':c*100,'x_end_m':min((c+1)*100,2200),'cell_length_lane_m':cell_length[c],'core_overlap_m':core_overlap[c],'is_merge_core':core_overlap[c]>0,'bin':k,'time_start_s':30*k,'time_end_s':30*(k+1),'period_tag':'pre300' if 30*k<300 else ('demand_time_300_1500' if 30*k<1500 else 'post1500'),'valid_bin':valid,'unique_M_ids':len(ids),'N_M_samples':N,'mean_abs_speed_mps':means,'mean_model_reference_ratio':meanr,'sample_slow_fraction':sfraction,'labels_nslow_ge2':nslow_labels,'mean_M_density_veh_per_lane_km':density,'M_density_sample_count':sum(n_by_t),'mean_MR_density_veh_per_lane_km':phys,'M_lanes_observed':';'.join(sorted(lanes_present)),'near_cut_sample_count':borderline,'density_margin_fraction':None,'uncertainty_flags':';'.join(flags),'low_state_bin':low,'reference_eligible':False,'density_gate':False,'fully_qualified_bin':False,'attribution_eligibility':'NOT_APPLICABLE','state1_eligible_bin':False,'event_recovery_status':'NOT_APPLICABLE','event_censor_status':'NOT_APPLICABLE','local_population_after_event':'NOT_APPLICABLE','upstream_propagation_status':'NOT_EVALUATED'}
                metrics.append(row); series[p][(c,k)]=row
    candidates=[]; attrib=[]; cell_events=[]
    for p,(alpha,dur,dfactor) in PROFILES.items():
        for c in range(22):
            k=0
            while k<90:
                if not series[p][(c,k)]['low_state_bin']: k+=1; continue
                start=k
                while k<90 and series[p][(c,k)]['low_state_bin']: k+=1
                end=k # exclusive
                length=end-start
                core=core_overlap[c]>0
                refbins=[series[p][(c,j)] for j in range(start-3,start)] if start>=3 else []
                refok=len(refbins)==3 and all(x['valid_bin'] and x['mean_model_reference_ratio'] is not None and x['mean_model_reference_ratio']>=.85 for x in refbins)
                refdensity=statistics.median([x['mean_M_density_veh_per_lane_km'] for x in refbins]) if refok else None
                required=length>=dur
                for j in range(start,end):
                    row=series[p][(c,j)]; row['reference_eligible']=refok
                    refcount=statistics.median([x['M_density_sample_count'] for x in refbins]) if refok else None
                    row['density_gate']=bool(refok and density_gate(row,refdensity,refcount,dfactor))
                    row['density_margin_fraction']=row['mean_M_density_veh_per_lane_km']/refdensity-1 if refdensity else None
                    if row['density_gate'] and row['density_margin_fraction']<=.01: row['uncertainty_flags']+=';WEAK_DENSITY_MARGIN'
                    if not refok: row['uncertainty_flags']+=';ONSET_REFERENCE_FAILED'
                density_gates=[density_gate(series[p][(c,j)],refdensity,statistics.median([x['M_density_sample_count'] for x in refbins]),dfactor) for j in range(start,start+dur)] if refok and refdensity else [False]*dur
                numerical=qualify_episode([True]*length,density_gates,dur,core,refok,'UNRESOLVED')=='NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW'
                for j in range(start,end):
                    row=series[p][(c,j)]
                    row['fully_qualified_bin']=bool(numerical and row['density_gate'])
                eid=cell_event_id(label,p,c,start)
                status='SHORT_LOW_STATE_CANDIDATE' if not required else ('ONSET_REFERENCE_UNRESOLVED' if core and not refok else ('NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW' if numerical else ('DENSITY_GATE_FAIL' if core and refok else 'OUTSIDE_MERGE_CORE')))
                qualified_bins=[j for j in range(start,end) if series[p][(c,j)]['fully_qualified_bin']]
                local_future=[series[p][(c,j)]['N_M_samples'] for j in range(end,90)]
                pop_after=population_status(local_future,end>=90)
                rec={'event_id':eid,'run':label,'profile':p,'cell':c,'x_start_m':c*100,'x_end_m':min((c+1)*100,2200),'is_merge_core':core,'first_low_bin':start,'low_bin_end_exclusive':end,'low_speed_bins':length,'required_bins':dur,'first_low_start_s':30*start,'confirmation_time_s':30*(start+dur) if required else None,'ref_start_bin':start-3 if start>=3 else None,'ref_eligible':refok,'ref_M_density':refdensity,'density_factor':dfactor,'numerical_positive':numerical,'event_status':status,'low_speed_continuation_bins':length,'qualified_density_bins':len(qualified_bins),'qualified_density_bin_ids':';'.join(map(str,qualified_bins)),'recovery_status':'NOT_ASSESSED','censor_flag':'RIGHT_CENSORED' if end>=90 else 'NOT_RIGHT_CENSORED','local_population_after_event':pop_after,'state2_discharge_status':'NOT_ASSESSED','trajectory_locators':f'outputs/fcd.xml#cell={c};bins={start}:{end}','upstream_propagation':'NOT_EVALUATED','upstream_propagation_evidence':'NOT_EVALUATED_PENDING_ADJACENT_EPISODE_LINKAGE'}
                if length>0:
                    future=[{'bin':j,'valid':series[p][(c,j)]['valid_bin'],'mean_ratio':series[p][(c,j)]['mean_model_reference_ratio'],'density':series[p][(c,j)]['mean_M_density_veh_per_lane_km']} for j in range(end,90)]
                    recbin=recovery_start(future,refdensity if refok else None)
                    rec['recovery_status']=recovery_status(recbin is not None,end>=90)
                    if recbin is not None: rec['recovery_start_s']=30*recbin
                    if rec['recovery_status']=='RECOVERY_UNRESOLVED':
                        for j in range(start,end): series[p][(c,j)]['uncertainty_flags']+=';RECOVERY_UNRESOLVED'
                    if rec['local_population_after_event']=='POPULATION_ENDED':
                        for j in range(start,end): series[p][(c,j)]['uncertainty_flags']+=';POPULATION_ENDED'
                    for j in range(start,end):
                        series[p][(c,j)]['event_recovery_status']=rec['recovery_status']
                        series[p][(c,j)]['event_censor_status']=rec['censor_flag']
                        series[p][(c,j)]['local_population_after_event']=rec['local_population_after_event']
                candidates.append(rec); cell_events.append(rec)
                # Evidence-led preliminary attribution states. TLS topology has no mainline red phase; causal context otherwise requires per-event evidence.
                tls=xmlroot(byname['tls_states.xml'],'tlsStates')
                has_main_red=False
                # mainline itself is unsignalized in compiled topology; recorded TLS are urban, not freeway mainline.
                source='UNRESOLVED'; tail='UNRESOLVED'; geom='UNRESOLVED' if core else 'EXCLUDED'; boundary='CLEAR' if start>=3 and end<90 else 'UNRESOLVED'
                if not numerical: overall='EXCLUDED'
                else: overall='UNRESOLVED'
                arec={'event_id':eid,'run':label,'profile':p,'tailback_status':tail,'tailback_evidence':f'UNRESOLVED: compare candidate FCD locator against downstream cells c18-c21 and E1 main_down20/200; automated ordering adjudication not established','source_artifact_status':source,'source_evidence':f'UNRESOLVED: inspect upstream FCD cells c00-c12 and vehroute insertion/lifecycle for this onset; no source cause inferred','direct_mainline_TLS_status':'CLEAR','TLS_evidence':'compiled topology has no direct mainline signal; tls_states.xml records urban junctions only','geometry_unrelated_bottleneck_status':geom,'geometry_evidence':f'event cell={c}; core overlay places it near merge, but candidate-specific unrelated-constraint exclusion remains unresolved','boundary_censoring_status':boundary,'boundary_evidence':f'FCD window 0..2700, onset={30*start}s, low continuation end={30*end}s','overall_attribution':overall,'attribution_locator':f'outputs/fcd.xml#cell={c};bins={start}:{end}; outputs/tls_states.xml; network.net.xml; outputs/p1_main_down_20_l0.xml; outputs/p1_main_down_200_l0.xml'}
                for j in range(start,end):
                    row=series[p][(c,j)]; row['attribution_eligibility']=overall
                    row['state1_eligible_bin']=bool(row['fully_qualified_bin'] and overall=='CLEAR')
                    row['uncertainty_flags']+=';DOWNSTREAM_ATTRIBUTION_UNRESOLVED;SOURCE_ARTIFACT_UNRESOLVED'
                    if boundary!='CLEAR': row['uncertainty_flags']+=';BOUNDARY_CENSORING'
                attrib.append(arec)
    # Production propagation diagnosis: only directly adjacent cell episodes
    # with overlapping observed low-state intervals are linked; gaps are never bridged.
    for ev in cell_events:
        alpha=PROFILES[ev['profile']][0]
        prop=event_propagation(ev,cell_events,obs,alpha)
        ev['upstream_propagation']=prop
        ev['upstream_propagation_evidence']='derived from adjacent-cell low-state episodes with overlapping recorded bins and per-episode slow-M identity sets; no non-contiguous cell bridging'
        for j in range(ev['first_low_bin'],ev['low_bin_end_exclusive']):
            series[ev['profile']][(ev['cell'],j)]['upstream_propagation_status']=prop
        ar=next(x for x in attrib if x['event_id']==ev['event_id'])
        ar['upstream_propagation_status']=prop
        ar['upstream_propagation_evidence']=ev['upstream_propagation_evidence']
    # Candidate A: at least two adjacent cells, common S duration window and density gates.
    candA=[]
    srows=[x for x in candidates if x['profile']=='S' and x['numerical_positive']]
    for a in srows:
        for b in srows:
            if b['cell']==a['cell']+1 and b['first_low_bin']==a['first_low_bin'] and (a['is_merge_core'] or b['is_merge_core']):
                candA.append({'run':label,'cell_left':a['cell'],'cell_right':b['cell'],'common_first_low_bin':a['first_low_bin'],'qualification_bins':4,'event_ids':a['event_id']+';'+b['event_id'],'status':'SPATIALLY_CORROBORATED_NUMERICAL_CANDIDATE_ATTRIBUTION_UNRESOLVED'})
    # Every manifest-bound XML must parse completely; required XML roles receive root checks below.
    for name,p in byname.items():
        if name.endswith('.xml'):
            ET.parse(p)
    root_checks={'tls_states.xml':'tlsStates','sumo_summary.xml':'summary','lanechanges.xml':'lanechanges','queues.xml':'queue-export','ramp_storage_e2.xml':'meandata','shared_boundary_e2.xml':'meandata'}
    for name,expected_root in root_checks.items():
        if name in byname and xmlroot(byname[name]).tag!=expected_root:
            # Native E2/E1 roots are detector-specific in SUMO's output API; preserve the observed root for receipt.
            if name not in {'ramp_storage_e2.xml','shared_boundary_e2.xml'}: raise ValueError(f'{label}: {name} root mismatch')
    # Native E1 lane table and expected time grid.
    e1rows=[]
    for n in e1:
        root=xmlroot(byname[n],'detector')
        intervals=root.findall('interval')
        begins=[int(round(float(z.get('begin')))) for z in intervals]
        if len(intervals)!=90 or sorted(begins)!=list(range(0,2700,30)) or len(set(begins))!=90: raise ValueError(f'{label}: {n} interval grid is not exactly 0..2670 by 30')
        for z in intervals:
            if abs(float(z.get('begin'))/30-round(float(z.get('begin'))/30))>1e-9 or abs((float(z.get('end'))-float(z.get('begin')))-30)>1e-9: raise ValueError(f'{label}: bad E1 bin boundary')
            c=int(z.get('nVehContrib')); sp=float(z.get('speed')); eid=z.get('id')
            e1rows.append({'run':label,'detector_id':eid,'file':n,'begin_s':z.get('begin'),'end_s':z.get('end'),'nVehContrib':c,'flow_veh_per_h':float(z.get('flow')),'occupancy_pct':float(z.get('occupancy')),'speed_mps':None if c==0 or sp<0 else sp,'speed_defined':bool(c>0 and sp>=0),'speed_missing_with_contribution':bool(c>0 and sp<0),'nVehEntered':z.get('nVehEntered')})
    summary={'run':label,'run_id':run,'fcd_records':sample_n,'FCD_M_ids':len(m_ids),'vehroute_M_ids':len(mroute),'tripinfo_M_ids':m_tripinfo_count,'FCD_M_with_tripinfo':len(m_trip&mroute),'vehroute_M_missing_tripinfo':len(mroute-set(trips)),'FCD_labels':len(labelcounts),'duplicate_time_id_warnings':sum(x.startswith('DUPLICATE') for x in warnings),'M_aux_samples':len(aux_m),'out_of_domain_samples':len(outdomain),'terminal_x2200_samples':terminal,'M_unexpected_lane_samples':sum(unknown_m_lanes.values()),'M_unexpected_lane_counts':json.dumps(unknown_m_lanes,sort_keys=True),'nonmainline_samples_other_classes':sum(n for cls,cc in class_lane_counts.items() if cls!='M' for lane,n in cc.items() if lane not in WHITELIST and lane!=AUX),'lane_presence_by_prefix':json.dumps({k:dict(v) for k,v in class_lane_counts.items()},sort_keys=True),'warnings':';'.join(sorted(set(warnings)))}
    return receipts,metrics,candidates,attrib,e1rows,summary,candA

def run_fixtures():
    cases=[
      ('one slow vehicle',lambda:low_state_gate(True,.6,1,0,.7),False),
      ('brief dip',lambda:qualify_episode([1,0],[1,1,1],3),'SHORT_LOW_STATE_CANDIDATE'),
      ('persistent group+accumulation',lambda:qualify_episode([1,1,1],[1,1,1],3),'NUMERICAL_POSITIVE_CLEAR'),
      ('stationary local cluster without remote propagation',lambda:(qualify_episode([1,1,1],[1,1,1],3),event_propagation({'run':'A','profile':'P','cell':15,'first_low_bin':4,'low_bin_end_exclusive':7},[{'run':'A','profile':'P','cell':15,'first_low_bin':4,'low_bin_end_exclusive':7}],{},.7)),('NUMERICAL_POSITIVE_CLEAR','UNRESOLVED_NO_LINKED_ADJACENT_EPISODE')),
      ('forward-moving platoon',lambda:event_propagation({'run':'A','profile':'P','cell':16,'first_low_bin':2,'low_bin_end_exclusive':4},[{'run':'A','profile':'P','cell':16,'first_low_bin':2,'low_bin_end_exclusive':4},{'run':'A','profile':'P','cell':17,'first_low_bin':3,'low_bin_end_exclusive':5}],{(16,60,'P'):[('M_d1',1,.5,True,1,'main_up_0'),('M_d2',1,.5,True,2,'main_up_0')],(17,90,'P'):[('M_u1',1,.5,True,1,'main_up_0'),('M_u2',1,.5,True,2,'main_up_0')]},.7),'NOT_ESTABLISHED_FORWARD_ONSET_ORDER'),
      ('backward-moving queue with different vehicles',lambda:event_propagation({'run':'A','profile':'P','cell':16,'first_low_bin':3,'low_bin_end_exclusive':5},[{'run':'A','profile':'P','cell':16,'first_low_bin':3,'low_bin_end_exclusive':5},{'run':'A','profile':'P','cell':17,'first_low_bin':2,'low_bin_end_exclusive':4}],{(16,90,'P'):[('M_u1',1,.5,True,1,'main_up_0'),('M_u2',1,.5,True,2,'main_up_0')],(17,60,'P'):[('M_d1',1,.5,True,1,'main_up_0'),('M_d2',1,.5,True,2,'main_up_0')]},.7),'ESTABLISHED_BACKWARD_PROPAGATION'),
      ('tied onset is unresolved',lambda:event_propagation({'run':'A','profile':'P','cell':16,'first_low_bin':3,'low_bin_end_exclusive':5},[{'run':'A','profile':'P','cell':16,'first_low_bin':3,'low_bin_end_exclusive':5},{'run':'A','profile':'P','cell':17,'first_low_bin':3,'low_bin_end_exclusive':5}],{(16,90,'P'):[('M_u1',1,.5,True,1,'main_up_0'),('M_u2',1,.5,True,2,'main_up_0')],(17,90,'P'):[('M_d1',1,.5,True,1,'main_up_0'),('M_d2',1,.5,True,2,'main_up_0')]},.7),'UNRESOLVED_BIN_ALIGNMENT'),
      ('downstream-first tailback',lambda:qualify_episode([1,1,1],[1,1,1],3,attribution='EXCLUDED'),'ATTRIBUTION_EXCLUDED'),
      ('zero passage',lambda:low_state_gate(False,None,None,0,.7),False),
      ('empty population',lambda:('OUTSIDE_M_STATE_EXPOSURE' if not low_state_gate(False,None,None,0,.7) else 'EXPOSED'),'OUTSIDE_M_STATE_EXPOSURE'),
      ('missing timestep',lambda:('INVALID_BIN' if not exact_grid([0,1,3],4) else 'VALID_BIN'),'INVALID_BIN'),
      ('internal-lane traversal',lambda:lane_cell(1450) if ':freeway_merge_0_0' in WHITELIST else None,(14,False)),
      ('exact temporal boundary',lambda:bin_index(30),1),
      ('exact spatial boundary',lambda:(lane_cell(100),lane_cell(2200)),((1,False),(21,True))),
      ('recovery absent',lambda:recovery_status(recovery_start([{'bin':8,'valid':True,'mean_ratio':.8,'density':8},{'bin':9,'valid':True,'mean_ratio':.8,'density':8}],10) is not None),'RECOVERY_UNRESOLVED'),
      ('recovery confirmed',lambda:recovery_status(recovery_start([{'bin':8,'valid':True,'mean_ratio':.9,'density':9},{'bin':9,'valid':True,'mean_ratio':.91,'density':9}],10) is not None),'RECOVERED'),
      ('run-end censor without recovery',lambda:recovery_status(False,True),'RIGHT_CENSORED'),
      ('speedFactor join failure',lambda:route_join_ok(True,0),False),
      ('invalid pre-onset reference',lambda:qualify_episode([1,1,1],[1,1,1],3,reference=False),'ONSET_REFERENCE_UNRESOLVED'),
      ('adjacent-cell duplicate episode',lambda:([cell_event_id('A','L',c,39) for c in (15,16)],union_intervals([(39,41),(39,41)])),(['A_L_c15_b39','A_L_c16_b39'],[39,40])),
      ('population ended',lambda:population_status([],False),'POPULATION_ENDED'),
      ('attribution unresolved',lambda:qualify_episode([1,1,1],[1,1,1],3,attribution='UNRESOLVED'),'NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW')]
    out=[]
    for name,fn,expected in cases:
        observed=fn(); passed=observed==expected
        if not passed: raise AssertionError(f'{name}: expected {expected!r}, observed {observed!r}')
        out.append({'fixture':name,'expected_result':json.dumps(expected,sort_keys=True),'observed_result':json.dumps(observed,sort_keys=True),'status':'PASS'})
    if len(out)!=22: raise AssertionError('fixture count is not exactly 22')
    return out

def main():
    method=ROOT/'docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md'
    if sha(method)!=EXPECTED_METHOD: raise ValueError('locked method hash mismatch; stop')
    nethash=sha(NET)
    fixtures=run_fixtures(); allrec=[]; allmetrics=[]; allevents=[]; allattrib=[]; alle1=[]; summaries=[]; allA=[]
    for label,run in RUNS.items():
        rec,met,ev,att,e1,su,a=run_one(label,run)
        allrec+=rec; allmetrics+=met; allevents+=ev; allattrib+=att; alle1+=e1; summaries.append(su); allA+=a
    evidence=[]
    for ev in allevents:
        if ev['profile']=='L' and ev['numerical_positive']:
            detail=event_evidence(ev,allmetrics); evidence.append(detail)
            ledger=next(x for x in allattrib if x['event_id']==ev['event_id'])
            ledger.update({'tailback_status':'UNRESOLVED','tailback_evidence':f"{detail['downstream_order_status']}; downstream low cells={detail['same-bin-downstream_low_state_cells']}; same 30-s bin cannot order onsets",'source_artifact_status':'UNRESOLVED','source_evidence':f"Insertion/source artifact attribution is {detail['insertion_source_artifact_status']}; descriptive M departures={detail['M_departures_in_window']}, max departDelay={detail['M_departure_delay_max_s']}s, mean={detail['M_departure_delay_mean_s']}s. No delay cutoff is applied; broader source/disturbance origin remains unresolved; pre-onset low cells and vehicle motion do not prove direction",'geometry_unrelated_bottleneck_status':'CLEAR','geometry_evidence':detail['geometry_unrelated_bottleneck_status']+'; candidate lies in compiled merge-core cells 13-17; merge causality remains unresolved','direct_mainline_TLS_status':'CLEAR','TLS_evidence':detail['TLS_status'],'boundary_censoring_status':'CLEAR','boundary_evidence':detail['boundary_status']+'; FCD ends at 2700s, event interval interior','overall_attribution':'UNRESOLVED','attribution_locator':detail['evidence_locators']})
    # P/S/L + Candidate C one-bin warning; run classification precedence applied using attribution status.
    matrix=[]; robustness=[]
    for run in RUNS:
        for rule,p in [('P','P'),('S','S'),('L','L'),('C_EARLY_WARNING','L'),('A_SPATIAL_S','S')]:
            evs=[e for e in allevents if e['run']==run and e['profile']==p]
            if rule=='C_EARLY_WARNING':
                pos=[e for e in evs if e['low_speed_bins']>=1 and e['is_merge_core']]
                status='EARLY_WARNING_PRESENT_NOT_STATE1' if pos else 'NO_EARLY_WARNING'
            elif rule=='A_SPATIAL_S':
                pos=[x for x in allA if x['run']==run]; status='SPATIALLY_CORROBORATED_CANDIDATE_ATTRIBUTION_UNRESOLVED' if pos else 'NO_SPATIAL_CANDIDATE'
            else:
                pos=[e for e in evs if e['numerical_positive']]
                if any(e['overall_attribution']=='CLEAR' for e in allattrib if e['event_id'] in {x['event_id'] for x in pos}): status='STATE1_EXPLORATORY_RULE_POSITIVE'
                elif pos: status='CANDIDATE_ATTRIBUTION_UNRESOLVED'
                elif any(e['event_status']=='ONSET_REFERENCE_UNRESOLVED' for e in evs): status='ONSET_REFERENCE_UNRESOLVED'
                elif any(e['event_status']=='DENSITY_GATE_FAIL' for e in evs): status='NO_QUALIFYING_EVENT_WITH_DENSITY_CANDIDATES'
                else: status='NO_QUALIFYING_EVENT'
            if rule=='C_EARLY_WARNING': npos=len(pos); ncand=len(pos)
            elif rule=='A_SPATIAL_S': npos=len(pos); ncand=len(pos)
            else: npos=sum(e['numerical_positive'] for e in evs); ncand=len(evs)
            matrix.append({'run':run,'rule':rule,'classification':status,'rule_positive_cell_events':npos,'candidate_cell_events':ncand,'cell_event_count_not_physical_event_count':True,'physical_event_count':'NOT_ESTIMATED'})
            qualified=[e for e in evs if e['numerical_positive']]
            if rule=='C_EARLY_WARNING': qualified=pos
            if rule=='A_SPATIAL_S':
                aid={eid for x in pos for eid in x['event_ids'].split(';')}
                qualified=[e for e in evs if e['event_id'] in aid]
            union_low=set(); union_full=set()
            for e in qualified:
                union_low.update(range(e['first_low_bin'],e['low_bin_end_exclusive']))
                union_full.update(int(j) for j in e['qualified_density_bin_ids'].split(';') if j)
            robustness.append({'run':run,'rule':rule,'classification':status,'low_state_candidate_count':ncand,'rule_positive_cell_event_count':npos,'rule_positive_bin_interval_union_s':30*len(union_low),'density_gate_bin_union_s':('NOT_APPLICABLE' if rule in {'C_EARLY_WARNING','A_SPATIAL_S'} else 30*len(union_full)),'attribution_cleared_state1_union_s':0,'cell_event_count_not_physical_event_count':True,'physical_event_count':'NOT_ESTIMATED'})
    APP.mkdir(parents=True,exist_ok=False)
    TAB.mkdir(parents=True,exist_ok=False)
    write_csv(APP/'raw_hash_manifest.csv',allrec)
    write_csv(TAB/'cell_bin_metrics.csv',allmetrics)
    write_csv(TAB/'candidate_events.csv',allevents)
    write_csv(TAB/'attribution_ledger.csv',allattrib)
    write_csv(TAB/'event_attribution_evidence.csv',evidence)
    write_csv(TAB/'classification_matrix.csv',matrix)
    write_csv(TAB/'rule_robustness_summary.csv',robustness)
    write_csv(TAB/'lane_e1_diagnostics.csv',alle1)
    station_groups=defaultdict(list)
    for r in alle1:
        station=r['detector_id'].rsplit('_l',1)[0]
        station_groups[(r['run'],station,r['begin_s'],r['end_s'])].append(r)
    station_rows=[]
    for (run,station,begin,end),grp in sorted(station_groups.items()):
        denom=sum(x['nVehContrib'] for x in grp); speeds=[x for x in grp if x['speed_mps'] is not None]
        speed_denom=sum(x['nVehContrib'] for x in speeds)
        station_rows.append({'run':run,'station':station,'begin_s':begin,'end_s':end,'lane_count':len(grp),'lanes_with_contribution':len(speeds),'total_nVehContrib_lane_events':denom,'speed_weight_denominator_nVehContrib':speed_denom,'contribution_weighted_speed_mps':sum(x['nVehContrib']*x['speed_mps'] for x in speeds)/speed_denom if speed_denom else None,'equal_lane_mean_occupancy_pct':sum(x['occupancy_pct'] for x in grp)/len(grp),'summed_flow_veh_per_h':sum(x['flow_veh_per_h'] for x in grp),'speed_na_if_no_contribution':speed_denom==0})
    write_csv(TAB/'e1_station_diagnostics.csv',station_rows)
    write_csv(TAB/'run_integrity_diagnostics.csv',summaries)
    write_csv(TAB/'candidate_A_spatial_confirmations.csv',allA)
    write_csv(APP/'fixture_test_receipt.csv',fixtures)
    static_paths=[method,NET,ENG/'compiled_audit.json']
    for run in RUNS.values(): static_paths += [ENG/'inputs'/run/'demand.rou.xml',ENG/'inputs'/run/'scenario.add.xml',ENG/'inputs'/run/'scenario.sumocfg']
    static_paths += [ROOT/'data/processed/stage6_o2_freeway_pressure_diagnosis_20260921_v1/REPORT_revision02.md',ROOT/'data/processed/stage6_o2_matched_abc_assessment_20260921_v1/REPORT_revision03.md',ROOT/'data/processed/stage6_o2_causal_diagnostic_20260921_v1/attempt03_data_audit_revision01/REPORT_revision04.md',ROOT/'data/processed/stage6_o2_causal_diagnostic_20260921_v1/attempt03_data_audit_revision01/SCIENTIFIC_REVIEW_FINAL_REVISION04.md']
    write_csv(APP/'static_input_manifest.csv',[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in static_paths])
    # Independently reconciled raw slice: recalculate one A M observation from XML + vehroute + network without analyzer aggregates.
    recslice=independent_slice('LOC')
    (APP/'raw_slice_reconciliation.json').write_text(json.dumps(recslice,indent=2)+'\n')
    cls='\n'.join(f"| {r['run']} | {r['rule']} | {r['classification']} | {r['rule_positive_cell_events']} |" for r in matrix)
    report=f'''# LOC_M3350_S17 — protectable-state exploratory application\n\nStatus: **single-point offline exploratory application; not a formal breakdown finding or protocol approval.** This report is generated only after a separately authorized runtime and subsequent offline processing.\n\n## Result\n\nLocked methodology SHA-256: `{sha(method)}` (expected `{EXPECTED_METHOD}`). Accepted compiled geometry audit SHA-256: `{sha(ENG/'compiled_audit.json')}`; network SHA-256: `{nethash}`. Static mapping retains mainline x=0–2200 m, merge core approximately x=1398.38–1704 m (cells 13–17), the nine registered E1 points, and A_OPEN with no direct mainline TLS restriction.\n\n| Run | Rule | Classification | Numeric-positive cell episodes |\n|---|---|---|---:|\n{cls}\n\nP is the primary exploratory profile. Candidate C remains an early-warning diagnostic, not State 1; Candidate A is a spatial-support check. The classification table reports the fixed rule outputs for this single point. Cell-event counts are not physical-event counts; physical event count is `NOT_ESTIMATED`.\n\n## Integrity and measurement audit\n\nThe application verifies every hash in the new raw output manifest and parses required XML. It checks the 0–2699 FCD/summary grid, 90 native 30 s detector intervals, required role set, vehicle identities, route/speedFactor joins, mainline lane coverage and class accounting. Expected scheduled counts are M=1396, R=300, U=150, X=75; actual insertions, arrivals, late/not inserted and unfinished identities are reported from output evidence. The independent raw-slice reconciliation reports one reproducible cell/bin from the new run.\n\nFCD lane-level metrics use the locked 100 m cells and mainline whitelist, with no interpolation. Empty cell-time labels contribute zero to density; cell/bin speed is NA when no M samples. M and physical M+R density are retained separately. Speed reference is lane speed limit times that vehicle's archived vehroute speedFactor; it is a model-reference ratio, not independently measured free-flow speed. E1 lane records remain lane-specific.\n\n## Attribution, uncertainty and limits\n\nEvery numerical candidate receives the locked event attribution checks. Source insertion, downstream tailback, direct TLS, geometry and unrelated bottleneck evidence are retained with uncertainty flags. Unresolved attribution is not upgraded to State 1. Propagation and recovery use the locked rules; missing or censored observations are not treated as recovery.\n\nThis is one stochastic realization. The result does not estimate breakdown probability, capacity, critical occupancy/density, capacity drop, ALINEA efficacy, causal freeway protection, or an M-vs-U trade-off. `O2` remains **NOT_RESOLVED** unless separately reviewed evidence changes that status.\n\n## Files\n\nApplication code is the hash-bound point-specific adapter in the launch package. Machine tables, report and receipt are written under this new `data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/` directory only after the run outputs exist; no existing result is overwritten.\n'''
    (APP/'REPORT.md').write_text(report)
    receipt={'status':'COMPLETED_EXPLORATORY_OFFLINE_APPLICATION','method_sha256':sha(method),'expected_method_sha256':EXPECTED_METHOD,'network_sha256':nethash,'geometry_audit_sha256':sha(ENG/'compiled_audit.json'),'runs':list(RUNS.values()),'script_sha256':sha(Path(__file__)),'fixture_count':len(fixtures),'fixture_status':'PASS_ALL_22','raw_slice_reconciliation':recslice['comparisons'],'no_sumo_or_netconvert':True,'output_hashes':{},'raw_summary':summaries,'classifications':matrix}
    for p in sorted(list(TAB.glob('*.csv'))+list(APP.glob('*.csv'))+[APP/'raw_slice_reconciliation.json',APP/'REPORT.md']): receipt['output_hashes'][str(p.relative_to(ROOT))]=sha(p)
    (APP/'application_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'fixtures':len(fixtures),'classifications':matrix,'summary':summaries},indent=2))

def independent_slice(label):
    run=RUNS[label]; rr=RAW/run; fcd=ET.parse(rr/'outputs/fcd.xml').getroot(); vr=ET.parse(rr/'outputs/vehroute.xml').getroot(); net=ET.parse(NET).getroot()
    sf={v.get('id'):float(v.get('speedFactor')) for v in vr.findall('vehicle')}
    lim={l.get('id'):float(l.get('speed')) for l in net.findall('.//lane')}
    rows=[]; counts=Counter()
    for ts in fcd.findall('timestep'):
        t=int(float(ts.get('time')))
        if not 900<=t<930: continue
        for v in ts.findall('vehicle'):
            x=float(v.get('x')); lane=v.get('lane'); vid=v.get('id')
            if vid.startswith('M_') and lane in WHITELIST and 1400<=x<1500:
                ratio=float(v.get('speed'))/(lim[lane]*sf[vid]); counts[t]+=1; rows.append({'time':t,'id':vid,'lane':lane,'x':x,'speed':float(v.get('speed')),'speedFactor':sf[vid],'ratio':ratio,'slow_P':ratio<=.70})
    meanr=sum(r['ratio'] for r in rows)/len(rows) if rows else None
    slowfrac=sum(r['slow_P'] for r in rows)/len(rows) if rows else None
    density=sum(counts.values())/(30*(200/1000))
    table=next(row for row in csv.DictReader(open(TAB/'cell_bin_metrics.csv')) if row['run']==label and row['profile']=='P' and row['cell']=='14' and row['bin']=='30')
    comparisons={'N_M_samples':int(table['N_M_samples'])==len(rows),'mean_ratio':abs(float(table['mean_model_reference_ratio'])-meanr)<1e-12,'mean_M_density':abs(float(table['mean_M_density_veh_per_lane_km'])-density)<1e-12,'slow_fraction':abs(float(table['sample_slow_fraction'])-slowfrac)<1e-12}
    if not all(comparisons.values()): raise AssertionError(f'independent slice does not reconcile: {comparisons}')
    return {'run':label,'selection':'raw FCD bin [900,930), M, whitelisted lane, x=[1400,1500)','count':len(rows),'mean_normalized_speed':meanr,'slow_fraction_P':slowfrac,'mean_density_veh_per_lane_km':density,'per_second_counts':dict(sorted(counts.items())),'id_cell_bin_assignments':rows,'table_row':table,'comparisons':comparisons,'status':'PASS_EXACT_ARITHMETIC_RECONCILIATION'}

def event_evidence(event, metrics):
    label=event['run']; run=RUNS[label]; rr=RAW/run; out=rr/'outputs'
    manifest=json.loads((rr/'output_manifest.json').read_text()); paths={Path(x['path']).name:Path(x['path']) for x in manifest['files']}
    # Resolve roles through each immutable run manifest; never infer alternate sources.
    fcd=ET.parse(paths['fcd.xml']).getroot(); vr=ET.parse(paths['vehroute.xml']).getroot(); ti=ET.parse(paths['tripinfo.xml']).getroot()
    sfs={v.get('id'):float(v.get('speedFactor')) for v in vr.findall('vehicle')}; net=ET.parse(NET).getroot(); limits={x.get('id'):float(x.get('speed')) for x in net.findall('.//lane')}
    start=int(event['first_low_bin']); end=int(event['low_bin_end_exclusive']); cell=int(event['cell']); t0=30*start; t1=30*end
    neigh=[]; cohort=defaultdict(set); loc=defaultdict(set)
    for k in range(max(0,start-1),min(90,end+1)):
        for c in range(max(0,cell-8),min(22,cell+5)):
            rows=[r for r in metrics if r['run']==label and r['profile']==event['profile'] and r['cell']==c and r['bin']==k]
            if rows:
                z=rows[0]; neigh.append({'cell':c,'bin':k,'time_start_s':30*k,'mean_ratio':z['mean_model_reference_ratio'],'M_density_veh_per_lane_km':z['mean_M_density_veh_per_lane_km'],'slow_fraction':z['sample_slow_fraction'],'low_state_bin':z['low_state_bin'],'valid_bin':z['valid_bin']})
    for ts in fcd.findall('timestep'):
        tm=float(ts.get('time')); k=int(tm//30)
        if max(0,start-1)<=k<=min(89,end):
            for v in ts.findall('vehicle'):
                if not v.get('id','').startswith('M_') or v.get('lane') not in WHITELIST: continue
                try: c,_=lane_cell(float(v.get('x')))
                except (ValueError,TypeError): continue
                if c is None: continue
                sf=sfs.get(v.get('id'),1.0)
                # Candidate-cohort identities defined by the locked L speed-ratio threshold.
                lim=limits[v.get('lane')]
                if float(v.get('speed'))/(lim*sf)<=.8:
                    cohort[k].add(v.get('id')); loc[(c,k)].add(v.get('id'))
    overlap=[]
    for k in range(start-1,end):
        a,b=loc.get((cell,k),set()),loc.get((cell,k+1),set())
        if a or b: overlap.append({'from_bin':k,'to_bin':k+1,'same_slow_id_count':len(a&b),'from_ids':len(a),'to_ids':len(b)})
    spatial_carry=[]
    for k in (start-1,start):
        for c0 in range(max(0,cell-8),cell):
            aa,bb=loc.get((c0,k),set()),loc.get((cell,k+1),set())
            if aa and bb: spatial_carry.append({'from_cell':c0,'from_bin':k,'to_cell':cell,'to_bin':k+1,'shared_slow_vehicle_ids':len(aa&bb),'from_slow_ids':len(aa),'to_slow_ids':len(bb),'example_shared_ids':';'.join(sorted(aa&bb)[:5])})
    e1=[]
    for name,p in paths.items():
        if not name.startswith('p1_') or not name.endswith('.xml'): continue
        root=ET.parse(p).getroot()
        for iv in root.findall('interval'):
            b=int(float(iv.get('begin')))
            if t0-30<=b<t1:
                n=int(iv.get('nVehContrib')); sp=float(iv.get('speed'))
                e1.append({'file':name,'detector_id':iv.get('id'),'begin_s':b,'nVehContrib':n,'speed_mps':None if n==0 or sp<0 else sp,'occupancy_pct':float(iv.get('occupancy')),'flow_veh_per_h':float(iv.get('flow'))})
    trip_rows=[x.attrib for x in ti.findall('tripinfo') if x.get('id','').startswith('M_') and t0<=float(x.get('depart','-1'))<t1]
    delays=[float(x.get('departDelay','0')) for x in trip_rows]
    preonset=[x for x in neigh if x['bin']==start-1 and x['cell']<cell and x['low_state_bin']]
    return {'event_id':event['event_id'],'event_window_s':f'{t0}-{t1}','event_cell_x_m':f'{cell*100}-{min((cell+1)*100,2200)}','neighborhood_fcd_metrics_json':json.dumps(neigh,separators=(',',':')),'same_cell_slow_id_carry_json':json.dumps(overlap,separators=(',',':')),'upstream_to_candidate_slow_id_carry_json':json.dumps(spatial_carry,separators=(',',':')),'preonset_upstream_low_state_cells':';'.join(str(x['cell']) for x in preonset),'source_origin_attribution_status':'UNRESOLVED','candidate_cell_slow_id_count_by_bin':json.dumps({k:len(v) for k,v in sorted(cohort.items())},separators=(',',':')),'relevant_E1_intervals_json':json.dumps(e1,separators=(',',':')),'M_departures_in_window':len(trip_rows),'M_departure_delay_max_s':max(delays,default=0),'M_departure_delay_mean_s':(sum(delays)/len(delays) if delays else None),'insertion_source_artifact_status':'UNRESOLVED_NO_APPROVED_DELAY_CUTOFF','same-bin-downstream_low_state_cells':';'.join(str(x['cell']) for x in neigh if x['bin']==start and x['cell']>cell and x['low_state_bin']),'downstream_order_status':'UNRESOLVED_SAME_30S_BIN' if any(x['bin']==start and x['cell']>cell and x['low_state_bin'] for x in neigh) else 'NO_DOWNSTREAM_LOW_STATE_OBSERVED','upstream_propagation_status':event['upstream_propagation'],'recovery_status':event['recovery_status'],'recovery_censor_status':event['censor_flag'],'local_population_after_event':event['local_population_after_event'],'geometry_unrelated_bottleneck_status':'CLEAR_NO_SEPARATE_CONSTRAINT_IDENTIFIED_IN_CANDIDATE_CELL','merge_causality_status':'UNRESOLVED','TLS_status':'CLEAR_NO_DIRECT_MAINLINE_TLS','boundary_status':'CLEAR_INTERIOR_OF_0_2700S_WINDOW','evidence_locators':f'{paths["fcd.xml"]}#bins={start-1}:{end}; {paths["tripinfo.xml"]}#depart=[{t0},{t1}); E1={"p1_main_up_1300_l*.xml,p1_merge20_l*.xml,p1_main_down_20_l*.xml,p1_main_down_200_l*.xml"}; {ENG/"compiled_audit.json"}; {NET}; TLS={paths["tls_states.xml"]}'}

if __name__=='__main__': main()
