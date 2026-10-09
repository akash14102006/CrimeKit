"""
NVIDIA Speech NIM Audio Forensic Transcription Adapter.

Pipeline:
Audio Evidence
→ Speech NIM ASR
→ Timestamped Transcript
→ GLiNER / NER
→ Entity Resolution
→ Timeline & Knowledge Graph
→ Testimony cross-check

Requirements:
- Emits events:
  speech.transcription.started, speech.transcription.completed, speech.transcription.failed
- Stores transcript, timestamps, confidence, source evidence ID, model, processing time.
- Clean mock/fallback adapter when local NVIDIA Speech NIM is unavailable.
"""

import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

SPEECH_NIM_ENDPOINT = os.getenv("NVIDIA_SPEECH_NIM_URL", "http://localhost:9000/v1/audio/transcriptions")
SPEECH_NIM_MODEL = os.getenv("NVIDIA_SPEECH_NIM_MODEL", "nvidia/parakeet-ctc-1.1b-asr")


class SpeechNIMTranscriptionResult:
    def __init__(
        self,
        transcript: str,
        timestamps: List[Dict[str, Any]],
        confidence: float,
        evidence_id: str,
        model: str,
        processing_time_ms: float,
        is_mock: bool = False,
    ):
        self.transcript = transcript
        self.timestamps = timestamps
        self.confidence = confidence
        self.evidence_id = evidence_id
        self.model = model
        self.processing_time_ms = processing_time_ms
        self.is_mock = is_mock

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transcript": self.transcript,
            "timestamps": self.timestamps,
            "confidence": round(self.confidence, 4),
            "evidence_id": self.evidence_id,
            "model": self.model,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "is_mock": self.is_mock,
        }


class SpeechNIMAdapter:
    """NVIDIA Speech NIM ASR Integration Adapter."""

    def __init__(self, endpoint: Optional[str] = None, model: Optional[str] = None):
        self._endpoint = endpoint or SPEECH_NIM_ENDPOINT
        self._model = model or SPEECH_NIM_MODEL

    @property
    def is_configured(self) -> bool:
        return bool(os.getenv("NVIDIA_SPEECH_NIM_URL") or os.getenv("NVIDIA_API_KEY"))

    async def transcribe_audio_evidence(
        self,
        *,
        evidence_id: str,
        case_id: str,
        audio_path: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
    ) -> SpeechNIMTranscriptionResult:
        start_time = time.time()

        def _emit(event_type: str, data: Dict[str, Any]):
            try:
                from ..events import DomainEvent, publish_event
                publish_event(DomainEvent(event_type=event_type, case_id=case_id, metadata=data))
            except Exception:
                pass

        base_event = {
            "case_id": case_id,
            "evidence_id": evidence_id,
            "model": self._model,
            "timestamp": start_time,
        }
        _emit("speech.transcription.started", base_event)

        # If live NVIDIA NIM server is not reachable, provide realistic deterministic forensics
        live_nim_available = False
        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    health_res = await client.get(f"{self._endpoint.rsplit('/', 2)[0]}/v1/health")
                    if health_res.status_code == 200:
                        live_nim_available = True
            except Exception:
                live_nim_available = False

        if not live_nim_available:
            # Deterministic forensic transcription for testing & demo
            transcript_text = (
                "Call recording Jan 12 at 21:14 UTC. "
                "Speaker 1: Rahul, are you at Sector 4? "
                "Speaker 2: Yes, I am near the building now, wait for my signal."
            )
            timestamp_segments = [
                {"start_sec": 0.0, "end_sec": 2.5, "text": "Call recording Jan 12 at 21:14 UTC."},
                {"start_sec": 2.6, "end_sec": 5.1, "text": "Speaker 1: Rahul, are you at Sector 4?"},
                {"start_sec": 5.2, "end_sec": 8.4, "text": "Speaker 2: Yes, I am near the building now, wait for my signal."},
            ]
            duration_ms = (time.time() - start_time) * 1000
            res = SpeechNIMTranscriptionResult(
                transcript=transcript_text,
                timestamps=timestamp_segments,
                confidence=0.965,
                evidence_id=evidence_id,
                model=self._model,
                processing_time_ms=duration_ms,
                is_mock=True,
            )
            _emit("speech.transcription.completed", {
                **base_event,
                "duration_ms": duration_ms,
                "confidence": 0.965,
                "segment_count": len(timestamp_segments),
            })
            return res

        # Real NVIDIA Speech NIM call
        try:
            files = {"file": ("audio.wav", audio_bytes or b"", "audio/wav")}
            data = {"model": self._model, "response_format": "verbose_json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self._endpoint, files=files, data=data)

            if resp.status_code != 200:
                err = f"NVIDIA Speech NIM error HTTP {resp.status_code}: {resp.text[:120]}"
                _emit("speech.transcription.failed", {**base_event, "error": err})
                raise RuntimeError(err)

            res_data = resp.json()
            duration_ms = (time.time() - start_time) * 1000
            result = SpeechNIMTranscriptionResult(
                transcript=res_data.get("text", ""),
                timestamps=res_data.get("segments", []),
                confidence=float(res_data.get("confidence", 0.95)),
                evidence_id=evidence_id,
                model=self._model,
                processing_time_ms=duration_ms,
                is_mock=False,
            )
            _emit("speech.transcription.completed", {
                **base_event,
                "duration_ms": duration_ms,
                "confidence": result.confidence,
                "segment_count": len(result.timestamps),
            })
            return result

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            _emit("speech.transcription.failed", {**base_event, "error": str(exc)})
            raise


speech_nim = SpeechNIMAdapter()
