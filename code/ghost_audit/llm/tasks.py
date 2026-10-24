"""
Ghost Audit LLM Task Implementations: L1, L2, L4.
Enforces untrusted model output validation:
- Code validates every field
- Code wins every safety disagreement
- Delimited data blocks for all external text
- Cross-checks with CLASSIFY_REQUEST rows and flags manual_review
- Rejects fabricated resource IDs from L2 document extraction
- Enforces hard signal requirements on L4 linkage adjudication
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from ghost_audit.intent import classify_request_intent
from ghost_audit.llm.client import LLMClient
from ghost_audit.llm.schemas import (
    ExtractedRecord,
    IntentType,
    L1IntentOutput,
    L2DocumentOutput,
    L4LinkageOutput,
    LinkageDecision,
)
from ghost_audit.loaders.manifest import EvidenceFileMeta


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _read_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


SYSTEM_PROMPT = _read_prompt("system_prompt.md")
L1_PROMPT = _read_prompt("l1_intent.md")
L2_PROMPT = _read_prompt("l2_document.md")
L4_PROMPT = _read_prompt("l4_linkage.md")


# ============================================================================
# L1: Intent Classification
# ============================================================================

def run_l1_intent_classification(
    client: LLMClient,
    case_id: str,
    request_text: str,
    intake_records: Optional[Dict[str, str]] = None,
) -> Tuple[L1IntentOutput, bool, Optional[Dict[str, Any]]]:
    """
    Executes multilingual intent classification for request_text.
    Cross-checks with CLASSIFY_REQUEST rows.
    Returns: (L1IntentOutput, is_model_call, manual_review_info_or_None)
    """
    # Deterministic fallback generator
    def fallback() -> L1IntentOutput:
        det = classify_request_intent(request_text)
        is_del = (det.intent == "DELETION")
        return L1IntentOutput(
            intent=IntentType.DELETE if is_del else IntentType.OTHER,
            authorizes_deletion=is_del,
            quote=det.matched_phrase,
            confidence=det.confidence,
        )

    # Delimited data block
    user_input = f"<request_text>\n{request_text}\n</request_text>"

    res, is_model, _ = client.call_structured(
        task_name="L1",
        system_prompt=SYSTEM_PROMPT,
        task_prompt=L1_PROMPT,
        user_input=user_input,
        schema_cls=L1IntentOutput,
        fallback_fn=fallback,
        target_id=case_id,
    )

    # Cross-check with CLASSIFY_REQUEST intake records
    manual_review: Optional[Dict[str, Any]] = None
    if intake_records and case_id in intake_records:
        intake_detail = intake_records[case_id].lower()
        intake_says_non_deletion = "non-deletion" in intake_detail
        if intake_says_non_deletion and res.authorizes_deletion:
            # Model classified as deletion, but official intake logged non-deletion!
            # Code wins: flag for manual review and DO NOT silently change the case
            manual_review = {
                "case_id": case_id,
                "reason": "DISAGREEMENT_CLASSIFY_REQUEST",
                "model_intent": res.intent.value,
                "intake_logged": "non-deletion",
                "action": "FLAGGED_FOR_MANUAL_REVIEW_CODE_SAFETY_PRESERVED",
            }
            # Fail closed: override authorizes_deletion to False to preserve code safety
            res = L1IntentOutput(
                intent=IntentType.OTHER,
                authorizes_deletion=False,
                quote=f"Intake override: {intake_records[case_id]}",
                confidence=res.confidence,
            )

    return res, is_model, manual_review


# ============================================================================
# L2: Vision / PDF Extraction
# ============================================================================

def run_l2_document_extraction(
    client: LLMClient,
    file_id: str,
    text_content: str,
) -> Tuple[L2DocumentOutput, bool, int, List[str]]:
    """
    Extracts structured records from document/OCR text for the 15 files.
    Cached by file hash.
    Rejects any resource_id that does not appear verbatim in text_content.
    Returns: (validated_output, is_model_call, rejected_hallucinations_count, extracted_rids)
    """
    file_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()

    def fallback() -> L2DocumentOutput:
        # Verbatim regex extraction
        matches = re.findall(r"\b(audit_record_\d+|support_\d+|account_\d+|backup_\d+|log_\d+)\b", text_content)
        records = []
        for m in sorted(set(matches)):
            records.append(
                ExtractedRecord(
                    resource_id=m,
                    category="DOCUMENT_RECORD",
                    identifiers={},
                    state="ACTIVE",
                    fields_visible=["resource_id"],
                )
            )
        return L2DocumentOutput(records=records)

    user_input = f"<document_text file_id=\"{file_id}\" hash=\"{file_hash}\">\n{text_content}\n</document_text>"

    raw_output, is_model, _ = client.call_structured(
        task_name="L2",
        system_prompt=SYSTEM_PROMPT,
        task_prompt=L2_PROMPT,
        user_input=user_input,
        schema_cls=L2DocumentOutput,
        fallback_fn=fallback,
        target_id=f"file:{file_id}",
    )

    # Code validation: Reject any resource_id not present in text_content
    verified_records: List[ExtractedRecord] = []
    rejected_count = 0
    extracted_rids: List[str] = []

    for rec in raw_output.records:
        if rec.resource_id in text_content:
            verified_records.append(rec)
            extracted_rids.append(rec.resource_id)
        else:
            rejected_count += 1
            client.log_silent_failure(
                "L2",
                f"file:{file_id}",
                f"REJECTED_HALLUCINATED_RESOURCE_ID: {rec.resource_id}",
            )

    output = L2DocumentOutput(records=verified_records)
    return output, is_model, rejected_count, extracted_rids


# ============================================================================
# L4: Linkage Adjudication
# ============================================================================

HARD_SIGNAL_PREFIXES = ("S1_", "S2_", "S3_", "S4_", "S5_", "S6_")


def run_l4_linkage_adjudication(
    client: LLMClient,
    case_id: str,
    candidate_resource_id: str,
    candidate_signals: List[Any],
    subject_info: Dict[str, Any],
) -> Tuple[L4LinkageOutput, bool, bool]:
    """
    Adjudicates candidate linkage for ambiguous resources.
    Hard invariant: Accepted ONLY IF >= 1 hard signal supports it.
    If model attempts to link without hard signal: Code safety overrides to NO_LINK!
    Returns: (output, is_model_call, was_safety_override)
    """
    has_hard_signal = any(
        getattr(s, "signal_name", str(s)).startswith(HARD_SIGNAL_PREFIXES)
        for s in candidate_signals
    )
    hard_ids = [
        getattr(s, "signal_name", str(s))[:2]
        for s in candidate_signals
        if getattr(s, "signal_name", str(s)).startswith(HARD_SIGNAL_PREFIXES)
    ]

    def fallback() -> L4LinkageOutput:
        if has_hard_signal:
            return L4LinkageOutput(
                decision=LinkageDecision.LINK,
                confidence=0.98,
                reasoning="Deterministic rule: verified hard signal exists",
                hard_signal_ids=hard_ids,
            )
        else:
            return L4LinkageOutput(
                decision=LinkageDecision.NO_LINK,
                confidence=0.98,
                reasoning="Deterministic rule: no hard signals support candidate",
                hard_signal_ids=[],
            )

    sig_names = [getattr(s, "signal_name", str(s)) for s in candidate_signals]
    user_input = (
        f"<subject case_id=\"{case_id}\">\n"
        f"  user_id: {subject_info.get('user_id', '')}\n"
        f"  email: {subject_info.get('email', '')}\n"
        f"</subject>\n"
        f"<candidate>\n"
        f"  resource_id: {candidate_resource_id}\n"
        f"  signals: {sig_names}\n"
        f"</candidate>"
    )

    output, is_model, _ = client.call_structured(
        task_name="L4",
        system_prompt=SYSTEM_PROMPT,
        task_prompt=L4_PROMPT,
        user_input=user_input,
        schema_cls=L4LinkageOutput,
        fallback_fn=fallback,
        target_id=f"{case_id}:{candidate_resource_id}",
    )

    was_safety_override = False
    # Enforce Hard Rule: Code wins every safety disagreement!
    if output.decision == LinkageDecision.LINK and not has_hard_signal:
        # Model hallucinated or over-linked without hard signals!
        # Code overrides to NO_LINK to protect data subject safety
        was_safety_override = True
        output = L4LinkageOutput(
            decision=LinkageDecision.NO_LINK,
            confidence=1.0,
            reasoning="CODE_SAFETY_OVERRIDE: Hard rule requires >= 1 hard signal (S1-S6) to link",
            hard_signal_ids=[],
        )
        client.log_silent_failure(
            "L4",
            f"{case_id}:{candidate_resource_id}",
            "SAFETY_OVERRIDE_PREVENTED_UNAUTHORIZED_LINK",
        )

    return output, is_model, was_safety_override
