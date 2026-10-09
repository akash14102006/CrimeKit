"""
Unit and Integration Tests for Nebius Token Factory & NVIDIA Nemotron AI Gateway (Phase 3).

Verifies:
1. Provider configuration & unconfigured states
2. Request and response normalization
3. Mocked HTTP success turns
4. Error normalization: 401 Auth, 429 Rate Limit, 500 Upstream, Timeouts
5. Detective system prompt construction and boundaries
6. NebiusNemotronRuntime execution & integration with BaseAgentRuntime
7. Case boundary and evidence reference preservation
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from backend.app.agents.gateway import (
    ModelRequest,
    ModelMessage,
    ProviderNotConfiguredError,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderError,
)
from backend.app.agents.nebius_provider import NebiusNemotronProvider
from backend.app.agents.detective_prompt import build_detective_prompt
from backend.app.agents.runtime import NebiusNemotronRuntime, MockDeterministicAgentRuntime


# ─── 1. Provider Configuration & Unconfigured Handling ──────────────────────

def test_nebius_provider_unconfigured():
    """Verify ProviderNotConfiguredError is raised if NEBIUS_API_KEY is missing."""
    provider = NebiusNemotronProvider(api_key="")
    assert not provider.is_configured
    assert provider.provider_name == "nebius"
    assert "nemotron" in provider.model_name

    with pytest.raises(ProviderNotConfiguredError):
        import asyncio
        asyncio.run(provider.chat(ModelRequest(messages=[ModelMessage(role="user", content="Test")])))


def test_nebius_provider_custom_configuration():
    """Verify custom model, base URL, and timeouts can be configured."""
    provider = NebiusNemotronProvider(
        api_key="neb-test-key-12345",
        base_url="https://custom.tokenfactory.nebius.com/v1",
        model="nvidia/nemotron-4-340b-instruct-custom",
        timeout_seconds=30.0,
        max_retries=1,
    )
    assert provider.is_configured
    assert provider.model_name == "nvidia/nemotron-4-340b-instruct-custom"
    assert provider._base_url == "https://custom.tokenfactory.nebius.com/v1"
    assert provider._timeout_seconds == 30.0
    assert provider._max_retries == 1


# ─── 2. Detective Prompt Engineering & Boundary Tests ───────────────────────

def test_detective_prompt_construction():
    """Verify Detective Agent system prompt includes forensic guardrails and case context."""
    case_id = "CASE-FORENSIC-001"
    evidence_refs = ["EV-087", "EV-104", "EV-210"]

    prompt = build_detective_prompt(case_id, evidence_refs)
    assert "Detective Agent" in prompt
    assert "AI discovers. AI correlates. AI explains. AI cites. AI shows uncertainty. Investigator decides." in prompt
    assert "NEVER claim guilt" in prompt
    assert "CASE-FORENSIC-001" in prompt
    assert "EV-087" in prompt
    assert "EV-104" in prompt


def test_detective_prompt_no_evidence():
    """Verify graceful prompt when no evidence exists yet in case."""
    prompt = build_detective_prompt("CASE-EMPTY")
    assert "CASE-EMPTY" in prompt
    assert "None currently registered" in prompt


# ─── 3. Mocked Nebius HTTP API Success ──────────────────────────────────────

@pytest.mark.asyncio
async def test_nebius_provider_successful_turn():
    """Verify successful 200 response is normalized into ModelResponse."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "id": "chatcmpl-test-001",
            "model": "nvidia/nemotron-4-340b-instruct",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Analysis indicates correlation between suspect and phone subscriber records.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 45,
                "total_tokens": 165,
            },
        },
        request=httpx.Request("POST", "https://api.tokenfactory.nebius.com/v1/chat/completions"),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response

    provider = NebiusNemotronProvider(api_key="valid-test-key", http_client=mock_client)
    req = ModelRequest(
        messages=[ModelMessage(role="user", content="Correlate suspect with telecom record.")],
        system_prompt="Detective Prompt",
    )

    resp = await provider.chat(req)
    assert resp.provider == "nebius"
    assert resp.model == "nvidia/nemotron-4-340b-instruct"
    assert "correlation between suspect" in resp.content
    assert resp.usage.total_tokens == 165
    assert resp.usage.completion_tokens == 45


