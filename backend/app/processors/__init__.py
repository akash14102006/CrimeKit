"""Processor plugin registry and simple built-in processors."""
from typing import Callable, Dict
import hashlib
import mimetypes
import os
import io
from email import policy
from email.parser import BytesParser
try:
    from PIL import Image, ExifTags
except Exception:
    Image = None
try:
    # prefer modern pypdf package (replacement for PyPDF2)
    from pypdf import PdfReader
except Exception:
    PdfReader = None

_registry: Dict[str, Callable] = {}


def register(name: str):
    def _decorator(fn):
        _registry[name] = fn
        return fn
    return _decorator


def get_processor(name: str):
    return _registry.get(name)


def list_processors():
    return list(_registry.keys())


@register('hashes')
def proc_hashes(evidence_path: str, **kwargs):
    # compute SHA-256, SHA-1, MD5
    h_sha256 = hashlib.sha256()
    h_sha1 = hashlib.sha1()
    h_md5 = hashlib.md5()
    size = 0
    with open(evidence_path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 64)
            if not chunk:
                break
            size += len(chunk)
            h_sha256.update(chunk)
            h_sha1.update(chunk)
            h_md5.update(chunk)
    return {'sha256': h_sha256.hexdigest(), 'sha1': h_sha1.hexdigest(), 'md5': h_md5.hexdigest(), 'size': size}


@register('mime')
def proc_mime(evidence_path: str, filename: str = None, **kwargs):
    # basic mime detection
    mime = None
    if filename:
        mime = mimetypes.guess_type(filename)[0]
    if not mime:
        mime = 'application/octet-stream'
    return {'mime_type': mime}


@register('metadata')
def proc_metadata(evidence_path: str, **kwargs):
    # file metadata: timestamps and size
    stat = os.stat(evidence_path)
    return {'size': stat.st_size, 'created_at': stat.st_ctime, 'modified_at': stat.st_mtime}


@register('ocr')
def proc_ocr(evidence_path: str, **kwargs):
    """OCR/text extraction — handles PDFs via pypdf, images via pytesseract."""
    filename = kwargs.get('filename', evidence_path)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    # ── PDF path: use pypdf text extraction (no tesseract needed) ──
    if ext == 'pdf' or (hasattr(evidence_path, 'endswith') and evidence_path.endswith('.pdf')):
        return proc_pdf_text(evidence_path, **kwargs)

    # ── Image path: try pytesseract, then PIL fallback ──
    try:
        import pytesseract
        if Image is None:
            return {'text': 'Pillow not available for OCR'}
        img = Image.open(evidence_path)
        text = pytesseract.image_to_string(img)
        if text and text.strip():
            return {'text': text}
    except ImportError:
        pass
    except Exception:
        pass

    # ── Fallback: read as plain text ──
    try:
        with open(evidence_path, 'r', errors='replace') as f:
            text = f.read(100_000)
        if text and text.strip() and len(text.strip()) > 10:
            return {'text': text.strip()}
    except Exception:
        pass

    return {'text': 'ocr unavailable or failed'}


@register('image_analysis')
def proc_image_analysis(evidence_path: str, **kwargs):
    # basic image analysis: dimensions and thumbnail
    if Image is None:
        return {'error': 'Pillow not installed'}
    try:
        img = Image.open(evidence_path)
        w, h = img.size
        # generate thumbnail bytes
        thumb = img.copy()
        thumb.thumbnail((256, 256))
        buf = io.BytesIO()
        thumb.save(buf, format='PNG')
        thumb_b64 = None
        try:
            import base64
            thumb_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        except Exception:
            thumb_b64 = None
        exif = None
        try:
            exif_data = img._getexif()
            if exif_data:
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
        except Exception:
            exif = None
        return {'width': w, 'height': h, 'thumbnail': thumb_b64, 'exif': exif}
    except Exception as e:
        return {'error': str(e)}


@register('image_metadata')
def proc_image_metadata(evidence_path: str, **kwargs):
    if Image is None:
        return {'error': 'Pillow not installed'}
    try:
        img = Image.open(evidence_path)
        exif = None
        try:
            exif_data = img._getexif()
            if exif_data:
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
        except Exception:
            exif = None
        return {'format': img.format, 'mode': img.mode, 'size': img.size, 'exif': exif}
    except Exception as e:
        return {'error': str(e)}


@register('pdf_text')
def proc_pdf_text(evidence_path: str, **kwargs):
    if PdfReader is None:
        return {'error': 'PDF reader not installed (pypdf or PyPDF2)'}
    try:
        with open(evidence_path, 'rb') as f:
            reader = PdfReader(f)
            texts = []
            # page access is consistent between pypdf and PyPDF2 via reader.pages
            for page in getattr(reader, 'pages', [])[:3]:
                # pypdf uses extract_text(), PyPDF2 may also support it
                text = ''
                try:
                    text = page.extract_text() or ''
                except Exception:
                    try:
                        text = page.get_text() or ''
                    except Exception:
                        text = ''
                texts.append(text)
            return {'text': '\n'.join(texts)}
    except Exception as e:
        return {'error': str(e)}


@register('zip_list')
def proc_zip_list(evidence_path: str, **kwargs):
    import zipfile
    try:
        with zipfile.ZipFile(evidence_path, 'r') as z:
            return {'files': z.namelist()}
    except Exception as e:
        return {'error': str(e)}


@register('email_parse')
def proc_email_parse(evidence_path: str, **kwargs):
    try:
        with open(evidence_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        return {'subject': msg.get('subject'), 'from': msg.get('from'), 'to': msg.get('to'), 'body': msg.get_body(preferencelist=('plain', 'html')).get_content() if msg.get_body() else None}
    except Exception as e:
        return {'error': str(e)}
