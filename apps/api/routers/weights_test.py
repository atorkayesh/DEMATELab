"""
Unit tests for the weights router.

Tests cover:
- /weights/defaults for 3 experts and the expert limit
- /weights/normalize correction and the 422 "Expert weights must sum to 1."
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.unit
class TestWeightsRouter(unittest.TestCase):
    """Test cases for the weights router."""

    def setUp(self):
        """Create the client."""
        self.client = TestClient(app)

    def test_defaults(self):
        """Test equal defaults and the 1-50 limit."""
        response = self.client.post("/api/v1/weights/defaults", json={"expert_count": 3})
        self.assertEqual(response.json()["data"]["weights"], [0.334, 0.333, 0.333])
        self.assertEqual(self.client.post("/api/v1/weights/defaults", json={"expert_count": 51}).status_code, 422)

    def test_normalize(self):
        """Test correction and rejection."""
        response = self.client.post("/api/v1/weights/normalize", json={"weights": [0.3333, 0.3333, 0.3333]})
        self.assertEqual(response.json()["data"]["weights"], [0.333, 0.333, 0.334])
        rejected = self.client.post("/api/v1/weights/normalize", json={"weights": [0.5, 0.4]})
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(rejected.json()["message"], "Expert weights must sum to 1.")
        self.assertEqual(rejected.json()["error"]["code"], "invalid_weights")
