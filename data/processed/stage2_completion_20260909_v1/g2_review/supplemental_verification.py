"""Supplemental G2 raw-data checks; default read-only, --record creates a receipt."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--record', action='store_true')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[4]
B = ROOT / 'data/processed/stage2_completion_20260909_v1'
T = ROOT / 'results/tables/stage2_completion_20260909_v1/revision_04'
inputs = {}


def register(path):
    path = Path(path)
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def read_json(path):
    return json.loads(register(path).read_text())


def read_csv(path):
    with register(path).open() as stream:
        return list(csv.DictReader(stream))


l = read_json(B / 'execution_ledger.json')
v = read_csv(T / 'vehicle_accounting.csv')
w = read_csv(T / 'run_window_summary.csv')
m = read_csv(T / 'merge_events.csv')
a = read_json(B / 'revision_04/run_audit.json')
results = []
assert {r['run_id'] for r in l['runs']} == {'C17', 'C23', 'ML17', 'ML23', 'MH17', 'MH23', 'RL17', 'RL23'}
for r in l['runs']:
    rid = r['run_id']
    att = next(x for x in r['attempts'] if x['attempt_id'] == r['selected_attempt_id'])
    mp = read_json(ROOT / att['source_manifest'])
    f = {Path(x['original_absolute_path']).name: ROOT / x['archive_relative_path'] for x in mp['file_map']}
    assert len(f) == len(mp['file_map']), 'Ambiguous archive basenames'
    tripnodes = E.parse(register(f['tripinfo.xml'])).getroot().findall('tripinfo')
    trip = {x.get('id'): x.attrib for x in tripnodes}
    veh = E.parse(register(f['vehroute.xml'])).getroot().findall('vehicle')
    runrows = [x for x in v if x['run_id'] == rid]
    rows = {x['vehicle_id']: x for x in runrows}
    assert len(tripnodes) == len(trip) == len(veh) == len(rows) == len(runrows)
    assert set(trip) == set(rows) == {x.get('id') for x in veh}
    for k, n in trip.items():
        for out, raw in [('actual_depart_s', 'depart'), ('arrival_s', 'arrival'), ('departDelay_s', 'departDelay'), ('completed_duration_s', 'duration')]:
            assert float(rows[k][out]) == float(n[raw]), (rid, k, out)
    ar = next(x for x in a['runs'] if x['run_id'] == rid)
    assert max(float(n['arrival']) for n in trip.values()) == ar['last_arrival_s']
    assert max(float(n['depart']) for n in trip.values()) == ar['last_actual_departure_s']
    loops = [n for n in E.parse(register(f['scenario.add.xml'])).getroot().findall('inductionLoop') if n.get('lane', '').startswith(':freeway_merge_1_')]
    assert len(loops) == 2
    raw = [x.attrib for n in loops for x in E.parse(register(f[Path(n.get('file')).name])).getroot().findall('interval')]
    for win, (lo, hi) in {'Full': (0, 2700), 'A': (0, 1500), 'B': (300, 1500), 'Post': (1500, 2700)}.items():
        sub = [n for n in raw if float(n['begin']) >= lo and float(n['end']) <= hi]
        count = sum(int(n['nVehContrib']) for n in sub)
        sv = [n for n in sub if int(n['nVehContrib']) > 0 and float(n['speed']) >= 0]
        den = sum(int(n['nVehContrib']) for n in sv)
        speed = sum(float(n['speed']) * int(n['nVehContrib']) for n in sv) / den if den else None
        for key, val in [('nVehContrib', count), ('flow_vehph', count * 3600 / (hi - lo)), ('speed_mps', speed)]:
            pubs = [x for x in w if x['run_id'] == rid and x['family'] == 'E1_group' and x['window'] == win and x['metric'] == key]
            assert len(pubs) == 1
            pub = pubs[0]['value']
            assert (val is None and pub == '') or (val is not None and abs(val - float(pub)) < 1e-10), (rid, win, key)
    events = {x['vehicle_id']: x for x in m if x['run_id'] == rid}
    first, prev = {}, {}
    for _, s in E.iterparse(register(f['fcd.xml']), events=('end',)):
        if s.tag != 'timestep':
            continue
        t = float(s.get('time'))
        for n in s:
            k, lane = n.get('id'), n.get('lane')
            if k in events and k not in first:
                if lane.startswith('main_down_'):
                    first[k] = t
                    assert t == float(events[k]['first_downstream_time_s'])
                    assert prev[k] == (float(events[k]['previous_time_s']), events[k]['previous_lane'])
                prev[k] = (t, lane)
        s.clear()
    assert len(first) == len(events)
    results.append({'run_id': rid, 'status': 'passed', 'vehicle_rows': len(rows), 'vehicle_fields_checked': ['actual_depart_s', 'arrival_s', 'departDelay_s', 'completed_duration_s'], 'tripinfo_vehroute_table_id_sets_equal': True, 'E1_group_window_metric_checks': 12, 'first_R_downstream_events': len(first), 'last_departure_s': ar['last_actual_departure_s'], 'last_arrival_s': ar['last_arrival_s']})
starts = sum(int(x.get('sumo_started', False)) for r in l['runs'] if r['origin'] == 'new' for x in r['attempts'])
assert starts == l['budget']['actual_new_starts'] == 7
assert l['budget']['retries_used'] == 0
report = {'status': 'passed', 'scope': 'Supplement existing revision_04 verification; direct raw XML checks without importing production analysis.', 'runs': results, 'vehicle_rows': sum(x['vehicle_rows'] for x in results), 'first_R_events': sum(x['first_R_downstream_events'] for x in results), 'actual_new_starts_recounted': starts, 'input_sha256': inputs, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'limitations': ['vehroute check covers complete identity sets, not all XML attributes.', 'Four published per-vehicle numeric fields checked, not every possible XML attribute.', '1 Hz first downstream observation is not exact physical crossing time.', 'No schedule, ordinary E1 per-ID completeness, statistical robustness or causal inference established.'], 'reproduce': '.venv/bin/python data/processed/stage2_completion_20260909_v1/g2_review/supplemental_verification.py'}
if args.record:
    with Path(__file__).with_suffix('.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
print(json.dumps({k: report[k] for k in ['status', 'vehicle_rows', 'first_R_events', 'actual_new_starts_recounted']}))
