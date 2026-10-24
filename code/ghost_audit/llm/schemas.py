"""
Enforced schemas for Ghost Audit LLM subsystem.
Rejects any unknown fields (extra='forbid') and enforces strict type validation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# L1: Intent Classification Schema
# ============================================================================

class IntentType(str, Enum):
    DELETE = "DELETE"
    ACCESS = "ACCESS"
    EXPORT = "EXPORT"
    CORRECTION = "CORRECTION"
    OPT_OUT = "OPT_OUT"
    OTHER = "OTHER"


class L1IntentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    intent: IntentType = Field(
        ...,
        description="The primary user intent: DELETE, ACCESS, EXPORT, CORRECTION, OPT_OUT, OTHER"
    )
    authorizes_deletion: bool = Field(
        ...,
        description="True if and only if the text specifically authorizes deletion/erasure/removal of personal data."
    )
    quote: str = Field(
        ...,
        description="Exact quote or phrase from the text justifying the classification (empty string if none)."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )


# ============================================================================
# L2: Document / OCR Extraction Schema
# ============================================================================

class ExtractedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(
        ...,
        description="Resource identifier explicitly present in the document/OCR text."
    )
    category: str = Field(
        ...,
        description="Resource category (e.g. USER_PROFILE, AUDIT_RECORD, SUPPORT_TICKET, BACKUP, LOG, ANALYTICS, OTHER)."
    )
    identifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Key-value mapping of extracted identifiers (e.g. user_id, email, phone)."
    )
    state: str = Field(
        ...,
        description="Current state observed in document (e.g. ACTIVE, DELETED, ARCHIVED, ANONYMIZED, UNKNOWN)."
    )
    fields_visible: List[str] = Field(
        default_factory=list,
        description="List of data fields visible in the record snippet."
    )


class L2DocumentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: List[ExtractedRecord] = Field(
        default_factory=list,
        description="List of records extracted from the document/image text. Must contain only resources verbatim in the text."
    )


# ============================================================================
# L4: Linkage Adjudication Schema
# ============================================================================

class LinkageDecision(str, Enum):
    LINK = "LINK"
    NO_LINK = "NO_LINK"


class L4LinkageOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: LinkageDecision = Field(
        ...,
        description="LINK if the candidate resource belongs to the subject, else NO_LINK."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(
        ...,
        description="Concise rationale for the adjudication."
    )
    hard_signal_ids: List[str] = Field(
        default_factory=list,
        description="IDs of verified hard signals (S1-S6) that support this linkage."
    )
