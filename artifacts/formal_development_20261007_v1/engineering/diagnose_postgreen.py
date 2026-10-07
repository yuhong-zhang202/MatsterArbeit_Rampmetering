"""Pure recorded-state guard counterexample. No TraCI import or simulation."""
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from stage6_safe_actuator_v10 import VehicleState,assess_release,post_green_red_interlock,normal_red_stop_requirement_m,immediate_red_stop_requirement_m
run='DEV_M3600_R750_S17_T1_A02'
raw=ROOT/f'data/raw/formal_development_20261007_v1/{run}/outputs'
card_path=ROOT/f'artifacts/formal_development_20261007_v1/inputs/{run}/card.json'
row=list(csv.DictReader((raw/'controller_steps.csv').open()))[-1]
assert row['time_begin_s']=='653'
pre={v['vehicle_id']:VehicleState(v['position_m'],v['speed_m_s'],5.0,2.5,v['accel_m_s2'],v['decel_m_s2']) for v in json.loads(row['guard_vehicle_states_json'])}
input=json.loads(row['post_green_interlock_json'])['input_evidence']
post={vid:VehicleState(**value) for vid,value in input['remaining_storage'].items()}
pre_decision=assess_release(vehicles=pre,storage_length_m=204.49,route_coverage_ok=True,
    leader_lookahead_m=478.67,connected_path_length_m=181.05,allowed_downstream_lanes=frozenset(),
    leader=None,secure_gap_m=None,nearest_internal_vehicle_id=None,nearest_internal_rear_clearance_m=float('inf'))
post_decision=post_green_red_interlock(expected_front_id=input['expected_front_id'],crossing_ids=tuple(input['crossing_ids']),remaining_storage=post,storage_length_m=204.49)
assert pre_decision['allowed'] and pre_decision['reason']=='STOPPED_READY'
assert post_decision['abort'] and post_decision['unsafe_ids']==('R_flow.3',)
before=pre['R_flow.3'];after=post['R_flow.3']
minimal_pre={vid:pre[vid] for vid in ('R_flow.0','R_flow.3')}
minimal=assess_release(vehicles=minimal_pre,storage_length_m=204.49,route_coverage_ok=True,
    leader_lookahead_m=478.67,connected_path_length_m=181.05,allowed_downstream_lanes=frozenset(),
    leader=None,secure_gap_m=None,nearest_internal_vehicle_id=None,nearest_internal_rear_clearance_m=float('inf'))
assert minimal['allowed']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
result={'status':'VERIFIED_PRE_GUARD_DOES_NOT_IMPLY_POST_INTERLOCK','run_id':run,
    'raw_sha256':{name:sha(raw/name) for name in ('controller_steps.csv','worker_stderr.log','fcd.xml.gz')},
    'card_sha256':sha(card_path),'guard_source_sha256':sha(ROOT/'src/stage6_safe_actuator_v10.py'),
    'pre_time_s':653,'post_time_s':654,'fcd_post_label_s':653,
    'pre_full_guard':pre_decision,'post_full_guard':post_decision,
    'minimal_pre_population':{vid:asdict(value) for vid,value in minimal_pre.items()},
    'minimal_pre_guard':minimal,'minimal_post_follower':asdict(after),
    'pre_follower_gap_m':204.49-before.position_m,'pre_required_m':normal_red_stop_requirement_m(before),
    'pre_margin_m':204.49-before.position_m-normal_red_stop_requirement_m(before),
    'post_follower_gap_m':204.49-after.position_m,'post_required_m':immediate_red_stop_requirement_m(after),
    'post_margin_m':204.49-after.position_m-immediate_red_stop_requirement_m(after),
    'green_step_advance_m':after.position_m-before.position_m,
    'pre_gap_needed_for_observed_post_requirement_m':after.position_m-before.position_m+immediate_red_stop_requirement_m(after),
    'scope':'Actual recorded pair and pure guard replay, not a prospective next-speed prediction or repaired controller.',
    'simulation_starts':0,'source_changes':False}
with Path(__file__).with_name('FIX02_DIAGNOSIS.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'status':result['status'],'simulation_starts':0}))
