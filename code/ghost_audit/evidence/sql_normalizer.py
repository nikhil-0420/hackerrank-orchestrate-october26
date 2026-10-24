import json
import sqlite3
from typing import Dict, List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..observation import CoverageRecord, Observation, extract_identifiers

# Map tables to their owning systems when not explicitly stored in origin_system column
TABLE_SYSTEM_MAP = {
    "customer_profiles": "account_service",
    "customer_profiles_primary": "account_service",
    "customer_profiles_failover_replica": "account_service",
    "customer_analytics_profiles": "analytics_platform",
    "customer_search_documents": "search_service",
    "search_documents_primary": "search_service",
    "connector_subscriptions": "integration_service",
    "backup_restore_entries": "backup_service",
    "customer_exports": "export_service",
    "support_records": "support_platform",
    "security_audit_records": "security_service",
}


def normalize_sql_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Executes an evidence SQL file in an in-memory SQLite database,
    inspects all tables (primary and replicas), expands JSON columns,
    and returns normalized Observations, CoverageRecords, and unparsed line count (always 0).
    """
    observations: List[Observation] = []
    coverage_records: List[CoverageRecord] = []

    conn = sqlite3.connect(":memory:")
    try:
        with open(meta.abs_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn.executescript(sql_script)

        # 1. Inspect snapshot_scope if present
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='snapshot_scope';")
        scope_row = cur.fetchone()
        scope_system = None
        scope_time = meta.captured_at
        if scope_row:
            s_cur = conn.execute("SELECT origin_system, captured_at FROM snapshot_scope LIMIT 1;")
            s_res = s_cur.fetchone()
            if s_res:
                scope_system, scope_time = s_res[0], s_res[1]

        # 2. Inspect all data tables
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != 'snapshot_scope' ORDER BY name;"
        )
        tables = [r[0] for r in cur.fetchall()]

        for table in tables:
            r_cur = conn.execute(f"SELECT * FROM `{table}`;")
            cols = [d[0] for d in r_cur.description] if r_cur.description else []
            rows = r_cur.fetchall()

            table_system = (
                TABLE_SYSTEM_MAP.get(table)
                or scope_system
                or meta.origin
            )
            table_obs_time = scope_time

            for row_idx, row in enumerate(rows):
                row_dict = dict(zip(cols, row))
                resource_id = str(row_dict.get("resource_id", f"{table}_{row_idx}"))

                # Check if this table has an expanded record_json column
                if "record_json" in row_dict and row_dict["record_json"]:
                    origin_system = row_dict.get("origin_system") or table_system
                    collection_name = row_dict.get("collection_name") or table
                    row_time = row_dict.get("updated_at") or scope_time
                    try:
                        record_data = json.loads(row_dict["record_json"])
                    except Exception:
                        record_data = {}

                    merged_state = dict(record_data)
                    merged_state["replica_of"] = table
                    merged_state["table_name"] = table
                    if "updated_at" in row_dict:
                        merged_state["row_updated_at"] = row_dict["updated_at"]

                    identifiers = extract_identifiers(record_data)
                    obs = Observation(
                        file_id=meta.file_id,
                        file_captured_at=meta.captured_at,
                        obs_time=row_time,
                        system_id=origin_system,
                        collection=collection_name,
                        resource_id=resource_id,
                        identifiers=identifiers,
                        state=merged_state,
                        source_kind="sql",
                        raw_ref=f"table:{table} row_id:{resource_id}",
                    )
                    observations.append(obs)
                else:
                    # Typed table
                    row_time = (
                        row_dict.get("updated_at")
                        or row_dict.get("indexed_at")
                        or scope_time
                    )
                    merged_state = dict(row_dict)
                    merged_state["replica_of"] = table
                    merged_state["table_name"] = table

                    identifiers = extract_identifiers(row_dict)
                    obs = Observation(
                        file_id=meta.file_id,
                        file_captured_at=meta.captured_at,
                        obs_time=row_time,
                        system_id=table_system,
                        collection=table,
                        resource_id=resource_id,
                        identifiers=identifiers,
                        state=merged_state,
                        source_kind="sql",
                        raw_ref=f"table:{table} row_id:{resource_id}",
                    )
                    observations.append(obs)

            if meta.origin != "customer_data_inventory_capture":
                coverage_records.append(
                    CoverageRecord(
                        file_id=meta.file_id,
                        file_captured_at=meta.captured_at,
                        system_id=table_system,
                        collection=table,
                        obs_time=table_obs_time,
                        source_kind="sql",
                        record_count=len(rows),
                    )
                )

    finally:
        conn.close()

    return observations, coverage_records, 0
