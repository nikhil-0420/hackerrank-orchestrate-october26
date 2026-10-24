import hashlib
import subprocess
from pathlib import Path
from ..paths import CACHE_DIR


def get_file_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_png_text(png_path: Path) -> str:
    """
    Extract OCR text from a PNG image with sha256-based caching.
    Tries pytesseract or tesseract CLI if installed; caches result.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    file_hash = get_file_sha256(png_path)
    cache_file = CACHE_DIR / f"png_{file_hash}.txt"

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")

    text = ""
    # 1. Try pytesseract
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
        with Image.open(png_path) as img:
            text = pytesseract.image_to_string(img)
    except (ImportError, Exception):
        pass

    # 2. Try tesseract CLI
    if not text:
        try:
            proc = subprocess.run(
                ["tesseract", str(png_path), "stdout"],
                capture_output=True,
                check=False,
                text=True
            )
            if proc.returncode == 0 and proc.stdout.strip():
                text = proc.stdout
        except FileNotFoundError:
            pass

    if not text:
        text = "[OCR_NOT_AVAILABLE: tesseract/pytesseract not installed]"

    cache_file.write_text(text, encoding="utf-8")
    return text
