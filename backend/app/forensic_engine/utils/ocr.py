import logging
import os
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

# Lazily-initialized OCR engine singletons (avoid reloading models per call).
_PADDLE_OCR = None
_PADDLE_TRIED = False


def _get_paddle_ocr(language: str):
    """Return a cached PaddleOCR instance, or None if unavailable."""
    global _PADDLE_OCR, _PADDLE_TRIED
    if _PADDLE_TRIED:
        return _PADDLE_OCR
    _PADDLE_TRIED = True
    try:
        from paddleocr import PaddleOCR

        # Map tesseract-style lang codes to PaddleOCR languages where possible.
        paddle_lang = "en" if language in ("eng", "en") else language
        _PADDLE_OCR = PaddleOCR(use_angle_cls=True, lang=paddle_lang, show_log=False)
        logger.info("PaddleOCR engine initialized (lang=%s)", paddle_lang)
    except Exception as e:
        logger.debug("PaddleOCR unavailable (%s) — falling back to pytesseract", e)
        _PADDLE_OCR = None
    return _PADDLE_OCR


def run_ocr(file_path: str, language: str = "eng") -> Optional[str]:
    """Run OCR on an image file.

    Uses PaddleOCR when available (preferred per forensic pipeline design),
    otherwise falls back to pytesseract. Returns extracted text or None.
    """
    # 1) PaddleOCR (preferred)
    try:
        ocr = _get_paddle_ocr(language)
        if ocr is not None:
            result = ocr.ocr(file_path, cls=True)
            texts = []
            for line in result or []:
                for item in line or []:
                    if item and len(item) >= 2 and item[1]:
                        texts.append(item[1][0])
            if texts:
                return "\n".join(t.strip() for t in texts if t.strip())
    except Exception as e:
        logger.debug("PaddleOCR failed for %s: %s", file_path, e)

    # 2) pytesseract fallback
    try:
        import pytesseract
        from PIL import Image

        text = pytesseract.image_to_string(Image.open(file_path), lang=language)
        if text and text.strip():
            return text.strip()
    except FileNotFoundError:
        logger.debug("pytesseract/tesseract not available for %s", file_path)
    except Exception as e:
        logger.debug("pytesseract OCR failed for %s: %s", file_path, e)

    # 3) Legacy tesseract CLI fallback (if installed)
    try:
        result = subprocess.run(
            ["tesseract", file_path, "stdout", "-l", language],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        logger.debug("tesseract CLI not found on PATH")
    except subprocess.TimeoutExpired:
        logger.warning("OCR timed out for %s", file_path)
    except Exception as e:
        logger.debug("tesseract CLI OCR failed for %s: %s", file_path, e)

    return None


def run_ocr_on_pdf(file_path: str, language: str = "eng", max_pages: int = 5) -> Optional[str]:
    """Extract text from PDF, falling back to OCR for scanned pages."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        texts = []
        pages = reader.pages[:max_pages]
        for page in pages:
            try:
                text = page.extract_text() or ""
                texts.append(text)
            except Exception:
                pass
        combined = "\n".join(texts).strip()
        if combined and len(combined) > 50:
            return combined
    except Exception:
        pass
    return _ocr_pdf_images(file_path, language, max_pages)


def _ocr_pdf_images(file_path: str, language: str, max_pages: int) -> Optional[str]:
    """Convert PDF pages to images and OCR them."""
    import subprocess
    import tempfile
    import os
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                "pdftoppm", "-png", "-r", "300",
                "-l", str(max_pages), file_path,
                os.path.join(tmpdir, "page"),
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                return None
            texts = []
            for fname in sorted(os.listdir(tmpdir)):
                if fname.endswith(".png"):
                    page_text = run_ocr(os.path.join(tmpdir, fname), language)
                    if page_text:
                        texts.append(page_text)
            return "\n".join(texts).strip() if texts else None
    except Exception as e:
        logger.debug("PDF OCR failed for %s: %s", file_path, e)
    return None
