"""
Evidence signals for resource attribution.

Signals in descending order of strength:
  S1: Direct identifier (email, phone, hash, name) in the same record.
  S2: user_id joins (customer_reference, lookup_key, subject_reference, user_ref).
  S3: Merged trace identity (produced by log normalizer).
  S4: LINK_RESOURCE_IDENTITY rows from system_activity.csv.
  S5: Chain keys (source_resource_id, object_key, archive_key, parent_resource_id) 1-hop traversal.
  S6: Handover documents (TXT, PDF, PNG) containing identifiers or resource IDs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.activity import ActivityLog, SystemActivityRow
from ghost_audit.identity import IdentityResolver, ResolvedIdentity, match_user_id
from ghost_audit.observation import Observation
from ghost_audit.paths import EVIDENCE_DIR
from ghost_audit.timegate import visible_state

VALID_PREFIXES = (
    "account_",
    "search_",
    "support_",
    "export_",
    "analytics_",
    "data_flow_",
    "backup_",
    "audit_record_",
    "tombstone_",
)

RESOURCE_REGEX = re.compile(
    r"\b(?:account|search|support|export|analytics|data_flow|backup|audit_record|tombstone)_[a-zA-Z0-9_]+\b"
)


def is_valid_resource_id(r: str) -> bool:
    """Check if string has a valid known resource prefix."""
    if not isinstance(r, str):
        return False
    return any(r.startswith(p) for p in VALID_PREFIXES)


@dataclass(frozen=True)
class Signal:
    """Represents a discrete signal linking a resource to a case/identity."""

    resource_id: str
    signal_name: str
    evidence_ref: str
    strength: float
    system_id: Optional[str] = None
    file_id: Optional[str] = None
    obs_time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def collect_hard_signals_for_case(
    case_id: str,
    requested_at: str,
    audit_at: str,
    identity: ResolvedIdentity,
    all_observations: list[Observation],
    activity: ActivityLog,
    obs_by_res: dict[str, list[Observation]],
    documents_dir: Optional[Path] = None,
) -> list[Signal]:
    """
    Collect all hard signals (S1 through S6) linking resources to the given user identity.
    Returns a deduplicated list of Signal objects.
    """
    signals: list[Signal] = []
    seen: set[tuple[str, str, str]] = set()

    def add_signal(sig: Signal) -> None:
        if not is_valid_resource_id(sig.resource_id):
            return
        key = (sig.resource_id, sig.signal_name, sig.evidence_ref)
        if key not in seen:
            seen.add(key)
            signals.append(sig)

    # 1. S1, S2, S3 from Evidence Observations
    for obs in all_observations:
        r_id = obs.resource_id
        if not is_valid_resource_id(r_id):
            continue

        # Time-gate check: visible state at or before audit cutoff
        if not visible_state(obs, audit_at):
            continue

        # Exclude historical negative/not-found lookups before the deletion request was made
        if (obs.state.get("rows") == "0" or obs.state.get("http_status") == "404") and obs.obs_time < requested_at:
            continue

        sys_id = obs.system_id
        s1_matched = False

        # S1: Direct identifiers
        if obs.identifiers:
            # Email exact lowercase match
            if obs.identifiers.email and obs.identifiers.email.lower().strip() in identity.emails:
                add_signal(Signal(r_id, "S1_IDENTIFIER", f"{obs.file_id}:{obs.raw_ref}", 1.0, sys_id, obs.file_id, obs.obs_time))
                s1_matched = True
            elif obs.identifiers.phone and obs.identifiers.phone.strip() in identity.phones:
                add_signal(Signal(r_id, "S1_IDENTIFIER", f"{obs.file_id}:{obs.raw_ref}", 1.0, sys_id, obs.file_id, obs.obs_time))
                s1_matched = True
            elif obs.identifiers.email_hash and obs.identifiers.email_hash.lower().strip() in identity.hashes:
                add_signal(Signal(r_id, "S1_IDENTIFIER", f"{obs.file_id}:{obs.raw_ref}", 1.0, sys_id, obs.file_id, obs.obs_time))
                s1_matched = True
            elif (
                obs.identifiers.name
                and identity.name
                and obs.identifiers.name.strip().lower() == identity.name.strip().lower()
            ):
                add_signal(Signal(r_id, "S1_IDENTIFIER", f"{obs.file_id}:{obs.raw_ref}", 0.98, sys_id, obs.file_id, obs.obs_time))
                s1_matched = True

        # Check for 64-char sha256 hashes in state dict
        if not s1_matched:
            for k, v in obs.state.items():
                if isinstance(v, str) and len(v) == 64 and v.lower() in identity.hashes:
                    add_signal(Signal(r_id, "S1_IDENTIFIER", f"{obs.file_id}:{k}={v}", 1.0, sys_id, obs.file_id, obs.obs_time))
                    s1_matched = True
                    break

        # S2: user_id joins
        if obs.identifiers and obs.identifiers.user_ref and match_user_id(obs.identifiers.user_ref, identity.user_id):
            add_signal(Signal(r_id, "S2_USER_ID", f"{obs.file_id}:{obs.raw_ref}", 0.95, sys_id, obs.file_id, obs.obs_time))
        else:
            for k, v in obs.state.items():
                if k.lower() in ("customer_reference", "lookup_key", "subject_reference", "user_ref", "user_id", "subject_key"):
                    if v and match_user_id(str(v), identity.user_id):
                        add_signal(Signal(r_id, "S2_USER_ID", f"{obs.file_id}:{k}={v}", 0.95, sys_id, obs.file_id, obs.obs_time))
                        break

        # S3: Merged trace identity
        if ("trace:" in obs.raw_ref or "trace_id" in obs.state) and (
            s1_matched or (obs.identifiers and obs.identifiers.user_ref and match_user_id(obs.identifiers.user_ref, identity.user_id))
        ):
            add_signal(Signal(r_id, "S3_MERGED_TRACE", f"{obs.file_id}:{obs.raw_ref}", 0.90, sys_id, obs.file_id, obs.obs_time))

    # 2. S4: LINK_RESOURCE_IDENTITY rows
    for link in activity.link_rows(audit_at=audit_at):
        link_email = (link.get("email") or "").lower().strip()
        link_uid = (link.get("user_id") or "").strip()
        r_id = link.get("resource_id", "").strip()
        if not is_valid_resource_id(r_id):
            continue
        ev_time = link.get("event_time", "")
        if ev_time and ev_time < requested_at and r_id not in obs_by_res:
            continue

        if (link_email and link_email in identity.emails) or (link_uid and match_user_id(link_uid, identity.user_id)):
            add_signal(Signal(r_id, "S4_LINK_ROW", f"system_activity:{link.get('activity_id', '')}", 0.85, metadata=link))

    # 3. S6: Handover documents (TXT, PDF, PNG text)
    docs_path = documents_dir if documents_dir else EVIDENCE_DIR / "documents"
    if docs_path.exists():
        for p in docs_path.glob("*.pdf"):
            try:
                from ghost_audit.loaders.pdf_loader import extract_pdf_text

                txt = extract_pdf_text(p)
                has_ident = (
                    any(em in txt.lower() for em in identity.emails)
                    or match_user_id(txt, identity.user_id)
                    or (identity.phones and any(ph in txt for ph in identity.phones))
                )
                if has_ident:
                    res_matches = RESOURCE_REGEX.findall(txt)
                    for r_id in res_matches:
                        if is_valid_resource_id(r_id):
                            add_signal(Signal(r_id, "S6_HANDOVER_DOC", f"{p.name}", 0.75))
            except Exception:
                pass

        for p in docs_path.glob("*.txt"):
            try:
                txt = p.read_text(encoding="utf-8")
                has_ident = (
                    any(em in txt.lower() for em in identity.emails)
                    or match_user_id(txt, identity.user_id)
                    or (identity.phones and any(ph in txt for ph in identity.phones))
                )
                if has_ident:
                    res_matches = RESOURCE_REGEX.findall(txt)
                    for r_id in res_matches:
                        if is_valid_resource_id(r_id):
                            add_signal(Signal(r_id, "S6_HANDOVER_DOC", f"{p.name}", 0.75))
            except Exception:
                pass

    # 4. S5: Chain keys (1 hop from existing hard resources)
    current_resources = {s.resource_id for s in signals}
    for r_id in list(current_resources):
        for o in obs_by_res.get(r_id, []):
            for k in ("source_resource_id", "object_key", "archive_key", "parent_resource_id"):
                if k in o.state and o.state[k]:
                    val = str(o.state[k])
                    m = RESOURCE_REGEX.search(val)
                    if m:
                        target_r_id = m.group(0)
                        if is_valid_resource_id(target_r_id) and target_r_id not in current_resources:
                            add_signal(Signal(target_r_id, "S5_CHAIN_KEY", f"{o.file_id}:{k}={val}", 0.80))
                            current_resources.add(target_r_id)

    # Sort signals strongest first
    signals.sort(key=lambda s: -s.strength)
    return signals
