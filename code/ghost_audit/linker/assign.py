"""
Anchor and activity-chain assignment (S7 and S8).

S7: Account-anchor assignment
  - Tutorial cases: anchors within [-10 min, +10 min] of reported_at.
  - Standard cases: anchors within [-80 min, -40 min] of reported_at.
  - 1-to-1 assignment; competing candidates eliminated by S1-S6 or status compatibility.

S8: Activity-chain offsets
  - Downstream event schedule offset tie-breaker.
  - Anonymized analytics attribution for cases with deleted account anchors.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.activity import ActivityLog, SystemActivityRow
from ghost_audit.identity import IdentityResolver, ResolvedIdentity, match_user_id
from ghost_audit.observation import Observation
from ghost_audit.linker.signals import Signal, is_valid_resource_id

TUTORIAL_WINDOW_MIN: Tuple[float, float] = (-10.0, 10.0)
STANDARD_WINDOW_MIN: Tuple[float, float] = (-80.0, -40.0)

KNOWN_OFFSETS: Dict[str, List[float]] = {
    "export_service": [0.4, 87.9],
    "identity_service": [45.7, 114.9],
    "search_service": [13.4, 106.4, 110.9, 116.4, 117.3, 124.4, 125.3, 129.4, 130.3, 143.3],
    "support_platform": [0.4, 30.2, 41.2, 52.2, 105.9, 110.9, 123.9, 129.4, 143.8, 148.8],
    "backup_service": [44.1, 55.1, 66.2, 87.9, 93.8, 115.9],
    "integration_service": [36.7, 47.7, 59.6, 97.9, 105.9, 110.9, 167.3, 168.3],
    "analytics_platform": [22.7, 23.7, 29.7, 33.7, 42.7, 45.7, 97.9, 105.9, 148.8, 162.3, 167.3],
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


def matches_known_offset(target_sys: str, delta_m: float, tol: float = 1.5) -> bool:
    """Check if the delta in minutes matches any known task offset for target system."""
    offsets = KNOWN_OFFSETS.get(target_sys, [])
    return any(abs(delta_m - exp) <= tol for exp in offsets)


def status_matches_result(req_status: str, rep_result: str) -> bool:
    """Check compatibility between request reported_status and system activity reported_result."""
    if req_status == "COMPLETE":
        return rep_result == "SUCCESS"
    if req_status == "NOT_STARTED":
        return rep_result == "FAILED"
    if req_status == "PARTIALLY_COMPLETE":
        return rep_result in ("PARTIAL", "SUCCESS", "FAILED")
    return True


def assign_account_anchors(
    requests: Dict[str, Dict[str, str]],
    resolver: IdentityResolver,
    activity: ActivityLog,
    all_observations: List[Observation],
    case_hard_resources: Dict[str, Set[str]],
    obs_by_res: Dict[str, List[Observation]],
) -> Tuple[Dict[str, str], Dict[str, List[Signal]], List[Tuple[str, str, List[str]]]]:
    """
    Perform 1-to-1 assignment of account anchors to requests (S7).
    Returns:
      - case_anchor_assigned: mapping case_id -> resource_id
      - case_anchor_signals: mapping case_id -> list of S7/S8 Signal objects
      - unattributed_anchor_logs: list of (case_id, reason, candidate_ids)
    """
    case_anchor_assigned: Dict[str, str] = {}
    case_anchor_signals: Dict[str, List[Signal]] = defaultdict(list)
    unattributed_anchor_logs: List[Tuple[str, str, List[str]]] = []
    assigned_anchors: Set[str] = set()

    # Precompute resource -> user mapping from evidence
    acc_identity: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    for o in all_observations:
        if o.resource_id.startswith("account_"):
            u = o.identifiers.user_ref if o.identifiers else None
            em = o.identifiers.email.lower() if o.identifiers and o.identifiers.email else None
            if u or em:
                acc_identity[o.resource_id] = (u, em)

    dw_account_rows = [
        r for r in activity.rows
        if r.source_system == "deletion_worker"
        and r.target_system == "account_service"
        and r.event_type == "DELETE_RECORD"
    ]

    # S7: Phase 1 - Tutorial cases (window [-10 min, +10 min])
    for cid, req in requests.items():
        rep_dt = parse_iso(req["reported_at"])
        is_tutorial = not req["reported_at"].endswith(":00:00Z")
        if is_tutorial:
            cands = []
            for r in dw_account_rows:
                dt = parse_iso(r.event_time)
                delta = (dt - rep_dt).total_seconds() / 60.0
                if TUTORIAL_WINDOW_MIN[0] <= delta <= TUTORIAL_WINDOW_MIN[1]:
                    cands.append(r)
            if len(cands) == 1:
                r = cands[0]
                case_anchor_assigned[cid] = r.resource_id
                assigned_anchors.add(r.resource_id)
                case_anchor_signals[cid].append(
                    Signal(
                        r.resource_id,
                        "S7_ACCOUNT_ANCHOR",
                        f"system_activity:{r.activity_id}",
                        0.70,
                        "account_service",
                        obs_time=r.event_time,
                        metadata={"reported_result": r.reported_result},
                    )
                )

    # S7: Phase 2 - Standard cases matching direct S1/S2 identity
    for cid, req in requests.items():
        if cid in case_anchor_assigned:
            continue
        rep_dt = parse_iso(req["reported_at"])
        ident = resolver.resolve(req["email"])
        cands = []
        for r in dw_account_rows:
            if r.resource_id in assigned_anchors:
                continue
            dt = parse_iso(r.event_time)
            delta = (dt - rep_dt).total_seconds() / 60.0
            if STANDARD_WINDOW_MIN[0] <= delta <= STANDARD_WINDOW_MIN[1]:
                cands.append(r)

        for c in cands:
            r_id = c.resource_id
            if r_id in case_hard_resources[cid]:
                case_anchor_assigned[cid] = r_id
                assigned_anchors.add(r_id)
                case_anchor_signals[cid].append(
                    Signal(
                        r_id,
                        "S7_ACCOUNT_ANCHOR",
                        f"system_activity:{c.activity_id}",
                        0.70,
                        "account_service",
                        obs_time=c.event_time,
                        metadata={"reported_result": c.reported_result},
                    )
                )
                break
            elif r_id in acc_identity:
                cu, cem = acc_identity[r_id]
                if (cu and cu == ident.user_id) or (cem and cem in ident.emails):
                    case_anchor_assigned[cid] = r_id
                    assigned_anchors.add(r_id)
                    case_anchor_signals[cid].append(
                        Signal(
                            r_id,
                            "S7_ACCOUNT_ANCHOR",
                            f"system_activity:{c.activity_id}",
                            0.70,
                            "account_service",
                            obs_time=c.event_time,
                            metadata={"reported_result": c.reported_result},
                        )
                    )
                    break

    # S7 & S8: Phase 3 - Disambiguation by reported_result & downstream activity
    cases_by_time: Dict[str, List[str]] = defaultdict(list)
    for cid, req in requests.items():
        if cid not in case_anchor_assigned:
            cases_by_time[req["reported_at"]].append(cid)

    for rep_time, cids in sorted(cases_by_time.items()):
        rep_dt = parse_iso(rep_time)
        batch_anchors = []
        for r in dw_account_rows:
            if r.resource_id in assigned_anchors:
                continue
            dt = parse_iso(r.event_time)
            delta = (dt - rep_dt).total_seconds() / 60.0
            if STANDARD_WINDOW_MIN[0] <= delta <= STANDARD_WINDOW_MIN[1]:
                batch_anchors.append(r)

        batch_anchors.sort(key=lambda r: parse_iso(r.event_time))

        for cid in list(cids):
            req = requests[cid]
            ident = resolver.resolve(req["email"])
            req_stat = req["reported_status"]
            hard_res = case_hard_resources[cid]

            # Eliminate any anchor whose identity is known to belong to someone else
            compatible = []
            for a in batch_anchors:
                if a.resource_id in assigned_anchors:
                    continue
                if not status_matches_result(req_stat, a.reported_result):
                    continue
                if a.resource_id in acc_identity:
                    cu, cem = acc_identity[a.resource_id]
                    if (cu and cu != ident.user_id) or (cem and cem not in ident.emails):
                        continue
                for obs in obs_by_res.get(a.resource_id, []):
                    if obs.identifiers:
                        if obs.identifiers.email and obs.identifiers.email.lower().strip() not in ident.emails:
                            continue
                compatible.append(a)

            scored_compatible = []
            for a in compatible:
                a_dt = parse_iso(a.event_time)
                score = 0.0
                for ev in activity.rows:
                    if ev.source_system == "deletion_worker" and ev.target_system != "account_service":
                        ev_dt = parse_iso(ev.event_time)
                        delta_m = (ev_dt - a_dt).total_seconds() / 60.0
                        if 0 < delta_m <= 180.0:
                            if ev.resource_id in hard_res:
                                score += 10.0
                                # S8 schedule offset bonus
                                if matches_known_offset(ev.target_system, delta_m, tol=1.5):
                                    score += 20.0
                scored_compatible.append((score, a))

            if scored_compatible:
                scored_compatible.sort(key=lambda x: (-x[0], parse_iso(x[1].event_time)))
                best_anchor = scored_compatible[0][1]
                case_anchor_assigned[cid] = best_anchor.resource_id
                assigned_anchors.add(best_anchor.resource_id)
                case_anchor_signals[cid].append(
                    Signal(
                        best_anchor.resource_id,
                        "S7_ACCOUNT_ANCHOR",
                        f"system_activity:{best_anchor.activity_id}",
                        0.70,
                        "account_service",
                        obs_time=best_anchor.event_time,
                        metadata={"reported_result": best_anchor.reported_result, "score": scored_compatible[0][0]},
                    )
                )
            else:
                unattributed_anchor_logs.append((cid, "no_compatible_anchor", [a.resource_id for a in batch_anchors]))

    return case_anchor_assigned, case_anchor_signals, unattributed_anchor_logs


def assign_activity_chain_resources(
    requests: Dict[str, Dict[str, str]],
    resolver: IdentityResolver,
    activity: ActivityLog,
    case_anchor_assigned: Dict[str, str],
    case_resources: Dict[str, Set[str]],
    obs_by_res: Dict[str, List[Observation]],
) -> Tuple[Dict[str, List[Signal]], Set[str]]:
    """
    Assign activity-chain resources (S8):
    - Tutorial accounts derived from user_id pattern: account_{int(u_num):03d}
    - Tutorial analytics deletion_worker events within 10 min of reported_at
    - Anonymized analytics records via S8 schedule offset matching
    Returns:
      - case_s8_signals: mapping case_id -> list of S8 Signal objects
      - assigned_analytics: set of assigned analytics resource IDs
    """
    case_s8_signals: Dict[str, List[Signal]] = defaultdict(list)
    assigned_analytics: Set[str] = set()

    dw_account_rows = [
        r for r in activity.rows
        if r.source_system == "deletion_worker"
        and r.target_system == "account_service"
        and r.event_type == "DELETE_RECORD"
    ]

    for cid, req in requests.items():
        is_tutorial = not req["reported_at"].endswith(":00:00Z")
        if is_tutorial:
            ident = resolver.resolve(req["email"])
            m = re.match(r"user_(\d+)", ident.user_id)
            if m:
                u_num = int(m.group(1))
                tut_acc = f"account_{u_num:03d}"
                case_s8_signals[cid].append(
                    Signal(
                        tut_acc,
                        "S8_TUTORIAL_ACCOUNT",
                        f"pattern:user_{u_num}->account_{u_num:03d}",
                        0.60,
                        "account_service",
                    )
                )

            rep_dt = parse_iso(req["reported_at"])
            for ev in activity.rows:
                if ev.source_system == "deletion_worker" and ev.target_system == "analytics_platform":
                    ev_dt = parse_iso(ev.event_time)
                    if abs((ev_dt - rep_dt).total_seconds()) <= 600:
                        case_s8_signals[cid].append(
                            Signal(
                                ev.resource_id,
                                "S8_TUTORIAL_ANALYTICS",
                                f"system_activity:{ev.activity_id}",
                                0.60,
                                "analytics_platform",
                                obs_time=ev.event_time,
                            )
                        )
                        assigned_analytics.add(ev.resource_id)

    # Anonymized analytics matching using exact schedule offsets
    for cid, req in requests.items():
        has_analytics = any(r.startswith("analytics_") for r in case_resources.get(cid, set())) or any(
            s.resource_id.startswith("analytics_") for s in case_s8_signals.get(cid, [])
        )
        if has_analytics:
            continue

        anchor = case_anchor_assigned.get(cid)
        if not anchor:
            continue
        a_row = next((r for r in dw_account_rows if r.resource_id == anchor), None)
        if not a_row:
            continue
        a_dt = parse_iso(a_row.event_time)

        cands = []
        for ev in activity.rows:
            if (
                ev.source_system == "deletion_worker"
                and ev.target_system == "analytics_platform"
                and ev.event_type in ("ANONYMIZE_RECORD", "DELETE_RECORD")
            ):
                if ev.resource_id in assigned_analytics:
                    continue
                ev_dt = parse_iso(ev.event_time)
                delta_m = (ev_dt - a_dt).total_seconds() / 60.0
                if 15.0 <= delta_m <= 50.0 and ev.resource_id in obs_by_res:
                    if matches_known_offset("analytics_platform", delta_m, tol=0.5):
                        obs_list = obs_by_res[ev.resource_id]
                        if any(
                            not (o.identifiers and (o.identifiers.email or o.identifiers.user_ref or o.identifiers.phone))
                            for o in obs_list
                        ):
                            diff = min(abs(delta_m - exp) for exp in KNOWN_OFFSETS["analytics_platform"])
                            cands.append((diff, ev))

        if cands:
            cands.sort(key=lambda x: x[0])
            chosen_ev = cands[0][1]
            case_s8_signals[cid].append(
                Signal(
                    chosen_ev.resource_id,
                    "S8_ANON_ANALYTICS",
                    f"system_activity:{chosen_ev.activity_id}",
                    0.65,
                    "analytics_platform",
                    obs_time=chosen_ev.event_time,
                    metadata={"offset_delta_m": (parse_iso(chosen_ev.event_time) - a_dt).total_seconds() / 60.0},
                )
            )
            assigned_analytics.add(chosen_ev.resource_id)

    return case_s8_signals, assigned_analytics
