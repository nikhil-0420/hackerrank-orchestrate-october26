"""
Time-gating functions for observations and evidence files.

Rules:
- visible_state(obs, audit_at): obs.obs_time <= audit_at (inclusive)
- citable(file_or_captured_at, audit_at): file_captured_at <= audit_at (inclusive)

Evidence captured after audit_at cannot be cited.
Observations with obs_time <= audit_at represent the visible state at audit cutoff.
"""

from datetime import datetime, timezone
from typing import Union
from .observation import Observation


def _parse_iso(ts: str) -> datetime:
    """Parse ISO-8601 timestamp string into timezone-aware datetime."""
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


parse_iso_ts = _parse_iso


def visible_state(obs: Observation, audit_at: str) -> bool:
    """
    Check if the observation state was observed at or before audit_at cutoff.
    obs.obs_time <= audit_at (inclusive)
    """
    try:
        return _parse_iso(obs.obs_time) <= _parse_iso(audit_at)
    except Exception:
        # Fallback to string comparison if parsing fails
        return obs.obs_time <= audit_at


def citable(file_or_captured_at: Union[str, Observation, dict], audit_at: str) -> bool:
    """
    Check if the evidence file was captured at or before audit_at cutoff.
    file_captured_at <= audit_at (inclusive)
    """
    if isinstance(file_or_captured_at, Observation):
        captured_at = file_or_captured_at.file_captured_at
    elif isinstance(file_or_captured_at, dict):
        captured_at = file_or_captured_at.get("captured_at") or file_or_captured_at.get("file_captured_at", "")
    else:
        captured_at = str(file_or_captured_at)

    try:
        return _parse_iso(captured_at) <= _parse_iso(audit_at)
    except Exception:
        return captured_at <= audit_at
