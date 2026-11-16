"""
Unit tests for the health router.

Tests cover:
- /health returns 200 and `healthy` with the API `up`
- /is-alive returns 200 without running the health check
- API responses are not cacheable
"""

import unittest
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.unit
class TestHealthRouter(unittest.TestCase):
    """Test cases for the health router."""

    def setUp(self):
        """Set up the test client."""
        self.client = TestClient(app)

    def test_health_returns_200_when_healthy(self):
        """Test /health returns 200 with the API up."""
        response = self.client.get("/api/v1/health")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "System is healthy")
        self.assertEqual(body["data"]["status"], "healthy")
        self.assertEqual(body["data"]["services"]["api"]["status"], "up")
        self.assertIn("timestamp", body["metadata"])
        self.assertIsNone(body["error"])

    @patch("routers.health.health_feature.get_health", new_callable=AsyncMock)
    def test_is_alive_does_not_check_health(self, mock_get_health):
        """Test /is-alive returns 200 without running the health check."""
        response = self.client.get("/api/v1/is-alive")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Service is alive")
        self.assertEqual(body["data"]["status"], "alive")
        mock_get_health.assert_not_called()

    def test_responses_are_not_cacheable(self):
        """Test API responses carry `Cache-Control: no-store`."""
        response = self.client.get("/api/v1/is-alive")

        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_docs_are_served(self):
        """Test the OpenAPI docs page is served under /api/docs."""
        self.assertEqual(self.client.get("/api/docs").status_code, 200)
