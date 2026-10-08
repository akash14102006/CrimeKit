"""
Nebius Token Factory & NVIDIA Nemotron Model Provider.

Communicates with Nebius Token Factory OpenAI-compatible API using httpx.
Features:
- Configurable base URL, API key, model name (NVIDIA Nemotron)
- Connect and read timeouts
- Exponential backoff retry on transient 5xx / connection errors
- Normalized error handling (401, 429, 503, timeouts)
- Zero secret logging
"""

import os
import time
import logging
import asyncio
from typing import Optional, Dict, Any, List
import httpx

from .gateway import (
    BaseModelProvider,
    ModelRequest,
    ModelResponse,
    ModelUsage,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderAuthError,
)

logger = logging.getLogger(__name__)

DEFAULT_NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1"
DEFAULT_NEMOTRON_MODEL = "nvidia/nemotron-4-340b-instruct"


class NebiusNemotronProvider(BaseModelProvider):
    """Production Nebius Token Factory client configured for NVIDIA Nemotron."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self._api_key = api_key or os.getenv("NEBIUS_API_KEY", "")
        self._base_url = (base_url or os.getenv("NEBIUS_BASE_URL", DEFAULT_NEBIUS_BASE_URL)).rstrip("/")
        self._model = model or os.getenv("NEBIUS_MODEL", DEFAULT_NEMOTRON_MODEL)
        self._timeout_seconds = timeout_seconds or float(os.getenv("NEBIUS_TIMEOUT_SECONDS", "45.0"))
        self._max_retries = max_retries if max_retries is not None else int(os.getenv("NEBIUS_MAX_RETRIES", "2"))
        self._client = http_client

    @property
    def provider_name(self) -> str:
        return "nebius"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client:
            return self._client
        return httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout_seconds, connect=10.0),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "User-Agent": "CrimeKit-Investigation-Platform/1.0",
            },
        )

    async def chat(self, request: ModelRequest) -> ModelResponse:
        """Execute chat completion against Nebius OpenAI-compatible endpoint."""
        if not self.is_configured:
            raise ProviderNotConfiguredError(
                "AI model provider is not configured. Set NEBIUS_API_KEY in backend environment."
            )

        messages_payload: List[Dict[str, Any]] = []
        if request.system_prompt:
            messages_payload.append({"role": "system", "content": request.system_prompt})
        for m in request.messages:
            messages_payload.append({"role": m.role, "content": m.content})

        body: Dict[str, Any] = {
            "model": self._model,
            "messages": messages_payload,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.tools:
            body["tools"] = request.tools

        endpoint = "/chat/completions"
        client = await self._get_client()
        should_close = self._client is None

        attempt = 0
        start_time = time.time()

        while attempt <= self._max_retries:
            attempt += 1
            try:
                logger.info(
                    "Dispatching request to Nebius Nemotron gateway",
                    extra={
                        "provider": "nebius",
                        "model": self._model,
                        "attempt": attempt,
                        "message_count": len(messages_payload),
                    },
                )
                response = await client.post(endpoint, json=body)

                # Check HTTP status
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise ProviderError("Empty response returned by Nebius model endpoint.")
                    first_choice = choices[0]
                    message_obj = first_choice.get("message", {})
                    content = message_obj.get("content", "") or ""
                    finish_reason = first_choice.get("finish_reason")

                    usage_raw = data.get("usage", {})
                    usage = ModelUsage(
                        prompt_tokens=usage_raw.get("prompt_tokens", 0),
                        completion_tokens=usage_raw.get("completion_tokens", 0),
                        total_tokens=usage_raw.get("total_tokens", 0),
                    )

                    duration_ms = (time.time() - start_time) * 1000
                    logger.info(
                        "Nebius Nemotron completion succeeded",
                        extra={
                            "provider": "nebius",
                            "model": self._model,
                            "duration_ms": round(duration_ms, 2),
                            "tokens": usage.total_tokens,
                        },
                    )
                    return ModelResponse(
                        content=content,
                        tool_calls=message_obj.get("tool_calls", []),
                        usage=usage,
                        model=self._model,
                        provider="nebius",
                        raw_finish_reason=finish_reason,
                    )

                elif response.status_code in (401, 403):
                    # Do not retry auth errors
                    logger.error("Nebius authentication rejected (HTTP %s)", response.status_code)
                    raise ProviderAuthError("Nebius Token Factory authentication failed. Check NEBIUS_API_KEY.")

                elif response.status_code == 429:
                    # Rate limit
                    logger.warning("Nebius rate limit reached (HTTP 429)")
                    if attempt <= self._max_retries:
                        await asyncio.sleep(1.5 * attempt)
                        continue
                    raise ProviderRateLimitError("Nebius model rate limit reached. Please retry in a few moments.")

                elif response.status_code >= 500:
                    # Transient server error
                    logger.warning("Nebius upstream 5xx error (HTTP %s)", response.status_code)
                    if attempt <= self._max_retries:
                        await asyncio.sleep(1.0 * attempt)
                        continue
                    raise ProviderError(
                        f"Nebius service returned upstream error HTTP {response.status_code}.",
                        status_code=502,
                    )

                else:
                    err_msg = response.text[:200]
                    raise ProviderError(
                        f"Nebius API error HTTP {response.status_code}: {err_msg}",
                        status_code=response.status_code,
                    )

            except (httpx.TimeoutException, TimeoutError) as exc:
                logger.warning("Nebius request timeout on attempt %s: %s", attempt, exc)
                if attempt <= self._max_retries:
                    await asyncio.sleep(0.5 * attempt)
                    continue
                raise ProviderTimeoutError("Nebius model gateway timed out. Please retry.")

            except httpx.NetworkError as exc:
                logger.warning("Nebius network connection error on attempt %s: %s", attempt, exc)
                if attempt <= self._max_retries:
                    await asyncio.sleep(0.8 * attempt)
                    continue
                raise ProviderError(f"Network error connecting to Nebius: {exc}", status_code=503)

            finally:
                if should_close and attempt > self._max_retries:
                    await client.aclose()

        if should_close:
            await client.aclose()

        raise ProviderError("Nebius model request failed after maximum retries.")
