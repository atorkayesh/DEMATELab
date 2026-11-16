"""
Unit tests for GeminiService (mocked client).

Tests cover:
- The key, model and prompt reach the SDK; text is trimmed
- The client stays open until generate_content returns, then is closed
- The default client carries the SDK HTTP timeout
- Empty text, API errors (401, 403, 429, 500), network errors, unexpected errors and timeouts are wrapped
"""

import time
import unittest
from unittest.mock import MagicMock

import httpx
import pytest
from google.genai import errors as genai_errors

from errors.llm_errors import LlmAuthError, LlmProviderError, LlmRateLimitError, LlmTimeoutError
from services.gemini_service import GeminiService


def factory(response=None, error=None, delay=0.0):
    """Build a client factory whose generate_content returns `response` or raises `error`."""
    client = MagicMock()

    def generate_content(**kwargs):
        time.sleep(delay)
        if error:
            raise error
        return response

    client.models.generate_content.side_effect = generate_content
    return MagicMock(return_value=client), client


@pytest.mark.unit
class TestGeminiService(unittest.IsolatedAsyncioTestCase):
    """Test cases for GeminiService."""

    async def test_generate(self):
        """Test the SDK call and the trimmed text."""
        make, client = factory(MagicMock(text="  Text  "))
        text = await GeminiService(make).generate(" key ", "gemini-2.5-pro", "prompt")

        self.assertEqual(text, "Text")
        make.assert_called_once_with("key")
        client.models.generate_content.assert_called_once_with(model="gemini-2.5-pro", contents="prompt")
        client.close.assert_called_once()

    async def test_client_open_during_call(self):
        """Test the client is not closed before generate_content finishes (the closed-client 500)."""
        client = MagicMock()

        def generate_content(**kwargs):
            client.close.assert_not_called()
            return MagicMock(text="ok")

        client.models.generate_content.side_effect = generate_content
        self.assertEqual(await GeminiService(MagicMock(return_value=client)).generate("k", "m", "p"), "ok")
        client.close.assert_called_once()

    def test_default_client_timeout(self):
        """Test the default client passes the time limit to the SDK in milliseconds."""
        client = GeminiService(timeout=2.5)._default_client("k")
        try:
            self.assertEqual(client._api_client._http_options.timeout, 2500)
        finally:
            client.close()

    async def test_empty_text(self):
        """Test Qt's message when Gemini returns no text."""
        make, _ = factory(MagicMock(text=""))
        with self.assertRaises(LlmProviderError) as context:
            await GeminiService(make).generate("k", "m", "p")
        self.assertEqual(context.exception.public_message, "No explanation was returned by Gemini.")

    async def test_api_errors(self):
        """Test status mapping of SDK errors."""
        for code, error_type in [
            (401, LlmAuthError),
            (403, LlmAuthError),
            (429, LlmRateLimitError),
            (500, LlmProviderError),
        ]:
            with self.subTest(code=code):
                make, _ = factory(error=genai_errors.APIError(code, {"error": {"message": "x"}}))
                with self.assertRaises(error_type):
                    await GeminiService(make).generate("k", "m", "p")

    async def test_invalid_key_400(self):
        """Gemini's HTTP 400 API_KEY_INVALID is an auth error; other 400s stay provider errors."""
        bad_key = {
            "error": {
                "message": "API key not valid. Please pass a valid API key.",
                "details": [{"reason": "API_KEY_INVALID"}],
            }
        }
        for body, error_type in [(bad_key, LlmAuthError), ({"error": {"message": "bad request"}}, LlmProviderError)]:
            with self.subTest(error_type=error_type):
                make, _ = factory(error=genai_errors.APIError(400, body))
                with self.assertRaises(error_type) as caught:
                    await GeminiService(make).generate("k", "m", "p")
                self.assertIs(type(caught.exception), error_type)

    async def test_timeout(self):
        """Test the time limit."""
        make, _ = factory(MagicMock(text="late"), delay=0.3)
        with self.assertRaises(LlmTimeoutError):
            await GeminiService(make, timeout=0.05).generate("k", "m", "p")

    async def test_network_errors(self):
        """Test httpx failures: unreachable maps to the provider error, an HTTP timeout to the timeout error."""
        make, _ = factory(error=httpx.ConnectError("refused"))
        with self.assertRaises(LlmProviderError) as context:
            await GeminiService(make).generate("k", "m", "p")
        self.assertEqual(context.exception.public_message, "The AI provider could not be reached.")
        make, _ = factory(error=httpx.ReadTimeout("slow"))
        with self.assertRaises(LlmTimeoutError):
            await GeminiService(make).generate("k", "m", "p")

    async def test_unexpected_error(self):
        """Test any other failure maps to the provider error with only the exception type in the detail."""
        make, _ = factory(error=RuntimeError("secret-key in message"))
        with self.assertRaises(LlmProviderError) as context:
            await GeminiService(make).generate("k", "m", "p")
        self.assertEqual(context.exception.detail, "Gemini call failed: RuntimeError")
