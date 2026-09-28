import copy
import importlib.util
import json
from pathlib import Path
import unittest



ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "artifacts/stage6_minimal3350_control_preparation_20260924_rev8"
CARD_PATH = PACKAGE / "MINIMAL3350_CTRL_S17_CARD_FINAL.json"
DEMAND_PATH = PACKAGE / "inputs/control/demand.rou.xml"
COMMON_PATH = PACKAGE / "COMMON_M_DEMAND_MANIFEST.json"
REQUEST_PATH = PACKAGE / "START_REQUEST.json"
RUNNER_PATH = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
ADAPTER_PATH = ROOT / "scripts/stage6/minimal3350/minimal3350_control_adapter.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class Minimal3350BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.runner = load_module("r02_minimal3350_test", RUNNER_PATH)
        cls.adapter = load_module("adapter_minimal3350_test", ADAPTER_PATH)


    def test_valid_3350_exact_card_and_guardian_request(self):
        card_check = self.adapter.validate_control_card(self.card, DEMAND_PATH, COMMON_PATH, ROOT)
        self.assertEqual(card_check["status"], "PASS")
        self.assertEqual(self.runner.validate_guardian_start_request(
            self.request, self.runner.REPO_ROOT, require_reviews=False)["kind"], "PAIR_RUN")


    def test_guardian_request_invalid_variants_fail_closed(self):
        for mutation in ("missing", "extra", "wrong_type", "wrong_path", "wrong_run_id", "wrong_runtime_hash",
                         "wrong_resource_limit", "wrong_schema_hash"):
            with self.subTest(mutation=mutation):
                request = copy.deepcopy(self.request)
                if mutation == "missing":
                    request.pop("reservation_path")
                elif mutation == "extra":
                    request["unexpected"] = "x"
                elif mutation == "wrong_type":
                    request["max_runtime_s"] = "90"
                elif mutation == "wrong_path":
                    request["output_directory"] = str(ROOT / "data/raw/unbound/outputs")
                elif mutation == "wrong_run_id":
                    request["run_id"] = "MINIMAL3199_CTRL_S17"
                elif mutation == "wrong_runtime_hash":
                    request["runtime_binding_sha256"] = "0" * 64
                elif mutation == "wrong_resource_limit":
                    request["max_output_bytes"] = 60_000_001
                elif mutation == "wrong_schema_hash":
                    request["additional_schema_sha256"] = "0" * 64
                with self.assertRaises(self.runner.GateError):
                    self.runner.validate_guardian_start_request(request, self.runner.REPO_ROOT, require_reviews=False)


    def test_control_card_invariant_mutations_fail_closed(self):
        for mutation in ("qmain", "m_count", "u_missing", "output_path", "runtime_hash"):
            with self.subTest(mutation=mutation):
                altered = copy.deepcopy(self.card)
                if mutation == "qmain":
                    altered["qMain_veh_per_h"] = 3350.0
                elif mutation == "m_count":
                    altered["class_counts"]["M"]["planned_count"] = 1395
                elif mutation == "u_missing":
                    del altered["class_counts"]["U"]
                elif mutation == "output_path":
                    altered["output_directory"] = "data/raw/wrong/outputs"
                elif mutation == "runtime_hash":
                    altered["runtime_binding"]["guardian_runner_sha256"] = "0" * 64
                with self.assertRaises(ValueError):
                    self.adapter.validate_control_card(altered, DEMAND_PATH, COMMON_PATH, ROOT)


    def test_materialized_common_m_schedule_and_ids(self):
        result = self.adapter.verify_demand(DEMAND_PATH)
        self.assertEqual(result["m_count"], 1396)
        self.assertEqual(result["m_ids"], 1396)
        self.assertEqual(result["schedule_offset_ms"], 1074)
        self.assertEqual(result["last_depart_ms"], 1_498_230)
        self.assertTrue(self.adapter.verify_common_manifest(
            COMMON_PATH, DEMAND_PATH, expected_sha256=self.adapter.sha256(COMMON_PATH))["matches_demand"])

    def test_every_configured_output_resolves_to_runner_bound_directory(self):
        result = self.adapter.verify_output_bindings(
            PACKAGE / "inputs/control/scenario.sumocfg",
            PACKAGE / "inputs/control/scenario.add.xml",
            PACKAGE / "inputs/control/output_roles.json",
            ROOT / self.card["output_directory"],
        )
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["all_targets_match"])
        self.assertEqual(result["role_paths"], 18)
        self.assertEqual(result["sumocfg_targets"], 8)
        self.assertEqual(result["additional_targets"], 12)

    def test_duplicated_raw_prefix_fails_closed(self):
        cfg = PACKAGE / "inputs/control/scenario.sumocfg"
        text = cfg.read_text(encoding="utf-8")
        altered = cfg.with_name("scenario.bad.sumocfg")
        altered.write_text(text.replace("/data/raw/stage6_minimal3350_ux0_20260924_v8/",
                                       "/data/raw/data/raw/stage6_minimal3350_ux0_20260924_v8/"),
                          encoding="utf-8")
        try:
            with self.assertRaises(ValueError):
                self.adapter.verify_output_bindings(
                    altered, PACKAGE / "inputs/control/scenario.add.xml",
                    PACKAGE / "inputs/control/output_roles.json",
                    ROOT / self.card["output_directory"],
                )
        finally:
            altered.unlink(missing_ok=True)

    def test_review_receipt_schemas_are_normalized_fail_closed(self):
        card_hash = "a" * 64
        base = {"run_id": "MINIMAL3350_CTRL_S17", "card_sha256": card_hash,
                "findings": {"blocker": 0, "major": 0, "required_minor": 0}}
        receipts = {
            "engineering": dict(base, schema="stage6_engineering_prelaunch_review_v1", status="PASS_PRELAUNCH"),
            "data_provenance": dict(base, schema="stage6_minimal3350_data_provenance_prelaunch_review_v2",
                                     status="PASS_DATA_PROVENANCE_PRELAUNCH"),
            "scientific": dict(base, schema="stage6_minimal3350_scientific_prelaunch_review_v1",
                               disposition="PASS_PRELAUNCH"),
        }
        for role, receipt in receipts.items():
            with self.subTest(role=role):
                self.assertTrue(self.runner.minimal3350_review_receipt_valid(
                    role, receipt, "MINIMAL3350_CTRL_S17", card_hash))
                for field, value in (("run_id", "wrong"), ("card_sha256", "0" * 64)):
                    mutated = copy.deepcopy(receipt)
                    mutated[field] = value
                    self.assertFalse(self.runner.minimal3350_review_receipt_valid(
                        role, mutated, "MINIMAL3350_CTRL_S17", card_hash))
                malformed = copy.deepcopy(receipt)
                malformed.pop("schema")
                self.assertFalse(self.runner.minimal3350_review_receipt_valid(
                    role, malformed, "MINIMAL3350_CTRL_S17", card_hash))
                bad_findings = copy.deepcopy(receipt)
                bad_findings["findings"]["major"] = True
                self.assertFalse(self.runner.minimal3350_review_receipt_valid(
                    role, bad_findings, "MINIMAL3350_CTRL_S17", card_hash))
        newer_data = copy.deepcopy(receipts["data_provenance"])
        newer_data["schema"] = "stage6_minimal3350_data_provenance_prelaunch_review_v3"
        self.assertTrue(self.runner.minimal3350_review_receipt_valid(
            "data_provenance", newer_data, "MINIMAL3350_CTRL_S17", card_hash))
        unsupported_schema = copy.deepcopy(newer_data)
        unsupported_schema["schema"] = "stage6_minimal3350_data_provenance_prelaunch_review_v99"
        self.assertFalse(self.runner.minimal3350_review_receipt_valid(
            "data_provenance", unsupported_schema, "MINIMAL3350_CTRL_S17", card_hash))
        wrong_status = copy.deepcopy(receipts["data_provenance"])
        wrong_status["status"] = "PASS"
        self.assertFalse(self.runner.minimal3350_review_receipt_valid(
            "data_provenance", wrong_status, "MINIMAL3350_CTRL_S17", card_hash))
        missing = copy.deepcopy(receipts["scientific"])
        missing.pop("disposition")
        self.assertFalse(self.runner.minimal3350_review_receipt_valid(
            "scientific", missing, "MINIMAL3350_CTRL_S17", card_hash))

    def test_review_sidecar_receipt_hashes_fail_closed(self):
        expected = {"engineering": "a" * 64, "data_provenance": "b" * 64, "scientific": "c" * 64}
        sidecar = {"status": "FINAL_PRELAUNCH_REVIEW_GATE_PASS", "run_id": "MINIMAL3350_CTRL_S17",
                   "card_sha256": "d" * 64, "review_receipt_sha256": expected}
        self.assertTrue(self.runner.minimal3350_review_sidecar_valid(
            sidecar, "MINIMAL3350_CTRL_S17", "d" * 64, expected))
        for field in ("card_sha256", "status", "review_receipt_sha256"):
            mutated = copy.deepcopy(sidecar)
            if field == "review_receipt_sha256":
                mutated[field]["data_provenance"] = "0" * 64
            else:
                mutated[field] = "wrong"
            self.assertFalse(self.runner.minimal3350_review_sidecar_valid(
                mutated, "MINIMAL3350_CTRL_S17", "d" * 64, expected))

    def test_start_request_uses_r02_canonical_bytes_and_rejects_pretty_digest(self):
        request = {"run_id": "MINIMAL3350_CTRL_S17", "action": "START", "max_output_bytes": 60000000}
        canonical = self.adapter.canonical_start_request_bytes(request, self.runner)
        pretty = (json.dumps(request, indent=2, sort_keys=True) + "\n").encode("utf-8")
        self.assertNotEqual(pretty, canonical)
        canonical_hash = self.adapter.hashlib.sha256(canonical).hexdigest()
        pretty_hash = self.adapter.hashlib.sha256(pretty).hexdigest()
        self.assertTrue(self.adapter.start_request_receipt_matches(request, canonical, canonical_hash, self.runner))
        self.assertFalse(self.adapter.start_request_receipt_matches(request, pretty, pretty_hash, self.runner))


if __name__ == "__main__":
    unittest.main()
