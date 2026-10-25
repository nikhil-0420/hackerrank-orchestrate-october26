"""
Unit tests for ghost_audit/rules.py.
Verifies rule engine parsing of deletion_rules.csv and policy decisions.
"""

import unittest

from ghost_audit.rules import RuleEngine, TreatmentDecision
from ghost_audit.state import ResourceState


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()
        self.audit_at = "2026-09-15T12:00:00Z"

    def test_rules_loaded(self):
        self.assertGreaterEqual(len(self.engine.rules_by_category), 15)
        self.assertIn("USER_PROFILE", self.engine.rules_by_category)
        self.assertEqual(self.engine.rules_by_category["USER_PROFILE"].required_action, "DELETE")

    def test_user_profile_present_violation(self):
        st = ResourceState(
            resource_id="account_test1",
            system_id="account_service",
            status="PRESENT",
            has_direct_identifiers=True,
        )
        dec = self.engine.evaluate_resource(st, "USER_PROFILE", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertEqual(dec.finding_op, "REPORT_REMAINING_RECORD")
        self.assertEqual(dec.remediation_op, "DELETE_RECORD")
        self.assertEqual(dec.verification_op, "VERIFY_RECORD_ABSENT")

    def test_user_profile_absent_compliant(self):
        st = ResourceState(
            resource_id="account_test2",
            system_id="account_service",
            status="ABSENT",
        )
        dec = self.engine.evaluate_resource(st, "USER_PROFILE", self.audit_at)
        self.assertTrue(dec.is_compliant)
        self.assertEqual(dec.verification_op, "VERIFY_RECORD_ABSENT")

    def test_support_message_pii_violation(self):
        st = ResourceState(
            resource_id="support_test1",
            system_id="support_platform",
            status="PRESENT",
            has_direct_identifiers=True,
        )
        dec = self.engine.evaluate_resource(st, "SUPPORT_MESSAGE", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertEqual(dec.finding_op, "REPORT_EXPOSED_PII")
        self.assertEqual(dec.remediation_op, "REDACT_RECORD")
        self.assertEqual(dec.verification_op, "VERIFY_RECORD_REDACTED")

    def test_analytics_profile_anonymized_compliant(self):
        st = ResourceState(
            resource_id="analytics_test1",
            system_id="analytics_platform",
            status="PRESENT",
            has_direct_identifiers=False,
        )
        dec = self.engine.evaluate_resource(st, "ANALYTICS_PROFILE", self.audit_at)
        self.assertTrue(dec.is_compliant)
        self.assertEqual(dec.verification_op, "VERIFY_RECORD_ANONYMIZED")

    def test_active_data_flow_violation(self):
        st = ResourceState(
            resource_id="data_flow_test1",
            system_id="integration_service",
            status="PRESENT",
            is_active=True,
        )
        dec = self.engine.evaluate_resource(st, "DATA_FLOW", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertEqual(dec.finding_op, "REPORT_ACTIVE_DATA_FLOW")
        self.assertEqual(dec.remediation_op, "DISABLE_DATA_FLOW")
        self.assertEqual(dec.verification_op, "VERIFY_DATA_FLOW_DISABLED")

    def test_backup_restore_risk_violation(self):
        st = ResourceState(
            resource_id="backup_test1",
            system_id="backup_service",
            status="PRESENT",
            is_active=True,
        )
        dec = self.engine.evaluate_resource(st, "BACKUP_ARCHIVE", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertEqual(dec.finding_op, "REPORT_RESTORE_RISK")
        self.assertEqual(dec.remediation_op, "BLOCK_RESTORE")
        self.assertEqual(dec.verification_op, "VERIFY_RESTORE_BLOCKED")

    def test_security_audit_retained_present(self):
        st = ResourceState(
            resource_id="audit_record_test1",
            system_id="security_service",
            status="PRESENT",
            retention_until="2034-09-30T23:59:59Z",
        )
        dec = self.engine.evaluate_resource(st, "SECURITY_AUDIT_LOG", self.audit_at)
        self.assertTrue(dec.is_compliant)
        self.assertEqual(dec.verification_op, "VERIFY_RECORD_PRESENT")

    def test_unknown_category_undecided(self):
        st = ResourceState(
            resource_id="custom_res1",
            system_id="custom_service",
            status="PRESENT",
        )
        dec = self.engine.evaluate_resource(st, "UNKNOWN", self.audit_at)
        self.assertTrue(dec.is_undecided)

    def test_data_flow_unknown_status_undecided(self):
        st = ResourceState(
            resource_id="data_flow_unknown_1",
            system_id="integration_service",
            status="PRESENT",
            is_active=False,
            is_blocked_or_disabled=False,
        )
        dec = self.engine.evaluate_resource(st, "DATA_FLOW", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertTrue(dec.is_undecided)
        self.assertEqual(dec.undecided_reason, "data_flow_status_unknown")
        self.assertEqual(dec.finding_op, "REPORT_ACTIVE_DATA_FLOW")
        self.assertEqual(dec.remediation_op, "DISABLE_DATA_FLOW")
        self.assertEqual(dec.verification_op, "VERIFY_DATA_FLOW_DISABLED")

    def test_backup_restore_unknown_status_undecided(self):
        st = ResourceState(
            resource_id="backup_unknown_1",
            system_id="backup_service",
            status="PRESENT",
            is_active=False,
            is_blocked_or_disabled=False,
        )
        dec = self.engine.evaluate_resource(st, "BACKUP_ARCHIVE", self.audit_at)
        self.assertFalse(dec.is_compliant)
        self.assertTrue(dec.is_undecided)
        self.assertEqual(dec.undecided_reason, "backup_restore_status_unknown")
        self.assertEqual(dec.finding_op, "REPORT_RESTORE_RISK")
        self.assertEqual(dec.remediation_op, "BLOCK_RESTORE")
        self.assertEqual(dec.verification_op, "VERIFY_RESTORE_BLOCKED")


if __name__ == "__main__":
    unittest.main()
