"""
Unit tests for AnalysisFeature.

Tests cover:
- Weight correction is applied and returned
- The diagonal is forced before conversion (an unknown label there is ignored)
- Fuzzy Z results carry `fuzzy_z_dematel` and `fuzzy_*` fields
- Invalid weights and unknown labels raise their errors
"""

import unittest

import pytest

from errors.analysis_errors import InvalidWeightsError, UnknownLinguisticTermError
from features.analysis_feature import AnalysisFeature
from models.analysis_request_models import AnalysisRequest

M = "Medium influence"


def request(solver: str = "dematel", weights=(0.5, 0.5), diagonal: str = "anything") -> AnalysisRequest:
    """Build a 3-factor request."""
    matrix = [[diagonal, M, "Low influence"], ["High influence", diagonal, M], [M, "Low influence", diagonal]]
    return AnalysisRequest(
        solver_type=solver,
        threshold_method="average",
        factors=["A", "B", "C"],
        experts=[{"name": f"E{i}", "weight": w, "matrix": matrix} for i, w in enumerate(weights)],
    )


@pytest.mark.unit
class TestAnalysisFeature(unittest.IsolatedAsyncioTestCase):
    """Test cases for AnalysisFeature."""

    def setUp(self):
        """Create the feature."""
        self.feature = AnalysisFeature()

    async def test_weights_corrected_and_diagonal_forced(self):
        """Test 0.3333 x 3 is corrected and an invalid diagonal label does not fail."""
        data = await self.feature.analyze(request(weights=(0.3333, 0.3333, 0.3333)))

        self.assertEqual(data.corrected_weights, [0.333, 0.333, 0.334])
        self.assertEqual(data.result.expert_weights, [0.333, 0.333, 0.334])
        self.assertEqual(data.result.direct_matrix[0][0], 0.0)

    def test_fuzzy_z_result(self):
        """Test the Z solver returns the fuzzy fields with the real solver type."""
        z_request = request("fuzzy_z_dematel", diagonal="x")
        for expert in z_request.experts:
            expert.matrix = [[f"{c} with M reliability" if c != "x" else c for c in row] for row in expert.matrix]
        data = self.feature.analyze_sync(z_request)

        self.assertEqual(data.result.solver_type, "fuzzy_z_dematel")
        self.assertEqual(len(data.result.fuzzy_total_matrix[0][0]), 3)
        self.assertEqual(data.summary.result_type_label, "Fuzzy Z-DEMATEL")

    def test_errors(self):
        """Test invalid weights and an unknown off-diagonal label."""
        with self.assertRaises(InvalidWeightsError):
            self.feature.analyze_sync(request(weights=(0.5, 0.4)))
        bad = request()
        bad.experts[0].matrix[0][1] = "Huge influence"
        with self.assertRaises(UnknownLinguisticTermError):
            self.feature.analyze_sync(bad)
