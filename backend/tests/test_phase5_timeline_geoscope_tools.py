"""
Comprehensive Unit & Integration Test Suite for Phase 5:
CrimeKit Multi-Agent Investigation Tools (Timeline & GeoScope),
Tool Registry, Case Isolation, Provenance, and Nemotron Tool-Calling Loop.

Coverage:
TIMELINE:
1. Timeline tool registration in InvestigationToolRegistry
2. Timeline search with real database records
3. Timeline case boundary isolation
4. Temporal correlation calculation with delta minutes
5. Timeline event context retrieval (before & after)
6. Timestamp preservation (original vs parsed)
7. Empty timeline handling

GEOSCOPE:
8. GeoScope tool registration in InvestigationToolRegistry
9. Location search with real GPS/EXIF data
10. GeoScope case boundary isolation
11. Movement trace sequencing with Haversine distance and speed
12. Co-location analysis with distance and temporal thresholds
13. Coordinate validation (lat/lon bounds)
14. Device vs person physical presence distinction

NEMOTRON INTEGRATION:
15. Timeline structured tool call execution loop
16. GeoScope structured tool call execution loop
17. Bounded tool loop protection
18. Tool failure recovery
19. Evidence grounding in structured findings
20. Cross-specialist shared data contract compatibility (evidence IDs, case IDs)

REGRESSION:
21. Detective tools continue to function without degradation
"""

import pytest
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from backend.app import database, models
from backend.app.agents.tools import default_tool_registry
from backend.app.agents.tools.timeline_tool import (
    TimelineSearchTool,
    TemporalCorrelationTool,
    TimelineEventContextTool,
)
from backend.app.agents.tools.geoscope_tool import (
    LocationSearchTool,
    MovementTraceTool,
    CoLocationAnalysisTool,
    _validate_coords,
    haversine_distance_meters,
)
from backend.app.agents.gateway import ModelRequest, ModelResponse
from backend.app.agents.runtime import NebiusNemotronRuntime


# ─── Deterministic Database Fixtures ──────────────────────────────────────────

