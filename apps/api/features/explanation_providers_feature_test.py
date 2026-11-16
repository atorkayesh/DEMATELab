"""
Unit tests for ExplanationProvidersFeature.

Tests cover:
- Every provider is listed in order with 3-7 models and a default from its own list
- Anthropic's catalogue; Azure is free text with no models and no default
"""

import unittest

import pytest

from constants.llm_constants import LlmProvider
from features.explanation_providers_feature import ExplanationProvidersFeature


@pytest.mark.unit
class TestExplanationProvidersFeature(unittest.TestCase):
    """Test cases for ExplanationProvidersFeature."""

    def setUp(self):
        """List the providers."""
        self.providers = ExplanationProvidersFeature().list_providers().providers

    def test_catalogue_shape(self):
        """Test order, list sizes, unique models and that each default is in its list."""
        self.assertEqual([p.id for p in self.providers], list(LlmProvider))
        for provider in [p for p in self.providers if not p.free_text_model]:
            with self.subTest(provider=provider.label):
                self.assertTrue(3 <= len(provider.models) <= 7)
                self.assertEqual(len(set(provider.models)), len(provider.models))
                self.assertIn(provider.default_model, provider.models)

    def test_anthropic_and_azure(self):
        """Test Anthropic's models and default, and that only Azure takes a free-text model."""
        by_id = {p.id: p for p in self.providers}
        anthropic = by_id[LlmProvider.ANTHROPIC]
        self.assertEqual(
            anthropic.models, ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-2"]
        )
        self.assertEqual(anthropic.default_model, "claude-haiku-5-5")
        azure = [p for p in self.providers if p.free_text_model]
        self.assertEqual([(p.id, p.models, p.default_model) for p in azure], [(LlmProvider.AZURE_OPENAI, [], None)])

    def test_openrouter_uses_vendor_slugs(self):
        """Test OpenRouter models use the vendor/model form."""
        for model in {p.id: p for p in self.providers}[LlmProvider.OPENROUTER].models:
            self.assertRegex(model, r"^[a-z0-9-]+/[a-z0-9.-]+$")
