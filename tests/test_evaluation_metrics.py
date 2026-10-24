"""
Unit tests for code/evaluation/metrics.py and evaluation harness correctness.
Tests each pure metric function on tiny hand-made inputs.
Asserts that dataset/sample_output.csv against itself yields 1.0 on all metrics.
Asserts that a corrupted copy drops metrics strictly below 1.0.
"""

import copy
from pathlib import Path
import unittest

from evaluation.main import load_output_cases
from evaluation.metrics import (
    compute_error_table,
    compute_field_level_accuracy,
    compute_lcs,
    compute_row_exact_match,
    compute_sequence_metrics,
    compute_status_metrics,
    compute_step_multiset_prf,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_OUTPUT_PATH = REPO_ROOT / "dataset" / "sample_output.csv"


class TestEvaluationMetrics(unittest.TestCase):
    def test_lcs_computation(self):
        s1 = ["A", "B", "C", "D"]
        s2 = ["A", "C", "D", "E"]
        lcs = compute_lcs(s1, s2)
        self.assertEqual(lcs, ["A", "C", "D"])

    def test_synthetic_status_metrics(self):
        truths = {
            "c1": {"deletion_status": "COMPLETE"},
            "c2": {"deletion_status": "INCOMPLETE"},
            "c3": {"deletion_status": "NOT_APPLICABLE"},
        }
        # 2 out of 3 correct
        preds = {
            "c1": {"deletion_status": "COMPLETE"},
            "c2": {"deletion_status": "COMPLETE"},  # wrong
            "c3": {"deletion_status": "NOT_APPLICABLE"},
        }
        res = compute_status_metrics(preds, truths)
        self.assertAlmostEqual(res["status_accuracy"], 2 / 3)
        self.assertEqual(res["confusion_matrix"]["COMPLETE"]["COMPLETE"], 1)
        self.assertEqual(res["confusion_matrix"]["INCOMPLETE"]["COMPLETE"], 1)
        self.assertEqual(res["confusion_matrix"]["NOT_APPLICABLE"]["NOT_APPLICABLE"], 1)

    def test_synthetic_row_exact_match(self):
        step_a = {"step_no": 1, "phase": "VERIFICATION", "system_id": "sys", "resource_id": "r1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev1"}
        step_b = {"step_no": 1, "phase": "VERIFICATION", "system_id": "sys", "resource_id": "r2", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev1"}

        truths = {
            "c1": {"deletion_status": "COMPLETE", "steps": [step_a]},
            "c2": {"deletion_status": "COMPLETE", "steps": [step_b]},
        }
        preds = {
            "c1": {"deletion_status": "COMPLETE", "steps": [step_a]},  # exact match
            "c2": {"deletion_status": "COMPLETE", "steps": [step_a]},  # wrong step
        }
        res = compute_row_exact_match(preds, truths)
        self.assertAlmostEqual(res["exact_match_rate"], 0.5)

    def test_synthetic_step_multiset_prf(self):
        s1 = {"phase": "FINDING", "system_id": "s", "resource_id": "r1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT"}
        s2 = {"phase": "FINDING", "system_id": "s", "resource_id": "r2", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT"}
        s3 = {"phase": "FINDING", "system_id": "s", "resource_id": "r3", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT"}

        truths = {"c1": {"steps": [s1, s2]}}
        preds = {"c1": {"steps": [s2, s3]}}

        res = compute_step_multiset_prf(preds, truths)
        # 1 match (s2) out of 2 pred -> P=0.5, 1 match out of 2 truth -> R=0.5, F1=0.5
        self.assertAlmostEqual(res["micro_precision"], 0.5)
        self.assertAlmostEqual(res["micro_recall"], 0.5)
        self.assertAlmostEqual(res["micro_f1"], 0.5)
        self.assertAlmostEqual(res["macro_f1"], 0.5)

    def test_synthetic_field_level_accuracy(self):
        # Steps align by (phase, system_id, resource_id, operation)
        t_step = {"step_no": 1, "phase": "VERIFICATION", "system_id": "sys", "resource_id": "r1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev1"}
        # Same key, but different evidence_id and step_no
        p_step = {"step_no": 2, "phase": "VERIFICATION", "system_id": "sys", "resource_id": "r1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev2"}

        truths = {"c1": {"steps": [t_step]}}
        preds = {"c1": {"steps": [p_step]}}

        res = compute_field_level_accuracy(preds, truths)
        self.assertEqual(res["aligned_count"], 1)
        self.assertAlmostEqual(res["field_accuracies"]["operation"], 1.0)
        self.assertAlmostEqual(res["field_accuracies"]["state"], 1.0)
        self.assertAlmostEqual(res["field_accuracies"]["evidence_id"], 0.0)
        self.assertAlmostEqual(res["field_accuracies"]["step_no"], 0.0)

    def test_synthetic_sequence_metrics(self):
        s1 = {"phase": "VERIFICATION", "system_id": "s", "resource_id": "r1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT"}
        s2 = {"phase": "VERIFICATION", "system_id": "s", "resource_id": "r2", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT"}

        # Case 1: reversed order
        truths = {"c1": {"steps": [s1, s2]}}
        preds = {"c1": {"steps": [s2, s1]}}

        res = compute_sequence_metrics(preds, truths)
        self.assertAlmostEqual(res["exact_order_rate"], 0.0)
        # LCS between [s1, s2] and [s2, s1] is length 1. Ratio = 2*1 / (2+2) = 0.5
        self.assertAlmostEqual(res["mean_lcs_ratio"], 0.5)

    def test_sample_output_against_itself(self):
        """Assert sample_output.csv against itself scores exactly 1.0 on all metrics."""
        cases = load_output_cases(SAMPLE_OUTPUT_PATH)
        self.assertEqual(len(cases), 32)

        status_res = compute_status_metrics(cases, cases)
        self.assertEqual(status_res["status_accuracy"], 1.0)

        exact_res = compute_row_exact_match(cases, cases)
        self.assertEqual(exact_res["exact_match_rate"], 1.0)

        step_prf = compute_step_multiset_prf(cases, cases)
        self.assertEqual(step_prf["micro_precision"], 1.0)
        self.assertEqual(step_prf["micro_recall"], 1.0)
        self.assertEqual(step_prf["micro_f1"], 1.0)
        self.assertEqual(step_prf["macro_f1"], 1.0)

        field_acc = compute_field_level_accuracy(cases, cases)
        for field, acc in field_acc["field_accuracies"].items():
            self.assertEqual(acc, 1.0, f"Field {field} accuracy not 1.0")

        seq_metrics = compute_sequence_metrics(cases, cases)
        self.assertEqual(seq_metrics["exact_order_rate"], 1.0)
        self.assertEqual(seq_metrics["mean_lcs_ratio"], 1.0)

        errors = compute_error_table(cases, cases)
        self.assertEqual(len(errors), 0)

    def test_sample_output_against_corrupted_copy(self):
        """Assert corrupted sample copy causes metrics to drop strictly below 1.0."""
        truths = load_output_cases(SAMPLE_OUTPUT_PATH)
        corrupted = copy.deepcopy(truths)

        # Mutate case_01: change status to INCOMPLETE
        corrupted["case_01"]["deletion_status"] = "INCOMPLETE"

        # Mutate case_03: drop a step
        corrupted["case_03"]["steps"].pop()

        # Mutate case_05: swap order of steps
        if len(corrupted["case_05"]["steps"]) >= 2:
            corrupted["case_05"]["steps"][0], corrupted["case_05"]["steps"][1] = (
                corrupted["case_05"]["steps"][1],
                corrupted["case_05"]["steps"][0],
            )

        status_res = compute_status_metrics(corrupted, truths)
        self.assertLess(status_res["status_accuracy"], 1.0)

        exact_res = compute_row_exact_match(corrupted, truths)
        self.assertLess(exact_res["exact_match_rate"], 1.0)

        step_prf = compute_step_multiset_prf(corrupted, truths)
        self.assertLess(step_prf["micro_f1"], 1.0)

        seq_metrics = compute_sequence_metrics(corrupted, truths)
        self.assertLess(seq_metrics["exact_order_rate"], 1.0)

        errors = compute_error_table(corrupted, truths)
        self.assertGreater(len(errors), 0)

        # Test module error attribution
        from evaluation.metrics import compute_module_error_attribution, compute_email_breakdowns
        attr = compute_module_error_attribution(errors)
        self.assertIn("identity", attr)
        self.assertIn("rules", attr)
        self.assertGreater(sum(m["error_count"] for m in attr.values()), 0)

        # Test email breakdowns
        req_path = REPO_ROOT / "dataset" / "sample_deletion_requests.csv"
        if req_path.exists():
            email_bd = compute_email_breakdowns(truths, truths, req_path)
            self.assertIn("Current Email", email_bd)
            self.assertIn("Historical Email Alias", email_bd)
            self.assertEqual(email_bd["Current Email"]["status_acc"], 1.0)
            self.assertEqual(email_bd["Historical Email Alias"]["status_acc"], 1.0)


if __name__ == "__main__":
    unittest.main()