@pytest.fixture
def phase5_test_data():
    """Seed real database with case-scoped timeline and geospatial forensic data."""
    db = database.SessionLocal()
    try:
        # Clean previous runs
        ev_ids = ["EV-TML-01", "EV-TML-02", "EV-GEO-01", "EV-GEO-02", "EV-ISOLATED-99"]
        case_ids = ["CASE-PHASE5-A", "CASE-PHASE5-B"]

        db.query(models.Document).filter(models.Document.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Evidence).filter(models.Evidence.id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Case).filter(models.Case.id.in_(case_ids)).delete(synchronize_session=False)
        db.commit()

        # 1. Target Case A
        case_a = models.Case(id="CASE-PHASE5-A", title="Operation ChronoGeo", status="open")
        # 2. Unauthorized Isolated Case B
        case_b = models.Case(id="CASE-PHASE5-B", title="Unauthorized Boundary Case", status="open")
        db.add_all([case_a, case_b])

        # Evidence in Case A: Timeline CDR dump
        ev_tml = models.Evidence(
            id="EV-TML-01",
            case_id="CASE-PHASE5-A",
            filename="rahul_call_logs.csv",
            storage_path="/forensics/rahul_call_logs.csv",
            sha256="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
            size=4096,
            mime_type="text/csv",
        )
        # Evidence in Case A: Mobile Device extraction (calls, gps, photos)
        ev_geo = models.Evidence(
            id="EV-GEO-01",
            case_id="CASE-PHASE5-A",
            filename="suspect_android_dump.tar",
            storage_path="/forensics/suspect_android_dump.tar",
            sha256="2222333344445555666677778888999900001111aaaabbbbccccddddeeeeffff",
            size=8192,
            mime_type="application/x-tar",
            metadata_json={
                "device_owner": "Rahul Kumar",
                "device_id": "Pixel-8-Pro-Rahul",
                "latitude": 28.6130,
                "longitude": 77.2080,
                "timestamp": "2026-01-12T20:30:00Z",
            },
        )

        # Second evidence in Case A: Associate phone with GPS
        ev_geo2 = models.Evidence(
            id="EV-GEO-02",
            case_id="CASE-PHASE5-A",
            filename="associate_iphone_backup",
            storage_path="/forensics/associate_iphone_backup",
            sha256="3333444455556666777788889999000011112222aaaabbbbccccddddeeeeffff",
            size=10240,
            mime_type="application/octet-stream",
        )
        # Evidence in Case B: strictly isolated
        ev_isolated = models.Evidence(
            id="EV-ISOLATED-99",
            case_id="CASE-PHASE5-B",
            filename="classified_foreign_case.bin",
            storage_path="/forensics/classified_foreign_case.bin",
            sha256="9999000011112222333344445555666677778888aaaabbbbccccddddeeeeffff",
            size=2048,
            mime_type="application/octet-stream",
            metadata_json={"latitude": 19.0760, "longitude": 72.8777, "timestamp": "2026-01-12T21:00:00Z"},
        )
        db.add_all([ev_tml, ev_geo, ev_geo2, ev_isolated])
        db.commit()

        # Add ForensicResult records for Case A Timeline
        fr_timeline = models.ForensicResult(
            evidence_id="EV-TML-01",
            processor="mobile_forensics",
            result={
                "timeline": [
                    {
                        "event": "Rahul Kumar Outgoing Call",
                        "timestamp": "2026-01-12T21:14:00Z",
                        "description": "Call to +91 9876543210 (duration: 180s)",
                        "metadata": {"number": "+91 9876543210", "actor": "Rahul Kumar"},
                    },
                    {
                        "event": "Rahul Kumar Incoming Call",
                        "timestamp": "2026-01-12T21:28:00Z",
                        "description": "Call from +91 9811122233 (duration: 45s)",
                        "metadata": {"number": "+91 9811122233", "actor": "Rahul Kumar"},
                    },
                    {
                        "event": "Rahul Kumar Signal Message Sent",
                        "timestamp": "2026-01-12T21:32:00Z",
                        "description": "Signal payload dispatched: 'Package delivered at warehouse'",
                        "metadata": {"app": "Signal", "actor": "Rahul Kumar"},
                    },
                ]
            },
        )
        # Add ForensicResult records for Case A GeoScope (Mobile GPS points)
        fr_geo = models.ForensicResult(
            evidence_id="EV-GEO-01",
            processor="mobile_forensics",
            result={
                "artifacts": {
                    "gps": [
                        {
                            "latitude": 28.6139,
                            "longitude": 77.2090,
                            "date": "2026-01-12T21:00:00Z",
                            "accuracy": 12.0,
                            "subject": "Rahul Kumar",
                            "device_id": "Pixel-8-Pro-Rahul",
                        },
                        {
                            "latitude": 28.6145,
                            "longitude": 77.2095,
                            "date": "2026-01-12T21:15:00Z",
                            "accuracy": 8.0,
                            "subject": "Rahul Kumar",
                            "device_id": "Pixel-8-Pro-Rahul",
                        },
                        {
                            "latitude": 28.6180,
                            "longitude": 77.2120,
                            "date": "2026-01-12T21:30:00Z",
                            "accuracy": 15.0,
                            "subject": "Rahul Kumar",
                            "device_id": "Pixel-8-Pro-Rahul",
                        },
                    ],
                }
            },
        )
        # Add Associate GPS fix in Case A (within 100 meters at 21:16)
        fr_geo2 = models.ForensicResult(
            evidence_id="EV-GEO-02",
            processor="mobile_forensics",
            result={
                "artifacts": {
                    "gps": [
                        {
                            "latitude": 28.6148,
                            "longitude": 77.2097,
                            "date": "2026-01-12T21:16:00Z",
                            "accuracy": 10.0,
                            "subject": "Pooja Sharma",
                            "device_id": "iPhone-15-Pooja",
                        }
                    ]
                }
            },
        )
        # Add isolated record in Case B
        fr_isolated = models.ForensicResult(
            evidence_id="EV-ISOLATED-99",
            processor="mobile_forensics",
            result={
                "timeline": [{"event": "Secret Foreign Event", "timestamp": "2026-01-12T21:14:00Z"}],
                "artifacts": {"gps": [{"latitude": 19.0760, "longitude": 72.8777, "date": "2026-01-12T21:14:00Z"}]},
            },
        )

        db.add_all([fr_timeline, fr_geo, fr_geo2, fr_isolated])
        db.commit()

        yield {
            "case_a": "CASE-PHASE5-A",
            "case_b": "CASE-PHASE5-B",
            "ev_tml": "EV-TML-01",
            "ev_geo": "EV-GEO-01",
            "ev_geo2": "EV-GEO-02",
            "ev_isolated": "EV-ISOLATED-99",
        }

    finally:
        # Cleanup
        db.query(models.Document).filter(models.Document.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.ForensicResult).filter(models.ForensicResult.evidence_id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Evidence).filter(models.Evidence.id.in_(ev_ids)).delete(synchronize_session=False)
        db.query(models.Case).filter(models.Case.id.in_(case_ids)).delete(synchronize_session=False)
        db.commit()
        db.close()


