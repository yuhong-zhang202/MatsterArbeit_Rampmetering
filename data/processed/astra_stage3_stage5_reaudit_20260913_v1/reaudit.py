"""Read-only exploratory re-audit; exclusive writes into this new audit directory."""
from pathlib import Path
import csv, json, hashlib, math, collections, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
S3 = ROOT / 'data/processed/stage3_baseline_diagnostic_20260912_v2'
S4 = ROOT / 'data/processed/stage4_qmain_sequential_20260912_v1'
S5 = ROOT / 'data/processed/exploratory_validation_closeout_20260913_v1'
REV = S3 / 'analysis_review/revision_06'
AGG = S3 / 'aggregate/revision_03'
TAB = ROOT / 'results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03'
hashes = {}
def sha(p):
    p = Path(p); h = hashlib.sha256(p.read_bytes()).hexdigest()
    hashes[str(p.relative_to(ROOT))] = h
    return h
def js(p):
    sha(p); return json.loads(Path(p).read_text())
def rows(p):
    sha(p)
    with Path(p).open(newline='') as f: return list(csv.DictReader(f))
def write(name, value):
    with (OUT/name).open('x') as f: json.dump(value, f, indent=2, ensure_ascii=False); f.write('\n')
def writecsv(name, records):
    with (OUT/name).open('x', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def close(a,b): return math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-8)
def sign(v): return 'positive' if v>1e-12 else 'negative' if v< -1e-12 else 'zero'
assert sign(0)=='zero' and sign(-2)=='negative' and close(3600*3/60,180)

contract=js(S3/'measurement_contract.json'); ledger=js(S3/'execution_ledger.json')
sources=js(S3/'source_registry.json'); raw_checks=[]; expected_bins={}; raw_hashes=0
for run in sources['runs']:
    rid=run['run_id']; files={f['source_suffix']:ROOT/f['archive_path'] for f in run['files']}
    for f in run['files']:
        assert sha(ROOT/f['archive_path'])==f['sha256']; raw_hashes+=1
    src=next(r for r in ledger['source_runs'] if r['run_id']==rid)
    assert sha(ROOT/src['source_map_path'])==src['source_map_sha256']
    trips={n.get('id') for _,n in ET.iterparse(files['outputs/tripinfo.xml'],events=('end',)) if n.tag=='tripinfo'}
    counts=collections.Counter(); frames=[]; first={}; previous={}; co=[]; regionfirst={}
    for _,n in ET.iterparse(files['outputs/fcd.xml'],events=('end',)):
        if n.tag!='timestep': continue
        t=float(n.get('time')); frames.append(t); ids=set(); stopped=set()
        for v in n:
            counts['vehicle_samples']+=1; vid=v.get('id'); lane=v.get('lane'); raw=v.get('speed')
            counts['duplicate_id_frame']+=int(vid in ids); ids.add(vid)
            counts['unknown_id']+=int(vid not in trips); counts['unknown_lane']+=int(lane not in contract['lanes'])
            if raw is None: counts['missing_speed']+=1; continue
            speed=float(raw); counts['nonfinite_speed']+=int(not math.isfinite(speed));counts['negative_speed']+=int(speed<0)
            region=contract['lanes'][lane]['region']; cls=vid.split('_')[0]
            if speed<=float(contract['stop_definition']['speed_threshold_mps']):
                if cls=='R': regionfirst.setdefault(region,t)
                if region=='shared_approach': stopped.add(cls)
            if cls=='R' and contract['lanes'][lane].get('first_downstream_eligible') and vid not in first:
                first[vid]=(t,previous.get(vid)); counts['unresolved_first_R']+=int(previous.get(vid)!=t-1)
            previous[vid]=t
        if {'R','U'}<=stopped: co.append(t)
        n.clear()
    counts['frames']=len(frames); counts['duplicate_frames']=len(frames)-len(set(frames))
    counts['missing_frames']=len(set(range(2700))-set(frames));counts['extra_frames']=len(set(frames)-set(range(2700)))
    tls=[]
    for _,n in ET.iterparse(files['outputs/tls_states.xml'],events=('end',)):
        if n.tag=='tlsState': tls.append(float(n.get('time')))
        n.clear()
    counts['tls_records']=len(tls);counts['tls_missing_labels']=len(set(range(2700))-set(tls));counts['tls_extra_labels']=len(set(tls)-set(range(2700)));counts['tls_duplicate_labels']=len(tls)-len(set(tls))
    internal=[]
    for detector in contract['e1_detectors']:
        intervals=[]
        for _,n in ET.iterparse(files[detector['output_suffix']],events=('end',)):
            if n.tag!='interval':continue
            b=float(n.get('begin'));e=float(n.get('end'));c=int(n.get('nVehContrib'));v=float(n.get('speed'))
            counts['e1_rows']+=1;counts['e1_negative_contrib']+=int(c<0);counts['e1_positive_contrib_invalid_speed']+=int(c>0 and (v<0 or not math.isfinite(v)))
            intervals.append((b,e));
            if detector['group']=='M-only_internal_merge_entry':internal.append((b,e,c,v))
            n.clear()
        assert intervals==[(float(b),float(b+30)) for b in range(0,2700,30)]
    for window,begin in [('A',0),('B',300)]:
        for aggregation in [30,60,120]:
            for b in range(begin,1500,aggregation):
                e=min(b+aggregation,1500); subset=[r for r in internal if r[0]>=b and r[1]<=e]; c=sum(r[2] for r in subset)
                assert len(subset)==(e-b)//30*2
                v=sum(r[2]*r[3] for r in subset if r[2]>0)/c if c else None
                expected_bins[(rid,window,aggregation,float(b),float(e))]=(3600*c/(e-b),v,c)
    counts['first_R_total']=len(first);counts['first_R_before_1500']=sum(t<1500 for t,_ in first.values());counts['shared_R_U_labels']=len(co)
    order=['ramp_accel','ramp_mid_internal','ramp_storage','ramp_diverge_internal','shared_approach']
    raw_checks.append({'run_id':rid, 'counts':dict(counts),'first_R_region_labels':{r:regionfirst.get(r) for r in order},'ordered':all(regionfirst[a]<=regionfirst[b] for a,b in zip(order,order[1:]))})

