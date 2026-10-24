from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Identifiers:
    """Standardized identity fields extracted from evidence records."""
    email: Optional[str] = None
    phone: Optional[str] = None
    email_hash: Optional[str] = None
    user_ref: Optional[str] = None      # user_id, customer_reference, subject_reference
    name: Optional[str] = None          # full_name, display_name, requester_name
    masked: bool = False                # True if any key was masked/truncated (e.g. lucia-torres@gmail.)
    raw_identifiers: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Observation:
    """
    Normalized observation extracted from an evidence file.
    Represents one record/finding at a specific point in time within a file.
    """
    file_id: str
    file_captured_at: str               # Captured timestamp from evidence_files.csv manifest
    obs_time: str                       # Row/section/log timestamp (observed_at, updated_at, captured_at)
    system_id: str                      # Originating system (e.g. account_service, search_service)
    collection: str                     # Collection or table name (e.g. customer_profiles, search_documents)
    resource_id: str                    # Unique resource identifier (e.g. res_005, res_123)
    identifiers: Identifiers
    state: Dict[str, Any]               # Observed status, flags, replication info (immutable copy)
    source_kind: str                    # File category: 'sql', 'json', 'log', 'txt', 'pdf', 'image'
    raw_ref: str                        # Pointer back to original line, row, or section for traceability


@dataclass(frozen=True)
class CoverageRecord:
    """
    Tracks snapshot sections and table scopes so the auditor can determine
    whether a system/collection was covered at a particular obs_time.
    Distinguishes 'absent from a covering snapshot' from 'not covered'.
    """
    file_id: str
    file_captured_at: str
    system_id: str
    collection: str
    obs_time: str
    source_kind: str
    record_count: int = 0


def extract_identifiers(data: Dict[str, Any]) -> Identifiers:
    """
    Extract and normalize personal identifiers from an arbitrary key-value mapping.
    Recursively inspects nested structures (e.g. document, profile, hits).
    Detects whether values are masked or truncated (e.g. 'lucia-torres@gmail.').
    """
    email = None
    phone = None
    email_hash = None
    user_ref = None
    name = None
    is_masked = False
    raw_found = {}

    flat_items = []

    def _collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    _collect(v)
                else:
                    flat_items.append((k, v))
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)

    _collect(data)

    for k, v in flat_items:
        if v is None or v == "" or v == "null" or v == "None":
            continue
        v_str = str(v).strip()
        if not v_str:
            continue

        k_lower = k.lower()

        # Check for masking
        if v_str.endswith(".") or v_str.endswith("@") or "*" in v_str or "..." in v_str:
            is_masked = True

        if k_lower in ("email", "customer_email", "owner_email", "requester_email"):
            if not email:
                email = v_str
            raw_found[k] = v_str
        elif k_lower in ("phone", "owner_phone", "requester_phone"):
            if not phone:
                phone = v_str
            raw_found[k] = v_str
        elif k_lower in ("email_hash",):
            if not email_hash:
                email_hash = v_str
            raw_found[k] = v_str
        elif k_lower in ("customer_reference", "user_id", "subject_reference", "subject_ref", "user_ref"):
            if not user_ref:
                user_ref = v_str
            raw_found[k] = v_str
        elif k_lower in ("full_name", "display_name", "requester_name", "name"):
            if not name:
                name = v_str
            raw_found[k] = v_str
        elif k_lower in ("lookup_key", "match_key", "correlation_key", "subject_key"):
            raw_found[k] = v_str
            if "@" in v_str:
                if not email:
                    email = v_str
            elif v_str.startswith("user_"):
                if not user_ref:
                    user_ref = v_str

    # Secondary check on email/user_ref if still None
    if not email and user_ref and "@" in user_ref:
        email = user_ref
        user_ref = None

    return Identifiers(
        email=email,
        phone=phone,
        email_hash=email_hash,
        user_ref=user_ref,
        name=name,
        masked=is_masked,
        raw_identifiers=raw_found,
    )


