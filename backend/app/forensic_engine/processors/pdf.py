import logging
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority
from ..utils.ocr import run_ocr_on_pdf

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    name = "pdf"
    description = "Processes PDFs: text extraction, page count, OCR for scanned documents"
    supported_categories = frozenset({EvidenceCategory.PDF})
    priority = ProcessorPriority.TEXT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        self._extract_text(evidence, config)
        self._extract_metadata(evidence)
        evidence.add_tag("pdf")
        return evidence

    def _extract_text(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> None:
        try:
            from pypdf import PdfReader
            reader = PdfReader(evidence.storage_path)
            evidence.metadata["page_count"] = len(reader.pages)
            texts = []
            pages_to_read = min(len(reader.pages), config.max_pages_text)
            for i in range(pages_to_read):
                try:
                    text = reader.pages[i].extract_text() or ""
                    texts.append(text)
                except Exception:
                    pass
            combined = "\n".join(texts).strip()
            if combined and len(combined) > 50:
                evidence.extracted_text = combined
            else:
                ocr_text = run_ocr_on_pdf(evidence.storage_path, config.ocr_language, config.max_pages_text)
                if ocr_text:
                    evidence.ocr_text = ocr_text
                    if not evidence.extracted_text:
                        evidence.extracted_text = ocr_text
        except Exception as e:
            evidence.add_error(self.name, f"PDF text extraction failed: {e}")

    def _extract_metadata(self, evidence: EvidenceSchema) -> None:
        try:
            from pypdf import PdfReader
            reader = PdfReader(evidence.storage_path)
            info = reader.metadata
            if info:
                meta = {}
                for key in ("/Title", "/Author", "/Subject", "/Creator", "/Producer",
                            "/CreationDate", "/ModDate"):
                    val = info.get(key)
                    if val:
                        meta[key.lstrip("/")] = str(val)
                evidence.metadata["pdf_info"] = meta
                for k, v in meta.items():
                    if "date" in k.lower():
                        evidence.add_timeline_event(v, f"PDF {k}: {v}", self.name)
        except Exception as e:
            evidence.add_error(self.name, f"PDF metadata extraction failed: {e}")
