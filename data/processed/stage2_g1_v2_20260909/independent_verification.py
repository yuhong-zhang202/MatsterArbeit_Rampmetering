"""Read raw records independently of the production parser; exclusive report."""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
TABLES = ROOT / 'results/tables/stage2_g1_v2_20260909'
RUNTIME = Path('/private/tmp/minimal_uncontrolled_8egb0qb1')
manifest = json.loads((BATCH / 'manifest.json').read_text())
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
for path, expected in {**manifest['source_sha256'], **manifest['generated_sha256']}.items():
    assert sha(path) == expected, path
assert sha(manifest['script']) == manifest['script_sha256']

def read_csv(name):
    with (TABLES/name).open() as stream:
        return list(csv.DictReader(stream))
e1 = read_csv('e1_native.csv')
lanes = read_csv('mainline_lane_timeline.csv')
cohort = read_csv('cohort_accounts.csv')
events = read_csv('merge_events.csv')
assert len(e1) == 360 and len(lanes) == 37814 and len(cohort) == 396 and len(events) == 300
assert len({(r['time_s'],r['lane_id'],r['vehicle_class']) for r in lanes}) == len(lanes)
assert len({r['vehicle_id'] for r in events}) == 300
assert all(r['vehicle_samples']=='' and r['stopped_samples']=='' and r['observation_available']=='False' for r in lanes if float(r['time_s'])==2700)

raw_interval_count = 0
empty_speed_count = 0
extrema = {}
for node in ET.parse(RUNTIME/'scenario.add.xml').getroot().findall('inductionLoop'):
    detector = node.attrib['id']
    raw = ET.parse(node.attrib['file']).getroot().findall('interval')
    table = [r for r in e1 if r['detector_id']==detector]
    for interval,row in zip(raw,table,strict=True):
        for key,column in [('begin','begin_s'),('end','end_s'),('flow','flow_vehph'),('speed','speed_raw_mps'),('occupancy','occupancy_pct'),('nVehContrib','nVehContrib'),('nVehEntered','nVehEntered')]:
            assert float(interval.attrib[key])==float(row[column])
        if int(interval.attrib['nVehContrib'])==0:
            empty_speed_count+=1
            assert row['speed_valid']=='False'
        raw_interval_count+=1
    valid=[r.attrib for r in raw if int(r.attrib['nVehContrib'])>0]
    extrema[detector]=min(valid,key=lambda r:float(r['speed']))

# Independently verify the two raw records defining each published bracket.
event_by_id={r['vehicle_id']:r for r in events}
matched_pairs=set()
window_specs=[(450,480,'main_up_1'),(1470,1530,'main_up_1'),(1980,2010,'main_down_1')]
minima={str(w):None for w in window_specs}
for _,step in ET.iterparse(RUNTIME/'outputs/fcd.xml',events=('end',)):
    if step.tag!='timestep':continue
    time=float(step.attrib['time'])
    for vehicle in step:
        a=vehicle.attrib
        event=event_by_id.get(a['id'])
        if event:
            if time==float(event['previous_time_s']):
                assert a['lane']==event['previous_lane']
                matched_pairs.add((a['id'],'previous'))
            if time==float(event['first_downstream_time_s']):
                assert a['lane']==event['first_downstream_lane']
                matched_pairs.add((a['id'],'downstream'))
        for window in window_specs:
            if window[0]<=time<window[1] and a['lane']==window[2]:
                key=str(window)
                if minima[key] is None or float(a['speed'])<float(minima[key]['speed']):
                    minima[key]={'time_s':time,**a}
    step.clear()
assert len(matched_pairs)==600
ambiguous=[r for r in events if r['boundary_30s_ambiguous']=='True']
assert len(ambiguous)==4
assert all(float(r['first_downstream_time_s'])-float(r['previous_time_s'])==1 for r in events)
assert all(float(r['first_downstream_time_s'])%30==0 for r in ambiguous)
for path, expected in manifest['source_sha256'].items():
    assert sha(path)==expected
report={'status':'passed_for_declared_checks', 'script_sha256':sha(__file__),
        'command':'.venv/bin/python data/processed/stage2_g1_v2_20260909/independent_verification.py',
        'table_rows':{'e1':len(e1),'lane_class':len(lanes),'cohort':len(cohort),'merge':len(events)},
        'raw_e1_rows_reconciled':raw_interval_count,'empty_speed_intervals':empty_speed_count,
        'merge_raw_endpoint_records_reconciled':len(matched_pairs),
        'merge_30s_boundary_cases':ambiguous,
        'first_downstream_observations_before':{str(t):sum(float(r['first_downstream_time_s'])<t for r in events) for t in [300,600,900,1200,1500,1800,2100,2400,2700]},
        'e1_minimum_valid_speed_intervals':extrema,'selected_raw_fcd_minima':minima,
        'source_and_artifact_hashes_unchanged':True,
        'interpretation':'E1 minima and selected same-lane raw FCD minima differ; no claim of instrument defect or congestion from this alone. Crossing brackets are sampled observations, not exact times.',
        'figure_check':'Analyst viewed PNG: 4 separate detector series, correct units, native step intervals, missing-speed gaps, 1500 dashed boundary and 1500-2700 shading; source table checked above.',
        'limitations':['Scientific review remains pending.','No exact substep trajectory or detector passage logs used.','No new simulation or independent statistical replication.']}
with (BATCH/'independent_verification.json').open('x') as stream:
    json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({k:report[k] for k in ['status','table_rows','raw_e1_rows_reconciled','empty_speed_intervals','merge_raw_endpoint_records_reconciled']}))
