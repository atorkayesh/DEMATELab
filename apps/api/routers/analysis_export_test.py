"""
Unit tests for the analysis export router.

Tests cover:
- The XLSX download headers; validation errors stay JSON
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestAnalysisExportRouter(unittest.TestCase):
    """Test cases for the analysis export router."""

    def test_download(self):
        """Test the attachment and the zip signature of the workbook."""
        request = parity_fixtures.parity_case("small__dematel__average")["request"]
        response = TestClient(app).post("/api/v1/analysis/export/xlsx", json=request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"PK"))
        self.assertIn("dematel_results.xlsx", response.headers["content-disposition"])

    def test_invalid_request(self):
        """Test a 422 JSON error."""
        response = TestClient(app).post("/api/v1/analysis/export/xlsx", json={})
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.json()["success"])
