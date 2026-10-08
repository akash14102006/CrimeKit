"""
Provider-Agnostic AI Model Gateway & Contracts.

Defines:
- ModelMessage: Normalized conversational message format
- ModelRequest: Internal model request contract
- ModelResponse: Internal normalized model response
- BaseModelProvider: Abstract provider interface
- ProviderError & subclasses for normalized error handling
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelMessage(BaseModel):
    role: str = Field(..., description="user | assistant | system | tool")
    content: str = Field(..., description="Text content")


class ModelRequest(BaseModel):
    messages: List[ModelMessage]
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1500, ge=1)
    tools: Optional[List[Dict[str, Any]]] = None


class ModelUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ModelResponse(BaseModel):
    content: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    usage: ModelUsage = Field(default_factory=ModelUsage)
    model: str
    provider: str = "nebius"
    raw_finish_reason: Optional[str] = None


class ProviderError(Exception):
    """Base exception for AI model provider issues."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "provider_error"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class ProviderNotConfiguredError(ProviderError):
    def __init__(self, message: str = "AI model provider is not configured."):
        super().__init__(message=message, status_code=503, error_code="provider_not_configured")


class ProviderRateLimitError(ProviderError):
    def __init__(self, message: str = "AI service is temporarily busy. Please retry."):
        super().__init__(message=message, status_code=429, error_code="rate_limit_exceeded")


class ProviderTimeoutError(ProviderError):
    def __init__(self, message: str = "AI request timed out. Please retry."):
        super().__init__(message=message, status_code=504, error_code="timeout")


class ProviderAuthError(ProviderError):
    def __init__(self, message: str = "Authentication failed with AI model provider."):
        super().__init__(message=message, status_code=401, error_code="invalid_credentials")


class BaseModelProvider(ABC):
    """Abstract interface for all LLM providers (Nebius, local, future)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'nebius')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model identifier."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """True if the provider has necessary API credentials."""
        pass

    @abstractmethod
    async def chat(self, request: ModelRequest) -> ModelResponse:
        """Execute a conversational completion."""
        pass
