"""
Unit tests for the scales router.

Tests cover:
- GET /scales returns the scales in the standard response shape
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.unit
class TestScalesRouter(unittest.TestCase):
    """Test cases for the scales router."""

    def test_get_scales(self):
        """Test the response shape and a few values."""
        response = TestClient(app).get("/api/v1/scales")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["standard"]["terms"][0], "No influence")
        self.assertEqual(body["data"]["limits"]["experts_max"], 50)
