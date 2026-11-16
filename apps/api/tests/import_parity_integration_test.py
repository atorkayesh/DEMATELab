"""
Import parity: every import fixture (Qt parser and matrix editor output) through the feature and HTTP.

Tests cover:
- Same factor names, matrices, and `matched_by`, or the same Qt error message
"""

import unittest

import pytest
from fastapi.testclient import TestClient

from errors.import_errors import InvalidImportError
from features.matrix_import_feature import matrix_import_feature
from main import app
from tests.parity_fixtures import parity_fixtures


@pytest.mark.integration
class TestImportParity(unittest.TestCase):
    """Every import fixture."""

    def setUp(self):
        """Create the client."""
        self.client = TestClient(app)

    def _run(self, fixture: dict, content: bytes):
        if fixture["kind"] == "matrix":
            return matrix_import_feature.import_matrix_bytes(content, fixture["factor_count"])
        return matrix_import_feature.import_workbook_bytes(content, fixture["factor_count"], fixture["expert_names"])

    def test_feature_matches_fixtures(self):
        """Test the import feature against every fixture."""
        fixtures = parity_fixtures.imports()
        self.assertGreaterEqual(len(fixtures), 20)
        for name, fixture, content in fixtures:
            with self.subTest(fixture=name):
                if "error_message" in fixture:
                    with self.assertRaises(InvalidImportError) as context:
                        self._run(fixture, content)
                    self.assertEqual(context.exception.public_message, fixture["error_message"])
                else:
                    self.assertEqual(self._run(fixture, content).model_dump(mode="json"), fixture["expected"])

    def test_http_matches_fixtures(self):
        """Test the import endpoints against every fixture."""
        for name, fixture, content in parity_fixtures.imports():
            with self.subTest(fixture=name):
                data = {"factor_count": str(fixture["factor_count"])}
                if fixture["kind"] == "workbook":
                    data["expert_names"] = fixture["expert_names"]
                response = self.client.post(
                    f"/api/v1/imports/{fixture['kind']}", files={"file": (fixture["file"], content)}, data=data
                )
                body = response.json()
                if "error_message" in fixture:
                    self.assertEqual((response.status_code, body["message"]), (422, fixture["error_message"]))
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(body["data"], fixture["expected"])
