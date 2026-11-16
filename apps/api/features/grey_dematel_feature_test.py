"""
Unit tests for GreyDematelFeature.

Tests cover:
- The grey engine reproduces a Qt fixture
- Interval order check
"""

import unittest

import numpy as np
import pytest

from constants.solver_constants import SolverType, ThresholdMethod
from errors.analysis_errors import InvalidAnalysisInputError
from features.grey_dematel_feature import GreyDematelFeature
from models.solver_models import SolverExpert
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestGreyDematelFeature(unittest.TestCase):
    """Test cases for GreyDematelFeature."""

    def test_grey_matches_fixture(self):
        """Test the grey engine's interval total matrix."""
        fixture, factors, experts = parity_fixtures.solver_experts("small__grey_dematel__mmde", SolverType.GREY_DEMATEL)
        output = GreyDematelFeature().solve(factors, experts, ThresholdMethod.MMDE)
        np.testing.assert_allclose(output.total_matrix, fixture["result"]["grey_total_matrix"], rtol=0, atol=1e-12)

    def test_order_check(self):
        """Test the lower <= upper rule."""
        bad_grey = SolverExpert("E", 1.0, np.array([[[0, 0], [0.5, 0.2]], [[0, 0], [0, 0]]], dtype=float))
        with self.assertRaises(InvalidAnalysisInputError) as context:
            GreyDematelFeature().solve(["A", "B"], [bad_grey], ThresholdMethod.AVERAGE)
        self.assertEqual(context.exception.public_message, "Grey matrix for expert 'E' must satisfy lower <= upper.")
