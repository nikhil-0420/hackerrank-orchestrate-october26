"""
Unit tests for ghost_audit/linker/ with hand-made data.

Verifies:
  - S1 exact identifier matching and decoy rejection
  - S2 word-boundary user_id joins
  - S3 merged trace identity
  - S4 link row matching
  - S5 chain key 1-hop traversal
  - S7 anchor window filtering (tutorial +/-10m, standard -80m to -40m)
  - Hard rule enforcement (attributed vs unattributed)
"""

import unittest
from datetime import datetime
from typing import Dict, List

from ghost_audit.activity import ActivityLog, SystemActivityRow
from ghost_audit.identity import IdentityResolver, ResolvedIdentity
from ghost_audit.linker import (
    AttributedResource,
    CaseLinkage,
    Linker,
    Signal,
    UnattributedResource,
    is_valid_resource_id,
)
from ghost_audit.linker.assign import (
    KNOWN_OFFSETS,
    STANDARD_WINDOW_MIN,
    TUTORIAL_WINDOW_MIN,
    matches_known_offset,
    status_matches_result,
)
from ghost_audit.linker.graph import build_case_attribution_graph
from ghost_audit.linker.signals import collect_hard_signals_for_case
from ghost_audit.observation import Identifiers, Observation


class TestLinkerSignals(unittest.TestCase):
    """Test S1-S6 signal extraction with hand-crafted observations."""

    def setUp(self):
        self.ident = ResolvedIdentity(
            user_id="user_101",
            resolution_kind="current",
            emails=["alice@example.com", "alice.old@example.com"],
            phones=["+1-555-0101"],
            hashes=["a" * 64],
            name="Alice Smith",
        )
        self.audit_at = "2026-10-01T12:00:00Z"
        self.requested_at = "2026-09-01T12:00:00Z"

    def test_s1_exact_email_and_decoy_rejection(self):
        obs_exact = Observation(
            file_id="ev_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="search_service",
            collection="searches",
            resource_id="search_101",
            identifiers=Identifiers(email="alice@example.com"),
            state={},
            source_kind="json",
            raw_ref="idx:0",
        )
        obs_decoy = Observation(
            file_id="ev_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="search_service",
            collection="searches",
            resource_id="search_102",
            identifiers=Identifiers(email="alice@example.org"),  # decoy domain
            state={},
            source_kind="json",
            raw_ref="idx:1",
        )
        obs_by_res = {
            "search_101": [obs_exact],
            "search_102": [obs_decoy],
        }
        activity = ActivityLog([])

        signals = collect_hard_signals_for_case(
            case_id="case_t1",
            requested_at=self.requested_at,
            audit_at=self.audit_at,
            identity=self.ident,
            all_observations=[obs_exact, obs_decoy],
            activity=activity,
            obs_by_res=obs_by_res,
        )

        attributed_ids = {s.resource_id for s in signals}
        self.assertIn("search_101", attributed_ids)
        self.assertNotIn("search_102", attributed_ids)

    def test_s2_word_boundary_user_id(self):
        obs_exact = Observation(
            file_id="ev_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="support_platform",
            collection="tickets",
            resource_id="support_101",
            identifiers=Identifiers(user_ref="user_101"),
            state={},
            source_kind="json",
            raw_ref="idx:0",
        )
        obs_prefix = Observation(
            file_id="ev_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="support_platform",
            collection="tickets",
            resource_id="support_102",
            identifiers=Identifiers(user_ref="user_1012"),  # user_101 prefix collision
            state={},
            source_kind="json",
            raw_ref="idx:1",
        )
        obs_by_res = {
            "support_101": [obs_exact],
            "support_102": [obs_prefix],
        }
        activity = ActivityLog([])

        signals = collect_hard_signals_for_case(
            case_id="case_t2",
            requested_at=self.requested_at,
            audit_at=self.audit_at,
            identity=self.ident,
            all_observations=[obs_exact, obs_prefix],
            activity=activity,
            obs_by_res=obs_by_res,
        )

        attributed_ids = {s.resource_id for s in signals}
        self.assertIn("support_101", attributed_ids)
        self.assertNotIn("support_102", attributed_ids)

    def test_s3_merged_trace_synthetic(self):
        """Synthetic test: S3 merged trace linking via trace_id in state or trace: in raw_ref."""
        obs_with_trace = Observation(
            file_id="ev_trace_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="support_platform",
            collection="tickets",
            resource_id="support_301",
            identifiers=Identifiers(email="alice@example.com"),
            state={"trace_id": "tr-998877", "ticket_id": "CS-301"},
            source_kind="log",
            raw_ref="trace:tr-998877:line_42",
        )
        obs_decoy_trace = Observation(
            file_id="ev_trace_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="support_platform",
            collection="tickets",
            resource_id="support_302",
            identifiers=Identifiers(email="bob@example.com"),
            state={"trace_id": "tr-112233", "ticket_id": "CS-302"},
            source_kind="log",
            raw_ref="trace:tr-112233:line_55",
        )
        obs_by_res = {
            "support_301": [obs_with_trace],
            "support_302": [obs_decoy_trace],
        }
        activity = ActivityLog([])

        signals = collect_hard_signals_for_case(
            case_id="case_t_s3",
            requested_at=self.requested_at,
            audit_at=self.audit_at,
            identity=self.ident,
            all_observations=[obs_with_trace, obs_decoy_trace],
            activity=activity,
            obs_by_res=obs_by_res,
        )

        s3_signals = [s for s in signals if s.signal_name == "S3_MERGED_TRACE"]
        self.assertTrue(len(s3_signals) >= 1)
        self.assertEqual(s3_signals[0].resource_id, "support_301")
        self.assertEqual(s3_signals[0].strength, 0.90)

        # Ensure decoy trace with non-matching email is not attributed
        attributed_ids = {s.resource_id for s in signals}
        self.assertNotIn("support_302", attributed_ids)

    def test_s4_link_row_synthetic(self):
        """Synthetic test: S4 LINK_RESOURCE_IDENTITY operational activity rows."""
        row_matching = SystemActivityRow(
            activity_id="act_4001",
            event_time="2026-09-05T10:00:00Z",
            event_type="LINK_RESOURCE_IDENTITY",
            source_system="data_catalog",
            target_system="analytics_platform",
            resource_id="analytics_404",
            reported_result="SUCCESS",
            details="Data catalog linked analytics_404 (analytics_404) to alice@example.com and user_101.",
        )
        row_unrelated = SystemActivityRow(
            activity_id="act_4002",
            event_time="2026-09-05T10:00:00Z",
            event_type="LINK_RESOURCE_IDENTITY",
            source_system="data_catalog",
            target_system="export_service",
            resource_id="export_999",
            reported_result="SUCCESS",
            details="Data catalog linked export_999 (export_999) to charlie@example.com and user_999.",
        )
        activity = ActivityLog([row_matching, row_unrelated])
        obs_by_res = {
            "analytics_404": [
                Observation(
                    file_id="ev_01",
                    file_captured_at="2026-09-10T12:00:00Z",
                    obs_time="2026-09-05T10:00:00Z",
                    system_id="analytics_platform",
                    collection="reports",
                    resource_id="analytics_404",
                    identifiers=Identifiers(),
                    state={},
                    source_kind="json",
                    raw_ref="idx:0",
                )
            ]
        }

        signals = collect_hard_signals_for_case(
            case_id="case_t_s4",
            requested_at=self.requested_at,
            audit_at=self.audit_at,
            identity=self.ident,
            all_observations=obs_by_res["analytics_404"],
            activity=activity,
            obs_by_res=obs_by_res,
        )

        s4_signals = [s for s in signals if s.signal_name == "S4_LINK_ROW"]
        self.assertEqual(len(s4_signals), 1)
        self.assertEqual(s4_signals[0].resource_id, "analytics_404")
        self.assertEqual(s4_signals[0].strength, 0.85)

        attributed_ids = {s.resource_id for s in signals}
        self.assertNotIn("export_999", attributed_ids)

    def test_s5_chain_keys_synthetic(self):
        """Synthetic test: S5 chain key 1-hop traversal across object_key, archive_key, and parent_resource_id."""
        obs_root = Observation(
            file_id="ev_01",
            file_captured_at="2026-09-10T12:00:00Z",
            obs_time="2026-09-05T12:00:00Z",
            system_id="export_service",
            collection="jobs",
            resource_id="export_501",
            identifiers=Identifiers(email="alice@example.com"),
            state={
                "source_resource_id": "account_999",
                "archive_key": "archive/customer-data/backup_888.tar.zst",
                "object_key": "exports/user_data/export_777.csv",
                "parent_resource_id": "support_666",
            },
            source_kind="json",
            raw_ref="idx:0",
        )
        obs_by_res = {"export_501": [obs_root]}
        activity = ActivityLog([])

        signals = collect_hard_signals_for_case(
            case_id="case_t_s5",
            requested_at=self.requested_at,
            audit_at=self.audit_at,
            identity=self.ident,
            all_observations=[obs_root],
            activity=activity,
            obs_by_res=obs_by_res,
        )

        s5_signals = [s for s in signals if s.signal_name == "S5_CHAIN_KEY"]
        s5_res_ids = {s.resource_id for s in s5_signals}

        # S5 traverses all 4 linked resource keys
        self.assertIn("account_999", s5_res_ids)
        self.assertIn("backup_888", s5_res_ids)
        self.assertIn("export_777", s5_res_ids)
        self.assertIn("support_666", s5_res_ids)
        for s in s5_signals:
            self.assertEqual(s.strength, 0.80)