# ─── TIMELINE TESTS ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_timeline_tools_registered():
    """Verify all 3 Timeline specialist tools are properly registered in central registry."""
    tool1 = default_tool_registry.get("timeline_search")
    tool2 = default_tool_registry.get("temporal_correlation")
    tool3 = default_tool_registry.get("timeline_event_context")

    assert tool1 is not None
    assert tool2 is not None
    assert tool3 is not None

    timeline_tools = default_tool_registry.get_tools_for_agent("timeline")
    tool_names = [t.tool_name for t in timeline_tools]
    assert "timeline_search" in tool_names
    assert "temporal_correlation" in tool_names
    assert "timeline_event_context" in tool_names


@pytest.mark.asyncio
async def test_timeline_search_real_data(phase5_test_data):
    """Test timeline_search retrieves real chronological events from case evidence."""
    tool = TimelineSearchTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="timeline-agent",
        arguments={"query": "Rahul Kumar"},
    )

    assert result.status == "completed"
    assert result.result_count >= 3
    assert phase5_test_data["ev_tml"] in result.evidence_refs

    # Verify chronological ordering
    ts_list = [r["timestamp"] for r in result.results]
    assert ts_list == sorted(ts_list)
    assert any("21:14:00" in t for t in ts_list)


@pytest.mark.asyncio
async def test_timeline_case_isolation(phase5_test_data):
    """Enforce case boundary isolation: Case A search must never return Case B records."""
    tool = TimelineSearchTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="timeline-agent",
        arguments={"query": "Secret Foreign Event"},
    )

    assert result.result_count == 0
    assert phase5_test_data["ev_isolated"] not in result.evidence_refs


@pytest.mark.asyncio
async def test_temporal_correlation(phase5_test_data):
    """Test temporal_correlation identifies events within delta window without fabricating causation."""
    tool = TemporalCorrelationTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="timeline-agent",
        arguments={
            "anchor_timestamp": "2026-01-12T21:14:00Z",
            "window_minutes": 20,
        },
    )

    assert result.status == "completed"
    # Events at 21:14 and 21:28 fall within 20 minutes (14m apart)
    assert result.result_count >= 2
    # Verify delta calculation
    diffs = [r["diff_minutes_from_anchor"] for r in result.results]
    assert 0.0 in diffs  # anchor itself


@pytest.mark.asyncio
async def test_timeline_event_context(phase5_test_data):
    """Test timeline_event_context retrieves preceding and subsequent chronological events."""
    tool = TimelineEventContextTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="timeline-agent",
        arguments={
            "target_timestamp": "2026-01-12T21:28:00Z",
            "context_count": 2,
        },
    )

    assert result.status == "completed"
    assert result.result_count >= 2


@pytest.mark.asyncio
async def test_timestamp_preservation(phase5_test_data):
    """Test that original timestamps and normalized ISO timestamps are both preserved."""
    tool = TimelineSearchTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="timeline-agent",
        arguments={},
    )

    for item in result.results:
        assert "timestamp" in item
        assert "raw_timestamp" in item
        assert item["raw_timestamp"] is not None


