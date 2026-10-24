"""
Treatment planner for Ghost Audit.
Generates CaseDecision with structured, ordered findings, remediation, and verification steps.
Adheres strictly to problem_statement.md and spec.py constants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.citation import resolve_step_citation
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.intent import is_deletion_request
from ghost_audit.linker.graph import CaseLinkage, select_best_citable_file
from ghost_audit.loaders.manifest import EvidenceFileMeta
from ghost_audit.observation import Observation
from ghost_audit.rules import RuleEngine, TreatmentDecision
from ghost_audit.spec import (
    OPERATION_ORDER_WITHIN_PHASE,
    PHASE_FINDING,
    PHASE_ORDER,
    PHASE_REMEDIATION,
    PHASE_VERIFICATION,
    STATUS_COMPLETE,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
)
from ghost_audit.state import ResourceState
from ghost_audit.timegate import citable, parse_iso_ts


@dataclass
class CaseDecision:
    """Complete decision container for a single deletion request case."""

    case_id: str
    deletion_status: str
    treatments: Dict[str, TreatmentDecision] = field(default_factory=dict)
    steps: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def steps_json(self) -> str:
        """Canonical JSON serialization of steps array."""
        return json.dumps(self.steps, separators=(",", ":"), ensure_ascii=False)


def find_latest_covering_evidence_id(
    system_id: str,
    coverage_index: CoverageIndex,
    audit_at: str,
) -> Optional[str]:
    """Finds the latest citable evidence_id covering system_id at or before audit_at."""
    citable_records = []
    for c_rec in coverage_index.records:
        if c_rec.system_id.lower() == system_id.lower():
            if citable(c_rec.file_captured_at, audit_at):
                citable_records.append(c_rec)

    if not citable_records:
        return None

    # Deterministic sort: latest file_captured_at, then lexical file_id
    citable_records.sort(
        key=lambda r: (parse_iso_ts(r.file_captured_at), r.file_id),
        reverse=True,
    )
    return citable_records[0].file_id


def plan_case(
    case_id: str,
    request_text: str,
    audit_at: str,
    case_linkage: CaseLinkage,
    resource_states: Dict[str, ResourceState],
    categories: Dict[str, str],
    rule_engine: RuleEngine,
    obs_by_res: Dict[str, List[Observation]],
    coverage_index: Optional[CoverageIndex] = None,
    manifest: Optional[Dict[str, EvidenceFileMeta]] = None,
) -> CaseDecision:
    """
    Evaluates policy across all attributed resources for a case and constructs ordered steps.
    """
    # 1. NOT_APPLICABLE check (deterministic intent classifier)
    if not is_deletion_request(request_text):
        return CaseDecision(
            case_id=case_id,
            deletion_status=STATUS_NOT_APPLICABLE,
            treatments={},
            steps=[],
        )

    # 2. Evaluate each attributed resource
    treatments: Dict[str, TreatmentDecision] = {}
    for rid, attr in case_linkage.attributed_resources.items():
        st = resource_states.get(
            rid,
            ResourceState(resource_id=rid, system_id=attr.system_id, status="UNKNOWN"),
        )
        cat = categories.get(rid, "UNKNOWN")
        dec = rule_engine.evaluate_resource(st, cat, audit_at)
        treatments[rid] = dec

    # 3. Determine overall case status
    # Any non-compliant treatment -> INCOMPLETE. Otherwise COMPLETE.
    is_incomplete = any(not t.is_compliant for t in treatments.values())
    deletion_status = STATUS_INCOMPLETE if is_incomplete else STATUS_COMPLETE

    # 4. Construct steps
    steps: List[Dict[str, Any]] = []

    if deletion_status == STATUS_INCOMPLETE:
        # Phase 1: FINDING
        findings = []
        for rid, dec in treatments.items():
            if not dec.is_compliant and dec.finding_op:
                attr = case_linkage.attributed_resources.get(rid)
                fallback_file = attr.best_citable_file_id if attr else None
                if not fallback_file:
                    fallback_file = select_best_citable_file(rid, obs_by_res, audit_at) or ""
                
                if manifest is not None:
                    ev_id = resolve_step_citation(
                        resource_id=rid,
                        system_id=dec.system_id,
                        state=dec.finding_state,
                        audit_at=audit_at,
                        obs_by_res=obs_by_res,
                        coverage_index=coverage_index,
                        manifest=manifest,
                        fallback_file_id=fallback_file,
                    )
                else:
                    ev_id = fallback_file

                findings.append({
                    "phase": PHASE_FINDING,
                    "system_id": dec.system_id,
                    "resource_id": rid,
                    "operation": dec.finding_op,
                    "state": dec.finding_state,
                    "evidence_id": ev_id,
                })
        findings.sort(
            key=lambda s: (
                OPERATION_ORDER_WITHIN_PHASE.get(s["operation"], 99),
                s["system_id"],
                s["resource_id"],
            )
        )
        steps.extend(findings)

        # Phase 2: REMEDIATION
        remediations = []
        for rid, dec in treatments.items():
            if not dec.is_compliant and dec.remediation_op:
                remediations.append({
                    "phase": PHASE_REMEDIATION,
                    "system_id": dec.system_id,
                    "resource_id": rid,
                    "operation": dec.remediation_op,
                    "state": dec.remediation_state,
                    "evidence_id": "",
                })
        remediations.sort(
            key=lambda s: (
                OPERATION_ORDER_WITHIN_PHASE.get(s["operation"], 99),
                s["system_id"],
                s["resource_id"],
            )
        )
        steps.extend(remediations)

        # Phase 3: VERIFICATION
        # Rule: verification = account VERIFY_RECORD_ABSENT once (not duplicated if account is also a finding)
        #       + one check per remediated resource
        #       + retained audit record VERIFY_RECORD_PRESENT when one exists
        #       (compliant-only records are NOT listed)
        verifications = []

        # Find account resource for the case
        account_res_id = None
        for rid in sorted(case_linkage.attributed_resources.keys()):
            if rid.startswith("account_") or case_linkage.attributed_resources[rid].system_id == "account_service":
                account_res_id = rid
                break

        if account_res_id:
            verifications.append({
                "phase": PHASE_VERIFICATION,
                "system_id": "account_service",
                "resource_id": account_res_id,
                "operation": "VERIFY_RECORD_ABSENT",
                "state": "ABSENT",
                "evidence_id": "",
            })

        # One check per remediated resource (excluding account if already added)
        for rid, dec in treatments.items():
            if not dec.is_compliant and dec.remediation_op:
                if rid == account_res_id:
                    continue  # already verified absent above
                verifications.append({
                    "phase": PHASE_VERIFICATION,
                    "system_id": dec.system_id,
                    "resource_id": rid,
                    "operation": dec.verification_op,
                    "state": dec.verification_state,
                    "evidence_id": "",
                })

        # Retained audit record check when one exists
        for rid, dec in treatments.items():
            if dec.category == "SECURITY_AUDIT_LOG" or rid.startswith("audit_record_"):
                verifications.append({
                    "phase": PHASE_VERIFICATION,
                    "system_id": "security_service",
                    "resource_id": rid,
                    "operation": "VERIFY_RECORD_PRESENT",
                    "state": "PRESENT",
                    "evidence_id": "",
                })

        verifications.sort(
            key=lambda s: (
                OPERATION_ORDER_WITHIN_PHASE.get(s["operation"], 99),
                s["system_id"],
                s["resource_id"],
            )
        )
        steps.extend(verifications)

    elif deletion_status == STATUS_COMPLETE:
        # Phase 3: VERIFICATION only
        verifications = []

        # Find shared citable file for complete case from covering snapshots or attributed files
        case_citable_files = []
        for rid, attr in case_linkage.attributed_resources.items():
            if attr.best_citable_file_id:
                case_citable_files.append(attr.best_citable_file_id)

        shared_file = case_citable_files[0] if case_citable_files else None
        if not shared_file and coverage_index is not None:
            shared_file = find_latest_covering_evidence_id("account_service", coverage_index, audit_at)

        for rid in sorted(case_linkage.attributed_resources.keys()):
            dec = treatments.get(rid)
            attr = case_linkage.attributed_resources[rid]
            sys_id = dec.system_id if dec else attr.system_id
            
            fallback_file = attr.best_citable_file_id
            if not fallback_file and coverage_index is not None:
                fallback_file = find_latest_covering_evidence_id(sys_id, coverage_index, audit_at)
            if not fallback_file:
                fallback_file = shared_file or ""

            if dec and dec.verification_op:
                op = dec.verification_op
                st = dec.verification_state
            elif rid.startswith("account_"):
                op = "VERIFY_RECORD_ABSENT"
                st = "ABSENT"
            else:
                continue

            if manifest is not None:
                ev_id = resolve_step_citation(
                    resource_id=rid,
                    system_id=sys_id,
                    state=st,
                    audit_at=audit_at,
                    obs_by_res=obs_by_res,
                    coverage_index=coverage_index,
                    manifest=manifest,
                    fallback_file_id=fallback_file,
                )
            else:
                ev_id = fallback_file

            verifications.append({
                "phase": PHASE_VERIFICATION,
                "system_id": sys_id,
                "resource_id": rid,
                "operation": op,
                "state": st,
                "evidence_id": ev_id,
            })

        verifications.sort(
            key=lambda s: (
                OPERATION_ORDER_WITHIN_PHASE.get(s["operation"], 99),
                s["system_id"],
                s["resource_id"],
            )
        )
        steps.extend(verifications)

    # 5. Enumerate consecutive step numbers
    for idx, s in enumerate(steps, start=1):
        s["step_no"] = idx

    return CaseDecision(
        case_id=case_id,
        deletion_status=deletion_status,
        treatments=treatments,
        steps=steps,
    )
