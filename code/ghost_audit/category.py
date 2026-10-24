"""
Data category classifier.
Maps (system_id, collection, field shape, resource_id) to one of the canonical
data categories defined in deletion_rules.csv or DATA_FLOW.

Categories:
- USER_PROFILE
- SECONDARY_IDENTIFIER
- SEARCH_INDEX_ENTRY
- CACHE_ENTRY
- SUPPORT_MESSAGE
- SUPPORT_ATTACHMENT
- ANALYTICS_PROFILE
- PRODUCT_TELEMETRY
- USER_EXPORT
- MARKETING_PROFILE
- EMAIL_DELIVERY_LOG
- SECURITY_AUDIT_LOG
- LEGAL_HOLD_RECORD
- BACKUP_ARCHIVE
- ACCOUNT_TOMBSTONE
- DATA_FLOW (operational process)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

VALID_DATA_CATEGORIES = {
    "USER_PROFILE",
    "SECONDARY_IDENTIFIER",
    "SEARCH_INDEX_ENTRY",
    "CACHE_ENTRY",
    "SUPPORT_MESSAGE",
    "SUPPORT_ATTACHMENT",
    "ANALYTICS_PROFILE",
    "PRODUCT_TELEMETRY",
    "USER_EXPORT",
    "MARKETING_PROFILE",
    "EMAIL_DELIVERY_LOG",
    "SECURITY_AUDIT_LOG",
    "LEGAL_HOLD_RECORD",
    "BACKUP_ARCHIVE",
    "ACCOUNT_TOMBSTONE",
    "DATA_FLOW",
}


def classify_category(
    system_id: str,
    collection: str,
    state: Optional[Dict[str, Any]] = None,
    resource_id: Optional[str] = None,
) -> str:
    """
    Table-driven classifier mapping (system_id, collection, field shape) to a data category.
    Shape classifier wins over metadata.
    """
    sys_str = (system_id or "").lower().strip().strip('"\'')
    col_str = (collection or "").lower().strip().strip('"\'')
    res_str = (resource_id or "").lower().strip().strip('"\'')
    state_dict = state if isinstance(state, dict) else {}

    # Check state record_type or category override if explicit
    record_type = str(state_dict.get("record_type") or state_dict.get("category") or "").upper().strip()
    if record_type in VALID_DATA_CATEGORIES:
        return record_type

    # 1. ACCOUNT_TOMBSTONE
    if (
        sys_str == "identity_service"
        or "tombstone" in col_str
        or "tombstone" in res_str
        or "deleted_customer_reference" in col_str
    ):
        return "ACCOUNT_TOMBSTONE"

    # 2. LEGAL_HOLD_RECORD
    if (
        sys_str == "legal_service"
        or "legal" in col_str
        or "legal" in res_str
        or "retained_order" in col_str
    ):
        return "LEGAL_HOLD_RECORD"

    # 3. SECURITY_AUDIT_LOG
    if (
        sys_str == "security_service"
        or "security_audit" in col_str
        or "audit_record" in res_str
        or col_str.startswith("audit_record")
        or "audit_ledger" in col_str
    ):
        return "SECURITY_AUDIT_LOG"

    # 4. BACKUP_ARCHIVE
    if (
        sys_str == "backup_service"
        or "backup" in col_str
        or "backup" in res_str
        or "restore_" in col_str
    ):
        return "BACKUP_ARCHIVE"

    # 5. USER_EXPORT
    if (
        sys_str == "export_service"
        or "customer_export" in col_str
        or "export_" in res_str
        or col_str.startswith("export")
    ):
        return "USER_EXPORT"

    # 6. SEARCH_INDEX_ENTRY
    if (
        sys_str == "search_service"
        or "search" in col_str
        or "search" in res_str
        or "customer_directory" in col_str
    ):
        return "SEARCH_INDEX_ENTRY"

    # 7. SUPPORT (Message vs Attachment)
    if sys_str == "support_platform" or "support" in col_str or "support" in res_str:
        if (
            "attachment" in col_str
            or "attachment" in res_str
            or "attachment_name" in state_dict
            or "attachment_url" in state_dict
            or "file" in state_dict
            or res_str.startswith("attachment_")
        ):
            return "SUPPORT_ATTACHMENT"
        return "SUPPORT_MESSAGE"

    # 8. ANALYTICS (Profile vs Telemetry)
    if sys_str == "analytics_platform" or "analytics" in col_str or "analytics" in res_str:
        if "telemetry" in col_str or "telemetry" in res_str or "device_metrics" in state_dict:
            return "PRODUCT_TELEMETRY"
        return "ANALYTICS_PROFILE"

    # 9. DATA_FLOW
    if (
        sys_str == "integration_service"
        or "connector" in col_str
        or "data_flow" in res_str
    ):
        return "DATA_FLOW"

    # 10. SECONDARY_IDENTIFIER vs USER_PROFILE
    if sys_str in ("account_service", "profile_service") or "profile" in col_str or "account" in res_str:
        if "secondary" in col_str or "secondary" in res_str or "secondary_email" in state_dict:
            return "SECONDARY_IDENTIFIER"
        return "USER_PROFILE"

    # 11. EMAIL_DELIVERY_LOG
    if (
        "notification" in sys_str
        or "notification" in col_str
        or "email_delivery" in col_str
        or "delivery" in col_str
    ):
        return "EMAIL_DELIVERY_LOG"

    # 12. CACHE_ENTRY
    if "cache" in sys_str or "cache" in col_str:
        return "CACHE_ENTRY"

    # 13. MARKETING_PROFILE
    if "marketing" in sys_str or "marketing" in col_str:
        return "MARKETING_PROFILE"

    return "UNKNOWN"
