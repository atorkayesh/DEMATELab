"""
Unit tests for the imports router.

Tests cover:
- Matrix and workbook uploads; unsupported files and factor_count limits
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestImportsRouter(unittest.TestCase):
    """Test cases for the imports router."""

    def setUp(self):
        """Create the client and load fixtures."""
        self.client = TestClient(app)
        self.files = {name: content for name, _, content in parity_fixtures.imports()}

    def test_matrix(self):
        """Test a labelled matrix upload."""
        response = self.client.post(
            "/api/v1/imports/matrix",
            files={"file": ("m.xlsx", self.files["matrix_labelled_4x4"])},
            data={"factor_count": "4"},
        )
        self.assertEqual(response.json()["data"]["factor_names"], ["Alpha", "Beta", "Gamma", "Delta"])

    def test_workbook_by_order(self):
        """Test a workbook matched by order."""
        response = self.client.post(
            "/api/v1/imports/workbook",
            files={"file": ("w.xlsx", self.files["workbook_by_order"])},
            data={"factor_count": "3", "expert_names": ["Ann", "Bob"]},
        )
        self.assertEqual(response.json()["data"]["matched_by"], "order")

    def test_rejections(self):
        """Test unsupported files and invalid factor counts."""
        csv = self.client.post("/api/v1/imports/matrix", files={"file": ("m.csv", b"a,b")}, data={"factor_count": "2"})
        self.assertEqual((csv.status_code, csv.json()["error"]["code"]), (422, "unsupported_file"))
        bad_count = self.client.post(
            "/api/v1/imports/matrix",
            files={"file": ("m.xlsx", self.files["matrix_plain_3x3"])},
            data={"factor_count": "1"},
        )
        self.assertEqual(bad_count.status_code, 422)
