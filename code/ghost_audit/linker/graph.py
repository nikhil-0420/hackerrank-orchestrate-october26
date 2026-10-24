"""
Resource attribution graph assembly and hard rule enforcement.

HARD RULE:
A resource is attributed to a user ONLY IF >= 1 hard signal (S1-S6) supports it,
except that S7/S8 may attach a deleted account or an anonymized analytics record
when no competing candidate remains. Everything else is UNATTRIBUTED and logged
with its candidates.

Outputs per case:
Attributed resources with the list of signals and the best citable file.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.observation import Observation
from ghost_audit.timegate import citable
from ghost_audit.linker.signals import Signal, is_valid_resource_id

SYSTEM_BY_PREFIX: Dict[str, str] = {
    "account_": "account_service",
    "search_": "search_service",
    "support_": "support_platform",
    "export_": "export_service",
    "analytics_": "analytics_platform",
    "data_flow_": "integration_service",
    "backup_": "backup_service",
    "audit_record_": "security_service",
    "tombstone_": "identity_service",
}

HARD_SIGNAL_NAMES: Set[str] = {
    "S1_IDENTIFIER",
    "S2_USER_ID",
    "S3_MERGED_TRACE",
    "S4_LINK_ROW",
    "S5_CHAIN_KEY",
    "S6_HANDOVER_DOC",
}

EXCEPTION_SIGNAL_NAMES: Set[str] = {
    "S7_ACCOUNT_ANCHOR",
    "S8_TUTORIAL_ACCOUNT",
    "S8_TUTORIAL_ANALYTICS",
    "S8_ANON_ANALYTICS",
}


def parse_iso(ts: str) -> datetime:
    """Parse ISO-8601 timestamp string into timezone-aware datetime."""
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def system_for_resource(resource_id: str, default: Optional[str] = None) -> str:
    """Derive system_id from resource_id prefix."""
    for prefix, sys_id in SYSTEM_BY_PREFIX.items():
        if resource_id.startswith(prefix):
            return sys_id
    return default or "unknown_service"


@dataclass(frozen=True)
class AttributedResource:
    """Represents a resource attributed to a case/user with supporting signals and evidence."""

    resource_id: str
    system_id: str
    signals: List[Signal]
    best_citable_file_id: Optional[str] = None


@dataclass(frozen=True)
class UnattributedResource:
    """Represents a candidate resource that failed attribution under the hard rule."""

    resource_id: str
    system_id: str
    candidate_signals: List[Signal]
    reason: str


@dataclass
class CaseLinkage:
    """Complete linkage result for a single deletion request case."""

    case_id: str
    user_id: str
    email: str
    attributed_resources: Dict[str, AttributedResource] = field(default_factory=dict)
    unattributed_resources: List[UnattributedResource] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)


def select_best_citable_file(
    resource_id: str,
    obs_by_res: Dict[str, List[Observation]],
    audit_at: str,
) -> Optional[str]:
    """
    Select the best citable evidence file for a resource:
    obs.file_captured_at <= audit_at (inclusive).
    Picks the most recently captured citable observation.
    """
    observations = obs_by_res.get(resource_id, [])
    citable_obs = [o for o in observations if citable(o, audit_at)]
    if not citable_obs:
        return None

    # Deterministic sort: latest file_captured_at, then lexical file_id
    citable_obs.sort(
        key=lambda o: (
            parse_iso(o.file_captured_at),
            o.file_id,
        ),
        reverse=True,
    )
    return citable_obs[0].file_id


def build_case_attribution_graph(
    case_id: str,
    user_id: str,
    email: str,
    audit_at: str,
    all_signals: List[Signal],
    obs_by_res: Dict[str, List[Observation]],
) -> CaseLinkage:
    """
    Assembles signals into attributed and unattributed resources for a case.
    Enforces HARD RULE:
      - Resource attributed if >= 1 hard signal (S1-S6)
      - OR allowed S7/S8 exception (deleted account or anonymized analytics)
      - Everything else -> UNATTRIBUTED.
    """
    signals_by_res: Dict[str, List[Signal]] = defaultdict(list)
    for sig in all_signals:
        signals_by_res[sig.resource_id].append(sig)

    attributed: Dict[str, AttributedResource] = {}
    unattributed: List[UnattributedResource] = []

    for r_id in sorted(signals_by_res.keys()):
        r_signals = signals_by_res[r_id]
        has_hard = any(s.signal_name in HARD_SIGNAL_NAMES for s in r_signals)
        has_exception = any(s.signal_name in EXCEPTION_SIGNAL_NAMES for s in r_signals)

        sys_id = None
        for s in r_signals:
            if s.system_id:
                sys_id = s.system_id
                break
        sys_id = sys_id or system_for_resource(r_id)

        if has_hard or has_exception:
            best_file = select_best_citable_file(r_id, obs_by_res, audit_at)
            attributed[r_id] = AttributedResource(
                resource_id=r_id,
                system_id=sys_id,
                signals=r_signals,
                best_citable_file_id=best_file,
            )
        else:
            unattributed.append(
                UnattributedResource(
                    resource_id=r_id,
                    system_id=sys_id,
                    candidate_signals=r_signals,
                    reason="hard_rule_failed_no_hard_or_exception_signal",
                )
            )

    return CaseLinkage(
        case_id=case_id,
        user_id=user_id,
        email=email,
        attributed_resources=attributed,
        unattributed_resources=unattributed,
        signals=all_signals,
    )
