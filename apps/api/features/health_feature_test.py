"""
Unit tests for HealthFeature.

Tests cover:
- The API reports itself `up` and the system `healthy` without checking any dependency
"""

import unittest

import pytest

from features.health_feature import HealthFeature


@pytest.mark.unit
class TestHealthFeature(unittest.IsolatedAsyncioTestCase):
    """Test cases for HealthFeature."""

    async def test_get_health_reports_api_up(self):
        """Test the health data is `healthy` with only the API listed as `up`."""
        health = await HealthFeature().get_health()

        self.assertEqual(health.status, "healthy")
        self.assertEqual(list(health.services), ["api"])
        self.assertEqual(health.services["api"].status, "up")
