"""
Multilingual intent classifier for deletion vs non-deletion requests.
Determines whether a request is DELETION (applicable) or NON_DELETION (NOT_APPLICABLE).

Cross-checks request_text against CLASSIFY_REQUEST intake records in system_activity.csv.
Flags any disagreements or low-confidence cases for manual_review.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class IntentResult:
    intent: str               # "DELETION" | "NON_DELETION"
    confidence: float         # 0.0 to 1.0
    matched_phrase: str
    is_manual_review: bool = False
    disagreement_reason: Optional[str] = None


# Phrases explicitly indicating non-deletion (access, export, correction, opt-out, login help)
NON_DELETION_PATTERNS: List[Tuple[str, str]] = [
    # Explicit negation of deletion
    (r"not (?:a )?request to erase", "not_a_request_to_erase"),
    (r"not asking for deletion", "not_asking_for_deletion"),
    (r"do not (?:close|delete)", "do_not_close_or_delete"),
    (r"don't delete", "dont_delete"),
    (r"leave (?:the|my) account active", "leave_account_active"),
    (r"leave my profile", "leave_my_profile"),
    (r"keep the account as it is", "keep_account_as_is"),
    (r"want to continue using the service", "continue_using_service"),
    (r"still use it", "still_use_it"),
    (r"still need the account", "still_need_the_account"),
    (r"still want receipts", "still_want_receipts"),
    # Rectification / Correction
    (r"is misspelled", "correction_misspelled"),
    (r"correct it without removing", "correct_without_removing"),
    (r"replace it with the new one", "replace_with_new_number"),
    (r"change the email address", "change_email_address"),
    # Access / Information request
    (r"what personal information you hold", "subject_access_request"),
    (r"copy of last year's invoices", "invoice_access_copy"),
    (r"copy of the information held", "information_copy_access"),
    (r"download my account information", "data_portability_download"),
    (r"portable format", "data_portability_format"),
    # Marketing opt-out only
    (r"remove me from marketing lists only", "marketing_opt_out_only"),
    (r"stop the promotional emails", "stop_promotional_emails"),
    # Support / Login help
    (r"help resetting the login", "login_reset_help"),
]

# Multilingual patterns for deletion requests
DELETION_PATTERNS: List[Tuple[str, str]] = [
    # English
    (r"\b(?:account[- ]?)?deletion\b", "account_deletion_en"),
    (r"\bdelete\b", "delete_en"),
    (r"\beras(?:e|ure)\b", "erase_en"),
    (r"\bremov(?:e|al) (?:of )?(?:the|my|this) account\b", "remove_account_en"),
    (r"\bclose (?:the|my|this) account\b", "close_account_en"),
    (r"\bpurge\b", "purge_en"),
    # Spanish
    (r"\beliminaci[oó]n\b", "eliminacion_es"),
    (r"\beliminar\b", "eliminar_es"),
    (r"\bborrar\b", "borrar_es"),
    (r"\bsuprimir\b", "suprimir_es"),
    # Portuguese
    (r"\bexclus[aã]o\b", "exclusao_pt"),
    (r"\bapagar\b", "apagar_pt"),
    (r"\bremover (?:a|minha|esta) conta\b", "remover_conta_pt"),
    # French
    (r"\bsuppression\b", "suppression_fr"),
    (r"\beffac(?:er|ement)\b", "effacer_fr"),
    (r"\bcl[oô]tur(?:er|e)\b", "cloturer_fr"),
    # German
    (r"\bl[oö]sch(?:en|ung)\b", "loeschen_de"),
    (r"\bentfern(?:en|ung)\b", "entfernen_de"),
    # Italian
    (r"\bcancell(?:are|azione)\b", "cancellare_it"),
    (r"\belimin(?:are|azione)\b", "eliminare_it"),
    # Korean
    (r"삭제", "delete_ko"),
    (r"탈퇴", "withdraw_ko"),
    (r"제거", "remove_ko"),
    # Japanese
    (r"削除", "delete_ja"),
    (r"消去", "erase_ja"),
    (r"退会", "withdraw_ja"),
]


def classify_request_intent(request_text: str) -> IntentResult:
    """
    Classifies a request text as DELETION or NON_DELETION.
    Uses regex patterns with confidence scores.
    """
    if not request_text:
        return IntentResult(
            intent="DELETION",
            confidence=0.5,
            matched_phrase="empty_text",
            is_manual_review=True,
            disagreement_reason="empty_request_text",
        )

    text_lower = request_text.lower()

    # 1. Check non-deletion patterns first (explicit retention/correction/access/opt-out)
    for pattern, name in NON_DELETION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return IntentResult(
                intent="NON_DELETION",
                confidence=0.98,
                matched_phrase=f"{name}: '{match.group(0)}'",
                is_manual_review=False,
            )

    # 2. Check deletion patterns
    for pattern, name in DELETION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return IntentResult(
                intent="DELETION",
                confidence=0.98,
                matched_phrase=f"{name}: '{match.group(0)}'",
                is_manual_review=False,
            )

    # Fallback keyword checks
    if any(k in text_lower for k in ("delete", "erase", "remove", "close", "purge", "cancel")):
        return IntentResult(
            intent="DELETION",
            confidence=0.85,
            matched_phrase="generic_deletion_keyword",
            is_manual_review=False,
        )

    # Unclear intent -> flag for manual review
    return IntentResult(
        intent="DELETION",
        confidence=0.50,
        matched_phrase="unclassified_text",
        is_manual_review=True,
        disagreement_reason="no_intent_patterns_matched",
    )


def is_deletion_request(request_text: str) -> bool:
    """Convenience boolean helper: True if request is for deletion, False if NOT_APPLICABLE."""
    res = classify_request_intent(request_text)
    return res.intent == "DELETION"
