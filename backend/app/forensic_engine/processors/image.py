import logging
import os
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority
from ..utils.thumbnail import generate_thumbnail
from ..utils.ocr import run_ocr

logger = logging.getLogger(__name__)


class ImageProcessor(BaseProcessor):
    name = "image"
    description = "Processes images: EXIF extraction, OCR, thumbnail generation"
    supported_categories = frozenset({EvidenceCategory.IMAGE})
    priority = ProcessorPriority.VISUAL

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        ext = self._get_file_extension(evidence)

        self._extract_exif(evidence)

        if config.generate_thumbnails:
            self._generate_thumbnail(evidence, config)

        if config.run_ocr:
            self._run_ocr(evidence, config)

        evidence.add_tag("image")
        return evidence

    def _extract_exif(self, evidence: EvidenceSchema) -> None:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            img = Image.open(evidence.storage_path)
            exif_data = img._getexif()
            if exif_data:
                exif = {TAGS.get(k, str(k)): v for k, v in exif_data.items()}
                evidence.metadata["exif"] = exif
                for k, v in exif.items():
                    if "date" in k.lower() and isinstance(v, str):
                        evidence.add_timeline_event(v, f"Image {k}: {v}", self.name)
            evidence.metadata["format"] = img.format
            evidence.metadata["mode"] = img.mode
            evidence.metadata["dimensions"] = list(img.size)
        except Exception as e:
            evidence.add_error(self.name, f"EXIF extraction failed: {e}")

    def _generate_thumbnail(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> None:
        thumb = generate_thumbnail(evidence.storage_path, config.thumbnail_size)
        if thumb:
            evidence.thumbnails["image"] = thumb

    def _run_ocr(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> None:
        text = run_ocr(evidence.storage_path, config.ocr_language)
        if text:
            evidence.ocr_text = text
            if not evidence.extracted_text:
                evidence.extracted_text = text
