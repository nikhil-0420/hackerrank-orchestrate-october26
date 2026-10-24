import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from ..paths import DATASET_DIR, MANIFEST_PATH


@dataclass(frozen=True)
class EvidenceFileMeta:
    file_id: str
    file_path: str
    origin: str
    captured_at: str
    abs_path: Path


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> List[EvidenceFileMeta]:
    """Load the evidence_files.csv manifest into a list of metadata objects."""
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = row["file_path"].strip()
            # relative to dataset dir if path starts with evidence/
            abs_p = (DATASET_DIR / rel).resolve()
            records.append(
                EvidenceFileMeta(
                    file_id=row["file_id"].strip(),
                    file_path=rel,
                    origin=row["origin"].strip(),
                    captured_at=row["captured_at"].strip(),
                    abs_path=abs_p,
                )
            )
    return records


def get_manifest_by_id(manifest_path: Path = MANIFEST_PATH) -> Dict[str, EvidenceFileMeta]:
    """Map file_id -> EvidenceFileMeta."""
    return {m.file_id: m for m in load_manifest(manifest_path)}
