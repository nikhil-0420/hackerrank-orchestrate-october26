from collections import defaultdict
from typing import Dict, List, Optional
from ..observation import CoverageRecord
from ..timegate import _parse_iso


class CoverageIndex:
    """
    Index of coverage records across all evidence snapshots and tables.
    Used to distinguish between 'absent from a covering snapshot' and 'not covered'.
    """

    def __init__(self, records: List[CoverageRecord] = None):
        self.records: List[CoverageRecord] = records or []
        self._by_system_collection: Dict[tuple, List[CoverageRecord]] = defaultdict(list)
        for r in self.records:
            key = (r.system_id.lower(), r.collection.lower())
            self._by_system_collection[key].append(r)

    def add(self, record: CoverageRecord) -> None:
        self.records.append(record)
        key = (record.system_id.lower(), record.collection.lower())
        self._by_system_collection[key].append(record)

    def is_covered(self, system_id: str, collection: str, audit_at: str) -> bool:
        """
        Returns True if at least one snapshot covering system_id and collection
        was captured at or before audit_at cutoff.
        """
        key = (system_id.lower(), collection.lower())
        records = self._by_system_collection.get(key, [])
        for r in records:
            try:
                if _parse_iso(r.obs_time) <= _parse_iso(audit_at) and _parse_iso(r.file_captured_at) <= _parse_iso(audit_at):
                    return True
            except Exception:
                if r.obs_time <= audit_at and r.file_captured_at <= audit_at:
                    return True
        return False

    def covering_snapshots(self, system_id: str, collection: str) -> List[CoverageRecord]:
        key = (system_id.lower(), collection.lower())
        return list(self._by_system_collection.get(key, []))