times=rows(AGG/'aggregation_timeseries.csv'); observed={}
for r in times:
    k=(r['run_id'],r['window'],int(float(r['aggregation'])),float(r['bin_begin']),float(r['bin_end']))
    assert k not in observed; observed[k]=r
assert set(observed)==set(expected_bins)
for k,(q,v,n) in expected_bins.items():
    r=observed[k];assert close(r['q'],q) and close(r['v'],v) and int(r['contribution'])==n
registry=rows(REV/'aggregation_timeseries_registry.csv'); shapes=rows(REV/'aggregation_shape_summary.csv')
assert len(registry)==len(shapes)==48
for r in registry:
    group=[(k,v) for k,v in expected_bins.items() if k[:3]==(r['run_id'],r['window'],int(float(r['aggregation_s'])))]
    assert len(group)==int(r['bin_count'])
for r in shapes:
    group=[(k,v) for k,v in expected_bins.items() if k[:3]==(r['run_id'],r['window'],int(float(r['aggregation_s'])))]
    for index,metric in enumerate(['q','v']):
        for kind,fn in [('min',min),('max',max)]:
            extreme=fn(v[index] for k,v in group);assert close(r[f'{metric}_{kind}'],extreme)
            tied=[k for k,v in group if math.isclose(v[index],extreme,rel_tol=1e-12,abs_tol=1e-12)]
            assert close(r[f'{metric}_{kind}_support_s'],sum(k[4]-k[3] for k in tied))
            assert r[f'{metric}_{kind}_time_ranges']=='|'.join(f'[{k[3]},{k[4]})' for k in tied)
sens=rows(AGG/'sensitivity.csv');assert len(sens)==96
for r in sens:
    group=[(k,v) for k,v in expected_bins.items() if k[:3]==(r['run_id'],r['window'],int(float(r['aggregation_s'])))]
    n=sum(v[2] for k,v in group); seconds=sum(k[4]-k[3] for k,v in group)
    expected=3600*n/seconds if r['metric']=='q' else sum(v[1]*v[2] for k,v in group)/n
    assert close(expected,r['value'])
summary=rows(TAB/'condition_evidence_summary.csv'); smap={}
for r in summary:
    k=(r['run_id'],r['window'],r['entity'],r['metric'],r['unit']);assert k not in smap;smap[k]=r
contrasts=rows(REV/'same_seed_contrasts.csv'); paired=collections.defaultdict(dict)
for r in contrasts:
    key=(r['window'],r['entity'],r['metric'],r['unit'])
    base=float(smap[(r['baseline_run'],)+key]['value']);treat=float(smap[(r['treatment_run'],)+key]['value']);delta=treat-base
    assert close(base,r['baseline_value']) and close(treat,r['treatment_value']) and close(delta,r['delta']) and sign(delta)==r['sign']
    paired[(r['contrast_id'].split('_seed')[0],)+key][int(r['seed'])]=delta
