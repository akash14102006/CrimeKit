"""
GeoScope Geospatial Investigation Tools for CrimeKit.

Defines:
1. LocationSearchTool: Searches GPS/EXIF and cell coordinates from mobile/photo artifacts and metadata.
2. MovementTraceTool: Sequences chronological waypoints for a device or subject with speed/distance calculation.
3. CoLocationAnalysisTool: Identifies co-present devices/subjects within spatial (meters) and temporal (minutes) windows.

All coordinates, timestamps, and evidence provenance are preserved from real CrimeKit forensic data.
Device location is strictly distinguished from personal physical presence.
"""

import math
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dateutil import parser as dt_parser

from sqlalchemy.orm import Session
from .base import BaseInvestigationTool, ToolResult
from ... import database, models

logger = logging.getLogger(__name__)


def _parse_iso_datetime(dt_str: Any) -> Optional[datetime]:
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


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two coordinates via Haversine formula."""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def _validate_coords(lat: Any, lon: Any) -> Optional[tuple[float, float]]:
    """Validate latitude (-90 to 90) and longitude (-180 to 180)."""
    try:
        f_lat = float(lat)
        f_lon = float(lon)
        if -90.0 <= f_lat <= 90.0 and -180.0 <= f_lon <= 180.0:
            return (f_lat, f_lon)
    except (ValueError, TypeError):
        pass
    return None


def _collect_case_location_records(
    db: Session,
    case_id: str,
    subject_filter: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Extract real location points from Evidence metadata (EXIF/GPS) and ForensicResult records.
    """
    case_evs = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
    if not case_evs:
        return []

    evidence_map = {e.id: e for e in case_evs}
    evidence_ids = list(evidence_map.keys())

    locations: List[Dict[str, Any]] = []

    # 1. Evidence.metadata_json (EXIF GPS data)
    for ev in case_evs:
        meta = ev.metadata_json or {}
        if isinstance(meta, dict):
            exif = meta.get("exif") or {}
            # Look for GPS coordinates directly in metadata
            lat = meta.get("latitude") or meta.get("lat") or exif.get("latitude") or exif.get("GPSLatitude")
            lon = meta.get("longitude") or meta.get("lon") or exif.get("longitude") or exif.get("GPSLongitude")

            coords = _validate_coords(lat, lon)
            if coords:
                f_lat, f_lon = coords
                ts_raw = meta.get("timestamp") or exif.get("DateTimeOriginal") or exif.get("date") or ev.uploaded_at
                parsed_ts = _parse_iso_datetime(ts_raw)
                locations.append({
                    "location_id": f"LOC-EV-{ev.id[:8]}",
                    "latitude": f_lat,
                    "longitude": f_lon,
                    "timestamp": _format_iso(parsed_ts),
                    "parsed_dt": parsed_ts,
                    "source_type": "EXIF_GPS",
                    "accuracy_meters": meta.get("accuracy"),
                    "subject": meta.get("device_owner") or meta.get("subject") or ev.filename,
                    "device_id": meta.get("device_id") or ev.filename,
                    "evidence_id": ev.id,
                    "filename": ev.filename,
                    "is_inferred": False,
                })

    # 2. ForensicResult extractions (mobile_forensics artifacts, image EXIF, etc.)
    fr_query = db.query(models.ForensicResult).filter(
        models.ForensicResult.evidence_id.in_(evidence_ids)
    )
    for fr in fr_query.all():
        res = fr.result or {}
        if not isinstance(res, dict):
            continue

        parent_ev = evidence_map.get(fr.evidence_id)
        ev_fn = parent_ev.filename if parent_ev else "evidence"

        # Check mobile artifacts -> gps
        artifacts = res.get("artifacts") or {}
        gps_list = artifacts.get("gps") or []
        if isinstance(gps_list, list):
            for idx, g in enumerate(gps_list):
                if isinstance(g, dict):
                    coords = _validate_coords(g.get("latitude"), g.get("longitude"))
                    if coords:
                        f_lat, f_lon = coords
                        ts_raw = g.get("date") or g.get("timestamp") or fr.created_at
                        parsed_ts = _parse_iso_datetime(ts_raw)
                        locations.append({
                            "location_id": f"LOC-FR-{fr.id[:8]}-GPS-{idx}",
                            "latitude": f_lat,
                            "longitude": f_lon,
                            "timestamp": _format_iso(parsed_ts),
                            "parsed_dt": parsed_ts,
                            "source_type": "MOBILE_GPS_LOG",
                            "accuracy_meters": g.get("accuracy"),
                            "subject": g.get("subject") or ev_fn,
                            "device_id": g.get("device_id") or ev_fn,
                            "evidence_id": fr.evidence_id,
                            "filename": ev_fn,
                            "is_inferred": False,
                        })

        # Check photo artifacts in mobile forensics (Photos.sqlite)
        photo_list = artifacts.get("photos") or []
        if isinstance(photo_list, list):
            for idx, p in enumerate(photo_list):
                if isinstance(p, dict):
                    coords = _validate_coords(p.get("latitude"), p.get("longitude"))
                    if coords:
                        f_lat, f_lon = coords
                        ts_raw = p.get("date") or fr.created_at
                        parsed_ts = _parse_iso_datetime(ts_raw)
                        locations.append({
                            "location_id": f"LOC-FR-{fr.id[:8]}-PHOTO-{idx}",
                            "latitude": f_lat,
                            "longitude": f_lon,
                            "timestamp": _format_iso(parsed_ts),
                            "parsed_dt": parsed_ts,
                            "source_type": "PHOTO_EXIF",
                            "accuracy_meters": None,
                            "subject": p.get("camera_model") or ev_fn,
                            "device_id": ev_fn,
                            "evidence_id": fr.evidence_id,
                            "filename": p.get("filename") or ev_fn,
                            "is_inferred": False,
                        })

        # Check call locations (calls.db with geocoded_location)
        call_list = artifacts.get("calls") or []
        if isinstance(call_list, list):
            for idx, c in enumerate(call_list):
                if isinstance(c, dict):
                    geo_loc = c.get("location")
                    if isinstance(geo_loc, dict):
                        coords = _validate_coords(geo_loc.get("lat"), geo_loc.get("lng"))
                        if coords:
                            f_lat, f_lon = coords
                            ts_raw = c.get("date") or fr.created_at
                            parsed_ts = _parse_iso_datetime(ts_raw)
                            locations.append({
                                "location_id": f"LOC-FR-{fr.id[:8]}-CALL-{idx}",
                                "latitude": f_lat,
                                "longitude": f_lon,
                                "timestamp": _format_iso(parsed_ts),
                                "parsed_dt": parsed_ts,
                                "source_type": "CELL_GEOCODE",
                                "accuracy_meters": geo_loc.get("radius"),
                                "subject": c.get("number") or ev_fn,
                                "device_id": ev_fn,
                                "evidence_id": fr.evidence_id,
                                "filename": ev_fn,
                                "is_inferred": True,
                            })

    # Filter by time and subject
    filtered = []
    subj_lower = subject_filter.lower() if subject_filter else ""
    for loc in locations:
        dt = loc["parsed_dt"]
        if start_time and dt and dt < start_time:
            continue
        if end_time and dt and dt > end_time:
            continue
        if subj_lower:
            haystack = f"{loc['subject']} {loc['device_id']} {loc['filename']}".lower()
            if subj_lower not in haystack:
                continue
        filtered.append(loc)

    filtered.sort(
        key=lambda x: x["parsed_dt"] or datetime.max.replace(tzinfo=timezone.utc),
    )
    return filtered


