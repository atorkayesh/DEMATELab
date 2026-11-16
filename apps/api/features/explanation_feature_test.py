"""
Unit tests for ExplanationFeature (mocked services).

Tests cover:
- Missing key, missing Azure endpoint, and Azure endpoints outside the allowed hosts (SSRF guard)
- Default models per provider; the provider each request goes to
- The prompt holds the real solver type; provider errors propagate
"""

import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from errors.llm_errors import (
    InvalidAzureEndpointError,
    LlmRateLimitError,
    MissingApiKeyError,
    MissingAzureEndpointError,
)
from features.explanation_feature import ExplanationFeature
from models.explanation_models import ExplanationRequest
from tests.parity_fixtures import parity_fixtures


def make_request(provider: str, **extra) -> ExplanationRequest:
    """Build an explanation request for a grey fixture."""
    analysis = parity_fixtures.parity_case("small__grey_dematel__mmde")["request"]
    return ExplanationRequest(analysis=analysis, provider=provider, **{"api_key": "sk-1", **extra})


@pytest.mark.unit
class TestExplanationFeature(unittest.IsolatedAsyncioTestCase):
    """Test cases for ExplanationFeature."""

    def setUp(self):
        """Create the feature with mocked services."""
        self.providers = MagicMock()
        self.providers.openai_compatible = AsyncMock(return_value="openai text")
        self.providers.azure = AsyncMock(return_value="azure text")
        self.gemini = MagicMock()
        self.gemini.generate = AsyncMock(return_value="gemini text")
        self.feature = ExplanationFeature(providers=self.providers, gemini=self.gemini)

    async def test_missing_key_and_endpoint(self):
        """Test the Qt messages."""
        with self.assertRaises(MissingApiKeyError) as context:
            await self.feature.explain(make_request("Groq", api_key="  "))
        self.assertEqual(context.exception.public_message, "Please enter an API key.")
        with self.assertRaises(MissingAzureEndpointError) as context:
            await self.feature.explain(make_request("Azure OpenAI", azure_endpoint=" "))
        self.assertEqual(context.exception.public_message, "Azure OpenAI endpoint is required.")

    async def test_default_models_and_routing(self):
        """Test the viewer's default models and the service each provider uses."""
        expected = {
            "Gemini": ("gemini-2.5-pro", "gemini text"),
            "OpenAI": ("gpt-4o-mini", "openai text"),
            "OpenRouter": ("openai/gpt-4o-mini", "openai text"),
            "Groq": ("llama-3.3-70b-versatile", "openai text"),
            "Azure OpenAI": ("gpt-4o-mini", "azure text"),
        }
        for provider, (model, text) in expected.items():
            with self.subTest(provider=provider):
                data = await self.feature.explain(
                    make_request(provider, model=" ", azure_endpoint="https://a.openai.azure.com")
                )
                self.assertEqual((data.model, data.text), (model, text))

    async def test_prompt_has_real_solver_type(self):
        """Test the grey payload is labelled grey_dematel and the custom model is used."""
        await self.feature.explain(make_request("OpenAI", model="gpt-x"))
        url, key, model, prompt, headers = self.providers.openai_compatible.call_args.args
        self.assertEqual(
            (url, key, model, headers), ("https://api.openai.com/v1/chat/completions", "sk-1", "gpt-x", None)
        )
        self.assertIn('"solver_type": "grey_dematel"', prompt)
        self.assertIn('"grey_prominence"', prompt)

    async def test_provider_error_propagates(self):
        """Test a rate limit from the service reaches the caller."""
        self.providers.openai_compatible.side_effect = LlmRateLimitError("429")
        with self.assertRaises(LlmRateLimitError):
            await self.feature.explain(make_request("Groq"))

    async def test_azure_endpoint_allowed(self):
        """Test the accepted Azure hosts reach the service unchanged."""
        for endpoint in [
            "https://r.openai.azure.com",
            "https://R.cognitiveservices.azure.com/openai/v1/",
            "https://r.services.ai.azure.com:443",
        ]:
            with self.subTest(endpoint=endpoint):
                await self.feature.explain(make_request("Azure OpenAI", azure_endpoint=endpoint))
                self.assertEqual(self.providers.azure.call_args.args[0], endpoint)

    async def test_azure_endpoint_rejected(self):
        """Test non-https, foreign hosts, userinfo and non-443 ports are rejected before any request."""
        for endpoint in [
            "http://r.openai.azure.com",
            "https://169.254.169.254/latest",
            "https://evil.test/r.openai.azure.com",
            "https://r.openai.azure.com.evil.test",
            "https://openai.azure.com",
            "https://user@r.openai.azure.com",
            "https://r.openai.azure.com:8443",
            "https://r.openai.azure.com:bad",
            "r.openai.azure.com",
        ]:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(InvalidAzureEndpointError) as context:
                    await self.feature.explain(make_request("Azure OpenAI", azure_endpoint=endpoint))
                self.assertEqual(
                    context.exception.public_message,
                    "Enter a valid Azure OpenAI endpoint, for example https://YOUR-RESOURCE-NAME.openai.azure.com.",
                )
        self.providers.azure.assert_not_called()
