"""Additional exact recorded-state and live-card evidence; no SUMO or TraCI."""
import csv, hashlib,json,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path.cwd(); E=ROOT/'artifacts/formal_development_20261007_v1/engineering'
sys.path.insert(0,str(ROOT/'scripts/formal_development_20261007_v1'))
from safe_actuator_fix02 import assess_release,VehicleState,required_pre_green_distance_m,capture_approaching_states
import runner
raw=ROOT/'data/raw/formal_development_20261007_v1/DEV_M3600_R750_S17_T1_A02/outputs/controller_steps.csv'
with raw.open() as f: row=list(csv.DictReader(f))[-1]
assert row['time_begin_s']=='653'
states={v['vehicle_id']:VehicleState(v['position_m'],v['speed_m_s'],5,2.5,v['accel_m_s2'],v['decel_m_s2']) for v in json.loads(row['guard_vehicle_states_json'])}
decision=assess_release(vehicles=states,approaching_vehicles={},storage_length_m=204.49,route_coverage_ok=True,leader_lookahead_m=478.67,connected_path_length_m=181.05,allowed_downstream_lanes=frozenset(),leader=None,secure_gap_m=None,nearest_internal_vehicle_id=None,nearest_internal_rear_clearance_m=float('inf'))
assert not decision['allowed'] and 'R_flow.3' in decision['unsafe_followers']
# Validate actual observation API-to-coordinate plumbing with a deterministic fake connection.
conn=SimpleNamespace(lane=SimpleNamespace(getLastStepVehicleIDs=lambda lane:('R_flow.test',)),vehicle=SimpleNamespace(getTypeID=lambda vid:'technical_passenger',getLanePosition=lambda vid:110.08,getSpeed=lambda vid:20.0,getLength=lambda vid:5.0,getMinGap=lambda vid:2.5),vehicletype=SimpleNamespace(getAccel=lambda typ:2.6,getDecel=lambda typ:4.5))
observed=capture_approaching_states(conn,113.08,'technical_passenger',55.55)
assert abs(observed['R_flow.test'].position_m+3)<1e-10
card=ROOT/'artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R750_S17_T1_A03/card.json'
c=runner.preflight(card)
assert not Path(c['output']).parent.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
result={'status':'PASS_EXACT_COUNTEREXAMPLE_AND_CARD','simulation_starts':0,'raw_sha256':sha(raw),'full_recorded_pre653_fixed_decision':decision,'offender_pre_gap_m':204.49-states['R_flow.3'].position_m,'offender_corrected_requirement_m':required_pre_green_distance_m(states['R_flow.3']),'entrant_observation_projection':'PASS 110.08-113.08=-3m','card':str(card),'card_sha256':sha(card),'source_sha256':c['source_sha256'],'repair_addendum_sha256':c['repair_addendum_sha256'],'original_contract_sha256':c['contract_sha256'],'raw_path_absent':True}
with (E/'FIX02_EXACT_VERIFICATION.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'card_sha256':result['card_sha256'],'gap_m':result['offender_pre_gap_m'],'new_required_m':result['offender_corrected_requirement_m']}))
