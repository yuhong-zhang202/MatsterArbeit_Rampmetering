"""Build diagnostic candidate and exact patch; never edit live scripts or start SUMO."""
from pathlib import Path
import difflib, json, hashlib
ROOT=Path.cwd(); S=ROOT/'scripts/formal_development_20261007_v1'; E=ROOT/'artifacts/formal_development_20261007_v1/engineering'
C=E/'FIX02_candidate'; C.mkdir(exist_ok=True)
texts={p.name:p.read_text() for p in S.glob('*.py')}
helper=texts['safe_actuator_fix02.py']
helper=helper.replace('    types = set()\n', '    if root.findall("flow") or root.findall("trip"):\n        raise ValueError("uncovered dynamic insertion source")\n    types = set()\n')
helper=helper.replace('        if node.get("id", "").split("_", 1)[0] != "R":\n            continue\n        route = routes.get(node.get("route"), [])\n', '        route = routes.get(node.get("route"), [])\n        is_ramp = node.get("id", "").split("_", 1)[0] == "R"\n        if not is_ramp and "ramp_storage" in route:\n            raise ValueError("non-R storage entrant not covered")\n        if not is_ramp:\n            continue\n')
helper+='''\n\ndef capture_approaching_states(conn, upstream_length_m, expected_type, max_speed_m_s):
    """Observe every current internal connector vehicle in storage coordinates."""
    states = {}
    for vid in conn.lane.getLastStepVehicleIDs(UPSTREAM_LANE):
        type_id = conn.vehicle.getTypeID(vid)
        if type_id != expected_type or vid.split("_", 1)[0] != "R":
            raise ValueError("uncovered actual storage entrant")
        position = conn.vehicle.getLanePosition(vid)
        speed = conn.vehicle.getSpeed(vid)
        if not (0 <= position <= upstream_length_m and 0 <= speed <= max_speed_m_s + 1e-9):
            raise ValueError("entrant violates checked coordinate/speed bounds")
        states[vid] = VehicleState(position - upstream_length_m, speed,
            conn.vehicle.getLength(vid), conn.vehicle.getMinGap(vid),
            conn.vehicletype.getAccel(type_id), conn.vehicletype.getDecel(type_id))
    return states
'''
texts['safe_actuator_fix02.py']=helper
w=texts['v15_worker.py']
w=w.replace('VehicleState, LeaderState, assess_release,','VehicleState, LeaderState,')
w=w.replace('BASE_PACKAGES =', 'from safe_actuator_fix02 import (REVISION, assess_release, checked_upstream_geometry,\n    checked_ramp_input_type, qualify_entrant_coverage, capture_approaching_states)\nBASE_PACKAGES =',1)
w=w.replace('    ("base_output",),', '    ("guard_revision",),\n    ("base_output",),',1)
w=w.replace('    if card["startup_deadline_s"] != 60', '    if card["guard_revision"] != REVISION:\n        raise ValueError("uncorrected guard card is held")\n    if card["startup_deadline_s"] != 60',1)
w=w.replace('        for t in range(HORIZON):', '''        if mode == "ALINEA":
            upstream_length = checked_upstream_geometry(NETWORK)
            ramp_type = checked_ramp_input_type(package / "demand.rou.xml")
            maximum_type_speed = conn.vehicletype.getMaxSpeed(ramp_type)
            entrant_coverage = qualify_entrant_coverage(
                upstream_length_m=upstream_length, max_speed_m_s=maximum_type_speed,
                accel_m_s2=conn.vehicletype.getAccel(ramp_type),
                tau_s=conn.vehicletype.getTau(ramp_type),
                action_step_s=conn.vehicletype.getActionStepLength(ramp_type))
            write_json_exclusive(output / "fix02_entrant_coverage.json", entrant_coverage)
        for t in range(HORIZON):''',1)
w=w.replace('                    type_id=conn.vehicle.getTypeID(vid)\n', '                    type_id=conn.vehicle.getTypeID(vid)\n                    if type_id != ramp_type:\n                        raise ValueError("uncovered storage type under FIX02")\n',1)
w=w.replace('                decision=assess_release(vehicles=safety_states,storage_length_m=lane_length,', '''                approaching_states = capture_approaching_states(
                    conn, upstream_length, ramp_type, maximum_type_speed)
                decision=assess_release(approaching_vehicles=approaching_states,
                    vehicles=safety_states,storage_length_m=lane_length,''',1)
