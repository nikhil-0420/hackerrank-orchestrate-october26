"""
Typed loader and query interface for dataset/system_activity.csv.
Time-gates all queries against case audit_at.
Treats reported_result strictly as a claim, never ground-truth state.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Any

from ghost_audit.paths import SYSTEM_ACTIVITY_PATH
from ghost_audit.timegate import visible_state


def parse_iso_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


@dataclass(frozen=True)
class SystemActivityRow:
    activity_id: str
    event_time: str
    event_type: str
    source_system: str
    target_system: str
    resource_id: str
    reported_result: str
    details: str

    def is_visible(self, audit_at: str | None) -> bool:
        if not audit_at:
            return True
        return parse_iso_ts(self.event_time) <= parse_iso_ts(audit_at)


EMAIL_RE = re.compile(r"\b([a-zA-Z0-9_\.\-\+]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,})\b")
USER_ID_RE = re.compile(r"\b(user_\d+)\b")


class ActivityLog:
    """In-memory collection of system activity events with time-gated query methods."""

    def __init__(self, rows: list[SystemActivityRow] | None = None, path: Path | str | None = None):
        if rows is not None:
            self.rows = rows
        else:
            p = Path(path) if path else SYSTEM_ACTIVITY_PATH
            self.rows = self._load_from_path(p)

    @staticmethod
    def _load_from_path(p: Path) -> list[SystemActivityRow]:
        if not p.exists():
            return []
        loaded: list[SystemActivityRow] = []
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                loaded.append(
                    SystemActivityRow(
                        activity_id=r.get("activity_id", "").strip(),
                        event_time=r.get("event_time", "").strip(),
                        event_type=r.get("event_type", "").strip(),
                        source_system=r.get("source_system", "").strip(),
                        target_system=r.get("target_system", "").strip(),
                        resource_id=r.get("resource_id", "").strip(),
                        reported_result=r.get("reported_result", "").strip(),
                        details=r.get("details", "").strip(),
                    )
                )
        return loaded

    @classmethod
    def load(cls, path: Path | str | None = None) -> ActivityLog:
        return cls(path=path)


    def _filter_time(self, rows: list[SystemActivityRow], audit_at: str | None) -> list[SystemActivityRow]:
        if not audit_at:
            return rows
        cutoff = parse_iso_ts(audit_at)
        return [r for r in rows if parse_iso_ts(r.event_time) <= cutoff]

    def anchors(self, audit_at: str | None = None) -> list[SystemActivityRow]:
        """
        Anchor rows:
        1. Account DELETE_RECORD rows executed by deletion_worker on account_service
        2. CLASSIFY_REQUEST rows (indicating intake non-deletion classification)
        """
        filtered = self._filter_time(self.rows, audit_at)
        results = []
        for r in filtered:
            is_dw_account_delete = (
                r.source_system == "deletion_worker"
                and r.target_system == "account_service"
                and r.event_type == "DELETE_RECORD"
            )
            is_classify = r.event_type == "CLASSIFY_REQUEST"
            if is_dw_account_delete or is_classify:
                results.append(r)
        return results

    def link_rows(self, audit_at: str | None = None) -> list[dict[str, Any]]:
        """
        Extracts structured identity links from LINK_RESOURCE_IDENTITY events.
        Parses resource_id, email, and user_id from details.
        """
        filtered = self._filter_time(self.rows, audit_at)
        links = []
        for r in filtered:
            if r.event_type == "LINK_RESOURCE_IDENTITY":
                email_match = EMAIL_RE.search(r.details)
                user_match = USER_ID_RE.search(r.details)

                email = email_match.group(1).lower() if email_match else ""
                user_id = user_match.group(1) if user_match else ""

                links.append({
                    "activity_id": r.activity_id,
                    "event_time": r.event_time,
                    "resource_id": r.resource_id,
                    "email": email,
                    "user_id": user_id,
                    "details": r.details,
                })
        return links

    def treatment_hint(self, resource_id: str, audit_at: str | None = None) -> str | None:
        """
        Returns the event_type of the deletion_worker row for resource_id if present.
        """
        filtered = self._filter_time(self.rows, audit_at)
        for r in filtered:
            if r.source_system == "deletion_worker" and r.resource_id == resource_id:
                return r.event_type
        return None

    def flow_actions(self, audit_at: str | None = None) -> list[SystemActivityRow]:
        """Events related to data flow checks or disabling."""
        filtered = self._filter_time(self.rows, audit_at)
        return [r for r in filtered if r.event_type in {"CHECK_DATA_FLOW", "DISABLE_DATA_FLOW"}]

    def restore_actions(self, audit_at: str | None = None) -> list[SystemActivityRow]:
        """Events related to restore access checks, blocking, or backup restoration."""
        filtered = self._filter_time(self.rows, audit_at)
        return [r for r in filtered if r.event_type in {"CHECK_RESTORE_ACCESS", "BLOCK_RESTORE", "RESTORE_BACKUP"}]

    def legal_rows(self, audit_at: str | None = None) -> list[SystemActivityRow]:
        """Events related to retention or legal holds."""
        filtered = self._filter_time(self.rows, audit_at)
        return [
            r for r in filtered
            if r.event_type == "RETAIN_RECORD"
            or "legal_hold" in r.source_system
            or "legal_hold" in r.target_system
            or "legal_hold" in r.details.lower()
        ]