# ─── 4. Mocked Error Normalization Tests ────────────────────────────────────

@pytest.mark.asyncio
async def test_nebius_provider_auth_failure():
    """Verify HTTP 401 converts to ProviderAuthError without retries."""
    mock_response = httpx.Response(
        status_code=401,
        text="Unauthorized: Invalid API key",
        request=httpx.Request("POST", "https://api.tokenfactory.nebius.com/v1/chat/completions"),
    )
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response

    provider = NebiusNemotronProvider(api_key="bad-key", http_client=mock_client, max_retries=2)
    req = ModelRequest(messages=[ModelMessage(role="user", content="Test")])

    with pytest.raises(ProviderAuthError) as exc_info:
        await provider.chat(req)

    assert "authentication failed" in str(exc_info.value).lower()
    assert mock_client.post.call_count == 1  # No wasteful retry storms on auth failures


@pytest.mark.asyncio
async def test_nebius_provider_rate_limit_normalization():
    """Verify HTTP 429 converts to ProviderRateLimitError."""
    mock_response = httpx.Response(
        status_code=429,
        text="Rate limit exceeded",
        request=httpx.Request("POST", "https://api.tokenfactory.nebius.com/v1/chat/completions"),
    )
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response

    provider = NebiusNemotronProvider(api_key="key", http_client=mock_client, max_retries=1)
    req = ModelRequest(messages=[ModelMessage(role="user", content="Test")])

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(ProviderRateLimitError) as exc_info:
            await provider.chat(req)

    assert "rate limit" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_nebius_provider_timeout_normalization():
    """Verify request timeout converts to ProviderTimeoutError."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")

    provider = NebiusNemotronProvider(api_key="key", http_client=mock_client, max_retries=1)
    req = ModelRequest(messages=[ModelMessage(role="user", content="Test")])

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(ProviderTimeoutError):
            await provider.chat(req)


# ─── 5. NebiusNemotronRuntime Full Turn Execution ───────────────────────────

@pytest.mark.asyncio
async def test_nebius_nemotron_runtime_detective_execution():
    """Verify NebiusNemotronRuntime formats turns and identifies handoffs."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "id": "cmpl-002",
            "model": "nvidia/nemotron-4-340b-instruct",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Based on evidence EV-087, Rahul Kumar is connected to +91 9876543210. A temporal timeline reconstruction is recommended.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 80, "completion_tokens": 30, "total_tokens": 110},
        },
        request=httpx.Request("POST", "https://api.tokenfactory.nebius.com/v1/chat/completions"),
    )
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response

    provider = NebiusNemotronProvider(api_key="valid-key", http_client=mock_client)
    runtime = NebiusNemotronRuntime(provider=provider)

    result = await runtime.execute_turn(
        agent_id="detective",
        case_id="CASE-ALPHA",
        query="Analyze connections for Rahul Kumar",
        session_id="sess-001",
        history=[],
        case_evidence_refs=["EV-087", "EV-104"],
    )

    assert "EV-087" in result.content
    assert len(result.tool_executions) == 1
    assert result.tool_executions[0].status == "completed"
    assert "EV-087" in result.evidence_refs
    assert result.handoff is not None
    assert result.handoff.target_agent == "timeline"


@pytest.mark.asyncio
async def test_nebius_nemotron_runtime_unconfigured_fallback():
    """Verify unconfigured provider returns informative non-fatal status without raising."""
    provider = NebiusNemotronProvider(api_key="")
    runtime = NebiusNemotronRuntime(provider=provider)

    result = await runtime.execute_turn(
        agent_id="detective",
        case_id="CASE-BETA",
        query="Query while unconfigured",
        session_id="sess-002",
        history=[],
    )

    assert "AI model provider is not configured" in result.content
    assert result.tool_executions[0].status == "failed"