texts['v15_worker.py']=w
r=texts['runner.py']
r=r.replace('from queue_protection import QueueParameters', 'from queue_protection import QueueParameters\nfrom safe_actuator_fix02 import REVISION, checked_upstream_geometry, checked_ramp_input_type')
r=r.replace('SUMO = Path(', 'REPAIR_ADDENDUM = BASE / "engineering/FIX02_REPAIR_ADDENDUM.json"\nSUMO = Path(',1)
r=r.replace('"queue_protection.py","test_offline.py"', '"queue_protection.py","test_offline.py","safe_actuator_fix02.py"')
r=r.replace('    if not CONTRACT.is_file():', '    if not REPAIR_ADDENDUM.is_file(): raise ValueError("repair addendum missing")\n    if not CONTRACT.is_file():',1)
r=r.replace('          "contract_sha256":sha(CONTRACT),', '          "guard_revision":REVISION,"repair_addendum_sha256":sha(REPAIR_ADDENDUM),\n          "contract_sha256":sha(CONTRACT),',1)
r=r.replace('    if sha(CONTRACT)!=c["contract_sha256"]:', '''    if c.get("guard_revision") != REVISION or c.get("repair_addendum_sha256") != sha(REPAIR_ADDENDUM):
        raise ValueError("repair revision/addendum mismatch")
    if set(c["source_sha256"]) != {str(p) for p in SOURCE_FILES+IMMUTABLE_SOURCES}:
        raise ValueError("incomplete source binding")
    checked_upstream_geometry(NETWORK)
    checked_ramp_input_type(Path(c["package"])/"demand.rou.xml")
    if sha(CONTRACT)!=c["contract_sha256"]:''',1)
texts['runner.py']=r
t=texts['test_offline.py'].replace('return dict(base_output=', 'return dict(guard_revision=v15_worker.REVISION, base_output=',1)
insert='''\n\nclass CorrectedGuardTests(unittest.TestCase):
    def setUp(self):
        from safe_actuator_fix02 import VehicleState
        self.V = VehicleState
        self.kw = dict(storage_length_m=204.49, route_coverage_ok=True,
            leader_lookahead_m=478.67, connected_path_length_m=181.05,
            allowed_downstream_lanes=frozenset(), leader=None, secure_gap_m=None,
            nearest_internal_vehicle_id=None, nearest_internal_rear_clearance_m=math.inf)
        self.front = self.V(203.49, 0, 5, 2.5, 2.6, 4.5)

    def check(self, states, approaching=None):
        from safe_actuator_fix02 import assess_release
        return assess_release(vehicles=states, approaching_vehicles=approaching or {}, **self.kw)

    def test_recorded_counterexample(self):
        from safe_actuator_fix02 import legacy_assess_release, required_pre_green_distance_m
        states = {"R_flow.0":self.front,
                  "R_flow.3":self.V(114.69805754,20.61937210,5,2.5,2.6,4.5)}
        self.assertTrue(legacy_assess_release(vehicles=states, **self.kw)["allowed"])
        d=self.check(states)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["reason"],"FOLLOWER_POST_RED_PREDICTION")
        self.assertGreater(required_pre_green_distance_m(states["R_flow.3"]), 89.79194246)

    def test_boundary_and_stopped_and_moving_follower(self):
        from dataclasses import replace
        from safe_actuator_fix02 import required_pre_green_distance_m
        for speed in (0, 0.099, 0.1, 5, 20.6193721, 30):
            follower=self.V(0,speed,5,2.5,2.6,4.5)
            req=required_pre_green_distance_m(follower)
            follower=replace(follower,position_m=204.49-req)
            self.assertTrue(self.check({"front":self.front,"follower":follower})["allowed"])
            self.assertFalse(self.check({"front":self.front,"follower":replace(follower,position_m=follower.position_m+1e-6)})["allowed"])

    def test_next_speed_bound_implies_unchanged_post(self):
        from dataclasses import replace
        from safe_actuator_fix02 import required_pre_green_distance_m, immediate_red_stop_requirement_m
        for speed in (0,0.099,0.1,5,20.6193721,30,55.55):
            state=self.V(0,speed,5,2.5,2.6,4.5)
            pre=required_pre_green_distance_m(state)
            for fraction in (0,0.001,0.25,0.75,1):
                nxt=(speed+state.accel_m_s2)*fraction
                self.assertGreaterEqual(pre-nxt+1e-9, immediate_red_stop_requirement_m(replace(state,speed_m_s=nxt)))

    def test_entrant_guard_and_coverage_bound(self):
        from safe_actuator_fix02 import qualify_entrant_coverage
        entrant=self.V(-0.01,40,5,2.5,2.6,4.5)
        d=self.check({"front":self.front},{"entrant":entrant})
        self.assertFalse(d["allowed"])
        self.assertEqual(d["unsafe_followers"],("entrant",))
        x=dict(upstream_length_m=113.08,max_speed_m_s=55.55,accel_m_s2=2.6,tau_s=1,action_step_s=1)
        self.assertLess(qualify_entrant_coverage(**x)["maximum_one_step_advance_m"],113.08)
        for field,value in (("max_speed_m_s",111),("tau_s",0.9),("action_step_s",2)):
            with self.assertRaises(ValueError): qualify_entrant_coverage(**{**x,field:value})
        with self.assertRaises(ValueError): self.check({"same":self.front},{"same":entrant})
        with self.assertRaises(ValueError): self.check({"front":self.front},{"entrant":self.V(.01,0,5,2.5,2.6,4.5)})

    def test_legacy_front_and_interlock_preserved(self):
        from safe_actuator_fix02 import legacy_assess_release
        from stage6_safe_actuator_v10 import post_green_red_interlock
        for front in (self.front,self.V(195,12,5,2.5,2.6,4.5)):
            states={"front":front}
            self.assertEqual(self.check(states)["allowed"],legacy_assess_release(vehicles=states,**self.kw)["allowed"])
        d=post_green_red_interlock(expected_front_id="front",crossing_ids=("front",),
            remaining_storage={"follower":self.V(135.57582461,20.87776707,5,2.5,2.6,4.5)},storage_length_m=204.49)
        self.assertTrue(d["abort"])
'''
t=t.replace('\n\nif __name__ == "__main__":',insert+'\n\nif __name__ == "__main__":')
texts['test_offline.py']=t
patch=['*** Begin Patch\n']
for name in ('safe_actuator_fix02.py','v15_worker.py','runner.py','test_offline.py'):
    old=(S/name).read_text(); new=texts[name]
    (C/name).write_text(new)
    patch.append('*** Update File: scripts/formal_development_20261007_v1/'+name+'\n')
    diff=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),n=3))[2:]
    patch.extend('@@\n' if line.startswith('@@') else line for line in diff)
