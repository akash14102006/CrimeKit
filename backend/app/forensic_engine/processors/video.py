import logging
import os
import subprocess
import json
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority
from ..utils.thumbnail import generate_video_thumbnail

logger = logging.getLogger(__name__)


class VideoProcessor(BaseProcessor):
    name = "video"
    description = "Processes video/audio: ffmpeg metadata extraction, frame thumbnails"
    supported_categories = frozenset({EvidenceCategory.VIDEO})
    priority = ProcessorPriority.VISUAL

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        self._extract_media_metadata(evidence)
        if config.generate_thumbnails:
            self._generate_thumbnail(evidence, config)
        self._extract_duration(evidence)
        evidence.add_tag("video")
        return evidence

    def _extract_media_metadata(self, evidence: EvidenceSchema) -> None:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", evidence.storage_path],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                evidence.metadata["ffprobe_format"] = info.get("format", {})
                evidence.metadata["ffprobe_streams"] = info.get("streams", [])
                fmt = info.get("format", {})
                if fmt.get("tags"):
                    for k, v in fmt["tags"].items():
                        if "date" in k.lower() or "time" in k.lower():
                            evidence.add_timeline_event(str(v), f"Video {k}: {v}", self.name)
                for stream in info.get("streams", []):
                    if stream.get("codec_type") == "video":
                        evidence.metadata["video_codec"] = stream.get("codec_name")
                        evidence.metadata["resolution"] = f"{stream.get('width')}x{stream.get('height')}"
                    elif stream.get("codec_type") == "audio":
                        evidence.metadata["audio_codec"] = stream.get("codec_name")
            else:
                evidence.add_error(self.name, f"ffprobe failed: {result.stderr[:200]}")
        except FileNotFoundError:
            evidence.add_error(self.name, "ffprobe not found on PATH")
        except Exception as e:
            evidence.add_error(self.name, f"Media metadata extraction failed: {e}")

    def _generate_thumbnail(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> None:
        thumb = generate_video_thumbnail(evidence.storage_path, config.thumbnail_size)
        if thumb:
            evidence.thumbnails["video_frame"] = thumb

    def _extract_duration(self, evidence: EvidenceSchema) -> None:
        fmt = evidence.metadata.get("ffprobe_format", {})
        duration = fmt.get("duration")
        if duration:
            try:
                evidence.metadata["duration_seconds"] = float(duration)
            except (ValueError, TypeError):
                pass
