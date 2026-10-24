import json
from typing import Any, Dict, List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..observation import CoverageRecord, Observation, extract_identifiers


def normalize_json_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Performs a hierarchical walk over JSON evidence files, tracking the enclosing
    section's captured_at, data_store/system_id, and collection.
    Emits one Observation per dict containing resource_id.
    """
    observations: List[Observation] = []
    coverage_records: List[CoverageRecord] = []

    with open(meta.abs_path, "r", encoding="utf-8") as f:
        root_data = json.load(f)

    file_time = (
        root_data.get("exported_at")
        or root_data.get("captured_at")
        or meta.captured_at
    )
    file_origin = (
        root_data.get("origin")
        or root_data.get("source")
        or meta.origin
    )

    # 1. Snapshot bundle: e.g. customer_data_snapshot_bundle_*.json
    if "snapshots" in root_data and isinstance(root_data["snapshots"], list):
        for snap_idx, snap in enumerate(root_data["snapshots"]):
            snap_time = snap.get("captured_at") or file_time
            snap_system = snap.get("system_id") or snap.get("data_store") or file_origin
            snap_coll = snap.get("collection") or snap.get("collection_name") or f"snapshot_{snap_idx}"
            records = snap.get("records", [])

            for rec_idx, rec in enumerate(records):
                if isinstance(rec, dict) and "resource_id" in rec and rec["resource_id"]:
                    r_id = str(rec["resource_id"])
                    rec_time = rec.get("updated_at") or rec.get("observed_at") or snap_time
                    identifiers = extract_identifiers(rec)
                    obs = Observation(
                        file_id=meta.file_id,
                        file_captured_at=meta.captured_at,
                        obs_time=rec_time,
                        system_id=snap_system,
                        collection=snap_coll,
                        resource_id=r_id,
                        identifiers=identifiers,
                        state=dict(rec),
                        source_kind="json",
                        raw_ref=f"snapshot:{snap_coll} idx:{rec_idx} id:{r_id}",
                    )
                    observations.append(obs)

            coverage_records.append(
                CoverageRecord(
                    file_id=meta.file_id,
                    file_captured_at=meta.captured_at,
                    system_id=snap_system,
                    collection=snap_coll,
                    obs_time=snap_time,
                    source_kind="json",
                    record_count=len(records),
                )
            )
        return observations, coverage_records, 0

    # 2. Service resource export: e.g. service_resource_export_*.json
    if "service_exports" in root_data and isinstance(root_data["service_exports"], dict):
        for svc_name, svc_content in root_data["service_exports"].items():
            if isinstance(svc_content, dict):
                for coll_name, items in svc_content.items():
                    if isinstance(items, list):
                        for it_idx, it in enumerate(items):
                            if isinstance(it, dict) and "resource_id" in it and it["resource_id"]:
                                r_id = str(it["resource_id"])
                                item_time = it.get("observed_at") or it.get("updated_at") or file_time
                                identifiers = extract_identifiers(it)
                                obs = Observation(
                                    file_id=meta.file_id,
                                    file_captured_at=meta.captured_at,
                                    obs_time=item_time,
                                    system_id=svc_name,
                                    collection=coll_name,
                                    resource_id=r_id,
                                    identifiers=identifiers,
                                    state=dict(it),
                                    source_kind="json",
                                    raw_ref=f"service_export:{svc_name}.{coll_name} idx:{it_idx} id:{r_id}",
                                )
                                observations.append(obs)

                        coverage_records.append(
                            CoverageRecord(
                                file_id=meta.file_id,
                                file_captured_at=meta.captured_at,
                                system_id=svc_name,
                                collection=coll_name,
                                obs_time=file_time,
                                source_kind="json",
                                record_count=len(items),
                            )
                        )
        return observations, coverage_records, 0

    # 3. Flat records list or generic walk
    if "records" in root_data and isinstance(root_data["records"], list):
        coll_name = root_data.get("collection") or meta.file_path.split("/")[-1].split(".")[0]
        records = root_data["records"]
        for rec_idx, rec in enumerate(records):
            if isinstance(rec, dict) and "resource_id" in rec and rec["resource_id"]:
                r_id = str(rec["resource_id"])
                rec_time = (
                    rec.get("recorded_at")
                    or rec.get("created_at")
                    or rec.get("observed_at")
                    or rec.get("updated_at")
                    or file_time
                )
                rec_sys = rec.get("system") or file_origin
                identifiers = extract_identifiers(rec)
                obs = Observation(
                    file_id=meta.file_id,
                    file_captured_at=meta.captured_at,
                    obs_time=rec_time,
                    system_id=rec_sys,
                    collection=coll_name,
                    resource_id=r_id,
                    identifiers=identifiers,
                    state=dict(rec),
                    source_kind="json",
                    raw_ref=f"records:{coll_name} idx:{rec_idx} id:{r_id}",
                )
                observations.append(obs)

        coverage_records.append(
            CoverageRecord(
                file_id=meta.file_id,
                file_captured_at=meta.captured_at,
                system_id=file_origin,
                collection=coll_name,
                obs_time=file_time,
                source_kind="json",
                record_count=len(records),
            )
        )
        return observations, coverage_records, 0

    return observations, coverage_records, 0
