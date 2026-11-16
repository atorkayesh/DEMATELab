"""
Unit tests for CrispDematelFeature.

Tests cover:
- The classical engine reproduces a Qt fixture
"""

import unittest

import numpy as np
import pytest

from constants.solver_constants import SolverType, ThresholdMethod
from features.crisp_dematel_feature import CrispDematelFeature
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestCrispDematelFeature(unittest.TestCase):
    """Test cases for CrispDematelFeature."""

    def test_crisp_matches_fixture(self):
        """Test the classical engine's total matrix and threshold."""
        fixture, factors, experts = parity_fixtures.solver_experts("weights3__dematel__median", SolverType.DEMATEL)
        output = CrispDematelFeature().solve(factors, experts, ThresholdMethod.MEDIAN)
        np.testing.assert_allclose(output.total_matrix, fixture["result"]["total_matrix"], rtol=0, atol=1e-12)
        self.assertAlmostEqual(output.threshold_value, fixture["result"]["threshold_value"], delta=1e-12)
