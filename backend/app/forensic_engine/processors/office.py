import logging
import subprocess
import tempfile
import os
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class OfficeProcessor(BaseProcessor):
    name = "office"
    description = "Processes Office documents: text extraction via LibreOffice or tika"
    supported_categories = frozenset({EvidenceCategory.OFFICE})
    priority = ProcessorPriority.TEXT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        self._extract_text(evidence, config)
        evidence.add_tag("office")
        return evidence

    def _extract_text(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> None:
        text = self._try_libreoffice(evidence)
        if not text:
            text = self._try_tika(evidence)
        if text:
            evidence.extracted_text = text

    def _try_libreoffice(self, evidence: EvidenceSchema) -> str:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "txt:Text",
                     "--outdir", tmpdir, evidence.storage_path],
                    capture_output=True, timeout=120,
                )
                if result.returncode == 0:
                    txt_files = [f for f in os.listdir(tmpdir) if f.endswith(".txt")]
                    if txt_files:
                        with open(os.path.join(tmpdir, txt_files[0]), "r", errors="replace") as f:
                            return f.read().strip()
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.debug("LibreOffice conversion failed for %s: %s", evidence.filename, e)
        return ""

    def _try_tika(self, evidence: EvidenceSchema) -> str:
        try:
            import requests
            resp = requests.put(
                "http://localhost:9998/tika",
                data=open(evidence.storage_path, "rb"),
                headers={"Accept": "text/plain"},
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass
        return ""