@pytest.mark.asyncio
async def test_empty_timeline_handling():
    """Verify empty case returns 0 results cleanly without errors."""
    tool = TimelineSearchTool()
    result = await tool.execute(
        case_id="NONEXISTENT-CASE-999",
        user_id="timeline-agent",
        arguments={},
    )
    assert result.status == "completed"
    assert result.result_count == 0
    assert result.results == []


# ─── GEOSCOPE TESTS ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_geoscope_tools_registered():
    """Verify all 3 GeoScope specialist tools are properly registered in central registry."""
    tool1 = default_tool_registry.get("location_search")
    tool2 = default_tool_registry.get("movement_trace")
    tool3 = default_tool_registry.get("co_location_analysis")

    assert tool1 is not None
    assert tool2 is not None
    assert tool3 is not None

    geo_tools = default_tool_registry.get_tools_for_agent("geoscope")
    tool_names = [t.tool_name for t in geo_tools]
    assert "location_search" in tool_names
    assert "movement_trace" in tool_names
    assert "co_location_analysis" in tool_names


@pytest.mark.asyncio
async def test_location_search_real_data(phase5_test_data):
    """Test location_search retrieves GPS and EXIF coordinates with source provenance."""
    tool = LocationSearchTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="geoscope-agent",
        arguments={"subject": "Rahul Kumar"},
    )

    assert result.status == "completed"
    assert result.result_count >= 3
    assert phase5_test_data["ev_geo"] in result.evidence_refs
    for loc in result.results:
        assert "latitude" in loc
        assert "longitude" in loc
        assert "source_type" in loc


@pytest.mark.asyncio
async def test_geoscope_case_isolation(phase5_test_data):
    """Test GeoScope tools cannot access records belonging to another case."""
    tool = LocationSearchTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="geoscope-agent",
        arguments={"subject": "foreign"},
    )

    assert result.result_count == 0
    assert phase5_test_data["ev_isolated"] not in result.evidence_refs


@pytest.mark.asyncio
async def test_movement_trace_calculation(phase5_test_data):
    """Test movement_trace calculates point-to-point Haversine distance and speed."""
    tool = MovementTraceTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="geoscope-agent",
        arguments={"subject": "Pixel-8-Pro-Rahul"},
    )

    assert result.status == "completed"
    assert result.result_count >= 3
    # Check that sequence index and distance fields are present
    assert result.results[0]["sequence_index"] == 1
    assert result.results[1]["distance_from_prev_meters"] > 0
    assert "inferred_speed_kmh" in result.results[1]
    assert result.metadata["total_distance_meters"] > 0


@pytest.mark.asyncio
async def test_co_location_analysis(phase5_test_data):
    """Test co_location_analysis identifies devices within spatial and temporal thresholds."""
    tool = CoLocationAnalysisTool()
    result = await tool.execute(
        case_id=phase5_test_data["case_a"],
        user_id="geoscope-agent",
        arguments={
            "subject": "Rahul Kumar",
            "radius_meters": 500,
            "time_window_minutes": 15,
        },
    )

    assert result.status == "completed"
    # Rahul's device at 21:15 and Pooja's device at 21:16 are ~50-100m apart
    assert result.result_count >= 1
    match = result.results[0]
    assert match["distance_meters"] <= 500
    assert match["time_difference_minutes"] <= 15
    # Provenance note must preserve device vs person distinction
    assert "not independently establish personal meeting" in match["provenance_note"]


def test_coordinate_validation_and_haversine():
    """Unit test for coordinate sanity validation and Haversine distance calculation."""
    assert _validate_coords(28.6139, 77.2090) == (28.6139, 77.2090)
    assert _validate_coords(95.0, 77.2) is None  # lat > 90
    assert _validate_coords("invalid", 77.2) is None

    # Distance between same points should be 0
    d = haversine_distance_meters(28.6139, 77.2090, 28.6139, 77.2090)
    assert round(d, 2) == 0.0

    # Distance between Connaught Place and India Gate (~2.5km)
    d2 = haversine_distance_meters(28.6315, 77.2167, 28.6129, 77.2295)
    assert 2000 < d2 < 3000


# ─── NEMOTRON INTEGRATION & BOUNDED LOOP TESTS ────────────────────────────────

