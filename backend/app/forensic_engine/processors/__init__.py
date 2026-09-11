from .image import ImageProcessor
from .video import VideoProcessor
from .pdf import PDFProcessor
from .office import OfficeProcessor
from .email import EmailProcessor
from .archive import ArchiveProcessor
from .mobile import MobileArtifactProcessor
from .disk import DiskImageProcessor

ALL_PROCESSORS = {
    "image": ImageProcessor,
    "video": VideoProcessor,
    "pdf": PDFProcessor,
    "office": OfficeProcessor,
    "email": EmailProcessor,
    "archive": ArchiveProcessor,
    "mobile_artifact": MobileArtifactProcessor,
    "disk_image": DiskImageProcessor,
}

__all__ = [
    "ImageProcessor", "VideoProcessor", "PDFProcessor", "OfficeProcessor",
    "EmailProcessor", "ArchiveProcessor", "MobileArtifactProcessor", "DiskImageProcessor",
    "ALL_PROCESSORS",
]
