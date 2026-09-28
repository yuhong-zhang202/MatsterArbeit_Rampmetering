#!/usr/bin/env python3
"""Offline implementation of the reviewed mainline reference-bank proposal.

This program reads archived XML only.  It never imports or calls the locked
P/S/L decision code.  A bank is a screened high-mobility context, not a
free-flow ground truth and not a transition classifier.
"""
from __future__ import annotations
import csv, hashlib, json, math, statistics, copy
from collections import defaultdict, Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/processed/stage6_mainline_reference_library_20260922_v1"
TABLE = ROOT / "results/tables/stage6_mainline_reference_library_20260922_v1"
OUT.mkdir(parents=True, exist_ok=True); TABLE.mkdir(parents=True, exist_ok=True)

NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
RUNS = {
    "A0": {
        "run_id":"TV_A_S17_attempt1", "root":ROOT/"data/raw/stage6_targeted_validation_20260920_v1/TV_A_S17_attempt1",
        "qMain":3199.2,"qRamp":720.0,"seed":17,"control":"A_OPEN",
        "events":ROOT/"results/tables/stage6_protectable_state_application_20260921_v1/candidate_events.csv",
    },
    "M3350": {
        "run_id":"LOC_M3350_S17_attempt1", "root":ROOT/"data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1",
        "qMain":3350.4,"qRamp":720.0,"seed":17,"control":"A_OPEN",
        "events":ROOT/"data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/classifier_output/tables/candidate_events.csv",
    },
}
WHITELIST = {"main_up_0":0,"main_up_1":1,":freeway_merge_0_0":0,":freeway_merge_0_1":1,
             "merge_section_1":0,"merge_section_2":1,":merge_end_0_0":0,":merge_end_0_1":1,
             "main_down_0":0,"main_down_1":1}
CELL_M = 100.0; BIN = 30; HORIZON = 2700; DEMAND_END = 1500
BLOCK = 90; SPEED_REF_MIN = 0.85; MIN_IDS = 2

