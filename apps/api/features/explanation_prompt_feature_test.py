"""
Unit tests for ExplanationPromptFeature.

Tests cover:
- The real solver type in the payload (grey, fuzzy Z), with grey interval vectors
- Crisp payloads have no interval vectors; the prompt embeds the JSON data
"""

import json
import unittest

import pytest

from features.analysis_feature import analysis_feature
from features.explanation_prompt_feature import ExplanationPromptFeature
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures


def payload(name: str) -> dict:
    """Build the payload of a fixture."""
    request = AnalysisRequest.model_validate(parity_fixtures.parity_case(name)["request"])
    return ExplanationPromptFeature().build_payload(analysis_feature.solve(request))


@pytest.mark.unit
class TestExplanationPromptFeature(unittest.TestCase):
    """Test cases for ExplanationPromptFeature."""

    def test_real_solver_types(self):
        """Test grey and Z payloads name their own solver."""
        grey = payload("small__grey_dematel__mmde")
        self.assertEqual(grey["solver_type"], "grey_dematel")
        self.assertEqual(len(grey["grey_prominence"][0]), 2)
        self.assertEqual(payload("small_z__fuzzy_z_dematel__mmde")["solver_type"], "fuzzy_z_dematel")

    def test_crisp_payload_and_prompt(self):
        """Test the crisp payload keys and the prompt's data block."""
        data = payload("small__dematel__average")
        self.assertNotIn("fuzzy_prominence", data)
        self.assertEqual(list(data)[-1], "solver_type")
        prompt = ExplanationPromptFeature().build_prompt(data)
        self.assertTrue(prompt.startswith("You are an analytical thinker."))
        self.assertTrue(prompt.endswith(json.dumps(data, indent=2, ensure_ascii=False)))
