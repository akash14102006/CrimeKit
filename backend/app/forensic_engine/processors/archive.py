import logging
import os
import hashlib
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class ArchiveProcessor(BaseProcessor):
    name = "archive"
    description = "Processes archives (zip, rar, 7z, tar): listing, hash computation of contents"
    supported_categories = frozenset({EvidenceCategory.ARCHIVE})
    priority = ProcessorPriority.TEXT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        ext = self._get_file_extension(evidence)
        if ext == "zip":
            self._process_zip(evidence)
        elif ext in ("rar",):
            self._process_rar(evidence)
        elif ext in ("7z",):
            self._process_7z(evidence)
        elif ext in ("tar", "gz", "bz2"):
            self._process_tar(evidence)
        evidence.add_tag("archive")
        return evidence

    def _process_zip(self, evidence: EvidenceSchema) -> None:
        import zipfile
        try:
            with zipfile.ZipFile(evidence.storage_path, "r") as z:
                file_list = z.namelist()
                evidence.metadata["archive_files"] = file_list
                evidence.metadata["archive_file_count"] = len(file_list)
                evidence.extracted_text = "\n".join(file_list)
                hashes = {}
                for name in file_list:
                    info = z.getinfo(name)
                    hashes[name] = {"size": info.file_size}
                    if not name.endswith("/"):
                        try:
                            data = z.read(name)
                            hashes[name]["sha256"] = hashlib.sha256(data).hexdigest()
                        except Exception:
                            pass
                evidence.metadata["archive_file_hashes"] = hashes
        except Exception as e:
            evidence.add_error(self.name, f"ZIP processing failed: {e}")

    def _process_rar(self, evidence: EvidenceSchema) -> None:
        try:
            import rarfile
            with rarfile.RarFile(evidence.storage_path) as rf:
                file_list = rf.namelist()
                evidence.metadata["archive_files"] = file_list
                evidence.metadata["archive_file_count"] = len(file_list)
                evidence.extracted_text = "\n".join(file_list)
        except ImportError:
            evidence.add_error(self.name, "rarfile not installed")
        except Exception as e:
            evidence.add_error(self.name, f"RAR processing failed: {e}")

    def _process_7z(self, evidence: EvidenceSchema) -> None:
        import subprocess
        try:
            result = subprocess.run(
                ["7z", "l", evidence.storage_path],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                evidence.extracted_text = result.stdout
                evidence.metadata["archive_listing"] = result.stdout
        except FileNotFoundError:
            evidence.add_error(self.name, "7z not found on PATH")
        except Exception as e:
            evidence.add_error(self.name, f"7z processing failed: {e}")

    def _process_tar(self, evidence: EvidenceSchema) -> None:
        import tarfile
        try:
            with tarfile.open(evidence.storage_path) as tf:
                file_list = tf.getnames()
                evidence.metadata["archive_files"] = file_list
                evidence.metadata["archive_file_count"] = len(file_list)
                evidence.extracted_text = "\n".join(file_list)
        except Exception as e:
            evidence.add_error(self.name, f"TAR processing failed: {e}")
