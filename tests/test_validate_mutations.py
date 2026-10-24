"""
Mutation tests for code/ghost_audit/validate.py.
Loads dataset/sample_output.csv in memory and applies ONE mutation at a time.
Asserts that the validator raises the expected rule_id and no unrelated ERROR.
Reports in the test output which mutation was caught by which rule.
"""

import copy
import csv
import json
from pathlib import Path
import tempfile
import unittest

from ghost_audit.validate import validate_output

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_OUTPUT_PATH = REPO_ROOT / "dataset" / "sample_output.csv"
SAMPLE_REQUESTS_PATH = REPO_ROOT / "dataset" / "sample_deletion_requests.csv"
MANIFEST_PATH = REPO_ROOT / "dataset" / "evidence_files.csv"


class TestValidateMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SAMPLE_OUTPUT_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            cls.header = next(reader)
            cls.baseline_rows = list(reader)

    def _run_validation(self, mutated_rows: list[list[str]], expected_rows: int | None = 32) -> list:
        with tempfile.TemporaryDirectory() as td:
            temp_out = Path(td) / "mutated_output.csv"
            with open(temp_out, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.header)
                writer.writerows(mutated_rows)

            violations = validate_output(
                path=temp_out,
                requests_path=SAMPLE_REQUESTS_PATH,
                evidence_manifest_path=MANIFEST_PATH,
                expected_rows=expected_rows,
                id_sort="lexical",
            )
            return violations

    def assert_mutation_caught(
        self, mutation_name: str, mutated_rows: list[list[str]], expected_rule: str, expected_rows: int | None = 32
    ):
        violations = self._run_validation(mutated_rows, expected_rows=expected_rows)
        errors = [v for v in violations if v.severity == "ERROR"]
        error_rules = {e.rule_id for e in errors}

        # Assert expected rule is present
        self.assertIn(
            expected_rule,
            error_rules,
            f"Mutation '{mutation_name}' did not trigger expected error {expected_rule}. Found errors: {error_rules}",
        )

        # Assert no unrelated error rules
        unrelated = error_rules - {expected_rule}
        self.assertEqual(
            unrelated,
            set(),
            f"Mutation '{mutation_name}' triggered unrelated errors: {unrelated}",
        )

        caught_viols = [e for e in errors if e.rule_id == expected_rule]
        print(f"[MUTATION CAUGHT] {mutation_name:<50} -> Rule {expected_rule} ({caught_viols[0].message[:70]}...)")

    def test_mutation_01_drop_step_gap(self):
        # Case_03 has 3 steps (step_no 1, 2, 3). Drop step 2.
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_03":
                steps = json.loads(r[2])
                del steps[1]  # drops step 2; remaining have step_no 1 and 3
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("drop a step (step_no gap)", mutated, "V05")

    def test_mutation_02_swap_two_steps_phase_order(self):
        # Case_05 is INCOMPLETE with FINDING, REMEDIATION, VERIFICATION.
        # Swap step 0 (FINDING) and step 3 (VERIFICATION).
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_05":
                steps = json.loads(r[2])
                # swap phase order
                steps[0]["phase"], steps[-1]["phase"] = steps[-1]["phase"], steps[0]["phase"]
                steps[0]["operation"], steps[-1]["operation"] = steps[-1]["operation"], steps[0]["operation"]
                steps[0]["state"], steps[-1]["state"] = steps[-1]["state"], steps[0]["state"]
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("swap two steps (non-monotonic phase)", mutated, "V07")

    def test_mutation_03_illegal_operation_state_pair(self):
        # Case_01: change state of VERIFY_RECORD_ABSENT to PRESENT
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                steps = json.loads(r[2])
                steps[0]["state"] = "PRESENT"  # illegal pair
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("change operation to illegal pair", mutated, "V08")

    def test_mutation_04_complete_empty_evidence_id(self):
        # Case_01: set evidence_id to "" on COMPLETE row
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                steps = json.loads(r[2])
                steps[0]["evidence_id"] = ""
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("set COMPLETE row evidence_id to empty", mutated, "V13")

    def test_mutation_05_future_evidence_id(self):
        # Case_01 has audit_at 2026-09-03. Evidence_03 is captured at 2026-10-01T12:00:00Z.
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                steps = json.loads(r[2])
                steps[0]["evidence_id"] = "evidence_03"
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("set future evidence_id (captured_at > audit_at)", mutated, "V10")

    def test_mutation_06_add_unknown_field(self):
        # Case_01: add unknown field 'extra_token'
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                steps = json.loads(r[2])
                steps[0]["extra_token"] = "unknown"
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("add unknown field to step", mutated, "V06")

    def test_mutation_07_status_complete_to_not_applicable_with_steps(self):
        # Case_01: change status to NOT_APPLICABLE without clearing steps
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                r[1] = "NOT_APPLICABLE"
                break
        self.assert_mutation_caught("status NOT_APPLICABLE without clearing steps", mutated, "V12")

    def test_mutation_08_duplicate_case_row(self):
        # Duplicate case_01 row
        mutated = copy.deepcopy(self.baseline_rows)
        mutated.insert(1, copy.deepcopy(mutated[0]))
        self.assert_mutation_caught("duplicate a case row", mutated, "V02", expected_rows=None)

    def test_mutation_09_unsort_rows(self):
        # Swap case_01 and case_02
        mutated = copy.deepcopy(self.baseline_rows)
        mutated[0], mutated[1] = mutated[1], mutated[0]
        self.assert_mutation_caught("unsort the rows", mutated, "V03")

    def test_mutation_10_evidence_id_not_in_manifest(self):
        # Case_01: evidence_NONEXISTENT_999
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                steps = json.loads(r[2])
                steps[0]["evidence_id"] = "evidence_NONEXISTENT_999"
                r[2] = json.dumps(steps)
                break
        self.assert_mutation_caught("use evidence_id not in manifest", mutated, "V09")

    def test_mutation_11_invalidate_json(self):
        # Case_01: invalid JSON string
        mutated = copy.deepcopy(self.baseline_rows)
        for r in mutated:
            if r[0] == "case_01":
                r[2] = "{not valid json"
                break
        self.assert_mutation_caught("invalidate steps_json", mutated, "V04")


if __name__ == "__main__":
    unittest.main()
