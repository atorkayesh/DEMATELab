"""
Unit tests for FuzzyDematelFeature.

Tests cover:
- Fuzzy and fuzzy Z results reproduce Qt fixtures
- Triangular order check
"""

import unittest

import numpy as np
import pytest

from constants.solver_constants import SolverType, ThresholdMethod
from errors.analysis_errors import InvalidAnalysisInputError
from features.fuzzy_dematel_feature import FuzzyDematelFeature
from models.solver_models import SolverExpert
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestFuzzyDematelFeature(unittest.TestCase):
    """Test cases for FuzzyDematelFeature."""

    def test_fuzzy_matches_fixture(self):
        """Test the fuzzy engine's triangular relation and crisp prominence."""
        fixture, factors, experts = parity_fixtures.solver_experts(
            "small__fuzzy_dematel__average", SolverType.FUZZY_DEMATEL
        )
        output = FuzzyDematelFeature().solve(factors, experts, ThresholdMethod.AVERAGE)
        np.testing.assert_allclose(output.raw_relation, fixture["result"]["fuzzy_relation"], rtol=0, atol=1e-12)
        np.testing.assert_allclose(output.prominence, fixture["result"]["prominence"], rtol=0, atol=1e-12)

    def test_fuzzy_z_keeps_solver_type(self):
        """Test Z input through the fuzzy engine."""
        fixture, factors, experts = parity_fixtures.solver_experts(
            "small_z__fuzzy_z_dematel__mmde", SolverType.FUZZY_Z_DEMATEL
        )
        output = FuzzyDematelFeature().solve(factors, experts, ThresholdMethod.MMDE, SolverType.FUZZY_Z_DEMATEL)
        self.assertEqual(output.solver_type, SolverType.FUZZY_Z_DEMATEL)
        self.assertAlmostEqual(output.threshold_value, fixture["result"]["threshold_value"], delta=1e-12)

    def test_order_check(self):
        """Test the l <= m <= u rule."""
        bad_fuzzy = SolverExpert("E", 1.0, np.array([[[0, 0, 0], [0.5, 0.2, 1]], [[0, 0, 0], [0, 0, 0]]], dtype=float))
        with self.assertRaises(InvalidAnalysisInputError) as context:
            FuzzyDematelFeature().solve(["A", "B"], [bad_fuzzy], ThresholdMethod.AVERAGE)
        self.assertEqual(context.exception.public_message, "Fuzzy matrix for expert 'E' must satisfy l <= m <= u.")
