"""
Evidence-to-case linkage engine for Ghost Audit.

Exposes:
  - Linker: Orchestrator for resolving and attributing resources to cases
  - Signal: Discrete evidence signal
  - AttributedResource: Resource linked with confidence and citable file
  - UnattributedResource: Candidate resource excluded under hard rule
  - CaseLinkage: Complete linkage container per case
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ghost_audit.activity import ActivityLog
from ghost_audit.evidence import normalize_all_evidence
from ghost_audit.identity import IdentityResolver
from ghost_audit.observation import Observation
from ghost_audit.paths import SAMPLE_REQUESTS_PATH
from ghost_audit.linker.assign import (
    KNOWN_OFFSETS,
    STANDARD_WINDOW_MIN,
    TUTORIAL_WINDOW_MIN,
    assign_account_anchors,
    assign_activity_chain_resources,
)
from ghost_audit.linker.graph import (
    AttributedResource,
    CaseLinkage,
    UnattributedResource,
    build_case_attribution_graph,
    system_for_resource,
)
from ghost_audit.linker.signals import Signal, collect_hard_signals_for_case, is_valid_resource_id


class Linker:
    """Orchestrates evidence signals, anchor assignment, and attribution graphs."""

    def __init__(
        self,
        resolver: Optional[IdentityResolver] = None,
        activity: Optional[ActivityLog] = None,
        observations: Optional[List[Observation]] = None,
    ):
        self.resolver = resolver or IdentityResolver()
        self.activity = activity or ActivityLog()
        if observations is not None:
            self.observations = observations
        else:
            obs, _, _ = normalize_all_evidence()
            self.observations = obs

        self.obs_by_res: Dict[str, List[Observation]] = defaultdict(list)
        for o in self.observations:
            if is_valid_resource_id(o.resource_id):
                self.obs_by_res[o.resource_id].append(o)

    def link_cases(
        self,
        requests: Dict[str, Dict[str, str]],
        documents_dir: Optional[Path] = None,
    ) -> Dict[str, CaseLinkage]:
        """
        Link evidence to deletion request cases.
        requests: mapping case_id -> request dict (email, requested_at, reported_at, reported_status, audit_at).
        """
        case_hard_signals: Dict[str, List[Signal]] = {}
        case_hard_resources: Dict[str, Set[str]] = {}

        # 1. Collect S1-S6 hard signals for each case
        for cid, req in requests.items():
            req_email = req["email"].lower().strip()
            try:
                ident = self.resolver.resolve(req_email)
            except Exception:
                ident = None

            if ident:
                h_signals = collect_hard_signals_for_case(
                    case_id=cid,
                    requested_at=req["requested_at"],
                    audit_at=req["audit_at"],
                    identity=ident,
                    all_observations=self.observations,
                    activity=self.activity,
                    obs_by_res=self.obs_by_res,
                    documents_dir=documents_dir,
                )
            else:
                h_signals = []
            case_hard_signals[cid] = h_signals
            case_hard_resources[cid] = {s.resource_id for s in h_signals}

        # 2. Assign S7 account anchors
        case_anchor_assigned, case_anchor_signals, _ = assign_account_anchors(
            requests=requests,
            resolver=self.resolver,
            activity=self.activity,
            all_observations=self.observations,
            case_hard_resources=case_hard_resources,
            obs_by_res=self.obs_by_res,
        )

        # 3. Assign S8 activity chain and anonymized analytics
        case_s8_signals, _ = assign_activity_chain_resources(
            requests=requests,
            resolver=self.resolver,
            activity=self.activity,
            case_anchor_assigned=case_anchor_assigned,
            case_resources=case_hard_resources,
            obs_by_res=self.obs_by_res,
        )

        # 4. Assemble CaseLinkage per case with HARD RULE enforcement
        linkages: Dict[str, CaseLinkage] = {}
        for cid, req in requests.items():
            try:
                ident = self.resolver.resolve(req["email"])
                user_id = ident.user_id
            except Exception:
                ident = None
                user_id = ""

            all_case_signals: List[Signal] = []
            all_case_signals.extend(case_hard_signals.get(cid, []))
            all_case_signals.extend(case_anchor_signals.get(cid, []))
            all_case_signals.extend(case_s8_signals.get(cid, []))

            linkage = build_case_attribution_graph(
                case_id=cid,
                user_id=user_id,
                email=req["email"],
                audit_at=req["audit_at"],
                all_signals=all_case_signals,
                obs_by_res=self.obs_by_res,
            )
            linkages[cid] = linkage

        return linkages


__all__ = [
    "Linker",
    "Signal",
    "AttributedResource",
    "UnattributedResource",
    "CaseLinkage",
    "TUTORIAL_WINDOW_MIN",
    "STANDARD_WINDOW_MIN",
    "KNOWN_OFFSETS",
    "system_for_resource",
    "is_valid_resource_id",
]
