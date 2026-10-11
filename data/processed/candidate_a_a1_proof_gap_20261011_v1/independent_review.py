"""Public static integrity review; no SUMO, raw, network or production imports."""
import csv, hashlib, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def review_old():
    binding = json.loads((OUT / 'PRE_REVIEW_BASELINE_BINDINGS.json').read_text())
    mismatches = [p for p,h in binding['protected'].items() if sha(ROOT / p) != h]
    assert not mismatches, mismatches
    snap = json.loads((ROOT / 'artifacts/candidate_a_qualification_20261008_v1/pr_review/CA_FIXED_R300_S17_A07/outputs/failure_snapshot.json').read_text())
    s = snap['snapshot']; rows=s['vehicle_states']; witnesses=s['red_transition']['witnesses']
    assert len(rows)==len(witnesses)==42
    assert len({r['vehicle_id'] for r in rows})==42
    byid={r['vehicle_id']:r for r in witnesses}; mapped=[]
    for r in rows:
        v=r['speed_m_s']; b=r['normal_decel_m_s2']; gap=204.49-r['position_m']
        required=0 if v==0 else 1.1+v+v*v/(2*b)
        margin=gap-required; safe=gap+1e-9>=required; w=byid[r['vehicle_id']]
        for k,x in [('gap_m',gap),('required_normal_red_m',required),('margin_m',margin)]:
            assert math.isclose(x,w[k],rel_tol=1e-12,abs_tol=1e-12),(r['vehicle_id'],k)
        assert safe==w['safe']
        mapped.append({'id':r['vehicle_id'],'population':r['population'],'gap_m':gap,'required_m':required,'margin_m':margin,'old_guard_safe':safe})
    assert sum(r['population']=='storage' for r in rows)==27
    assert sum(r['population']=='ingress' for r in rows)==15
    assert [r['id'] for r in mapped if not r['old_guard_safe']]==['R_flow.1']
    assert snap['last_completed_step_s']==snap['last_accounted_s']==snap['decision_time_s']==1206
    assert s['cycle']['completed'] is False
    with (ROOT / 'results/tables/candidate_a_qualification_20261008_v1/R300_A07_SERVICE_WINDOWS_V3.csv').open() as f: windows=list(csv.DictReader(f))
    assert len(windows)==6 and [int(w['observed_steps']) for w in windows]==[6,0,0,0,0,0]
    fields=['C_observed','C_applied_observed','E_observed','N_observed','command_latency','quantization','physical_shortfall']
    assert [float(windows[0][k]) for k in fields]==[.5,.5,0,1,0,.5,-1]
    assert all(w[k]=='' for w in windows[1:] for k in fields)
    assert all(w['tracking_error']=='' for w in windows)
    with (ROOT / 'results/tables/candidate_a_qualification_20261008_v1/R300_A07_PHASE_LEDGER_THIN_V3.csv').open() as f: thin=list(csv.DictReader(f))
    assert len(thin)==1206
    return {'status':'PASS','protected_checked':len(binding['protected']),'protected_mismatches':mismatches,'witnesses':mapped,'counts':{'storage':27,'ingress':15,'native_complete_branch_observed':0,'refused_red_motion_observed':0,'completed_cycles':0,'service_windows':6,'observed_seconds':[6,0,0,0,0,0],'thin_derived_rows':1206},'limits':'Public derived evidence only; no ignored raw reconstruction; no future coverage or counterfactual native red outcome.'}

def review_ledger():
    eng=ROOT/'artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering'
    ledger=json.loads((eng/'SOURCE_TO_STATE_LEDGER.json').read_text())
    matrix=json.loads((eng/'COVERAGE_AND_JOINT_MATRIX.json').read_text())
    excerpts=json.loads((eng/'SOURCE_EXCERPTS.json').read_text())
    ids={x['id'] for x in excerpts['excerpts']}
    fields=ledger['fields']; byid={x['id']:x for x in fields}
    assert len(fields)==len(byid)==ledger['count']==69
    required=['variable','proof_ids','observability_level','status','api_or_method','source_excerpt_ids','measurement_time','saved_A07_evidence','bound_or_derivation','limit']
    assert all(all(k in f and f[k] for k in required) for f in fields)
    assert all(set(f['source_excerpt_ids'])<=ids for f in fields)
    assert all(f['observability_level'] in 'abcde' for f in fields)
    proofs=matrix['proof_obligations']
    assert {p['id'] for p in proofs}=={f'P{i}' for i in range(11)} and len(proofs)==11
    for p in proofs:
        assert set(p['matching_state_fields'])=={f['id'] for f in fields if p['id'] in f['proof_ids']},p['id']
    for e in excerpts['excerpts']:
        assert hashlib.sha256(e['text'].encode()).hexdigest()==e['sha256']
        assert len(e['text'].splitlines())==e['line_end']-e['line_start']+1
        assert ledger['source_commit'] in e['url']
        assert e['url'].endswith(f"#L{e['line_start']}-L{e['line_end']}")
    assert ledger['verdict']==matrix['verdict']=='STOP_A1_UNDER_CURRENT_INTERFACE'
    assert ledger['all_stronger_conservative_proofs_impossible']=='NOT_PROVED'
    assert ledger['no_ELIGIBLE_state_generated'] is True
    assert byid['S32']['observability_level']=='b'
    assert 'getLastActionTime' in next(e['text'] for e in excerpts['excerpts'] if e['id']=='V_TYPE_PROPERTIES')
    assert byid['S59']['observability_level']=='e'
    assert len(matrix['coverage'])==12
    for demo in matrix['interval_insufficiency_demonstrations']:
        i=demo['input']
        if 'v_m_s' in i:
            assert demo['ordinary_lower_m_s']==max(0,i['v_m_s']-i['normal_b_m_s2']*i['dt_s'])
            assert demo['emergency_lower_m_s']==max(0,i['v_m_s']-i['emergency_b_m_s2']*i['dt_s'])
        else:
            assert math.isclose(demo['conditional_upper_displacement_m'],(i['front_v_m_s']+i['a_m_s2']*i['dt_s'])*i['dt_s'])
            assert demo['conditional_upper_displacement_m']>i['gap_m']
    baseline=json.loads((OUT/'PRE_REVIEW_BASELINE_BINDINGS.json').read_text())
    preserved=[p for p in baseline['files'] if not p.startswith('docs/PROJECT_STATE') and not p.startswith('docs/WORKLOG')]
    assert all(sha(ROOT/p)==baseline['files'][p] for p in preserved)
    return {'status':'PASS','fields':69,'proof_obligations':11,'coverage_rows':12,'physical_excerpt_schema_hashes':44,'analytical_interval_recomputations':2,'old_baseline_preserved_files':len(preserved),'verdict':'STOP_A1_UNDER_CURRENT_INTERFACE','verdict_scope':'Engineering stop recommendation for this current-interface bounded proof attempt; not proven impossibility of every stronger sufficient bound or all A1 designs.','new_synthetic_cases':0,'existing_43_regressions':'SKIP_UNCHANGED_UPSTREAM_IMPLEMENTATION_BOUND_BY_SHA','native_runtime_queries':'NOT_RUN','delivered_clean_checkout':'PENDING_PARENT_GATE'}

if __name__=='__main__':
    print(json.dumps({'old_evidence':review_old(),'ledger':review_ledger()},indent=2))
