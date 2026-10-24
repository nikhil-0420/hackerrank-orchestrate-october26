"""
Resource state determination at audit_at cutoff.

Rules:
- State of a resource at audit_at = latest observation with obs_time <= audit_at.
- Presence in ANY visible replica counts as present (record which replica).
- Conflicts: later obs_time wins, log the conflict.
- Absence is proven only by a covering snapshot (coverage.py) that lacks the record;
  a non-covering file proves nothing.
- Output: present|absent|unknown plus the supporting observation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.observation import Observation
from ghost_audit.timegate import parse_iso_ts, visible_state

logger = logging.getLogger(__name__)


# Status values representing explicit absence in lookup events
ABSENT_STATUS_VALUES: Set[str] = {
    "not_found",
    "miss",
    "404",
    "deleted",
    "absent",
    "unregistered",
}


@dataclass(frozen=True)
class ResourceState:
    """Represents the determined state of a resource at audit_at."""

    resource_id: str
    system_id: str
    status: str                         # "PRESENT" | "ABSENT" | "UNKNOWN"
    obs_time: Optional[str] = None
    supporting_observation: Optional[Observation] = None
    replica_info: Optional[str] = None
    has_direct_identifiers: bool = False
    direct_identifiers: Dict[str, str] = field(default_factory=dict)
    is_active: bool = False             # data flow enabled=True or restore_allowed=True
    is_blocked_or_disabled: bool = False # data flow enabled=False or restore_allowed=False
    is_tombstone: bool = False
    retention_until: Optional[str] = None
    conflict_notes: Optional[str] = None


def _is_explicit_absence(obs: Observation) -> bool:
    """Checks whether an observation explicitly records a lookup miss / 404 / NOT_FOUND."""
    if not isinstance(obs.state, dict):
        return False
    state = obs.state
    # Check http_status
    if str(state.get("http_status", "")).strip() == "404":
        return True
    if str(state.get("rows", "")).strip() == "0":
        return True
    # Check result
    result_val = str(state.get("result", "")).strip().lower().strip('"\'')
    if result_val in ABSENT_STATUS_VALUES:
        return True
    # Check hits total in search queries
    hits = state.get("hits")
    if isinstance(hits, dict) and hits.get("total") == 0:
        return True
    return False


def _extract_direct_pii(obs: Observation) -> Dict[str, str]:
    """Extracts non-empty, unmasked direct PII (email, phone, name, email_hash)."""
    pii = {}
    if obs.identifiers:
        ident = obs.identifiers
        if ident.email and not ident.masked:
            pii["email"] = ident.email
        if ident.phone and not ident.masked:
            pii["phone"] = ident.phone
        if ident.name and not ident.masked:
            pii["name"] = ident.name
        if ident.email_hash and not ident.masked:
            pii["email_hash"] = ident.email_hash

    if isinstance(obs.state, dict):
        for k, v in obs.state.items():
            if v and isinstance(v, str) and not v.startswith("***"):
                kl = k.lower()
                if "email" in kl and "hash" not in kl and "@" in v:
                    pii["email"] = v
                elif "phone" in kl:
                    pii["phone"] = v
                elif kl in ("name", "full_name", "display_name"):
                    pii["name"] = v
                elif "hash" in kl and len(v) in (32, 64):
                    pii["email_hash"] = v
    return pii


def determine_resource_state(
    resource_id: str,
    system_id: str,
    observations: List[Observation],
    audit_at: str,
    coverage_index: Optional[CoverageIndex] = None,
    collection_hint: Optional[str] = None,
) -> ResourceState:
    """
    Determines the state of a resource at audit_at.

    Rules:
    1. Filter observations to visible ones (obs_time <= audit_at).
    2. If multiple observations exist, sort by obs_time ascending.
       - Presence in ANY visible replica counts as present.
       - If there are conflicting records (e.g. miss vs present): later obs_time wins.
       - If same obs_time: presence in any replica wins.
    3. If no observation exists:
       - Check coverage_index: if a covering snapshot exists at/before audit_at, state is ABSENT.
       - Otherwise state is UNKNOWN.
    """
    visible_obs = [o for o in observations if visible_state(o, audit_at)]

    if not visible_obs:
        # Check covering snapshot
        is_covered = False
        if coverage_index is not None:
            # Check covering snapshots for system_id
            target_col = collection_hint or "*"
            if target_col != "*":
                is_covered = coverage_index.is_covered(system_id, target_col, audit_at)
            else:
                for c_rec in coverage_index.records:
                    if c_rec.system_id.lower() == system_id.lower():
                        try:
                            if parse_iso_ts(c_rec.obs_time) <= parse_iso_ts(audit_at):
                                is_covered = True
                                break
                        except Exception:
                            pass

        if is_covered:
            return ResourceState(
                resource_id=resource_id,
                system_id=system_id,
                status="ABSENT",
                obs_time=None,
                supporting_observation=None,
            )
        else:
            return ResourceState(
                resource_id=resource_id,
                system_id=system_id,
                status="UNKNOWN",
                obs_time=None,
                supporting_observation=None,
            )

    # Sort observations deterministically by obs_time, then file_id
    visible_obs.sort(key=lambda o: (parse_iso_ts(o.obs_time), o.file_id))

    # Partition by presence vs explicit absence
    present_obs = [o for o in visible_obs if not _is_explicit_absence(o)]
    absent_obs = [o for o in visible_obs if _is_explicit_absence(o)]

    conflict_notes = None

    if present_obs and absent_obs:
        # Conflict exists between presence and absence
        latest_present = max(present_obs, key=lambda o: parse_iso_ts(o.obs_time))
        latest_absent = max(absent_obs, key=lambda o: parse_iso_ts(o.obs_time))
        t_pres = parse_iso_ts(latest_present.obs_time)
        t_abs = parse_iso_ts(latest_absent.obs_time)

        if t_pres > t_abs:
            chosen = latest_present
            chosen_status = "PRESENT"
            conflict_notes = f"conflict: present at {latest_present.obs_time} superseded absent at {latest_absent.obs_time}"
        elif t_abs > t_pres:
            chosen = latest_absent
            chosen_status = "ABSENT"
            conflict_notes = f"conflict: absent at {latest_absent.obs_time} superseded present at {latest_present.obs_time}"
        else:
            # Identical timestamps: presence in ANY replica counts as present
            chosen = latest_present
            chosen_status = "PRESENT"
            conflict_notes = f"conflict: concurrent present and absent at {latest_present.obs_time}; replica presence wins"
        logger.info(f"State conflict on {resource_id}: {conflict_notes}")
    elif present_obs:
        chosen = present_obs[-1]
        chosen_status = "PRESENT"
    else:
        chosen = absent_obs[-1]
        chosen_status = "ABSENT"

    # Replica info extraction
    replica_info = None
    if isinstance(chosen.state, dict):
        rep = chosen.state.get("replica_of") or chosen.state.get("table_name")
        if rep:
            replica_info = str(rep)

    # PII extraction
    pii = _extract_direct_pii(chosen)
    has_pii = bool(pii)

    # Active flow / backup restore risk checks
    is_active = False
    is_blocked_or_disabled = False
    if isinstance(chosen.state, dict):
        st = chosen.state
        # Data flow
        if "enabled" in st:
            en_val = st["enabled"]
            if en_val is True or str(en_val).lower() == "true":
                is_active = True
            elif en_val is False or str(en_val).lower() == "false":
                is_blocked_or_disabled = True
        # Backup restore
        if "restore_allowed" in st:
            ra_val = st["restore_allowed"]
            if ra_val is True or str(ra_val).lower() == "true":
                is_active = True
            elif ra_val is False or str(ra_val).lower() == "false":
                is_blocked_or_disabled = True
        if "deletion_block" in st:
            db_val = st["deletion_block"]
            if db_val is False or str(db_val).lower() == "false":
                is_active = True
            elif db_val is True or str(db_val).lower() == "true":
                is_blocked_or_disabled = True

    # Tombstone check
    is_tomb = (
        chosen.system_id == "identity_service"
        or "tombstone" in chosen.collection.lower()
        or resource_id.startswith("tombstone_")
    )

    # Retention check
    retention_val = None
    if isinstance(chosen.state, dict):
        retention_val = chosen.state.get("retention_until") or chosen.state.get("retained_until")

    return ResourceState(
        resource_id=resource_id,
        system_id=system_id,
        status=chosen_status,
        obs_time=chosen.obs_time,
        supporting_observation=chosen,
        replica_info=replica_info,
        has_direct_identifiers=has_pii,
        direct_identifiers=pii,
        is_active=is_active,
        is_blocked_or_disabled=is_blocked_or_disabled,
        is_tombstone=is_tomb,
        retention_until=retention_val,
        conflict_notes=conflict_notes,
    )
