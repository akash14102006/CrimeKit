import io
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def generate_thumbnail(file_path: str, size: Tuple[int, int] = (256, 256), fmt: str = "PNG") -> Optional[bytes]:
    """Generate a thumbnail from an image file. Returns PNG bytes or None."""
    try:
        from PIL import Image
        img = Image.open(file_path)
        img.thumbnail(size)
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()
    except Exception as e:
        logger.debug("Thumbnail generation failed for %s: %s", file_path, e)
        return None


def generate_video_thumbnail(file_path: str, size: Tuple[int, int] = (256, 256)) -> Optional[bytes]:
    """Extract a frame from video as thumbnail using ffmpeg."""
    import subprocess
    import tempfile
    import os
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-vf", f"scale={size[0]}:{size[1]}",
            "-frames:v", "1", "-f", "image2", tmp_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and os.path.exists(tmp_path):
            with open(tmp_path, "rb") as f:
                data = f.read()
            os.unlink(tmp_path)
            return data
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception as e:
        logger.debug("Video thumbnail failed for %s: %s", file_path, e)
    return None
