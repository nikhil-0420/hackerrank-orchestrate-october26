import hashlib
import shutil
import subprocess
from pathlib import Path
from ..paths import OCR_CACHE_DIR


def get_file_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _get_tesseract_bins() -> list[str]:
    bins = []
    which = shutil.which("tesseract")
    if which:
        bins.append(which)
    common_paths = [
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe",
    ]
    for p in common_paths:
        if p.exists() and str(p) not in bins:
            bins.append(str(p))
    if not bins:
        bins.append("tesseract")
    return bins


def extract_png_text(png_path: Path) -> str:
    """
    Extract OCR text from a PNG image with sha256-based caching.
    Reads from committed code/ocr_cache/<sha256>.txt so output is hermetic and
    does not depend on the host machine.
    """
    file_hash = get_file_sha256(png_path)

    # 1. Read from committed code/ocr_cache/
    cache_file = OCR_CACHE_DIR / f"{file_hash}.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")

    text = ""
    tess_bins = _get_tesseract_bins()

    # 2. Try pytesseract
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
        if tess_bins and tess_bins[0] != "tesseract":
            pytesseract.pytesseract.tesseract_cmd = tess_bins[0]
        with Image.open(png_path) as img:
            text = pytesseract.image_to_string(img)
    except (ImportError, Exception):
        pass

    # 3. Try tesseract CLI across known binaries
    if not text:
        for tess_bin in tess_bins:
            try:
                proc = subprocess.run(
                    [tess_bin, str(png_path), "stdout"],
                    capture_output=True,
                    check=False,
                    text=True
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    text = proc.stdout
                    break
            except (FileNotFoundError, OSError):
                pass

    if not text:
        text = "[OCR_NOT_AVAILABLE: tesseract/pytesseract not installed]"

    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(text, encoding="utf-8")
    return text

