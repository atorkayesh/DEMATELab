"""
HTTP calls to the OpenAI-compatible providers (Groq, OpenRouter, OpenAI) and Azure OpenAI, ported from
`llm_explanation_service.py:100-195`, and to the Anthropic Messages API (new in the web app). One
`httpx.AsyncClient` per call. The key is never logged; provider response bodies go to the internal `detail`
only after the key is removed.
"""

from typing import Dict, Optional

import httpx

from constants.llm_constants import ANTHROPIC_SETTINGS, LLM_SETTINGS
from errors.app_error import AppError
from errors.llm_errors import (
    AzureDeploymentNotFoundError,
    LlmAuthError,
    LlmProviderError,
    LlmRateLimitError,
    LlmTimeoutError,
)


class LlmProviderService:
    """Sends chat completion requests and wraps every failure in an `AppError`."""

    def __init__(self, transport: Optional[httpx.AsyncBaseTransport] = None):
        """
        Create the service.

        Args:
            transport: httpx transport (tests pass `httpx.MockTransport`); defaults to the network
        """
        self._transport = transport

    async def openai_compatible(
        self, url: str, api_key: str, model: str, prompt: str, extra_headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Call an OpenAI-compatible chat completion endpoint.

        Args:
            url: Chat completion URL
            api_key: Provider key (sent as a Bearer token)
            model: Model name
            prompt: User prompt
            extra_headers: Additional headers (OpenRouter's referer and title)

        Returns:
            str: The generated text, trimmed
        """
        key = api_key.strip()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", **(extra_headers or {})}
        body = {"model": model, "messages": self._messages(prompt), "temperature": LLM_SETTINGS["TEMPERATURE"]}
        data = await self._post(url, headers, body, key)
        return self._content(data, "Unexpected response format from the selected LLM provider.")

    async def azure(self, endpoint: str, api_key: str, model: str, prompt: str) -> str:
        """
        Call Azure OpenAI: `/openai/v1` endpoints take the model in the body, others use the deployment URL.

        Args:
            endpoint: Azure resource endpoint
            api_key: Azure key (sent as `api-key`)
            model: Model or deployment name
            prompt: User prompt

        Returns:
            str: The generated text, trimmed
        """
        base = endpoint.strip().rstrip("/")
        body = {"messages": self._messages(prompt), "temperature": LLM_SETTINGS["TEMPERATURE"]}
        if base.endswith(LLM_SETTINGS["AZURE_V1_SUFFIX"]):
            url = f"{base}/chat/completions"
            body = {"model": model, **body}
        else:
            url = f"{base}/openai/deployments/{model}/chat/completions?api-version={LLM_SETTINGS['AZURE_API_VERSION']}"
        key = api_key.strip()
        headers = {"api-key": key, "Content-Type": "application/json"}
        data = await self._post(url, headers, body, key, azure=True)
        return self._content(data, "Unexpected response format from Azure OpenAI.")

    async def anthropic(self, api_key: str, model: str, prompt: str) -> str:
        """
        Call the Anthropic Messages API.

        Args:
            api_key: Anthropic key (sent as `x-api-key`)
            model: Model name
            prompt: User prompt

        Returns:
            str: The text blocks of the reply, joined and trimmed
        """
        key = api_key.strip()
        headers = {
            "x-api-key": key,
            "anthropic-version": ANTHROPIC_SETTINGS["VERSION"],
            "content-type": "application/json",
        }
        body = {
            "model": model,
            "max_tokens": ANTHROPIC_SETTINGS["MAX_TOKENS"],
            "system": LLM_SETTINGS["SYSTEM_MESSAGE"],
            "messages": [{"role": "user", "content": prompt}],
        }
        data = await self._post(ANTHROPIC_SETTINGS["URL"], headers, body, key)
        try:
            text = "".join(block["text"] for block in data["content"] if block.get("type") == "text").strip()
        except (KeyError, TypeError, AttributeError) as exc:
            raise LlmProviderError(
                f"Unexpected Anthropic response shape: {type(exc).__name__}",
                public_message="Unexpected response format from Anthropic.",
            ) from exc
        if not text:
            raise LlmProviderError("Anthropic response had no text block", public_message="Anthropic returned no text.")
        return text

    def _messages(self, prompt: str) -> list:
        """Build the system and user messages."""
        return [
            {"role": "system", "content": LLM_SETTINGS["SYSTEM_MESSAGE"]},
            {"role": "user", "content": prompt},
        ]

    async def _post(self, url: str, headers: Dict[str, str], body: dict, key: str, azure: bool = False) -> dict:
        """POST JSON and return the decoded response, mapping failures to typed errors (Azure adds 404)."""
        try:
            async with httpx.AsyncClient(timeout=LLM_SETTINGS["TIMEOUT_SECONDS"], transport=self._transport) as client:
                response = await client.post(url, headers=headers, json=body)
        except httpx.TimeoutException as exc:
            raise LlmTimeoutError(f"Timeout calling {url}: {type(exc).__name__}") from exc
        except httpx.HTTPError as exc:
            raise LlmProviderError(f"Request to {url} failed: {type(exc).__name__}") from exc
        if response.status_code >= 400:
            raise self._status_error(response, url, key, azure)
        try:
            return response.json()
        except ValueError as exc:
            raise LlmProviderError(
                f"Non-JSON response from {url}", public_message="The AI provider returned an unexpected response."
            ) from exc

    def _status_error(self, response: httpx.Response, url: str, key: str, azure: bool = False) -> AppError:
        """Map an HTTP error status to its typed error; the body (without the key) is kept for the logs."""
        body = response.text[:2000]
        if key:
            body = body.replace(key, "***")
        detail = f"{url} answered HTTP {response.status_code}: {body}"
        if response.status_code in (401, 403):
            return LlmAuthError(detail)
        if response.status_code == 429:
            return LlmRateLimitError(detail)
        if azure and (response.status_code == 404 or "DeploymentNotFound" in body):
            return AzureDeploymentNotFoundError(detail)
        return LlmProviderError(detail, public_message=f"The AI provider request failed (HTTP {response.status_code}).")

    def _content(self, data: dict, message: str) -> str:
        """Extract `choices[0].message.content`."""
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise LlmProviderError(f"Unexpected response shape: {type(exc).__name__}", public_message=message) from exc


llm_provider_service = LlmProviderService()
