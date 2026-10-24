"""
Unit tests for code/ghost_audit/activity.py.
Uses ONLY synthetic hand-made rows (no dataset files).
"""

from pathlib import Path
import tempfile
import unittest

from ghost_audit.activity import ActivityLog, SystemActivityRow


class TestActivity(unittest.TestCase):
    def setUp(self):
        self.rows = [
            SystemActivityRow(
                activity_id="act_01",
                event_time="2026-08-01T10:00:00Z",
                event_type="DELETE_RECORD",
                source_system="deletion_worker",
                target_system="account_service",
                resource_id="account_99",
                reported_result="SUCCESS",
                details="Account deletion processed account_99.",
            ),
            SystemActivityRow(
                activity_id="act_02",
                event_time="2026-08-01T12:00:00Z",
                event_type="CLASSIFY_REQUEST",
                source_system="privacy_intake",
                target_system="workflow_engine",
                resource_id="account_88",
                reported_result="SUCCESS",
                details="Privacy intake classified request for account_88 as non-deletion.",
            ),
            SystemActivityRow(
                activity_id="act_03",
                event_time="2026-08-01T14:00:00Z",
                event_type="LINK_RESOURCE_IDENTITY",
                source_system="data_catalog",
                target_system="identity_service",
                resource_id="search_77",
                reported_result="SUCCESS",
                details="Data catalog linked search_77 (search_77) to user.test@example.com and user_5.",
            ),
            SystemActivityRow(
                activity_id="act_04",
                event_time="2026-08-02T10:00:00Z",
                event_type="CHECK_DATA_FLOW",
                source_system="flow_service",
                target_system="stream_service",
                resource_id="flow_11",
                reported_result="ACTIVE",
                details="Active flow check for flow_11.",
            ),
            SystemActivityRow(
                activity_id="act_05",
                event_time="2026-08-02T11:00:00Z",
                event_type="BLOCK_RESTORE",
                source_system="backup_service",
                target_system="archive_service",
                resource_id="backup_22",
                reported_result="SUCCESS",
                details="Backup restore access blocked for backup_22.",
            ),
            SystemActivityRow(
                activity_id="act_06",
                event_time="2026-08-03T10:00:00Z",  # future event relative to audit_at
                event_type="RETAIN_RECORD",
                source_system="security_service",
                target_system="legal_hold_service",
                resource_id="audit_33",
                reported_result="SUCCESS",
                details="Legal hold retained audit_33.",
            ),
        ]
        self.log = ActivityLog(self.rows)

    def test_anchors_and_timegating(self):
        # All anchors up to Aug 2
        anchors = self.log.anchors(audit_at="2026-08-02T23:59:59Z")
        self.assertEqual(len(anchors), 2)
        res_ids = {a.resource_id for a in anchors}
        self.assertEqual(res_ids, {"account_99", "account_88"})

        # Cut off before act_02
        early_anchors = self.log.anchors(audit_at="2026-08-01T11:00:00Z")
        self.assertEqual(len(early_anchors), 1)
        self.assertEqual(early_anchors[0].resource_id, "account_99")

    def test_link_rows_parsing(self):
        links = self.log.link_rows()
        self.assertEqual(len(links), 1)
        l = links[0]
        self.assertEqual(l["resource_id"], "search_77")
        self.assertEqual(l["email"], "user.test@example.com")
        self.assertEqual(l["user_id"], "user_5")

    def test_treatment_hint(self):
        self.assertEqual(self.log.treatment_hint("account_99"), "DELETE_RECORD")
        self.assertIsNone(self.log.treatment_hint("search_77"))

    def test_flow_restore_legal_actions(self):
        flows = self.log.flow_actions(audit_at="2026-08-02T23:59:59Z")
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0].resource_id, "flow_11")

        restores = self.log.restore_actions(audit_at="2026-08-02T23:59:59Z")
        self.assertEqual(len(restores), 1)
        self.assertEqual(restores[0].resource_id, "backup_22")

        # legal_rows with cutoff before Aug 3 returns empty
        legals_early = self.log.legal_rows(audit_at="2026-08-02T23:59:59Z")
        self.assertEqual(len(legals_early), 0)

        # legal_rows with cutoff after Aug 3 returns 1
        legals_late = self.log.legal_rows(audit_at="2026-08-04T00:00:00Z")
        self.assertEqual(len(legals_late), 1)
        self.assertEqual(legals_late[0].resource_id, "audit_33")


if __name__ == "__main__":
    unittest.main()
