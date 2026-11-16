"""
Unit tests for LlmProviderService (httpx.MockTransport).

Tests cover:
- OpenAI-compatible URL, headers, body; OpenRouter extra headers
- Azure URL variants (`/openai/v1` vs deployment URL with api-version)
- Azure 404 / DeploymentNotFound mapped to its own message
- Anthropic Messages API request, text blocks, status and transport errors
- Error wrapping: 401/403, 429, other statuses, timeout, unreachable, bad format; key never in the detail
"""

import json
import unittest

import httpx
import pytest

from errors.llm_errors import (
    AzureDeploymentNotFoundError,
    LlmAuthError,
    LlmProviderError,
    LlmRateLimitError,
    LlmTimeoutError,
)
from services.llm_provider_service import LlmProviderService

KEY = "sk-test-secret"
OK_BODY = {"choices": [{"message": {"content": "  Explanation.  "}}]}


def service(handler) -> LlmProviderService:
    """Create a service on a mock transport."""
    return LlmProviderService(transport=httpx.MockTransport(handler))


@pytest.mark.unit
class TestLlmProviderService(unittest.IsolatedAsyncioTestCase):
    """Test cases for LlmProviderService."""

    async def test_openai_compatible_request(self):
        """Test the URL, bearer key, extra headers, model, messages and temperature."""
        seen = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["request"] = request
            return httpx.Response(200, json=OK_BODY)

        text = await service(handler).openai_compatible(
            "https://openrouter.ai/api/v1/chat/completions", f" {KEY} ", "m", "prompt", {"X-Title": "DEMATELab"}
        )
        request = seen["request"]
        body = json.loads(request.content)
        self.assertEqual(text, "Explanation.")
        self.assertEqual(request.headers["authorization"], f"Bearer {KEY}")
        self.assertEqual(request.headers["x-title"], "DEMATELab")
        self.assertEqual(body["model"], "m")
        self.assertEqual(body["temperature"], 0.4)
        self.assertEqual(body["messages"][1], {"role": "user", "content": "prompt"})
        self.assertEqual(body["messages"][0]["role"], "system")

    async def test_azure_urls(self):
        """Test both Azure URL forms and the api-key header."""
        seen = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request)
            return httpx.Response(200, json=OK_BODY)

        await service(handler).azure("https://r.openai.azure.com/openai/v1/", KEY, "gpt", "p")
        await service(handler).azure("https://r.openai.azure.com", KEY, "dep", "p")
        self.assertEqual(str(seen[0].url), "https://r.openai.azure.com/openai/v1/chat/completions")
        self.assertEqual(json.loads(seen[0].content)["model"], "gpt")
        self.assertEqual(
            str(seen[1].url),
            "https://r.openai.azure.com/openai/deployments/dep/chat/completions?api-version=2024-06-01",
        )
        self.assertNotIn("model", json.loads(seen[1].content))
        self.assertEqual(seen[1].headers["api-key"], KEY)

    async def test_status_errors(self):
        """Test status mapping and that the key is removed from the logged detail."""
        cases = [(401, LlmAuthError), (403, LlmAuthError), (429, LlmRateLimitError), (500, LlmProviderError)]
        for status, error_type in cases:
            with self.subTest(status=status):
                handler = lambda request, s=status: httpx.Response(s, text=f"bad key {KEY}")  # noqa: E731
                with self.assertRaises(error_type) as context:
                    await service(handler).openai_compatible("https://x.test/c", KEY, "m", "p")
                self.assertNotIn(KEY, context.exception.detail)
                self.assertNotIn(KEY, context.exception.public_message)
        self.assertEqual(context.exception.public_message, "The AI provider request failed (HTTP 500).")

    async def test_transport_errors(self):
        """Test timeout, unreachable host and unexpected response shape."""

        def timeout(request):
            raise httpx.ReadTimeout("slow", request=request)

        def unreachable(request):
            raise httpx.ConnectError("down", request=request)

        with self.assertRaises(LlmTimeoutError):
            await service(timeout).openai_compatible("https://x.test/c", KEY, "m", "p")
        with self.assertRaises(LlmProviderError) as context:
            await service(unreachable).openai_compatible("https://x.test/c", KEY, "m", "p")
        self.assertEqual(context.exception.public_message, "The AI provider could not be reached.")
        with self.assertRaises(LlmProviderError) as context:
            await service(lambda r: httpx.Response(200, json={"x": 1})).azure("https://a.test", KEY, "m", "p")
        self.assertEqual(context.exception.public_message, "Unexpected response format from Azure OpenAI.")

    async def test_anthropic_request(self):
        """Test the Messages API URL, headers, body, and that only text blocks are joined."""
        seen = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["request"] = request
            blocks = [
                {"type": "thinking", "thinking": "x"},
                {"type": "text", "text": " A"},
                {"type": "text", "text": "B "},
            ]
            return httpx.Response(200, json={"content": blocks})

        text = await service(handler).anthropic(f" {KEY} ", "claude-haiku-5-5", "prompt")
        request = seen["request"]
        body = json.loads(request.content)
        self.assertEqual(text, "AB")
        self.assertEqual(str(request.url), "https://api.anthropic.com/v1/messages")
        self.assertEqual(request.headers["x-api-key"], KEY)
        self.assertEqual(request.headers["anthropic-version"], "2023-06-01")
        self.assertEqual(request.headers["content-type"], "application/json")
        self.assertEqual((body["model"], body["max_tokens"]), ("claude-haiku-5-5", 4096))
        self.assertEqual(body["system"], "You are an expert academic analyst interpreting DEMATEL results.")
        self.assertEqual(body["messages"], [{"role": "user", "content": "prompt"}])

    async def test_anthropic_errors(self):
        """Test Anthropic status, transport and shape errors; the key never reaches the detail."""
        cases = [(401, LlmAuthError), (403, LlmAuthError), (429, LlmRateLimitError), (529, LlmProviderError)]
        for status, error_type in cases:
            with self.subTest(status=status):
                handler = lambda request, s=status: httpx.Response(s, text=f"bad {KEY}")  # noqa: E731
                with self.assertRaises(error_type) as context:
                    await service(handler).anthropic(KEY, "m", "p")
                self.assertNotIn(KEY, context.exception.detail)

        def timeout(request):
            raise httpx.ReadTimeout("slow", request=request)

        def unreachable(request):
            raise httpx.ConnectError("down", request=request)

        with self.assertRaises(LlmTimeoutError):
            await service(timeout).anthropic(KEY, "m", "p")
        with self.assertRaises(LlmProviderError):
            await service(unreachable).anthropic(KEY, "m", "p")
        for body in [{"x": 1}, {"content": [{"type": "tool_use"}]}]:
            with self.assertRaises(LlmProviderError):
                await service(lambda r, b=body: httpx.Response(200, json=b)).anthropic(KEY, "m", "p")

    async def test_azure_deployment_not_found(self):
        """Test Azure 404 and DeploymentNotFound bodies map to the deployment message; 404 elsewhere stays generic."""
        not_found = '{"error": {"code": "DeploymentNotFound"}}'
        for status in (404, 400):
            with self.subTest(status=status):
                handler = lambda r, s=status: httpx.Response(s, text=not_found)  # noqa: E731
                with self.assertRaises(AzureDeploymentNotFoundError) as context:
                    await service(handler).azure("https://r.openai.azure.com", KEY, "dep", "p")
                self.assertEqual(
                    context.exception.public_message,
                    "Deployment not found. Check the deployment name in your Azure portal.",
                )
        with self.assertRaises(LlmProviderError):
            await service(lambda r: httpx.Response(404, text="nope")).openai_compatible(
                "https://x.test/c", KEY, "m", "p"
            )
