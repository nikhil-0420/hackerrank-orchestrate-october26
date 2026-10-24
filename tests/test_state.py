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


if __name__ == "__main__":
    unittest.main()
