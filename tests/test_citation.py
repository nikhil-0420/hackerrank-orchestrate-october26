import unittest
from pathlib import Path
import sys

code_dir = Path(__file__).resolve().parent.parent / "code"
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

from ghost_audit.citation import resolve_step_citation
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.loaders.manifest import EvidenceFileMeta
from ghost_audit.observation import CoverageRecord, Identifiers, Observation


class TestCitationEngine(unittest.TestCase):
    def setUp(self):
        self.manifest = {
            "ev_01": EvidenceFileMeta("ev_01", "p1", "db", "2026-08-01T10:00:00Z", Path("p1")),
            "ev_02": EvidenceFileMeta("ev_02", "p2", "db", "2026-09-01T10:00:00Z", Path("p2")),
            "ev_03_future": EvidenceFileMeta("ev_03_future", "p3", "db", "2026-10-01T10:00:00Z", Path("p3")),
            "ev_log_404": EvidenceFileMeta("ev_log_404", "p4", "log", "2026-09-05T12:00:00Z", Path("p4")),
        }
        self.cov_records = [
            CoverageRecord("ev_01", "2026-08-01T10:00:00Z", "account_service", "accounts", "2026-08-01T10:00:00Z", "sql", 5),
            CoverageRecord("ev_02", "2026-09-01T10:00:00Z", "account_service", "accounts", "2026-09-01T10:00:00Z", "sql", 5),
            CoverageRecord("ev_03_future", "2026-10-01T10:00:00Z", "account_service", "accounts", "2026-10-01T10:00:00Z", "sql", 5),
        ]
        self.cov_index = CoverageIndex(self.cov_records)

    def test_present_record_cites_latest_citable(self):
        obs_by_res = {
            "res_1": [
                Observation("ev_01", "2026-08-01T10:00:00Z", "2026-08-01T10:00:00Z", "search_service", "idx", "res_1", Identifiers(), {"status": "ACTIVE"}, "log", "ref"),
                Observation("ev_02", "2026-09-01T10:00:00Z", "2026-09-01T10:00:00Z", "search_service", "idx", "res_1", Identifiers(), {"status": "ACTIVE"}, "log", "ref"),
                Observation("ev_03_future", "2026-10-01T10:00:00Z", "2026-10-01T10:00:00Z", "search_service", "idx", "res_1", Identifiers(), {"status": "ACTIVE"}, "log", "ref"),
            ]
        }
        # audit_at before future file
        cited = resolve_step_citation(
            resource_id="res_1",
            system_id="search_service",
            state="PRESENT",
            audit_at="2026-09-15T00:00:00Z",
            obs_by_res=obs_by_res,
            coverage_index=self.cov_index,
            manifest=self.manifest,
        )
        self.assertEqual(cited, "ev_02")

    def test_never_cites_file_captured_after_audit_at(self):
        obs_by_res = {
            "res_1": [
                Observation("ev_03_future", "2026-10-01T10:00:00Z", "2026-10-01T10:00:00Z", "search_service", "idx", "res_1", Identifiers(), {"status": "ACTIVE"}, "log", "ref"),
            ]
        }
        cited = resolve_step_citation(
            resource_id="res_1",
            system_id="search_service",
            state="PRESENT",
            audit_at="2026-09-15T00:00:00Z",
            obs_by_res=obs_by_res,
            coverage_index=self.cov_index,
            manifest=self.manifest,
        )
        self.assertEqual(cited, "")

    def test_absent_record_with_404_cites_404_file(self):
        obs_by_res = {
            "res_absent": [
                Observation("ev_log_404", "2026-09-05T12:00:00Z", "2026-09-05T12:00:00Z", "account_service", "profiles", "res_absent", Identifiers(), {"http_status": 404}, "log", "ref"),
            ]
        }
        cited = resolve_step_citation(
            resource_id="res_absent",
            system_id="account_service",
            state="ABSENT",
            audit_at="2026-09-15T00:00:00Z",
            obs_by_res=obs_by_res,
            coverage_index=self.cov_index,
            manifest=self.manifest,
        )
        self.assertEqual(cited, "ev_log_404")

    def test_absent_record_without_404_cites_covering_snapshot(self):
        obs_by_res = {}
        cited = resolve_step_citation(
            resource_id="res_absent",
            system_id="account_service",
            state="ABSENT",
            audit_at="2026-09-15T00:00:00Z",
            obs_by_res=obs_by_res,
            coverage_index=self.cov_index,
            manifest=self.manifest,
        )
        # Should cite ev_02 (latest citable covering snapshot for account_service)
        self.assertEqual(cited, "ev_02")


if __name__ == "__main__":
    unittest.main()