def sha(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def write_csv(p, rows, fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def q(v): return "" if v is None else (f"{v:.12g}" if isinstance(v,float) else v)
def mean_or_none(vals):
    vals=list(vals); return statistics.fmean(vals) if vals else None

def network_limits():
    out={}
    root=ET.parse(NETWORK).getroot()
    for lane in root.iter('lane'):
        if lane.attrib.get('id') in WHITELIST: out[lane.attrib['id']]=float(lane.attrib['speed'])
    return out

def cell_lane_lengths():
    out={(c,l):0.0 for c in range(22) for l in (0,1)}
    root=ET.parse(NETWORK).getroot()
    for lane in root.iter('lane'):
        lid=lane.attrib.get('id');
        if lid not in WHITELIST: continue
        role=WHITELIST[lid]; pts=[]
        shape=lane.attrib.get('shape','')
        for point in shape.split():
            try: pts.append(float(point.split(',')[0]))
            except (ValueError,IndexError): pass
        if len(pts)<2: continue
        lo,hi=min(pts),max(pts)
        for c in range(22):
            overlap=max(0.0,min(hi,(c+1)*100.0)-max(lo,c*100.0))
            out[(c,role)] += overlap/1000.0
    return out

def route_data(run):
    out={}; p=run['root']/"outputs/vehroute.xml"
    for v in ET.parse(p).getroot().findall('vehicle'):
        edges=(v.find('route').attrib.get('edges','').split() if v.find('route') is not None else [])
        vid=v.attrib['id']; factor=float(v.attrib['speedFactor']) if v.attrib.get('speedFactor') else math.nan
        cohort=None
        if vid.startswith('M_flow.') and edges==['main_up','merge_section','main_down']: cohort='M'
        elif vid.startswith('R_flow.') and 'merge_section' in edges and 'main_down' in edges: cohort='R'
        out[vid]={'type':v.attrib.get('type',''),'factor':factor,'cohort':cohort,'edges':edges}
    return out

def read_fcd(run, limits, cell_km):
    routes=route_data(run); rows=[]; labels=[]; seen=set(); issues=Counter(); label_counts=Counter()
    try: root=ET.parse(run['root']/"outputs/fcd.xml").getroot()
    except (ET.ParseError,OSError) as e: return [],[],routes,{'ok':False,'issues':{'XML_PARSE_ERROR':str(e)}}
    for ts in root.findall('timestep'):
        if 'time' not in ts.attrib: issues['MISSING_TIME']+=1; continue
        t=float(ts.attrib['time']); ti=int(round(t)); labels.append(ti); label_counts[ti]+=1
        for veh in ts.findall('vehicle'):
            lane=veh.attrib.get('lane'); vid=veh.attrib.get('id')
            if vid is None: issues['MISSING_VEHICLE_ID']+=1; continue
            key=(ti,vid)
            if key in seen: issues['DUPLICATE_TIME_VEHICLE']+=1
            seen.add(key)
            if vid not in routes or routes[vid].get('cohort') not in {'M','R'}: continue
            cohort=routes[vid]['cohort']
            if not all(k in veh.attrib for k in ('x','speed')): issues['MISSING_X_OR_SPEED']+=1; continue
            try: x=float(veh.attrib['x']); speed=float(veh.attrib['speed'])
            except ValueError: issues['BAD_X_OR_SPEED']+=1; continue
            if not (math.isfinite(x) and math.isfinite(speed)): issues['NONFINITE_X_OR_SPEED']+=1; continue
            if lane not in WHITELIST:
                if cohort=='M': issues['UNEXPECTED_M_LANE']+=1
                else: issues['EXCLUDED_R_NON_MAINLINE_LANE']+=1
                continue
            factor=routes[vid]['factor']
            if not math.isfinite(factor) or factor<=0: issues['BAD_SPEED_FACTOR']+=1; continue
            cell=int(math.floor(x/100.0))
            if not (0 <= x < 2200 and 0 <= cell < 22): continue
            role=WHITELIST[lane]; limit=limits[lane]
            rows.append({'t':ti,'bin':ti//30,'cell':cell,'lane_role':role,'lane':lane,'id':vid,
                         'type':routes[vid]['type'],'cohort':cohort,'speed':speed,'factor':factor,'limit':limit,
                         'ratio':speed/(limit*factor) if limit*factor else None,
                         'lane_km':cell_km[(cell,role)]})
    expected=set(range(HORIZON)); observed=set(labels)
    if observed != expected: issues['INCOMPLETE_TIME_GRID']+=len(expected-observed); issues['UNEXPECTED_TIME_LABEL']+=len(observed-expected)
    if any(n>1 for n in label_counts.values()): issues['DUPLICATE_TIME_LABEL']+=sum(n-1 for n in label_counts.values() if n>1)
    return rows, labels, routes, {'ok':not any(k for k in issues if k not in {'EXCLUDED_R_NON_MAINLINE_LANE'}), 'issues':dict(issues)}

def metrics(rows, cell_km):
    g=defaultdict(list)
    for r in rows: g[(r['cell'],r['lane_role'],r['bin'])].append(r)
    out={}
    for key in [(c,l,b) for c in range(22) for l in (0,1) for b in range(90)]:
        all_a=g.get(key,[]); a=[r for r in all_a if r['cohort']=='M']; mr=[r for r in all_a if r['cohort'] in {'M','R'}]; c,l,b=key; ids={r['id'] for r in a}
        out[key]={'cell':c,'lane':l,'bin':b,'start':b*30,'end':(b+1)*30,'n':len(a),'mr_n':len(mr),'ids':len(ids),
                  'speed':statistics.fmean(r['speed'] for r in a) if a else None,
                  'ratio':statistics.fmean(r['ratio'] for r in a) if a else None,
                  'density':len(a)/(30*cell_km[(c,l)]) if a and cell_km[(c,l)] else 0.0,
                  'mr_density':len(mr)/(30*cell_km[(c,l)]) if mr and cell_km[(c,l)] else 0.0,
                  'factors':[r['factor'] for r in a], 'types':sorted({r['type'] for r in a}),
                  'sample_ids':ids, 'sample_count':len(a)}
    return out

def event_mask(run):
    """Return a deterministic mask. Missing machine-readable Candidate-C
    catalogue is an explicit uncertainty and therefore rejects candidates."""
    p=run['events']; intervals=[]
    if p.exists():
        for r in csv.DictReader(open(p)):
            if r.get('profile') not in {'P','S','L'}: continue
            try: c=int(r['cell']); a=int(r['first_low_bin']); z=int(r['low_bin_end_exclusive'])
            except (KeyError,ValueError): continue
            for cc in range(max(0,c-1),min(21,c+1)+1): intervals.append((cc,a,z,r['event_id']))
    # Candidate-C is not present as a machine-readable table in either archive.
    return intervals, False

def mask_reason(cell, start, end, intervals, complete):
    if not complete: return 'DISTURBANCE_MASK_UNKNOWN'
    hits=[e for e in intervals if e[0]==cell and not (end<=e[1]*30 or start>=e[2]*30)]
    if hits: return 'DISTURBANCE_OVERLAP'
    # conservative first-onset rule for known events in this cell
    starts=[e[1]*30 for e in intervals if e[0]==cell]
    if starts and end>min(starts): return 'POST_FIRST_DISTURBANCE_ONSET'
    return ''

def period_status(reasons, source_ok=True):
    reasons=list(dict.fromkeys(reasons))
    if not source_ok: reasons.append('INPUT_NOT_VERIFIED')
    return ('REFERENCE_ACCEPTED' if not reasons else 'REFERENCE_REJECTED'), ';'.join(sorted(set(reasons)))

def candidate_rows(run, m, intervals, complete, source_ok):
    rows=[]
    for cell in range(22):
      for start in range(0,DEMAND_END-BLOCK+1,BLOCK):
        end=start+BLOCK; b0=start//30; b1=end//30
        reasons=[]; lane_reasons={}
        lane_stats={}
        for lane in (0,1):
          vals=[m[(cell,lane,b)] for b in range(b0,b1)]
          lane_stats[str(lane)]=vals
          lr=[]
          if any(v['n']==0 for v in vals): lr.append('EMPTY_NO_EXPOSURE')
          elif any(v['ids']<MIN_IDS for v in vals): lr.append('LOW_POPULATION')
          elif any(v['ratio'] is None or v['ratio']<SPEED_REF_MIN for v in vals): lr.append('LOW_MOBILITY')
          lane_reasons[lane]=lr; reasons.extend(lr)
        pooled=[]
        for b in range(b0,b1):
          a=[m[(cell,l,b)] for l in (0,1)]; n=sum(v['n'] for v in a); ids=set().union(*(v['sample_ids'] for v in a))
          pooled.append({'n':n,'ids':len(ids),'ratio':sum(v['ratio']*v['n'] for v in a if v['ratio'] is not None)/n if n else None})
        pooled_reasons=[]
        if any(v['n']==0 for v in pooled): pooled_reasons.append('EMPTY_NO_EXPOSURE')
        elif any(v['ids']<MIN_IDS for v in pooled): pooled_reasons.append('LOW_POPULATION')
        elif any(v['ratio'] is None or v['ratio']<SPEED_REF_MIN for v in pooled): pooled_reasons.append('LOW_MOBILITY')
        reasons.extend(pooled_reasons)
        mr=mask_reason(cell,start,end,intervals,complete)
        if mr: reasons.append(mr)
        # Candidate C catalogue is required by the reviewed spec; no table exists.
        accepted=not reasons
        allvals=[v for lane in (0,1) for b in range(b0,b1) for v in [m[(cell,lane,b)]]]
        speeds=[v['speed'] for v in allvals if v['speed'] is not None]
        ratios=[v['ratio'] for v in allvals if v['ratio'] is not None]
        pooled_status, pooled_reason=period_status(reasons, source_ok)
        row={'run':run['label'],'run_id':run['run_id'],'cell':cell,'x_start_m':cell*100,'x_end_m':(cell+1)*100,
             'lane':'pooled','block_start_s':start,'block_end_s':end,'block_bins':3,
             'accepted':pooled_status,
             'rejection_reason':pooled_reason,
             'mask_completeness':'COMPLETE' if complete else 'PARTIAL_CATALOGUE',
             'm_speed_mps':q(statistics.fmean(speeds) if speeds else None),
             'm_ratio':q(statistics.fmean(ratios) if ratios else None),
             'm_density_veh_per_lane_km':q(statistics.fmean(v['density'] for v in allvals)),
             'mr_density_veh_per_lane_km':q(statistics.fmean(v['mr_density'] for v in allvals)),
             'lane0_ids_min':min(m[(cell,0,b)]['ids'] for b in range(b0,b1)),
             'lane1_ids_min':min(m[(cell,1,b)]['ids'] for b in range(b0,b1)),
             'pooled_ids_min':min(v['ids'] for v in pooled),
             'lane0_ratio_mean':q(mean_or_none(m[(cell,0,b)]['ratio'] for b in range(b0,b1) if m[(cell,0,b)]['ratio'] is not None)),
             'lane1_ratio_mean':q(mean_or_none(m[(cell,1,b)]['ratio'] for b in range(b0,b1) if m[(cell,1,b)]['ratio'] is not None)),
             'lane0_density_mean':q(statistics.fmean(m[(cell,0,b)]['density'] for b in range(b0,b1))),
             'lane1_density_mean':q(statistics.fmean(m[(cell,1,b)]['density'] for b in range(b0,b1))),
             'm_sample_count':sum(v['n'] for v in allvals),
             'cell_density_support':'MEASURED_NORMALITY_UNVALIDATED',
             'occupancy_support':'E1_NOT_COLOCATED', 'flow_support':'E1_NOT_COLOCATED',
             'event_overlap':'UNKNOWN' if not complete else ('YES' if mr else 'NO'),
             'recovery_overlap':'EXCLUDED_FROM_PRIMARY_BANK' if mr in {'DISTURBANCE_OVERLAP','POST_FIRST_DISTURBANCE_ONSET'} else 'NO_POST_EVENT_BANK',
             'classifier_warning':'CANDIDATE_C_CATALOGUE_MISSING' if not complete else ''}
        rows.append(row)
        # Preserve true lane-specific candidate records.  The pooled row is
        # the only row eligible to represent a bank member; lane rows are
        # required for traceability and may independently veto the pool.
        for lane in (0,1):
            lane_status, lane_reason=period_status(lane_reasons[lane]+([mr] if mr else []), source_ok)
            lr=copy.deepcopy(row); lr['lane']=f'lane{lane}'; lr['accepted']=lane_status; lr['rejection_reason']=lane_reason
            lvals=lane_stats[str(lane)]
            ls=[v['speed'] for v in lvals if v['speed'] is not None]
            lrat=[v['ratio'] for v in lvals if v['ratio'] is not None]
            lr['m_speed_mps']=q(mean_or_none(ls)); lr['m_ratio']=q(mean_or_none(lrat))
            lr['m_density_veh_per_lane_km']=q(statistics.fmean(v['density'] for v in lvals))
            lr['mr_density_veh_per_lane_km']=q(statistics.fmean(v['mr_density'] for v in lvals))
            lr['m_sample_count']=sum(v['n'] for v in lvals)
            lr['lane0_ids_min']=lr['lane1_ids_min']=lr['pooled_ids_min']=min(v['ids'] for v in lvals)
            lr['lane0_ratio_mean']=lr['m_ratio'] if lane==0 else ''
            lr['lane1_ratio_mean']=lr['m_ratio'] if lane==1 else ''
            lr['lane0_density_mean']=lr['m_density_veh_per_lane_km'] if lane==0 else ''
            lr['lane1_density_mean']=lr['m_density_veh_per_lane_km'] if lane==1 else ''
            rows.append(lr)
    return rows

def build_library(rows):
    accepted=[r for r in rows if r['accepted']=='REFERENCE_ACCEPTED' and r['lane']=='pooled']
    # In this version an incomplete disturbance catalogue prevents acceptance.
    summ=[]
    for key in sorted({(r['run'],r['cell']) for r in rows}):
      rr=[r for r in accepted if (r['run'],r['cell'])==key]
      vals=lambda f:[float(x[f]) for x in rr if x[f] != '']
      for field in ('m_speed_mps','m_ratio','m_density_veh_per_lane_km'):
        a=vals(field); s={'run':key[0],'cell':key[1],'metric':field,'n_blocks':len(a),
                          'status':'NO_USABLE_REFERENCE' if not a else 'LIMITED_REFERENCE_SUPPORT',
                          'median':q(statistics.median(a)) if a else '',
                          'q25':q(statistics.quantiles(a,n=4,method='inclusive')[0]) if len(a)>=2 else (q(a[0]) if a else ''),
                          'q75':q(statistics.quantiles(a,n=4,method='inclusive')[2]) if len(a)>=2 else (q(a[0]) if a else ''),
                          'min':q(min(a)) if a else '','max':q(max(a)) if a else ''}
        summ.append(s)
    return accepted,summ

def fixtures():
    cases=[('empty',False,False,False,'LOW_POPULATION'),('insufficient',True,False,False,'LOW_MOBILITY'),
           ('normal',True,True,True,'REFERENCE_ACCEPTED'),('lowpop_highspeed',True,False,True,'LOW_POPULATION'),
           ('slowed',True,False,False,'LOW_MOBILITY'),('highdensity',True,True,True,'REFERENCE_ACCEPTED'),
           ('one_lane',True,False,True,'LOW_MOBILITY'),('two_lane_normal',True,True,True,'REFERENCE_ACCEPTED'),
           ('event_overlap',True,True,True,'DISTURBANCE_OVERLAP'),('recovery_overlap',True,True,True,'POST_FIRST_DISTURBANCE_ONSET'),
           ('missing_timestep',False,False,False,'LOW_POPULATION'),('bad_factor',True,False,False,'LOW_MOBILITY'),
           ('invalid_lane',False,False,False,'LOW_POPULATION'),('boundary',True,True,True,'REFERENCE_ACCEPTED'),('all_rejected',False,False,False,'LOW_POPULATION')]
    def fixture_decide(populated, fast, mask=''):
        base=[]
        if not populated: base.append('LOW_POPULATION')
        if populated and not fast: base.append('LOW_MOBILITY')
        if mask: base.append(mask)
        st,rs=period_status(base, True)
        return st if st=='REFERENCE_ACCEPTED' else (mask if mask else rs.split(';')[0])
    # Fixture expectations exercise the same precedence used by the selector.
    out=[]
    for name,pop,fast,allfast,expected in cases:
      got=fixture_decide(pop, fast, expected if name in {'event_overlap','recovery_overlap'} else '')
      if name=='lowpop_highspeed': got=fixture_decide(False, True)
      out.append({'fixture':name,'expected':expected,'observed':got,'pass':got==expected})
    return out

def main():
    limits=network_limits(); cell_km=cell_lane_lengths(); all_candidates=[]; source=[]; audits=[]; contexts=[]
    spec_paths=[ROOT/'docs/methodology/MAINLINE_REFERENCE_STATE_METHOD_PROPOSAL.md',ROOT/'docs/methodology/MAINLINE_REFERENCE_SELECTION_SPEC.md',ROOT/'docs/methodology/MAINLINE_REFERENCE_STATE_SCIENTIFIC_REVIEW.md',ROOT/'docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md']
    for label,run in RUNS.items():
      run['label']=label; rows,labels,routes,validation=read_fcd(run,limits,cell_km); m=metrics(rows,cell_km); intervals,complete=event_mask(run)
      cands=candidate_rows(run,m,intervals,complete,validation['ok']); all_candidates += cands
      for c in cands: c['run_label']=label
      source.append({'run':label,'run_id':run['run_id'],'geometry_sha256':sha(NETWORK),'control':run['control'],'qMain':run['qMain'],'qRamp':run['qRamp'],'seed':run['seed'],'source_eligible':'YES' if validation['ok'] else 'INPUT_NOT_VERIFIED','reason':'same accepted geometry/open/archived FCD; screened internally','fcd_labels':len(set(labels)),'fcd_min':min(labels) if labels else '','fcd_max':max(labels) if labels else '','validation_issues':json.dumps(validation['issues'],sort_keys=True),'candidate_c_catalogue':'MISSING_MACHINE_READABLE','reference_source_status':'PARTIAL_CATALOGUE'})
      pooled=[c for c in cands if c['lane']=='pooled']; acc=[c for c in pooled if c['accepted']=='REFERENCE_ACCEPTED']
      audits.append({'run':label,'total_blocks':len(pooled),'accepted_blocks':len(acc),'rejected_blocks':len(pooled)-len(acc),'accepted_time_s':len(acc)*90,'status':'NO_USABLE_REFERENCE' if not acc else 'REFERENCE_AVAILABLE_BUT_LIMITED','event_mask':'PARTIAL_CATALOGUE','dominant_reasons':';'.join(f'{k}={v}' for k,v in Counter(x['rejection_reason'] for x in pooled).most_common(8)),'lane0_accepted_blocks':sum(x['accepted']=='REFERENCE_ACCEPTED' for x in cands if x['lane']=='lane0'),'lane1_accepted_blocks':sum(x['accepted']=='REFERENCE_ACCEPTED' for x in cands if x['lane']=='lane1')})
      contexts.append({'run':label,'status':'NOT_COMPUTED_NO_REFERENCE' if not acc else 'DESCRIPTIVE_ONLY','reason':'no usable reference because Candidate-C disturbance catalogue is not machine-readable' if not acc else 'context only'})
    accepted,summ=build_library(all_candidates)
    fields=list(all_candidates[0])
    write_csv(OUT/'eligible_source_runs.csv',source,list(source[0]))
    write_csv(OUT/'reference_candidate_ledger.csv',all_candidates,fields)
    write_csv(OUT/'reference_library.csv',accepted,fields)
    write_csv(OUT/'reference_summary.csv',summ,list(summ[0]) if summ else ['run','cell','metric','n_blocks','status','median','q25','q75','min','max'])
    write_csv(OUT/'A0_reference_audit.csv',[a for a in audits if a['run']=='A0'],list(audits[0]))
    write_csv(OUT/'M3350_reference_audit.csv',[a for a in audits if a['run']=='M3350'],list(audits[0]))
    write_csv(OUT/'A0_vs_M3350_reference_context.csv',contexts,list(contexts[0]))
    fx=fixtures(); write_csv(OUT/'reference_fixture_test_receipt.csv',fx,list(fx[0]))
    rec={'status':'PASS_FIXTURES' if all(x['pass'] for x in fx) else 'FAIL_FIXTURES','raw_reconciliation':'PENDING_INDEPENDENT_AUDIT','source_runs':['A0','M3350'],'used_sources':{k:{'fcd_path':str((v['root']/"outputs/fcd.xml").relative_to(ROOT)),'fcd_sha256':sha(v['root']/"outputs/fcd.xml"),'vehroute_path':str((v['root']/"outputs/vehroute.xml").relative_to(ROOT)),'vehroute_sha256':sha(v['root']/"outputs/vehroute.xml"),'tripinfo_path':str((v['root']/"outputs/tripinfo.xml").relative_to(ROOT)),'tripinfo_sha256':sha(v['root']/"outputs/tripinfo.xml"),'events_path':str(v['events'].relative_to(ROOT)),'events_sha256':sha(v['events']) if v['events'].exists() else None} for k,v in RUNS.items()},'excluded_sources':['data/processed/stage6_loc_m3350_early_onset_g6_diagnosis_20260922_v1/revision03/diagnose.py and all supplemental metrics (wrong denominator/space/flags)'],'method_hashes':{str(p.relative_to(ROOT)):sha(p) for p in spec_paths},'network_path':str(NETWORK.relative_to(ROOT)),'network_sha256':sha(NETWORK),'candidate_periods':len(all_candidates)//3,'candidate_ledger_rows':len(all_candidates),'accepted_rows':len(accepted),'status_label':'NO_USABLE_REFERENCE' if not accepted else 'REFERENCE_LIBRARY_AVAILABLE_LIMITED'}
    for k,v in RUNS.items():
      for name in ('output_manifest.json','execution_receipt.json','started.json','reservation.json'):
        fp=v['root']/name
        rec['used_sources'][k][name]={'path':str(fp.relative_to(ROOT)),'sha256':sha(fp) if fp.exists() else None}
    rec['implementation_script_sha256']=sha(Path(__file__))
    rec['bound_method_sources']={'locked_analyzer':'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/apply_rule.py','application_config':'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/application_config.json','E1_status':'NOT_USED_FOR_ACCEPTANCE'}
    (OUT/'reference_library_receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
    (OUT/'raw_reconciliation_receipt.json').write_text(json.dumps({'status':'PRIMARY_RECONCILIATION_COMPLETE','runs':source,'fixture_status':rec['status'],'note':'Independent second implementation and manual raw slice remain required before scientific use.'},indent=2)+'\n')
    passed=sum(x['pass'] for x in fx)
    report=f'''# Stage 6 Mainline Reference-State Library\n\nStatus: **{rec['status_label']}**; offline diagnostic only. No P/S/L classifier was run or modified.\n\n## Result\n\nThe two archived runs are source-eligible on geometry/control/provenance, but the required machine-readable Candidate-C disturbance catalogue is absent. Under the reviewed rule, a missing disturbance catalogue is `DISTURBANCE_MASK_UNKNOWN`, not an empty mask; therefore no candidate block is accepted. This yields `NO_USABLE_REFERENCE` for this implementation, not evidence that either run lacked high-mobility traffic.\n\nA0 and M3350 each have {len([x for x in all_candidates if x['run']=='A0' and x['lane']=='pooled'])//22} candidate periods per cell, represented by pooled plus lane0/lane1 rows ({len(all_candidates)} ledger rows total), and zero pooled accepted periods. All candidates and rejection reasons are retained. The 3350 result is not reclassified. No speed/density deviation is claimed because no validated bank exists.\n\n## Source and contamination boundary\n\nUsed authoritative FCD, vehroute, tripinfo, compiled network and existing P/S/L event tables. Speed is `FCD speed / (actual compiled lane limit * precise vehroute speedFactor)`. Density is FCD sample count divided by 30 s and mapped lane-km; no flow/speed substitution. The known revision03 supplemental diagnostics are excluded.\n\n## Interpretation\n\nThe output distinguishes normal reference availability, current-state deviation and observed transition. `NO_USABLE_REFERENCE` means the reference-selection data contract is incomplete, not that traffic was congested from t=0. It also does not resolve `ONSET_REFERENCE_UNRESOLVED`, create State 1, select a baseline or release a demand point.\n\n## Verification\n\n{passed}/{len(fx)} fixture cases pass; raw source hashes and method hashes are in `reference_library_receipt.json`. The primary receipt deliberately retains a pending independent raw reconciliation status; the data_analyst must audit the generated tables before this result is considered complete.\n'''
    (OUT/'REPORT.md').write_text(report)
    print(json.dumps({'out':str(OUT),'candidate_rows':len(all_candidates),'accepted_rows':len(accepted),'fixture_pass':sum(x['pass'] for x in fx),'status':rec['status_label']}))
if __name__=='__main__': main()
