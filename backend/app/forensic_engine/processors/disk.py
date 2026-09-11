import logging
import subprocess
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class DiskImageProcessor(BaseProcessor):
    name = "disk_image"
    description = "Processes disk images (E01, VMDK, ISO): Sleuth Kit integration, partition listing"
    supported_categories = frozenset({EvidenceCategory.DISK_IMAGE, EvidenceCategory.FORENSIC_DISK_IMAGE})
    priority = ProcessorPriority.ANALYSIS

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        ext = self._get_file_extension(evidence)
        self._list_partitions(evidence)
        if ext in ("iso", "img", "dd", "raw"):
            self._extract_filesystem_info(evidence)
        evidence.add_tag("disk_image")
        return evidence

    def _list_partitions(self, evidence: EvidenceSchema) -> None:
        try:
            result = subprocess.run(
                ["mmls", evidence.storage_path],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                evidence.metadata["partitions"] = result.stdout
            else:
                evidence.add_error(self.name, f"mmls failed: {result.stderr[:200]}")
        except FileNotFoundError:
            evidence.add_error(self.name, "Sleuth Kit (mmls) not found on PATH")
        except Exception as e:
            evidence.add_error(self.name, f"Partition listing failed: {e}")

    def _extract_filesystem_info(self, evidence: EvidenceSchema) -> None:
        try:
            result = subprocess.run(
                ["fls", "-r", evidence.storage_path],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                evidence.metadata["file_system_entries"] = len(lines)
                evidence.extracted_text = "\n".join(lines[:500])
        except FileNotFoundError:
            pass
        except Exception as e:
            evidence.add_error(self.name, f"Filesystem info failed: {e}")
