"""
Output emitter for Ghost Audit.
Formats case decisions into compliant canonical CSV output.
"""

from __future__ import annotations

import csv
from pathlib import Path
import re
from typing import Iterable, List, Union

from ghost_audit.planner import CaseDecision


def natural_sort_key(s: str) -> list[Union[int, str]]:
    """Helper to split string into string and integer chunks for natural sorting."""
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", s)
    ]


def emit_output_file(
    decisions: Iterable[CaseDecision],
    out_path: Union[str, Path],
    id_sort: str = "natural",
) -> None:
    """
    Writes case decisions to CSV at out_path in specified case_id sort order.

    CSV format:
      case_id,deletion_status,steps_json
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    decision_list: List[CaseDecision] = list(decisions)

    if id_sort == "natural":
        decision_list.sort(key=lambda d: natural_sort_key(d.case_id))
    elif id_sort == "lexical":
        decision_list.sort(key=lambda d: d.case_id)
    else:
        raise ValueError(f"Unknown id_sort mode: {id_sort}")

    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "deletion_status", "steps_json"])
        for d in decision_list:
            writer.writerow([d.case_id, d.deletion_status, d.steps_json])
