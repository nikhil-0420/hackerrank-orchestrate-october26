"""
Unit tests for ghost_audit/evidence/doc_normalizer.py.
Verifies resource regex digit requirement, OCR typo normalization,
per-resource identifier attribution, and status word parsing.
"""

import unittest
from pathlib import Path
from ghost_audit.evidence.doc_normalizer import (
    RESOURCE_RE,
    _extract_doc_observations,
)
from ghost_audit.loaders.manifest import EvidenceFileMeta


class TestDocNormalizer(unittest.TestCase):
    def test_resource_regex_requires_digits(self):
        # Must match prefix + digits
        valid_examples = [
            "account_123",
            "search_01",
            "support_999",
            "analytics_42",
            "data_flow_1121",
            "backup_9287",
            "audit_record_001",
            "audlt_record_002",
            "tombstone_7",
            "export_88",
            "legal_9",
        ]
        for example in valid_examples:
            matches = RESOURCE_RE.findall(example)
            self.assertEqual(matches, [example], f"Failed to match valid resource {example}")

        # Must NOT match non-digit suffixes
        invalid_examples = [
            "account_closure_recorded",
            "account_service",
            "support_platform",
            "analytics_profile",
            "audit_record_deleted",
            "legal_hold_active",
        ]
        for example in invalid_examples:
            matches = RESOURCE_RE.findall(example)
            self.assertEqual(matches, [], f"Incorrectly matched invalid resource {example}")

    def test_audlt_typo_normalization(self):
        meta = EvidenceFileMeta(
            file_id="evidence_999",
            file_path="mock/path.png",
            origin="test",
            captured_at="2026-09-01T00:00:00Z",
            abs_path=Path("mock/path.png"),
        )
        raw_text = "audlt_record_002 actor automated account workflow"
        obs = _extract_doc_observations(raw_text, meta, "png")
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0].state["resource_id"], "audit_record_002")

    def test_per_resource_identifiers_multi_user(self):
        meta = EvidenceFileMeta(
            file_id="evidence_998",
            file_path="mock/path.png",
            origin="test",
            captured_at="2026-09-01T00:00:00Z",
            abs_path=Path("mock/path.png"),
        )
        raw_text = """
        User Directory Export
        user_101 | alice@example.com | account_101 | Active
        user_102 | bob@example.com   | account_102 | Active
        data_flow_9000               | Connected
        """
        obs = _extract_doc_observations(raw_text, meta, "png")
        obs_by_res = {o.state["resource_id"]: o for o in obs}

        self.assertIn("account_101", obs_by_res)
        self.assertEqual(obs_by_res["account_101"].identifiers.email, "alice@example.com")
        self.assertEqual(obs_by_res["account_101"].identifiers.user_ref, "user_101")

        self.assertIn("account_102", obs_by_res)
        self.assertEqual(obs_by_res["account_102"].identifiers.email, "bob@example.com")
        self.assertEqual(obs_by_res["account_102"].identifiers.user_ref, "user_102")

        # Multi-user document: data_flow_9000 must NOT fall back to alice or bob
        self.assertIn("data_flow_9000", obs_by_res)
        self.assertIsNone(obs_by_res["data_flow_9000"].identifiers.email)
        self.assertIsNone(obs_by_res["data_flow_9000"].identifiers.user_ref)

    def test_single_user_document_fallback(self):
        meta = EvidenceFileMeta(
            file_id="evidence_997",
            file_path="mock/path.png",
            origin="test",
            captured_at="2026-09-01T00:00:00Z",
            abs_path=Path("mock/path.png"),
        )
        raw_text = """
        User Settings for alice@example.com
        user_101
        
        Connected Services:
        data_flow_9001
        Continuous
        """
        obs = _extract_doc_observations(raw_text, meta, "png")
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0].identifiers.email, "alice@example.com")
        self.assertEqual(obs[0].identifiers.user_ref, "user_101")
        self.assertEqual(obs[0].state.get("enabled"), True)
        self.assertEqual(obs[0].state.get("state"), "ACTIVE")

    def test_status_word_parsing(self):
        meta = EvidenceFileMeta(
            file_id="evidence_996",
            file_path="mock/path.png",
            origin="test",
            captured_at="2026-09-01T00:00:00Z",
            abs_path=Path("mock/path.png"),
        )
        raw_text = """
        data_flow_1001 status Healthy
        data_flow_1002 mode Paused
        backup_2001 Active
        backup_2002 Disabled
        """
        obs = _extract_doc_observations(raw_text, meta, "png")
        obs_by_res = {o.state["resource_id"]: o for o in obs}

        self.assertEqual(obs_by_res["data_flow_1001"].state.get("enabled"), True)
        self.assertEqual(obs_by_res["data_flow_1001"].state.get("state"), "ACTIVE")

        self.assertEqual(obs_by_res["data_flow_1002"].state.get("enabled"), False)
        self.assertEqual(obs_by_res["data_flow_1002"].state.get("state"), "DISABLED")

        self.assertEqual(obs_by_res["backup_2001"].state.get("enabled"), True)
        self.assertEqual(obs_by_res["backup_2001"].state.get("restore_allowed"), True)

        self.assertEqual(obs_by_res["backup_2002"].state.get("enabled"), False)
        self.assertEqual(obs_by_res["backup_2002"].state.get("restore_allowed"), False)


if __name__ == "__main__":
    unittest.main()
