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
    """Checks whether an observation explicitly records a lookup miss / 404 / NOT_FOUND / DELETED."""
    if not isinstance(obs.state, dict):
        return False
    state = obs.state
    # Check status_code or http_status
    if str(state.get("status_code", "")).strip() == "404" or str(state.get("http_status", "")).strip() == "404":
        return True
    if "profile" in state and state["profile"] is None:
        return True
    if "tombstone" not in obs.collection.lower() and "deleted_customer_reference" not in obs.collection.lower() and not str(obs.resource_id).startswith("tombstone_"):
        if str(state.get("account_status", "")).strip().upper() == "DELETED":
            return True
    if str(state.get("rows", "")).strip() == "0":
        return True
    # Check result or state string
    result_val = str(state.get("result", "")).strip().lower().strip('"\'')
    if result_val in ABSENT_STATUS_VALUES:
        return True
    st_val = str(state.get("state", "")).strip().lower().strip('"\'')
    if st_val in ABSENT_STATUS_VALUES:
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
                if "@" in v and not v.endswith("@") and "..." not in v:
                    import re
                    m = re.search(r"\b([a-zA-Z0-9_\.\-\+]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,})\b", v)
                    if m and not m.group(0).startswith("***"):
                        pii["email"] = m.group(0)
                elif "phone" in kl:
                    pii["phone"] = v
                elif kl in ("name", "full_name", "display_name"):
                    pii["name"] = v
                elif "hash" in kl and len(v) in (32, 64):
                    pii["email_hash"] = v
    return pii


