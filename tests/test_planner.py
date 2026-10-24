"""
Unit tests for ghost_audit.planner and ghost_audit.emit.
"""

from pathlib import Path
import tempfile
import unittest

from ghost_audit.emit import emit_output_file, natural_sort_key
from ghost_audit.linker.graph import AttributedResource, CaseLinkage
from ghost_audit.planner import CaseDecision, plan_case
from ghost_audit.rules import RuleEngine
from ghost_audit.spec import (
    PHASE_FINDING,
    PHASE_REMEDIATION,
    PHASE_VERIFICATION,
    STATUS_COMPLETE,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
)
from ghost_audit.state import ResourceState


class DummyCoverageIndex:
    def __init__(self):
        self.records = []


class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.rule_engine = RuleEngine()
        self.coverage_index = DummyCoverageIndex()

    def test_natural_sort_key(self):
        keys = ["case_1", "case_10", "case_2"]
        keys.sort(key=natural_sort_key)
        self.assertEqual(keys, ["case_1", "case_2", "case_10"])

    def test_plan_case_not_applicable(self):
        linkage = CaseLinkage(case_id="case_100", email="user1@example.com", user_id="user_1")
        dec = plan_case(
            case_id="case_100",
            request_text="Please export all my personal data in JSON format.",
            audit_at="2026-09-17T00:00:00Z",
            case_linkage=linkage,
            resource_states={},
            categories={},
            rule_engine=self.rule_engine,
            obs_by_res={},
            coverage_index=self.coverage_index,
        )
        self.assertEqual(dec.deletion_status, STATUS_NOT_APPLICABLE)
        self.assertEqual(dec.steps, [])
        self.assertEqual(dec.steps_json, "[]")

    def test_plan_case_complete(self):
        rid_acc = "acc_001"
        rid_audit = "audit_001"

        linkage = CaseLinkage(
            case_id="case_101",
            email="user1@example.com",
            user_id="user_1",
            attributed_resources={
                rid_acc: AttributedResource(resource_id=rid_acc, system_id="account_service", signals=[], best_citable_file_id="ev_01"),
                rid_audit: AttributedResource(resource_id=rid_audit, system_id="security_service", signals=[], best_citable_file_id="ev_01"),
            },
        )
        states = {
            rid_acc: ResourceState(resource_id=rid_acc, system_id="account_service", status="ABSENT"),
            rid_audit: ResourceState(resource_id=rid_audit, system_id="security_service", status="PRESENT", retention_until="2030-01-01T00:00:00Z"),
        }
        categories = {
            rid_acc: "USER_PROFILE",
            rid_audit: "SECURITY_AUDIT_LOG",
        }

        dec = plan_case(
            case_id="case_101",
            request_text="Please delete my account and all associated data.",
            audit_at="2026-09-17T00:00:00Z",
            case_linkage=linkage,
            resource_states=states,
            categories=categories,
            rule_engine=self.rule_engine,
            obs_by_res={},
            coverage_index=self.coverage_index,
        )
        self.assertEqual(dec.deletion_status, STATUS_COMPLETE)
        self.assertEqual(len(dec.steps), 2)
        # All verifications
        for s in dec.steps:
            self.assertEqual(s["phase"], PHASE_VERIFICATION)
            self.assertNotEqual(s["evidence_id"], "")
        self.assertEqual(dec.steps[0]["step_no"], 1)
        self.assertEqual(dec.steps[1]["step_no"], 2)

    def test_plan_case_incomplete(self):
        rid_acc = "acc_002"
        rid_search = "search_002"
        rid_audit = "audit_002"

        linkage = CaseLinkage(
            case_id="case_102",
            email="user2@example.com",
            user_id="user_2",
            attributed_resources={
                rid_acc: AttributedResource(resource_id=rid_acc, system_id="account_service", signals=[], best_citable_file_id="ev_01"),
                rid_search: AttributedResource(resource_id=rid_search, system_id="search_service", signals=[], best_citable_file_id="ev_02"),
                rid_audit: AttributedResource(resource_id=rid_audit, system_id="security_service", signals=[], best_citable_file_id="ev_01"),
            },
        )
        states = {
            rid_acc: ResourceState(resource_id=rid_acc, system_id="account_service", status="ABSENT"),
            rid_search: ResourceState(resource_id=rid_search, system_id="search_service", status="PRESENT"),
            rid_audit: ResourceState(resource_id=rid_audit, system_id="security_service", status="PRESENT", retention_until="2030-01-01T00:00:00Z"),
        }
        categories = {
            rid_acc: "USER_PROFILE",
            rid_search: "SEARCH_INDEX_ENTRY",
            rid_audit: "SECURITY_AUDIT_LOG",
        }

        dec = plan_case(
            case_id="case_102",
            request_text="I want to erase my account and profile.",
            audit_at="2026-09-17T00:00:00Z",
            case_linkage=linkage,
            resource_states=states,
            categories=categories,
            rule_engine=self.rule_engine,
            obs_by_res={},
            coverage_index=self.coverage_index,
        )
        self.assertEqual(dec.deletion_status, STATUS_INCOMPLETE)

        findings = [s for s in dec.steps if s["phase"] == PHASE_FINDING]
        remediations = [s for s in dec.steps if s["phase"] == PHASE_REMEDIATION]
        verifications = [s for s in dec.steps if s["phase"] == PHASE_VERIFICATION]

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["resource_id"], rid_search)
        self.assertEqual(findings[0]["evidence_id"], "ev_02")

        self.assertEqual(len(remediations), 1)
        self.assertEqual(remediations[0]["resource_id"], rid_search)
        self.assertEqual(remediations[0]["evidence_id"], "")

        # Verifications: account verified absent + search remediated + audit retained
        self.assertEqual(len(verifications), 3)
        v_res = [v["resource_id"] for v in verifications]
        self.assertIn(rid_acc, v_res)
        self.assertIn(rid_search, v_res)
        self.assertIn(rid_audit, v_res)
        for v in verifications:
            self.assertEqual(v["evidence_id"], "")

    def test_emit_output_file(self):
        decisions = [
            CaseDecision(case_id="case_10", deletion_status=STATUS_NOT_APPLICABLE, treatments={}, steps=[]),
            CaseDecision(case_id="case_2", deletion_status=STATUS_COMPLETE, treatments={}, steps=[]),
        ]
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "out.csv"
            emit_output_file(decisions, out_file, id_sort="natural")
            self.assertTrue(out_file.exists())
            content = out_file.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(content[0], "case_id,deletion_status,steps_json")
            # Natural sort: case_2 before case_10
            self.assertTrue(content[1].startswith("case_2,"))
            self.assertTrue(content[2].startswith("case_10,"))


if __name__ == "__main__":
    unittest.main()
