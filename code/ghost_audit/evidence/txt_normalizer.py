import re
from typing import List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..observation import CoverageRecord, Observation, extract_identifiers


def normalize_txt_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Parses handover text files with format:
    time | system | resource | CATEGORY | STATE | identifier
    """
    observations: List[Observation] = []
    coverage_records: List[CoverageRecord] = []
    unparsed_count = 0

    snapshot_time = meta.captured_at

    with open(meta.abs_path, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            raw = line.strip()
            if not raw:
                continue

            # Header / section titles
            if raw.startswith("CUSTOMER PLATFORM") or raw.startswith("Account and downstream checks"):
                continue

            if raw.startswith("Snapshot:"):
                snapshot_time = raw.split(":", 1)[1].strip()
                continue

            # Handover record line: - time | system | resource | CATEGORY | STATE | identifier
            clean_line = raw.lstrip("- ").strip()
            parts = [p.strip() for p in clean_line.split("|")]
            if len(parts) == 6:
                obs_time, system, resource, category, state_val, identifier = parts

                id_map = {}
                if identifier and identifier != "no direct identifier":
                    if "@" in identifier:
                        id_map["email"] = identifier
                    elif identifier.startswith("user_"):
                        id_map["user_ref"] = identifier
                    else:
                        id_map["lookup_key"] = identifier

                identifiers = extract_identifiers(id_map)
                obs_state = {
                    "category": category,
                    "state": state_val,
                    "result": state_val,
                    "raw_identifier": identifier,
                }

                obs = Observation(
                    file_id=meta.file_id,
                    file_captured_at=meta.captured_at,
                    obs_time=obs_time or snapshot_time,
                    system_id=system,
                    collection=category.lower(),
                    resource_id=resource,
                    identifiers=identifiers,
                    state=obs_state,
                    source_kind="txt",
                    raw_ref=f"line:{lno} id:{resource}",
                )
                observations.append(obs)
            else:
                unparsed_count += 1

    coverage_records.append(
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="shift_handover",
            obs_time=snapshot_time,
            source_kind="txt",
            record_count=len(observations),
        )
    )

    return observations, coverage_records, unparsed_count
