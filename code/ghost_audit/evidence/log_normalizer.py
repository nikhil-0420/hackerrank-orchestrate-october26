import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..observation import CoverageRecord, Observation, extract_identifiers

# Known identifier keys across log grammars
IDENTIFIER_FIELD_NAMES = {
    "lookup_key", "match_key", "correlation_key", "customer_email",
    "customer_reference", "subject_key", "subject_ref", "subject_reference",
    "email", "phone", "user_id", "owner_email", "requester_email", "user_ref"
}


def _extract_kvs(text: str) -> Dict[str, str]:
    """Extract key=value and key=\"value\" pairs from freeform text."""
    res = {}
    for match in re.finditer(r'([a-zA-Z0-9_\-\.]+)=(?:"([^"]*)"|(\S+))', text):
        k = match.group(1)
        v = match.group(2) if match.group(2) is not None else match.group(3)
        if v and r'\"' in v:
            v = v.replace(r'\"', '"')
        res[k] = v
    return res


def parse_log_line(raw: str) -> Optional[Tuple[str, Optional[str], Optional[str], Optional[str], Dict[str, Any]]]:
    """
    Parses any of the 7 supported log grammars into:
    (timestamp, service_name, trace_id, event, kv_dict)
    Returns None if the line does not match any grammar.
    """
    raw = raw.strip()
    if not raw:
        return None

    # 1. Pure JSON line
    if raw.startswith("{") and raw.endswith("}"):
        try:
            d = json.loads(raw)
            ts = d.get("timestamp") or d.get("time") or d.get("@timestamp")
            svc = d.get("service") or d.get("logger")
            trace_id = d.get("trace_id") or d.get("trace") or d.get("requestId")
            event = d.get("event") or d.get("action")
            return ts, svc, trace_id, event, d
        except Exception:
            pass

    # 2. Timestamp-prefixed JSON: 2026-04-19T06:51:11Z {"severity":"DEBUG", ...}
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(\{.*\})$", raw)
    if m:
        ts_str, j_str = m.groups()
        try:
            d = json.loads(j_str)
            svc = d.get("service") or d.get("logger")
            trace_id = d.get("trace_id") or d.get("trace") or d.get("requestId")
            event = d.get("event") or d.get("action")
            return ts_str, svc, trace_id, event, d
        except Exception:
            pass

    # 3. Syslog RFC5424: 2026-08-22T10:51:11Z <15>1 node-1 account_service tr-4973247 - - level=DEBUG ...
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+<\d+>\d+\s+\S+\s+(\S+)\s+(\S+)\s+-\s+-\s+(.*)$", raw)
    if m:
        ts_str, svc_name, procid, rest = m.groups()
        kv = _extract_kvs(rest)
        trace_id = procid if procid != "-" else kv.get("trace_id")
        return ts_str, svc_name, trace_id, kv.get("event"), kv

    # 4. Cloud runtime export: 2026-09-30T11:51:01Z requestId=collector-4 level=DEBUG function=log_router message="..."
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+requestId=(\S+)\s+level=(\S+)\s+function=(\S+)\s+message=\"(.*)\"$", raw)
    if m:
        ts_str, req_id, level, fn_name, msg = m.groups()
        kv = _extract_kvs(msg)
        kv["level"] = level
        trace_id = req_id if req_id.startswith("tr-") else kv.get("trace_id", req_id)
        return ts_str, fn_name, trace_id, kv.get("event"), kv

    # 5. Application trace bracketed: 2026-07-28T05:51:18Z [DEBUG] [account_service] [tr-6074163] profile_lookup_started: ...
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+\[(\S+)\]\s+\[(\S+)\]\s+\[(\S+)\]\s+(?:(\S+):\s*)?(.*)$", raw)
    if m:
        ts_str, level, svc_name, token3, evt_prefix, rest = m.groups()
        kv = _extract_kvs(rest)
        kv["level"] = level
        trace_id = token3 if (token3.startswith("tr-") or token3.startswith("rb-")) else None
        event = evt_prefix if evt_prefix else kv.get("event")
        if event:
            kv["event"] = event
        return ts_str, svc_name, trace_id, event, kv

    # 6. Operations stream piped: 2026-07-03T07:51:30Z | DEBUG | log_router | collector-5 | export_started | ...
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.*)$", raw)
    if m:
        ts_str, level, svc_name, token4, evt, rest = m.groups()
        kv = _extract_kvs(rest)
        kv["level"] = level
        kv["event"] = evt
        trace_id = token4 if (token4.startswith("tr-") or token4.startswith("rb-")) else None
        return ts_str, svc_name, trace_id, evt, kv

    # 7. Record lookup log or standard key-value: e.g. 2026-03-15T07:00:00Z INFO service=... or 2026-09-15T08:51:43Z level=DEBUG service=...
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(?:(\w+)\s+)?(.*)$", raw)
    if m:
        ts_str, level_token, rest = m.groups()
        kv = _extract_kvs(rest)
        if level_token and "level" not in kv:
            kv["level"] = level_token
        svc_name = kv.get("service") or kv.get("system")
        trace_id = kv.get("trace_id")
        return ts_str, svc_name, trace_id, kv.get("event"), kv

    return None