patch.append('*** End Patch\n')
(E/'FIX02_IMPLEMENTATION.patch').write_text(''.join(patch))
(E/'FIX02_REPAIR_ADDENDUM.json').write_text(json.dumps({
    'classification':'DEVELOPMENT_TECHNICAL_SAFETY_REPAIR','revision':'FIX02_GREEN_ADVANCE_PLUS_POST_RED',
    'authority':'D-019 and ../SCIENCE_FIX02_REPAIR_SCOPE.md',
    'original_parameter_contract_sha256':hashlib.sha256((E/'PARAMETER_CONTRACT.json').read_bytes()).hexdigest(),
    'original_post_guard_sha256':hashlib.sha256((ROOT/'src/stage6_safe_actuator_v10.py').read_bytes()).hexdigest(),
    'precondition':'For each current storage follower and each vehicle on the upstream internal connector: distance_to_meter >= (v+a)*1s + immediate_red_stop_requirement(v+a).',
    'derivation':'At fixed dt=1, speed_next<=v+a, displacement_green<=v+a. Post requirement is monotone nondecreasing for nonnegative speed, including its stopped shortcut. Subtracting displacement from pre distance leaves at least the unchanged post requirement.',
    'coverage':'All current connector vehicles are observed. Checked route/input topology and actual type maximum speed plus acceleration below connector length exclude vehicles further upstream or newly inserted from entering storage during one green step.',
    'front_limit':'Intended front retains legacy route/receiver/reachability gate. Empty-green front and crossings remain protected by the unchanged mandatory post interlock; follower bound is not a proof that every intended moving front crosses.',
    'unchanged':['post interlock and 1.1m margin','1s step/green and >=2s red','network, model, vehicle requests, seeds, demand','nominal feedback and queue override definitions','900 cap and 10% service screen','credit scheduler','runtime/storage rules'],
    'reuse':'Old controlled evidence must pass decision and pulse/credit equivalence, not only sampled post safety. Replacements remain within same authorized combinations.',
    'release':'HOLD pending exact corrected source/card and independent release'
},indent=2)+'\n')
print(json.dumps({'patch':str(E/'FIX02_IMPLEMENTATION.patch'),'patch_sha256':hashlib.sha256((E/'FIX02_IMPLEMENTATION.patch').read_bytes()).hexdigest()}))
