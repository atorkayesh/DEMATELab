"""
Numerical parity with the Qt app, against the frozen fixtures from `qt-app/`.

Tests cover, for every fixture (case x solver x threshold):
- The feature result and the HTTP response equal the fixture (atol 1e-12, rtol 0)
- Groups, factors, threshold method, and corrected weights equal exactly
- Error fixtures give the same public message
- Summary ranking order and strongest relation equal the fixture (tie cases included)
- Cluster labels and codes equal the fixture, or the same clustering error
"""

import unittest
import warnings

import numpy as np
import pytest
from fastapi.testclient import TestClient

from errors.app_error import AppError
from features.analysis_feature import analysis_feature
from features.clustering_feature import clustering_feature
from main import app
from models.analysis_request_models import AnalysisRequest
from tests.parity_fixtures import parity_fixtures

EXACT_FIELDS = {"factors", "cause_group", "effect_group", "threshold_method"}


def assert_result_matches(test: unittest.TestCase, actual: dict, expected: dict) -> None:
    """Compare a serialized result with a fixture result."""
    for field, value in expected.items():
        with test.subTest(field=field):
            if field in EXACT_FIELDS:
                test.assertEqual(actual[field], value)
            else:
                np.testing.assert_allclose(
                    np.asarray(actual[field], float), np.asarray(value, float), rtol=0, atol=1e-12
                )


@pytest.mark.integration
class TestParity(unittest.TestCase):
    """Every parity fixture through the feature and through HTTP."""

    @classmethod
    def setUpClass(cls):
        """Create the client and silence KMeans warnings on matrices with repeated values."""
        cls.client = TestClient(app)
        warnings.filterwarnings("ignore", message="Number of distinct clusters")

    def test_fixture_count(self):
        """Test the fixture set covers every case x solver x threshold."""
        self.assertEqual(len(parity_fixtures.parity()), 135)

    def test_feature_matches_fixtures(self):
        """Test the analysis feature against every fixture."""
        for name, fixture in parity_fixtures.parity():
            with self.subTest(fixture=name):
                request = AnalysisRequest.model_validate(fixture["request"])
                if "error_message" in fixture:
                    with self.assertRaises(AppError) as context:
                        analysis_feature.analyze_sync(request)
                    self.assertEqual(context.exception.public_message, fixture["error_message"])
                    continue
                data = analysis_feature.analyze_sync(request)
                result = data.result.model_dump(mode="json")
                assert_result_matches(self, result, fixture["result"])
                np.testing.assert_allclose(
                    result["crisp_total_matrix"], fixture["crisp_total_matrix"], rtol=0, atol=1e-12
                )
                self.assertEqual(data.corrected_weights, fixture["corrected_weights"])
                self.assertEqual(result["solver_type"], fixture["request"]["solver_type"])
                order = [data.result.factors.index(item.factor) for item in data.summary.prominence_ranking]
                self.assertEqual(order, fixture["summary_order"])
                self._assert_strongest_relation(data.summary.strongest_relation, result["relation"], fixture)

    def _assert_strongest_relation(self, strongest: float, relation: list, fixture: dict) -> None:
        """
        Check Qt's rule `relation[argmax(|relation|)]` and the fixture value.

        When two relations have the same magnitude (within 1e-12, e.g. the `mmde_tie` cases), Qt's own pick
        depends on the last bits the BLAS library produces, so either tied value is accepted.
        """
        values = np.asarray(relation, dtype=float)
        self.assertEqual(strongest, float(values[int(np.argmax(np.abs(values)))]))
        expected = fixture["strongest_relation"]
        tied = np.sum(np.isclose(np.abs(values), abs(expected), rtol=0, atol=1e-12)) > 1
        if tied:
            self.assertAlmostEqual(abs(strongest), abs(expected), delta=1e-12)
        else:
            self.assertAlmostEqual(strongest, expected, delta=1e-12)

    def test_http_matches_fixtures(self):
        """Test POST /analysis against every fixture, including the error message of failing cases."""
        for name, fixture in parity_fixtures.parity():
            with self.subTest(fixture=name):
                response = self.client.post("/api/v1/analysis", json=fixture["request"])
                body = response.json()
                if "error_message" in fixture:
                    self.assertEqual(response.status_code, 422)
                    self.assertEqual(body["message"], fixture["error_message"])
                    self.assertEqual(body["error"]["code"], "analysis_failed")
                    continue
                self.assertEqual(response.status_code, 200)
                assert_result_matches(self, body["data"]["result"], fixture["result"])
                self.assertEqual(body["data"]["corrected_weights"], fixture["corrected_weights"])

    def test_clusters_match_fixtures(self):
        """Test cluster labels and codes, or the clustering error, for every successful fixture."""
        for name, fixture in parity_fixtures.parity():
            if "error_message" in fixture:
                continue
            with self.subTest(fixture=name):
                matrix = np.asarray(fixture["crisp_total_matrix"])
                expected = fixture["cluster"]
                if "error_message" in expected:
                    with self.assertRaises(AppError) as context:
                        clustering_feature.cluster(matrix, fixture["result"]["factors"])
                    self.assertTrue(context.exception.public_message.endswith(expected["error_message"]))
                    continue
                clusters = clustering_feature.cluster(matrix, fixture["result"]["factors"])
                self.assertEqual(clusters.labels_numeric.tolist(), expected["labels_numeric"])
                self.assertEqual(clusters.labels_named.tolist(), expected["labels_named"])