def normalize_log_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Parses a log file, enforces grammar coverage, groups entries by trace_id,
    and emits one Observation per resource_id carrying merged identifiers.
    """
    observations: List[Observation] = []
    coverage_records: List[CoverageRecord] = []
    unparsed_count = 0

    traces: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    standalone_entries: List[Dict[str, Any]] = []

    with open(meta.abs_path, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            raw = line.strip()
            if not raw:
                continue
            parsed = parse_log_line(raw)
            if not parsed:
                unparsed_count += 1
                continue

            ts, svc, trace_id, event, kv = parsed
            entry = {
                "line": lno,
                "ts": ts or meta.captured_at,
                "svc": svc or meta.origin,
                "trace_id": trace_id,
                "event": event,
                "kv": kv,
                "raw": raw,
            }
            if trace_id:
                traces[trace_id].append(entry)
            else:
                standalone_entries.append(entry)

    # 1. Process traces grouped by trace_id
    for tr_id, entries in traces.items():
        # Merge identifiers, kv fields, and find all resource_ids
        merged_kvs: Dict[str, Any] = {}
        resource_ids: List[Tuple[str, str, str, int]] = []  # (resource_id, obs_time, svc, line_no)

        min_line = entries[0]["line"]
        max_line = entries[-1]["line"]
        trace_time = entries[-1]["ts"]
        trace_svc = entries[-1]["svc"]

        for e in entries:
            kv = e["kv"]
            # Accumulate all KV pairs
            for k, v in kv.items():
                if v is not None and v != "null" and v != "":
                    merged_kvs[k] = v

            if e["svc"]:
                trace_svc = e["svc"]

            # Record any resource_id mentioned
            if "resource_id" in kv and kv["resource_id"] and kv["resource_id"] != "null":
                r_id = str(kv["resource_id"])
                resource_ids.append((r_id, e["ts"], e["svc"] or trace_svc, e["line"]))

        if not resource_ids:
            # Trace contained no resource_id (e.g. heartbeat or export lifecycle event)
            continue

        identifiers = extract_identifiers(merged_kvs)

        # Emit one Observation per resource_id
        seen_res = set()
        for r_id, r_time, r_svc, r_line in resource_ids:
            if r_id in seen_res:
                continue
            seen_res.add(r_id)

            collection = (
                merged_kvs.get("index")
                or merged_kvs.get("collection")
                or merged_kvs.get("record_type")
                or merged_kvs.get("event")
                or "log_events"
            )

            state = dict(merged_kvs)
            state["trace_id"] = tr_id

            obs = Observation(
                file_id=meta.file_id,
                file_captured_at=meta.captured_at,
                obs_time=r_time or trace_time,
                system_id=r_svc or trace_svc or meta.origin,
                collection=str(collection),
                resource_id=r_id,
                identifiers=identifiers,
                state=state,
                source_kind="log",
                raw_ref=f"trace:{tr_id} lines:{min_line}-{max_line} id:{r_id}",
            )
            observations.append(obs)

    # 2. Process standalone lines (e.g. notification_delivery / search_index_diagnostic)
    for e in standalone_entries:
        kv = e["kv"]
        if "resource_id" in kv and kv["resource_id"] and kv["resource_id"] != "null":
            r_id = str(kv["resource_id"])
            identifiers = extract_identifiers(kv)
            svc = kv.get("system") or kv.get("service") or e["svc"] or meta.origin
            coll = kv.get("record_type") or kv.get("collection") or "record_lookup"

            obs = Observation(
                file_id=meta.file_id,
                file_captured_at=meta.captured_at,
                obs_time=e["ts"],
                system_id=str(svc),
                collection=str(coll),
                resource_id=r_id,
                identifiers=identifiers,
                state=dict(kv),
                source_kind="log",
                raw_ref=f"line:{e['line']} id:{r_id}",
            )
            observations.append(obs)

    coverage_records.append(
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="log_stream",
            obs_time=meta.captured_at,
            source_kind="log",
            record_count=len(observations),
        )
    )

    return observations, coverage_records, unparsed_count
