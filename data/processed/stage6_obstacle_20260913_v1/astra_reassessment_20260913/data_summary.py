"""Small post-hoc descriptive audit of existing qualified D2 products; no simulation."""
import hashlib
import json
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'data/processed/stage6_obstacle_20260913_v1/d2_data_review_revision_01'
sources = []

def read(name):
    path = BASE / name
    sources.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return json.loads(path.read_text())

out = {'scope': 'post_hoc_exploratory_descriptive_audit; no registered decision changed',
       'uncertainty': 'TT interval arithmetic covers crossing brackets and optional cohort membership; not a statistical confidence interval; ratio interval is an outer envelope, not sharp identified bounds',
       'conditions': {}, 'sources': sources}
oracles = {}
for condition in ['ML', 'C']:
    oracle = read(f'{condition}_raw_oracle.json')
    measurement = read(f'S6_V1_{condition}_S17_registered_analysis/measurements.json')
    oracles[condition] = oracle
    passages = oracle['r_passages']
    assert len(passages) == len({r['vehicle_id'] for r in passages}) == 300
    assert len(oracle['r_counts']) == len(oracle['ru_labels']) == 20
    categories = {'pre_certain': 0, 'B_certain': 0, 'post_certain': 0, 'boundary_ambiguous': 0}
    for r in passages:
        a, b = r['entry_bracket']
        assert 0 <= a <= b < 2700
        category = ('pre_certain' if b < 300 else 'B_certain' if a >= 300 and b < 1500 else
                    'post_certain' if a >= 1500 and b < 2700 else 'boundary_ambiguous')
        categories[category] += 1
    stats = {}
    for cls in ['M', 'R', 'U']:
        trips = [v for k,v in measurement['tripinfo'].items() if k.startswith(cls + '_')]
        stats[cls] = {'count': len(trips)}
        for field in ['duration','timeLoss','departDelay']:
            values = [v[field] for v in trips]
            stats[cls][field] = {'mean': mean(values), 'median': median(values), 'max': max(values)}
    out['conditions'][condition] = {
        'R_passages': categories,
        'R_first_crossing_bracket': min(r['entry_bracket'] for r in passages),
        'R_last_crossing_bracket': max(r['entry_bracket'] for r in passages),
        'R_B_certain_per60s': oracle['r_counts'],
        'R_B_certain_per60s_sum': sum(oracle['r_counts']),
        'R_B_internal_bin_boundary_events': [r for r in passages
            if r['entry_bracket'][0] >= 300 and r['entry_bracket'][1] < 1500
            and not any(r['entry_bracket'][0] >= t and r['entry_bracket'][1] < t+60
                        for t in range(300,1500,60))],
        'RU_B_joint_stopped_labels': sum(oracle['ru_labels']),
        'M_regional_full_stopped_samples': {k: sum(v['M']) for k,v in oracle['regional_stops'].items()},
        'whole_observed_trip_descriptions': stats,
        'feeder_TT_bounds': oracle['feeder']['bounds'],
        'common_TT_bounds': oracle['common']['bounds']}
out['TT_effect_outer_envelope_percent'] = {}
for domain in ['feeder','common']:
    ml = oracles['ML'][domain]['bounds']
    c = oracles['C'][domain]['bounds']
    out['TT_effect_outer_envelope_percent'][domain] = {
        'lower': 100 * (c['lower']/ml['upper']-1),
        'upper': 100 * (c['upper']/ml['lower']-1)}
out['checks'] = {'unique_R_passages_each': 300, 'complete_B_bins_each': 20, 'no_simulation_calls': True}
target = Path(__file__).with_name('data_summary_revision02.json')
with target.open('x') as stream:
    json.dump(out, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['conditions','sources']}, indent=2))
