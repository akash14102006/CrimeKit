"""
CrimeKit Investigation Tools Package.

Exposes:
- BaseInvestigationTool
- ToolResult
- ToolDefinition
- ToolCall
- EvidenceSearchTool
- EntitySearchTool
- KnowledgeGraphTool
- InvestigationToolRegistry
- get_tool_registry
"""

from .base import BaseInvestigationTool, ToolResult, ToolDefinition, ToolCall
from .evidence_tool import EvidenceSearchTool
from .entity_tool import EntitySearchTool
from .graph_tool import KnowledgeGraphTool
from .vector_tool import VectorSearchTool
from .timeline_tool import TimelineSearchTool, TemporalCorrelationTool, TimelineEventContextTool
from .geoscope_tool import LocationSearchTool, MovementTraceTool, CoLocationAnalysisTool
from .registry import InvestigationToolRegistry, get_tool_registry, default_tool_registry

# Register default forensic investigation tools into singleton registry
# Detective tools
default_tool_registry.register(EvidenceSearchTool())
default_tool_registry.register(EntitySearchTool())
default_tool_registry.register(KnowledgeGraphTool())
default_tool_registry.register(VectorSearchTool())

# Timeline tools
default_tool_registry.register(TimelineSearchTool())
default_tool_registry.register(TemporalCorrelationTool())
default_tool_registry.register(TimelineEventContextTool())

# GeoScope tools
default_tool_registry.register(LocationSearchTool())
default_tool_registry.register(MovementTraceTool())
default_tool_registry.register(CoLocationAnalysisTool())

# Tavily Web Research tool
from ...tools.tavily_tool import TavilyWebResearchTool
default_tool_registry.register(TavilyWebResearchTool())

__all__ = [
    "BaseInvestigationTool",
    "ToolResult",
    "ToolDefinition",
    "ToolCall",
    "EvidenceSearchTool",
    "EntitySearchTool",
    "KnowledgeGraphTool",
    "TimelineSearchTool",
    "TemporalCorrelationTool",
    "TimelineEventContextTool",
    "LocationSearchTool",
    "MovementTraceTool",
    "CoLocationAnalysisTool",
    "TavilyWebResearchTool",
    "InvestigationToolRegistry",
    "get_tool_registry",
    "default_tool_registry",
]

