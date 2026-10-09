"""
Timeline Investigation Tools for CrimeKit.

Defines:
1. TimelineSearchTool: Searches chronological timeline events from ForensicResult and Document extractions.
2. TemporalCorrelationTool: Identifies events clustered within a temporal delta window around an anchor event.
3. TimelineEventContextTool: Fetches surrounding chronological context (before/after) for an event or timestamp.

All executions are case-isolated and preserve original timestamps and forensic provenance.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dateutil import parser as dt_parser

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models
from ...kg import extract_timeline

logger = logging.getLogger(__name__)


def _parse_iso_datetime(dt_str: Any) -> Optional[datetime]:
    """Robustly parse timestamps into timezone-aware UTC datetime."""
    if not dt_str:
        return None
    if isinstance(dt_str, datetime):
        if dt_str.tzinfo is None:
            return dt_str.replace(tzinfo=timezone.utc)
        return dt_str.astimezone(timezone.utc)
    try:
        dt = dt_parser.parse(str(dt_str))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _format_iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _collect_case_timeline_events(
    db: Session,
    case_id: str,
    query_text: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Query real CrimeKit timeline records belonging strictly to case_id.
    Queries both ForensicResult records (with timeline payload) and Document text extractions.
    """
    case_evs = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
    if not case_evs:
        return []

    evidence_map = {e.id: e for e in case_evs}
    evidence_ids = list(evidence_map.keys())

    events: List[Dict[str, Any]] = []

    # 1. ForensicResult records
    fr_query = db.query(models.ForensicResult).filter(
        models.ForensicResult.evidence_id.in_(evidence_ids)
    )
    for fr in fr_query.all():
        res_data = fr.result or {}
        if isinstance(res_data, dict) and "timeline" in res_data:
            t_data = res_data["timeline"]
            if isinstance(t_data, list):
                for idx, item in enumerate(t_data):
                    raw_ts = item.get("timestamp") or fr.created_at
                    parsed_ts = _parse_iso_datetime(raw_ts)
                    evt_title = item.get("event") or item.get("title") or "Forensic Artifact"
                    evt_desc = item.get("description") or f"Extracted via {fr.processor}"

                    ev_id = fr.evidence_id
                    parent_ev = evidence_map.get(ev_id)

                    events.append({
                        "event_id": f"FR-{fr.id[:8]}-{idx}",
                        "timestamp": _format_iso(parsed_ts),
                        "raw_timestamp": str(raw_ts),
                        "parsed_dt": parsed_ts,
                        "title": evt_title,
                        "description": evt_desc,
                        "source_type": fr.processor or "forensic_engine",
                        "evidence_id": ev_id,
                        "filename": parent_ev.filename if parent_ev else None,
                        "metadata": item.get("metadata") or {},
                    })

    # 2. Document text timeline extraction if fewer than 5 events or to enrich text evidence
    doc_query = db.query(models.Document).filter(
        models.Document.evidence_id.in_(evidence_ids)
    )
    for doc in doc_query.all():
        if doc.text:
            extracted = extract_timeline(doc.text)
            for idx, item in enumerate(extracted):
                raw_date = item.get("date")
                parsed_ts = _parse_iso_datetime(raw_date) or _parse_iso_datetime(doc.created_at)
                ev_id = doc.evidence_id
                parent_ev = evidence_map.get(ev_id) if ev_id else None

                events.append({
                    "event_id": f"DOC-{doc.id[:8]}-{idx}",
                    "timestamp": _format_iso(parsed_ts),
                    "raw_timestamp": str(raw_date),
                    "parsed_dt": parsed_ts,
                    "title": "Text Date Reference",
                    "description": item.get("summary", ""),
                    "source_type": "document_ocr",
                    "evidence_id": ev_id,
                    "filename": parent_ev.filename if parent_ev else None,
                    "metadata": {"document_id": doc.id},
                })

    # Filter by time window if specified
    filtered = []
    q_lower = query_text.lower() if query_text else ""
    for ev in events:
        dt = ev["parsed_dt"]
        if start_time and dt and dt < start_time:
            continue
        if end_time and dt and dt > end_time:
            continue
        if q_lower:
            haystack = f"{ev['title']} {ev['description']} {ev.get('filename') or ''}".lower()
            if q_lower not in haystack:
                continue
        filtered.append(ev)

    # Sort chronologically by timestamp (None timestamps placed last)
    filtered.sort(
        key=lambda x: x["parsed_dt"] or datetime.max.replace(tzinfo=timezone.utc),
    )

    # Clean internal datetime object before serializing
    out: List[Dict[str, Any]] = []
    for ev in filtered[:limit]:
        c = dict(ev)
        c.pop("parsed_dt", None)
        out.append(c)

    return out


