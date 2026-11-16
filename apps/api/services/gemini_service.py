"""
Gemini call through `google-genai` (`llm_explanation_service.py:198-214`), run in a worker thread with a
time limit. A new client is created per call inside the worker and kept open until `generate_content`
returns; the SDK HTTP timeout stops a timed-out call. The key is never logged.
"""

import asyncio
from typing import Any, Callable, Optional

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from constants.llm_constants import LLM_SETTINGS
from errors.app_error import AppError
from errors.llm_errors import LlmAuthError, LlmProviderError, LlmRateLimitError, LlmTimeoutError


class GeminiService:
    """Generates text with Gemini."""

    def __init__(
        self, client_factory: Optional[Callable[[str], Any]] = None, timeout: float = LLM_SETTINGS["TIMEOUT_SECONDS"]
    ):
        """
        Create the service.

        Args:
            client_factory: Builds a client from a key; defaults to `genai.Client` with the SDK HTTP timeout
                (tests pass a mock)
            timeout: Seconds to wait for an answer
        """
        self._client_factory = client_factory or self._default_client
        self._timeout = timeout

    def _default_client(self, api_key: str) -> Any:
        """Build a Gemini client whose HTTP requests stop after the time limit (the SDK takes milliseconds)."""
        options = genai_types.HttpOptions(timeout=int(self._timeout * 1000))
        return genai.Client(api_key=api_key, http_options=options)

    async def generate(self, api_key: str, model: str, prompt: str) -> str:
        """
        Generate the explanation.

        Args:
            api_key: Gemini key
            model: Model name
            prompt: Prompt text

        Returns:
            str: The generated text, trimmed
        """
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self._call, api_key.strip(), model, prompt), timeout=self._timeout
            )
        except TimeoutError as exc:
            raise LlmTimeoutError("Gemini did not answer in time") from exc
        except genai_errors.APIError as exc:
            raise self._api_error(exc) from exc
        except httpx.TimeoutException as exc:
            raise LlmTimeoutError(f"Timeout calling Gemini: {type(exc).__name__}") from exc
        except httpx.HTTPError as exc:
            raise LlmProviderError(f"Request to Gemini failed: {type(exc).__name__}") from exc
        except Exception as exc:
            raise LlmProviderError(f"Gemini call failed: {type(exc).__name__}") from exc
        text = getattr(response, "text", None)
        if not text:
            raise LlmProviderError("Gemini returned no text", public_message="No explanation was returned by Gemini.")
        return text.strip()

    def _call(self, api_key: str, model: str, prompt: str) -> Any:
        """Run the blocking SDK call, keeping the client open until it returns."""
        client = self._client_factory(api_key)
        try:
            return client.models.generate_content(model=model, contents=prompt)
        finally:
            client.close()

    def _api_error(self, exc: genai_errors.APIError) -> AppError:
        """Map a Gemini API error to its typed error."""
        status = getattr(exc, "code", None)
        detail = f"Gemini answered HTTP {status}: {getattr(exc, 'message', '')}"
        if status in (401, 403):
            return LlmAuthError(detail)
        if status == 429:
            return LlmRateLimitError(detail)
        return LlmProviderError(detail, public_message=f"The AI provider request failed (HTTP {status}).")


gemini_service = GeminiService()
