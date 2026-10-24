from pathlib import Path
from typing import Any, Dict, List, Tuple
from ..loaders.manifest import EvidenceFileMeta, load_manifest
from ..observation import CoverageRecord, Observation
from .doc_normalizer import normalize_pdf_file, normalize_png_file
from .json_normalizer import normalize_json_file
from .log_normalizer import normalize_log_file
from .sql_normalizer import normalize_sql_file
from .txt_normalizer import normalize_txt_file


def normalize_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Dispatches evidence file to its corresponding format normalizer.
    Returns (observations, coverage_records, unparsed_lines_count).
    """
    ext = meta.abs_path.suffix.lower()

    if ext == ".sql":
        return normalize_sql_file(meta)
    elif ext == ".json":
        return normalize_json_file(meta)
    elif ext == ".log":
        return normalize_log_file(meta)
    elif ext == ".txt":
        return normalize_txt_file(meta)
    elif ext == ".pdf":
        return normalize_pdf_file(meta)
    elif ext == ".png":
        return normalize_png_file(meta)
    else:
        raise ValueError(f"Unsupported evidence file extension: {ext} for {meta.file_path}")


def normalize_all_evidence(
    manifest_path: Path = None,
) -> Tuple[List[Observation], List[CoverageRecord], Dict[str, Dict[str, Any]]]:
    """
    Normalizes every evidence file listed in the manifest.
    Returns:
    - all_observations
    - all_coverage_records
    - per_file_stats: map from file_id to stats dict
    """
    from ..paths import MANIFEST_PATH

    mp = manifest_path or MANIFEST_PATH
    manifest = load_manifest(mp)

    all_obs: List[Observation] = []
    all_coverage: List[CoverageRecord] = []
    file_stats: Dict[str, Dict[str, Any]] = {}

    for meta in manifest:
        obs, cov, unparsed = normalize_file(meta)
        all_obs.extend(obs)
        all_coverage.extend(cov)
        file_stats[meta.file_id] = {
            "file_path": meta.file_path,
            "origin": meta.origin,
            "captured_at": meta.captured_at,
            "obs_count": len(obs),
            "unparsed_lines": unparsed,
            "source_kind": meta.abs_path.suffix.lower().lstrip("."),
        }

    return all_obs, all_coverage, file_stats