class TimelineSearchTool(BaseInvestigationTool):
    """
    Search and retrieve chronologically sorted timeline events for an authorized case.
    """

    @property
    def tool_name(self) -> str:
        return "timeline_search"

    @property
    def description(self) -> str:
        return (
            "Retrieve chronologically ordered timeline events for the active case. "
            "Filter by keyword, subject name, or start/end timestamp ranges. "
            "Returns original forensic timestamps and evidence provenance."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Optional keyword, subject, or phrase to filter timeline events.",
                },
                "start_time": {
                    "type": "string",
                    "description": "Optional start timestamp in ISO format (e.g. '2024-01-12T00:00:00Z' or '2024-01-12').",
                },
                "end_time": {
                    "type": "string",
                    "description": "Optional end timestamp in ISO format (e.g. '2024-01-12T23:59:59Z').",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of events to return (1-50, default 20).",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
        }

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        query_text = arguments.get("query")
        limit = min(max(int(arguments.get("limit", 20)), 1), 50)
        start_ts = _parse_iso_datetime(arguments.get("start_time"))
        end_ts = _parse_iso_datetime(arguments.get("end_time"))

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            events = _collect_case_timeline_events(
                db=db,
                case_id=case_id,
                query_text=query_text,
                start_time=start_ts,
                end_time=end_ts,
                limit=limit,
            )

            evidence_refs = list({e["evidence_id"] for e in events if e.get("evidence_id")})
            duration_ms = (time.time() - start_time_exec) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(events),
                results=events,
                evidence_refs=evidence_refs,
                duration_ms=round(duration_ms, 2),
                metadata={
                    "case_id": case_id,
                    "filter_query": query_text,
                    "start_time": _format_iso(start_ts),
                    "end_time": _format_iso(end_ts),
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("TimelineSearchTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Timeline search failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()


class TemporalCorrelationTool(BaseInvestigationTool):
    """
    Finds events occurring within a specified temporal delta window around an anchor event or timestamp.
    """

    @property
    def tool_name(self) -> str:
        return "temporal_correlation"

    @property
    def description(self) -> str:
        return (
            "Analyze temporal proximity between forensic events in the case. "
            "Given an anchor event ID or anchor timestamp, identifies other events "
            "occurring within +/- window_minutes. Note: temporal correlation does not imply causation."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "anchor_event_id": {
                    "type": "string",
                    "description": "Optional event ID (e.g. 'FR-12345678-0') to center correlation window around.",
                },
                "anchor_timestamp": {
                    "type": "string",
                    "description": "Optional ISO timestamp string if anchor_event_id is not known.",
                },
                "window_minutes": {
                    "type": "integer",
                    "description": "Symmetric temporal search window in minutes (1-720, default 30).",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 720,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum correlated events to return (1-50, default 20).",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
        }

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        anchor_id = arguments.get("anchor_event_id")
        anchor_ts_raw = arguments.get("anchor_timestamp")
        window_minutes = min(max(int(arguments.get("window_minutes", 30)), 1), 720)
        limit = min(max(int(arguments.get("limit", 20)), 1), 50)

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            all_events = _collect_case_timeline_events(
                db=db,
                case_id=case_id,
                limit=500,
            )

            # Determine anchor datetime
            anchor_event = None
            anchor_dt: Optional[datetime] = None

            if anchor_id:
                for ev in all_events:
                    if ev["event_id"] == anchor_id:
                        anchor_event = ev
                        anchor_dt = _parse_iso_datetime(ev.get("timestamp"))
                        break

            if not anchor_dt and anchor_ts_raw:
                anchor_dt = _parse_iso_datetime(anchor_ts_raw)

            if not anchor_dt:
                return ToolResult(
                    tool_name=self.tool_name,
                    execution_id="",
                    status="failed",
                    error_message=(
                        "Unable to establish anchor timestamp. Please specify a valid anchor_event_id "
                        "or ISO anchor_timestamp."
                    ),
                    duration_ms=round((time.time() - start_time_exec) * 1000, 2),
                )

            delta = timedelta(minutes=window_minutes)
            min_bound = anchor_dt - delta
            max_bound = anchor_dt + delta

            correlated: List[Dict[str, Any]] = []
            for ev in all_events:
                ev_dt = _parse_iso_datetime(ev.get("timestamp"))
                if not ev_dt:
                    continue
                if min_bound <= ev_dt <= max_bound:
                    diff_seconds = (ev_dt - anchor_dt).total_seconds()
                    diff_minutes = round(diff_seconds / 60.0, 1)
                    c_record = dict(ev)
                    c_record["diff_minutes_from_anchor"] = diff_minutes
                    c_record["is_anchor"] = bool(anchor_id and ev["event_id"] == anchor_id)
                    correlated.append(c_record)

            correlated.sort(key=lambda x: abs(x.get("diff_minutes_from_anchor", 0)))
            trimmed = correlated[:limit]

            evidence_refs = list({e["evidence_id"] for e in trimmed if e.get("evidence_id")})
            duration_ms = (time.time() - start_time_exec) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(trimmed),
                results=trimmed,
                evidence_refs=evidence_refs,
                duration_ms=round(duration_ms, 2),
                metadata={
                    "anchor_timestamp": _format_iso(anchor_dt),
                    "anchor_event_id": anchor_id,
                    "window_minutes": window_minutes,
                    "total_in_window": len(correlated),
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("TemporalCorrelationTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Temporal correlation failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()


class TimelineEventContextTool(BaseInvestigationTool):
    """
    Retrieve surrounding chronological events (preceding and subsequent) for an event or timestamp.
    """

    @property
    def tool_name(self) -> str:
        return "timeline_event_context"

    @property
    def description(self) -> str:
        return (
            "Retrieve immediate surrounding chronological events (N before, N after) "
            "around a target event ID or timestamp in the case timeline."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_event_id": {
                    "type": "string",
                    "description": "Event ID to retrieve surrounding context around.",
                },
                "target_timestamp": {
                    "type": "string",
                    "description": "ISO timestamp to retrieve surrounding context around if ID not known.",
                },
                "context_count": {
                    "type": "integer",
                    "description": "Number of preceding and subsequent events to retrieve (1-20, default 5).",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                },
            },
        }

    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        target_id = arguments.get("target_event_id")
        target_ts_raw = arguments.get("target_timestamp")
        count = min(max(int(arguments.get("context_count", 5)), 1), 20)

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            all_events = _collect_case_timeline_events(
                db=db,
                case_id=case_id,
                limit=500,
            )

            if not all_events:
                return ToolResult(
                    tool_name=self.tool_name,
                    execution_id="",
                    status="completed",
                    result_count=0,
                    results=[],
                    evidence_refs=[],
                    duration_ms=round((time.time() - start_time_exec) * 1000, 2),
                )

            # Locate target index
            target_idx = -1
            if target_id:
                for idx, ev in enumerate(all_events):
                    if ev["event_id"] == target_id:
                        target_idx = idx
                        break

            if target_idx == -1 and target_ts_raw:
                t_dt = _parse_iso_datetime(target_ts_raw)
                if t_dt:
                    # Find closest event
                    closest_idx = 0
                    closest_diff = float("inf")
                    for idx, ev in enumerate(all_events):
                        ev_dt = _parse_iso_datetime(ev.get("timestamp"))
                        if ev_dt:
                            diff = abs((ev_dt - t_dt).total_seconds())
                            if diff < closest_diff:
                                closest_diff = diff
                                closest_idx = idx
                    target_idx = closest_idx

            if target_idx == -1:
                return ToolResult(
                    tool_name=self.tool_name,
                    execution_id="",
                    status="failed",
                    error_message="Target event ID or timestamp could not be resolved in the timeline.",
                    duration_ms=round((time.time() - start_time_exec) * 1000, 2),
                )

            start_idx = max(0, target_idx - count)
            end_idx = min(len(all_events), target_idx + count + 1)
            sliced = all_events[start_idx:end_idx]

            evidence_refs = list({e["evidence_id"] for e in sliced if e.get("evidence_id")})
            duration_ms = (time.time() - start_time_exec) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(sliced),
                results=sliced,
                evidence_refs=evidence_refs,
                duration_ms=round(duration_ms, 2),
                metadata={
                    "target_index": target_idx,
                    "target_event_id": target_id,
                    "window_range": f"{start_idx}..{end_idx}",
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("TimelineEventContextTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Timeline context lookup failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()
