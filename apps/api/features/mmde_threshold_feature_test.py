"""
Unit tests for MmdeThresholdFeature.

Tests cover:
- A known threshold from a Qt fixture
- Non-square input is rejected
"""

import unittest

import numpy as np
import pytest

from errors.analysis_errors import InvalidAnalysisInputError
from features.mmde_threshold_feature import MmdeThresholdFeature
from tests.parity_fixtures import parity_fixtures


@pytest.mark.unit
class TestMmdeThresholdFeature(unittest.TestCase):
    """Test cases for MmdeThresholdFeature."""

    def test_matches_qt_fixture_with_ties(self):
        """Test the tie fixture's MMDE threshold (repeated values, stable sort)."""
        fixture = parity_fixtures.parity_case("mmde_tie__dematel__mmde")
        total = np.asarray(fixture["result"]["total_matrix"])
        self.assertAlmostEqual(MmdeThresholdFeature().compute(total), fixture["result"]["threshold_value"], delta=1e-12)

    def test_rejects_non_square(self):
        """Test the Qt message for a non-square matrix."""
        with self.assertRaises(InvalidAnalysisInputError) as context:
            MmdeThresholdFeature().compute(np.zeros((2, 3)))
        self.assertEqual(context.exception.public_message, "MMDE requires a square matrix.")
