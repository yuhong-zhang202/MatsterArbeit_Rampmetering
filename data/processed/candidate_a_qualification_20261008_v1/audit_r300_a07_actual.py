"""Independent immutable-raw audit of the stopped R300 A07 attempt.

Uses standard library only; does not import the actor or invoke SUMO.
Writes new artifacts exclusively, or verifies byte-identical existing output.
"""
import csv
import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).parent
TABLE = ROOT / 'results/tables/candidate_a_qualification_20261008_v1'
ART = ROOT / 'artifacts/candidate_a_qualification_20261008_v1'
RAW = ROOT / 'data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07'
OUT = RAW / 'outputs'
STORAGE = 'ramp_storage_0'
INGRESS = ':urban_diverge_1_0'
INTERNAL = ':ramp_mid_0_0'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def csvread(name, required):
    with (OUT / name).open(newline='') as stream:
        reader = csv.DictReader(stream)
        assert len(reader.fieldnames) == len(set(reader.fieldnames)), name
        assert set(required) <= set(reader.fieldnames), (name, required)
        result = list(reader)
        assert all(None not in r and None not in r.values() for r in result), name
        return result


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data.encode(), 'Preserve existing artifact: ' + str(path)
    else:
        with path.open('x') as stream:
            stream.write(data)


def table(name, rows, fields=None):
    s = io.StringIO(newline='')
    writer = csv.DictWriter(s, fieldnames=fields or list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    save(TABLE / name.replace('.csv', '_V3.csv'), s.getvalue())


def close(a, b, tol=1e-8):
    assert abs(float(a)-float(b)) <= tol, (a, b, tol)


def red_required(speed, decel=4.5):
    return 0 if speed == 0 else 1.1 + speed + speed**2/(2*decel)


def service(rows, begin, end):
    selected = [r for r in rows if begin <= int(r['time_begin_s']) < end]
    complete = len(selected) == end-begin
    supplied = complete and all(r['storage_supply'] == 'True' for r in selected)
    # No recorded step is missing evidence, not an observed zero measurement.
    C = sum(float(r['C_delta']) for r in selected) if selected else None
    A = sum(float(r['C_applied_delta']) for r in selected) if selected else None
    E = sum(int(r['E_delta']) for r in selected) if selected else None
    N = sum(int(r['N_delta']) for r in selected) if selected else None
    error = abs(C-N)/C if complete and supplied and C else None
    status = 'NOT_TESTED_INCOMPLETE_WINDOW' if not complete else 'NOT_TESTED_SUPPLY' if not supplied else 'PASS' if error <= .1+1e-12 else 'FAIL'
    return dict(begin_s=begin, end_s=end, observed_steps=len(selected), required_steps=end-begin,
                full_window=complete, sustained_supply_verified=supplied, C_observed=C,
                C_applied_observed=A, E_observed=E, N_observed=N,
                command_latency=C-A if selected else None, quantization=A-E if selected else None,
                physical_shortfall=E-N if selected else None,
                tracking_error=error, status=status)


def known_examples():
    close(red_required(0), 0)
    close(red_required(3), 5.1)
    close(red_required(.05), 1.150277777777778)
    base = dict(storage_supply='True', C_delta=1, C_applied_delta=1, E_delta=1, N_delta=1)
    rows = [dict(base, time_begin_s=i) for i in range(10)]
    assert service(rows, 0, 10)['status'] == 'PASS'
    rows[-1]['N_delta'] = 0
    assert service(rows, 0, 10)['status'] == 'PASS'  # inclusive 10% reference
    rows[-2]['N_delta'] = 0
    assert service(rows, 0, 10)['status'] == 'FAIL'
    assert service(rows[:-1], 0, 10)['tracking_error'] is None
    rows[0]['storage_supply'] = 'False'
    assert service(rows, 0, 10)['status'] == 'NOT_TESTED_SUPPLY'


def main():
    known_examples()
    guardian = read(RAW/'guardian_receipt.json')
    worker = read(OUT/'worker_receipt.json')
    failure = read(OUT/'failure_snapshot.json')
    card = read(OUT/'snapshots/card.json')
    contract = read(OUT/'snapshots/config/candidate_a_qualification_20261008_v1/PHASE_RATE_CONTRACT.json')
    manifest = guardian['files_sha256']
    inventory = {str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file()}
    assert inventory == set(manifest)
    for name, h in manifest.items():
        assert sha(OUT/name) == h, name
    for p, h in card['sources_sha256'].items():
        assert sha(OUT/'snapshots'/p) == h, p
    for p, h in card['protected_baseline_sha256'].items():
        assert sha(ROOT/p) == h, p
    for p, h in card['prepared_input_sha256'].items():
        assert sha(ROOT/p) == h and sha(OUT/'snapshots'/p) == h, p
    release = ART/'RELEASE_FIXED_R300_A07.json'
    assert sha(release) == guardian['release_sha256']
    assert read(release)['card_sha256'] == sha(OUT/'snapshots/card.json') == worker['card_sha256'] == guardian['card_sha256']
    ledger = [json.loads(s) for s in (ART/'engineering/EXECUTION_LEDGER.jsonl').read_text().splitlines() if s.strip()]
    matched = [r for r in ledger if r['run_id'] == worker['run_id']]
    assert matched == [guardian]
    assert worker['status'] == failure['status'] == 'ABORTED_SAFETY_BEFORE_RED'
    assert worker['last_completed_step_s'] == worker['last_accounted_s'] == failure['decision_time_s'] == 1206
    assert worker['accounting_complete'] and failure['accounting_complete']
    assert guardian['worker_exit_code'] == 1
    assert card['fixed_command_veh_h'] == 300 and card['activation_s'] == 1200 and card['seed'] == 17
    assert card['horizon_s'] == 4200 and card['tracking_tolerance'] == .1
    assert card['service_windows'] == contract['service_windows_s'] == [[b,b+300] for b in range(1200,3000,300)]
    startup = read(OUT/'startup_context.json')
    for name, h in startup['schema_sha256'].items():
        assert sha(Path(startup['sumo_home'])/'data/xsd'/name) == h
    cfg = ET.parse(OUT/'snapshots/config/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07/scenario.sumocfg')
    assert cfg.find('./report/xml-validation').get('value') == 'always'
    assert cfg.find('./time/step-length').get('value') == '1'
    netname = next(n for n in manifest if n.endswith('network.net.xml'))
    net = ET.parse(OUT/netname).getroot()
    links = [v.attrib for v in net.findall('connection') if v.get('tl') == 'ramp_mid']
    assert len(links) == 1 and links[0]['via'] == INTERNAL and links[0]['from'] == 'ramp_storage' and links[0]['to'] == 'ramp_accel' and links[0]['linkIndex'] == '0'
    lanes = {v.get('id'):v for v in net.iter('lane')}
    for lane, length in [(STORAGE,204.49),(INGRESS,113.08),(INTERNAL,81.98)]:
        close(lanes[lane].get('length'), length)
    addname = next(n for n in manifest if n.endswith('scenario.add.xml'))
    addition = ET.parse(OUT/addname).getroot()
    programs = {v.get('programID'):v for v in list(net.findall('tlLogic'))+list(addition.findall('tlLogic')) if v.get('id')=='ramp_mid'}
    assert programs['A_OPEN'].find('phase').get('duration')=='60'
    for period in range(8,25):
        phases=programs['CA_C'+str(period)].findall('phase')
        assert [(p.get('state'),int(p.get('duration')),int(p.get('next'))) for p in phases]==[('G',3,1),('y',3,2),('r',period-6,2)]
    steps = csvread('phase_steps.csv', ['time_begin_s','time_end_s','vehicle_states_json','phase_api_requests_json','C_delta','E_delta','N_delta'])
    crossings = csvread('crossings.csv', ['vehicle_id','crossing_time_lower_s','crossing_time_upper_s','motion_signal_state'])
    cycles = csvread('cycles.csv', ['cycle_id','begin_s','end_s','completed','N_G','N_y','N_r'])
    assert len(steps) == 1206 and [int(r['time_begin_s']) for r in steps] == list(range(1206))
    assert [int(r['time_end_s']) for r in steps] == list(range(1,1207))
    with gzip.open(OUT/'fcd.xml.gz') as stream:
        fcdroot = ET.parse(stream).getroot()
    assert fcdroot.tag == 'fcd-export'
    fcd = {}
    for ts in fcdroot:
        t = int(float(ts.get('time')))
        assert t not in fcd
        vehicles = {v.get('id'):v.attrib for v in ts}
        assert len(vehicles) == len(ts)
        assert all({'id','lane','speed','pos'} <= set(v) for v in vehicles.values())
        fcd[t] = vehicles
    assert sorted(fcd) == list(range(1206))
    tlsroot = ET.parse(OUT/'tls_states.xml').getroot()
    tls = {int(float(x.get('time'))):x.attrib for x in tlsroot if x.get('id') == 'ramp_mid'}
    assert len(tls) == len(steps) and sorted(tls) == list(range(1206))
    requests = []; phase_thin = []; reconstructed_crossings = []; decels = []; C=A=0.; E=N=0
    all_ids = set(); state_comparisons = 0; receiver_checks=0
    for r in steps:
        t = int(r['time_begin_s']); qual = t>=1200
        expected = 'G' if t<600 else 'y' if t<603 else 'r' if t<1200 else 'G' if t<1203 else 'y'
        assert r['predicted_motion_state'] == r['state_after'] == tls[t]['state'] == expected
        assert r['program_after'] == tls[t]['programID'] and r['phase_after'] == tls[t]['phase']
        # Validate native pending events from each snapshotted phase program.
        if t>=600:
            period=int(r['program_before'].split('CA_C')[1])
            before_phase=int(r['phase_before']); durations=(3,3,period-6)
            next_phase=(1,2,2)[before_phase]
            predicted=next_phase if float(r['next_switch_before_s'])<=t+1e-7 else before_phase
            assert float(r['next_switch_before_s'])>=t-1e-7
            assert int(r['phase_after'])==predicted
            expected_switch=float(r['next_switch_before_s']) if predicted==before_phase and float(r['next_switch_before_s'])>t else t+durations[predicted]
            close(r['next_switch_after_s'],expected_switch)
        else:
            close(r['next_switch_before_s'],60*((max(t-1,0)//60)+1))
            close(r['next_switch_after_s'],60*((t//60)+1))
        req = json.loads(r['phase_api_requests_json']); requests.extend(req)
        assert all(x['time_s']==t and x['call_completed'] for x in req)
        before = fcd.get(t-1,{})
        after = fcd[t]
        observations = json.loads(r['vehicle_states_json'])
        before_covered = {vid for vid,v in before.items() if v['lane'] in (STORAGE,INGRESS)}
        assert {v['vehicle_id'] for v in observations} == before_covered
        observed_decel=[]
        for v in observations:
            fv=before[v['vehicle_id']]
            close(v['position_m'],float(fv['pos'])-(113.08 if fv['lane']==INGRESS else 0),.0050001)
            close(v['speed_m_s'],fv['speed'],.0050001)
            assert v['tau_s']==v['action_step_s']==1 and v['normal_decel_m_s2']==4.5 and v['accel_m_s2']==2.6
            if v['vehicle_id'] in after:
                decels.append(float(after[v['vehicle_id']]['speed'])-float(fv['speed']))
                observed_decel.append(float(after[v['vehicle_id']]['speed'])-v['speed_m_s'])
            state_comparisons += 1
        close(min(observed_decel,default=0),r['minimum_actual_deceleration_m_s2'],.0050001)
        checked=json.loads(r['red_transition_json'])
        if checked:
            assert len(checked['witnesses'])==len(observations)
            for v,w in zip(observations,checked['witnesses']):
                assert v['vehicle_id']==w['vehicle_id']
                close(w['margin_m'],204.49-v['position_m']-red_required(v['speed_m_s']))
                assert w['safe']
        after_internal={vid for vid,v in after.items() if v['lane']==INTERNAL}
        before_internal={vid for vid,v in before.items() if v['lane']==INTERNAL}
        new=after_internal-before_internal
        assert not (new & all_ids)
        assert all(before[vid]['lane']==STORAGE for vid in new)
        all_ids.update(new)
        assert sorted(new)==json.loads(r['crossing_ids_json']) and len(new)==int(r['N_delta'])
        for vid in sorted(new):
            reconstructed_crossings.append(dict(vehicle_id=vid,crossing_time_lower_s=t,crossing_time_upper_s=t+1,
                fcd_before_label_s=t-1,fcd_entry_label_s=t,motion_signal_state=expected,cycle_id=int(r['cycle_id']) if qual else -1))
        assert (r['storage_supply']=='True') == any(v['population']=='storage' for v in observations)
        recv=json.loads(r['receiver_json'])
        assert (r['receiver_available']=='True') == recv['available']
        if recv['front_id']:
            front=max((v for v in observations if v['population']=='storage'),key=lambda v:v['position_m'])
            assert recv['front_id']==front['vehicle_id']
            if recv.get('leader'):
                leader=recv['leader']; assert leader['vehicle_id'] in before
                assert leader['lane_id']==before[leader['vehicle_id']]['lane']
                assert leader['secure_gap_m']>=0
            receiver_checks+=1
        assert float(r['minimum_actual_deceleration_m_s2'])>=-4.500001
        C+=float(r['C_delta']); A+=float(r['C_applied_delta']); E+=int(r['E_delta']); N+=int(r['N_delta']) if qual else 0
        close(r['C_delta'],300/3600 if qual else 0);close(r['C_applied_delta'],300/3600 if qual else 0)
        assert int(r['E_delta'])==0
        for key,value in [('C_total',C),('C_applied_total',A),('E_total',E),('N_total',N)]:close(r[key],value)
        if qual:
            assert r['cycle_executed']=='True' and int(r['cycle_period_s'])==24 and int(r['cycle_id'])==0
            close(r['pending_command_veh_h'],300);close(r['applied_command_veh_h'],300)
            assert int(r['command_applied_s'])==1200 and int(r['application_delay_s'])==0
        phase_thin.append({k:r[k] for k in ['time_begin_s','time_end_s','segment','cycle_id','program_before','phase_before','state_before','next_switch_before_s','predicted_motion_state','program_after','phase_after','state_after','next_switch_after_s','storage_supply','receiver_available','receiver_reason','C_delta','C_applied_delta','E_delta','N_delta','C_total','E_total','N_total','phase_api_requests_json']})
    assert [(x['time_s'],x['method'],x['value']) for x in requests] == [(0,'setProgram','A_OPEN'),(0,'setPhase',0),(600,'setProgram','CA_C8'),(600,'setPhase',1),(1200,'setProgram','CA_C24'),(1200,'setPhase',2),(1200,'setPhase',0)]
    assert len(crossings)==len(reconstructed_crossings)==1
    for raw, calculated in zip(crossings,reconstructed_crossings):
        for key in ['vehicle_id','motion_signal_state']:assert raw[key]==calculated[key]
        for key in ['crossing_time_lower_s','crossing_time_upper_s','cycle_id']:close(raw[key],calculated[key])
    assert len(cycles)==1 and cycles[0]['completed']=='False' and int(cycles[0]['end_s'])==1224
    assert int(cycles[0]['N_G'])==1 and int(cycles[0]['N_y'])==int(cycles[0]['N_r'])==0
    assert json.loads(cycles[0]['crossing_ids_json'])==['R_flow.0']
    for k,v in [('C',C),('C_applied',A),('E',E),('N',N)]:close(worker['accounting'][k],v)
    close(C,.5);close(A,.5);assert E==0 and N==1
    snapshot=failure['snapshot']; witnesses=[]
    assert snapshot['time_s']==1206 and snapshot['phase_before']==1 and snapshot['state_before']=='y'
    assert snapshot['next_switch']==1206 and snapshot['predicted_motion']=='r' and not snapshot.get('step_advanced',False)
    assert {v['vehicle_id'] for v in snapshot['vehicle_states']}=={vid for vid,v in fcd[1205].items() if v['lane'] in (STORAGE,INGRESS)}
    for v in snapshot['vehicle_states']:
        fv=fcd[1205][v['vehicle_id']]
        close(v['position_m'],float(fv['pos'])-(113.08 if fv['lane']==INGRESS else 0),.0050001)
        close(v['speed_m_s'],fv['speed'],.0050001)
        gap=204.49-v['position_m'];required=red_required(v['speed_m_s'],v['normal_decel_m_s2'])
        # Maximum possible margin using FCD two-decimal rounding intervals.
        fcd_upper_margin=204.49-(float(fv['pos'])-.005-(113.08 if fv['lane']==INGRESS else 0))-red_required(max(0,float(fv['speed'])-.005))
        witnesses.append(dict(time_s=1206,vehicle_id=v['vehicle_id'],population=v['population'],position_m=v['position_m'],speed_m_s=v['speed_m_s'],gap_m=gap,required_m=required,margin_m=gap-required,safe=gap+1e-9>=required,fcd_label_s=1205,fcd_position_m=fv['pos'],fcd_speed_m_s=fv['speed'],fcd_rounding_maximum_margin_m=fcd_upper_margin))
    unsafe=[r for r in witnesses if not r['safe']]
    assert [r['vehicle_id'] for r in unsafe]==snapshot['red_transition']['unsafe_ids']==['R_flow.1']
    assert unsafe[0]['fcd_rounding_maximum_margin_m']<0
    for a,b in zip(witnesses,snapshot['red_transition']['witnesses']):
        assert a['vehicle_id']==b['vehicle_id'];close(a['margin_m'],b['margin_m'])
    summary=ET.parse(OUT/'sumo_summary.xml').getroot().findall('step')
    assert [int(float(x.get('time'))) for x in summary]==list(range(1206))
    assert all(int(x.get('collisions'))==int(x.get('teleports'))==0 for x in summary)
    warnings=(OUT/'sumo_error.log').read_text().splitlines()
    assert len(warnings)==17 and all('only loops backs to itself' in w for w in warnings)
    for name in ['sumo_error.log','sumo_stderr.log','sumo.log']:
        text=(OUT/name).read_text().lower()
        assert not any(w in text for w in ['emergency braking','collision','teleport','emergency stop'])
    assert 'Simulation ended at time: 1206.00.' in (OUT/'sumo.log').read_text()
    assert min(decels)>=-4.51  # at most 0.01m/s rounding difference
    input_name=next(n for n in manifest if n.endswith('demand.rou.xml'))
    demand=ET.parse(OUT/input_name).getroot().findall('vehicle')
    assert len(demand)==4050 and len({v.get('id') for v in demand})==4050
    planned={v.get('id'):v.attrib for v in demand}
    trips=ET.parse(OUT/'tripinfo.xml').getroot().findall('tripinfo')
    routes=ET.parse(OUT/'vehroute.xml').getroot().findall('vehicle')
    assert len({v.get('id') for v in trips})==len(trips) and len({v.get('id') for v in routes})==len(routes)
    departed={v.get('id') for v in trips if float(v.get('depart'))>=0}
    arrived={v.get('id') for v in trips if float(v.get('arrival'))>=0}
    assert departed=={v.get('id') for v in routes}==set().union(*(set(v) for v in fcd.values()))
    assert set(planned)>=departed>=arrived
    endpoint=set(fcd[1205]);assert departed-arrived==endpoint
    assert len(departed)==1467 and len(arrived)==1267 and len(endpoint)==200
    lifecycle=[];counts=[]
    for vid,p in planned.items():
        due=float(p['depart'])<1206
        status='ARRIVED' if vid in arrived else 'IN_NETWORK_UNFINISHED' if vid in departed else 'SOURCE_BACKLOG_DUE' if due else 'FUTURE_SCHEDULE_NOT_DUE'
        lifecycle.append(dict(vehicle_id=vid,group=vid[0],scheduled_depart_s=p['depart'],due_before_actual_endpoint=due,status=status))
    for cls in 'MRUX':
        selected=[r for r in lifecycle if r['group']==cls];ct=Counter(r['status'] for r in selected)
        counts.append(dict(group=cls,planned=len(selected),due=sum(r['due_before_actual_endpoint'] for r in selected),inserted=sum(r['vehicle_id'] in departed for r in selected),arrived=ct['ARRIVED'],in_network_unfinished=ct['IN_NETWORK_UNFINISHED'],source_backlog_due=ct['SOURCE_BACKLOG_DUE'],future_not_due=ct['FUTURE_SCHEDULE_NOT_DUE']))
    windows=[service(steps,b,e) for b,e in card['service_windows']]
    assert all(w['tracking_error'] is None for w in windows)
    table('R300_A07_SERVICE_WINDOWS.csv',windows)
    table('R300_A07_PHASE_LEDGER_THIN.csv',phase_thin)
    table('R300_A07_CROSSINGS_RECONSTRUCTED.csv',reconstructed_crossings)
    table('R300_A07_CYCLES.csv',cycles)
    table('R300_A07_PRE_RED_WITNESSES.csv',witnesses)
    table('R300_A07_LIFECYCLE_COUNTS.csv',counts)
    table('R300_A07_LIFECYCLE_IDS.csv',lifecycle)
    table('R300_A07_NATIVE_WARNINGS.csv',[dict(index=i+1,message=s) for i,s in enumerate(warnings)])
    report=dict(classification='INDEPENDENT_ENGINEERING_EXPLORATORY_ACTUAL_RAW_AUDIT_NOT_FORMAL',run_id=worker['run_id'],
        disposition='NOT_QUALIFIED_SAFETY_GUARD_STOP',data_integrity='PASS_FOR_COMPLETED_PREFIX_ONLY',
        accounting='RECONCILED_COMPLETED_PREFIX',last_completed_s=1206,last_accounted_s=1206,planned_horizon_s=4200,
        safety='FAIL_PROSPECTIVE_RED_GUARD_BEFORE_MOTION',service='NOT_TESTED_NO_COMPLETE_WINDOW',
        phase='OBSERVED_PREFIX_PASS_FULL_CYCLE_NOT_TESTED',crossing_accounting='PASS_INDEPENDENT_FCD_ALL_OBSERVED_COLORS',
        highest_safe_qualified_rate_veh_h=None,other_fixed_rates='NOT_RUN_HELD',phaseC='NOT_PREPARED_HELD',
        C=C,C_applied=A,E=E,N=N,command_latency=C-A,quantization=A-E,physical_shortfall=E-N,
        prefix_by_segment=dict(PRECONTROL=dict(C=0,E=0,N=0,observed_steps=600),EXTERNAL_HOLD=dict(C=0,E=0,N=0,observed_steps=600)),
        cycles_started=1,cycles_completed=0,partial_cycle_N_G=1,partial_cycle_N_y=0,partial_cycle_N_r=0,
        nominal_n_status='UNQUALIFIED_ASSUMPTION_NOT_REPLACED_WITH_OBSERVED_N',actual_cycle_discharge_distribution='NO_COMPLETED_CYCLE',
        unsafe_witness=unsafe[0],red_witness_count=len(witnesses),fcd_time_semantics='API pre(t) equals FCD(t-1), API post(t+1) equals FCD(t); independently confirmed all storage/ingress observations, crossing and terminal snapshot',
        fcd_tls_summary_steps=1206,pre_state_observations_checked=state_comparisons,receiver_observations_checked=receiver_checks,
        receiver_limitation='Native secureGap logged and nonnegative; no independent dynamics-model recalculation of that API value. No denied cycle exists in observed prefix.',
        phase_api_requests=requests,minimum_logged_normal_acceleration_m_s2=min(float(r['minimum_actual_deceleration_m_s2']) for r in steps),minimum_rounded_fcd_acceleration_m_s2=min(decels),
        native_collisions=0,native_teleports=0,native_emergency_warning_count=0,native_selfloop_warnings=17,
        lifecycle_counts=counts,input_ids=4050,inserted=1467,arrived=1267,in_network_unfinished=200,source_backlog_due=73,future_scheduled=2510,
        lifecycle_note='1541 tripinfo rows include74 undeparted (73due and1future at1206); incremental native loaded1542 is not the input cohort. Native loading bookkeeping cannot replace full input IDs.',
        full_horizon_coverage='FAILED_EARLY_STOP_NOT_IMPUTED',service_windows=windows,
        actual_attempts_in_ledger=len(ledger),effective_qualifications=0,manifest_files_verified=len(manifest),protected_hashes_verified=len(card['protected_baseline_sha256']),
        tests='Independent known examples: red envelope, exactly10pct inclusive screen, failure, incomplete and insufficient-supply windows; actual raw schema/identity/time/crossing/accounting/phase/native-log checks.',
        exclusions='None; failure and all six incomplete windows retained. No metrics, tolerance, vehicle model, inputs or raw files modified.',
        interpretation_boundaries='The conservative prospective guard failed; no red transition at1206 executed, collision, inevitable crash, 300capacity failure, or900 infeasibility is established. E-N=-1 reflects unfinished nominal packet; it is not negative physical shortfall of a completed cycle.',
        next_step='Hold all launches. Engineering diagnosis and independent scientific review must determine whether a bounded minimal repair is possible or IssueSTOP applies. No repair, next rate or closed-loop release follows from this audit.',
        documentation_impact='Parent must update PROJECT_STATE and WORKLOG with actual early safety stop; analyst write scope excludes governance.',
        bindings={str((RAW/'guardian_receipt.json').relative_to(ROOT)):sha(RAW/'guardian_receipt.json'),str(release.relative_to(ROOT)):sha(release),str(Path(__file__).relative_to(ROOT)):sha(__file__),
                  'raw_manifest':manifest})
    report['schema_version'] = 3
    report['supersedes'] = 'R300_A07_ACTUAL_DATA_GATE_V2.json'
    report['supersedes_sha256'] = sha(DEST/'R300_A07_ACTUAL_DATA_GATE_V2.json')
    report['missing_value_policy'] = 'Wholly unobserved windows: JSON null / CSV blank for all measurement sums and differences; observed zero remains numeric zero; partial observed sums retained with no qualification.'
    report['historical_correction'] = 'The earlier V2 service(empty) zero sums and no-zero-imputation prose were inconsistent. V3 corrects expression only; original V2 artifacts/reviews are preserved, not valid missing-value evidence.'
    save(DEST/'R300_A07_ACTUAL_DATA_GATE_V3.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['disposition','last_completed_s','C','E','N','manifest_files_verified','pre_state_observations_checked','source_backlog_due']},indent=2))


if __name__=='__main__':
    main()
