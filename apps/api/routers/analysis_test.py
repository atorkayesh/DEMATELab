"""
Unit tests for the analysis router.

Tests cover:
- 200 with result, summary and corrected weights
- 422 validation errors with field paths; unknown label and failed analysis messages; no stack traces
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestAnalysisRouter(unittest.TestCase):
    """Test cases for the analysis router."""

    def setUp(self):
        """Create the client and a request."""
        self.client = TestClient(app)
        self.request = parity_fixtures.parity_case("small__grey_dematel__mmde")["request"]

    def test_success(self):
        """Test the response data."""
        body = self.client.post("/api/v1/analysis", json=self.request).json()
        self.assertEqual(body["data"]["result"]["solver_type"], "grey_dematel")
        self.assertEqual(body["data"]["summary"]["result_type_label"], "Grey DEMATEL")
        self.assertEqual(body["data"]["corrected_weights"], [0.6, 0.4])

    def test_validation_error_fields(self):
        """Test 422 with the field path."""
        response = self.client.post("/api/v1/analysis", json={**self.request, "factors": ["Cost", "Cost", "Time"]})
        body = response.json()
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["fields"][0]["field"], "factors")
        self.assertIn("Factor names must be unique.", body["error"]["fields"][0]["message"])

    def test_unknown_label(self):
        """Test the unknown label error is public and has no traceback."""
        experts = [{**self.request["experts"][0], "matrix": [["x", "Huge", "Low influence"]] * 3}]
        response = self.client.post("/api/v1/analysis", json={**self.request, "experts": experts * 1})
        body = response.json()
        self.assertEqual((response.status_code, body["error"]["code"]), (422, "invalid_weights"))
        experts[0]["weight"] = 1.0
        body = self.client.post("/api/v1/analysis", json={**self.request, "experts": experts}).json()
        self.assertEqual(body["error"]["code"], "unknown_linguistic_term")
        self.assertIn("'Huge'", body["message"])
        self.assertNotIn("Traceback", str(body))
