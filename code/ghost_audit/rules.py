"""
Rule evaluation engine for Ghost Audit.
Parses deletion_rules.csv and evaluates resource treatment decisions dynamically.
No hardcoded policy.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional

from ghost_audit.paths import DELETION_RULES_PATH
from ghost_audit.spec import ALLOWED_OPERATIONS, PHASE_ORDER
from ghost_audit.state import ResourceState
from ghost_audit.timegate import parse_iso_ts

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletionRule:
    rule_id: str
    data_category: str
    condition: str
    required_action: str  # "DELETE" | "REDACT" | "ANONYMIZE" | "RETAIN"


@dataclass(frozen=True)
class TreatmentDecision:
    resource_id: str
    system_id: str
    category: str
    rule_id: Optional[str]
    required_action: str
    is_compliant: bool
    is_undecided: bool = False
    undecided_reason: Optional[str] = None
    finding_op: Optional[str] = None
    finding_state: Optional[str] = None
    remediation_op: Optional[str] = None
    remediation_state: Optional[str] = None
    verification_op: Optional[str] = None
    verification_state: Optional[str] = None


class RuleEngine:
    """Table-driven rule evaluator based on deletion_rules.csv."""

    def __init__(self, rules_path: Optional[Path | str] = None):
        p = Path(rules_path) if rules_path else DELETION_RULES_PATH
        self.rules_by_category: Dict[str, DeletionRule] = {}
        self.rules_by_id: Dict[str, DeletionRule] = {}
        if p.exists():
            self._load_rules(p)

    def _load_rules(self, p: Path) -> None:
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = DeletionRule(
                    rule_id=row["rule_id"].strip(),
                    data_category=row["data_category"].strip(),
                    condition=row.get("condition", "").strip(),
                    required_action=row["required_action"].strip().upper(),
                )
                self.rules_by_category[rule.data_category] = rule
                self.rules_by_id[rule.rule_id] = rule

    def evaluate_resource(
        self,
        resource_state: ResourceState,
        category: str,
        audit_at: str,
    ) -> TreatmentDecision:
        """
        Evaluates a resource against deletion rules and returns a TreatmentDecision.
        """
        rid = resource_state.resource_id
        sys_id = resource_state.system_id
        st = resource_state.status

        # Unknown category handling
        if category == "UNKNOWN":
            return TreatmentDecision(
                resource_id=rid,
                system_id=sys_id,
                category=category,
                rule_id=None,
                required_action="UNKNOWN",
                is_compliant=False,
                is_undecided=True,
                undecided_reason="unrecognized_category",
            )

        # Operational process: DATA_FLOW
        if category == "DATA_FLOW":
            if resource_state.is_active:
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=None,
                    required_action="DISABLE_FLOW",
                    is_compliant=False,
                    finding_op="REPORT_ACTIVE_DATA_FLOW",
                    finding_state="ACTIVE",
                    remediation_op="DISABLE_DATA_FLOW",
                    remediation_state="DISABLED",
                    verification_op="VERIFY_DATA_FLOW_DISABLED",
                    verification_state="DISABLED",
                )
            else:
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=None,
                    required_action="DISABLE_FLOW",
                    is_compliant=True,
                    verification_op="VERIFY_DATA_FLOW_DISABLED",
                    verification_state="DISABLED",
                )

        rule = self.rules_by_category.get(category)
        if not rule:
            return TreatmentDecision(
                resource_id=rid,
                system_id=sys_id,
                category=category,
                rule_id=None,
                required_action="UNKNOWN",
                is_compliant=False,
                is_undecided=True,
                undecided_reason=f"no_rule_for_category_{category}",
            )

        # Unknown state on records that must be verified absent
        if st == "UNKNOWN":
            return TreatmentDecision(
                resource_id=rid,
                system_id=sys_id,
                category=category,
                rule_id=rule.rule_id,
                required_action=rule.required_action,
                is_compliant=False,
                is_undecided=True,
                undecided_reason="unobserved_and_uncovered_state",
            )

        action = rule.required_action

        # 1. DELETE
        if action == "DELETE":
            if st == "PRESENT":
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=rule.rule_id,
                    required_action=action,
                    is_compliant=False,
                    finding_op="REPORT_REMAINING_RECORD",
                    finding_state="PRESENT",
                    remediation_op="DELETE_RECORD",
                    remediation_state="ABSENT",
                    verification_op="VERIFY_RECORD_ABSENT",
                    verification_state="ABSENT",
                )
            else:
                # ABSENT
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=rule.rule_id,
                    required_action=action,
                    is_compliant=True,
                    verification_op="VERIFY_RECORD_ABSENT",
                    verification_state="ABSENT",
                )

        # 2. REDACT
        if action == "REDACT":
            if st == "PRESENT":
                if resource_state.has_direct_identifiers:
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=False,
                        finding_op="REPORT_EXPOSED_PII",
                        finding_state="PRESENT",
                        remediation_op="REDACT_RECORD",
                        remediation_state="REDACTED",
                        verification_op="VERIFY_RECORD_REDACTED",
                        verification_state="REDACTED",
                    )
                else:
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=True,
                        verification_op="VERIFY_RECORD_REDACTED",
                        verification_state="REDACTED",
                    )
            else:
                # ABSENT
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=rule.rule_id,
                    required_action=action,
                    is_compliant=True,
                    verification_op="VERIFY_RECORD_ABSENT",
                    verification_state="ABSENT",
                )

        # 3. ANONYMIZE
        if action == "ANONYMIZE":
            if st == "PRESENT":
                if resource_state.has_direct_identifiers:
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=False,
                        finding_op="REPORT_EXPOSED_PII",
                        finding_state="PRESENT",
                        remediation_op="ANONYMIZE_RECORD",
                        remediation_state="ANONYMIZED",
                        verification_op="VERIFY_RECORD_ANONYMIZED",
                        verification_state="ANONYMIZED",
                    )
                else:
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=True,
                        verification_op="VERIFY_RECORD_ANONYMIZED",
                        verification_state="ANONYMIZED",
                    )
            else:
                # ABSENT
                return TreatmentDecision(
                    resource_id=rid,
                    system_id=sys_id,
                    category=category,
                    rule_id=rule.rule_id,
                    required_action=action,
                    is_compliant=True,
                    verification_op="VERIFY_RECORD_ABSENT",
                    verification_state="ABSENT",
                )

        # 4. RETAIN
        if action == "RETAIN":
            if category == "BACKUP_ARCHIVE":
                if resource_state.is_active:
                    # Restore access allowed is a risk
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=False,
                        finding_op="REPORT_RESTORE_RISK",
                        finding_state="ACTIVE",
                        remediation_op="BLOCK_RESTORE",
                        remediation_state="BLOCKED",
                        verification_op="VERIFY_RESTORE_BLOCKED",
                        verification_state="BLOCKED",
                    )
                else:
                    # Restore blocked -> compliant
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=True,
                        verification_op="VERIFY_RESTORE_BLOCKED",
                        verification_state="BLOCKED",
                    )
            else:
                # SECURITY_AUDIT_LOG or LEGAL_HOLD_RECORD
                is_active_hold = True
                if resource_state.retention_until:
                    try:
                        is_active_hold = parse_iso_ts(resource_state.retention_until) >= parse_iso_ts(audit_at)
                    except Exception:
                        is_active_hold = True

                if is_active_hold:
                    # Must be retained and present
                    if st == "PRESENT":
                        return TreatmentDecision(
                            resource_id=rid,
                            system_id=sys_id,
                            category=category,
                            rule_id=rule.rule_id,
                            required_action=action,
                            is_compliant=True,
                            verification_op="VERIFY_RECORD_PRESENT",
                            verification_state="PRESENT",
                        )
                    else:
                        return TreatmentDecision(
                            resource_id=rid,
                            system_id=sys_id,
                            category=category,
                            rule_id=rule.rule_id,
                            required_action=action,
                            is_compliant=True,
                            verification_op=None,
                            verification_state=None,
                        )
                else:
                    # Expired retention
                    return TreatmentDecision(
                        resource_id=rid,
                        system_id=sys_id,
                        category=category,
                        rule_id=rule.rule_id,
                        required_action=action,
                        is_compliant=True,
                        verification_op="VERIFY_RECORD_ABSENT",
                        verification_state="ABSENT",
                    )

        return TreatmentDecision(
            resource_id=rid,
            system_id=sys_id,
            category=category,
            rule_id=rule.rule_id,
            required_action=action,
            is_compliant=False,
            is_undecided=True,
            undecided_reason=f"unhandled_action_{action}",
        )
