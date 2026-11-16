"""
Unit tests for the chart router.

Tests cover:
- PNG responses for both charts, both modes and both dpi values; 300 dpi about 3x wider (tight crop)
- dpi and mode restricted; cluster failure is 422 with the Qt message
"""

import struct
import unittest

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.parity_fixtures import parity_fixtures


def width(content: bytes) -> int:
    """Read a PNG width."""
    return struct.unpack(">I", content[16:20])[0]


@pytest.mark.unit
class TestAnalysisChartsRouter(unittest.TestCase):
    """Test cases for the chart router."""

    def setUp(self):
        """Create the client and a request."""
        self.client = TestClient(app)
        self.request = parity_fixtures.parity_case("weights3__fuzzy_dematel__median")["request"]

    def test_pngs(self):
        """Test every chart, mode and resolution."""
        urls = ["causal-diagram?", "heatmap?mode=standard&", "heatmap?mode=cluster&"]
        for url in urls:
            sizes = {}
            for dpi in (100, 300):
                with self.subTest(url=url, dpi=dpi):
                    response = self.client.post(f"/api/v1/analysis/charts/{url}dpi={dpi}", json=self.request)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.headers["content-type"], "image/png")
                    sizes[dpi] = width(response.content)
            self.assertEqual(sizes[100], 800)
            # 300 dpi is cropped tight like Qt's PNG export, so it is a little under 3x the full 100 dpi canvas.
            self.assertTrue(2.4 <= sizes[300] / sizes[100] <= 3.0, sizes)

    def test_restricted_parameters(self):
        """Test only 100/300 dpi and the two modes are accepted."""
        self.assertEqual(
            self.client.post("/api/v1/analysis/charts/causal-diagram?dpi=120", json=self.request).status_code, 422
        )
        self.assertEqual(
            self.client.post("/api/v1/analysis/charts/heatmap?mode=pie", json=self.request).status_code, 422
        )

    def test_cluster_failure(self):
        """Test 422 with Qt's message when clustering fails."""
        request = parity_fixtures.parity_case("two_factors__dematel__average")["request"]
        response = self.client.post("/api/v1/analysis/charts/heatmap?mode=cluster", json=request)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "clustering_failed")
        self.assertTrue(response.json()["message"].startswith("Could not generate cluster heatmap:"))