class LocationSearchTool(BaseInvestigationTool):
    """
    Search and retrieve location-bearing digital forensic evidence for the authorized case.
    """

    @property
    def tool_name(self) -> str:
        return "location_search"

    @property
    def description(self) -> str:
        return (
            "Search location-bearing forensic records (EXIF, mobile GPS logs, cell tower coordinates, "
            "and photo waypoints) for the active case. "
            "IMPORTANT: Device location records do not independently prove physical presence of a person."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Optional subject name, phone number, device identifier, or filename filter.",
                },
                "start_time": {
                    "type": "string",
                    "description": "Optional start timestamp in ISO format (e.g. '2024-01-12T00:00:00Z').",
                },
                "end_time": {
                    "type": "string",
                    "description": "Optional end timestamp in ISO format (e.g. '2024-01-12T23:59:59Z').",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of location records to return (1-50, default 20).",
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
        subject = arguments.get("subject")
        limit = min(max(int(arguments.get("limit", 20)), 1), 50)
        start_ts = _parse_iso_datetime(arguments.get("start_time"))
        end_ts = _parse_iso_datetime(arguments.get("end_time"))

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            records = _collect_case_location_records(
                db=db,
                case_id=case_id,
                subject_filter=subject,
                start_time=start_ts,
                end_time=end_ts,
            )

            out = []
            for r in records[:limit]:
                item = dict(r)
                item.pop("parsed_dt", None)
                out.append(item)

            evidence_refs = list({e["evidence_id"] for e in out if e.get("evidence_id")})
            duration_ms = (time.time() - start_time_exec) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(out),
                results=out,
                evidence_refs=evidence_refs,
                duration_ms=round(duration_ms, 2),
                metadata={
                    "case_id": case_id,
                    "subject_filter": subject,
                    "start_time": _format_iso(start_ts),
                    "end_time": _format_iso(end_ts),
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("LocationSearchTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Location search failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()


class MovementTraceTool(BaseInvestigationTool):
    """
    Constructs an ordered chronological trajectory/trace from verified location records.
    """

    @property
    def tool_name(self) -> str:
        return "movement_trace"

    @property
    def description(self) -> str:
        return (
            "Construct a chronological sequence of waypoints for a specific device or subject. "
            "Computes point-to-point geodesic distances and elapsed times. "
            "Does not interpolate routes between sparse points without clear labeling."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject, device ID, or filename to trace movement for.",
                },
                "start_time": {
                    "type": "string",
                    "description": "Optional start timestamp in ISO format.",
                },
                "end_time": {
                    "type": "string",
                    "description": "Optional end timestamp in ISO format.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum waypoints in movement sequence (2-100, default 30).",
                    "default": 30,
                    "minimum": 2,
                    "maximum": 100,
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
        subject = arguments.get("subject")
        limit = min(max(int(arguments.get("limit", 30)), 2), 100)
        start_ts = _parse_iso_datetime(arguments.get("start_time"))
        end_ts = _parse_iso_datetime(arguments.get("end_time"))

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            records = _collect_case_location_records(
                db=db,
                case_id=case_id,
                subject_filter=subject,
                start_time=start_ts,
                end_time=end_ts,
            )

            # Sort strictly by timestamp
            dated_records = [r for r in records if r.get("parsed_dt")]
            dated_records.sort(key=lambda x: x["parsed_dt"])
            selected = dated_records[:limit]

            waypoints: List[Dict[str, Any]] = []
            total_distance_meters = 0.0

            for idx, pt in enumerate(selected):
                dist_from_prev = 0.0
                time_diff_sec = 0.0
                speed_kmh = None

                if idx > 0:
                    prev_pt = selected[idx - 1]
                    dist_from_prev = haversine_distance_meters(
                        prev_pt["latitude"], prev_pt["longitude"],
                        pt["latitude"], pt["longitude"],
                    )
                    total_distance_meters += dist_from_prev

                    time_diff_sec = (pt["parsed_dt"] - prev_pt["parsed_dt"]).total_seconds()
                    if time_diff_sec > 0:
                        speed_mps = dist_from_prev / time_diff_sec
                        speed_kmh = round(speed_mps * 3.6, 1)

                wp = dict(pt)
                wp.pop("parsed_dt", None)
                wp["sequence_index"] = idx + 1
                wp["distance_from_prev_meters"] = round(dist_from_prev, 1)
                wp["time_diff_from_prev_seconds"] = round(time_diff_sec, 1)
                wp["inferred_speed_kmh"] = speed_kmh
                waypoints.append(wp)

            evidence_refs = list({w["evidence_id"] for w in waypoints if w.get("evidence_id")})
            duration_ms = (time.time() - start_time_exec) * 1000

            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="completed",
                result_count=len(waypoints),
                results=waypoints,
                evidence_refs=evidence_refs,
                duration_ms=round(duration_ms, 2),
                metadata={
                    "total_waypoints": len(waypoints),
                    "total_distance_meters": round(total_distance_meters, 1),
                    "total_distance_km": round(total_distance_meters / 1000.0, 2),
                    "subject": subject,
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("MovementTraceTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Movement trace failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()


class CoLocationAnalysisTool(BaseInvestigationTool):
    """
    Identifies devices or subjects co-present within spatial (meters) and temporal (minutes) thresholds.
    """

    @property
    def tool_name(self) -> str:
        return "co_location_analysis"

    @property
    def description(self) -> str:
        return (
            "Analyze whether two or more distinct devices were recorded in close spatial proximity "
            "(within radius_meters) during a temporal window (within time_window_minutes). "
            "IMPORTANT: Co-presence of devices is NOT proof that subjects met or had contact."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Anchor subject or device identifier to find co-located devices against.",
                },
                "radius_meters": {
                    "type": "number",
                    "description": "Maximum geographic distance in meters (10-5000, default 500).",
                    "default": 500,
                    "minimum": 10,
                    "maximum": 5000,
                },
                "time_window_minutes": {
                    "type": "integer",
                    "description": "Maximum time difference in minutes (1-240, default 30).",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 240,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum co-location encounters to return (1-50, default 20).",
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
        anchor_subj = str(arguments.get("subject", "")).strip()
        radius_m = min(max(float(arguments.get("radius_meters", 500)), 10.0), 5000.0)
        time_win_min = min(max(int(arguments.get("time_window_minutes", 30)), 1), 240)
        limit = min(max(int(arguments.get("limit", 20)), 1), 50)

        start_time_exec = time.time()
        db: Session = database.SessionLocal()
        try:
            records = _collect_case_location_records(
                db=db,
                case_id=case_id,
            )

            # Partition into anchor records and comparison records
            anchor_records = []
            other_records = []

            for r in records:
                if not r.get("parsed_dt"):
                    continue
                ident = f"{r.get('subject')} {r.get('device_id')} {r.get('filename')}"
                if anchor_subj and anchor_subj.lower() in ident.lower():
                    anchor_records.append(r)
                else:
                    other_records.append(r)

            if not anchor_subj:
                # If no anchor subject provided, pairwise test all distinct devices
                anchor_records = records
                other_records = records

            matches: List[Dict[str, Any]] = []
            seen_pairs = set()

            for a_pt in anchor_records:
                a_dt = a_pt["parsed_dt"]
                for b_pt in other_records:
                    # Ignore identical record or identical subject/device
                    if a_pt["location_id"] == b_pt["location_id"]:
                        continue
                    if a_pt.get("device_id") == b_pt.get("device_id"):
                        continue

                    # Temporal check
                    time_diff_sec = abs((a_dt - b_pt["parsed_dt"]).total_seconds())
                    if time_diff_sec > time_win_min * 60:
                        continue

                    # Spatial check
                    dist_m = haversine_distance_meters(
                        a_pt["latitude"], a_pt["longitude"],
                        b_pt["latitude"], b_pt["longitude"],
                    )
                    if dist_m > radius_m:
                        continue

                    pair_key = tuple(sorted([a_pt["location_id"], b_pt["location_id"]]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    matches.append({
                        "device_a": a_pt.get("device_id") or a_pt.get("subject"),
                        "device_b": b_pt.get("device_id") or b_pt.get("subject"),
                        "location_id_a": a_pt["location_id"],
                        "location_id_b": b_pt["location_id"],
                        "timestamp_a": a_pt["timestamp"],
                        "timestamp_b": b_pt["timestamp"],
                        "time_difference_minutes": round(time_diff_sec / 60.0, 1),
                        "distance_meters": round(dist_m, 1),
                        "coordinates_a": [a_pt["latitude"], a_pt["longitude"]],
                        "coordinates_b": [b_pt["latitude"], b_pt["longitude"]],
                        "evidence_refs": list(filter(None, [a_pt.get("evidence_id"), b_pt.get("evidence_id")])),
                        "provenance_note": (
                            "Spatial/temporal co-presence of devices detected. "
                            "Does not independently establish personal meeting between individuals."
                        ),
                    })

            matches.sort(key=lambda x: (x["distance_meters"], x["time_difference_minutes"]))
            trimmed = matches[:limit]

            evidence_refs = list({ref for m in trimmed for ref in m.get("evidence_refs", [])})
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
                    "anchor_subject": anchor_subj,
                    "radius_meters": radius_m,
                    "time_window_minutes": time_win_min,
                    "matches_found": len(matches),
                },
            )
        except Exception as exc:
            duration_ms = (time.time() - start_time_exec) * 1000
            logger.error("CoLocationAnalysisTool error: %s", exc, exc_info=True)
            return ToolResult(
                tool_name=self.tool_name,
                execution_id="",
                status="failed",
                error_message=f"Co-location analysis failed: {str(exc)[:150]}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            db.close()
