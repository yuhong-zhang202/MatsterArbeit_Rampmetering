"""Pure offline boundary fixture for the locked S density gate.

No simulator or project output is touched.  The exact ratio is represented by
integer sample counts because all compared rows use the same mapped cell
denominator.  This is the serialization-safe equivalent of candidate >= 1.25
* reference.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = [
    ROOT / "data/processed/stage6_protectable_state_application_20260921_v1/apply_rule.py",
    ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/apply_rule.py",
]

def load(path):
    spec = spec_from_file_location("locked_density_fixture", path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    results = []
    for path in SOURCES:
        mod = load(path)
        ref = {"mean_M_density_veh_per_lane_km": 4.0, "M_density_sample_count": 4}
        exact = {"mean_M_density_veh_per_lane_km": 5.0, "M_density_sample_count": 5}
        below = {"mean_M_density_veh_per_lane_km": 4.0, "M_density_sample_count": 4}
        above = {"mean_M_density_veh_per_lane_km": 6.0, "M_density_sample_count": 6}
        observed = [
            mod.density_gate(exact, 4.0, 4, 1.25),
            mod.density_gate(below, 4.0, 4, 1.25),
            mod.density_gate(above, 4.0, 4, 1.25),
        ]
        expected = [True, False, True]
        if observed != expected:
            raise AssertionError(f"{path}: expected {expected}, observed {observed}")
        results.append({"source": str(path), "exact_1_25_pass": True, "below_fail": True, "above_pass": True})
    print({"status": "PASS", "results": results})

if __name__ == "__main__":
    main()
