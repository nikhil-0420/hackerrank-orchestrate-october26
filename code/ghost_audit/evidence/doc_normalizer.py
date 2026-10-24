import re
from typing import List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..loaders.pdf_loader import extract_pdf_text
from ..loaders.png_loader import extract_png_text
from ..observation import CoverageRecord, Identifiers, Observation

RESOURCE_RE = re.compile(
    r"\b((?:account|search|support|analytics|data_flow|backup|audit_record|tombstone|export|legal)_\w+)\b",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b([a-zA-Z0-9_\.\-\+]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,})\b")
USER_ID_RE = re.compile(r"\b(user_\d+)\b")
PHONE_RE = re.compile(r"(\+\d[\d\s\-]{8,}\d)")


def _extract_doc_observations(text: str, meta: EvidenceFileMeta, source_kind: str) -> List[Observation]:
    if not text:
        return []

    observations = []

    # Document-level identifiers
    doc_emails = EMAIL_RE.findall(text)
    doc_users = USER_ID_RE.findall(text)
    doc_phones = PHONE_RE.findall(text)

    email = doc_emails[0].strip().lower() if doc_emails else None
    user_ref = doc_users[0].strip() if doc_users else None
    phone = doc_phones[0].strip() if doc_phones else None

    # Check distinct resources in text
    found_resources = set(RESOURCE_RE.findall(text))
    coll_name = meta.abs_path.stem

    for r_id in sorted(found_resources):
        state_dict = {
            "resource_id": r_id,
            "file": meta.file_path,
        }
        if "attachment" in meta.file_path.lower() or "attachment" in coll_name.lower():
            state_dict["attachment_name"] = meta.abs_path.name
            state_dict["category"] = "SUPPORT_ATTACHMENT"
        if email:
            state_dict["email"] = email
        if user_ref:
            state_dict["user_id"] = user_ref
        if phone:
            state_dict["phone"] = phone

        obs = Observation(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            obs_time=meta.captured_at,
            system_id=meta.origin,
            collection=coll_name,
            resource_id=r_id,
            identifiers=Identifiers(
                email=email,
                phone=phone,
                email_hash=None,
                user_ref=user_ref,
                name=None,
                masked=False,
                raw_identifiers={"email": email} if email else {},
            ),
            state=state_dict,
            source_kind=source_kind,
            raw_ref=f"{source_kind}:{meta.file_id} id:{r_id}",
        )
        observations.append(obs)

    return observations


def normalize_pdf_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Extracts layout text from a PDF, caches under code/.cache/ by sha256.
    Parses structured observations from document contents.
    """
    text = extract_pdf_text(meta.abs_path)
    observations = _extract_doc_observations(text, meta, "pdf")
    coverage_records = [
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="document_pdf",
            obs_time=meta.captured_at,
            source_kind="pdf",
            record_count=len(observations),
        )
    ]
    return observations, coverage_records, 0


def normalize_png_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Extracts OCR text from a PNG image, caches under code/.cache/ by sha256.
    Parses structured observations from image OCR contents.
    """
    text = extract_png_text(meta.abs_path)
    observations = _extract_doc_observations(text, meta, "image")
    coverage_records = [
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="admin_screenshot_png",
            obs_time=meta.captured_at,
            source_kind="image",
            record_count=len(observations),
        )
    ]
    return observations, coverage_records, 0
