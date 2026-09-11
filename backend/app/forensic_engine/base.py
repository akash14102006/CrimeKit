from abc import ABC, abstractmethod
from typing import Optional, Set

from .schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority


class BaseProcessor(ABC):
    """Base class for all forensic processors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique processor name used for registration."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        ...

    @property
    @abstractmethod
    def supported_categories(self) -> Set[EvidenceCategory]:
        """Set of evidence categories this processor handles."""
        ...

    @property
    def priority(self) -> ProcessorPriority:
        """Execution order - lower values run first."""
        return ProcessorPriority.ANALYSIS

    @abstractmethod
    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        """Process evidence and return enriched schema."""
        ...

    def can_process(self, evidence: EvidenceSchema) -> bool:
        """Check if this processor can handle the given evidence."""
        if evidence.category in self.supported_categories:
            return True
        if evidence.category == EvidenceCategory.UNKNOWN and EvidenceCategory.UNKNOWN in self.supported_categories:
            return True
        return False

    def _get_file_extension(self, evidence: EvidenceSchema) -> str:
        return evidence.filename.rsplit(".", 1)[-1].lower() if "." in evidence.filename else ""