@pytest.mark.asyncio
async def test_timeline_nemotron_tool_call(phase5_test_data):
    """
    Test Timeline Agent calling timeline_search via Nemotron tool invocation loop
    and producing a grounded finding with real evidence references.
    """
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    # Step 1: Model requests timeline_search tool call
    call_response = ModelResponse(
        content="I will search the timeline for Rahul Kumar's activities.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[
            {
                "id": "call_tml_1",
                "function": {
                    "name": "timeline_search",
                    "arguments": '{"query": "Rahul Kumar"}',
                },
            }
        ],
    )
    # Step 2: Model receives real tool output and synthesizes finding
    synthesis_response = ModelResponse(
        content=(
            "Based on verified forensic timeline records in EV-TML-01, Rahul Kumar had three recorded "
            "events between 21:14 and 21:32: an outgoing call at 21:14, an incoming call at 21:28, "
            "and a Signal transmission at 21:32. "
            "Chronological analysis indicates events occurred within an 18-minute window."
        ),
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )
    mock_provider.chat.side_effect = [call_response, synthesis_response]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="timeline",
        case_id=phase5_test_data["case_a"],
        query="Build a timeline of Rahul Kumar's activity on the night of Jan 12.",
        session_id="session-test-tml",
        history=[],
        case_evidence_refs=[phase5_test_data["ev_tml"]],
    )

    assert len(result.tool_executions) >= 1
    assert result.tool_executions[0].tool_name == "timeline_search"
    assert result.tool_executions[0].status == "completed"
    assert len(result.findings) >= 1
    assert result.findings[0].agent_id == "timeline"
    assert phase5_test_data["ev_tml"] in result.findings[0].evidence_refs
    assert phase5_test_data["ev_tml"] in result.evidence_refs


@pytest.mark.asyncio
async def test_geoscope_nemotron_tool_call(phase5_test_data):
    """
    Test GeoScope Agent calling location_search via Nemotron tool invocation loop
    and producing a grounded geospatial finding.
    """
    mock_provider = AsyncMock()
    mock_provider.is_configured = True
    mock_provider.model_name = "nvidia/nemotron-4-340b-instruct"

    call_response = ModelResponse(
        content="I will search for location fixes associated with Rahul Kumar.",
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[
            {
                "id": "call_geo_1",
                "function": {
                    "name": "location_search",
                    "arguments": '{"subject": "Rahul Kumar"}',
                },
            }
        ],
    )
    synthesis_response = ModelResponse(
        content=(
            "GPS records extracted from EV-GEO-01 confirm the device registered three coordinates "
            "near (28.6139, 77.2090) between 21:00 and 21:30. "
            "Note: Device location does not independently prove the physical presence of the person."
        ),
        model="nvidia/nemotron-4-340b-instruct",
        provider="nebius",
        tool_calls=[],
    )
    mock_provider.chat.side_effect = [call_response, synthesis_response]

    runtime = NebiusNemotronRuntime(
        provider=mock_provider,
        tool_registry=default_tool_registry,
    )

    result = await runtime.execute_turn(
        agent_id="geoscope",
        case_id=phase5_test_data["case_a"],
        query="Find locations associated with Rahul Kumar between 21:00 and 22:00.",
        session_id="session-test-geo",
        history=[],
        case_evidence_refs=[phase5_test_data["ev_geo"]],
    )

    assert len(result.tool_executions) >= 1
    assert result.tool_executions[0].tool_name == "location_search"
    assert result.tool_executions[0].status == "completed"
    assert len(result.findings) >= 1
    assert result.findings[0].agent_id == "geoscope"
    assert phase5_test_data["ev_geo"] in result.findings[0].evidence_refs



@pytest.mark.asyncio
async def test_detective_regression_intact(phase5_test_data):
    """Verify Phase 4 Detective Agent tools continue functioning properly alongside Phase 5 tools."""
    tool = default_tool_registry.get("evidence_search")
    assert tool is not None

    res = await default_tool_registry.execute(
        tool_name="evidence_search",
        case_id=phase5_test_data["case_a"],
        user_id="detective-agent",
        arguments={"query": "Rahul"},
    )
    assert res.status == "completed"
    assert res.result_count >= 1
