"""Enterprise Forensic Processing Engine.

Modular processor architecture for forensic evidence analysis.
"""
from .schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessingResult, ProcessorPriority
from .base import BaseProcessor
from .pipeline import ProcessingPipeline
from .processors import ALL_PROCESSORS

try:
    from ..advanced_forensics import ALL_ADVANCED_PROCESSORS
    ALL_AVAILABLE_PROCESSORS = {**ALL_PROCESSORS, **ALL_ADVANCED_PROCESSORS}
except ImportError:
    ALL_AVAILABLE_PROCESSORS = ALL_PROCESSORS

__all__ = [
    "EvidenceSchema",
    "EvidenceCategory",
    "ForensicProcessorConfig",
    "ProcessingResult",
    "ProcessorPriority",
    "BaseProcessor",
    "ProcessingPipeline",
    "ALL_PROCESSORS",
    "ALL_AVAILABLE_PROCESSORS",
]
