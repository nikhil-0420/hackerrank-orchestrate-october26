"""
Unit tests for code/ghost_audit/validate.py.
Uses ONLY tiny synthetic hand-made inputs (no dataset files).
Tests each error rule (V01-V14) and warning rule (W01-W06) with good and bad examples.
"""

import json
from pathlib import Path
import tempfile
import unittest

from ghost_audit.spec import OUTPUT_HEADER
from ghost_audit.validate import (
    Violation,
    check_case_sorting,
    check_complete_rule,
    check_header,
    check_incomplete_finding_rule,
    check_not_applicable_rule,
    check_requests_alignment,
    check_status_validity,
    check_steps_structure_and_order,
    check_warn_conventions,
    validate_output,
)


class TestValidatePureRules(unittest.TestCase):
    def test_v01_header(self):
        # Good
        self.assertEqual(check_header(OUTPUT_HEADER), [])
        # Bad
        bad_header = ["case_id", "status", "steps"]
        res = check_header(bad_header)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].rule_id, "V01")
        self.assertEqual(res[0].severity, "ERROR")

    def test_v02_requests_alignment(self):
        # Good
        self.assertEqual(check_requests_alignment(["c1", "c2"], ["c1", "c2"], expected_rows=2), [])
        # Bad: Missing row, extra row, duplicate row, wrong count
        res = check_requests_alignment(["c1", "c1", "c3"], ["c1", "c2"], expected_rows=2)
        rule_ids = [v.rule_id for v in res]
        self.assertIn("V02", rule_ids)
        # Should catch count mismatch, duplicate c1, missing c2, extra c3
        self.assertTrue(any("Duplicate" in v.message for v in res))
        self.assertTrue(any("Missing" in v.message for v in res))
        self.assertTrue(any("Extra" in v.message for v in res))

    def test_v03_case_sorting(self):
        # Good
        self.assertEqual(check_case_sorting(["c1", "c2", "c3"], id_sort="lexical"), [])
        # Bad
        res = check_case_sorting(["c2", "c1", "c3"], id_sort="lexical")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].rule_id, "V03")

    def test_v04_steps_json_parsing(self):
        # Handled in validate_output; let's test via a small synthetic file
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "out.csv"
            req_file = Path(td) / "req.csv"
            man_file = Path(td) / "man.csv"
            req_file.write_text("case_id,audit_at\nc1,2026-09-01T00:00:00Z\n", encoding="utf-8")
            man_file.write_text("file_id,captured_at\n", encoding="utf-8")

            # Corrupt JSON
            out_file.write_text(
                "case_id,deletion_status,steps_json\nc1,COMPLETE,{not-json}\n", encoding="utf-8"
            )
            v = validate_output(out_file, req_file, man_file)
            self.assertTrue(any(x.rule_id == "V04" for x in v))

            # Not an array
            out_file.write_text(
                "case_id,deletion_status,steps_json\nc1,COMPLETE,{\"step_no\": 1}\n", encoding="utf-8"
            )
            v = validate_output(out_file, req_file, man_file)
            self.assertTrue(any(x.rule_id == "V04" for x in v))

    def test_v05_step_no_sequence(self):
        manifest = {}
        # Good
        good_steps = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            }
        ]
        self.assertEqual(check_steps_structure_and_order("c1", good_steps, manifest, "2026-09-01T00:00:00Z"), [])

        # Bad: gap (starts at 2)
        bad_steps = [
            {
                "step_no": 2,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_steps, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V05" for v in res))

    def test_v06_exact_step_fields(self):
        manifest = {}
        # Bad: missing 'evidence_id', extra 'foo'
        bad_step = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "foo": "bar",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_step, manifest, "2026-09-01T00:00:00Z")
        v06 = [v for v in res if v.rule_id == "V06"]
        self.assertEqual(len(v06), 1)
        self.assertIn("missing", v06[0].message)
        self.assertIn("extra", v06[0].message)

    def test_v07_phase_allowed_and_monotonic(self):
        manifest = {}
        # Bad: invalid phase
        bad_phase = [
            {
                "step_no": 1,
                "phase": "UNKNOWN_PHASE",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_phase, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V07" for v in res))

        # Bad: non-monotonic (VERIFICATION then FINDING)
        bad_order = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            },
            {
                "step_no": 2,
                "phase": "FINDING",
                "system_id": "account_service",
                "resource_id": "acc_2",
                "operation": "REPORT_REMAINING_RECORD",
                "state": "PRESENT",
                "evidence_id": "",
            },
        ]
        res = check_steps_structure_and_order("c1", bad_order, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V07" for v in res))

    def test_v08_operation_state_legal_pair(self):
        manifest = {}
        # Bad: illegal state for operation
        bad_pair = [
            {
                "step_no": 1,
                "phase": "FINDING",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "REPORT_REMAINING_RECORD",
                "state": "ABSENT",  # should be PRESENT
                "evidence_id": "",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_pair, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V08" for v in res))

        # Bad: operation belonging to different phase
        bad_op_phase = [
            {
                "step_no": 1,
                "phase": "FINDING",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",  # belongs to VERIFICATION
                "state": "ABSENT",
                "evidence_id": "",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_op_phase, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V08" for v in res))

    def test_v09_evidence_id_in_manifest(self):
        manifest = {"ev_1": "2026-08-01T00:00:00Z"}
        # Good: empty
        good_empty = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            }
        ]
        self.assertEqual(check_steps_structure_and_order("c1", good_empty, manifest, "2026-09-01T00:00:00Z"), [])

        # Good: in manifest
        good_ev = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "ev_1",
            }
        ]
        self.assertEqual(check_steps_structure_and_order("c1", good_ev, manifest, "2026-09-01T00:00:00Z"), [])

        # Bad: unknown evidence id
        bad_ev = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "ev_UNKNOWN",
            }
        ]
        res = check_steps_structure_and_order("c1", bad_ev, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V09" for v in res))

    def test_v10_evidence_timegate(self):
        manifest = {"ev_future": "2026-10-01T00:00:00Z"}
        bad_time = [
            {
                "step_no": 1,
                "phase": "VERIFICATION",
                "system_id": "account_service",
                "resource_id": "acc_1",
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "ev_future",
            }
        ]
        # audit_at is earlier than captured_at
        res = check_steps_structure_and_order("c1", bad_time, manifest, "2026-09-01T00:00:00Z")
        self.assertTrue(any(v.rule_id == "V10" for v in res))

    def test_v11_status_validity(self):
        self.assertEqual(check_status_validity("c1", "COMPLETE"), [])
        res = check_status_validity("c1", "INVALID_STATUS")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].rule_id, "V11")

    def test_v12_not_applicable_steps(self):
        step = {
            "step_no": 1,
            "phase": "VERIFICATION",
            "system_id": "account_service",
            "resource_id": "acc_1",
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": "",
        }
        # Good NOT_APPLICABLE
        self.assertEqual(check_not_applicable_rule("c1", "NOT_APPLICABLE", []), [])
        # Bad: NOT_APPLICABLE with steps
        res = check_not_applicable_rule("c1", "NOT_APPLICABLE", [step])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].rule_id, "V12")

        # Bad: COMPLETE with empty steps
        res2 = check_not_applicable_rule("c1", "COMPLETE", [])
        self.assertEqual(len(res2), 1)
        self.assertEqual(res2[0].rule_id, "V12")

    def test_v13_complete_rule(self):
        good_ver = {
            "step_no": 1,
            "phase": "VERIFICATION",
            "system_id": "account_service",
            "resource_id": "acc_1",
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": "ev_1",
        }
        self.assertEqual(check_complete_rule("c1", "COMPLETE", [good_ver]), [])

        # Bad: non-VERIFICATION step
        finding_step = {
            "step_no": 1,
            "phase": "FINDING",
            "system_id": "account_service",
            "resource_id": "acc_1",
            "operation": "REPORT_REMAINING_RECORD",
            "state": "PRESENT",
            "evidence_id": "ev_1",
        }
        res = check_complete_rule("c1", "COMPLETE", [finding_step])
        self.assertTrue(any(v.rule_id == "V13" for v in res))

        # Bad: empty evidence_id
        empty_ev = dict(good_ver, evidence_id="")
        res2 = check_complete_rule("c1", "COMPLETE", [empty_ev])
        self.assertTrue(any(v.rule_id == "V13" for v in res2))

    def test_v14_incomplete_finding_rule(self):
        finding_step = {
            "step_no": 1,
            "phase": "FINDING",
            "system_id": "account_service",
            "resource_id": "acc_1",
            "operation": "REPORT_REMAINING_RECORD",
            "state": "PRESENT",
            "evidence_id": "ev_1",
        }
        self.assertEqual(check_incomplete_finding_rule("c1", "INCOMPLETE", [finding_step]), [])

        # Bad: INCOMPLETE with no findings
        ver_step = {
            "step_no": 1,
            "phase": "VERIFICATION",
            "system_id": "account_service",
            "resource_id": "acc_1",
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": "",
        }
        res = check_incomplete_finding_rule("c1", "INCOMPLETE", [ver_step])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].rule_id, "V14")

    def test_w01_incomplete_evidence_id(self):
        # Good: empty evidence_id on remediation and verification
        good_steps = [
            {"step_no": 1, "phase": "FINDING", "system_id": "account_service", "resource_id": "acc_1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "REMEDIATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": ""},
            {"step_no": 3, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
        ]
        self.assertEqual(check_warn_conventions("c1", "INCOMPLETE", good_steps), [])

        # Bad: non-empty evidence_id on REMEDIATION
        bad_steps = [
            {"step_no": 1, "phase": "FINDING", "system_id": "account_service", "resource_id": "acc_1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "REMEDIATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": "ev_2"},
            {"step_no": 3, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
        ]
        res = check_warn_conventions("c1", "INCOMPLETE", bad_steps)
        self.assertTrue(any(v.rule_id == "W01" for v in res))

    def test_w02_matching_chains(self):
        # Bad: Finding without remediation
        bad_steps = [
            {"step_no": 1, "phase": "FINDING", "system_id": "account_service", "resource_id": "acc_1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
        ]
        res = check_warn_conventions("c1", "INCOMPLETE", bad_steps)
        self.assertTrue(any(v.rule_id == "W02" for v in res))

    def test_w03_step_ordering(self):
        # Bad: DELETE_RECORD before DISABLE_DATA_FLOW in REMEDIATION phase
        bad_order = [
            {"step_no": 1, "phase": "FINDING", "system_id": "account_service", "resource_id": "acc_1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "FINDING", "system_id": "event_stream", "resource_id": "flow_1", "operation": "REPORT_ACTIVE_DATA_FLOW", "state": "ACTIVE", "evidence_id": "ev_1"},
            {"step_no": 3, "phase": "REMEDIATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": ""},
            {"step_no": 4, "phase": "REMEDIATION", "system_id": "event_stream", "resource_id": "flow_1", "operation": "DISABLE_DATA_FLOW", "state": "DISABLED", "evidence_id": ""},
            {"step_no": 5, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
            {"step_no": 6, "phase": "VERIFICATION", "system_id": "event_stream", "resource_id": "flow_1", "operation": "VERIFY_DATA_FLOW_DISABLED", "state": "DISABLED", "evidence_id": ""},
        ]
        res = check_warn_conventions("c1", "INCOMPLETE", bad_order)
        self.assertTrue(any(v.rule_id == "W03" for v in res))

    def test_w04_duplicate_steps(self):
        dup_steps = [
            {"step_no": 1, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": "ev_1"},
        ]
        res = check_warn_conventions("c1", "COMPLETE", dup_steps)
        self.assertTrue(any(v.rule_id == "W04" for v in res))

    def test_w05_remediation_on_retain_resource(self):
        # Remediation deleting a security audit log
        retain_steps = [
            {"step_no": 1, "phase": "FINDING", "system_id": "security_service", "resource_id": "audit_record_1", "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "REMEDIATION", "system_id": "security_service", "resource_id": "audit_record_1", "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": ""},
            {"step_no": 3, "phase": "VERIFICATION", "system_id": "security_service", "resource_id": "audit_record_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
            {"step_no": 4, "phase": "VERIFICATION", "system_id": "account_service", "resource_id": "acc_1", "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""},
        ]
        res = check_warn_conventions("c1", "INCOMPLETE", retain_steps)
        self.assertTrue(any(v.rule_id == "W05" for v in res))

    def test_w06_incomplete_account_absent_verification(self):
        # INCOMPLETE without account_service VERIFY_RECORD_ABSENT
        no_account_steps = [
            {"step_no": 1, "phase": "FINDING", "system_id": "analytics_platform", "resource_id": "an_1", "operation": "REPORT_EXPOSED_PII", "state": "PRESENT", "evidence_id": "ev_1"},
            {"step_no": 2, "phase": "REMEDIATION", "system_id": "analytics_platform", "resource_id": "an_1", "operation": "ANONYMIZE_RECORD", "state": "ANONYMIZED", "evidence_id": ""},
            {"step_no": 3, "phase": "VERIFICATION", "system_id": "analytics_platform", "resource_id": "an_1", "operation": "VERIFY_RECORD_ANONYMIZED", "state": "ANONYMIZED", "evidence_id": ""},
        ]
        res = check_warn_conventions("c1", "INCOMPLETE", no_account_steps)
        self.assertTrue(any(v.rule_id == "W06" for v in res))


if __name__ == "__main__":
    unittest.main()
