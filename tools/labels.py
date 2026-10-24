"""
DEV-ONLY label extractor for sample ground truth.
Reads dataset/sample_output.csv and yields:
(case_id, resource_id, system_id, role)
where role is 'finding', 'remediation', or 'verification'.

STRICT CONSTRAINTS:
This module is for evaluation and developer verification only.
It MUST NOT be imported from any module under ghost_audit/.
"""

import csv
import inspect
import json
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_OUTPUT_PATH = REPO_ROOT / "dataset" / "sample_output.csv"


def _guard_no_ghost_audit():
    """Ensure ghost_audit never imports or calls this module."""
    for frame_info in inspect.stack():
        module = inspect.getmodule(frame_info.frame)
        if module and module.__name__.startswith("ghost_audit"):
            raise ImportError(
                f"Forbidden import: ghost_audit module '{module.__name__}' attempted to access tools.labels"
            )
        f_name = frame_info.frame.f_globals.get("__name__", "")
        if f_name.startswith("ghost_audit"):
            raise ImportError(
                f"Forbidden import: ghost_audit module '{f_name}' attempted to access tools.labels"
            )


_guard_no_ghost_audit()


def iter_sample_labels(
    path: Path | str | None = None,
) -> Iterator[tuple[str, str, str, str]]:
    """
    Yields (case_id, resource_id, system_id, role) for each step in sample_output.csv.
    role is one of 'finding', 'remediation', 'verification'.
    """
    _guard_no_ghost_audit()
    p = Path(path) if path else SAMPLE_OUTPUT_PATH
    if not p.exists():
        return

    with open(p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["case_id"].strip()
            raw_steps = row.get("steps_json", "[]")
            steps = json.loads(raw_steps)
            for s in steps:
                res_id = s.get("resource_id", "").strip()
                sys_id = s.get("system_id", "").strip()
                phase = s.get("phase", "").strip().lower()
                yield (cid, res_id, sys_id, phase)


def load_case_resource_labels(
    path: Path | str | None = None,
) -> dict[str, set[tuple[str, str, str]]]:
    """
    Returns a mapping of case_id -> set of (resource_id, system_id, role).
    """
    _guard_no_ghost_audit()
    labels_by_case = {}
    for cid, res_id, sys_id, role in iter_sample_labels(path):
        labels_by_case.setdefault(cid, set()).add((res_id, sys_id, role))
    return labels_by_case


if __name__ == "__main__":
    count = 0
    cases = set()
    for cid, res_id, sys_id, role in iter_sample_labels():
        count += 1
        cases.add(cid)
    print(f"Loaded {count} step labels across {len(cases)} sample cases.")
