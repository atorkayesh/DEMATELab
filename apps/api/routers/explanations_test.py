"""
Unit tests for the explanations router.

Tests cover:
- Success through a mocked feature
- 422s (missing key, unknown provider) never contain the API key in the body or the logs
"""

import unittest
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from models.explanation_models import ExplanationData
from tests.parity_fixtures import parity_fixtures

KEY = "sk-very-secret-key"


@pytest.mark.unit
class TestExplanationsRouter(unittest.TestCase):
    """Test cases for the explanations router."""

    def setUp(self):
        """Create the client and a request."""
        self.client = TestClient(app)
        self.body = {"analysis": parity_fixtures.parity_case("small__dematel__average")["request"], "provider": "Groq"}

    @patch("routers.explanations.explanation_feature.explain", new_callable=AsyncMock)
    def test_success(self, explain):
        """Test the response data."""
        explain.return_value = ExplanationData(text="Text", provider="Groq", model="m")
        response = self.client.post("/api/v1/explanations", json={**self.body, "api_key": KEY})
        self.assertEqual(response.json()["data"], {"text": "Text", "provider": "Groq", "model": "m"})

    def test_missing_key(self):
        """Test Qt's message for a blank key."""
        response = self.client.post("/api/v1/explanations", json={**self.body, "api_key": " "})
        self.assertEqual((response.status_code, response.json()["message"]), (422, "Please enter an API key."))

    def test_validation_error_hides_key(self):
        """Test an invalid request never echoes or logs the key."""
        with self.assertLogs(level="INFO") as logs:
            response = self.client.post(
                "/api/v1/explanations", json={**self.body, "provider": "Claude", "api_key": KEY, "model": [KEY]}
            )
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(KEY, response.text)
        self.assertNotIn(KEY, "\n".join(logs.output))
