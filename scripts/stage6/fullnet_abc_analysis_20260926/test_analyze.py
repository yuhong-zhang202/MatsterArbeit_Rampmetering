"""Small synthetic schema and arithmetic fixtures; never runs SUMO."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("fullnet_analyze", HERE / "analyze.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AnalysisFixture(unittest.TestCase):
    def make_fixture(self, root):
        arms = {}
        for arm in mod.ARMS:
            raw = root / arm / "outputs"
            raw.mkdir(parents=True)
            demand = root / arm / "demand.rou.xml"
            ids = ["M_flow.0", "U_flow.0", "X_flow.0"]
            if arm != "R0":
                ids += ["R_flow.0"]
            vehicles = "".join(
                f'<vehicle id="{vid}" depart="{540 if vid[0] == "R" else 0}" '
                'type="car" speedFactor="1.01" departLane="best" '
                'departSpeed="max" departPos="last"><route edges="a b"/></vehicle>'
                for vid in ids)
            demand.write_text("<routes>" + vehicles + "</routes>")
            trips = "".join(
                f'<tripinfo id="{vid}" depart="{540 if vid[0] == "R" else 0}" '
                'departDelay="0" arrival="600" timeLoss="6"/>' for vid in ids)
            (raw / "tripinfo.xml").write_text("<tripinfos>" + trips + "</tripinfos>")
            veh = "".join(
                f'<vehicle id="{vid}" depart="{540 if vid[0] == "R" else 0}" arrival="600"/>'
                for vid in ids)
            (raw / "vehroute.xml").write_text("<routes>" + veh + "</routes>")
            frames = []
            for t in range(mod.HORIZON):
                content = ''
                if t < 5:
                    content = '<vehicle id="M_flow.0" lane="merge_section_1" x="1500" y="0" pos="100" speed="20"/>'
                if t == 540 and arm != "R0":
                    content = '<vehicle id="R_flow.0" lane="merge_section_1" x="1500" y="0" pos="100" speed="10"/>'
                frames.append(f'<timestep time="{t}">{content}</timestep>')
            (raw / "fcd.xml").write_text("<fcd-export>" + ''.join(frames) + "</fcd-export>")
            intervals = ''.join(
                f'<interval begin="{30*i}" end="{30*(i+1)}" maxJamLengthInVehicles="0" '
                'maxJamLengthInMeters="0" meanOccupancy="0"/>' for i in range(90))
            (raw / "ramp_storage_e2.xml").write_text("<detector>" + intervals + "</detector>")
            (raw / "lanechanges.xml").write_text("<lanechanges/>")
            manifest = {"artifact_roles": [], "support_files": []}
            for name in ("tripinfo.xml", "vehroute.xml", "fcd.xml", "ramp_storage_e2.xml", "lanechanges.xml"):
                p = raw / name
                manifest["artifact_roles"].append({"relative_path": name,
                    "size_bytes": p.stat().st_size, "sha256": mod.digest(p)})
            (raw / "output_manifest.json").write_text(json.dumps(manifest))
            arms[arm] = {"raw_outputs": str(raw), "demand_xml": str(demand)}
        path = root / "spec.json"
        path.write_text(json.dumps({"arms": arms, "expected_counts": {"M": 1, "R": 1, "U": 1, "X": 1}}))
        return path

    def test_end_to_end_counts_and_exposure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.make_fixture(root)
            out = root / "derived"
            receipt = mod.run(path, out)
            self.assertEqual(receipt["status"], "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_DISPOSITION")
            import csv
            with (out / "R_exposure.csv").open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(next(r for r in rows if r["arm"] == "A")["R_through_unique"], "1")
            with (out / "M_core_30s.csv").open() as f:
                core = list(csv.DictReader(f))
            row = next(r for r in core if r["arm"] == "R0" and r["cell"] == "15" and r["begin"] == "0")
            self.assertEqual(row["M_samples"], "5")
            self.assertEqual(float(row["M_mean_speed_mps"]), 20)
            self.assertAlmostEqual(float(row["M_mean_simultaneous_count"]), 5/30)
            self.assertAlmostEqual(float(row["M_density_veh_per_km"]), 5/(30*0.2))
            empty = next(r for r in core if r["arm"] == "R0" and r["cell"] == "15" and r["begin"] == "30")
            self.assertEqual(empty["M_mean_speed_mps"], "")
            with (out / "pre_R_pairability.csv").open() as f:
                pre = list(csv.DictReader(f))
            self.assertEqual(next(r for r in pre if r["class"] == "M")["exact_tuple_matches"], "5")
            with (out / "route_costs.csv").open() as f:
                costs = list(csv.DictReader(f))
            m = next(r for r in costs if r["arm"] == "R0" and r["class"] == "M")
            self.assertEqual(float(m["network_residence_observed_mean_per_planned_s"]), 600)
            self.assertEqual(float(m["timeLoss_recorded_sum_s"]), 6)

    def test_exogenous_change_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.make_fixture(root)
            b = root / "B" / "demand.rou.xml"
            b.write_text(b.read_text().replace('speedFactor="1.01"', 'speedFactor="1.02"', 1))
            with self.assertRaisesRegex(ValueError, "Exogenous input mismatch"):
                mod.run(path, root / "derived")
            self.assertFalse((root / "derived").exists())

    def test_sequential_r0_a_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.make_fixture(root)
            spec_obj = json.loads(path.read_text())
            spec_obj["arms"] = {a: spec_obj["arms"][a] for a in ("R0", "A")}
            path.write_text(json.dumps(spec_obj))
            receipt = mod.run(path, root / "derived")
            self.assertEqual(set(receipt["runs"]), {"R0", "A"})

    def test_missing_fcd_second_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            fcd = root / "R0" / "outputs" / "fcd.xml"
            fcd.write_text(fcd.read_text().replace('<timestep time="5"></timestep>', '', 1))
            with self.assertRaisesRegex(ValueError, "Raw manifest mismatch"):
                mod.summarize_run("R0", root / "R0" / "outputs", root / "R0" / "demand.rou.xml")


if __name__ == "__main__":
    unittest.main()
