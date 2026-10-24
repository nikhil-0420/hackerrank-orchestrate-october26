"""
Single source of truth for Ghost Audit specification constants.
Extracted directly from problem_statement.md and dataset contracts.
No other module may hardcode these values.
"""

from typing import Final

# Output CSV columns (problem_statement.md line 64)
OUTPUT_HEADER: Final[list[str]] = ["case_id", "deletion_status", "steps_json"]

# JSON Step object fields (problem_statement.md lines 78-86)
STEP_FIELDS: Final[tuple[str, ...]] = (
    "step_no",
    "phase",
    "system_id",
    "resource_id",
    "operation",
    "state",
    "evidence_id",
)

# Deletion statuses (problem_statement.md line 70)
STATUS_COMPLETE: Final[str] = "COMPLETE"
STATUS_INCOMPLETE: Final[str] = "INCOMPLETE"
STATUS_NOT_APPLICABLE: Final[str] = "NOT_APPLICABLE"

ALLOWED_STATUSES: Final[set[str]] = {
    STATUS_COMPLETE,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
}

# Phases (problem_statement.md lines 89, 126)
PHASE_FINDING: Final[str] = "FINDING"
PHASE_REMEDIATION: Final[str] = "REMEDIATION"
PHASE_VERIFICATION: Final[str] = "VERIFICATION"

ALLOWED_PHASES: Final[tuple[str, ...]] = (
    PHASE_FINDING,
    PHASE_REMEDIATION,
    PHASE_VERIFICATION,
)

PHASE_ORDER: Final[dict[str, int]] = {
    PHASE_FINDING: 1,
    PHASE_REMEDIATION: 2,
    PHASE_VERIFICATION: 3,
}

# Full Operation Table from problem_statement.md lines 103-120
# (phase, operation, state, meaning)
OPERATION_TABLE: Final[list[tuple[str, str, str, str]]] = [
    # FINDING
    (
        PHASE_FINDING,
        "REPORT_REMAINING_RECORD",
        "PRESENT",
        "A record that should have been deleted still exists.",
    ),
    (
        PHASE_FINDING,
        "REPORT_EXPOSED_PII",
        "PRESENT",
        "A record may remain, but it still contains identifiers that should have been redacted or anonymized.",
    ),
    (
        PHASE_FINDING,
        "REPORT_ACTIVE_DATA_FLOW",
        "ACTIVE",
        "An active process can copy or recreate the user's data.",
    ),
    (
        PHASE_FINDING,
        "REPORT_RESTORE_RISK",
        "ACTIVE",
        "A backup or restore path can bring deleted data back.",
    ),
    # REMEDIATION
    (
        PHASE_REMEDIATION,
        "DISABLE_DATA_FLOW",
        "DISABLED",
        "Stop the process that can copy or recreate the data.",
    ),
    (
        PHASE_REMEDIATION,
        "BLOCK_RESTORE",
        "BLOCKED",
        "Prevent the affected backup from restoring the user's data.",
    ),
    (
        PHASE_REMEDIATION,
        "DELETE_RECORD",
        "ABSENT",
        "Remove the entire record.",
    ),
    (
        PHASE_REMEDIATION,
        "REDACT_RECORD",
        "REDACTED",
        "Keep the record but remove the identifying fields required by policy.",
    ),
    (
        PHASE_REMEDIATION,
        "ANONYMIZE_RECORD",
        "ANONYMIZED",
        "Keep the record after irreversibly unlinking it from the user.",
    ),
    # VERIFICATION
    (
        PHASE_VERIFICATION,
        "VERIFY_RECORD_ABSENT",
        "ABSENT",
        "Confirm that a record no longer exists.",
    ),
    (
        PHASE_VERIFICATION,
        "VERIFY_RECORD_PRESENT",
        "PRESENT",
        "Confirm that a policy-required retained record still exists.",
    ),
    (
        PHASE_VERIFICATION,
        "VERIFY_RECORD_REDACTED",
        "REDACTED",
        "Confirm that required identifying fields have been removed.",
    ),
    (
        PHASE_VERIFICATION,
        "VERIFY_RECORD_ANONYMIZED",
        "ANONYMIZED",
        "Confirm that the record can no longer be linked to the user.",
    ),
    (
        PHASE_VERIFICATION,
        "VERIFY_DATA_FLOW_DISABLED",
        "DISABLED",
        "Confirm that the relevant data flow is inactive.",
    ),
    (
        PHASE_VERIFICATION,
        "VERIFY_RESTORE_BLOCKED",
        "BLOCKED",
        "Confirm that the affected data cannot be restored.",
    ),
]

# Legal (operation, state) pairs
LEGAL_OPERATION_STATE_PAIRS: Final[set[tuple[str, str]]] = {
    (op, state) for _, op, state, _ in OPERATION_TABLE
}

# Operation to legal phase mapping
OPERATION_TO_PHASE: Final[dict[str, str]] = {
    op: phase for phase, op, _, _ in OPERATION_TABLE
}

# Operation to legal state mapping
OPERATION_TO_STATE: Final[dict[str, str]] = {
    op: state for _, op, state, _ in OPERATION_TABLE
}

ALLOWED_OPERATIONS: Final[set[str]] = set(OPERATION_TO_STATE.keys())

# Within-phase operation ordering index (1-based relative to problem_statement.md table order)
OPERATION_ORDER_WITHIN_PHASE: Final[dict[str, int]] = {
    # FINDING
    "REPORT_REMAINING_RECORD": 1,
    "REPORT_EXPOSED_PII": 2,
    "REPORT_ACTIVE_DATA_FLOW": 3,
    "REPORT_RESTORE_RISK": 4,
    # REMEDIATION
    "DISABLE_DATA_FLOW": 1,
    "BLOCK_RESTORE": 2,
    "DELETE_RECORD": 3,
    "REDACT_RECORD": 4,
    "ANONYMIZE_RECORD": 5,
    # VERIFICATION
    "VERIFY_RECORD_ABSENT": 1,
    "VERIFY_RECORD_PRESENT": 2,
    "VERIFY_RECORD_REDACTED": 3,
    "VERIFY_RECORD_ANONYMIZED": 4,
    "VERIFY_DATA_FLOW_DISABLED": 5,
    "VERIFY_RESTORE_BLOCKED": 6,
}

# Global operation order index across all operations
OPERATION_GLOBAL_ORDER: Final[dict[str, int]] = {
    op: idx for idx, (_, op, _, _) in enumerate(OPERATION_TABLE, start=1)
}

# Operation semantic matching chains: (Finding -> Remediation -> Verification)
# Used for W02 convention checks.
FINDING_TO_REMEDIATION: Final[dict[str, set[str]]] = {
    "REPORT_ACTIVE_DATA_FLOW": {"DISABLE_DATA_FLOW"},
    "REPORT_RESTORE_RISK": {"BLOCK_RESTORE"},
    "REPORT_REMAINING_RECORD": {"DELETE_RECORD"},
    "REPORT_EXPOSED_PII": {"REDACT_RECORD", "ANONYMIZE_RECORD"},
}

REMEDIATION_TO_VERIFICATION: Final[dict[str, str]] = {
    "DISABLE_DATA_FLOW": "VERIFY_DATA_FLOW_DISABLED",
    "BLOCK_RESTORE": "VERIFY_RESTORE_BLOCKED",
    "DELETE_RECORD": "VERIFY_RECORD_ABSENT",
    "REDACT_RECORD": "VERIFY_RECORD_REDACTED",
    "ANONYMIZE_RECORD": "VERIFY_RECORD_ANONYMIZED",
}