signs=rows(REV/'seed_sign_consistency.csv');assert len(signs)==len([v for v in paired.values() if set(v)=={17,23}])
for r in signs:
    key=tuple(r[k] for k in ['contrast_family','window','entity','metric','unit']);v=paired[key]
    assert sign(v[17])==r['sign_seed17'] and sign(v[23])==r['sign_seed23']
    assert r['status']==('same_sign' if sign(v[17])==sign(v[23]) else 'symbol_inconsistent')
unpaired=[{'key':list(k),'available_seeds':sorted(v)} for k,v in paired.items() if set(v)!={17,23}]

inventory=rows(S5/'artifact_inventory.csv'); gates=rows(S5/'gate_inventory.csv');handover=rows(S5/'method_handover_draft.csv');old=js(S5/'inventory_verification_revision_02.json')
pairs=[]
for r in inventory:
    paths=json.loads(r['actual_paths']); hs=json.loads(r['sha256_by_path']); assert len(paths)==len(hs)
    for p,h in zip(paths,hs):pairs.append({'path':p,'actual':sha(ROOT/p),'expected':h,'matched':sha(ROOT/p)==h})
assert len(inventory)==6 and len(gates)==8 and len(handover)==22
mirrors={}
for n in ['artifact_inventory.csv','gate_inventory.csv','method_handover_draft.csv']:
    mirrors[n]=sha(S5/n)==sha(ROOT/'results/tables/exploratory_validation_closeout_20260913_v1'/n)
ids=sorted({i for r in gates+handover for i in r['evidence_id'].split('|')})
snapshot=js(S4/'final_evidence_ledger_snapshot.json');decision=js(S4/'analysis/final/revision_04/registered_final_decision.json')
canonical=hashlib.sha256(json.dumps(snapshot['execution_ledger'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
assert canonical==snapshot['canonical_execution_ledger_sha256']
assert decision['evidence_provenance']['normative_evidence_ledger_snapshot']['sha256']==sha(S4/'final_evidence_ledger_snapshot.json')
write('audit_results.json',{'classification':'exploratory evidence audit, not formal analysis','raw_file_hashes_passed':raw_hashes,'raw_checks':raw_checks,'independent_checker_result':js(OUT/'independent_all_runs.json'),'aggregation_bins_reconstructed':len(expected_bins),'series_and_shapes_checked':len(shapes),'window_values_reconstructed':len(sens),'contrast_rows_reconciled':len(contrasts),'paired_sign_rows':len(signs),'inconsistent_signs':sum(r['status']=='symbol_inconsistent' for r in signs),'unpaired_contrast_keys':unpaired,'questions':sum(r['entity'].startswith('question:') for r in summary),'inventory_path_hash_pairs':pairs,'unique_inventory_paths':len({p['path'] for p in pairs}),'mirrors':mirrors,'handover_qualifications':dict(collections.Counter(r['qualification'] for r in handover)),'formal_values_selected':sum(r['proposed_formal_value']!='unknown_not_selected' for r in handover),'unresolved_original_evidence_ids':ids,'stage4_snapshot_sha256':sha(S4/'final_evidence_ledger_snapshot.json'),'stage4_canonical_sha256':canonical,'stage4_decision_sha256':sha(S4/'analysis/final/revision_04/registered_final_decision.json'),'stage4_action':decision['action'],'limitations':['Historical checker is reused; its dictionary/set normalization can hide duplicated derived rows. Fresh raw scanner tests duplicates directly.','This task independently reconstructs all Stage3 raw core quantities and all 1264 sensitivity bins, but does not establish causal or formal validity.','Stage4 is checked only as the final snapshot/decision dependency; no Stage4 XML reanalysis here.','Original E-* evidence references have no definitions in the inspected current Stage5 package, related docs or analysis source; EV-* index is a separate namespace.','Original gate G08 text still states T51/T53 required although revision_02 records both complete.']})
sha(Path(__file__));sha(ROOT/'src/analysis/verify_stage3_baseline.py')
write('input_hashes.json',hashes)
print(json.dumps({'raw_runs':len(raw_checks),'raw_hashes':raw_hashes,'bins':len(expected_bins),'sign_inconsistencies':sum(r['status']=='symbol_inconsistent' for r in signs),'unpaired_keys':len(unpaired),'pairs_matched':sum(r['matched'] for r in pairs),'pairs':len(pairs),'ids_unresolved':len(ids)}))
