import hashlib
import subprocess
from pathlib import Path
from ..paths import OCR_CACHE_DIR


def get_file_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract text from a PDF file with sha256-based caching.
    Reads from committed code/ocr_cache/<sha256>.txt so output is hermetic.
    """
    file_hash = get_file_sha256(pdf_path)

    # 1. Read from committed code/ocr_cache/
    cache_file = OCR_CACHE_DIR / f"{file_hash}.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")

    text = ""
    # 1. Try pdftotext CLI
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            check=False,
            text=True
        )
        if proc.returncode == 0 and proc.stdout.strip():
            text = proc.stdout
    except FileNotFoundError:
        pass

    # 2. Try pdfplumber
    if not text:
        try:
            import pdfplumber  # type: ignore
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = [p.extract_text(layout=True) or "" for p in pdf.pages]
                text = "\n".join(pages_text)
        except ImportError:
            pass

    # 3. Try pypdf
    if not text:
        try:
            from pypdf import PdfReader  # type: ignore
            reader = PdfReader(str(pdf_path))
            pages_text = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages_text)
        except ImportError:
            pass

    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(text, encoding="utf-8")
    return text
