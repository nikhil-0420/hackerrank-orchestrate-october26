"""
Unit test verifying that no hardcoded case IDs, evidence IDs, resource ID literals,
evaluation imports, or sample_output references exist within code/ghost_audit/.
"""

from pathlib import Path
import re
import unittest


class TestNoHardcoding(unittest.TestCase):
    """Enforces no hardcoding constraints across all modules in code/ghost_audit/."""

    def setUp(self):
        self.code_dir = Path(__file__).resolve().parent.parent / "code" / "ghost_audit"
        self.assertTrue(self.code_dir.is_dir(), f"Directory not found: {self.code_dir}")

    def test_no_hardcoded_literals_or_eval_imports(self):
        py_files = list(self.code_dir.rglob("*.py"))
        self.assertGreater(len(py_files), 0, "No python files found in code/ghost_audit")

        # Patterns to prohibit:
        patterns = [
            (re.compile(r"\bcase_\d+\b"), "case ID literal (case_\\d+)"),
            (re.compile(r"\bevidence_\d+\b"), "evidence ID literal (evidence_\\d+)"),
            (
                re.compile(r"\b(?:account|search|support|export|analytics|data_flow|backup|audit_record|tombstone)_\d+\b"),
                "resource ID literal (<type>_\\d+)",
            ),
            (re.compile(r"\b(?:import\s+evaluation|from\s+evaluation|import\s+code\.evaluation|from\s+code\.evaluation)\b"), "evaluation import"),
            (re.compile(r"sample_output"), "sample_output reference"),
        ]

        violations = []

        for py_file in py_files:
            rel_path = py_file.relative_to(self.code_dir)
            content = py_file.read_text(encoding="utf-8", errors="replace")

            for line_idx, line in enumerate(content.splitlines(), start=1):
                for regex, desc in patterns:
                    match = regex.search(line)
                    if match:
                        violations.append(
                            f"{rel_path}:{line_idx} - matched {desc}: '{match.group(0)}' in line: {line.strip()}"
                        )

        self.assertEqual(violations, [], "Found prohibited hardcoded values or imports in code/ghost_audit:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