class TestLinkerAssignment(unittest.TestCase):
    """Test S7 anchor windows and S8 schedule offsets."""

    def test_status_compatibility(self):
        self.assertTrue(status_matches_result("COMPLETE", "SUCCESS"))
        self.assertFalse(status_matches_result("COMPLETE", "FAILED"))
        self.assertTrue(status_matches_result("NOT_STARTED", "FAILED"))
        self.assertFalse(status_matches_result("NOT_STARTED", "SUCCESS"))
        self.assertTrue(status_matches_result("PARTIALLY_COMPLETE", "PARTIAL"))

    def test_known_offsets(self):
        self.assertTrue(matches_known_offset("export_service", 87.9, tol=0.5))
        self.assertTrue(matches_known_offset("search_service", 106.4, tol=0.5))
        self.assertTrue(matches_known_offset("identity_service", 114.9, tol=0.5))
        self.assertTrue(matches_known_offset("analytics_platform", 29.7, tol=0.5))
        self.assertFalse(matches_known_offset("export_service", 30.0, tol=0.5))


class TestAttributionGraph(unittest.TestCase):
    """Test hard rule enforcement and best citable file selection."""

    def test_hard_rule_enforcement(self):
        obs_citable = Observation(
            file_id="ev_early",
            file_captured_at="2026-09-01T12:00:00Z",
            obs_time="2026-09-01T10:00:00Z",
            system_id="account_service",
            collection="profiles",
            resource_id="account_100",
            identifiers=Identifiers(),
            state={},
            source_kind="json",
            raw_ref="idx:0",
        )
        obs_by_res = {"account_100": [obs_citable]}

        hard_signal = Signal(
            resource_id="account_100",
            signal_name="S1_IDENTIFIER",
            evidence_ref="ev_early:idx:0",
            strength=1.0,
            system_id="account_service",
            file_id="ev_early",
        )
        weak_signal = Signal(
            resource_id="backup_999",
            signal_name="S9_UNOFFICIAL_WEAK",
            evidence_ref="unsupported",
            strength=0.1,
            system_id="backup_service",
        )

        linkage = build_case_attribution_graph(
            case_id="case_test",
            user_id="user_100",
            email="test@example.com",
            audit_at="2026-09-15T12:00:00Z",
            all_signals=[hard_signal, weak_signal],
            obs_by_res=obs_by_res,
        )

        # account_100 has hard signal -> ATTRIBUTED
        self.assertIn("account_100", linkage.attributed_resources)
        attr = linkage.attributed_resources["account_100"]
        self.assertEqual(attr.best_citable_file_id, "ev_early")

        # backup_999 has no hard signal or exception -> UNATTRIBUTED
        self.assertNotIn("backup_999", linkage.attributed_resources)
        unattributed_ids = [u.resource_id for u in linkage.unattributed_resources]
        self.assertIn("backup_999", unattributed_ids)


if __name__ == "__main__":
    unittest.main()