from ghost_audit.category import normalize_system_id


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
    2. Check covering snapshots (json, sql, txt) at or before audit_at.
    3. A later covering snapshot or observation of absence supersedes an earlier presence.
       Presence in another replica captured at or before audit_at still counts as present
       if that replica snapshot is later than or equal to the absence observation.
    4. If no observation exists:
       - If a covering snapshot exists at/before audit_at, state is ABSENT.
       - Otherwise state is UNKNOWN.
    """
    visible_obs = [o for o in observations if visible_state(o, audit_at)]

    # Collect covering snapshots from coverage_index
    # Real covering snapshots are structured data stores: json, sql, txt
    covering_snaps = []
    if coverage_index is not None:
        target_col = collection_hint or "*"
        for c in coverage_index.records:
            if c.source_kind in ("json", "sql", "txt"):
                sys_match = (
                    c.system_id.lower() == system_id.lower()
                    or normalize_system_id(c.system_id) == normalize_system_id(system_id)
                )
                if not sys_match:
                    continue
                if target_col != "*":
                    if c.collection.lower() != target_col.lower():
                        continue
                try:
                    if parse_iso_ts(c.obs_time) <= parse_iso_ts(audit_at) and parse_iso_ts(c.file_captured_at) <= parse_iso_ts(audit_at):
                        covering_snaps.append(c)
                except Exception:
                    pass

    # Sort covering snapshots deterministically by obs_time ascending, then file_id
    covering_snaps.sort(key=lambda c: (parse_iso_ts(c.obs_time), c.file_id))

    # Identify covering snapshots that do NOT contain resource_id
    covering_absent_snaps = []
    for c in covering_snaps:
        in_file = any(o.file_id == c.file_id for o in visible_obs)
        if not in_file:
            covering_absent_snaps.append(c)

    # 1. No visible observations: check coverage index
    if not visible_obs:
        is_covered = False
        if coverage_index is not None:
            target_col = collection_hint or "*"
            if target_col != "*":
                is_covered = coverage_index.is_covered(system_id, target_col, audit_at)
            else:
                for c_rec in coverage_index.records:
                    sys_match = (
                        c_rec.system_id.lower() == system_id.lower()
                        or normalize_system_id(c_rec.system_id) == normalize_system_id(system_id)
                    )
                    if sys_match:
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

    # 2. Partition visible observations
    visible_obs.sort(key=lambda o: (parse_iso_ts(o.obs_time), o.file_id))
    present_obs = [o for o in visible_obs if not _is_explicit_absence(o)]
    absent_obs = [o for o in visible_obs if _is_explicit_absence(o)]

    conflict_notes = None

    if present_obs:
        latest_present = max(present_obs, key=lambda o: parse_iso_ts(o.obs_time))
        t_pres = parse_iso_ts(latest_present.obs_time)
        t_pres_file = parse_iso_ts(latest_present.file_captured_at)

        # Check latest explicit absence
        latest_explicit_absent = max(absent_obs, key=lambda o: parse_iso_ts(o.obs_time)) if absent_obs else None

        # Check covering snapshots that are strictly LATER than latest_present observation
        # and captured after latest_present file was captured
        qualifying_cov_absent = []
        for c in covering_absent_snaps:
            t_cov_obs = parse_iso_ts(c.obs_time)
            t_cov_file = parse_iso_ts(c.file_captured_at)
            if t_cov_obs > t_pres and t_cov_file >= t_pres_file:
                qualifying_cov_absent.append(c)

        latest_cov_absent = qualifying_cov_absent[-1] if qualifying_cov_absent else None

        t_abs = None
        abs_source = None
        if latest_explicit_absent and latest_cov_absent:
            t_exp = parse_iso_ts(latest_explicit_absent.obs_time)
            t_cov = parse_iso_ts(latest_cov_absent.obs_time)
            if t_exp >= t_cov:
                t_abs = t_exp
                abs_source = latest_explicit_absent
            else:
                t_abs = t_cov
                abs_source = latest_cov_absent
        elif latest_explicit_absent:
            t_abs = parse_iso_ts(latest_explicit_absent.obs_time)
            abs_source = latest_explicit_absent
        elif latest_cov_absent:
            t_abs = parse_iso_ts(latest_cov_absent.obs_time)
            abs_source = latest_cov_absent

        if t_abs is not None:
            if t_pres > t_abs:
                chosen = latest_present
                chosen_status = "PRESENT"
                conflict_notes = f"conflict: present at {latest_present.obs_time} superseded absent at {abs_source.obs_time if hasattr(abs_source, 'obs_time') else str(abs_source)}"
            elif t_pres == t_abs:
                chosen = latest_present
                chosen_status = "PRESENT"
                conflict_notes = f"conflict: concurrent present and absent at {latest_present.obs_time}; replica presence wins"
            else:
                # t_abs > t_pres: absence supersedes earlier presence
                chosen_status = "ABSENT"
                if isinstance(abs_source, Observation):
                    chosen = abs_source
                else:
                    chosen = None
                conflict_notes = f"conflict: absent at {t_abs.isoformat()} superseded present at {latest_present.obs_time}"
        else:
            chosen = latest_present
            chosen_status = "PRESENT"
    else:
        chosen = absent_obs[-1]
        chosen_status = "ABSENT"

    # Replica info extraction
    replica_info = None
    if chosen and isinstance(chosen.state, dict):
        rep = chosen.state.get("replica_of") or chosen.state.get("table_name")
        if rep:
            replica_info = str(rep)

    # PII extraction
    pii = _extract_direct_pii(chosen) if chosen else {}
    has_pii = bool(pii)

    # Active flow / backup restore risk checks
    is_active = False
    is_blocked_or_disabled = False
    if chosen and isinstance(chosen.state, dict):
        st = chosen.state
        # State / Result value checks
        state_str = str(st.get("state") or st.get("result") or "").strip().upper()
        if state_str == "ACTIVE":
            is_active = True
        elif state_str in ("DISABLED", "BLOCKED"):
            is_blocked_or_disabled = True

        # Data flow
        if "enabled" in st:
            en_val = st["enabled"]
            if en_val is True or str(en_val).lower() in ("true", "1"):
                is_active = True
            elif en_val is False or str(en_val).lower() in ("false", "0"):
                is_blocked_or_disabled = True
        # Backup restore
        if "restore_allowed" in st:
            ra_val = st["restore_allowed"]
            if ra_val is True or str(ra_val).lower() in ("true", "1"):
                is_active = True
            elif ra_val is False or str(ra_val).lower() in ("false", "0"):
                is_blocked_or_disabled = True
        if "decision" in st:
            dec_val = str(st["decision"]).strip().lower()
            if dec_val in ("deny", "denied", "blocked"):
                is_blocked_or_disabled = True
            elif dec_val in ("allow", "allowed", "permit", "permitted"):
                is_active = True
        if "deletion_block" in st:
            db_val = st["deletion_block"]
            if db_val is False or str(db_val).lower() in ("false", "0"):
                is_active = True
            elif db_val is True or str(db_val).lower() in ("true", "1"):
                is_blocked_or_disabled = True

    # Tombstone check
    is_tomb = False
    if chosen:
        is_tomb = (
            chosen.system_id == "identity_service"
            or "tombstone" in chosen.collection.lower()
            or resource_id.startswith("tombstone_")
        )
    elif resource_id.startswith("tombstone_"):
        is_tomb = True

    # Retention check
    retention_val = None
    if chosen and isinstance(chosen.state, dict):
        retention_val = chosen.state.get("retention_until") or chosen.state.get("retained_until")

    return ResourceState(
        resource_id=resource_id,
        system_id=system_id,
        status=chosen_status,
        obs_time=chosen.obs_time if chosen else (latest_cov_absent.obs_time if latest_cov_absent else None),
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
