"""
Controlled Investigation Tool Abstractions & Contracts for CrimeKit.

Defines:
- BaseInvestigationTool: Abstract base class for all CrimeKit investigation tools.
- ToolResult: Structured output of tool execution containing metadata, evidence IDs, and results.
- ToolDefinition: Specification provided to LLM/Nemotron for tool selection.
- ToolCall: Structured tool call requested by LLM.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time
import uuid


class ToolResult(BaseModel):
    tool_name: str
    execution_id: str
    status: str = Field(default="completed", description="completed | failed | permission_denied")
    result_count: int = 0
    results: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema of parameters


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class BaseInvestigationTool(ABC):
    """
    Abstract contract for an authorized, case-scoped CrimeKit investigation tool.
    Never exposes raw SQL, Cypher, filesystem paths, or arbitrary HTTP execution.
    """

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Unique identifier of the tool (e.g. 'evidence_search')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human & LLM readable explanation of tool capabilities."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema defining accepted input parameters."""
        pass

    def get_tool_definition(self) -> ToolDefinition:
        """Return schema definition formatted for LLM function/tool specification."""
        return ToolDefinition(
            name=self.tool_name,
            description=self.description,
            parameters=self.input_schema,
        )

    def to_openai_tool(self) -> Dict[str, Any]:
        """Format as an OpenAI-compatible function tool definition."""
        return {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    @abstractmethod
    async def execute(
        self,
        *,
        case_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """
        Execute tool within authenticated case boundary.
        case_id is authoritative and cannot be overridden by arguments.
        """
        pass
