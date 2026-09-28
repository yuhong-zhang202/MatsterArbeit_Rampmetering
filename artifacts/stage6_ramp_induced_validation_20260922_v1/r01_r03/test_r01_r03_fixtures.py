from audit_static_inputs import run as audit_r01
from paired_matching import OBSERVED_FIELDS, PLANNED_FIELDS, PRE_R_SAMPLE_FIELDS, compare_pair


def main():
    r01 = audit_r01()
    assert r01["status"] == "PASS_STATIC_SEMANTIC_DIFF_WITH_OUTPUT_PLACEHOLDERS"

    planned = [{"class": "M", "vehicle_id": "M.0", "scheduled_depart": 0.0,
                "route_id": "M_route", "type_id": "technical_passenger", "depart_pos": "100",
                "depart_lane": "best", "depart_speed": "max"}]
    assert compare_pair(planned, planned.copy(), PLANNED_FIELDS)["status"] == "PASS_EXACT"
    altered = [dict(planned[0], depart_pos="last")]
    mismatch = compare_pair(planned, altered, PLANNED_FIELDS)
    assert mismatch["status"] == "MISMATCH_VISIBLE"
    assert mismatch["mismatches"][0]["fields"]["depart_pos"] == {"control": "100", "transition": "last"}

    observed = [{"class": "M", "vehicle_id": "M.0", "time": 539.0, "lane": "main_up_0",
                 "pos": 100.0, "x": 25.0, "speed": 27.0}]
    assert compare_pair(observed, observed.copy(), PRE_R_SAMPLE_FIELDS)["status"] == "PASS_EXACT"
    shifted = [dict(observed[0], speed=26.999)]
    assert compare_pair(observed, shifted, PRE_R_SAMPLE_FIELDS)["status"] == "MISMATCH_VISIBLE"
    missing = []
    assert compare_pair(observed, missing, PRE_R_SAMPLE_FIELDS)["status"] == "MISMATCH_VISIBLE"
    required_missing_both = dict(planned[0])
    required_missing_both.pop("depart_pos")
    incomplete_both = compare_pair([required_missing_both], [dict(required_missing_both)], PLANNED_FIELDS)
    assert incomplete_both["status"] == "INCOMPLETE_REQUIRED_FIELDS"
    required_missing_one = dict(planned[0])
    required_missing_one.pop("depart_pos")
    incomplete_one = compare_pair([required_missing_one], [planned[0]], PLANNED_FIELDS)
    assert incomplete_one["status"] == "INCOMPLETE_REQUIRED_FIELDS"
    obs_control = {"class": "M", "vehicle_id": "M.0", "actual_depart": 1.0, "speed_factor_precise": 1.0}
    obs_transition = dict(obs_control, speed_factor_precise=1.01)
    assert compare_pair([obs_control], [obs_transition], OBSERVED_FIELDS)["status"] == "MISMATCH_VISIBLE"
    speed_factor_missing = dict(obs_control)
    speed_factor_missing.pop("speed_factor_precise")
    assert compare_pair([speed_factor_missing], [speed_factor_missing], OBSERVED_FIELDS)["status"] == "INCOMPLETE_REQUIRED_FIELDS"
    try:
        compare_pair(planned, planned + planned, PLANNED_FIELDS)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate IDs not rejected")
    print("R01 static XML audit + R03 exact-match/mismatch/missing/duplicate fixtures: PASS")


if __name__ == "__main__":
    main()
