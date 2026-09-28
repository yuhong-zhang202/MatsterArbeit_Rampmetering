from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import reviewed_attribution_interface as ai


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class ReviewedAttributionInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.provenance = {"run_id": "SYNTH_RUN", "method_sha256": "1" * 64,
                           "locked_analyzer_sha256": "2" * 64,
                           "event_source_sha256": "3" * 64}
        self.event = {"event_id": "e01", "cell": 13, "onset_lower": 600,
                      "onset_upper": 630, "confirmation": 690, "end": 720,
                      "locked_P_status": "NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW",
                      "local_reference_status": "PASS", "numerical_gates": {"speed": True},
                      "locked_numerical_positive": True, "locked_reference_pass": True,
                      "locked_population_pass": True,
                      "locked_attribution_original": "UNRESOLVED"}
        self.evidence_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.evidence_tmp.cleanup)
        self.evidence_root = Path(self.evidence_tmp.name)
        evidence = self.evidence_root / "review.txt"
        evidence.write_text("synthetic reviewed evidence")
        self.evidence_path = str(evidence)
        self.evidence_hash = hashlib.sha256(evidence.read_bytes()).hexdigest()

    @staticmethod
    def verifier(reviewer, payload, signature):
        # Test-only verifier. Production must inject the trusted project verifier.
        return reviewer == "independent-reviewer" and signature == hashlib.sha256(
            b"test-key:" + payload).hexdigest()

    def make_review(self, alt, status="CLEARED", *, event=None, bad_signature=False, bad_hash=False):
        event = event or self.event
        review = {"event_id": event["event_id"], "alternative": alt, "status": status,
                  "evidence_paths": [self.evidence_path],
                  "hashes": {self.evidence_path: "0" * 64 if bad_hash else self.evidence_hash},
                  "vehicle_ids": ["M_01"], "cell_lane": "cell=13;lane=merge_section_1",
                  "time_bounds": {"lower": 600, "upper": 630},
                  "reason": "Synthetic explicit adjudication", "reviewer": "independent-reviewer",
                  "reviewer_signature": "placeholder"}
        review["reviewer_signature"] = ("invalid" if bad_signature else
            hashlib.sha256(b"test-key:" + ai.signing_payload(
                review, self.provenance, ai.event_locked_digest(event))).hexdigest())
        return review

    def test_candidate_preserves_locked_fields_and_defaults_unknown(self):
        rows, receipt = ai.build_interface([self.event], self.provenance)
        self.assertEqual(len(rows), 4)
        self.assertEqual({r["status"] for r in rows}, {"UNKNOWN"})
        self.assertEqual({r["locked_attribution_original"] for r in rows}, {"UNRESOLVED"})
        self.assertEqual({r["adjudicated_P_status"] for r in rows},
                         {"NOT_ADJUDICATED_ATTRIBUTION_NOT_ALL_CLEARED"})
        self.assertEqual(ai.validate_receipt(rows, receipt, self.provenance), ("PASS", []))

    def test_explicit_unresolved_review_remains_unknown(self):
        review = {"event_id": "e01", "alternative": ai.ALTERNATIVES[0], "status": "UNKNOWN",
                  "reason": "Insufficient evidence", "reviewer": "reviewer-1"}
        rows, _ = ai.build_interface([self.event], self.provenance, [review])
        row = next(r for r in rows if r["alternative"] == ai.ALTERNATIVES[0])
        self.assertEqual(row["status"], "UNKNOWN")
        self.assertEqual(row["reviewed_attribution_status"], "REVIEW_NOT_ALL_CLEARED")

    def test_all_explicit_signed_clears_adjudicate_without_mutating_locked_result(self):
        reviews = [self.make_review(alt) for alt in ai.ALTERNATIVES]
        rows, receipt = ai.build_interface([self.event], self.provenance, reviews,
                                     evidence_root=self.evidence_root,
                                     signature_verifier=self.verifier)
        self.assertEqual({r["status"] for r in rows}, {"CLEARED"})
        self.assertEqual({r["adjudicated_P_status"] for r in rows},
                         {"RULE_GATES_SATISFIED_WITH_REVIEWED_ATTRIBUTION"})
        self.assertEqual({r["locked_attribution_original"] for r in rows}, {"UNRESOLVED"})
        self.assertEqual(ai.validate_receipt(rows, receipt, self.provenance,
                                             evidence_root=self.evidence_root,
                                             signature_verifier=self.verifier), ("PASS", []))
        blocked = dict(self.event, locked_population_pass=False)
        blocked_reviews = [self.make_review(alt, event=blocked) for alt in ai.ALTERNATIVES]
        blocked_rows, _ = ai.build_interface([blocked], self.provenance, blocked_reviews,
                                             evidence_root=self.evidence_root,
                                             signature_verifier=self.verifier)
        self.assertEqual({r["adjudicated_P_status"] for r in blocked_rows},
                         {"NOT_ADJUDICATED_LOCKED_GATES_NOT_ALL_PASS"})

    def test_contradiction_does_not_auto_clear_other_explanations(self):
        reviews = [self.make_review(alt, "CONTRADICTED" if alt == ai.ALTERNATIVES[0] else "CLEARED")
                   for alt in ai.ALTERNATIVES]
        rows, _ = ai.build_interface([self.event], self.provenance, reviews,
                                     evidence_root=self.evidence_root,
                                     signature_verifier=self.verifier)
        self.assertEqual({r["adjudicated_P_status"] for r in rows},
                         {"NOT_ADJUDICATED_ATTRIBUTION_NOT_ALL_CLEARED"})
        self.assertEqual(sum(r["status"] == "CONTRADICTED" for r in rows), 1)

    def test_zero_event_receipt_is_complete_and_missing_is_unknown(self):
        rows, receipt = ai.build_interface([], self.provenance)
        self.assertEqual(rows, [])
        self.assertEqual(receipt["status"], "COMPLETE_BOUND_ZERO_EVENT")
        self.assertEqual(ai.validate_receipt(rows, receipt, self.provenance), ("PASS", []))
        self.assertEqual(ai.validate_receipt(rows, None, self.provenance),
                         ("UNKNOWN", ["ATTRIBUTION_RECEIPT_MISSING"]))
        with tempfile.TemporaryDirectory() as td:
            csv_path = Path(td) / "attribution_audit.csv"
            receipt_path = Path(td) / "attribution_receipt.json"
            written = ai.write_interface(csv_path, receipt_path, [], self.provenance)
            self.assertEqual(hashlib.sha256(csv_path.read_bytes()).hexdigest(), written["csv_sha256"])
            persisted = json.loads(receipt_path.read_text())
            self.assertEqual(ai.validate_receipt([], persisted, self.provenance), ("PASS", []))
            with self.assertRaises(FileExistsError):
                ai.write_interface(csv_path, receipt_path, [], self.provenance)

    def test_invalid_signature_or_evidence_hash_rejects_review(self):
        bad_signature = [self.make_review(ai.ALTERNATIVES[0], bad_signature=True)]
        with self.assertRaisesRegex(ValueError, "signature verification failed"):
            ai.build_interface([self.event], self.provenance, bad_signature,
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)
        bad_evidence = [self.make_review(ai.ALTERNATIVES[0], bad_hash=True)]
        with self.assertRaisesRegex(ValueError, "evidence hash mismatch"):
            ai.build_interface([self.event], self.provenance, bad_evidence,
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)

    def test_signature_is_bound_to_run_source_and_locked_event(self):
        reviews = [self.make_review(alt) for alt in ai.ALTERNATIVES]
        changed = dict(self.provenance, run_id="OTHER_RUN", event_source_sha256="4" * 64)
        with self.assertRaisesRegex(ValueError, "signature verification failed"):
            ai.build_interface([self.event], changed, reviews,
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)
        altered_event = dict(self.event, cell=14)
        with self.assertRaisesRegex(ValueError, "signature verification failed"):
            ai.build_interface([altered_event], self.provenance, reviews,
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)

    def test_signed_relative_evidence_path_is_preserved_exactly(self):
        review = self.make_review(ai.ALTERNATIVES[0])
        review["evidence_paths"] = ["review.txt"]
        review["hashes"] = {"review.txt": self.evidence_hash}
        review["reviewer_signature"] = hashlib.sha256(
            b"test-key:" + ai.signing_payload(
                review, self.provenance, ai.event_locked_digest(self.event))).hexdigest()
        rows, _ = ai.build_interface([self.event], self.provenance, [review],
                                     evidence_root=self.evidence_root,
                                     signature_verifier=self.verifier)
        output = next(row for row in rows if row["alternative"] == ai.ALTERNATIVES[0])
        self.assertEqual(output["evidence_paths"], ["review.txt"])
        self.assertEqual(output["hashes"], {"review.txt": self.evidence_hash})

    def test_empty_vehicle_id_list_is_rejected_for_clearance(self):
        review = self.make_review(ai.ALTERNATIVES[0])
        review["vehicle_ids"] = []
        review["reviewer_signature"] = hashlib.sha256(
            b"test-key:" + ai.signing_payload(
                review, self.provenance, ai.event_locked_digest(self.event))).hexdigest()
        with self.assertRaisesRegex(ValueError, "nonempty explicit string list"):
            ai.build_interface([self.event], self.provenance, [review],
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)

    def test_event_order_is_canonical(self):
        second = dict(self.event, event_id="a00")
        rows, receipt = ai.build_interface([self.event, second], self.provenance)
        self.assertEqual([rows[0]["event_id"], rows[4]["event_id"]], ["a00", "e01"])
        self.assertEqual(ai.validate_receipt(rows, receipt, self.provenance), ("PASS", []))

    def test_duplicate_or_unbound_review_and_receipt_tampering_fail(self):
        review = self.make_review(ai.ALTERNATIVES[0])
        with self.assertRaisesRegex(ValueError, "duplicate review"):
            ai.build_interface([self.event], self.provenance, [review, review],
                               evidence_root=self.evidence_root,
                               signature_verifier=self.verifier)
        rows, receipt = ai.build_interface([self.event], self.provenance)
        receipt["run_id"] = "OTHER"
        status, reasons = ai.validate_receipt(rows, receipt, self.provenance)
        self.assertEqual(status, "UNKNOWN")
        self.assertIn("PROVENANCE_MISMATCH:run_id", reasons)

    def test_receipt_validator_rejects_forged_adjudication_even_with_rehashed_csv(self):
        rows, receipt = ai.build_interface([self.event], self.provenance)
        for row in rows:
            row["status"] = "CLEARED"
            row["reviewed_attribution_status"] = "ALL_ALTERNATIVES_CLEARED"
            row["adjudicated_P_status"] = "RULE_GATES_SATISFIED_WITH_REVIEWED_ATTRIBUTION"
        receipt["csv_sha256"] = hashlib.sha256(ai.csv_bytes(rows)).hexdigest()
        status, reasons = ai.validate_receipt(rows, receipt, self.provenance,
                                              evidence_root=self.evidence_root,
                                              signature_verifier=self.verifier)
        self.assertEqual(status, "UNKNOWN")
        self.assertTrue(any(reason.startswith("REVIEW_ROW_INVALID:e01:") for reason in reasons))


if __name__ == "__main__":
    unittest.main()
