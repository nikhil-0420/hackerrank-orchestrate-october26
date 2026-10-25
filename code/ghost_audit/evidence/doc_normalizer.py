import re
from typing import Any, List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..loaders.pdf_loader import extract_pdf_text
from ..loaders.png_loader import extract_png_text
from ..observation import CoverageRecord, Identifiers, Observation

RESOURCE_RE = re.compile(
    r"\b((?:account|search|support|analytics|data_flow|backup|audit_record|audlt_record|tombstone|export|legal)_\d+)\b",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b([a-zA-Z0-9_\.\-\+]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,})\b")
USER_ID_RE = re.compile(r"\b(user_\d+)\b")
PHONE_RE = re.compile(r"(\+\d[\d\s\-]{8,}\d)")

STATUS_ACTIVE_RE = re.compile(r"\b(?:continuous|active|healthy)\b", re.IGNORECASE)
STATUS_DISABLED_RE = re.compile(r"\b(?:paused|disabled)\b", re.IGNORECASE)


def _extract_doc_observations(text: str, meta: EvidenceFileMeta, source_kind: str) -> List[Observation]:
    if not text:
        return []

    lines = [line.strip() for line in text.splitlines()]

    # Document-level identifiers
    doc_emails = sorted(set(e.strip().lower() for e in EMAIL_RE.findall(text)))
    doc_users = sorted(set(u.strip().lower() for u in USER_ID_RE.findall(text)))
    doc_phones = sorted(set(p.strip() for p in PHONE_RE.findall(text)))

    has_exactly_one_user = (
        len(doc_users) <= 1
        and len(doc_emails) <= 1
        and (len(doc_users) == 1 or len(doc_emails) == 1)
    )

    doc_email = doc_emails[0] if doc_emails else None
    doc_user = doc_users[0] if doc_users else None
    doc_phone = doc_phones[0] if doc_phones else None

    # Map normalized resource id -> list of line indices where it appears
    res_to_lines: dict[str, list[int]] = {}
    for i, line_text in enumerate(lines):
        for raw_rid in RESOURCE_RE.findall(line_text):
            r_id = raw_rid.strip().lower()
            if r_id.startswith("audlt_record_"):
                r_id = f"audit_record_{r_id[len('audlt_record_'):]}"
            res_to_lines.setdefault(r_id, []).append(i)

    if not res_to_lines:
        return []

    coll_name = meta.abs_path.stem
    observations = []

    for r_id in sorted(res_to_lines.keys()):
        line_indices = res_to_lines[r_id]

        email = None
        user_ref = None
        phone = None
        enabled = None

        # Pass 1: check same line across occurrences
        for i in line_indices:
            l_text = lines[i]
            m_em = EMAIL_RE.findall(l_text)
            if m_em and not email:
                email = m_em[0].strip().lower()
            m_usr = USER_ID_RE.findall(l_text)
            if m_usr and not user_ref:
                user_ref = m_usr[0].strip().lower()
            m_ph = PHONE_RE.findall(l_text)
            if m_ph and not phone:
                phone = m_ph[0].strip()
            if enabled is None:
                if STATUS_ACTIVE_RE.search(l_text):
                    enabled = True
                elif STATUS_DISABLED_RE.search(l_text):
                    enabled = False

        # Pass 2: check card/row [i : i+4] if still missing
        for i in line_indices:
            card_lines = []
            for j in range(i, min(len(lines), i + 4)):
                if j > i and any(other_rid != r_id and j in other_lines for other_rid, other_lines in res_to_lines.items()):
                    break
                card_lines.append(lines[j])
            card_text = " ".join(card_lines)

            if not email:
                m_em = EMAIL_RE.findall(card_text)
                if m_em:
                    email = m_em[0].strip().lower()
            if not user_ref:
                m_usr = USER_ID_RE.findall(card_text)
                if m_usr:
                    user_ref = m_usr[0].strip().lower()
            if not phone:
                m_ph = PHONE_RE.findall(card_text)
                if m_ph:
                    phone = m_ph[0].strip()
            if enabled is None:
                if STATUS_ACTIVE_RE.search(card_text):
                    enabled = True
                elif STATUS_DISABLED_RE.search(card_text):
                    enabled = False

        # Pass 3: fallback to document-level only if single user
        if has_exactly_one_user:
            if not email and doc_email:
                email = doc_email
            if not user_ref and doc_user:
                user_ref = doc_user
            if not phone and doc_phone:
                phone = doc_phone

        state_dict: dict[str, Any] = {
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
        if enabled is not None:
            state_dict["enabled"] = enabled
            state_dict["state"] = "ACTIVE" if enabled else "DISABLED"
            if r_id.startswith("backup_"):
                state_dict["restore_allowed"] = enabled

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
