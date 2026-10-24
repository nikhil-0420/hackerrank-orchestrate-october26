"""
Unit tests for tools/labels.py.
Asserts that labels are read correctly from sample_output.csv
and that ghost_audit is strictly prohibited from importing tools.labels.
"""

from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.labels import iter_sample_labels, load_case_resource_labels



class TestLabels(unittest.TestCase):
    def test_sample_labels_reading(self):
        labels = list(iter_sample_labels())
        self.assertGreater(len(labels), 0)

        # First step in case_01 is account_001 in account_service with role verification
        first_label = labels[0]
        self.assertEqual(len(first_label), 4)
        cid, res_id, sys_id, role = first_label
        self.assertEqual(cid, "case_01")
        self.assertEqual(res_id, "account_001")
        self.assertEqual(sys_id, "account_service")
        self.assertEqual(role, "verification")

        by_case = load_case_resource_labels()
        self.assertEqual(len(by_case), 32)
        self.assertIn("case_01", by_case)
        self.assertIn(("account_001", "account_service", "verification"), by_case["case_01"])

    def test_ghost_audit_cannot_import_labels(self):
        """Simulate an access from a module with ghost_audit in its name."""
        import types

        fake_ghost_mod = types.ModuleType("ghost_audit.fake_module")
        fake_ghost_mod.__dict__["__name__"] = "ghost_audit.fake_module"
        fake_code = """
from tools.labels import load_case_resource_labels
load_case_resource_labels()
"""
        with self.assertRaises(ImportError) as ctx:
            exec(fake_code, fake_ghost_mod.__dict__)
        self.assertIn("Forbidden import", str(ctx.exception))

    def test_no_ghost_audit_module_imports_labels_statically(self):
        """Ensure no actual file in code/ghost_audit/ references tools.labels."""
        ghost_audit_dir = REPO_ROOT / "code" / "ghost_audit"
        for py_file in ghost_audit_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            self.assertNotIn(
                "tools.labels",
                content,
                f"File {py_file} contains forbidden reference to tools.labels",
            )
            self.assertNotIn(
                "sample_output.csv",
                content,
                f"File {py_file} contains forbidden reference to sample_output.csv",
            )


if __name__ == "__main__":
    unittest.main()
