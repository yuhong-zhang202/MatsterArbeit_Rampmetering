"""Static engineering gates; never start SUMO."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts/stage6/boundary_search_20261002/runner.py"
SPEC = importlib.util.spec_from_file_location("boundary_runner", MODULE)
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


class DemandTests(unittest.TestCase):
    def test_common_attributes_invariant(self):
        a = {v["id"]: v for v in r.vehicle_records(3000, 0, 17)}
        b = {v["id"]: v for v in r.vehicle_records(3000, 1200, 17)}
        self.assertTrue(all(b[k] == v for k,v in a.items()))
        self.assertEqual(sum(k.startswith("M_") for k in a), 2500)
        self.assertEqual(sum(k.startswith("U_") for k in a), 300)
        self.assertEqual(sum(k.startswith("X_") for k in a), 150)
        self.assertEqual(sum(k.startswith("R_") for k in b), 800)

    def test_schedule_and_seed(self):
        rows = r.vehicle_records(2400, 600, 17)
        ramp = [v for v in rows if v["id"].startswith("R_")]
        self.assertEqual(ramp[0]["depart"], "600.000")
        self.assertLess(float(ramp[-1]["depart"]), 3000)
        self.assertNotEqual(r.speed_factor(17,"M",0),r.speed_factor(23,"M",0))
        self.assertEqual([float(v["depart"]) for v in rows], sorted(float(v["depart"]) for v in rows))

    def test_rounding_refused(self):
        with self.assertRaises(ValueError): r.vehicle_records(2401,600,17)


class GatesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.patch_raw=patch.object(r,"RAW",self.root/"raw")
        self.patch_packages=patch.object(r,"PACKAGES",self.root/"inputs")
        self.patch_raw.start(); self.patch_packages.start()
        self.plan=self.root/"plan.md"
        self.plan.write_text("Exploratory test only")

    def tearDown(self):
        self.patch_raw.stop(); self.patch_packages.stop(); self.temp.cleanup()

    def prepared(self):
        return r.prepare("TEST_M2400_R600_S17",2400,600,17,self.plan)

    def test_prepare_preflight_and_no_raw(self):
        p=self.prepared()
        card=r.preflight(p["card"],p["card_sha256"])
        self.assertEqual(card["counts"],{"M":2000,"R":400,"U":300,"X":150})
        self.assertFalse(r.RAW.exists())
        with self.assertRaises(FileExistsError): self.prepared()

    def test_tampered_input_refused(self):
        p=self.prepared()
        (Path(p["card"]).parent/"demand.rou.xml").write_text("bad")
        with self.assertRaises(ValueError): r.preflight(p["card"],p["card_sha256"])

    def test_release_must_bind_exact_card(self):
        p=self.prepared()
        release=self.root/"release.json"
        release.write_text(json.dumps({"status":"PASS_FOR_EXPLORATORY_EXECUTION","cards":{}}))
        with self.assertRaises(ValueError): r.preflight(p["card"],p["card_sha256"],release)

    def test_consumed_reservation_refused(self):
        p=self.prepared()
        reservations=r.PACKAGES/"reservations"
        reservations.mkdir()
        (reservations/"TEST_M2400_R600_S17.json").write_text("{}")
        with self.assertRaises(FileExistsError): r.preflight(p["card"],p["card_sha256"])

    def test_global_start_cap(self):
        p=self.prepared()
        reservations=r.PACKAGES/"reservations"
        reservations.mkdir()
        for i in range(r.MAX_STARTS): (reservations/f"old{i}.json").write_text("{}")
        with self.assertRaises(ValueError): r.preflight(p["card"],p["card_sha256"])


if __name__=="__main__": unittest.main()
