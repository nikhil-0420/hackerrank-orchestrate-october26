"""
Unit tests for ghost_audit/state.py.
Tests presence, absence, conflict resolution, covering snapshot absence proof,
timegating, and PII detection with synthetic test data.
"""

from datetime import datetime
import unittest

from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.observation import CoverageRecord, Identifiers, Observation
from ghost_audit.state import ResourceState, determine_resource_state


class TestResourceState(unittest.TestCase):
    def setUp(self):
        self.audit_at = "2026-09-15T12:00:00Z"

    def test_single_presence_observation(self):
        obs = Observation(
            file_id="evidence_10",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-10T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles",
            resource_id="account_test1",
            identifiers=Identifiers(email="test@example.com"),
            state={"account_status": "ACTIVE", "replica_of": "primary"},
            source_kind="sql",
            raw_ref="row:1",
        )
        res = determine_resource_state(
            resource_id="account_test1",
            system_id="account_service",
            observations=[obs],
            audit_at=self.audit_at,
        )
        self.assertEqual(res.status, "PRESENT")
        self.assertEqual(res.obs_time, "2026-09-10T10:00:00Z")
        self.assertEqual(res.replica_info, "primary")
        self.assertTrue(res.has_direct_identifiers)
        self.assertEqual(res.direct_identifiers["email"], "test@example.com")
        self.assertIsNone(res.conflict_notes)

    def test_conflict_resolution_later_wins(self):
        # Present at 09-01, but lookup miss (404) at 09-10
        obs_pres = Observation(
            file_id="evidence_05",
            file_captured_at="2026-09-01T12:00:00Z",
            obs_time="2026-09-01T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles",
            resource_id="account_test2",
            identifiers=Identifiers(email="test2@example.com"),
            state={"account_status": "ACTIVE"},
            source_kind="sql",
            raw_ref="row:1",
        )
        obs_abs = Observation(
            file_id="evidence_12",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-10T10:00:00Z",
            system_id="account_service",
            collection="profile_lookup_completed",
            resource_id="account_test2",
            identifiers=Identifiers(),
            state={"http_status": "404", "rows": "0"},
            source_kind="log",
            raw_ref="line:5",
        )
        res = determine_resource_state(
            resource_id="account_test2",
            system_id="account_service",
            observations=[obs_pres, obs_abs],
            audit_at=self.audit_at,
        )
        self.assertEqual(res.status, "ABSENT")
        self.assertIsNotNone(res.conflict_notes)
        self.assertIn("superseded", res.conflict_notes)

    def test_conflict_concurrent_replica_presence_wins(self):
        # Concurrent at 2026-09-10T10:00:00Z: miss on secondary, present in failover replica
        obs_abs = Observation(
            file_id="evidence_12",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-10T10:00:00Z",
            system_id="account_service",
            collection="profile_lookup_completed",
            resource_id="account_test3",
            identifiers=Identifiers(),
            state={"result": "miss"},
            source_kind="log",
            raw_ref="line:5",
        )
        obs_pres = Observation(
            file_id="evidence_13",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-10T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles_failover_replica",
            resource_id="account_test3",
            identifiers=Identifiers(email="test3@example.com"),
            state={"account_status": "ACTIVE", "replica_of": "failover"},
            source_kind="sql",
            raw_ref="row:1",
        )
        res = determine_resource_state(
            resource_id="account_test3",
            system_id="account_service",
            observations=[obs_abs, obs_pres],
            audit_at=self.audit_at,
        )
        self.assertEqual(res.status, "PRESENT")
        self.assertIn("replica presence wins", res.conflict_notes)
        self.assertEqual(res.replica_info, "failover")

    def test_covering_snapshot_proves_absence(self):
        # No observation exists, but a covering snapshot was captured before audit_at
        cov = CoverageIndex([
            CoverageRecord(
                file_id="evidence_54",
                file_captured_at="2026-09-02T23:00:00Z",
                system_id="account_service",
                collection="customer_profiles",
                obs_time="2026-09-02T23:00:00Z",
                source_kind="sql",
                record_count=100,
            )
        ])
        res = determine_resource_state(
            resource_id="account_test4",
            system_id="account_service",
            observations=[],
            audit_at=self.audit_at,
            coverage_index=cov,
            collection_hint="customer_profiles",
        )
        self.assertEqual(res.status, "ABSENT")
        self.assertIsNone(res.obs_time)
        self.assertIsNone(res.supporting_observation)

    def test_non_covering_file_yields_unknown(self):
        # No observations and no covering snapshot
        cov = CoverageIndex([])
        res = determine_resource_state(
            resource_id="account_test5",
            system_id="account_service",
            observations=[],
            audit_at=self.audit_at,
            coverage_index=cov,
        )
        self.assertEqual(res.status, "UNKNOWN")

    def test_timegating_future_observation_ignored(self):
        # Observation is after audit_at -> should be ignored
        obs_future = Observation(
            file_id="evidence_99",
            file_captured_at="2026-10-01T12:00:00Z",
            obs_time="2026-10-01T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles",
            resource_id="account_test6",
            identifiers=Identifiers(email="future@example.com"),
            state={"account_status": "ACTIVE"},
            source_kind="sql",
            raw_ref="row:1",
        )
        res = determine_resource_state(
            resource_id="account_test6",
            system_id="account_service",
            observations=[obs_future],
            audit_at=self.audit_at,
        )
        self.assertEqual(res.status, "UNKNOWN")

    def test_data_flow_active_vs_disabled(self):
        obs_active = Observation(
            file_id="evidence_13",
            file_captured_at="2026-08-12T09:00:00Z",
            obs_time="2026-08-12T09:00:00Z",
            system_id="integration_service",
            collection="connector_configurations",
            resource_id="flow_test1",
            identifiers=Identifiers(),
            state={"enabled": True},
            source_kind="json",
            raw_ref="item:1",
        )
        res = determine_resource_state(
            resource_id="flow_test1",
            system_id="integration_service",
            observations=[obs_active],
            audit_at=self.audit_at,
        )
        self.assertEqual(res.status, "PRESENT")
        self.assertTrue(res.is_active)
        self.assertFalse(res.is_blocked_or_disabled)

    def test_supersedence_later_covering_snapshot_supersedes_earlier_presence(self):
        # Presence in an earlier image snapshot at 2026-06-18
        obs_pres = Observation(
            file_id="evidence_23",
            file_captured_at="2026-06-18T12:00:00Z",
            obs_time="2026-06-18T12:00:00Z",
            system_id="export_service",
            collection="customer_exports",
            resource_id="export_test_super",
            identifiers=Identifiers(),
            state={"status": "AVAILABLE"},
            source_kind="image",
            raw_ref="image:evidence_23 id:export_test_super",
        )
        # Later covering SQL export snapshot at 2026-07-18 that does NOT contain export_test_super
        cov_rec = CoverageRecord(
            file_id="evidence_83",
            system_id="export_service",
            collection="customer_exports",
            obs_time="2026-07-18T10:43:35Z",
            file_captured_at="2026-07-18T10:43:35Z",
            source_kind="sql",
        )
        cov = CoverageIndex([cov_rec])

        res = determine_resource_state(
            resource_id="export_test_super",
            system_id="export_service",
            observations=[obs_pres],
            audit_at="2026-07-19T13:00:00Z",
            coverage_index=cov,
            collection_hint="customer_exports",
        )
        self.assertEqual(res.status, "ABSENT")
        self.assertIn("superseded present", res.conflict_notes or "")

    def test_replica_presence_supersedes_earlier_absence(self):
        # Absence observation (e.g. 404 lookup) at 2026-07-10
        obs_abs = Observation(
            file_id="evidence_15",
            file_captured_at="2026-07-10T12:00:00Z",
            obs_time="2026-07-10T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles",
            resource_id="account_test_rep",
            identifiers=Identifiers(),
            state={"result": "NOT_FOUND"},
            source_kind="json",
            raw_ref="lookup:404",
        )
        # Replica snapshot at 2026-07-12 shows record present in replica
        obs_replica = Observation(
            file_id="evidence_20",
            file_captured_at="2026-07-12T12:00:00Z",
            obs_time="2026-07-12T10:00:00Z",
            system_id="account_service",
            collection="customer_profiles",
            resource_id="account_test_rep",
            identifiers=Identifiers(email="replica@example.com"),
            state={"account_status": "ACTIVE", "replica_of": "read_replica_1"},
            source_kind="sql",
            raw_ref="row:10",
        )
        res = determine_resource_state(
            resource_id="account_test_rep",
            system_id="account_service",
            observations=[obs_abs, obs_replica],
            audit_at="2026-07-15T12:00:00Z",
        )
        self.assertEqual(res.status, "PRESENT")
        self.assertEqual(res.replica_info, "read_replica_1")
        self.assertIn("superseded absent", res.conflict_notes or "")

    def test_earlier_covering_snapshot_does_not_supersede_later_presence(self):
        # Covering snapshot at 2026-06-01 lacking the resource
        cov_rec = CoverageRecord(
            file_id="evidence_02",
            system_id="search_service",
            collection="search_documents",
            obs_time="2026-06-01T10:00:00Z",
            file_captured_at="2026-06-01T10:00:00Z",
            source_kind="sql",
        )
        cov = CoverageIndex([cov_rec])

        # Resource created / observed present later at 2026-06-15
        obs_pres = Observation(
            file_id="evidence_11",
            file_captured_at="2026-06-15T12:00:00Z",
            obs_time="2026-06-15T10:00:00Z",
            system_id="search_service",
            collection="search_documents",
            resource_id="search_test_late",
            identifiers=Identifiers(),
            state={"index_status": "INDEXED"},
            source_kind="sql",
            raw_ref="doc:5",
        )
        res = determine_resource_state(
            resource_id="search_test_late",
            system_id="search_service",
            observations=[obs_pres],
            audit_at="2026-06-20T12:00:00Z",
            coverage_index=cov,
            collection_hint="search_documents",
        )
        self.assertEqual(res.status, "PRESENT")


if __name__ == "__main__":
    unittest.main()
