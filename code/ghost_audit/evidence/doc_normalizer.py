from typing import List, Tuple
from ..loaders.manifest import EvidenceFileMeta
from ..loaders.pdf_loader import extract_pdf_text
from ..loaders.png_loader import extract_png_text
from ..observation import CoverageRecord, Observation


def normalize_pdf_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Extracts layout text from a PDF, caches under code/.cache/ by sha256.
    Text is stored for downstream LLM extraction in Phase 2.
    """
    text = extract_pdf_text(meta.abs_path)
    coverage_records = [
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="document_pdf",
            obs_time=meta.captured_at,
            source_kind="pdf",
            record_count=1 if text else 0,
        )
    ]
    # No unparsed lines; raw text stored in cache
    return [], coverage_records, 0


def normalize_png_file(meta: EvidenceFileMeta) -> Tuple[List[Observation], List[CoverageRecord], int]:
    """
    Extracts OCR text from a PNG image, caches under code/.cache/ by sha256.
    Text is stored for downstream LLM extraction in Phase 2.
    """
    text = extract_png_text(meta.abs_path)
    coverage_records = [
        CoverageRecord(
            file_id=meta.file_id,
            file_captured_at=meta.captured_at,
            system_id=meta.origin,
            collection="admin_screenshot_png",
            obs_time=meta.captured_at,
            source_kind="image",
            record_count=1 if text else 0,
        )
    ]
    return [], coverage_records, 0
